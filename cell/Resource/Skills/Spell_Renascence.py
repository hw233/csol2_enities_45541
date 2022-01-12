# -*- coding: gb18030 -*-
#
# $Id: Spell_Renascence.py,v 1.1 2007-12-28 08:57:28 kebiao Exp $

"""
"""

from SpellBase import *
import csdefine

class Spell_Renascence( Spell ):
	"""
	复活
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		receiver.reviveOnOrigin()
					
# $Log: not supported by cvs2svn $
#