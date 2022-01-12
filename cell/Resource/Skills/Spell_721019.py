# -*- coding: gb18030 -*-

# 

import BigWorld
import csdefine
import csstatus
import ItemTypeEnum
import random
from SpellBase import *
from bwdebug import *
from Spell_BuffNormal import Spell_BuffNormal_With_Homing
import CooldownFlyweight
g_cooldowns = CooldownFlyweight.CooldownFlyweight.instance()

BUFF_TARGET_CASTER = 1
BUFF_TARGET_RECEIVER = 2

class Spell_721019( Spell_BuffNormal_With_Homing ):
	"""
	系统技能
	"该技能同时存在对目标的DEBUFF和对自身的BUFF，普通BUFF技能不能满足要求。
	同时，必须判断首先对目标的DEBUFF施放成功（目标获得此DEBUFF），才能产生对自身的BUFF
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		icd = dict["param3"].split(" ") if len( dict["param3"] ) > 0 else []
		self._internalCD = []
		for i in icd:
			datas = i.split(":")
			self._internalCD.append( (int(datas[0]), int(datas[1]) ) )

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
		self.receiveLinkBuff( caster, receiver )
		
	def receiveLinkBuff( self, caster, receiver ):
		"""
		给entity附加buff的效果
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 施展对象
		@type  receiver: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		if len( self._buffLink ) <= 0:
			return
		_buff = self._buffLink[0]
		rate = _buff.getLinkRate()
		odd = random.randint( 1, 100 )
		# 有产生机率则判断机率
		if odd > rate:
			return
		self.setInternalCooldownInIntonate( caster )	# 设置内部CD
		buff_successed = False
		for bl in self._buffLink:
			buff = bl.getBuff()
			if buff.param3 is None or buff.param3 == "":
				continue
			if int(buff.param3) == BUFF_TARGET_CASTER:
				buff.receive( caster, caster )
			elif int(buff.param3) == BUFF_TARGET_RECEIVER:
				buff.receive( caster, receiver )
			buff_successed = True
		# 蛋疼到 无以复加 的神器技能提示
		if buff_successed and caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
			weapon = caster.getItem_( ItemTypeEnum.CEL_RIGHTHAND )
			if weapon and weapon.getType() in ItemTypeEnum.WEAPON_LIST and weapon.getGodWeaponSkillID() == self.getID():
				caster.statusMessage( csstatus.GW_SKILL_TRIGGERED, self.getName() )
			
	def cast( self, caster, target ):
		"""
		去除父类接口中关于引导技能的检测，话说俺到是觉得引导检测这种东西不适合扔底层咧
		"""
		self.setCooldownInIntonateOver( caster )
		# 处理消耗
		self.doRequire_( caster )
		#通知所有客户端播放动作/做其他事情
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )

		#保证客户端和服务器端处理的受术者一致
		delay = self.calcDelay( caster, target )
		if delay <= 0.1:
			# 瞬发
			caster.addCastQueue( self, target, 0.1 )
		else:
			# 延迟
			caster.addCastQueue( self, target, delay )

		# 法术施放完毕通知，不一定能打中人哦(是否能打中已经和施法没任何关系了)！
		# 如果是channel法术(未实现)，只有等法术结束后才能调用
		self.onSkillCastOver_( caster, target )
			
	def setInternalCooldownInIntonate( self, caster ):
		"""
		特殊需求
		给施法者设置法术该技能内部的cooldown时间(buff成功释放时)

		@return: None
		"""
		endTime = 0
		if len( self._internalCD ) <= 0:
			ERROR_MSG( "Internal cooldown config error, skill: %i ."%self.getID() )
			return
		for cd, time in self._internalCD:
			try:
				endTime = g_cooldowns[ cd ].calculateTime( time )
			except:
				EXCEHOOK_MSG("skillID:%d" % self.getID())
			if caster.getCooldown( cd ) < endTime:
				caster.changeCooldown( cd, time, time, endTime )