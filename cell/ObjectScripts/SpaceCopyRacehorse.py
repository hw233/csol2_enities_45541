# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyTianguan.py,v 1.5 2008-08-20 01:23:37 zhangyuxing Exp $

"""
"""

from SpaceCopyTemplate import SpaceCopyTemplate
from CopyContent import NEXT_CONTENT
from CopyContent import CopyContent
from CopyContent import CCKickPlayersProcess
from CopyContent import CCWait
from CopyContent import CCEndWait
import BigWorld
import time
import csdefine

WAIT_FOR_RACE	= 760014001	# 等待赛马BUFF
RACE_START		= 1			# 赛马开始
RACE_WAIT_TIME	= 120		# 赛马等待时间(120秒)
RACE_HORSE_TIME = 1200		# 赛马时间

class CCRacehorse( CopyContent ):
	"""
	赛马内容
	"""
	def __init__( self ):
		"""
		"""
		self.key = "raceContent"
		self.val = 1
		
	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.addTimer( RACE_HORSE_TIME, 0, NEXT_CONTENT )

	def endContent( self, spaceEntity ):
		"""
		结束内容
		"""
		BigWorld.globalData["RacehorseManager"].closeRacehorseMap( spaceEntity.params["spaceKey"] )
		CopyContent.endContent( self, spaceEntity )

	def onTeleportReady( self, spaceEntity, baseMailbox ):
		"""
		进入的玩家，加赛马等待BUFF
		"""
		baseMailbox.cell.spellTarget( WAIT_FOR_RACE, baseMailbox.id )


class SpaceCopyRacehorse( SpaceCopyTemplate ):
	"""
	赛马活动
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopyTemplate.__init__( self )
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = True
			
	def initContent( self ):
		"""
		"""
		self.contents.append( CCRacehorse() )
		self.contents.append( CCKickPlayersProcess() )
	
	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		离开的玩家，改变模型，并隐藏赛马快捷栏
		"""
		baseMailbox.cell.onBecomeNonRacer()
		SpaceCopyTemplate.onLeaveCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.cell.remoteCall( "removeFlag", ( csdefine.ROLE_FLAG_AREA_SKILL_ONLY, ) )
	
	def onTeleportReady( self, selfEntity, baseMailbox ):
		"""
		"""
		baseMailbox.cell.onBecomeRacer()
		SpaceCopyTemplate.onTeleportReady( self, selfEntity, baseMailbox )
	
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		SpaceCopyTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )
		enterList = selfEntity.queryTemp( "enterPlayerIDs", [] )
		enterList.append( baseMailbox.id )
		selfEntity.setTemp( "enterPlayerIDs", enterList )
		baseMailbox.cell.remoteCall( "addFlag", ( csdefine.ROLE_FLAG_AREA_SKILL_ONLY, ) )

