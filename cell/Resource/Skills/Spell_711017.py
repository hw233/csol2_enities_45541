# -*- coding: gb18030 -*-
#
# $Id: Spell_711016.py,v 1.1 2008-08-26 01:08:44 kebiao Exp $

"""
传送技能基础
"""

from SpellBase import *

class Spell_711017( Spell ):
	"""
	采集
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
		receiver.gossipWith( caster.id, "getTarget" )
		
# $Log: not supported by cvs2svn $
#