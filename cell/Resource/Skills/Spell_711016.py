# -*- coding: gb18030 -*-
#
# $Id: Spell_711016.py,v 1.1 2008-08-26 01:08:44 kebiao Exp $

"""
传送技能基础
"""

from SpellBase import *

class Spell_711016( SystemSpell ):
	"""
	城市战场进入
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		SystemSpell.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		SystemSpell.init( self, dict )
		#self.spaceName = dict.readString( "param1" )
		#self.revivePosition = dict.readVector3( "param2" )
		#self.reviveDirection = dict.readVector3( "param2" )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		spaceName, position, direction = receiver.popTemp( "gotoCityWarData" )
		receiver.gotoSpace( spaceName, position, direction )

# $Log: not supported by cvs2svn $
#