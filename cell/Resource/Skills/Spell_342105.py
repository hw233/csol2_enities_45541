# -*- coding: gb18030 -*-
#

import csdefine
from SpellBase import *


class Spell_342105( Spell ):
	"""
	#���
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
		self.param1 = int( dict[ "param1" ] )

	def receive( self, caster, receiver ):
		"""
		��������ʱ����Ϣ�ص�
		@param   caster: ʩ����
		@type    caster: Entity
		@param   receiver: ������
		@type    receiver: Entity
		"""
		monster = receiver.entitiesInRangeExt( self.param1, "MonsterYayu", receiver.position )
		if len( monster ) == 0:
			return
		for e in monster:
			e.die( caster.id )
