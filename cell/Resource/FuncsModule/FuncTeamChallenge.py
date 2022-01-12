# -*- coding: gb18030 -*-

import time
import random

from Function import Function
from bwdebug import *
import csdefine
import csconst
import BigWorld
import csstatus
import utils

class FuncTeamChallengeSignUp( Function ):
	"""
	报名
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._param1 = section.readInt( "param1" )
		
	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if player.level < self._param1:
			player.statusMessage( csstatus.TEAM_CHALLENGE_MUST_LEVEL,[ ])
		else:
			player.client.challengeTeamSignUp()
			
		player.endGossip( talkEntity )

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True

class FuncTeamChallengeGetReward( Function ):
	"""
	冠军领奖励
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self.itemID = section.readInt( "param1" )	# 奖励的物品ID
		self.requireTitleID = section.readInt( "param2" )	# 称号ID

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		
		if not player.query( "teamChallengeChampion" ) or player.query( "teamChallengeChampion" )[ 0 ] < time.time():
			player.statusMessage( csstatus.TEAM_CHALLENGE_REWARD_UN_CHAMPION )
			player.endGossip( talkEntity )
			return
		
		if player.query( "teamChallengeChampion" )[ 1 ]:
			player.statusMessage( csstatus.TEAM_CHALLENGE_REWARD_ALREADY )
			player.endGossip( talkEntity )
			return
			
		if self.itemID != 0:
			item = player.createDynamicItem( self.itemID )
			kitbagState = player.checkItemsPlaceIntoNK_( [item] )
			if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
				# 背包空间不够
				player.statusMessage( csstatus.CIB_MSG_CANT_OPERATER_FULL )
				player.endGossip( talkEntity.id )
				return
				
			player.addItemAndNotify_( item, csdefine.REWARD_TONG_TEAM_CHALLENGE )
			player.addTitle( self.requireTitleID )
			player.selectTitle( player.id, self.requireTitleID )
		
		teamChallengeChampion = ( player.query( "teamChallengeChampion" )[ 0 ], True )
		player.set( "teamChallengeChampion", teamChallengeChampion )
		player.endGossip( talkEntity )

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True


class FuncTeamChallengeEnterSpace( Function ):
	"""
	进入副本
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self.pos = None
		position = section.readString( "param1" )
		pos = utils.vector3TypeConvert( position )
		if pos is None:
			ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section param1 " % ( self.__class__.__name__, position ) )
		else:
			self.pos = pos
		
		self.distance = section["param2"].asFloat if section["param2"].asFloat else 10									#成员距离

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if not player.isInTeam():
			player.client.onStatusMessage( csstatus.TEAM_CHALLENGE_NO_TEAM, "" )
			player.endGossip( talkEntity )
			return
		
		if len( player.teamMembers ) < csconst.TEAM_CHALLENGE_MEMBER_MUST:
			player.client.onStatusMessage( csstatus.TEAM_CHALLENGE_TEAM_MEM_LESS, "" )
			player.endGossip( talkEntity )
			return
		
		playerStep = self._getStep( player.level )
		if BigWorld.globalData.has_key( 'TeamChallengeTempID_%i'%player.getTeamMailbox().id ):
			if playerStep== BigWorld.globalData[ 'TeamChallengeTempID_%i'%player.getTeamMailbox().id ]:
				player.gotoSpace( "fu_ben_team_challenge", self.pos + ( random.randint(-2,2), 0, random.randint(-2,2) ), (0,0,0) )
			else:
				player.client.onStatusMessage( csstatus.TEAM_CHALLENGE_TEAM_STEP_ERR ,"")
			
			player.endGossip( talkEntity )
			return
		
		if not player.isTeamCaptain():
			if BigWorld.globalData.has_key( "TeamChallengeCloseEnter" ):
				player.client.onStatusMessage( csstatus.TEAM_CHALLENGE_STAGE_UNDERWAY, "" )
			else:
				player.client.onStatusMessage( csstatus.TEAM_CHALLENGE_TEAM_NOT_CAPTAIN, "" )
				player.endGossip( talkEntity )
			return
		
		members = player.getAllMemberInRange( self.distance )
		
		if len( members ) < csconst.TEAM_CHALLENGE_MEMBER_MUST:
			player.client.onStatusMessage( csstatus.TEAM_CHALLENGE_TEAM_MEM_LESS, "" )
			player.endGossip( talkEntity )
			return	
		
		for i in members:
			if i.id == player.id:
				continue
				
			if playerStep != self._getStep( i.level ):
				player.client.onStatusMessage( csstatus.TEAM_CHALLENGE_TEAM_LEVEL_ERR,"" )
				player.endGossip( talkEntity )
				return
			
		enterID = []
		for m in members:
			if m.id in enterID:
				continue
				
			m.gotoSpace( "fu_ben_team_challenge", self.pos + ( random.randint(-2,2), 0, random.randint(-2,2) ), (0,0,0) )
			enterID.append( m.id )

		player.endGossip( talkEntity )
		
	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True

	
	def _getStep( self, level ):
		if level >= csconst.TEAM_CHALLENGE_JOIN_LEVEL_MIN and level <= csconst.TEAM_CHALLENGE_JOIN_LEVEL_MAX:
			if level == csconst.TEAM_CHALLENGE_JOIN_LEVEL_MAX:
				return level / 10 - 1
			else:
				return level / 10
		else:
			return 0

class FuncTeamChallengeSubstitute( Function ):
	# 加入替补名单
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
	
	def do( self, player, talkEntity = None ):
		if not BigWorld.globalData.has_key( "TeamChallengeStart" ):
			player.client.onStatusMessage( csstatus.TEAM_CHALLENGE_TIBU_FAILED,"" )
			player.endGossip( talkEntity.id )
			return
			
		if player.level < 60:
			player.client.onStatusMessage( csstatus.TEAM_CHALLENGE_MUST_LEVEL,"" )
			player.endGossip( talkEntity.id )
			return
			
		if player.isInTeam():
			player.client.onStatusMessage( csstatus.TEAM_CHALLENGE_HAS_TEAM,"" )
			player.endGossip( talkEntity.id )
			return
			
		BigWorld.globalData[ "TeamChallengeMgr" ].substitutePlayer( player.base, player.level )
		player.endGossip( talkEntity )
	
	def valid( self, player, talkEntity = None ):
		return True