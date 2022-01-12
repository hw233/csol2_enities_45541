# -*- coding: gb18030 -*-
import BigWorld

import csconst

class SpaceCopyYeWaiInterface:
	def __init__( self ):
		pass
	
	def onSetSpawnInfos( self, monsterNum, bossNum ):
		"""
		define method
		设置怪物，BOSS数量
		"""
		self.monsterCount = monsterNum
		self.bossCount = bossNum
		self.setTemp( "allMonsterCount", monsterNum )
		self.setTemp( "bossCount", bossNum )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, self.monsterCount )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, self.bossCount )
	
	def checkSpaceIsFull( self ):
		"""
		检查空间是否满员
		"""
		if self.getPlayerNumber() >= csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ self.params[ "difficulty" ] ]:
			return True
			
		return False