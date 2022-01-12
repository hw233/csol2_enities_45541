# -*- coding: gb18030 -*-
#
# $Id: Spell_NPC_Visible.py,v 1.1 12:10 2010-9-4 jianyi Exp $

import BigWorld
import csdefine
import csstatus
from bwdebug import *
from SpellBase.Spell import Spell

class Spell_NPC_Visible( Spell ):
	"""
	��һ��NPC�ɼ�/���ɼ�
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
		self.targetNpcClassName = dict["param1"] if len( dict["param1"] ) > 0 else None	# str or None
		self.checkDistance = int( dict["param2"] if len( dict["param2"] ) > 0 else 0 )
		self.visible = bool( int( dict["param3"] if len( dict["param3"] ) > 0 else 0 ) )
		self.lasted = float( dict["param4"] if len( dict["param4"] ) > 0 else 0 )
		
	def receive( self, caster, receiver ):
		"""
		��������ʱ
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		if self.targetNpcClassName is None:
			ERROR_MSG( "config error, target npc className is None." )
			return
		if self.checkDistance <= 0:
			ERROR_MSG( "config error, check distance is 0 or less." )
			return
		entities = receiver.entitiesInRangeExt( self.checkDistance )
		for e in entities:
			if e.utype == csdefine.ENTITY_TYPE_NPC and e.className == self.targetNpcClassName:
				if e.isReal():
					e.setVisibleByRole( caster, self.visible, self.lasted )
				else:
					e.remoteCall( "setVisibleByRole", ( caster, self.visible, self.lasted ) )
		Spell.receive( self, caster, receiver )