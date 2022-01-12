# -*- coding: gb18030 -*-

# 10 级剧情副本 
# alienbrain://PROJECTSERVER/创世Online/绿色版本/09_游戏世界/05_副本设计/04_剧情副本/10级剧情副本.docx
# by mushuang 

from SpaceCopy import SpaceCopy


class SpaceCopyBeforeNirvana( SpaceCopy ) :
	def __init__( self ):
		SpaceCopy.__init__( self )		
		self.spawnMonstersList = {}
		
	def addSpawnPointCopy( self, mailbox, entityName ):
		"""
		define method
		"""
		if self.spawnMonstersList.has_key( entityName ):
			self.spawnMonstersList[entityName].append( mailbox )
		else:
			self.spawnMonstersList[entityName] = [mailbox]
		
	def openDoor( self, params ):
		"""
		define method，通过spawnPoint找到门entity，打开门entity
		"""
		for e in self.spawnMonstersList[ params["entityName"] ]:
			#e.cell.openDoor()
			e.cell.remoteCallScript( "openDoor", [ False, ] )
