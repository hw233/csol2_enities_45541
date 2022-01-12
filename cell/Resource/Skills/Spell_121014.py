# -*- coding: gb18030 -*-
#
# $Id: Spell_121014.py,v 1.5 2008-07-15 04:06:26 kebiao Exp $

"""
技能对物品施展法术基础。
"""

from bwdebug import *
from SpellBase import *
from Spell_PhysSkill import Spell_PhysSkill2
import utils
import csstatus
import csdefine

class Spell_121014( Spell_PhysSkill2 ):
	"""
	物理技能	冲锋	技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_PhysSkill2.__init__( self )
		self._triggerBuffInterruptCode = []							# 该技能触发这些标志码中断某些BUFF

	def init( self, dict ):
		"""
		读取配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_PhysSkill2.init( self, dict )
		for val in dict[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )

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
		d  = caster.distanceBB( target.getObject() )
		if d < 8.0:
			return csstatus.SKILL_INVALID_DISTANCE_CHONGFENG1
		if d > 20.0:
			return csstatus.SKILL_INVALID_DISTANCE_CHONGFENG2
		return Spell_PhysSkill2.useableCheck( self, caster, target )

	def receiveLinkBuff( self, caster, receiver ):
		"""
		给entity附加buff的效果
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 施展对象
		@type  receiver: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell_PhysSkill2.receiveLinkBuff( self, caster, caster ) #施放者获得该buff。

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
		caster.clearBuff( self._triggerBuffInterruptCode ) #删除自身现在所有可以删除的BUFF
		caster.changeAttackTarget( target.getObject().id )
		Spell_PhysSkill2.cast( self, caster, target )
		caster.move_speed = 50.0
		if caster.actionSign( csdefine.ACTION_FORBID_MOVE ):
			DEBUG_MSG( "im cannot the move!" )
			caster.stopMoving()
			return
		caster.gotoPosition( target.getObject().position )

	def onSkillCastOver_( self, caster, target ):
		"""
		virtual method.
		法术施放完毕通知
		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell_PhysSkill2.onSkillCastOver_( self, caster, target )
		caster.calcMoveSpeed()

# $Log: not supported by cvs2svn $
# Revision 1.4  2008/05/28 05:59:47  kebiao
# 修改BUFF的清除方式
#
# Revision 1.3  2008/03/29 08:58:43  phw
# 调整distanceBB()的调用方式，原来从utils模块中调用，改为直接在 entity 身上调用
#
# Revision 1.2  2007/12/29 09:13:42  kebiao
# no message
#
# Revision 1.1  2007/12/20 05:43:42  kebiao
# no message
#
#