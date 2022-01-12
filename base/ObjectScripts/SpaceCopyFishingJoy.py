# -*- coding:gb18030 -*-

from SpaceMultiLine import SpaceMultiLine
from bwdebug import *

class SpaceCopyFishingJoy( SpaceMultiLine ):
	def __init__( self ):
		SpaceMultiLine.__init__( self )
		self.fishingPointList = []
		
	def load( self, section ):
		SpaceMultiLine.load( self, section )
		for item in section["enterPosition"].values():
			position = eval( item.asString )
			self.fishingPointList.append( position )
		DEBUG_MSG( "self.spawnPointList:", self.fishingPointList )

	def getFishingPositionList( self ):
		return self.fishingPointList
		
	def getFirstFishingPosition( self ):
		return self.fishingPointList[0]
		