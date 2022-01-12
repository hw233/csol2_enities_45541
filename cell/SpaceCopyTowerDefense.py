# -*- coding: gb18030 -*-
#
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface
from SpaceCopy import SpaceCopy
import Const
import BigWorld

class SpaceCopyTowerDefense( SpaceCopy, SpaceCopyYeWaiInterface ):
	"""
	��������
	"""
	def __init__( self ):
		"""
		���캯����
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
		���ռ��Ƿ���Ա
		"""
		if self.getPlayerNumber() >= csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ self.getScript().difficulty ]:
			return True
			
		return False
		