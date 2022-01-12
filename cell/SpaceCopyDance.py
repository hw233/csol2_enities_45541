# -*- coding: gb18030 -*-
#

"""
"""
import time
import BigWorld
import csdefine
import csconst
from bwdebug import *
from SpaceCopy import SpaceCopy
import Const
import csstatus

class SpaceCopyDance( SpaceCopy ):
	"""
	斗舞副本
	"""
	def __init__( self ):
		SpaceCopy.__init__(self)
		self.NPCMailbox = None
		

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		"""
		SpaceCopy.onEnter( self, baseMailbox, params )
		baseMailbox.cell.onEnterDanceCopy()

	def enterDanceCopy(self, time):
		#define method
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time )
		if time:#挑战斗舞
			BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, csdefine.DANCECOPYTIMELIMIT )
		else: #练习斗舞
			BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, -1 )
		
	def onLeave( self, baseMailbox, params ):
		"""
		define method.
		"""
		SpaceCopy.onLeave( self, baseMailbox, params )
		baseMailbox.cell.onLeaveDanceCopy()
		BigWorld.globalData["DanceMgr"].removeSpace(self.base)
		self.addTimer( 5.0, 0, Const.SPACE_COPY_CLOSE_CBID ) #玩家离开后5秒立即销毁
		
	def regesiterNPC(self, NPCMailbox):
		#define method
		self.NPCMailbox = NPCMailbox
		
	def setDanceChallengeIndex(self, challengeIndex):
		#define method
		self.NPCMailbox.setDanceChallengeIndex(challengeIndex)
		
	def noticeChallengeResult(self, challengeResult):
		#define method, 由于这个副本只有一个玩家
		self._players[0].noticeChallengeResult(challengeResult)

	def onConditionChange( self, params ):
		"""
		define method
		用于副本的事件变化通知。
		副本的事件变化可以是多个变化构成一个内容的完成，也可以是一个。
		"""
		self.getScript().onConditionChange( params )
		BigWorld.setSpaceData(self.spaceID, csconst.SPACE_DANCECOPY_COMOBOPOINT, params["comoboPoint"])
		BigWorld.setSpaceData(self.spaceID, csconst.SPACE_DANCECHALLENGE_TIMELIMIT, params["timeLimit"])
		
	def shownDetails( self ):
		"""
		shownDetails 副本内容显示规则：
		[ 
			0: 剩余时间
			18：斗舞副本中显示的副本的连击数
			19: 斗舞副本每次挑战动作的时间限制
		]
		"""
		# 默认显示的三项，其余有显示的需要，需要在另外定义shownDetails
		return [ 0, 18, 19]

		

			
				
				
		

		
			

		
	