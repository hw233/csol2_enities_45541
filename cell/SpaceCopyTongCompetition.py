# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy
import time
import BigWorld
import csconst
import random
from ObjectScripts.GameObjectFactory import g_objFactory
import csstatus

THIRDBOXID				= "10121063"
REWARD_POSITION = ( -2.375, 9.01, 16.637)

class SpaceCopyTongCompetition( SpaceCopy ):

	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )

	def onQueryTongWinner( self, tongDBID ):
		"""
		define method.
		"""
		enterPlayerMBList = self.queryTemp( "enterPlayerMB", [] )
		for e in enterPlayerMBList:
			player = BigWorld.entities[ e.id ]
			if player.tong_dbID == tongDBID:
				player.statusMessage( csstatus.ROLE_GOTO_BOX3 )
				player.statusMessage( csstatus.ROLE_GOTO_BOX3 )
				winnerList = self.queryTemp( "winnerPlayerDBIDs", [] )
				winnerList.append( player.id )
				self.setTemp( "winnerPlayerDBIDs", winnerList )
				g_objFactory.getObject( THIRDBOXID ).createEntity( self.spaceID, REWARD_POSITION, (0, 0, 0), {"tempMapping" : { "winnerPlayerDBIDs" :self.queryTemp( "winnerPlayerDBIDs", 0) } } )
				#发奖励给冠军帮主
				tongEntity = player.tong_getTongEntity( tongDBID )
				tongEntity.sendAwardToChief()
				BigWorld.globalData["TongCompetitionMgr"].sendChampionBox( tongDBID )





