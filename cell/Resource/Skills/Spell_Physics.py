# -*- coding: gb18030 -*-
#
# $Id: Spell_Physics.py,v 1.28 2008-08-13 07:55:41 kebiao Exp $

"""
持续性效果
"""

import random
import csdefine
import csstatus
from SpellBase import *
import BigWorld
from bwdebug import *
import Const

class Spell_Physics( CombatSpell ):
	"""
	普通物理攻击
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		CombatSpell.__init__( self )
		self._baseType = csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL
		self._damageType = csdefine.DAMAGE_TYPE_PHYSICS_NORMAL				# 伤害类别

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
		return csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL

	def calcSkillHitStrength( self, source,receiver, dynPercent, dynValue ):
		"""
		virtual method.
		计算技能攻击力
		技能攻击力（总公式中的基础值）= 角色的物理攻击力
		"""
		#普通物理攻击 只需要返回source.damage
		return random.randint( int( source.damage_min ), int( source.damage_max ) )

	def getRangeMax( self, caster ):
		"""
		virtual method.
		取得攻击距离
		"""
		return caster.range + getattr( caster, "modelScale", 1.0 ) * caster.getBoundingBox().z /4.0

	def getCastRange( self, caster ):
		"""
		法术释放距离
		"""
		return self.getRangeMax( caster ) + 0.5

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
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER

		if caster.actionSign( csdefine.ACTION_FORBID_ATTACK ):
			return csstatus.SKILL_CANT_ATTACK

		state = CombatSpell.useableCheck( self, caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# 检查攻击延迟
		if not caster.hitDelayOver():
			return csstatus.SKILL_NOT_HIT_TIME
		return csstatus.SKILL_GO_ON

	def onSkillCastOver_( self, caster, target ):
		"""
		virtual method.
		法术施放完毕通知
		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		#计算攻击延迟时间， 下一次攻击时会检查时间 时间到了才可以继续攻击
		#caster.hitDelay = BigWorld.time() + caster.hit_speed
		caster.setHitDelay()
		CombatSpell.onSkillCastOver_( self, caster, target )

	def getReceivers( self, caster, target ):
		"""
		取得所有的符合条件的受术者Entity列表；
		所有的onArrive()方法都应该调用此方法来获取有效的entity。

		@rtype: list of Entity
		"""
		entity = target.getObject()
		if entity is None:
			return []
		return [ entity ]

	def calcDelay( self, caster, target ):
		"""
		virtual method.
		取得伤害延迟
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: float(秒)
		"""
		return CombatSpell.calcDelay( self, caster, target ) + 0.7

#
# $Log: not supported by cvs2svn $
# Revision 1.27  2008/07/29 02:56:38  wangshufeng
# 由于damage_min和damage_max改为浮点型，攻击力计算做相应调整
#
# Revision 1.26  2008/07/04 03:50:57  kebiao
# 对效果状态的实现优化
#
# Revision 1.25  2008/07/03 02:49:39  kebiao
# 改变 睡眠 定身等效果的实现
#
# Revision 1.24  2008/03/03 06:34:23  kebiao
# SKILL getRange to getRangeMax
#
# Revision 1.23  2008/02/02 09:09:52  phw
# method modified: calcDelay(), change extra delay from 1.0 to 0.7
#
# Revision 1.22  2008/02/02 08:33:48  kebiao
# 添加延迟时间1秒
#
# Revision 1.21  2007/12/25 03:09:39  kebiao
# 调整效果记录属性为effectLog
#
# Revision 1.20  2007/12/13 06:52:32  kebiao
# 调整物理攻击 玩家 怪物 宠物 使用一个普通物理攻击
#
# Revision 1.19  2007/12/12 06:01:38  kebiao
# 添加眩晕等状态提示
#
# Revision 1.18  2007/12/12 04:21:10  kebiao
# 修改眩晕等状态判断
#
# Revision 1.17  2007/12/05 07:43:58  kebiao
# 增加了注释
#
# Revision 1.16  2007/11/20 08:18:40  kebiao
# 战斗系统第2阶段调整
#
# Revision 1.15  2007/10/26 07:06:24  kebiao
# 根据全新的策划战斗系统做调整
#
# Revision 1.15  2007/08/15 03:28:57  kebiao
# 新技能系统
#
#
#
