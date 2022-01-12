# -*- coding: gb18030 -*-
#
# $Id: Spell.py,v 1.47 2008-08-13 07:55:54 kebiao Exp $

"""
法术。
"""

import Language
import csdefine
import csstatus
import utils
from bwdebug import *
from csdefine import *
from interface.State import State
from Skill import Skill
import ObjectDefine
import AreaDefine
import RequireDefine
import CooldownFlyweight
import SkillTargetObjImpl
from CasterCondition import CasterCondition
import ReceiverObject
from EffectState import EffectState
from random import randint
from SmartImport import smartImport
g_cooldowns = CooldownFlyweight.CooldownFlyweight.instance()

from CPUCal import CPU_CostCal

class BuffData:
	"""
	buff实例的简单封装
	"""
	def __init__( self ):
		"""
		"""
		self._rate = 100	#改Buff附加比率
		self._buff = None	#BUFF实例

	def init( self, dictDat, skillID, index ):
		"""
		@param skillID:源技能ID
		@param index: 该BUFF在技能中的索引位置
		"""
		if dictDat[ "LinkRate" ] > 0.0:
			self._rate = dictDat[ "LinkRate" ]
		script = "Buff_" + str( int( dictDat[ "ID" ] ) )
		self._buff = smartImport( "Resource.Skills." + script + ":" + script )()
		self._buff.init( dictDat )
		self._buff.setSource( skillID, index )
		Skill.register( self._buff.getID(), self._buff )

	def getBuff( self ):
		"""
		取得BUFF实例
		"""
		return self._buff

	def getLinkRate( self ):
		"""
		返回改BUFF附加的比率
		"""
		return self._rate

