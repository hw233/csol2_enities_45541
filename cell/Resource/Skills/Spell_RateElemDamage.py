# -*- coding: gb18030 -*-
#
# $Id: Spell_RateElemDamage.py,v 11:09 2010-8-27 jiangyi Exp $

import random
import csdefine
import csstatus
import ItemTypeEnum
import CooldownFlyweight
from bwdebug import *
from Spell_ElemDamage import Spell_ElemDamage
from SpellBase import *

g_cooldowns = CooldownFlyweight.CooldownFlyweight.instance()

class Spell_RateElemDamage( Spell_ElemDamage ):
	"""
	一定概率产生元素伤害技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_ElemDamage.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		self._rate = int( dict["param1"] if len(dict["param1"]) > 0 else 0 )	# 0 ~ 100
		icd = dict["param3"].split(" ") if len( dict["param3"] ) > 0 else []
		self._internalCD = []
		for i in icd:
			datas = i.split(":")
			self._internalCD.append( (int(datas[0]), int(datas[1]) ) )
		Spell_ElemDamage.init( self, dict )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if random.uniform(0,100) > self._rate:
			return
		self.setInternalCooldownInIntonate( caster )	# 设置内部CD
		# 蛋疼到 无以复加 的神器技能提示
		if caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
			weapon = caster.getItem_( ItemTypeEnum.CEL_RIGHTHAND )
			if weapon and weapon.getType() in ItemTypeEnum.WEAPON_LIST and weapon.getGodWeaponSkillID() == self.getID():
				caster.statusMessage( csstatus.GW_SKILL_TRIGGERED, self.getName() )
		if receiver.isDestroyed:
			return

		damageType = self._damageType
		
		# 计算命中率
		hit = self.calcHitProbability( caster, receiver )
		if receiver.effect_state & csdefine.EFFECT_STATE_INVINCIBILITY > 0 or not random.random() < hit:
			# 被躲开了并不代表我没打你，因此仇恨是有可能存在的，需要通知受到0点伤害
			receiver.receiveSpell( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0, 0 )
			receiver.receiveDamage( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0 )
			return
		
		# 计算技能攻击力和计算直接伤害
		skillDamage = self.calcSkillHitStrength( caster, receiver, 0, 0 )
		attackdamage = self.calcDamage( caster, receiver, skillDamage )

		# 计算元素伤害 元素伤害列表 按次序分别为 火玄雷冰4个元素所产生的伤害
		elemDamageList = self.calcElemDamage( caster, receiver )

		# 给出受击装备伤害
		equipmentDamage = int( skillDamage - attackdamage )
		receiver.equipDamage( equipmentDamage )

		# 判断是否爆击
		if self.isDoubleHit( caster, receiver ):
			damageType |= csdefine.DAMAGE_TYPE_FLAG_DOUBLE
			dm = self.calcDoubleMultiple( caster )
			# 普通伤害暴击
			attackdamage *= dm
			# 元素暴击
			elemDamageList = [ x * dm for x in elemDamageList ]
			# 执行成功暴击后的行为
			caster.doAttackerOnDoubleHit( receiver, damageType )	# 攻击者触发
			receiver.doVictimOnDoubleHit( caster, damageType )   	# 受击者触发

		# 计算此次攻击的招架 执行成功招架后的行为
		if self.isResistHit( caster, receiver ):
			caster.doAttackerOnResistHit( receiver, damageType )	# 攻击者触发
			receiver.doVictimOnResistHit( caster, damageType )   	# 受击者触发
			attackdamage -= attackdamage * receiver.resist_hit_derate
			damageType |= csdefine.DAMAGE_TYPE_RESIST_HIT

		# 伤害削减  因为这个流程之后其他功能会参考此次的消减后的最终伤害所以此接口不能放到receiveDamage中
		attackdamage = self.calcDamageScissor( caster, receiver, attackdamage )

		# 元素伤害消减
		self.calcElemDamageScissor( receiver, elemDamageList )

		# 计算原始最终伤害
		basedamage = attackdamage + elemDamageList[0] + elemDamageList[1] + elemDamageList[2] + elemDamageList[3]
		
		# 护盾吸收 因为这个流程之后其他功能会参考此次的消减后的最终伤害所以此接口不能放到receiveDamage中
		finiDamage = self.calcShieldSuck( caster, receiver, attackdamage, self._damageType, elemDamageList )
		
		# 附加元素伤害
		finiDamage_ss = finiDamage + elemDamageList[0] + elemDamageList[1] + elemDamageList[2] + elemDamageList[3]

		# 显示护盾所抵抗的伤害
		if basedamage - finiDamage_ss > 0:
			SkillMessage.spell_DamageSuck( caster, receiver, int( basedamage - finiDamage_ss  ) )
		
		#计算御敌、破敌带来的实际减免 
		reRate = self.calReduceDamage( caster, receiver )
		rm =  1 - reRate
		finiDamage *= rm
		elemDamageList = [ x * rm for x in elemDamageList ]
		
		finiDamage +=  elemDamageList[0] + elemDamageList[1] + elemDamageList[2] + elemDamageList[3]
		
		# 怪物和玩家等级差别造成的伤害变动 by姜毅
		finiDamage = self.damageWithLevelWave( caster, receiver, finiDamage )

		# 给出手击者伤害 最少也得造成1点伤害
		self.persentDamage( caster, receiver, damageType, max( 1, int( finiDamage ) ) )
		self.receiveLinkBuff( caster, receiver )					# 接收额外的CombatSpell效果，通常是buff(如果存在的话)
		
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