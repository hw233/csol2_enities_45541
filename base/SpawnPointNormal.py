# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from interface.GameObject import GameObject
import SpawnPointScript

#在文件的这一层，我不希望在这个地方做任何的实现，我希望SpawnPointEntity只是提供接口，以及要迁移的属性定义和方法；
#要实现具体功能性的东西，请去SpawnPointScrip里面去做
#by kenner

class SpawnPointNormal( BigWorld.Base, GameObject ):
	"""
	"""
	def __init__( self ):
		BigWorld.Base.__init__( self )
		if hasattr( self, "cellData" ):
			self.spawnType = self.cellData["spawnType"]
			
		GameObject.__init__( self )
		
		self.getScript().initEntity( self )
		
	def getScript( self ):
		return SpawnPointScript.getScript( self.spawnType )
	
	def getSpawnType( self ):
		return self.spawnType
	
	def createBaseEntity( self, entityName, params ):
		"""
		virtual method.
		刷出有base的怪物
		"""
		self.getScript().createBaseEntity( self, entityName, params )
		
	def onLoseCell( self ):
		self.getScript().onLoseCell( self )
	
	def onGetCell( self ):
		self.getScript().onGetCell( self )
