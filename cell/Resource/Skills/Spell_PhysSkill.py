# -*- coding: gb18030 -*-
#
# $Id: Spell_PhysSkill.py,v 1.18 2008-09-04 07:46:27 kebiao Exp $

"""
持续性效果
"""

import random
import csdefine
import csstatus
from SpellBase import *
import BigWorld
import csconst
from bwdebug import *
import SkillTargetObjImpl
import Const

class Spell_PhysSkill( CombatSpell ):
	"""
	物理技能 技能本身的攻击力+角色的物理攻击力  单体
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		CombatSpell.__init__( self )
		self._damageType = csdefine.DAMAGE_TYPE_PHYSICS				# 伤害类别

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		CombatSpell.init( self, dict )

	def getType( self ):
		"""
		取得基础分类类型
		这些值是BASE_SKILL_TYPE_*之一
		"""
		return csdefine.BASE_SKILL_TYPE_PHYSICS

	def getRangeMax( self, caster ):
		"""
		virtual method.
		@param caster: 施法者，通常某些需要武器射程做为距离的法术就会用到。
		@return: 施法距离
		"""
		return ( self._rangeMax + caster.phySkillRangeVal_value ) * ( 1 + caster.phySkillRangeVal_percent / csconst.FLOAT_ZIP_PERCENT ) + getattr( caster, "modelScale", 1.0 ) * caster.getBoundingBox().z /4.0

	def getCastRange( self, caster ):
		"""
		法术释放距离
		"""
		return (self._skillCastRange + caster.phySkillRangeVal_value ) * ( 1 + caster.phySkillRangeVal_percent / csconst.FLOAT_ZIP_PERCENT )

	def calcExtraRequire( self, caster ):
		"""
		virtual method.
		计算技能消耗的额外值， 由其他装备或者技能BUFF影响到技能的消耗
		return : (额外消耗附加值，额外消耗加成)
		"""
		return ( caster.phyManaVal_value, caster.phyManaVal_percent / csconst.FLOAT_ZIP_PERCENT )

	def calcSkillHitStrength( self, source,receiver, dynPercent, dynValue ):
		"""
		virtual method.
		计算技能攻击力
		方式1：技能攻击力（总公式中的基础值）=技能本身的攻击力+角色的物理攻击力
		带入总公式中就是：（技能本身的攻击力+角色物理攻击力）*（1+物理攻击力加成）+物理攻击力加值
		@param source:	攻击方
		@type  source:	entity
		@param dynPercent:	在本次攻击流程中可能会有外部其他技能导致额外的 技能攻击力加成
		@param  dynValue:	在本次攻击流程中可能会有外部其他技能导致额外的 技能攻击力加值
		"""
		#角色物理攻击力
		extra = random.randint( int( source.damage_min ), int( source.damage_max ) )
		base = random.randint( self._effect_min, self._effect_max )
		return self.calcProperty( base, extra, dynPercent + source.skill_extra_percent / csconst.FLOAT_ZIP_PERCENT, dynValue + source.skill_extra_value )

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
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
		# 防止其他原因导致的不可施法
		if caster.actionSign( csdefine.ACTION_FORBID_SPELL_PHY ):
			return csstatus.SKILL_CANT_CAST
		return CombatSpell.useableCheck( self, caster, target )

class Spell_PhysSkill2( Spell_PhysSkill ):
	"""
	物理技能  技能本身的攻击力 单体
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_PhysSkill.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_PhysSkill.init( self, dict )

	def calcSkillHitStrength( self, source,receiver, dynPercent, dynValue ):
		"""
		virtual method.
		计算技能攻击力
		方式2：技能攻击力（总公式中的基础值）=技能本身的攻击力
		带入总公式中就是：技能本身的攻击力*（1+物理攻击力加成）+物理攻击力加值
		@param source:	攻击方
		@type  source:	entity
		@param dynPercent:	在本次攻击流程中可能会有外部其他技能导致额外的 技能攻击力加成
		@param  dynValue:	在本次攻击流程中可能会有外部其他技能导致额外的 技能攻击力加值
		"""
		base = random.randint( self._effect_min, self._effect_max )
		return self.calcProperty( base, 0, dynPercent + source.skill_extra_percent / csconst.FLOAT_ZIP_PERCENT, dynValue + source.skill_extra_value )

class Spell_PhyVolley( Spell_PhysSkill ):
	"""
	物理技能 技能本身的攻击力+角色的物理攻击力  群体
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_PhysSkill.__init__( self )
		self._skill = ChildSpell( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_PhysSkill.init( self, dict )
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
		# 恶性技能使用触发
		caster.doOnUseMaligSkill( self )

class Spell_PhyVolley2( Spell_PhysSkill2 ):
	"""
	物理技能 技能本身的攻击力+角色的物理攻击力  群体
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_PhysSkill.__init__( self )
		self._skill = ChildSpell( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_PhysSkill.init( self, dict )
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
		# 恶性技能使用触发
		caster.doOnUseMaligSkill( self )
#
# $Log: not supported by cvs2svn $
# Revision 1.17  2008/08/13 07:55:41  kebiao
# 调整该技能的类型
#
# Revision 1.16  2008/07/29 02:57:07  wangshufeng
# 由于damage_min和damage_max改为浮点型，攻击力计算做相应调整
#
# Revision 1.15  2008/07/04 03:50:57  kebiao
# 对效果状态的实现优化
#
# Revision 1.14  2008/07/03 02:49:39  kebiao
# 改变 睡眠 定身等效果的实现
#
# Revision 1.13  2008/01/15 07:23:09  kebiao
# 去掉添加BUFF操作 移动到combatSpell
#
# Revision 1.12  2007/12/25 03:09:39  kebiao
# 调整效果记录属性为effectLog
#
# Revision 1.11  2007/12/13 00:48:08  kebiao
# 重新修正了状态改变部分，因为底层有相关冲突机制 因此这里就不再关心冲突问题
#
# Revision 1.10  2007/12/12 06:01:38  kebiao
# 添加眩晕等状态提示
#
# Revision 1.9  2007/12/12 04:21:10  kebiao
# 修改眩晕等状态判断
#
# Revision 1.8  2007/12/11 08:05:51  kebiao
# 调整群体技能
#
# Revision 1.7  2007/11/27 03:20:02  kebiao
# 添加施法判定 对沉没等支持
#
# Revision 1.6  2007/11/26 08:44:09  kebiao
# self._receiverObject.getReceivers( caster, target )
# 修改为调用自身
# getReceivers( self, caster, target )
#
# Revision 1.5  2007/11/26 08:23:22  kebiao
# 添加只算技能攻击力的群体物理技能
#
# Revision 1.4  2007/11/24 08:31:48  kebiao
# 修改了结构
#
# Revision 1.3  2007/11/23 02:55:29  kebiao
# 将群体法术搬进来了
#
# Revision 1.2  2007/11/20 08:18:40  kebiao
# 战斗系统第2阶段调整
#
# Revision 1.1  2007/10/26 07:06:24  kebiao
# 根据全新的策划战斗系统做调整
#
# Revision 1.15  2007/08/15 03:28:57  kebiao
# 新技能系统
#
#
#