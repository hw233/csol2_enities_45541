# -*- coding: gb18030 -*-
#
# $Id: Spell_312602.py,v 1.7 2008-08-13 02:24:55 kebiao Exp $

"""
���ܶ���Ʒʩչ����������
"""

from SpellBase import *
import random
import csdefine

class Spell_750001( Spell ):
	"""
	��������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
			
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return		
		receiver.removeSkill( receiver.popTemp( "clearSkillID" ) )

# $Log: not supported by cvs2svn $
#