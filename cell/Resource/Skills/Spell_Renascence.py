# -*- coding: gb18030 -*-
#
# $Id: Spell_Renascence.py,v 1.1 2007-12-28 08:57:28 kebiao Exp $

"""
"""

from SpellBase import *
import csdefine

class Spell_Renascence( Spell ):
	"""
	����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		receiver.reviveOnOrigin()
					
# $Log: not supported by cvs2svn $
#