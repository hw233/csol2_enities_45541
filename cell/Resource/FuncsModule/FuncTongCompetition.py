# -*- coding: gb18030 -*-

"""
帮会竞技场
"""
import time
import BigWorld
import csdefine
import random
import csstatus
from Function import Function
from Resource.Rewards.RewardManager import g_rewardMgr
import utils
from bwdebug import *

COMPETITION_PRESTIGE_LIMIT    = 100    # 帮会竞技的声望限制
COMPETITION_LEVEL_LIMIT       = 60     # 帮会竞技的等级限制
COMPETITION_NUMBER_LIMIT      = 10     # 帮会竞技的60级以上玩家的人数限制


class FuncCompetitionSignUp( Function ):
	"""
	申请帮会竞技
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )


	def do( self, player, talkEntity = None ):
		"""
		点击NPC报名参加帮会竞技
		"""
		player.endGossip( talkEntity )
		allowSignUp = BigWorld.globalData.has_key( "AS_TongCompetition_SignUp" )

		if allowSignUp:
			if not player.checkDutyRights( csdefine.TONG_RIGHT_ACTIVITY_COMPETITION ):	# 权限检测
				player.client.onStatusMessage( csstatus.TONG_COMPETETION_NOTICE_2 , "" )
				return
			else:
				player.tong_competitionRequest( talkEntity )
			player.sendGossipComplete( talkEntity.id )
			return
		else:
			player.client.onStatusMessage( csstatus.TONG_COMPETETION_TONG_SIGNUP , "" )
			player.sendGossipComplete( talkEntity.id )


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


class FuncTongCompetition( Function ):
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
		# 将玩家帮会ID映射到某个进入点，从而支持诸如“进入赛场的玩家，出生点将在副本里几
		# 个坐标点进行随机（与组队乱斗中的机制类似）。同一个帮会的玩家，进入的坐标点是相
		# 同的。进入后的玩家应该是有默认的传送保护BUFF。 ”这样的设计
		self.__mapTongToPos	= {} #{ tongDBID:position }

	def do( self, player, talkEntity = None ):
		"""
		点击NPC进入赛场，5分钟后关闭
		"""
		player.endGossip( talkEntity )

		gameOn = BigWorld.globalData.has_key( "AS_TongCompetition" )
		if not gameOn:		# 如果不在进入副本的5分钟内，那么将不能进入副本
			player.client.onStatusMessage( csstatus.TONG_COMPETETION_TONG_ENTER , "" )
			return

		if player.level < self.__level:
			player.client.onStatusMessage( csstatus.TONG_COMPETITION_FORBID_LEVEL, str(( self.__level, )) )
			return

		if player.tong_dbID == 0:
			player.client.onStatusMessage( csstatus.TONG_COMPETITION_FORBID_MEMBER, "" )
			return

		pos = None
		# if 此帮会已经有成员进入了副本
		if self.__mapTongToPos.has_key( player.tong_dbID ):
			# 使用这个进入点
			pos = self.__mapTongToPos[ player.tong_dbID ]
		# else
		else:
			# 随机一个进入点
			pos = random.choice( self.__positions )
			# 标记：此帮会已经有人进入了副本
			self.__mapTongToPos[ player.tong_dbID ] = pos

		# 避免进去之后玩家挤在一起，加上一点小范围的随机
		x1 = random.randint( -2, 2 )
		z1 = random.randint( -2, 2 )
		pos = ( pos[0]+x1, pos[1], pos[2]+z1 )
		player.gotoSpace( self.__mapName, pos, self.__direction )

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
		return BigWorld.globalData.has_key( "AS_TongCompetition" )

