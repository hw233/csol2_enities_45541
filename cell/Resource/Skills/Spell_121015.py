# -*- coding: gb18030 -*-
#
# $Id: Spell_121015.py,v 1.2 2007-12-21 04:21:10 kebiao Exp $

"""
���ܶ���Ʒʩչ����������
"""

from SpellBase import *
from Spell_PhysSkill import Spell_PhysSkill2
import random

class Spell_121015( Spell_PhysSkill2 ):
	"""
	������	���	����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_PhysSkill2.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_PhysSkill2.init( self, dict )

	def receiveLinkBuff( self, caster, receiver ):
		"""
		��entity����buff��Ч��
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: ʩչ����
		@type  receiver: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		for buff in self._buffLink:
			# �в����������жϻ���
			if not self.canLinkBuff( caster, receiver, buff ): continue
			r = receiver
			if buff.getBuff().getSourceSkillIndex() == 0:
				r = caster
			buff.getBuff().receive( caster, r )				# ����buff��receive()���Զ��ж�receiver�Ƿ�ΪrealEntity

# $Log: not supported by cvs2svn $
# Revision 1.1  2007/12/20 05:56:37  kebiao
# no message
#
#