# -*- coding: gb18030 -*-
#
# $Id: Spell_121015.py,v 1.2 2007-12-21 04:21:10 kebiao Exp $

"""
技能对物品施展法术基础。
"""

from SpellBase import *
from Spell_PhysSkill import Spell_PhysSkill2
import random

class Spell_121015( Spell_PhysSkill2 ):
	"""
	物理技能	冲锋	技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_PhysSkill2.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_PhysSkill2.init( self, dict )

	def receiveLinkBuff( self, caster, receiver ):
		"""
		给entity附加buff的效果
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 施展对象
		@type  receiver: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		for buff in self._buffLink:
			# 有产生机率则判断机率
			if not self.canLinkBuff( caster, receiver, buff ): continue
			r = receiver
			if buff.getBuff().getSourceSkillIndex() == 0:
				r = caster
			buff.getBuff().receive( caster, r )				# 接收buff，receive()会自动判断receiver是否为realEntity

# $Log: not supported by cvs2svn $
# Revision 1.1  2007/12/20 05:56:37  kebiao
# no message
#
#