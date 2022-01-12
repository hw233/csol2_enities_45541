# -*- coding: gb18030 -*-

"""
��������
"""

from SpellBase import *
from Spell_BuffNormal import Spell_BuffNormal
import utils
import csstatus
import csdefine
import BigWorld

class Spell_122196002( Spell_BuffNormal ):
	"""
	��������
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

	def getReceivers( self, caster, target ) :
		"""
		virtual method
		Ĭ��ֻ������Ŀ��ʩ�š�
		"""
		receivers = []
		targetEntity = target.getObject()
		if not targetEntity.isDestroyed and \
		( targetEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or targetEntity.isEntityType( csdefine.ENTITY_TYPE_PET ) ):
			receivers.append( targetEntity )

		return receivers

	def _validCaster( self, caster ):
		"""
		virtual method.
		���ʩ�����Ƿ�������������
		@return: INT��see also SkillDefine.SKILL_*
		"""
		return csstatus.SKILL_GO_ON
