# -*- coding: gb18030 -*-
#
# $Id: Spell_711016.py,v 1.1 2008-08-26 01:08:44 kebiao Exp $

"""
���ͼ��ܻ���
"""

from SpellBase import *

class Spell_711016( SystemSpell ):
	"""
	����ս������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		SystemSpell.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		SystemSpell.init( self, dict )
		#self.spaceName = dict.readString( "param1" )
		#self.revivePosition = dict.readVector3( "param2" )
		#self.reviveDirection = dict.readVector3( "param2" )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		spaceName, position, direction = receiver.popTemp( "gotoCityWarData" )
		receiver.gotoSpace( spaceName, position, direction )

# $Log: not supported by cvs2svn $
#