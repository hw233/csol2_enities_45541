# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *

class SpawnPoint( object ):
	"""
	"""
	def __init__( self ):
		object.__init__( self )
	
	def initEntity( self, selfEntity ):
		try:
			cell = selfEntity.createOnCell
			del selfEntity.createOnCell
		except AttributeError, e:
			cell = None
		
		if cell is not None:
			selfEntity.createCellEntity( cell )
		
	def onLoseCell( self, selfEntity ):
		selfEntity.destroy()

	def onGetCell( self, selfEntity ):
		selfEntity.cell.onBaseGotCell()
	
	def initEntityParams( self, spaceEntity, params ):
		"""
		virtual method.
		��ʼ��һ�²���
		"""
		return {}
	
	def initTempParams( self, spaceEntity, params ):
		"""
		virtual method.
		��ʼ��һ�²���
		"""
		return {}
	
	def createEntity( self, params, spaceEntity, position, direction ):
		"""
		����SpawnPoint Entity
		return Entity
		"""
		entityType = self.getEntityType()
		argList = []
		arg = {}
		arg[ "spawnType" ] = self.__class__.__name__
		arg[ "spaceType" ] = spaceEntity.className
		arg[ "createOnCell" ] = spaceEntity.cell
		arg[ "position" ] = position
		arg[ "direction" ] = direction
		arg[ "entityParams" ] = self.initEntityParams( spaceEntity, params )
		arg[ "tempMapping" ] = self.initTempParams( spaceEntity, params )
		
		argList.append( arg )
		argList.append( params )
		entity = BigWorld.createBaseLocally( entityType, *argList )
		return entity
	
	def createBaseEntity( self, selfEntity, entityName, params ):
		"""
		ˢ����base�Ĺ���
		"""
		dict = {	"PYDATASECTION"	: params,
					"createOnCell"	: self.cell,
					"position"		: params[ "position" ],
					"direction"		: params[ "direction" ],
				}
				
		e = g_objFactory.createLocalBase( entityName , dict )
	
	def getEntityType( self ):
		"""
		��ȡSpawnPoint �� Entity Type
		retrun String
		"""
		return "SpawnPointNormal"
