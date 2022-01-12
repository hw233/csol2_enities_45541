# -*- coding: gb18030 -*-

"""
活动混沌入侵
"""
import time
import BigWorld
import csdefine
import random
import csstatus
import cschannel_msgs
import utils
from Function import Function
from Resource.Rewards.RewardManager import g_rewardMgr
from bwdebug import *

TEAM_MEMBER_NEED 	= 3																	#需要的队伍成员


class FuncRoleCompetition( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		"""
		self.__mapName 		= section["param1"].asString								#地图名
		self.__level		= section["param2"].asInt									#需要等级
		self.__positions	= [( -0.918, 5.112, 104.200 ), ( -2.389, 4.678, -60.276 ), ( 71.558, 4.679, 16.489 ), ( -78.512, 4.667, 16.665 )]

		self.__direction = None
		direction = section.readString( "param3" )										#进入朝向
		dir = utils.vector3TypeConvert( direction )
		if dir is None:
			ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section param3 " % ( self.__class__.__name__, direction ) )
		else:
			self.__direction = dir
	
	def do( self, player, talkEntity = None ):
		"""
		进入个人竞技
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
		if player.level < self.__level:
			player.client.onStatusMessage( csstatus.ROLECOMPETITION_FORBID_LEVEL, str(( self.__level, )) )
			return

		if BigWorld.globalData.has_key("AS_RoleCompetitionAdmission"):
			index = random.randint( 0, len( self.__positions ) - 1 )
			pos = self.__positions[index]
			x1 = random.randint( -2, 2 )
			z1 = random.randint( -2, 2 )
			pos = ( pos[0]+x1, pos[1], pos[2]+z1 )
			BigWorld.globalData["RoleCompetitionMgr"].onEnterRoleCompetitionSpace( player.base, player.playerName, \
			self.__mapName, pos, self.__direction, player.level, player.databaseID )
			return
		


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
		return BigWorld.globalData.has_key( "AS_RoleCompetitionAdmission" )

class FuncSignUpRoleCompetition( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		self.__level		= section["param1"].asInt

	def do( self, player, talkEntity = None ):
		"""
		个人竞技报名
		"""
		player.endGossip( talkEntity )
		if player.level < self.__level:
			player.client.onStatusMessage( csstatus.ROLECOMPETITION_FORBID_LEVEL, str(( self.__level, )) )
			return
		if BigWorld.globalData.has_key("AS_RoleCompetitionSignUp"):
			BigWorld.globalData["RoleCompetitionMgr"].requestSignUp( player.level, player.base, player.playerName )
			return
		elif BigWorld.globalData.has_key("AS_RoleCompetitionReady"):
			player.client.onStatusMessage( csstatus.ROLE_COMPETITION_VOICE_4, "" )
			return
		else:
			player.client.onStatusMessage( csstatus.ROLE_COMPETITION_VOICE_6, "" )
			return


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