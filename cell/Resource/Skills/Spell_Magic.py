# -*- coding: gb18030 -*-
#
# $Id: Spell_Magic.py,v 1.21 2008-09-04 07:46:27 kebiao Exp $

"""
"""

import random
import csdefine
import csstatus
from SpellBase import *
import BigWorld
import csconst
from bwdebug import *
from Spell_PhysSkill import Spell_PhysSkill
import SkillTargetObjImpl
from CombatSystemExp import CombatExp
import CombatUnitConfig
import Const

class Spell_Magic( Spell_PhysSkill ):
	"""
	法术单体技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_PhysSkill.__init__( self )
		self._damageType = csdefine.DAMAGE_TYPE_MAGIC				# 伤害类别
		self._effectConvert = 1.0	#如果没有效果 那么折算为1.0 否则为0.95
		self._volleyConvert = 1		#如果是群体法术则要除3

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_PhysSkill.init( self, dict )
		# 过去这里是判断是否为-1.0 是则不设置 策划将表弄坏了 现在修改为是否!=0.0
		if float( dict[ "EffectConvert" ] if dict[ "EffectConvert" ] > 0 else 0.0 )  != 0.0:	#效果导致该技能2秒规则中的一个折算 不是100%释放效果那么折算为1.0 否则为0.95
			self._effectConvert = int( dict[ "EffectConvert" ] if dict[ "EffectConvert" ] > 0 else 0 )  / 100.0
		if float( dict[ "VolleyConvert" ] if dict[ "VolleyConvert" ] > 0 else 0.0 )  != 0.0:	#效果导致该技能2秒规则中的一个折算 不是100%释放效果那么折算为1.0 否则为0.95
			self._volleyConvert = int( dict[ "VolleyConvert" ] if dict[ "VolleyConvert" ] > 0 else 0 )

	def getType( self ):
		"""
		取得基础分类类型
		这些值是BASE_SKILL_TYPE_*之一
		"""
		return csdefine.BASE_SKILL_TYPE_MAGIC

	def getRangeMax( self, caster ):
		"""
		virtual method.
		@param caster: 施法者，通常某些需要武器射程做为距离的法术就会用到。
		@return: 施法距离
		"""
		return ( self._rangeMax + caster.magicSkillRangeVal_value ) * ( 1 + caster.magicSkillRangeVal_percent / csconst.FLOAT_ZIP_PERCENT )

	def getCastRange( self, caster ):
		"""
		法术释放距离
		"""
		return ( self._skillCastRange + caster.magicSkillRangeVal_value ) * ( 1 + caster.magicSkillRangeVal_percent / csconst.FLOAT_ZIP_PERCENT )

	def calcExtraRequire( self, caster ):
		"""
		virtual method.
		计算技能消耗的额外值， 由其他装备或者技能BUFF影响到技能的消耗
		return : (额外消耗附加值，额外消耗加成)
		"""
		return ( caster.magicManaVal_value, caster.magicManaVal_percent / csconst.FLOAT_ZIP_PERCENT )

	def calcTwoSecondRule( self, source, skillDamageExtra ):
		"""
		virtual method.
		法术的2秒规则计算
		对于法术技能攻击力来说，它的附加值效果受以下几个条件限制：
		1)只有当法术的吟唱时间t大于或等于2秒的时候，该法术才能享受到加值的全额效果。但是当t大于2秒的时候，取2计算。当t小于2秒时，取t值。
		例1．一个法术的吟唱时间为1.5秒，则该法术享受的附加值为：附加值*1.5/2
		例2．一个法术的吟唱时间为6秒，则该法术享受的附加值为：附加值*2/2。
		2)如果：该法术是瞬发法术，即t=0。在加值的计算上取0.8。则该法术享受的附加值为：附加值*0.8/2。
		3)如果：该法术本身一定能产生某种额外的效果，则附加值还有0.95的折算。
		例如：一个法术吟唱时间为t(t遵从上述规则)，在击中目标后，能让目标减速，则该法术享受的附加值为：附加值*t/2*0.95。
		4)当技能能够产生伤害性质的buff时，又分为两种情况：
				A．此buff为技能本身具备buff
		此类技能的伤害分为初次伤害和buff伤害，享受加值的效果分别为70%和30%，如技能A，击中对方后给予对方造成a~b的火攻，同时造成一个伤害buff，分十次共20秒造成c点火伤，此时，如果武器上有100的法术攻击力附加值，那么，其中的70点攻击力在首次攻击时产生作用，30点平分到10次buff的伤害中。
				B．此buff为学习被动技能后，附带拥有的效果
		此类技能的伤害分同样分为初次伤害和buff伤害，两种伤害分别享受攻击加值的效果。
		如技能B，击中对方后给予对方造成a~b的火攻，此时技能本身是不能产生buff的。学习被动技能后，能够造成一个伤害buff，分十次共20秒造成c点火伤，此时，如果武器上有100的法术攻击附加值，那么，首次攻击时会增加100的法术攻击力，同时，100点法术攻击力也会平分到10次buff伤害中。

		5)附加值对buff的15秒规则
		只有当buff的持续时间t大于或等于15秒的时候，该buff才能享受到附加值的全额效果。当t大于15秒的时候，取15计算。当t小于15秒时，取t值。
		例1．一个buff的持续时间为10秒，则该buff享受的附加值为：附加值*10/15
		例2．一个buff的持续时间为17秒，则该法术享受的附加值为：附加值*15/15。

		6)如果：该法术是群体攻击法术，那么在附加值的计算中，还要有1/3的折算。则
		该法术享受的附加值为：附加值*1/3。
		例如：一个群体攻击法术，它是瞬发，对攻击范围内的目标造成伤害，并且能让目标移动速度降低50%，持续6秒。那么该法术享受的加值为：附加值*(0.8/2)*0.95/3
		以上条件只对附加值起效果，对加成无效。
		"""
		tVal = 2.0 #2秒规则的取值
		"""策划规定， 固定取2秒的值
		itime = self.getIntonateTime( source ) #由于吟唱时间可能被其他技能改变 因此无法在初始化时期优化 只能动态计算
		if itime <= 0:
			tVal = 0.8
		elif itime < 2.0:
			tVal = itime
		"""
		ret = skillDamageExtra * tVal / 2 * self._effectConvert#如果一定会产生效果则进行则算_effectConvert
		return ret / self._volleyConvert

	def calcHitProbability( self, source, target ):
		"""
		virtual method.
		计算命中率
		法术命中率=1-（0.13-（攻方命中/10000-0.9）+（守方闪避/10000-0.03）-取整（（攻方等级-守方等级）/5）*0.01）
		以上攻方命中为攻击者命中终值，守方闪避为防守方闪避终值。
		以上计算结果大于1时，取1；小于0.7时，取0.7。

		@param source:	攻击方
		@type  source:	entity
		@param target:	被攻击方
		@type  target:	entity
		return type:	Float
		"""
		hitRate = CombatUnitConfig.calcMagicHitProbability( source, target )
		return max( 0.25, min( 1, hitRate ) )

	def calcSkillHitStrength( self, source,receiver, dynPercent, dynValue ):
		"""
		virtual method.
		计算技能攻击力
		基础法术攻击力(总公式中的基础值)=智力*0.14
		法术技能攻击力(总公式中的基础值)=(法术技能本身的攻击力+角色法术攻击力受2秒规则计算后的值)*(1+法术攻击力加成)+法术攻击力加值
		注意：法术技能攻击力这里稍稍有些不同，计算后的角色法术攻击力，对法术技能攻击力起效时，是处于附加值的位置。
		@param source:	攻击方
		@type  source:	entity
		@param dynPercent:	在本次攻击流程中可能会有外部其他技能导致额外的 技能攻击力加成
		@param  dynValue:	在本次攻击流程中可能会有外部其他技能导致额外的 技能攻击力加值
		"""
		base = random.randint( self._effect_min, self._effect_max )
		extra = self.calcTwoSecondRule( source, source.magic_damage )
		return self.calcProperty( base, extra * self._shareValPercent, dynPercent + source.magic_skill_extra_percent / csconst.FLOAT_ZIP_PERCENT, dynValue + source.magic_skill_extra_value / csconst.FLOAT_ZIP_PERCENT )

	def calcVictimResist( self, source, target ):
		"""
		virtual method.
		计算被攻击方法术防御减伤
		角色基础法术防御值(总公式中的基础值)=0
		法术防御减伤(总公式中的基础值)= 物理防御值/(物理防御值+40*攻击方等级+350)-0.23
		@param source:	攻击方
		@type  source:	entity
		@param target:	被攻击方
		@type  target:	entity
		@return: FLOAT
		"""
		exp = CombatExp( source, target )
		val = max( 0.0, exp.getMagicDamageReductionRate() )
		if val > 0.95:
			val = 0.95
		return self.calcProperty( val, target.magic_armor_reduce_damage_extra / csconst.FLOAT_ZIP_PERCENT, target.magic_armor_reduce_damage_percent / csconst.FLOAT_ZIP_PERCENT, target.magic_armor_reduce_damage_value / csconst.FLOAT_ZIP_PERCENT )

	def calcDamageScissor( self, caster, receiver, damage ):
		"""
		virtual method.
		计算被攻击方法术伤害削减
		公式：伤害=直接法术伤害x (1 – 被攻击方法术伤害减免率)
		–	被攻击方法术伤害减免值
		基础法术伤害减免点数(总公式中的基础值)=0
		基础法术伤害减免值(总公式中的基础值)=0

		@param receiver: 被攻击方
		@type  receiver: entity
		@param  damage: 经过招架判断后的伤害
		@type   damage: INT
		@return: INT32
		"""
		return caster.calcMagicDamageScissor( receiver, damage )

	def calcDoubleMultiple( self, caster ):
		"""
		virtual method.
		计算暴击伤害加倍
		@param caster: 被攻击方
		@type  caster: entity
		@return type:计算后得到的暴击倍数
		"""
		return caster.magic_double_hit_multiple

	def calcDamage( self, source, target, skillDamage ):
		"""
		virtual method.
		计算直接伤害
		普通物理伤害(总公式中的基础值)=物理攻击力*(1-被攻击方物理防御减伤)
		技能物理伤害(总公式中的基础值)=技能攻击力*(1-被攻击方物理防御减伤)

		@param source: 攻击方
		@type  source: entity
		@param target: 被攻击方
		@type  target: entity
		@param skillDamage: 技能攻击力
		@return: INT32
		"""
		# 计算被攻击方物理防御减伤
		armor = self.calcVictimResist( source, target )
		return ( skillDamage * ( 1 - armor ) ) * ( 1 + target.receive_magic_damage_percent / csconst.FLOAT_ZIP_PERCENT ) + target.receive_magic_damage_value

	def isDoubleHit( self, caster, receiver ):
		"""
		virtual method.
		判断攻击者是否爆击
		return type:bool
		"""
		return random.random() < ( caster.magic_double_hit_probability + ( receiver.be_magic_double_hit_probability - receiver.be_magic_double_hit_probability_reduce ) / csconst.FLOAT_ZIP_PERCENT )

	def isResistHit( self, caster, receiver ):
		"""
		virtual method.
		判断被攻击者是否招架
		return type:bool
		"""
		return False # 法术技能不可被招架

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
		#处理沉默等一类技能的施法判断
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB

		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER

		# 防止其他原因导致的不可施法
		if caster.actionSign( csdefine.ACTION_FORBID_SPELL_MAGIC ):
			return csstatus.SKILL_CANT_CAST
		return CombatSpell.useableCheck( self, caster, target )

class Spell_MagicVolley( Spell_Magic ):
	"""
	法术群体技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Magic.__init__( self )
		self._skill = ChildSpell( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		self._skill.init( dict )

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
		for receiver in receivers:
			receiver.clearBuff( self._triggerBuffInterruptCode )
			self._skill.cast( caster, SkillTargetObjImpl.createTargetObjEntity( receiver ) )
			self.receiveEnemy( caster, receiver )
		# 恶性技能使用触发
		caster.doOnUseMaligSkill( self )
#
# $Log: not supported by cvs2svn $
# Revision 1.20  2008/08/22 07:07:57  kebiao
# 修改命中率公式固定0.9
#
# Revision 1.19  2008/08/13 07:55:41  kebiao
# 调整该技能的类型
#
# Revision 1.18  2008/07/15 04:06:42  kebiao
# 将技能配置修改到datatool相关初始化需要修改
#
# Revision 1.17  2008/07/04 03:50:57  kebiao
# 对效果状态的实现优化
#
# Revision 1.16  2008/07/03 02:49:39  kebiao
# 改变 睡眠 定身等效果的实现
#
# Revision 1.15  2008/02/25 09:29:42  kebiao
# 修改 护盾减伤相关
#
# Revision 1.14  2008/02/25 03:35:56  kebiao
# 调整命中率计算公式
#
# Revision 1.13  2007/12/25 03:09:39  kebiao
# 调整效果记录属性为effectLog
#
# Revision 1.12  2007/12/13 00:48:08  kebiao
# 重新修正了状态改变部分，因为底层有相关冲突机制 因此这里就不再关心冲突问题
#
# Revision 1.11  2007/12/12 06:01:38  kebiao
# 添加眩晕等状态提示
#
# Revision 1.10  2007/12/12 04:21:10  kebiao
# 修改眩晕等状态判断
#
# Revision 1.9  2007/12/11 08:05:51  kebiao
# 调整群体技能
#
# Revision 1.8  2007/11/29 03:46:52  kebiao
# 修正BUG
#
# Revision 1.7  2007/11/28 01:46:31  kebiao
# 修改calcDamage公式
#
# Revision 1.6  2007/11/26 08:44:09  kebiao
# self._receiverObject.getReceivers( caster, target )
# 修改为调用自身
# getReceivers( self, caster, target )
#
# Revision 1.5  2007/11/24 08:31:48  kebiao
# 修改了结构
#
# Revision 1.4  2007/11/23 02:55:08  kebiao
# 将群体法术搬进来了
#
# Revision 1.3  2007/11/22 07:23:40  kebiao
# 修正防御减伤计算
#
# Revision 1.2  2007/11/20 08:18:40  kebiao
# 战斗系统第2阶段调整
#
# Revision 1.1  2007/10/26 07:06:24  kebiao
# 根据全新的策划战斗系统做调整
#
#