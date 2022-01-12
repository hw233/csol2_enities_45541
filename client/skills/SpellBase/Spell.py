# -*- coding: gb18030 -*-
#
# $Id: Spell.py,v 1.48 2008-08-26 08:00:56 yangkai Exp $

"""
Spell技能类。
"""
import BigWorld
from bwdebug import *
from Function import Functor
import csdefine
import csstatus
import csconst
import GUIFacade
from event.EventCenter import *
from csdefine import *
from SkillBase import SkillBase
from Buff import Buff
from SmartImport import smartImport
import ObjectDefine
import AreaDefine
import RequireDefine
from CasterCondition import CasterCondition
import ReceiverObject
import skills
import event.EventCenter as ECenter
from gbref import rds
from Time import Time
import time
import Const
from interface.CombatUnit import CombatUnit
from config.client.NpcSkillName import Datas as npcSkillName

class Spell( SkillBase ):
	"""
	主动技能模块
	"""
	def __init__( self ):
		"""
		构造SkillBase
		"""
		SkillBase.__init__( self )
		self._casterCondition = CasterCondition()					# 施法者可以施法的要求(判断一个施法者是否能施展这个法术)
		self._receiverObject = ReceiverObject.newInstance( 0, self )# 受术者对象，其中包括受术者的一些合法性判断
		self._require = RequireDefine.newInstance( None )			# see also RequireDefine; 施放法术消耗的东西; 默认为"None"，无需求
		self._buffLink	= []										# 技能产生的BUFF [buffInstance...]
		self._effectState = 0										# 目前单体技能似乎都是恶性的 因此当前这么写。
		self.isNotRotate = False									# 施法是否需要转向
		self.target = None

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type  dict:			python dict
		"""
		SkillBase.init( self, dict )
		# 施展目标类型，see also CAST_OBJECT_TYPE_*
		self._castObject = ObjectDefine.newInstance( self.getCastObjectType(), self )
		self._castObject.init( dict[ "CastObjectType" ] )
		self.isNotRotate = dict.get( "isNotRotate", 0 )

		# 施法需求
 		if len( dict[ "Require" ] ) > 0: #list
			self._require = RequireDefine.newInstance( dict["Require"] )		# 施放法术消耗的东西

		if len( dict[ "CasterCondition" ] ) > 0: #dict
			self._casterCondition.init( dict["CasterCondition"] )

		if len( dict[ "ReceiverCondition" ] ) > 0: #dict
			conditions = dict["ReceiverCondition"][ "conditions" ]
			if len( conditions ) > 0:
				self._receiverObject = ReceiverObject.newInstance( eval( dict["ReceiverCondition"][ "conditions" ] ), self )
				self._receiverObject.init( dict["ReceiverCondition"] )

		if dict.has_key( "buff" ): #list
			index = 0
			for datI in xrange( len( dict[ "buff" ] ) ):
				dat = dict[ "buff" ][datI]
				inst = None
				if len( dat[ "ClientClass" ] ) > 0:
					buffclass = "skills." + dat[ "ClientClass" ]
					inst = smartImport( buffclass )()
				else:
					inst = Buff()
				inst.init( dat )
				inst.setSource( self.getID(), index )
				self._buffLink.append( inst )
				skills.register( inst.getID(), inst )
				index += 1

	def isMalignant( self ):
		"""
		virtual method.
		判断法术效果是否为恶性
		这个接口将来可能有问题，  因为当前单体技能都是恶性的， 所以默认是恶性的， 如果
		这个技能所附带的 BUFF全部是良性的 那么它被改变为良性， 如果BUFF中有一个是恶性的 那么这个技能是恶性的。
		"""
		effectState = self._datas[ "EffectState" ]
		return effectState in [ csdefine.SKILL_EFFECT_STATE_MALIGNANT, csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT ]

	def isNeutral( self ):
		"""
		是否是中性技能
		"""
		return self._datas[ "EffectState" ] == csdefine.SKILL_EFFECT_STATE_NONE

	def getIntonateTime( self ):
		"""
		获得该技能的基础吟唱时间（不受其他因素影响 ），主要提供给界面使用
		@return:		释放时间
		@rtype:			float
		"""
		return self._datas[ "IntonateTime" ]			# 吟唱时间
	
	def getReceiveDelayTime( self ):
		"""
		类似技能前摇时间
		"""
		return self._datas.get( "receiveDelayTime", 0.0 )

	def getSpringOnUsedCD( self ):
		"""
		获得释放该技能所需CoolDown 时间
		"""
		return  self._datas[ "SpringUsedCD" ]

	def getSpringOnIntonateOverCD( self ):
		"""
		获得_springOnIntonateOverCD
		"""
		return self._datas[ "SpringIntonateOverCD" ]

	def getLimitCooldown( self ):
		"""
		获得释放该技能所需的受限技能
		"""
		return self._datas[ "LimitCD" ]

	def getRequire( self ):
		"""
		获得释放该技能所需消耗
		"""
		return self._require

	def getType( self ):
		"""
		@return: 技能类型
		"""
		if self._datas.has_key( "Type" ):
			return eval( 'csdefine.' + self._datas[ "Type" ] )
		return csdefine.BASE_SKILL_TYPE_NONE					# 技能类别

	def getFlySpeed( self ):
		"""
		@return: 法术的飞行速度
		"""
		return self._datas[ "Speed" ]

	def getCastRange( self, role ):
		"""
		@return: 法术的释放距离
		"""
		if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS or self.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			val1 = role.magicSkillRangeVal_value
			val2 = role.magicSkillRangeVal_percent
			if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
				val1 = role.phySkillRangeVal_value
				val2 = role.phySkillRangeVal_percent
			return ( self._datas[ "CastRange" ] + val1 ) * ( 1 + val2 / csconst.FLOAT_ZIP_PERCENT )
		return self._datas[ "CastRange" ]

	def getBuffLink( self ):
		"""
		@return: 技能产生的BUFF [buffInstance,...]
		"""
		return self._buffLink

	def getRangeMax( self, role ):
		"""
		获得射程。
		"""
		if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS or self.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			val1 = role.magicSkillRangeVal_value
			val2 = role.magicSkillRangeVal_percent
			if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
				val1 = role.phySkillRangeVal_value
				val2 = role.phySkillRangeVal_percent
			return ( self._datas[ "RangeMax" ] + val1 ) * ( 1 + val2 / csconst.FLOAT_ZIP_PERCENT )
		return self._datas[ "RangeMax" ]

	def getPosture( self ) :
		"""
		获取技能所需姿态
		"""
		for condition in self._casterCondition :
			if condition.GetConditionType() == csdefine.CASTER_CONDITION_POSTURE :
				return condition.posture
		return SkillBase.getPosture( self )

	def calcExtraRequire( self, role ):
		"""
		virtual method.
		计算技能消耗的额外值， 由其他装备或者技能BUFF影响到技能的消耗
		return : (额外消耗附加值，额外消耗加成)
		"""
		if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS or self.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			val1 = role.magicManaVal_value
			val2 = role.magicManaVal_percent
			if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
				val1 = role.phyManaVal_value
				val2 = role.phyManaVal_percent
			return ( val1, val2 / csconst.FLOAT_ZIP_PERCENT )
		return ( 0, 0.0 )

	def getRangeMin( self, caster ):
		"""
		virtual method.
		@param caster: 施法者，通常某些需要武器射程做为距离的法术就会用到。
		@return: 施法最小距离
		"""
		return self._datas[ "RangeMin" ]

	def isCooldownType( self, cooldownType ):
		"""
		判断自身是否与某一类型的cooldown相同

		@param cooldownType: cooldown类型
		@type  cooldownType: INT
		@return: bool
		"""
		return cooldownType in self.getLimitCooldown()

	def isCooldown( self, caster ):
		"""
		判断法术的cooldown是否已过

		@return: BOOL
		"""
		for cd in self.getLimitCooldown():
			endTime = caster.getCooldown( cd )[3]
			if endTime > Time.time():	# getCooldown modified by hyw( 08.01.31 )
				return False
		return True

	def isHomingSkill( self ):
		"""
		判断是否引导技能 	by 姜毅
		@return: BOOL
		"""
		return False
		
	def isMoveSpell( self ):
		"""
		判断是否是作用区域技能 by wuxo 2012-4-28
		@return: BOOL
		"""
		return False
	
	def isTriggerSkill( self ):
		"""
		判断是否触发连续技能  add by wuxo 2012-2-20
		@return: BOOL
		"""
		return False
	
	def isNormalHomingSkill( self ):
		"""
		判断是否引导普通攻击技能 by wuxo
		@return: BOOL
		"""
		return False

	def isTargetPositionSkill( self ):
		"""
		判断是否是位置光效技能
		@return: BOOL
		"""
		return False

	def getCooldownData( self, caster ):
		"""
		获取该技能所受cooldown的相关数据
		@return type: ( 最后结束的 cooldown 起始时间, 最后结束的 cooldown 结束时间 )
		modified by hyw( 08.01.31 )
		"""
		totalTime, endTime = 0, 0
		for cdID in self.getLimitCooldown() :
			cdData = caster.getCooldown( cdID )
			t = cdData[1]
			e = cdData[3]
			if e > Time.time() and e > endTime :
				totalTime, endTime = t, e
		return totalTime, endTime

	def getCastObjectType( self ):
		"""
		virtual method.
		取得法术可施法的目标对像类型。

		@return: CAST_OBJECT_TYPE_*
		@rtype:  INT8
		"""
		return self._datas["CastObjectType"][ "type" ]

	def getCastObject( self ):
		"""
		virtual method.
		取得法术可施法的目标对像定义。
		@rtype:  ObjectDefine Instance
		"""
		return self._castObject

	def getCastTargetLevelMin( self ):
		"""
		virtual method = 0.
		技能可施展对象最底级
		"""
		return self._datas[ "CastObjLevelMin" ]

	def getCastTargetLevelMax( self ):
		"""
		virtual method = 0.
		技能可施展对象最高级
		"""
		return self._datas[ "CastObjLevelMax" ]

	def _checkRequire( self, caster ):
		"""
		virtual method.
		检测消耗是否够

		@return: INT，see also csdefine.SKILL_*
		"""
		return self._require.validObject( caster, self )

	def validCaster( self, caster ):
		"""
		virtual method.
		判断施法者是否符合施法要求

		@return: INT，see also csdefine.SKILL_*
		"""
		if hasattr( caster, "state" ):
			if caster.state == csdefine.ENTITY_STATE_DEAD:	# 对施法者是否死亡的判断写在脚本里，不需要配置。
				return csstatus.SKILL_IN_DEAD

		return self._casterCondition.valid( caster )

	def validTarget( self, caster, target ):
		"""
		virtual method.
		判断施法目标是否符合施法要求

		@return: INT，see also csdefine.SKILL_*
		"""
		return self._castObject.valid( caster, target )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		# 检查是否可以施法
		if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_PHY ) or caster.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
				return csstatus.SKILL_CANT_CAST
		elif self.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_MAGIC ) or caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
				 return csstatus.SKILL_CANT_CAST

		# 检查施法者条件是否满足
		state = self.validCaster( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		# 检查目标是否符合
		state = self.validTarget( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# 检查施法者的消耗是否足够
		state = self._checkRequire( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		if caster.intonating():
			return csstatus.SKILL_INTONATING

		# 检查玩家是否处于竞技场死亡隐身或GM观察者状态
		player = BigWorld.player()
		if caster == player:
			if caster.isDeadWatcher() or caster.isGMWatcher():
				return csstatus.SKILL_NOT_IN_POSTURE
				
		if hasattr( caster, "isInHomingSpell" ) and caster.isInHomingSpell:
			return csstatus.SKILL_CANT_CAST
		if caster.effect_state & csdefine.EFFECT_STATE_BE_HOMING:
			return csstatus.SKILL_CANT_CAST

		# 检查技能cooldown 根据快捷栏变色的需求调整技能条件的判断顺序 这个只能放最后
		if not self.isCooldown( caster ):
			return csstatus.SKILL_NOT_READY
		
		return csstatus.SKILL_GO_ON

	def spell( self, caster, target ):
		"""
		向服务器发送Spell请求。

		@param caster:		施放者Entity
		@type  caster:		Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT, see also csdefine.SKILL_*
		"""
		skillID = self.getID()
		sk_id = str( skillID )[:-3]	 # 取前六位判断
		if not sk_id: sk_id = "0"
		orgSkillID = int( sk_id )
		if BigWorld.player().id == caster.id and ( not orgSkillID in Const.JUMP_SPELL_SKILLS ) :	# 特殊技能跳跃中可以主动施法，如离弦破空等
			if caster.isJumping():		# 跳跃中不允许主动施法
				caster.statusMessage( csstatus.SKILL_ROLE_IS_JUMPING )
				return

		if hasattr( target.getObject(), "level" ) and self.getCastTargetLevelMin() > target.getObject().level:
			# 施展目标级别太低了
			skillID = skills.binarySearchSKillID( target.getObject().level, self.getID() )
			if skillID != -1:
				tempSkill = skills.getSkill( skillID )
				caster.statusMessage( csstatus.SKILL_TARGET_ENTITY_LEVE_MIN_USE, tempSkill.getLevel(), tempSkill.getName() )

		caster.useSpell( skillID, target )
		if hasattr( caster, "showSpellingItemCover" ) :
			caster.showSpellingItemCover( self.getID() )

		if not self.isNotRotate:
			castObjectType = self.getCastObjectType()
			if castObjectType == 0:
				# 无目标和位置
				pass
			elif castObjectType == 1:
				# 位置
				self.rotate( caster, target.getObject() )
			elif castObjectType == 2:
				# 目标Entity
				self.rotate( caster, target.getObject() )
			elif castObjectType == 3:
				# 对物品
				self.rotate( caster, target.getOwner() )
			elif castObjectType == 4:
				# 对多目标Entity
				self.rotate( caster, target.getObject() )

	def rotate( self, caster, receiver ):
		"""
		转动方向
		"""
		if caster.id == receiver.id:
			return
		#中了昏睡、眩晕、定身等效果时不能自动转向
		EffectState_list = csdefine.EFFECT_STATE_FIX | csdefine.EFFECT_STATE_VERTIGO | csdefine.EFFECT_STATE_SLEEP |csdefine.EFFECT_STATE_BE_HOMING
		if caster.effect_state & EffectState_list != 0: return
		new_yaw = (receiver.position - caster.position).yaw
		# yaw差距大于10度时才转向
		if abs( caster.yaw - new_yaw ) > 0.0:
			caster.turnaround( receiver.matrix, None )

	def interrupt( self, caster, reason ):
		"""
		中止施放技能。
		@param caster:			施放者Entity
		@type caster:			Entity
		"""
		if reason not in [ csstatus.SKILL_INTONATING, csstatus.SKILL_NOT_HIT_TIME, csstatus.SKILL_NOT_READY,csstatus.SKILL_CANT_CAST,csstatus.SKILL_INTERRUPTED_BY_TIME_OVER]  :
			if hasattr( caster, "hideSpellingItemCover" ) :
				caster.hideSpellingItemCover()
			caster.isInterrupt = True
			self.pose.interrupt( caster )
			rds.skillEffect.interrupt( caster )
			if caster.effect.has_key( self.getID() ):
				caster.effect.pop( self.getID() )
		if BigWorld.player().id == caster.id :
			caster.flushAction()

	def intonate( self, caster, intonateTime, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		"""
		caster.isInterrupt = False
		caster.hasCast = False
		skillID = self.getID()
		# 动作播放
		result = self.pose.intonate( caster, skillID, Functor( self.onStartActionEnd, caster, caster ) )
		if not result:
			self.onStartActionEnd( caster, caster )
		# 光效播放
		rds.skillEffect.playBeginEffects( caster, targetObject, skillID )
		# 界面吟唱条
		if BigWorld.player().id == caster.id :
			self.target = rds.targetMgr.getTarget()
			if self.getReceiveDelayTime() <= 0.1:
				lastTime = intonateTime
				GUIFacade.onSkillIntonate( lastTime )
			self.onCheckTarget()

	def onCheckTarget( self ):
		"""
		吟唱过程受术者检测
		"""
		player = BigWorld.player()
		if player is None:
			self.target = None
			return
		if player.hasCast:
			self.target = None
			return
		if player.isInterrupt:
			self.target = None
			return
		if self.target is None:
			return
		# 受术者不存在
		if not self.target.inWorld:
			self.target = None
			player.interruptAttack( csstatus.SKILL_TARGET_NOT_EXIST )
			return
		# 受术者是无效目标
		if ( not self.target.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and self.target.hasFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED ) ) or \
			self.target.hasFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE ):
				self.target = None
				player.interruptAttack( csstatus.SKILL_NO_TARGET )
				return
		# 受术者已死亡
		if isinstance( self.target, CombatUnit ):
			if self.target.isDead():
				self.target = None
				player.interruptAttack( csstatus.SKILL_TARGET_DEAD )
				return
		BigWorld.callback( 0.1, self.onCheckTarget )

	def onStartActionEnd( self, caster, target ):
		"""
		吟唱动作结束，可以播放循环动作的光效等。
		"""
		#DEBUG_MSG( "Spell", self.getName(), caster.id  )
		# 因为异步的关系，有可能在播放loop效果的时候收到了中断消息，
		# 这时候直接中断不让loop效果播放
		if not caster.inWorld: return
		if caster.isInterrupt: return
		# 因为异步的关系，有可能在播放Loop效果的时候Cast效果已经播放了
		# 这时候直接中断不让loop效果播放
		if caster.hasCast: return
		self.pose.onStartActionEnd( caster )	# 通知pose起手动作播放完毕
		
	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		caster.hasCast = True
		skillID = self.getID()

		# 对动作而言，我只会播放一次
		self.pose.cast( caster, skillID, targetObject )
		if hasattr( caster,"isLoadModel" ) and caster.isLoadModel:
			caster.delayCastEffects.append( Functor( rds.skillEffect.playCastEffects, caster, targetObject, skillID ) )
		else:
			rds.skillEffect.playCastEffects( caster, targetObject, skillID )

		# 技能名称显示
		speller = caster  #重新赋值，防止后面调用混乱
		if hasattr( speller, 'getOwner' ):
			speller = speller.getOwner()

		player = BigWorld.player()
		if player is None: return
		if speller is None: return

		if player.position.distTo( speller.position ) > 20: return
		if hasattr( caster, "className" ):
			sk_id = str( skillID )[:-3]
			if not sk_id: return		# 如果为空，直接返回
			orgSkillID = int( sk_id )	# 支持配置表可变等级NPC技能填写
			skillIDs = npcSkillName.get( caster.className, [] )
			if orgSkillID in skillIDs or skillID in skillIDs:
		 		caster.showSkillName( skillID )
				return
		if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or caster.isEntityType( csdefine.ENTITY_TYPE_PET ):
			caster.showSkillName( skillID )

	def _skillAE( self, player, target, caster, damageType, damage ):
		"""
		技能产生伤害时的动作效果等处理
		@param player:			玩家自己
		@type player:			Entity
		@param target:			Spell施放的目标Entity
		@type target:			Entity
		@param caster:			Buff施放者 可能为None
		@type castaer:			Entity
		@param damageType:		伤害类型
		@type damageType:		Integer
		@param damage:			伤害数值
		@type damage:			Integer
		"""
		if damageType & csdefine.DAMAGE_TYPE_REBOUND == csdefine.DAMAGE_TYPE_REBOUND:
			return
		id = self.getID()
		if caster and damage != 0:
			self.pose.hit( id, target )
			rds.skillEffect.playHitEffects( caster, target, id )
		rds.skillEffect.playCameraEffects( caster, target, id )
