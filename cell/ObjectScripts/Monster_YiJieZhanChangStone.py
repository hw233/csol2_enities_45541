# -*- coding: gb18030 -*-
#
# $Id: $

import BigWorld
import csdefine
from bwdebug import DEBUG_MSG
from Monster import Monster


class Monster_YiJieZhanChangStone(Monster):
	"""
	异界战场中的洪荒灵石
	"""
	def __init__( self ):
		"""
		初始化
		"""
		Monster.__init__( self )
	
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		初始化自己的entity的数据
		"""
		Monster.initEntity( self, selfEntity )
		
		if not selfEntity.getCurrentSpaceType() == csdefine.SPACE_TYPE_YI_JIE_ZHAN_CHANG :
			return
		
		spaceBase = selfEntity.getCurrentSpaceBase()
		if spaceBase:
			spaceBase.cell.remoteScriptCall( "onYiJieStoneCreate", () )

	def dieNotify( self, selfEntity, killerID ):
		"""
		死亡通知；当selfEntity的die()被触发时被调用
		"""
		Monster.dieNotify( self, selfEntity, killerID )
		
		killer = BigWorld.entities.get( killerID )
		killerDBID = 0
		if not killer : return
		if killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ) :
			killerDBID = killer.databaseID
		elif killer.isEntityType( csdefine.ENTITY_TYPE_PET ) :
			killer = killer.getOwner().entity
			killerDBID = getattr( killer, "databaseID", 0 )
		if killerDBID == 0 : return
		
		spaceBase = selfEntity.getCurrentSpaceBase()
		if spaceBase:
			spaceBase.cell.remoteScriptCall( "onYiJieStoneDie", ( killerDBID, ) )
		