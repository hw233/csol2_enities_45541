# -*- coding: gb18030 -*-
#
# $Id: Spell_Item_Dart_Add_HP.py,v 1.1 2008-09-05 03:42:03 zhangyuxing Exp $

from SpellBase import *
from Spell_ItemCure import Spell_ItemCure
import csstatus
import BigWorld
import csconst
import csdefine
import csarithmetic

class Spell_Item_Dart_Add_HP( Spell_ItemCure ):
	"""
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_ItemCure.__init__( self )	

			
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_ItemCure.init( self, dict )
		self.param1 = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 		# �����ڳ��ľ���
				
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if caster.isReal():
			Spell_ItemCure.receive( self, caster, receiver )
			dartId = caster.queryTemp( 'dart_id', 0 )
			receiver = BigWorld.entities[dartId]
			if not receiver.isReal():
				receiver.receiveOnReal( caster.id, self )
				return
		caster.statusMessage( csstatus.SKILL_USE_ITEM_DART_ADD_BLOOD )
		
		self.cureHP( caster, receiver, self._effect_max )
		

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		for id in caster.questsTable._quests:
			if caster.getQuest( id ).getType() == csdefine.QUEST_TYPE_DART or caster.getQuest( id ).getType() == csdefine.QUEST_TYPE_MEMBER_DART:
				dartId = caster.queryTemp( 'dart_id', 0 )
				if BigWorld.entities.has_key( dartId ) and csarithmetic.distancePP3( caster.position, BigWorld.entities[dartId].position ) <= self.param1:
					return Spell_ItemCure.useableCheck( self, caster, target)
		return csstatus.SKILL_USE_ITEM_DO_NOT_FIND_DART
		
	