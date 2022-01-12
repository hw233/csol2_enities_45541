# -*- coding: gb18030 -*-
import random
# bigworld
import math
import Math
import BigWorld
# common
import csconst
import csdefine
import csstatus
from bwdebug import *
# cell
from Monster import Monster

FORMATION_TYPE_POSITION = {
	1:[(1,0,1),(1,0,-1),(-1,0,-1),(1,0,-1),(-1,0,-2),(1,0,-2),(-1,0,-3),(1,0,-3)]
}

class NPCFormation( Monster ):
	"""
	负责布阵的NPC（主人）
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		
	def registerLineup( self, selfEntity, id ):
		"""
		define method
		怪物创建后，把自己注册到主人上
		"""
		lineupList = selfEntity.queryTemp( "lineupList", [] )
		if id not in lineupList:
			lineupList.append( id )
		selfEntity.setTemp( "lineupList", lineupList )
	
	def setFormation( self, selfEntity, formation ):
		"""
		define method
		设置召唤NPC布阵
		"""
		posInfos = FORMATION_TYPE_POSITION[ formation ]
		for index,nid in enumerate( selfEntity.queryTemp( "lineupList", [] ) ):
			npcEntity = BigWorld.entities.get( nid )
			if npcEntity:
				pos = ( 0.0, 0.0, 0.0 )
				if len( posInfos ) > index:
					pos = posInfos[ index ]
					
				npcEntity.setToOwnerPos( pos )

	def queryRelation( self, selfEntity, entity ):
		"""
		virtual method.
		取得自己与目标的关系

		@param entity: 任意目标entity
		@return : RELATION_*
		"""
		#if selfEntity.isDestroyed or entity.isDestroyed:
		#	return csdefine.RELATION_NOFIGHT
		
		if not selfEntity.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if selfEntity.isUseCombatCamp and entity.isUseCombatCamp:
			return Monster.queryRelation( self, selfEntity, entity )
			
		if hasattr( entity, "getOwnerID" ) and  entity.getOwnerID() == selfEntity.id:
			return csdefine.RELATION_FRIEND
			
		return Monster.queryRelation( self, selfEntity, entity )