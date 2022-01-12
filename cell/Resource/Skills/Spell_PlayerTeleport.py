# -*- coding: gb18030 -*-
#
# $Id: Spell_PlayerTeleport.py,v 1.1 2008-04-26 04:04:50 kebiao Exp $

"""
传送技能基础
"""
import BigWorld
import csstatus
import csdefine
from SpellBase import *
from Spell_TeleportBase import Spell_TeleportBase

class Spell_PlayerTeleport( Spell_TeleportBase ):
	"""
	玩家出生就有的传送技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_TeleportBase.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_TeleportBase.init( self, dict )

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
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		return Spell_TeleportBase.useableCheck( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		receiver.gotoSpace( receiver.reviveSpace, receiver.revivePosition, receiver.reviveDirection )

# $Log: not supported by cvs2svn $
#