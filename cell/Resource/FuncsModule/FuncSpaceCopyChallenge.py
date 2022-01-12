# -*- coding: gb18030 -*-
#
# $Id: FuncTianguan.py,v 1.6 2008-09-01 03:37:25 zhangyuxing Exp $

"""
"""
from Function import Function
#import ChuangtianguanMgr
import csdefine
import csconst
import csstatus
import Language
import time
import BigWorld

import csdefine

CAN_ENTER_NUM = 1
ENTERN_MENBER_DISTANCE = 30.0
MIN_LEVEL = 40		#进入挑战副本的最低等级
	
class FuncSpaceCopyChallenge( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		"""
		#self.challengeMaxLevelDiff = section.readInt( "param1" )
		pass
		
	def valid( self, player, talkEntity = None ):
		return True
		
	def do( self, player, talkEntity = None ):
		"""
		进入挑战副本。
		"""
		if MIN_LEVEL > player.level:
			player.statusMessage( csstatus.CHALLENGE_MIN_LEVEL ,MIN_LEVEL )
			return
			
		if player.isInTeam() :
			player.statusMessage( csstatus.CHALLENGE_SPACE_PERSONAL_IN_TEAM )
			player.endGossip( talkEntity )
			return
			
		if player.spaceChallengeKey:
			BigWorld.globalData[ "SpaceChallengeMgr" ].reEnter( player.spaceChallengeKey, player.base )
			player.endGossip( talkEntity )
			return
				
		#验证进入次数
		if not self.checkEnterFlags( player ):
			player.statusMessage( csstatus.CHALLENGE_IN_ENTER_FULL )
			player.endGossip( talkEntity )
			return
		
		#player.client.challengeSpaceShow( csconst.SPACE_CHALLENGE_SHOW_TYPE_DEFAULT )
		player.challengeSpaceEnter( player.id )
		player.endGossip( talkEntity )
	
	def checkEnterFlags( self, player ):
		if player.isActivityCanNotJoin( csdefine.ACTIVITY_CHALLENGE_FUBEN ) :
			recordStr = player.queryRoleRecord("challengeFuben_record")
			if recordStr != "":
				timeStr, enterCount = recordStr.split("_")
				if int(enterCount) >= CAN_ENTER_NUM :
					return False
		
		return True

class FuncSpaceCopyChallengeThree( Function ):
	# 进入挑战副本，三人
	def __init__( self, section ):
		pass
	
	def valid( self, player, talkEntity = None ):
		return True
	
	def do( self, player, talkEntity = None ):
		if not player.isInTeam():
			player.statusMessage( csstatus.CHALLENGE_SPACE_MANY_NOT_TEAM )
			player.endGossip( talkEntity )
			return
			
		if player.spaceChallengeKey:
			if player.query( "challengeSpaceType" ) == csconst.SPACE_CHALLENGE_TYPE_SINGLE:
				BigWorld.globalData[ "SpaceChallengeMgr" ].endChallenge( player.spaceChallengeKey )
			else:
				BigWorld.globalData[ "SpaceChallengeMgr" ].reEnter( player.spaceChallengeKey, player.base )
				player.endGossip( talkEntity )
				return
		
		#验证进入次数
		if not self.checkEnterFlags( player ):
			player.statusMessage( csstatus.CHALLENGE_SPACE_MANY_ENTER_FULL )
			player.endGossip( talkEntity )
			return
			
		if BigWorld.globalData.has_key( "spaceChallengeTeam_%d"%player.teamMailbox.id ):
			spaceChallengeKey = BigWorld.globalData[ "spaceChallengeTeam_%d"%player.teamMailbox.id ]
			BigWorld.globalData[ "SpaceChallengeMgr" ].newJoinRequestEnter( spaceChallengeKey, player.base )
			player.endGossip( talkEntity )
			return
			
		if not player.isTeamCaptain():
			player.statusMessage( csstatus.CHALLENGE_OPEN_MUST_CAPTAIN )
			player.endGossip( talkEntity )
			return
			
		memNum = len( player.getAllMemberInRange( ENTERN_MENBER_DISTANCE ) )
		
		if memNum < 3:
			player.statusMessage( csstatus.CHALLENGE_SPACE_MANY_MEM_LESS )
			player.endGossip( talkEntity )
			return
		
		if memNum > 3:
			player.statusMessage( csstatus.CHALLENGE_SPACE_MANY_MEM_MORE )
			player.endGossip( talkEntity )
			return
			
		# 获取附近队友
		minLevel = player.level
		maxLevel = player.level
		teamMemberList = player.getAllMemberInRange( 30 )
		for m in teamMemberList:
			if m == player:
				continue
				
			if m.level < minLevel:
				minLevel = m.level
			if m.level > maxLevel:
				maxLevel = m.level
			
			if m.isReal() and m.spaceChallengeKey:
				if m.query( "challengeSpaceType" ) == csconst.SPACE_CHALLENGE_TYPE_SINGLE:
					BigWorld.globalData[ "SpaceChallengeMgr" ].endChallenge( m.spaceChallengeKey )
			
			#验证队友进入次数
			if not self.checkEnterFlags( m ):
				player.statusMessage( csstatus.CHALLENGE_IN_ENTER_MEM_FULL, m.playerName )
				player.endGossip( talkEntity )
				return
		
		if maxLevel - minLevel >= 5:
			player.statusMessage( csstatus.CHALLENGE_NOT_INT_CONDITION_LEVEL )
			player.endGossip( talkEntity )
			return
			
		if MIN_LEVEL > minLevel:
			player.statusMessage( csstatus.CHALLENGE_MIN_LEVEL ,MIN_LEVEL )
			return
			
		#for m in teamMemberList:
		#	m.client.challengeSpaceShow( csconst.SPACE_CHALLENGE_SHOW_TYPE_DEFAULT )
		
		#player.client.challengeSpaceShow( csconst.SPACE_CHALLENGE_SHOW_TYPE_DEFAULT )
		player.challengeSpaceEnter( player.id )
		player.endGossip( talkEntity )
	
	def checkEnterFlags( self, player ):
		if player.isActivityCanNotJoin( csdefine.ACTIVITY_CHALLENGE_FUBEN_MANY ) :
			recordStr = player.queryRoleRecord("challengeFuben_many_record")
			if recordStr != "":
				timeStr, enterCount = recordStr.split("_")
				if int(enterCount) >= CAN_ENTER_NUM :
					return False
		
		return True

class FuncSpaceCopyPiShanEnter( Function ):
	# 进入劈山副本
	def __init__( self, section ):
		Function.__init__( self, section )
	
	def valid( self, player, talkEntity = None ):
		return True
	
	def do( self, player, talkEntity = None ):
		if player.isInTeam() and not player.isTeamCaptain():
			player.statusMessage( csstatus.CHALLENGE_SPACE_NPC_MUST_CAPTIAN )
			player.endGossip( talkEntity )
			return
			
		if player.spaceChallengeKey:
			BigWorld.globalData[ "SpaceChallengeMgr" ].enterPiShan( player.spaceChallengeKey )
		player.endGossip( talkEntity )

class FuncSpaceCopyPiShanLevel( Function ):
	# 退出劈山副本
	def __init__( self, section ):
		Function.__init__( self, section )
	
	def valid( self, player, talkEntity = None ):
		return True
	
	def do( self, player, talkEntity = None ):
		if player.isInTeam() and not player.isTeamCaptain():
			player.statusMessage( csstatus.CHALLENGE_SPACE_NPC_MUST_CAPTIAN )
			player.endGossip( talkEntity )
			return
			
		if player.spaceChallengeKey:
			BigWorld.globalData[ "SpaceChallengeMgr" ].levelPiShan( player.spaceChallengeKey )
		player.endGossip( talkEntity )

class FuncSpaceCopyBaoXiangEnter( Function ):
	# 进入宝藏副本
	def __init__( self, section ):
		Function.__init__( self, section )
	
	def valid( self, player, talkEntity = None ):
		return True
	
	def do( self, player, talkEntity = None ):
		if player.isInTeam() and not player.isTeamCaptain():
			player.statusMessage( csstatus.CHALLENGE_SPACE_NPC_MUST_CAPTIAN )
			player.endGossip( talkEntity )
			return
			
		if player.spaceChallengeKey:
			BigWorld.globalData[ "SpaceChallengeMgr" ].enterBaoXiang( player.spaceChallengeKey )
		player.endGossip( talkEntity )