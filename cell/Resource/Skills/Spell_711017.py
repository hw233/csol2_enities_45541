# -*- coding: gb18030 -*-
#
# $Id: Spell_711016.py,v 1.1 2008-08-26 01:08:44 kebiao Exp $

"""
���ͼ��ܻ���
"""

from SpellBase import *

class Spell_711017( Spell ):
	"""
	�ɼ�
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
		receiver.gossipWith( caster.id, "getTarget" )
		
# $Log: not supported by cvs2svn $
#