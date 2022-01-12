# -*- coding:gb18030 -*-

from SpellBase import Spell
from bwdebug import *
import ECBExtend

class Spell_NotifySpawnMonster( Spell ):
	"""
	ˮ������ר�ã�֪ͨ������ʼ�ڶ��ء�������ˢ��
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
		if receiver.isDestroyed:
			return
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		spaceEntity = BigWorld.entities.get( receiver.getCurrentSpaceBase().id, None )
		if spaceEntity:
			spaceEntity.startSpawnMonsterBySkill()
		self.receiveLinkBuff( caster, receiver )
		