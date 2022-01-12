# -*- coding: gb18030 -*-
#
# $Id: Spell_311101.py,v 1.1 2008-01-04 03:39:06 kebiao Exp $

"""
技能对物品施展法术基础。
"""

from SpellBase import *
from Spell_PhysSkill import Spell_PhysSkill
import csstatus
import csdefine

class Spell_311101( Spell_PhysSkill ):
	"""
	物理技能	猛击技能 在服务器上重载Spell_PhysSkill没有任何意义，仅仅是客户端需要一些特性
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


		
# $Log: not supported by cvs2svn $
#