# -*- coding: gb18030 -*-

"""
��Ӿ���
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


TEAM_MEMBER_NEED = 3																	#��Ҫ�Ķ����Ա

class FuncTeamCompetitionRequest( Function ):
	"""
	������Ӿ���
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		self.__level		= section["param1"].asInt									#��Ҫ�ȼ�
	
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
	
	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		if not BigWorld.globalData.has_key( "teamCompetitionSingUp" ):
			# ʱ�䲻��
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
		self.__mapName 		= section["param1"].asString								#��ͼ��
		self.__level		= section["param2"].asInt									#��Ҫ�ȼ�
		self.__positions	= [( -0.918, 5.112, 104.200 ), ( -2.389, 4.678, -60.276 ), ( 71.558, 4.679, 16.489 ), ( -78.512, 4.667, 16.665 )]

		self.__direction = None
		direction = section.readString( "param4" )										#���볯��
		dir = utils.vector3TypeConvert( direction )
		if dir is None:
			ERROR_MSG( "Vector3 Type Error��%s Bad format '%s' in section param4 " % ( self.__class__.__name__, direction ) )
		else:
			self.__direction = dir
		
		self.__distance		= section["param5"].asFloat									#��Ա����
		#self.inSpace

	def do( self, player, talkEntity = None ):
		"""
		������Ӿ�������
		����
			�������������Ѷ�Ա����������
				�����Աû�н���������ġ����б�Ǽ�¼��ȥ���ģ�
				Ҫ��Ի����Ƕӳ���
				�ﵽ�ȼ�Ҫ��
				������������3�ˡ�
			������������ֻ���Լ�һ���˽�ȥ��
				����ӡ�
				�ж��鸱�����ڡ�
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
		���һ�������Ƿ����ʹ��
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return BigWorld.globalData.has_key( "teamCompetitionEnter" )