class Spell( Skill, EffectState ):
	def __init__( self ):
		"""
		构造函数。
		"""
		Skill.__init__( self )
		EffectState.__init__( self )
		"""
		关于CD的描述
		1:自身CD CD：1 ms:8秒
		2：受限CD：技能施放开始时查看是否有这些CD没有冷却完毕， 否则不能施放
		3：引发CD：引发一个这样的全局CD 使其他技能也冷却

		self._casterCondition = []		# 施法者可以施法的要求(判断一个施法者是否能施展这个法术)
		self._receiverCondition = []		# 可以被施法的受术者要求(判断一个entity是否是符合条件的受术者)
		可战斗、可施法、可攻击、魔法免疫等都属于要求。
		"""
		self._level = 0												# 技能等级
		self._maxLevel = 0											# spell max level
		self._casterCondition = CasterCondition()					# 施法者可以施法的要求(判断一个施法者是否能施展这个法术)
		self._receiverObject = ReceiverObject.newInstance( 0, self )		# 受术者对象，其中包括受术者的一些合法性判断
		self._baseType = csdefine.BASE_SKILL_TYPE_NONE  			# 技能基础分类，see also SkillDefine.BASE_SKILL_TYPE
		self._rangeMax = 0.0										# float; 施展距离，米，默认值0，表示无距离限制
		self._rangeMin = 0.0										# float; 施展距离，米，默认值0，表示无距离限制
		self._speed = 0.0											# float; 法术飞行速度，米/秒，默认值0，表示瞬发
		self._castObjectType = csdefine.SKILL_CAST_OBJECT_TYPE_NONE	# 施展目标类型，see also CAST_OBJECT_TYPE_*
		self._require = RequireDefine.newInstance( None )			# see also RequireDefine; 施放法术消耗的东西; 默认为"None"，无需求
		self._buffLink	= []										# 技能产生的BUFF [buffDataInstance...]
		self._springOnUsedCD = []									# 该法术所引发的CD 技能使用后
		self._springOnIntonateOverCD = []							# 该法术所引发的CD 技能吟唱后
		self._limitCooldown = []									# 该法术受限CD
		self._skillCastRange = 0.0									# 法术释放距离
		self._effect_min = 0										# 技能影响力最小值
		self._effect_max = 0										# 技能影响力最大值
		self._castTargetLvMin = 0									# 技能可施展对象最底级
		self._castTargetLvMax = 0									# 技能可施展对象最高级
		self.isNotRotate = False									# 施法是否需要转向
		self._receiveDelayTime = 0.0  #技能效果延迟时间 （类似施法前摇）
		self._triggerBuffInterruptCode = []

	def init( self, dictDat ):
		"""
		读取技能配置
		@param dictDat:	配置数据
		@type dictDat:	python dictDat
		"""
		Skill.init( self, dictDat )
		EffectState.init( self, dictDat)
		self._rangeMax = dictDat[ "RangeMax" ]
		self._rangeMin = dictDat[ "RangeMin" ]
		self._intonateTime = dictDat[ "IntonateTime" ]								# 吟唱时间
		self._baseType = eval( str( dictDat[ "Type" ] ) )
		self.isNotRotate = dictDat.get( "isNotRotate", 0 )
		self._receiveDelayTime = dictDat.get( "receiveDelayTime", 0.0 )
		self._getCombatCount = dictDat.get( "getCombatCount", 0 )
		
		self._skillCastRange = dictDat[ "CastRange" ]								# 法术释放距离
		if self._skillCastRange < self._rangeMax:
			self._skillCastRange = self._rangeMax + 0.1 							#保证释放距离不小于技能施法距离

		for i in xrange( len( dictDat[ "SpringUsedCD" ] ) ):
			val = dictDat[ "SpringUsedCD" ][ i ]
			self._springOnUsedCD.append( ( val[ "CDID" ], val[ "CDTime" ] ) )

		for i in xrange( len( dictDat[ "SpringIntonateOverCD" ] ) ):
			val = dictDat[ "SpringIntonateOverCD" ][ i ]
			self._springOnIntonateOverCD.append( ( val[ "CDID" ], val[ "CDTime" ] ) )

		for i in xrange( len( dictDat[ "LimitCD" ] ) ):
			self._limitCooldown.append( dictDat[ "LimitCD" ][ i ] )

		self._level = dictDat[ "Level" ]
		self._maxLevel = dictDat[ "MaxLevel" ]
		self._speed = dictDat[ "Speed" ]											# 法术飞行速度，米/秒，为0则表示瞬发
		self._castObjectType = dictDat["CastObjectType"][ "type" ]					# 施展目标类型，see also CAST_OBJECT_TYPE_*
		self._castObject = ObjectDefine.newInstance( self._castObjectType, self )
		self._castObject.init( dictDat[ "CastObjectType" ] )

		if len( dictDat[ "Require" ] ) > 0: #list
			self._require = RequireDefine.newInstance( dictDat[ "Require" ] )		# 施放法术消耗的东西

		if len( dictDat[ "CasterCondition" ] ) > 0: #dict
			self._casterCondition.init( dictDat["CasterCondition"] )

		val = dictDat[ "ReceiverCondition" ]
		if len( val ) > 0: #dict
			conditions = val[ "conditions" ]
			if len( conditions ) > 0:
				self._receiverObject = ReceiverObject.newInstance( eval( conditions ), self )
				self._receiverObject.init( val )

		self._effect_min = dictDat[ "EffectMin" ]									# 技能影响力最小值
		self._effect_max = dictDat[ "EffectMax" ]									# 技能影响力最大值
		if self._effect_max < self._effect_min:
			self._effect_max = self._effect_min

		self._castTargetLvMin = dictDat[ "CastObjLevelMin" ]
		self._castTargetLvMax = dictDat[ "CastObjLevelMax" ]
		
		for val in dictDat[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )

		self._param5 = dictDat[ "param5" ]

		if dictDat.has_key( "buff" ):
			for i in xrange( len( dictDat[ "buff" ] ) ):
				dat = dictDat[ "buff" ][ i ]
				inst = BuffData()
				inst.init( dat, self._id, i )
				self._buffLink.append( inst )

	def getLevel( self ):
		"""
		virtual method = 0.
		获取技能级别
		"""
		return self._level

	def getMaxLevel( self ):
		"""
		virtual method = 0.
		获取技能最高级别
		"""
		return self._maxLevel

	def getRangeMax( self, caster ):
		"""
		virtual method.
		@param caster: 施法者，通常某些需要武器射程做为距离的法术就会用到。
		@return: 施法距离
		"""
		return self._rangeMax

	def getRangeMin( self, caster ):
		"""
		virtual method.
		@param caster: 施法者，通常某些需要武器射程做为距离的法术就会用到。
		@return: 施法最小距离
		"""
		return self._rangeMin

	def getCastRange( self, caster ):
		"""
		法术释放距离
		"""
		return self._skillCastRange

	def getFlySpeed( self ):
		"""
		@return: 法术的飞行速度
		"""
		return self._speed

	def getBuffLink( self, index ):
		"""
		"""
		return self._buffLink[ index ]

	def getBuffsLink( self ):
		"""
		@return: 所有技能产生的buff
		"""
		return self._buffLink[:]

	def getCastTargetLevelMin( self ):
		"""
		virtual method = 0.
		技能可施展对象最底级
		"""
		return self._castTargetLvMin

	def getCastObject( self ):
		"""
		virtual method.
		取得法术可施法的目标对像定义。
		@rtype:  ObjectDefine Instance
		"""
		return self._castObject

	def getCastTargetLevelMax( self ):
		"""
		virtual method = 0.
		技能可施展对象最高级
		"""
		return self._castTargetLvMax

	def getParam5Data( self ):
		"""
		获取param5数据 by姜毅
		"""
		return self._param5

	def getReceiveDelayTime( self ):
		"""
		获取技能效果延迟时间
		"""
		return self._receiveDelayTime

	def calcDelay( self, caster, target ):
		"""
		virtual method.
		取得伤害延迟
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: float(秒)
		"""
		return target.calcDelay( self, caster )


	def getIntonateTime( self , caster ):
		"""
		virtual method.
		获取技能自身的吟唱时间，此吟唱时间如果有必要，可以根据吟唱者决定具体的时长。

		@param caster:	使用技能的实体。用于以后扩展，如某些天赋会影响某些技能的默认吟唱时间。
		@type  caster:	Entity
		@return:		释放时间
		@rtype:			float
		"""
		return ( self._intonateTime + caster.queryTemp( "intonateTime_extra", 0 ) ) * ( 1 + caster.queryTemp( "intonateTime_percent", 0.0 ) ) + caster.queryTemp( "intonateTime_value", 0 )

	def getMaxCooldown( self, caster ):
		"""
		virtual method.
		获取法术本身最长的cooldown(也就是该法术能施展的时间)
		"""
		maxTimeVal = 0.0
		for cd in self._limitCooldown:
			timeVal = caster.getCooldown( cd )
			maxTimeVal = max( maxTimeVal, timeVal )
		return maxTimeVal

	def isCooldown( self, caster ):
		"""
		virtual method.
		判断法术本身的cooldown是否已过

		@return: BOOL
		"""
		for cd in self._limitCooldown:
			timeVal = caster.getCooldown( cd )
			if not g_cooldowns[ cd ].isTimeout( timeVal ):
				return False
		return True

	def setCooldownInUsed( self, caster ):
		"""
		virtual method.
		给施法者设置法术本身的cooldown时间 (技能使用后 吟唱开始时)

		@return: None
		"""
		if len( self._springOnUsedCD ) <= 0: return
		for cd, time in self._springOnUsedCD:
			try:
				endTime = g_cooldowns[ cd ].calculateTime( time )
			except:
				EXCEHOOK_MSG("skillID:%d" % self.getID())
			if caster.getCooldown( cd ) < endTime:
				caster.changeCooldown( cd, time, time, endTime )

	def setCooldownInIntonateOver( self, caster ):
		"""
		virtual method.
		给施法者设置法术本身的cooldown时间(技能吟唱结束时)

		@return: None
		"""
		if len( self._springOnIntonateOverCD ) <= 0: return
		for cd, time in self._springOnIntonateOverCD:
			try:
				endTime = g_cooldowns[ cd ].calculateTime( time )
			except:
				EXCEHOOK_MSG("skillID:%d" % self.getID())
			if caster.getCooldown( cd ) < endTime:
				caster.changeCooldown( cd, time, time, endTime )

	def getType( self ):
		"""
		取得基础分类类型
		这些值是BASE_SKILL_TYPE_*之一
		"""
		return self._baseType

	def calcExtraRequire( self, caster ):
		"""
		virtual method.
		计算技能消耗的额外值， 由其他装备或者技能BUFF影响到技能的消耗
		return : (额外消耗附加值，额外消耗加成)
		"""
		return ( 0, 0.0 )

	def checkRequire_( self, caster ):
		"""
		virtual method.
		检测消耗是否够
		@return: INT，see also SkillDefine.SKILL_*
		"""
		return self._require.validObject( caster, self )

	def doRequire_( self, caster ):
		"""
		virtual method.
		处理消耗

		@param caster	:	释放者实体
		@type caster	:	Entity
		"""
		self._require.pay( caster, self )

	def getRequire( self ):
		"""
		"""
		return self._require

	def _validCaster( self, caster ):
		"""
		virtual method.
		检查施法者是否满足吟唱条件
		@return: INT，see also SkillDefine.SKILL_*
		"""
		return self._casterCondition.valid( caster )

	def interruptCheck( self, caster, reason ):
		"""
		virtual method.
		用于在吟唱时接收某一类型的中断，判断属于自己需要中断的类型则允许中断（返回True），
		对于不可中断的技能，直接返回 False，默认情况下，我们应该允许玩家主动中断技能的吟唱；
		@param reason: 导致中断原因
		@type  receiver: bool
		"""
		return True

	def onSpellInterrupted( self, caster ):
		"""
		当施法被打断时的通知；
		打断后需要做一些事情
		"""
		pass

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		# 检查技能cooldown
		if not self.isCooldown( caster ):
			return csstatus.SKILL_NOT_READY

		# 施法需求检查
		state = self.checkRequire_( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		# 施法者检查
		state = self.castValidityCheck( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# 检查目标是否符合法术施展
		state = self.getCastObject().valid( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state
			
		#如果处在连击状态
		if caster.inHomingSpell():
			return csstatus.SKILL_CANT_CAST

		return csstatus.SKILL_GO_ON

	def castValidityCheck( self, caster, target):
		"""
		virtual method.
		校验技能是否可以施展。
		此接口仅仅用于当法术吟唱完后判断是否能对目标施展，
		如果需要判断一个法术是否能对目标使用，应该使用intonateValidityCheck()方法。
		此接口会被intonateValidityCheck()接口调用，如果重载时某些条件需要在吟唱结束后判断，
		则必须重载此接口并加入相关判断，否则只能重载intonateValidityCheck()接口。

		注：此接口是旧版中的validCast()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		return self._validCaster( caster )

	def use( self, caster, target ):
		"""
		virtual method.
		请求对 target/position 施展一个法术，任何法术的施法入口由此进。
		dstEntity和position是可选的，不用的参数用None代替，具体看法术本身是对目标还是位置，一般此方法都是由client调用统一接口后再转过来。
		默认啥都不做，直接返回。
		注：此接口即原来旧版中的cast()接口
		@param   caster: 施法者
		@type    caster: Entity

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		if not self.isNotRotate:
			caster.rotateToSpellTarget( target )					# 转向

		# 设置技能冷却时间
		self.setCooldownInUsed( caster )

		if self.getIntonateTime( caster ) <= 0.1 and self.getReceiveDelayTime() <= 0.1:
			# 没有吟唱时间，直接施法
			self.cast( caster, target )
			return

		#这里传入target 吟唱完后对于一个位置来说他仍然是位置，对一个entity来说 entity已经不在
		#这个cell上了那么法术将中断 对于物品找不到拥有者法术将中断

		if self.getReceiveDelayTime() > 0.1:
			caster.intonate( self, target, self.getReceiveDelayTime() )
		else:
			caster.intonate( self, target, self.getIntonateTime( caster )  )# 吟唱


	def cast( self, caster, target ):
		"""
		virtual method.
		正式向一个目标或位置施放（或叫发射）法术，此接口通常直接（或间接）由intonate()方法调用。

		注：此接口即原来旧版中的castSpell()接口

		@param     caster: 使用技能的实体
		@type      caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		# 引导技能检测
		caster.delHomingOnCast( self )
		self.setCooldownInIntonateOver( caster )
		# 处理消耗
		self.doRequire_( caster )
		#通知所有客户端播放动作/做其他事情
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )

		# 法术施放完毕通知，不一定能打中人哦(是否能打中已经和施法没任何关系了)！
		# 如果是channel法术(未实现)，只有等法术结束后才能调用
		self.onSkillCastOver_( caster, target )

		#保证客户端和服务器端处理的受术者一致
		delay = self.calcDelay( caster, target )
		if delay <= 0.5:
			# 瞬发
			#caster.addCastQueue( self, target, 0.1 )
			className = caster.className if caster.className != "" else caster.id
			CPU_CostCal( csdefine.CPU_COST_SKILL, csdefine.CPU_COST_SKILL_ARRIVE, self.getID(), className )
			self.onArrive( caster, target )
			CPU_CostCal( csdefine.CPU_COST_SKILL, csdefine.CPU_COST_SKILL_ARRIVE, self.getID(), className )
		else:
			# 延迟
			caster.addCastQueue( self, target, delay )
		
		#这里处理可以获得多少格斗点数
		if hasattr( caster, "calCombatCount" ) and self._getCombatCount >0 :
			caster.calCombatCount( self._getCombatCount )

	def trapCast( self, caster, target ):
		"""
		virtual method.
		陷阱触发技能专用进入接口
		"""
		#通知所有客户端播放动作/做其他事情
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )

		# 法术施放完毕通知，不一定能打中人哦(是否能打中已经和施法没任何关系了)！
		# 如果是channel法术(未实现)，只有等法术结束后才能调用
		self.onSkillCastOver_( caster, target )

		#保证客户端和服务器端处理的受术者一致
		delay = self.calcDelay( caster, target )
		if delay <= 0.1:
			# 瞬发
			#caster.addCastQueue( self, target, 0.1 )
			self.onArrive( caster, target )
		else:
			# 延迟
			caster.addCastQueue( self, target, delay )


	def onSkillCastOver_( self, caster, target ):
		"""
		virtual method.
		法术施放完毕通知
		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		# 通知施法者
		# 这是一次技能施法通知
		if not caster.isDestroyed:
			caster.onSkillCastOver( self, target )

	def getReceivers( self, caster, target ):
		"""
		virtual method
		取得所有的符合条件的受术者Entity列表；
		所有的onArrive()方法都应该调用此方法来获取有效的entity。
		@return: array of Entity

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@rtype: list of Entity
		"""
		return self._receiverObject.getReceivers( caster, target )

	def onArrive( self, caster, target ):
		"""
		法术抵达目标通告。在默认情况下，此处执行可受术人员的获取，然后调用receive()方法进行对每个可受术者进行处理。
		注：此接口为旧版中的receiveSpell()
		特别注意:此方法重载时必须继承基类Spell中的onArrive方法
		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		# 获取所有受术者
		receivers = self.getReceivers( caster, target )
		for receiver in receivers:
			#法术到达时发生的一些事情
			receiver.clearBuff( self._triggerBuffInterruptCode ) # 必须放在前面，因为在后面有可能被销毁等
			self.receive( caster, receiver )
			self.receiveEnemy( caster, receiver )

		if not caster.isDestroyed:
			caster.onSkillArrive( self, receivers )


	def springOnHit( self, caster, receiver, damageType ):
		"""
		技能命中时的消息回调
		@param   caster: 施法者
		@type    caster: Entity
		@param   receiver: 受术者
		@type    receiver: Entity
		@param   damageType: 伤害类别
		@type    damageType: uint32
		"""
		caster.spellTarget( self.getID(), receiver.id )


	def receive( self, caster, receiver ):
		"""
		virtual method = 0.
		针对每一个受术者进行受术处理，如计算伤害、改变属性等等。通常情况下此接口是由onArrive()调用，
		但它亦有可能由SpellUnit::receiveOnreal()方法调用，用于处理一些需要在受术者的real entity身上作的事情。
		但对于是否需要在real entity身上接收，由技能设计者在receive()中自行判断，并不提供相关机制。
		注：此接口为旧版中的onReceive()

		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		pass

	def canLinkBuff( self, caster, receiver, buff ):
		"""
		判定buff是否能够link
		@param   caster	: 施法者
		@type    caster	: Entity
		@param   buff	: BUFF数据
		@type    buff	: BUFFInstance
		@return 		: BOOL
		"""
		odds = buff.getLinkRate()
		if caster:
			skillID = self.getID()/1000
			odds += caster.skillBuffOdds.getOdds( skillID ) * 100 

		if randint( 1, 100 ) > odds:
			caster.onBuffMiss( receiver, self )
			return False

		if buff.getBuff().checkResist( caster, receiver ):
			caster.onBuffResist( receiver, buff )
			receiver.onBuffResistHit( buff )
			return False

		return True

	def receiveLinkBuff( self, caster, receiver ):
		"""
		给entity附加buff的效果
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 施展对象
		@type  receiver: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		for buff in self._buffLink:
			if self.canLinkBuff( caster, receiver, buff ):
				buff.getBuff().receive( caster, receiver )				# 接收buff，receive()会自动判断receiver是否为realEntity
				
#
# Spell.py
