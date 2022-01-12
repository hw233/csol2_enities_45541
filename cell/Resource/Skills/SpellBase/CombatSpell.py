# -*- coding: gb18030 -*-
#
# $Id: CombatSpell.py,v 1.37 2008-08-11 06:01:33 kebiao Exp $

"""
法术。
"""

import Language
import csdefine
import csstatus
from bwdebug import *
from csdefine import *
from Spell import Spell,BuffData
from SkillAttack import SkillAttack
import Const
import random
import csconst
import SkillMessage

class CombatSpell( Spell, SkillAttack ):
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		SkillAttack.__init__( self )

	def init( self, dictDat ):
		"""
		读取技能配置
		"""
		Spell.init( self, dictDat )
		SkillAttack.init( self, dictDat )

	def onReceiveBefore_( self, caster, receiver ):
		"""
		virtual method = 0.
		接受法术之前所要做的事情
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		pass

	def onHit( self, damageType, caster, receiver ):
		"""
		本技能命中后回调 by 姜毅
		"""
		pass

	def persentDamage( self, caster, receiver, damageType, damage ):
		"""
		virtual method.
		对受术者呈现最终伤害
		通常用于这些情况需要重载 需要根据对某entity所产生的伤害 进行其他方面的影响
		"""
		# 伤害分享 最终伤害是给目标的， 分享伤害是给自己的
		
		finiDamage = damage
		shareDamage = 0
		if caster.damage_share_percent > 0:
			finiDamage = max( 1, damage * ( 1 - ( caster.damage_share_percent / csconst.FLOAT_ZIP_PERCENT ) ) )
			shareDamage = damage - finiDamage

		if shareDamage > 0:
			caster.receiveSpell( receiver.id, self.getID(), damageType, shareDamage, 0 )
			caster.receiveDamage( receiver.id, self.getID(), damageType, shareDamage )

		receiver.receiveSpell( caster.id, self.getID(), damageType, finiDamage, 0 )
		receiver.receiveDamage( caster.id, self.getID(), damageType, finiDamage )

		# 有可能是远程技能， 到达目标后施法者在这个过程中已经死亡了。
		if not caster.isDestroyed:
			caster.doAttackerAfterDamage( self, receiver, finiDamage )
		# 有可能是远程技能，到达目标之前，目标就已经死亡。
		if not receiver.isDestroyed:
			receiver.doVictimOnDamage( self, caster, finiDamage )
			receiver.reboundDamage( caster.id, self.getID(), finiDamage, damageType )

	def isDoubleHit( self, caster, receiver ):
		"""
		virtual method.
		判断攻击者是否爆击
		return type:bool
		"""
		return random.random() < ( caster.double_hit_probability + ( receiver.be_double_hit_probability - receiver.be_double_hit_probability_reduce ) / csconst.FLOAT_ZIP_PERCENT )

	def isResistHit( self, caster, receiver ):
		"""
		virtual method.
		判断被攻击者是否招架
		return type:bool
		"""
		return random.random() < receiver.resist_hit_probability

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
		caster.doOnUseSkill( self )	# 触发技能使用时的列表 处理其他导致 吟唱时间 或 XX 消耗的改变
		Spell.use( self, caster, target )

	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		法术抵达目标通告。在默认情况下，此处执行可受术人员的获取，然后调用receive()方法进行对每个可受术者进行处理。
		注：此接口为旧版中的receiveSpell()

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""

		# 获取所有受术者
		receivers = self.getReceivers( caster, target )
		# 不管有没有击中目标，不管攻击几个目标，攻击几次
		caster.equipAbrasion( 100.0 )

		for receiver in receivers:
			# 法术接收之前所做的工作
			receiver.clearBuff( self._triggerBuffInterruptCode )
			self.onReceiveBefore_( caster, receiver )
			self.receive( caster, receiver )
			# 对接收者而言，不管技能是否命中，不管技能攻击几次
			# 添加仇恨
			self.receiveEnemy( caster, receiver )
			# 在receive之后可能角色已经死亡了
			if caster.isDestroyed:
				return

		# 恶性技能使用触发
		caster.doOnUseMaligSkill( self )
		if not caster.isDestroyed:
			caster.onSkillArrive( self, receivers )

	def onMiss( self, damageType, caster, receiver ):
		"""
		技能未命中
		"""
		# 被躲开了并不代表我没打你，因此仇恨是有可能存在的，需要通知受到0点伤害
		receiver.receiveSpell( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0, 0 )
		receiver.receiveDamage( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0 )
		caster.doAttackerOnDodge( receiver, damageType )
		receiver.doVictimOnDodge( caster, damageType )
		
	def calReduceDamage( self,caster, receiver ):
		"""
		计算实际减伤率
		等级修正 = (攻方等级-守方等级)*4% 
		实际减伤=MAX(守方御敌属性-攻方破敌属性-等级修正,0) 
		"""
		disLevel = 0
		if caster.level  > receiver.level:
			disLevel = ( caster.level - receiver.level ) * 0.04
		
		return max( receiver.reduce_role_damage - caster.add_role_damage - disLevel, 0.0 )
		
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if receiver.isDestroyed:
			return

		damageType = self._damageType

		# 计算命中率
		hit = self.calcHitProbability( caster, receiver )
		if receiver.effect_state & csdefine.EFFECT_STATE_INVINCIBILITY > 0 or not random.random() < hit:
			self.onMiss( damageType, caster, receiver )				# 本技能未命中
			return

		# 执行命中后的行为
		caster.doAttackerOnHit( receiver, damageType )				# 攻击者触发
		receiver.doVictimOnHit( caster, damageType )				# 受击者触发
		self.onHit( damageType, caster, receiver )					# 本技能命中后回调

		if caster.queryTemp( "ELEM_ATTACK_EFFECT", "" ):	# 如果有元素攻击效果，则用另外的伤害计算流程
			self.__receiveElemDamage( caster, receiver )
			return

		# 计算技能攻击力和计算直接伤害
		skillDamage = self.calcSkillHitStrength( caster,receiver, 0, 0 )
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

		# 元素伤害加深
		self.calcElemDamageDeep( receiver, elemDamageList )

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

	def __receiveElemDamage( self, caster, receiver ):
		"""
		元素攻击效果伤害计算
		"""
		damageType = self._damageType

		# 计算技能攻击力和计算直接伤害
		skillDamage = self.calcSkillHitStrength( caster,receiver, 0, 0 )
		attackdamage = self.calcDamage( caster, receiver, skillDamage )

		# 给出受击装备伤害
		equipmentDamage = int( skillDamage - attackdamage )
		receiver.equipDamage( equipmentDamage )

		# 计算此次攻击的招架 执行成功招架后的行为
		if self.isResistHit( caster, receiver ):
			caster.doAttackerOnResistHit( receiver, damageType )	# 攻击者触发
			receiver.doVictimOnResistHit( caster, damageType )   	# 受击者触发
			attackdamage -= attackdamage * receiver.resist_hit_derate
			damageType |= csdefine.DAMAGE_TYPE_RESIST_HIT

		# 伤害削减
		attackdamage = self.calcDamageScissor( caster, receiver, attackdamage )

		# 计算元素伤害 元素伤害列表 按次序分别为 火玄雷冰4个元素所产生的伤害
		elemDamageList = self.calcElemDamage( caster, receiver, attackdamage )
		attackdamage = 0	# 普通伤害置为0

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

		# 元素伤害加深
		self.calcElemDamageDeep( receiver, elemDamageList )

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

	def damageWithLevelWave( self, caster, receiver, attackdamage ):
		"""
		怪物和玩家等级差别造成的伤害变动 by姜毅
		"""
		if caster.getEntityType() != csdefine.ENTITY_TYPE_MONSTER or receiver.getEntityType() != csdefine.ENTITY_TYPE_ROLE:
			return attackdamage

		levelWave = caster.level - receiver.level

		if levelWave < 4:
			return attackdamage
		elif levelWave > 13:
			return attackdamage * 2
		else:
			return attackdamage * ( 1 + ( levelWave - 3 ) / 10.0 )


#
# $Log: not supported by cvs2svn $
# Revision 1.36  2008/07/28 03:17:12  kebiao
# 修正招架减伤公式
#
# Revision 1.35  2008/07/04 03:51:05  kebiao
# 对效果状态的实现优化
#
# Revision 1.34  2008/07/03 02:49:02  kebiao
# 改变 睡眠 定身等效果的实现
#
# Revision 1.33  2008/07/01 06:17:04  zhangyuxing
# 去掉装备损耗计算临时测试信息
#
# Revision 1.32  2008/06/26 00:55:32  zhangyuxing
# 加入：重新计算耐久度消耗方式
#
# Revision 1.31  2008/06/19 04:08:17  kebiao
# 强制定义了该类型技能为恶性
#
# Revision 1.30  2008/06/04 01:17:06  kebiao
# 调整BUFF释放位置
#
# Revision 1.29  2008/05/28 06:35:33  kebiao
# 修改攻击目标 在目标没有闪避的情况下最少造成1点伤害
#
# Revision 1.28  2008/04/23 00:50:32  kebiao
# 增加攻击者未击中回调
#
# Revision 1.27  2008/04/10 04:07:51  kebiao
# 改为在接受伤害之前通知客户端接受技能处理
#
# Revision 1.26  2008/04/10 03:51:50  kebiao
# 改为在接受伤害之前通知客户端接受技能处理
#
# Revision 1.25  2008/04/10 03:27:31  kebiao
# modify to receiveSpell pertinent.
#
# Revision 1.24  2008/03/31 09:04:33  kebiao
# 修改receiveDamage和通知客户端接受某技能结果分开
# 技能通过receiveSpell通知客户端去表现，支持各技能不同的表现
#
# Revision 1.23  2008/02/27 07:15:33  kebiao
# 部分触发列表增加damageType
#
# Revision 1.22  2008/02/27 06:52:20  kebiao
# doAttackerOnHit 增加damageType
#
# Revision 1.21  2008/02/25 09:26:34  kebiao
# 修改伤害反弹部分 与 护盾减伤相关
#
# Revision 1.20  2008/02/13 08:39:47  kebiao
# 修改护盾计算的流程位置
#
# Revision 1.19  2008/01/30 07:22:13  kebiao
# 修改伤害反弹的处理位置
#
# Revision 1.18  2008/01/29 01:27:27  kebiao
# 增加其它伤害类型的标志
#
# Revision 1.17  2008/01/15 07:22:33  kebiao
# 修改成功命中后执行添加BUFF的操作
#
# Revision 1.16  2007/12/25 03:10:24  kebiao
# 增加无敌判断
#
# Revision 1.15  2007/12/21 09:00:31  kebiao
# 添加注释
#
# Revision 1.14  2007/12/18 04:15:18  kebiao
# 调整onReceiveBefore参数位置
#
# Revision 1.13  2007/11/30 05:50:42  kebiao
# 调整伤害处理流程
#
# Revision 1.12  2007/11/28 01:44:02  kebiao
# 调整结构
#
# Revision 1.11  2007/11/27 02:08:27  kebiao
# 修改战斗流程
#
# Revision 1.10  2007/11/26 08:21:12  kebiao
# ADD:persentDamage方法
#
# Revision 1.9  2007/11/24 06:58:22  kebiao
# 调整技能关系
#
# Revision 1.8  2007/11/23 02:00:28  kebiao
# 增加一次伤害流程产生多次伤害支持
#
# Revision 1.7  2007/11/20 08:19:26  kebiao
# 战斗系统第2阶段调整
#
# Revision 1.6  2007/11/01 03:21:55  kebiao
# 去掉持续时间
#
# Revision 1.5  2007/10/26 07:08:51  kebiao
# 根据全新的策划战斗系统做调整
#
# Revision 1.4  2007/08/30 08:00:39  kebiao
# add:getMaxLevel
#
# Revision 1.3  2007/08/16 02:34:30  yangkai
# 根据策划最新装备耐久磨损规则
# 不管是否命中目标都磨损耐久
# 磨损耐久和技能类型有关
# 装备耐久磨损放在了 CombatSpell::onArrive()
#
# Revision 1.2  2007/08/15 09:04:25  kebiao
# 修改接口
#
# Revision 1.1  2007/08/15 04:23:06  kebiao
# 攻击性技能
#
#
#