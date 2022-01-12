# -*- coding: gb18030 -*-
#
# $Id: Spell_ItemHP.py,v 1.10 2008-08-14 06:11:09 songpeifang Exp $

"""
技能对物品施展法术基础。
"""

from SpellBase import *
from Spell_Item import Spell_Item
import csstatus
import csdefine

class Spell_ItemPK( Spell_Item ):
	"""
	使用：立刻改变受术者的PK值 by姜毅
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
		self.redPKValue = int(( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ))
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		self.setPKValue( caster, receiver )
		
	def setPKValue( self, caster, receiver ):
		"""
		设置受术者的PK值
		"""
		if receiver.getEntityType() != csdefine.ENTITY_TYPE_ROLE: return
		if receiver.pkValue < self.redPKValue:
			receiver.statusMessage( csstatus.SKILL_CHANGE_PKVALUE, receiver.pkValue )
		else:
			receiver.statusMessage( csstatus.SKILL_CHANGE_PKVALUE, self.redPKValue )
		receiver.setPkValue( receiver.pkValue - self.redPKValue )
		
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
		if target.getObject().pkValue == 0:
			return csstatus.SKILL_CHANGE_PKVALUE_NONEED
		return Spell_Item.useableCheck( self, caster, target)