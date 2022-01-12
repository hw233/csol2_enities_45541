# -*- coding: gb18030 -*-
#
# $Id: Spell_912310001.py,v 1.1 2008-08-12 08:55:15 kebiao Exp $

"""
技能对物品施展法术基础。
"""

from SpellBase import *
from Spell_Item import Spell_Item
import csstatus
import csdefine
import csconst

class Spell_912310001( Spell_Item ):
	"""
	帮主集结令	技能								把在线家族成员召唤到自己身边，只能族长使用。
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )

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
		if not target.getObject().isTongChief():
			return csstatus.TONG_CHIEF_ITEM
		if not target.getObject().tong_getTongEntity( target.getObject().tong_dbID ):
			return csstatus.TONG_CHIEF_ITEM
		return Spell_Item.useableCheck( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		spaceType = receiver.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		position = receiver.position
		dbid = receiver.databaseID
		lineNumber = receiver.getCurrentSpaceLineNumber()
		tong = receiver.tong_getTongEntity( receiver.tong_dbID )
		if tong:
			tong.chiefCommand_conjure( dbid, lineNumber, spaceType, position )
		
# $Log: not supported by cvs2svn $
#