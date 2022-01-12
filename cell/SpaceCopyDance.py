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
	���踱��
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
		if time:#��ս����
			BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, csdefine.DANCECOPYTIMELIMIT )
		else: #��ϰ����
			BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, -1 )
		
	def onLeave( self, baseMailbox, params ):
		"""
		define method.
		"""
		SpaceCopy.onLeave( self, baseMailbox, params )
		baseMailbox.cell.onLeaveDanceCopy()
		BigWorld.globalData["DanceMgr"].removeSpace(self.base)
		self.addTimer( 5.0, 0, Const.SPACE_COPY_CLOSE_CBID ) #����뿪��5����������
		
	def regesiterNPC(self, NPCMailbox):
		#define method
		self.NPCMailbox = NPCMailbox
		
	def setDanceChallengeIndex(self, challengeIndex):
		#define method
		self.NPCMailbox.setDanceChallengeIndex(challengeIndex)
		
	def noticeChallengeResult(self, challengeResult):
		#define method, �����������ֻ��һ�����
		self._players[0].noticeChallengeResult(challengeResult)

	def onConditionChange( self, params ):
		"""
		define method
		���ڸ������¼��仯֪ͨ��
		�������¼��仯�����Ƕ���仯����һ�����ݵ���ɣ�Ҳ������һ����
		"""
		self.getScript().onConditionChange( params )
		BigWorld.setSpaceData(self.spaceID, csconst.SPACE_DANCECOPY_COMOBOPOINT, params["comoboPoint"])
		BigWorld.setSpaceData(self.spaceID, csconst.SPACE_DANCECHALLENGE_TIMELIMIT, params["timeLimit"])
		
	def shownDetails( self ):
		"""
		shownDetails ����������ʾ����
		[ 
			0: ʣ��ʱ��
			18�����踱������ʾ�ĸ�����������
			19: ���踱��ÿ����ս������ʱ������
		]
		"""
		# Ĭ����ʾ�������������ʾ����Ҫ����Ҫ�����ⶨ��shownDetails
		return [ 0, 18, 19]

		

			
				
				
		

		
			

		
	