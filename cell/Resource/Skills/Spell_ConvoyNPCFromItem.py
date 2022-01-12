# -*- coding: gb18030 -*-

import BigWorld

import math
import Math
import random

import csstatus

from Spell_Item import Spell_Item

class Spell_ConvoyNPCFromItem( Spell_Item ):
	def __init__( self ):
		Spell_Item.__init__( self )
		
	def init( self, dict ):
		self._isDestroy = int( dict[ "param1" ] )
		Spell_Item.init( self, dict )
		self._spellClassName = dict[ "param2" ]
		self._resultClassName = dict[ "param3" ].split( "|" )
		self._questID = int( dict[ "param4" ] )
	
	def receive( self, caster, receiver ):	
		dict = {}
		dict[ "level" ] = caster.level
		npcIDs = []
		for r in self._resultClassName:
			eid, enum = r.split( ":" )
			for i in xrange( eval( enum ) ):
				newEntity = receiver.createObjectNearPlanes( eid, self._getCallPosition( receiver ), receiver.direction, dict )
				newEntity.setTemp( "npc_ownerBase", caster.base )
				newEntity.setOwner( caster.id )
				npcIDs.append(newEntity.id)
		tasks = caster.getQuestTasks( self._questID )
		npcids = tasks.query( "follow_NPC" , [] )
		npcids.extend(npcIDs)
		tasks.set( "follow_NPC" , npcids)

		if self._isDestroy == 1:
			receiver.destroy()

	def useableCheck( self, caster, target ):
		if target.getObject().className != self._spellClassName :
			return csstatus.SKILL_USE_ITEM_WRONG_TARGET
		
		return Spell_Item.useableCheck( self, caster, target )

	def _getCallPosition( self, entity ):
		# 取得刷怪的位置
		newPos = Math.Vector3()
		castPos = entity.position
		newPos.x = castPos.x + random.randint( 0, 2 ) * random.choice( ( -1, 1 ) )
		newPos.z = castPos.z + math.sqrt( pow( 2, 2 ) - pow( newPos.x - castPos.x , 2 ) ) * random.choice( ( -1, 1 ) )
		newPos.y = castPos.y

		result = BigWorld.collide( entity.spaceID, ( newPos.x, newPos.y + 10, newPos.z ), ( newPos.x, newPos.y - 10, newPos.z ) )
		if result != None:
			newPos.y = result[0].y
		else:
			newPos = entity.position

		return newPos