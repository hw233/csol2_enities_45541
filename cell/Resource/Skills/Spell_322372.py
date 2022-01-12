# -*- coding: gb18030 -*-
#
# $Id: Spell_CatchPet.py,v 1.20 2008-07-04 03:50:57 kebiao Exp $

"""
"""

from SpellBase import *
import csstatus
import csconst
from PetFormulas import formulas
from Spell_CatchPet import Spell_CatchPet

class Spell_322372( Spell_CatchPet ):
	"""
	使用：抓获宠物
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_CatchPet.__init__( self )
		self.canCatchs = []

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_CatchPet.init( self, dict )
		self.canCatchs = ( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else "" ) .split( "|" )	

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csstatus.SKILL_*
		@rtype:            INT
		"""
		bool = Spell_CatchPet.useableCheck( self, caster, target )
		if bool != csstatus.SKILL_GO_ON:
			return bool
		if target.getObject().className in self.canCatchs:
			return csstatus.SKILL_GO_ON
		else:
			return csstatus.SKILL_CAST_OBJECT_INVALID

# $Log: not supported by cvs2svn $
#