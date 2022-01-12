# -*- coding: gb18030 -*-

# 40 级剧情副本

# common
from bwdebug import *
# base
from SpaceCopy import SpaceCopy
import BigWorld


class SpaceCopyPlotLv40( SpaceCopy ) :
	def __init__( self ):
		SpaceCopy.__init__( self )
		self.spawnPointList = []

	def onLoseCell( self ):
		SpaceCopy.onLoseCell( self )
		INFO_MSG( "Copy plot lv40 lose cell." )

	def createCell( self ):
		SpaceCopy.createCell( self )
		INFO_MSG( "Copy plot lv40 create cell." )

	def onGetCell( self ):
		SpaceCopy.onGetCell( self )
		INFO_MSG( "Copy plot lv40 get cell." )

	def addSpawnPointControl( self, spawnPoint ):
		"""
		define method
		"""
		self.spawnPointList.append( spawnPoint )
	
	def destroySpawnPointControl( self ):
		"""
		define method
		通过AI来控制该刷新点的销毁
		"""
		for e in self.spawnPointList:
			e.cell.destroySpawnPoint()
