# -*- coding: gb18030 -*-
#
# $Id: Spell_Item_Dart_Add_Speed.py,v 1.1 2008-09-05 03:42:03 zhangyuxing Exp $

from SpellBase import *
from Spell_BuffNormal import Spell_ItemBuffNormal
import csstatus
import BigWorld
import csconst
import csdefine
import csarithmetic

class Spell_Item_EvolutMonster( Spell_ItemBuffNormal ):
	"""
	��������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_ItemBuffNormal.__init__( self )	

			
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_ItemBuffNormal.init( self, dict )
		self.param1 = ( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else "" ) 		#Ҫ�����Ĺ���id

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		receiver.setTemp( "evolute_player_id", caster.id )
		Spell_ItemBuffNormal.receive( self, caster, receiver )
		

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		entity = target.getObject()
		if not entity.getEntityType() in [ csdefine.ENTITY_TYPE_NPC, csdefine.ENTITY_TYPE_MONSTER ] or entity.className != self.param1:
			return csstatus.SKILL_USE_ITEM_CNNOT_EVOLUTE
		return Spell_ItemBuffNormal.useableCheck( self, caster, target )