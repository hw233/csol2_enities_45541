# -*- coding: gb18030 -*-
#

import csdefine
from SpellBase import *
from Spell_Item import Spell_Item


class Spell_Item_Clear_Monster( Spell_Item ):
	"""
	#���
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self.param1 = int( dict[ "param1" ] )

	def cast( self, caster, receiver ):
		"""
		��������ʱ����Ϣ�ص�
		@param   caster: ʩ����
		@type    caster: Entity
		@param   receiver: ������
		@type    receiver: Entity
		"""
		Spell_Item.cast( self, caster, target )
		monster = caster.entitiesInRangeExt( self.param1, "MonsterYayu", caster.position )
		if len( monster ) == 0:
			return
		for e in monster:
			e.die( caster.id )
