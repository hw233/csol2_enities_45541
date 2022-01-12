# -*- coding: gb18030 -*-
#
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface
from SpaceCopy import SpaceCopy
import Const
import BigWorld

class SpaceCopyTowerDefense( SpaceCopy, SpaceCopyYeWaiInterface ):
	"""
	塔防副本
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )
		SpaceCopyYeWaiInterface.__init__( self )
		
	def addSpawnPoint( self, spawnPointBaseMB ):
		key = "towerDefenseSpawnPoint"
		spawnPointBaseMBList = self.queryTemp( key, [] )
		spawnPointBaseMBList.append( spawnPointBaseMB )
		self.setTemp( key, spawnPointBaseMBList )
		
	def checkSpaceIsFull( self ):
		"""
		检查空间是否满员
		"""
		if self.getPlayerNumber() >= csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ self.getScript().difficulty ]:
			return True
			
		return False
		