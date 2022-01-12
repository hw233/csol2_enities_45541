# -*- coding: gb18030 -*-

"""
��Ὰ����
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

COMPETITION_PRESTIGE_LIMIT    = 100    # ��Ὰ������������
COMPETITION_LEVEL_LIMIT       = 60     # ��Ὰ���ĵȼ�����
COMPETITION_NUMBER_LIMIT      = 10     # ��Ὰ����60��������ҵ���������


class FuncCompetitionSignUp( Function ):
	"""
	�����Ὰ��
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )


	def do( self, player, talkEntity = None ):
		"""
		���NPC�����μӰ�Ὰ��
		"""
		player.endGossip( talkEntity )
		allowSignUp = BigWorld.globalData.has_key( "AS_TongCompetition_SignUp" )

		if allowSignUp:
			if not player.checkDutyRights( csdefine.TONG_RIGHT_ACTIVITY_COMPETITION ):	# Ȩ�޼��
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
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
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
		self.__mapName 		= section["param1"].asString								#��ͼ��
		self.__level		= section["param2"].asInt									#��Ҫ�ȼ�
		self.__positions	= [( -0.918, 5.112, 104.200 ), ( -2.389, 4.678, -60.276 ), ( 71.558, 4.679, 16.489 ), ( -78.512, 4.667, 16.665 )]

		self.__direction = None
		direction = section.readString( "param3" )										#���볯��
		dir = utils.vector3TypeConvert( direction )
		if dir is None:
			ERROR_MSG( "Vector3 Type Error��%s Bad format '%s' in section param3 " % ( self.__class__.__name__, direction ) )
		else:
			self.__direction = dir
		# ����Ұ��IDӳ�䵽ĳ������㣬�Ӷ�֧�����硰������������ң������㽫�ڸ����Ｘ
		# ���������������������Ҷ��еĻ������ƣ���ͬһ��������ң���������������
		# ͬ�ġ����������Ӧ������Ĭ�ϵĴ��ͱ���BUFF�� �����������
		self.__mapTongToPos	= {} #{ tongDBID:position }

	def do( self, player, talkEntity = None ):
		"""
		���NPC����������5���Ӻ�ر�
		"""
		player.endGossip( talkEntity )

		gameOn = BigWorld.globalData.has_key( "AS_TongCompetition" )
		if not gameOn:		# ������ڽ��븱����5�����ڣ���ô�����ܽ��븱��
			player.client.onStatusMessage( csstatus.TONG_COMPETETION_TONG_ENTER , "" )
			return

		if player.level < self.__level:
			player.client.onStatusMessage( csstatus.TONG_COMPETITION_FORBID_LEVEL, str(( self.__level, )) )
			return

		if player.tong_dbID == 0:
			player.client.onStatusMessage( csstatus.TONG_COMPETITION_FORBID_MEMBER, "" )
			return

		pos = None
		# if �˰���Ѿ��г�Ա�����˸���
		if self.__mapTongToPos.has_key( player.tong_dbID ):
			# ʹ����������
			pos = self.__mapTongToPos[ player.tong_dbID ]
		# else
		else:
			# ���һ�������
			pos = random.choice( self.__positions )
			# ��ǣ��˰���Ѿ����˽����˸���
			self.__mapTongToPos[ player.tong_dbID ] = pos

		# �����ȥ֮����Ҽ���һ�𣬼���һ��С��Χ�����
		x1 = random.randint( -2, 2 )
		z1 = random.randint( -2, 2 )
		pos = ( pos[0]+x1, pos[1], pos[2]+z1 )
		player.gotoSpace( self.__mapName, pos, self.__direction )

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return BigWorld.globalData.has_key( "AS_TongCompetition" )

