# -*- coding: gb18030 -*-

"""
����̶
"""

from SpellBase import *
from Spell_BuffNormal import Spell_BuffNormal
import utils
import csstatus
import csdefine
import BigWorld

class Spell_122195002( Spell_BuffNormal ):
	"""
	����̶
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_BuffNormal.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_BuffNormal.init( self, dict )
		self.className = str( dict[ "param1" ] )		# ����̶ֻ���ض�������Ч

	def receiveLinkBuff( self, caster, receiver ):
		"""
		��entity����buff��Ч��
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: ʩչ����
		@type  receiver: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		if receiver.className != self.className:	# ����̶ֻ���ض�������Ч
			return
		
		Spell_BuffNormal.receiveLinkBuff( self, caster, receiver )					# ʩ���߻�ø�buff��
#
