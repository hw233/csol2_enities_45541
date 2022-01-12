# -*- coding:gb18030 -*-

from SpellBase import Spell
from bwdebug import *
import ECBExtend

class Spell_PushEntity( Spell ):
	"""
	NPC���ܣ����������������������������ʩ���ߴ�����������ȥ��
	"""
	def __init__( self ):
		"""
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
		for entity in caster.entitiesInRangeExt( 50.0, "AreaRestrictTransducer", caster.position ):
			if entity.casterID == caster.id and isinstance( receiver, BigWorld.Entity ):
				receiver.position = entity.position
				self.receiveLinkBuff( caster, receiver )
			