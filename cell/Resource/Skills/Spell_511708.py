# -*- coding: gb18030 -*-
#
# $Id: Spell_511708.py,v 1.1 2007-12-26 08:19:25 kebiao Exp $

"""
���ܶ���Ʒʩչ����������
"""

from SpellBase import *
from Spell_PhysSkill import Spell_PhysSkill
import utils
import csstatus

class Spell_511708( Spell_PhysSkill ):
	"""
	������	���	����
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

	def receiveLinkBuff( self, caster, receiver ):
		"""
		��entity����buff��Ч��
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: ʩչ����
		@type  receiver: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		Spell_PhysSkill.receiveLinkBuff( self, caster, caster ) #ʩ���߻�ø�buff��

# $Log: not supported by cvs2svn $
# Revision 1.1  2007/12/20 05:43:42  kebiao
# no message
#
#