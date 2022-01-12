# -*- coding: gb18030 -*-
#
# $Id: Spell_511708.py,v 1.1 2007-12-26 08:19:25 kebiao Exp $

"""
技能对物品施展法术基础。
"""

from SpellBase import *
from Spell_PhysSkill import Spell_PhysSkill
import utils
import csstatus

class Spell_511708( Spell_PhysSkill ):
	"""
	物理技能	冲锋	技能
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

	def receiveLinkBuff( self, caster, receiver ):
		"""
		给entity附加buff的效果
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 施展对象
		@type  receiver: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell_PhysSkill.receiveLinkBuff( self, caster, caster ) #施放者获得该buff。

# $Log: not supported by cvs2svn $
# Revision 1.1  2007/12/20 05:43:42  kebiao
# no message
#
#