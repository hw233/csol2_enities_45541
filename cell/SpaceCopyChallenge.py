# -*- coding: gb18030 -*-

import time

import BigWorld

import csconst
import Const
import Love3

from SpaceCopy import SpaceCopy

CHALLENGE_SKILL_ID = 122297001

class SpaceCopyChallenge( SpaceCopy ):
	"""
	��ս����
	"""
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopy.__init__( self )
		self.initMonsterInfo()
	
	def initMonsterInfo( self ):
		self.monsterNum, self.bossNum, self.bigBossNum = Love3.g_spaceHuaShanData.getMonsterInfos( self.params[ "spaceChallengeGate" ], self.params[ "spaceChallengeEnterNums" ] )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, self.monsterNum  )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, self.bossNum + self.bigBossNum  )

	def onEnterCommon( self, baseMailbox, params ):
		SpaceCopy.onEnterCommon( self, baseMailbox, params )
		baseMailbox.cell.clearBuff([0])
		baseMailbox.cell.spellTarget( CHALLENGE_SKILL_ID, baseMailbox.id )
		baseMailbox.client.challengeSpaceOnEnter( params[ "challengeSpaceAvatar" ], params[ "challengeSpaceType" ] )
		
	def onLeaveCommon( self, baseMailbox, params ):
		"""
		�˳�
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		if len( self._players ) == 0 and self.params[ "spaceChallengeEnterNums" ] > 1:
			BigWorld.globalData[ "SpaceChallengeMgr" ].endChallenge( self.params[ "spaceChallengeKey" ] )
		else:
			BigWorld.globalData[ "SpaceChallengeMgr" ].playerTempLeave( self.params[ "spaceChallengeKey" ], baseMailbox, self.params[ "spaceChallengeGate" ] )
		
	def shownDetails( self ):
		"""
		shownDetails ����������ʾ����
		[ 
			0: ʣ��ʱ��
			1: ʣ��С��
			2: ʣ��С������
			3: ʣ��BOSS
			4: ��������
			5: ʣ��ħ�ƻ�����
			6: ʣ�����Ӱʨ����
			7: ��һ��ʣ��ʱ��(���Ȫm؅)
			9: ��ɽ�󷨲���
		]
		"""
		return [ 0, 1, 3, 9 ]
