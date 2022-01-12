# -*- coding: gb18030 -*-
#
# $Id: Spell_Item_Dart_Add_Speed.py,v 1.1 2008-09-05 03:42:03 zhangyuxing Exp $

from SpellBase import *
from Spell_BuffNormal import Spell_ItemBuffNormal
import csstatus
import BigWorld
import csdefine
import csarithmetic
from interface.State import State

class Spell_Item_Dart_Add_Speed( Spell_ItemBuffNormal ):
	"""
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
		#self.param1 = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 		# �����ڳ��ľ���
				
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if caster.isReal():
			dartId = caster.queryTemp( 'dart_id', 0 )
			caster.statusMessage( csstatus.SKILL_USE_ITEM_DART_ADD_SPEED )
			receiver = BigWorld.entities[dartId]
		Spell_ItemBuffNormal.receive( self, caster, receiver )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		for id in caster.questsTable._quests:
			if caster.getQuest( id ).getType() == csdefine.QUEST_TYPE_DART or caster.getQuest( id ).getType() == csdefine.QUEST_TYPE_MEMBER_DART:
				dartId = caster.queryTemp( 'dart_id', 0 )
				if BigWorld.entities.has_key( dartId ):
					return self.totalCheck( caster, target)
		
		return csstatus.SKILL_USE_ITEM_DO_NOT_FIND_DART
		
	
	def totalCheck( self, caster, target ):
		"""
		"""
		if caster.actionSign( csdefine.ACTION_FORBID_USE_ITEM ) and not( caster.vehicle and caster.vehicle.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ) ):
			if caster.getState() == csdefine.ENTITY_STATE_PENDING:
				return csstatus.CIB_MSG_PENDING_CANT_USE_ITEM
			return csstatus.CIB_MSG_TEMP_CANT_USE_ITEM

		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER

		# ��鼼��cooldown
		if not self.isCooldown( caster ):
			return csstatus.SKILL_ITEM_NOT_READY

		if isinstance( caster, State ) and caster.isState( csdefine.ENTITY_STATE_VEND ):	# ��̯״̬�������ͷ��κμ���
			return csstatus.SKILL_VENDING


		# ʩ��ǰ��Ҫ���ʩ���ߵ������Ƿ��㹻
		state = self.castValidityCheck( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# ���ʩ���ߵ������Ƿ��㹻
		state = self.checkRequire_( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		# ���Ŀ���Ƿ���Ϸ���ʩչ
		state = self._castObject.valid( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state
		return csstatus.SKILL_GO_ON