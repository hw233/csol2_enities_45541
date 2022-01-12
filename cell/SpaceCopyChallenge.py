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
	挑战副本
	"""
	def __init__(self):
		"""
		构造函数。
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
		退出
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		if len( self._players ) == 0 and self.params[ "spaceChallengeEnterNums" ] > 1:
			BigWorld.globalData[ "SpaceChallengeMgr" ].endChallenge( self.params[ "spaceChallengeKey" ] )
		else:
			BigWorld.globalData[ "SpaceChallengeMgr" ].playerTempLeave( self.params[ "spaceChallengeKey" ], baseMailbox, self.params[ "spaceChallengeGate" ] )
		
	def shownDetails( self ):
		"""
		shownDetails 副本内容显示规则：
		[ 
			0: 剩余时间
			1: 剩余小怪
			2: 剩余小怪批次
			3: 剩余BOSS
			4: 蒙蒙数量
			5: 剩余魔纹虎数量
			6: 剩余真鬼影狮数量
			7: 下一波剩余时间(拯救猰貐)
			9: 华山阵法层数
		]
		"""
		return [ 0, 1, 3, 9 ]
