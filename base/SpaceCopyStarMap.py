# -*- coding: gb18030 -*-

# 星际地图

# common
from bwdebug import *
# base
from SpaceCopy import SpaceCopy


class SpaceCopyStarMap( SpaceCopy ) :
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
