# -*- coding: gb18030 -*-

"""
组队竞技
"""
import time
import BigWorld
import csdefine
import cschannel_msgs
import random
import csstatus
import csconst
from Function import Function
from Resource.Rewards.RewardManager import g_rewardMgr
import utils
from bwdebug import *


TEAM_MEMBER_NEED = 3																	#需要的队伍成员

class FuncTeamCompetitionRequest( Function ):
	"""
	申请组队竞技
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		self.__level		= section["param1"].asInt									#需要等级
	
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
	
	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		if not BigWorld.globalData.has_key( "teamCompetitionSingUp" ):
			# 时间不到
			player.client.onStatusMessage( csstatus.TEAM_COMPETETION_TONG_SIGNUP, "" )
			return
		
		if player.level < self.__level:
			player.client.onStatusMessage( csstatus.TEAM_COMPETITION_FORBID_LEVEL, str(( self.__level, )) )
			return
			
		if not player.isInTeam():
			player.client.onStatusMessage( csstatus.TEAM_COMPETITION_FORBID_TEAM, "" )
			return
		
		if not player.isTeamCaptain():
			player.client.onStatusMessage( csstatus.TEAM_COMPETITION_FORBID_CAPTAIN, "" )
			return
			
		if not len( player.teamMembers ) >= TEAM_MEMBER_NEED :
			player.client.onStatusMessage( csstatus.TEAM_COMPETITION_FORBID_MEMBER_AMOUNT,"" )
			return
		player.client.teamCompetitionCheck( self.__level )
		
class FuncTeamCompetition( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		self.__mapName 		= section["param1"].asString								#地图名
		self.__level		= section["param2"].asInt									#需要等级
		self.__positions	= [( -0.918, 5.112, 104.200 ), ( -2.389, 4.678, -60.276 ), ( 71.558, 4.679, 16.489 ), ( -78.512, 4.667, 16.665 )]

		self.__direction = None
		direction = section.readString( "param4" )										#进入朝向
		dir = utils.vector3TypeConvert( direction )
		if dir is None:
			ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section param4 " % ( self.__class__.__name__, direction ) )
		else:
			self.__direction = dir
		
		self.__distance		= section["param5"].asFloat									#成员距离
		#self.inSpace

	def do( self, player, talkEntity = None ):
		"""
		进入组队竞技副本
		规则：
			创建条件：（把队员都拉进来）
				队伍成员没有进入过副本的。（有标记记录进去过的）
				要求对话者是队长。
				达到等级要求。
				队伍人数大于3人。
			进入条件：（只有自己一个人进去）
				有组队。
				有队伍副本存在。
		"""
		player.endGossip( talkEntity )

		index = random.randint( 0, len( self.__positions ) - 1 )
		pos = self.__positions[index]
		x1 = random.randint( -2, 2 )
		z1 = random.randint( -2, 2 )
		pos = ( pos[0]+x1, pos[1], pos[2]+z1 )
		
		if player.level < self.__level:
			player.client.onStatusMessage( csstatus.TEAM_COMPETITION_FORBID_LEVEL, str(( self.__level, )) )
			return
		
		if not player.isInTeam():
			player.client.onStatusMessage( csstatus.TEAM_COMPETITION_FORBID_TEAM, "" )
			return
		
		teamID = player.teamMailbox.id
		level = player.level
		if level == csconst.ROLE_LEVEL_UPPER_LIMIT:
			level = csconst.ROLE_LEVEL_UPPER_LIMIT - 1
		if not BigWorld.globalData.has_key( 'TeamCompetitionSelectedTeam_%i'%teamID ):
			player.client.onStatusMessage( csstatus.TEAM_COMPETITION_TEAM_NOT_BE_CHOOSED ,"")
			return
			
		if BigWorld.globalData.has_key( 'TeamCompetition_%i'%teamID ):
			if level/10 == BigWorld.globalData[ 'TeamCompetition_%i'%teamID ]:
				player.setTemp( "team_compete_team_id", teamID )
				player.gotoSpace( self.__mapName, pos, self.__direction )
			else:
				player.client.onStatusMessage( csstatus.TEAM_COMPETITION_TEAM_HAVE_NOT_IN ,"")
			return
		
		if not player.isTeamCaptain():
			player.client.onStatusMessage( csstatus.TEAM_COMPETITION_FORBID_CAPTAIN_IN, "" )
			return
			
		members = player.getAllMemberInRange( self.__distance )
		
		if not len( members ) >= TEAM_MEMBER_NEED :
			player.client.onStatusMessage( csstatus.TEAM_COMPETITION_FORBID_MEMBER_AMOUNT_1, "" )
			return	
			
		for i in members:
			if i.level < self.__level:
				player.client.onStatusMessage( csstatus.TEAM_COMPETITION_FORBID_MEMBER_LEVEL, "" )
				return
			
			memberLevel = i.level
			if memberLevel == csconst.ROLE_LEVEL_UPPER_LIMIT:
				memberLevel = csconst.ROLE_LEVEL_UPPER_LIMIT - 1
			if memberLevel/10 != BigWorld.globalData[ 'TeamCompetitionSelectedTeam_%i'%teamID ]:
				player.client.onStatusMessage( csstatus.TEAM_COMPETITION_FORBID_MEMBER_LEVEL_AREA,"" )
				return

		for i in members:
			i.setTemp( "team_compete_team_id", teamID )
			i.gotoSpace( self.__mapName, pos, self.__direction )
		

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
		return BigWorld.globalData.has_key( "teamCompetitionEnter" )