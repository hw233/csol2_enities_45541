# -*- coding: gb18030 -*-
#
# $Id: Spell_311101.py,v 1.1 2008-01-04 03:39:06 kebiao Exp $

"""
���ܶ���Ʒʩչ����������
"""

from SpellBase import *
from Spell_PhysSkill import Spell_PhysSkill
import csstatus
import csdefine

class Spell_311101( Spell_PhysSkill ):
	"""
	������	�ͻ����� �ڷ�����������Spell_PhysSkillû���κ����壬�����ǿͻ�����ҪһЩ����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_PhysSkill.__init__( self )
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_PhysSkill.init( self, dict )


		
# $Log: not supported by cvs2svn $
#