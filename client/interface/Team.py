# -*- coding: gb18030 -*-
#
# $Id: Team.py,v 1.105 2008-08-21 09:59:25 huangyongwei Exp $

import time
import BigWorld
import csdefine
import csstatus
import csconst
import Define
import Const
import keys
import GUIFacade
from bwdebug import *
from cscollections import MapList
from Function import Functor
from gbref import rds
from ItemsFactory import BuffItem
from event import EventCenter as ECenter
from config.client.msgboxtexts import Datas as mbmsgs
from MessageBox import *


#����ͷ��·������

HEADERS_OUTLINE = ""		#����Ĭ��ͷ��(������HEADERS_ONLINE,��Ҫ������Դ)
REQUEST_TEAM_INTERVAL = 30

class TeamMember( object ):
	"""
	�����Ա�࣬ÿ��ʵ������һ����Ա�����ṹ��
	"""
	def __init__( self ):
		self.DBID = 0 # DBID
		self.raceclass = -1
		self.name = ""
		self.level = 0
		self.hp = 0
		self.hpMax = 0
		self.mp = 0
		self.mpMax = 0
		self.online = False
		self.objectID = 0
		self.title = []						#���ѵĳƺ�
		self.spaceLabel = 0					#���ѵĿռ�����
		self.position = ( 0.0, 0.0, 0.0 )	#���ѵ�λ��
		self.header = None					#���ѵ�ͷ��
		self.gender = None					#���ѵ��Ա�
		self.spaceID = 0					#���ѵĿռ�ID
		self.petID = 0					#���ѳ�����Ϣ

	def getName( self ) :
		return self.name

	def getPosition( self ) :
		return self.position
	
	def getCamp( self ):
		return self.camp


# --------------------------------------------------------------------
# --------------------------------------------------------------------
class Team:
	def __init__( self ):
		self.captainID = 0 				# entityID���ӳ�ID
		self.teamID = 0					# ����ID
		self.teamMember = MapList()		# [TeamMember,...] �����Ա��ID����
		self.__teammemberBuffs = {}		# ���� buff �б�{ ���� ID : [buff �б�] }  ( hyw -- 2008.9.24 )
		self.pickUpState = csdefine.TEAM_PICKUP_STATE_FREE

		self.followTargetID = 0				# ��������id
		self.teamFollowTimerID = 0			# �����������timeID
		self.teamOutSapceTimerID = 0		# �뿪space����ʱtimeID
		self.captainStartPosition = ( 0, 0, 0 )	# ��ʼ����ʱ�ӳ��ĳ�ʼλ��
		self.copyInterfaceBox = None 		# ��Ϣȷ�Ͽ�
		self.followWaitTime = 0				# ����ȴ�ʱ��

		self.requestTeamClearTimer = 0		# ��������������ݵ�timer
		self.requestTeamPlayerDict = {}		# ������ӵ���Ҽ���

	def onBecomePlayer( self ) :
		"""
		ֻ���� PlayerRole ʱ���Żᱻ����
		"""
		rds.shortcutMgr.setHandler( "PREPARE_FOR_TEAM_INVITE", self.prepareForTeamInvite )			# ����׼���������״̬

	#---------------------------------------------------------------------------------
	# private
	def _addMember( self, playerDBID, playerName, objectID, playerRaceclass, onlineState, headTextureID ):
		"""
		����������

		@param objectID: ��ҵ�EntityID
		@type  objectID: OBJECT_ID
		@param playerName: �������
		@type  playerName: string
		@param playerRaceclass: 
		@type  playerRaceclass: INT32
		@param onlineState: �Ƿ�����
		@type  onlineState: BOOL
		"""
		info = TeamMember()

		info.raceclass = playerRaceclass & csdefine.RCMASK_CLASS
		info.camp = ( playerRaceclass & csdefine.RCMASK_CAMP ) >> 20
		info.gender    = playerRaceclass & csdefine.RCMASK_GENDER
		info.DBID = playerDBID
		info.name = playerName
		info.level = 0
		info.hp = 0
		info.hpMax = 0
		info.mp = 0
		info.mpMax = 0
		info.online = onlineState
		info.objectID = objectID
		info.title = []
		info.spaceLabel = ""
		info.spaceID = 0
		info.position = ( 0.0, 0.0, 0.0 )
		headTexturePath = rds.iconsSound.getHeadTexturePath( headTextureID )
		if not headTexturePath is None:
			info.header = headTexturePath		#�����Զ���ͷ��
		else:
			info.header = Const.ROLE_HEADERS[ info.raceclass ][ info.gender ]	#����ְҵ��ȡͷ��

		self.teamMember[objectID] = info

	def _removeMember( self, objectID ):
		"""
		ɾ��һ����Ա
		@param objectID: ���OBJECTID
		@type objectID: OBJECTID
		"""
		self.teamMember.pop( objectID )

	#---------------------------------------------------------------------------------
	def isCaptain( self ):
		"""
		�ǲ��Ƕӳ�
		"""
		return self.captainID == self.id

	#---------------------------------------------------------------------------------
	def inviteJoinTeamNear( self, playerEntity ):
		"""
		���������
		@param playerEntity: ���ʵ��
		@type playerEntity: Entity

		�ڿͻ��˴���ͬ������������
		"""
		if self.isInSpaceChallenge():
			self.statusMessage( csstatus.CHALLENGE_SPACE_PERSONAL_CREATE_TEAM )
			return

		# ��ǰ��ͼ�Ƿ��������
		if self.isInTeamInviteForbidSpace():
			self.statusMessage( csstatus.TEAM_INVITE_IS_FORBID )
			return

		# ���ս���в������
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_YI_JIE_ZHAN_CHANG :
			self.statusMessage( csstatus.YI_JIE_ZHAN_CHANG_CANNOT_INVITE_TEAM )
			return

		if playerEntity == self:
			#self.statusMessage( csstatus.TEAM_NOT_INVITE_SELF )
			if self.isInTeam():
				self.statusMessage( csstatus.TEAM_IN_TEAM_NOT_CREATE_SELF )
			else:
				self.base.createTeamBySelf()
			return

		if self.isInTeam():
			if self.isCaptain() and self.turnWar_isJoin:		# ����ս�ڼ䲻�üӶ���
				self.statusMessage( csstatus.TONG_TURN_WAR_ON_JOIN_TEAM )
				return

			if self.isTeamFull():
				self.statusMessage( csstatus.TEAM_FULL )
				return

			if playerEntity.hasFlag( csdefine.ROLE_FLAG_TEAMMING ):
				self.statusMessage( csstatus.TEAM_PLAYER_IN_TEAM )
			else:
				self.cell.teamInviteFC( playerEntity.id )
		else:
			if playerEntity.hasFlag( csdefine.ROLE_FLAG_TEAMMING ):
				self.requestJoinTeamNear( playerEntity )
			else:
				self.cell.teamInviteFC( playerEntity.id )

	def requestJoinTeamNear( self, playerEntity ):
		"""
		�������Է��Ķ���
		"""
		playerName = playerEntity.getName()
		if playerName in self.requestTeamPlayerDict:
			self.statusMessage( csstatus.TEAM_REQUEST_TOO_FREQUENT )
			return
		self.requestTeamPlayerDict[playerName] = time.time()
		if not self.requestTeamClearTimer:	# 5��������һ��������ӵ�����
			 self.requestTeamClearTimer = BigWorld.callback( REQUEST_TEAM_INTERVAL, self.clearRequestTeamData )
		playerEntity.cell.requestJoinTeamNear()
#		self.statusMessage( csstatus.TEAM_REQUEST_HAD_BEEN_SEND )

	def clearRequestTeamData( self ):
		"""
		��������Ӷӵ�����
		"""
		BigWorld.cancelCallback( self.requestTeamClearTimer )
		self.requestTeamClearTimer = 0
		for key, value in self.requestTeamPlayerDict.items():
			if value + REQUEST_TEAM_INTERVAL < time.time():
				del self.requestTeamPlayerDict[key]

		if len( self.requestTeamPlayerDict ) > 0:
			self.requestTeamClearTimer = BigWorld.callback( REQUEST_TEAM_INTERVAL, self.clearRequestTeamData )

	def allowPlayerJoinTeam( self, playerID, targetName ):
		"""
		ͬ��Է����������
		"""
		if not self.isCaptain():
			return

		if self.turnWar_isJoin:		# ����ս�ڼ䲻�üӶ���
			self.statusMessage( csstatus.TONG_TURN_WAR_ON_JOIN_TEAM )
			return

		# ��ǰ��ͼ�Ƿ��������
		if self.isInTeamInviteForbidSpace():
			self.statusMessage( csstatus.TEAM_INVITE_IS_FORBID )
			return

		if self.isTeamFull():
			self.statusMessage( csstatus.TEAM_FULL_REFUSE_JOIN )
			return

		try:
			targetEntity = BigWorld.entities[playerID]
		except KeyError:
			self.base.acceptTeamRequset( targetName )
		else:
			self.cell.acceptTeamRequestNear( playerID )

	def refusePlayerJoinTeam( self, playerID, playerName ):
		"""
		�ܾ���ҵ��������
		"""
		if not self.isCaptain():
			return
		try:
			BigWorld.entities[playerID]
		except KeyError:
			self.base.refusePlayerJoinTeam( playerName )
		else:
			self.cell.refusePlayerJoinTeam( playerID )

	def receiveJoinTeamRequest( self, playerName, raceclass, level, entityID ):
		"""
		Define method.
		���ռӶ�����

		@param playerName 	: ����������ҵ�����
		@type playerName 	: STRING
		@param metier 		: ����������ҵ�ְҵ
		@type metier 		: INT32
		@param level 		: ����������ҵĵȼ�
		@type level 		: UINT16
		@param entityID 	: ����������ҵ�entity id
		@type entityID 		: OBJECT_ID
		"""
		# ��ǰ��ͼ�Ƿ�������ӣ���������������������
		if self.isInTeamInviteForbidSpace():
			return
			
		metier = raceclass & csdefine.RCMASK_CLASS
		ECenter.fireEvent( "EVT_ON_APPLIED_JOIN_TEAM", playerName, metier, level, entityID )

	def teamInviteByTeammate( self, targetName, targetID, teammateName, teammateID ):
		"""
		Define method.
		��������Ŀ�������ӣ��ӳ��յ�������Ϣ
		"""
		def query( response ) :
			self.replyTeammateInvite( response == RS_YES, targetName, targetID, teammateID )
		if not rds.statusMgr.isInWorld() :
			query( RS_NO )
			return
		# "���Ķ�Ա%s������%s������飬���Ƿ�ͬ�⣿"
		msg = mbmsgs[0x0181] % ( teammateName, targetName )
		showMessage( msg, "", MB_YES_NO, query, gstStatus = Define.GST_IN_WORLD )

	def replyTeammateInvite( self, agree, targetName, targetID, teamateID ):
		"""
		�ӳ�ͬ���������������ӡ�
		"""
		if not agree:
			self.base.refuseTeammateInvite( targetName, teamateID )
			return
		try:
			targetEntity = BigWorld.entities[targetID]
		except KeyError:
			self.base.teamRemoteInviteFC( targetName )
		else:
			self.cell.teamInviteFC( targetEntity.id )

	def inviteJoinTeam( self, playerName ):
		"""
		Զ�������
		@param playerName: �������
		@type playerName: String
		"""
		if self.isCaptain() and self.turnWar_isJoin:		# ����ս�ڼ䲻�üӶ���
			self.statusMessage( csstatus.TONG_TURN_WAR_ON_JOIN_TEAM )
			return

		# ��ǰ��ͼ�Ƿ��������
		if self.isInTeamInviteForbidSpace():
			self.statusMessage( csstatus.TEAM_INVITE_IS_FORBID )
			return

		# ���ս���в������
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_YI_JIE_ZHAN_CHANG :
			self.statusMessage( csstatus.YI_JIE_ZHAN_CHANG_CANNOT_INVITE_TEAM )
			return

		if self.isTeamFull():
			self.statusMessage( csstatus.TEAM_FULL )
			return

		if self.isInSpaceChallenge():
			if self.challengeType == csconst.SPACE_CHALLENGE_TYPE_SINGLE:
				self.statusMessage( csstatus.CHALLENGE_SPACE_PERSONAL_CREATE_TEAM )
				return

		if playerName == self.getName():
			self.statusMessage( csstatus.TEAM_NOT_INVITE_SELF )
			return
		if self.isTeamMemberByName( playerName ):
			self.statusMessage( csstatus.TEAM_PLAYER_IN_TEAM )
			return
		if playerName in self.requestTeamPlayerDict:
			self.statusMessage( csstatus.TEAM_REQUEST_TOO_FREQUENT )
			return
		self.requestTeamPlayerDict[playerName] = time.time()
		if not self.requestTeamClearTimer:	# 5��������һ��������ӵ�����
			 self.requestTeamClearTimer = BigWorld.callback( REQUEST_TEAM_INTERVAL, self.clearRequestTeamData )
		self.base.teamRemoteInviteFC( playerName )
		#self.statusMessage( csstatus.TEAM_REQUEST_HAD_BEEN_SEND )

	def isTeamFull( self ):
		"""
		�Ƿ������Ա
		"""
		return len( self.teamMember ) >= csconst.TEAM_MEMBER_MAX

	def teamDisemploy( self, playerID ):
		"""
		���鿪��
		@param playerID: ���ID
		@type playerID: OBJECT_ID
		"""
		if not self.teamMember.has_key( playerID ):
			self.statusMessage( csstatus.TEAM_IS_NOT_MEMBER )
			return

		# ���ܿ����Լ�
		if self.id == playerID:
			self.statusMessage( csstatus.TEAM_CAN_NOT_DISEMPLOY_SELF )
			return

		# ���Ƕӳ�
		if not self.isCaptain():
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_CAPTAIN )
			return

		if self.getSpaceLabel() == "fu_ben_bang_hui_che_lun_zhan":			# ��ᳵ��ս�����в��ܽ�ɢ����
			self.statusMessage( csstatus.TONG_TURN_WAR_ON_DISPLOY_TEAMMEMBER )
			return

		if self.isInSpaceChallenge():
			def kickMember( rs_id ):
				if rs_id == RS_YES:
					self.base.leaveTeamFC( playerID )

			showMessage( 0x0186, "", MB_YES_NO, kickMember )
			return

		self.base.leaveTeamFC( playerID )

	#---------------------------------------------------------------------------------
	def teamInviteBy( self, inviterName ):
		"""
		define method.
		�������
		������
		������֪ͨclient

		���̣�
		����client�������

		@param inviterName: �����ߵ�����
		@type  inviterName: STRING
		"""
		# ��ʾ�����Ҫ�����
		if not self.allowInvite:
			self.revertInviteJoinTeam( False )
			return

		if self.state == csdefine.ENTITY_STATE_PENDING:
			self.revertInviteJoinTeam( False )
			return

		if not rds.statusMgr.isInWorld() :
			self.revertInviteJoinTeam( False )
			return

		GUIFacade.onAskJoinTeam( inviterName, 1 )
		if rds.ruisMgr.copyTeamSys.visible :
			rds.ruisMgr.copyTeamSys.visible = False

	def revertInviteJoinTeam( self, agree ):
		"""
		�ظ����
		������
		��agree��ͬ�����

		���̣�
		�������ж�
		��1�������¼�����ڣ��жϲ���
		��ɾ�������¼
		����¼���Ϊ���״̬
		��֪ͨ������ͬ�����

		@param agree: ͬ�����
		@type agree: INT8
		"""
		if self.isInSpaceChallenge():
			if self.challengeType == csconst.SPACE_CHALLENGE_TYPE_SINGLE:
				self.statusMessage( csstatus.CHALLENGE_SPACE_PERSONAL_JOIN_TEAM )
				self.base.replyTeamInviteByFC( False )
				return

		self.base.replyTeamInviteByFC( agree )

	#---------------------------------------------------------------------------------
	def addTeamMember( self, playerID, playerDBID, playerName, playerRaceclass, onlineState, headTextureID ):
		"""
		define method.
		���ͳ�Ա����

		���̣�
		�����Ա�б�����ӳ�Ա

		@param playerID: ��ҵ�EntityID
		@type  playerID: OBJECT_ID
		@param playerName: �������
		@type  playerName: string
		@param playerRaceclass: ���ְҵ
		@type  playerRaceclass: INT32
		@param onlineState: ��ǰ�Ƿ�����
		@type  onlineState: INT8
		@param onlineState: ʰȡ��ʽ
		@type  onlineState: INT8
		"""
		# ��ӳ�Ա
		self._addMember( playerDBID, playerName, playerID, playerRaceclass, onlineState, headTextureID )

		if self.id == playerID:
			if self.copyInterfaceBox: #�˳����鸱��ʱ��ȷ�Ͽ�û����ʧ�����¼������
				self.copyInterfaceBox.hide()
			return

		self.__teammemberBuffs[playerID] = []					# ��� buff �б�( hyw -- 2008.9.24 )
	#	self.team_requestMemberBuffs( playerID )				# ������ѵ� buff

		BigWorld.callback( csconst.TEAM_DATA_UPDATE_TIME, self.updataMemberData )
		BigWorld.callback( csconst.TEAM_DATA_UPDATE_TIME_NEAR, self.updataMemberDataNear )

		GUIFacade.onTeamMemberAdded( self.teamMember[playerID] )
		self.onTeamMemberChange()

	def updataMemberData( self ):
		"""
		�����������
		"""
		player = BigWorld.player()
		if ( not player ) or ( not player.inWorld ) : return	#��ֹ��ɫ����ʱû��captainID�������汨��
		if self.captainID == 0:
			return

		for key in self.teamMember.keys():
			if BigWorld.entities.has_key(key):
				continue
			self.requestTeammateInfo( key )

		if len(self.teamMember) != 0:
			BigWorld.callback( csconst.TEAM_DATA_UPDATE_TIME, self.updataMemberData )

	def updataMemberDataNear( self ):
		"""
		�����������
		"""
		player = BigWorld.player()
		if ( not player ) or ( not player.inWorld ) : return	#��ֹ��ɫ����ʱû��captainID�������汨��
		if self.captainID == 0:
			return
		e = BigWorld.entities
		spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
		for key in self.teamMember.keys():
			if e.has_key(key):
				self.teammateInfoNotify( key, e[key].level, e[key].HP, e[key].HP_Max, e[key].MP, e[key].MP_Max, 0, spaceLabel, e[key].position, e[key].spaceID )
		if len(self.teamMember) != 0:
			BigWorld.callback( csconst.TEAM_DATA_UPDATE_TIME_NEAR, self.updataMemberDataNear )

	def addTeamMemberPet( self, playerID, petID, uname, name, modelNumber, species ):
		"""
		defined method
		���ѳ�����Ϣ
		"""
		if playerID == self.id:return
		if playerID in self.teamMember:
			self.teamMember[playerID].petID = petID
			ECenter.fireEvent( "EVT_ON_TEAM_ADD_MEMBER_PET", playerID, petID, uname, name, modelNumber, species )
			BigWorld.callback( csconst.TEAM_DATA_UPDATE_PET, self.updateMemberPetData )
			BigWorld.callback( csconst.TEAM_DATA_UPDATE_TIME_NEAR, self.updateMemberPetDataNear )

	def updateMemberPetData( self ):
		"""
		Զ����������ѳ�����Ϣ
		"""
		player = BigWorld.player()
		if ( not player ) or ( not player.inWorld ) : return	#��ֹ��ɫ����ʱû��captainID�������汨��
		if self.captainID == 0:
			return
		for key in self.teamMember.keys():
			if BigWorld.entities.has_key(key):
				continue
			self.requestTeammatePetInfo( key )

		if len(self.teamMember) != 0:
			BigWorld.callback( csconst.TEAM_DATA_UPDATE_PET, self.updateMemberPetData )

	def updateMemberPetDataNear( self ):
		"""
		���¸������ѳ�������
		"""
		player = BigWorld.player()
		if ( not player ) or ( not player.inWorld ) : return	#��ֹ��ɫ����ʱû��captainID�������汨��
		if self.captainID == 0:
			return
		es = BigWorld.entities
		for key, member in self.teamMember.items():
			if key == self.id:continue
			petID = member.petID
			if es.has_key( petID ):
				pet = es[petID]
				self.teammatePetInfoNotify( key, petID, pet.uname, pet.name, pet.level, pet.HP, pet.HP_Max, pet.MP, pet.MP_Max, None, pet.modelNumber, pet.species )
		if len(self.teamMember) != 0:
			BigWorld.callback( csconst.TEAM_DATA_UPDATE_TIME_NEAR, self.updateMemberPetDataNear )

	def requestTeammatePetInfo( self, playerID ):
		"""
		������ѳ�����Ϣ
		"""
		if not self.teamMember.has_key( playerID ):
			self.statusMessage( csstatus.TEAM_IS_NOT_MEMBER )
			return
		if not self.teamMember[playerID].online:
			return
		self.base.requestTeammatePetInfoFC( playerID )

	def disbandTeamNotify( self ):
		"""
		define method.
		�����ɢ֪ͨ���˷�����base����
		"""
		self.captainID = 0 				# entityID���ӳ�ID
		self.teamID = 0					# ����ID
		self.teamMember.clear()			# [TeamMember,...] �����Ա��ID����
		self.__teammemberBuffs = {}		# ������ж��� buff �б�
		self.statusMessage( csstatus.TEAM_HAS_DISBAND )
		GUIFacade.onTeamDisbanded()
		self.onTeamMemberChange()
		self.cmi_onLeaveTeam()

	def teamInfoNotify( self, teamID, captainID ):
		"""
		define method.
		֪ͨ������Ϣ

		@param teamID: �����EntityID
		@type teamID: OBJECT_ID
		@param captainID: �ӳ�ID
		@type captainID: OBJECT_ID
		"""
		self.teamID = teamID
		self.captainID = captainID
		self.followTargetID = captainID								# ��ʼ������Ŀ��id��16:38 2009-3-12,wsf
		GUIFacade.onTeamCaptainChanged( captainID )
		rds.helper.courseHelper.interactive( "jiaruduiwu_caozuo" )	# �������ʱ���������̰���( hyw--2009.06.13 )

	# ----------------------------------------------------------------
	def leaveTeamNotify( self, playerID, disemploy ):
		"""
		define method.
		����뿪֪ͨ

		@param playerID: ���ID
		@type playerID: OBJECT_ID
		@param disemploy: �������
		@type disemploy: INT8
		"""
		if playerID == self.id:
			# ����
			self.captainID = 0 #entityID
			self.teamID = 0

			for key in self.teamMember.keys():
				del self.teamMember[ key ]
				GUIFacade.onTeamMemberLeft( key )
			self.__teammemberBuffs = {}						# ��ն��� buff �б� ( hyw -- 2008.9.24 )

			if disemploy:
				self.statusMessage( csstatus.TEAM_HAVE_KICKED_OUT )
			else:
				self.statusMessage( csstatus.TEAM_TEAMMATER_LEAVE_TEAM, self.getName() ) #ԭ�����ﱻд��TEAM_HAS_DISBAND �޸���Ϣ by����
				GUIFacade.onTeamDisbanded()
			self.cmi_onLeaveTeam()
		else:
			# ������Ա
			if disemploy:
				self.statusMessage( csstatus.TEAM_TEAMMATER_TICKED_OUT, self.teamMember[playerID].name )
			else:
				self.statusMessage( csstatus.TEAM_TEAMMATER_LEAVE_TEAM, self.teamMember[playerID].name )

			self._removeMember( playerID )
			if playerID in self.__teammemberBuffs :
				self.__teammemberBuffs.pop( playerID )			# �����Ӷ��ѵ� buff �б�hyw -- 2008.9.24��
			GUIFacade.onTeamMemberLeft( playerID )
			self.cmi_onTeammateLeave( playerID )

		self.onTeamMemberChange()

	def changeCaptain( self, playerID ):
		"""
		�ƽ��ӳ�Ȩ��
		"""
		if not self.teamMember.has_key( playerID ):
			self.statusMessage( csstatus.TEAM_NOT_IN_TEAM )
			return

		if self.teamMember[playerID].objectID == self.id:
			return

		self.base.changeCaptainFC( playerID )

	def changeCaptainNotify( self, playerID ):
		"""
		define method.

		���̣�
		�������¶ӳ�
		  ��ʾ�ӳ��Ѿ��ı�

		@param playerID: ���ID
		@type playerID: OBJECT_ID
		"""
		if self.teamMember.has_key( playerID ):
			self.statusMessage( csstatus.TEAM_TEAMMATER_IS_CAPTAIN, self.teamMember[playerID].name )
			self.captainID = playerID
		else:
			self.statusMessage( csstatus.TEAM_TEAMMATER_IS_CAPTAIN, self.playerName )
			self.captainID = self.id
		GUIFacade.onTeamCaptainChanged( self.captainID )
		if self.isFollowing():
			self.team_followDetect()

	def changePickUpStateNotify( self, state ):
		"""
		define method.
		������Ʒʰȡ��ʽ֪ͨ

		@param state: ���ĵ�ʰȡ��ʽ define in csdefine.py
		@type state: INT8
		"""
		self.pickUpState = state
		if state == csdefine.TEAM_PICKUP_STATE_FREE:
			self.statusMessage( csstatus.TEAM_FREE_PICK )
		elif state == csdefine.TEAM_PICKUP_STATE_ORDER:
			self.statusMessage( csstatus.TEAM_ORDER_PICK )
		elif state == csdefine.TEAM_PICKUP_STATE_SPECIFY:
			self.statusMessage( csstatus.TEAM_LEADER_PICK )
		GUIFacade.onPickUpStateChange( state )

	def rejoinTeam( self, oldEntityID, newEntityID ):
		"""
		define method.
		�����Ա���ߣ����¼��������

		@param oldEntityID: ��Ҿɵ�entityID
		@type  oldEntityID: OBJECT_ID
		@param newEntityID: ����µ�entityID
		@type  newEntityID: OBJECT_ID
		"""
		info = self.teamMember[oldEntityID]
		info.online = True
		info.objectID = newEntityID
		self.teamMember[newEntityID] = info
		self.teamMember.pop( oldEntityID )

		self.__teammemberBuffs[ newEntityID ] = []					# ���´�������buff�б�

		GUIFacade.onTeamMemberRejoin( oldEntityID, newEntityID )
		header_path = info.header
		GUIFacade.onTeamMemberChangeIcon( newEntityID, header_path )#֪ͨGUIͷ��ı��¼�����

		#self.statusMessage( csstatus.TEAM_TEAMMATER_IS_ONLINE, info.name )	# �������߲�֪ͨ��17:55 2009-3-6��wsf
		self.onTeamMemberChange()
		self.cmi_onTeammateLogon( oldEntityID, newEntityID )

	def logoutNotify( self, playerID ):
		"""
		define method.
		��Ա����

		���̣�
		���ڳ�Ա�б����������Ϊ����״̬

		@param playerID: ���ID
		@type playerID: OBJECT_ID
		"""
		if self.teamMember.has_key( playerID ):
			self.teamMember[playerID].online = False

		header_path = HEADERS_OUTLINE
		GUIFacade.onTeamMemberLogOut( playerID )#

		if playerID in self.__teammemberBuffs :				# ��������ʱ������ buff �б���գ�hyw--2008.09.25��
			self.__teammemberBuffs.pop( playerID )

	def teamlogout( self ):
		"""
		����
		"""
		self.captainID = 0
		BigWorld.cancelCallback( self.teamFollowTimerID )
		BigWorld.cancelCallback( self.requestTeamClearTimer )
		self.requestTeamClearTimer = 0

	# -------------------------------------------------
	def team_onMemberAddBuff( self, memberID, buff ) :
		"""
		defined method.
		��һ����������� buff ʱ������
		hyw -- 2008.09.24
		"""
		if memberID not in self.__teammemberBuffs :
			ERROR_MSG( "buff list doesn't contain teammate member: %i" % memberID )
		else :
			self.__teammemberBuffs[memberID].append( buff )
			buffItem = BuffItem( buff )
			ECenter.fireEvent( "EVT_ON_TEAMMEMBER_ADD_BUFF", memberID, buffItem )

	def team_onMemberRemoveBuff( self, memberID, index ) :
		"""
		defined method.
		��һ������ɾ���� buff ʱ������
		hyw -- 2008.09.24
		"""
		if memberID not in self.__teammemberBuffs :
			ERROR_MSG( "buff list doesn't contain teammate member: %i" % memberID )
		else :
			for buff in self.__teammemberBuffs[memberID]:
				if buff["index"] == index:
					buffItem = BuffItem( buff )
					ECenter.fireEvent( "EVT_ON_TEAMMEMBER_REMOVE_BUFF", memberID, buffItem )
					return

	def team_onMemberUpdateBuff( self, memberID, index, buff ) :
		"""
		defined method.
		��һ�����Ѹ�����ĳ�� buff ʱ������
		hyw -- 2008.09.24
		"""
		if memberID not in self.__teammemberBuffs :
			ERROR_MSG( "buff list doesn't contain teammate member: %i" % memberID )
		else :
			self.__teammemberBuffs[memberID][index] = buff
			buffItem = BuffItem( buff )
			ECenter.fireEvent( "EVT_ON_TEAMMEMBER_UPDATE_BUFF", memberID, index, buffItem )

	def team_onMemberPetAddBuff( self, memberID, buff ):
		"""
		define method
		���ѳ������buffʱ����
		"""
		if memberID not in self.teamMember :
			ERROR_MSG( "team list doesn't contain teammate member: %i" % memberID )
			return
		if self.id == memberID:return
		buffItem = BuffItem( buff )
		ECenter.fireEvent( "EVT_ON_TEAMMEMBER_PET_ADD_BUFF", memberID, buffItem )

	def team_onMemberPetRemoveBuff( self, memberID, buff ):
		"""
		define method
		���ѳ����Ƴ�buffʱ����
		"""
		if memberID not in self.teamMember :
			ERROR_MSG( "team list doesn't contain teammate member: %i" % memberID )
			return
		if self.id == memberID:return
		buffItem = BuffItem( buff )
		ECenter.fireEvent( "EVT_ON_TEAMMEMBER_PET_REMOVE_BUFF", memberID, buffItem )
	#---------------------------------------------------------------------------------
	def requestTeammateInfo( self, playerID ):
		"""
		���������״̬

		@param playerID: ���ID
		@type playerID: OBJECT_ID
		"""
		# ��Ҳ��Ƕ�Ա
		#print "TeamClient..........requestTeammateInfo"

		if not self.teamMember.has_key( playerID ):
			self.statusMessage( csstatus.TEAM_IS_NOT_MEMBER )
			return
		if not self.teamMember[playerID].online:
			return
		self.base.requestTeammateInfoFC( playerID )

	def teammateInfoNotify( self, playerID, level, hp, hpMax, mp, mpMax, buff, spaceLabel, position, spaceID ):
		"""
		define method.
		״̬����

		���̣�
		��������ҵ���ʾ״̬

		@param playerID: ���ID
		@type playerID: OBJECT_ID
		@param level: ��ҵȼ�
		@type level: UINT8
		@param hp: ���ID
		@type hp: INT32
		@param hpMax: ���ID
		@type hpMax: INT32
		@param mp: ���ID
		@type mp: INT32
		@param mpMax: ���ID
		@type mpMax: INT32
		@param buff: ���ID
		@type buff: INT32
		"""
		if playerID == self.id:
			return

		if playerID:
			self.teamMember[playerID].hp = hp
			self.teamMember[playerID].level = level
			self.teamMember[playerID].hpMax = hpMax
			self.teamMember[playerID].mp = mp
			self.teamMember[playerID].mpMax = mpMax
			self.teamMember[playerID].spaceLabel = spaceLabel
			self.teamMember[playerID].position = position
			self.teamMember[playerID].spaceID = spaceID

			GUIFacade.onTeamMemberChangeLevel( playerID, level )	# �ȼ��ı�
			GUIFacade.onTeamMemberChangeHP( playerID, hp, hpMax )
			GUIFacade.onTeamMemberChangeMP( playerID, mp, mpMax )

	def teammatePetInfoNotify( self, playerID, petID, uname, name, petLevel, petHP, petHP_Max, petMP, petMP_Max, buff, modelNumber, species ):
		"""
		define method.
		������ҳ������ʾ״̬
		"""
		if playerID == self.id:
			return
		if playerID:
			petInfos = ( petID, uname, name, petLevel, petHP, petHP_Max, petMP, petMP_Max, buff, modelNumber, species )
			self.teamMember[playerID].petID = petID
			ECenter.fireEvent( "EVT_ON_TEAM_MEMBER_PET_INFO_RECEIVE", playerID, petInfos )

	def team_onPetConjureNotify( self, playerID, petID, uname, name, modelNumber, species ):
		"""
		���ѳ����ս֪ͨ
		"""
		if playerID == self.id:
			return
		self.addTeamMemberPet( playerID, petID, uname, name, modelNumber, species )

	def team_onPetWithdrawNotify( self, playerID ):
		"""
		�����ٻس���֪ͨ
		"""
		if playerID == self.id:
			return
		if not playerID in self.teamMember:return
		self.teamMember[playerID].petID = 0
		ECenter.fireEvent( "EVT_ON_TEAM_MEMBER_PET_WITHDRAWED", playerID )

	def teammateLevelChange( self, playerID, level ):
		"""
		define method.
		��ҵȼ��ı�

		@param playerID: ���ID
		@type playerID: OBJECT_ID
		@param level: ��ҵȼ�
		@type level: INT16
		"""
		if playerID != 0:
			self.teamMember[playerID].level = level

			GUIFacade.onTeamMemberChangeLevel( playerID, level )

	def teammatePetLevelChange( self, playerID, petLevel ):
		"""
		���ѳ���ȼ��ı�
		"""
		if playerID != 0:
			ECenter.fireEvent( "EVT_ON_TEAM_MEMBER_PET_LEVEL_CHANGE", playerID, petLevel )

	def teammateNameChange( self, entityID, playerName ):
		"""
		�ɷ��������߿ͻ��ˣ�������ĳ����Ա��������ʲô

		@param   entityID: ��Աentity id
		@type    entityID: OBJECT_ID
		@param playerName: ��Ա����
		@type  playerName: STRING
		@return:           ��
		"""
		if entityID != 0:
			self.teamMember[entityID].name = playerName
			GUIFacade.onTeamMemberChangeName( entityID, playerName )

	def teammateNameChange( self, playerID, petName ):
		"""
		���ѳ������Ƹı�
		"""
		if playerID != 0:
			ECenter.fireEvent( "EVT_ON_TEAM_MEMBER_PET_NAME_CHANGE", playerID, petName )

	def teammateSpaceChange( self, playerID, spaceLabel ):
		"""
		define method.
		��ҿռ�λ�øı�

		@param playerID: ���ID
		@type playerID: DATABASE_ID
		@param spaceLabel: ��ҳ��ڿռ�
		@type spaceLabel: STRING
		"""

		if self.teamMember.has_key( playerID ):
			self.teamMember[playerID].spaceLabel = spaceLabel

			GUIFacade.onTeamMemberChangeSpace( playerID, spaceLabel )

	def disbandTeam( self ):
		"""
		��ɢ����
		"""
		if self.isCaptain():
			if self.getSpaceLabel() == "fu_ben_bang_hui_che_lun_zhan":			# ��ᳵ��ս�����в��ܽ�ɢ����
				self.statusMessage( csstatus.TONG_TURN_ON_DISBAND_TEAM )
				return
			if self.isInSpaceChallenge():
				def disband( rs_id ):
					if rs_id == RS_YES:
						self.base.disbandTeamFC()

				showMessage( 0x0184, "", MB_YES_NO, disband )
				return
			self.base.disbandTeamFC()
		else:
			self.statusMessage( csstatus.TEAM_TEAMMATER_NOT_CAPTAIN )

	def leaveTeam( self ):
		"""
		������
		"""
		if self.getSpaceLabel() == "fu_ben_bang_hui_che_lun_zhan":			# ��ᳵ��ս�����в��ܽ�ɢ����
			self.statusMessage( csstatus.TONG_TURN_WAR_ON_LEAVE_TEAM )
			return
		if self.isInSpaceChallenge():
			def leave( rs_id ):
				if rs_id == RS_YES:
					self.base.leaveTeamFC( self.id )

			showMessage( 0x0185, "", MB_YES_NO, leave )
			return

		self.base.leaveTeamFC( self.id )

	def isTeamMemberByName( self, playerName ):
		"""
		ͨ�������ж϶Է��Ƿ����
		"""
		for teammateInfo in self.teamMember.values():
			if teammateInfo.name == playerName:
				return True
		return False

	def isJoinTeam( self ):
		"""
		����Ƿ��ڶ�����
		"""
		return self.teamID != 0

	def isTeamMember( self, ID ):
		"""
		����Ƿ��ڶ�����

		@param ID: ���ID
		@type ID: OBJECT_ID
		"""
		return self.teamMember.has_key( ID )

	def isInTeam( self ):
		"""
		�ж��Լ��Ƿ��ڶ�����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.teamID != 0

	def changePickUpQuality( self, quality ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_PICKUP_QUALITY_CHANGE", quality )

	def changeRollQuality( self, quality ):
		"""
		define method
		"""
		pass


	def teamNotifyWithMemberName( self, statusID, id ):
		"""
		��ʾ��Ϣ�����������Ա����
		"""
		self.onStatusMessage( statusID, "(\'%s\',)" % self.teamMember[id].name )

	def allcateDropItem( self, index ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_CAPTAIN_ALLOCATE_ITEM", index )

	# ---------------------------------------------------------------------------------
	# ��Ӹ���
	# ---------------------------------------------------------------------------------
	def team_leadTeam( self ):
		"""
		�ӳ�������Ӹ���
		"""
		if not self.isCaptain():
			return
		self.statusMessage( csstatus.TEAM_CAPTAIN_LEAD_TEAM )
		nameList = []
		if self.isTeamLeading():
			for entity in self.entitiesInRange( csconst.TEAM_FOLLOW_DISTANCE, lambda entity : self.teamMember.has_key( entity.id ) and entity.isFollowing() ):
				nameList.append( entity.getName() )
			if len( nameList ):
				self.statusMessage( csstatus.TEAM_FOLLOW_ALREADY_PLAYER, ",".join( nameList ) )

		self.cell.leadTeam()

	def team_requestFollow( self ):
		"""
		Define method.
		ѯ���Ƿ�Ҫ����ӳ�
		"""
		if not rds.statusMgr.isInWorld() : return
		def query( rs_id ):
			"""
			"""
			if self.isCaptain():
				return
			captain = BigWorld.entities.get( self.captainID )
			if captain is None or not self.isSamePlanes( captain ):	# ����ӳ�����AOI����ô����û�յ�����
				return

			if rs_id == RS_OK and time.time() - requestTime < Const.TEAM_FOLLOW_REQUEST_VALIDITY:
				reply = True
				if self._isVend():
					self.statusMessage( csstatus.TEAM_FOLLOW_CANT_VEND )
					return
				if self.effect_state & csdefine.EFFECT_STATE_SLEEP:
					self.statusMessage( csstatus.TEAM_FOLLOW_CANT_SLEEP )
					return
				if self.effect_state & csdefine.EFFECT_STATE_VERTIGO or self.effect_state & csdefine.EFFECT_STATE_BE_HOMING:
					self.statusMessage( csstatus.TEAM_FOLLOW_CANT_VERTIGO )
					return
				if self.effect_state & csdefine.EFFECT_STATE_FIX:
					self.statusMessage( csstatus.TEAM_FOLLOW_CANT_FIX )
					return
				if self.position.flatDistTo( captain.position ) > csconst.TEAM_FOLLOW_DISTANCE:
					self.statusMessage( csstatus.FOLLOW_FORBID_TOO_FAR )
					return
				if not self.getState() in [ csdefine.ENTITY_STATE_FREE, csdefine.ENTITY_STATE_FIGHT ]:
					self.statusMessage( csstatus.FOLLOW_FORBID_STATE )
					return
			else:
				reply = False

			self.cell.team_replyForFollowRequest( reply )

		requestTime = time.time()	# �յ������ʱ�̣��ظ������ܳ���һ���ӷ��������ܾ�����
		# "�Ƿ�Ҫ����ӳ��ж�?"
		showAutoHideMessage( Const.TEAM_FOLLOW_REQUEST_VALIDITY, 0x0183, "", MB_OK_CANCEL, query, gstStatus = Define.GST_IN_WORLD )

	def team_startFollow( self ):
		"""
		��ʼ����ӳ��ж�
		"""
		captainEntity = BigWorld.entities.get( self.captainID )
		if captainEntity is None:
			self.cell.team_cancelFollow()
			return

		pet = self.pcg_getActPet()
		if pet is not None:
			pet.setActionMode( csdefine.PET_ACTION_MODE_FOLLOW )
		self.captainStartPosition = captainEntity.position[:]		# ����ӳ��ĳ�ʼλ�ã�����ӳ�������ô��Ա�Ͳ���ʼ����
		self.pursueEntity( captainEntity, Const.TEAM_FOLLOW_START_DISTANCE )
		#self.moveTo( self.__followPositionConvert( captainEntity.position, Const.TEAM_FOLLOW_START_DISTANCE ) )
		self.statusMessage( csstatus.TEAMATE_START_FOLLOW )
		self.team_followDetect()

	def team_stopFollow( self ):
		"""
		ֹͣ����
		"""
		self.resetTeamFollow()

	def isFollowing( self ):
		"""
		�Ƿ��ڸ���״̬
		"""
		return self.effect_state & csdefine.EFFECT_STATE_FOLLOW

	def isTeamLeading( self ):
		"""
		�Ƿ�����������״̬
		"""
		return self.effect_state & csdefine.EFFECT_STATE_LEADER

	def team_checkFollow( self ):
		"""
		�ж��Ƿ��ܸ���

		�������Ŀ����
		"""
		if time.time() > self.followWaitTime + Const.TEAM_FOLLOW_WAIT_TIEM:	# �ȴ�ʱ�䵽
			self.followWaitTime = 0
			return False
		return True

	def team_followDetect( self ):
		"""
		�������
		"""
		BigWorld.cancelCallback( self.teamFollowTimerID )

		# ����������ڴ����д����˸����⣬��ô�п����Ҳ����ӳ���ӳ���λ�þ��벻���ʣ�������Ҳ����ӳ���
		# �ӳ�λ��̫Զʱ��һ��Const.TEAM_FOLLOW_WAIT_TIEM�Ļ��壬���Const.TEAM_FOLLOW_WAIT_TIEM��
		# �����ܷ��ϸ�����������ô�˳����档
		captainEntity = BigWorld.entities.get( self.captainID )
		if self.followWaitTime == 0:
			self.followWaitTime = time.time()		# ��¼���Ϸ��Ŀ�ʼʱ��
		if captainEntity is None:
			if not self.team_checkFollow():		# �ȴ�ʱ�䵽
				self.team_cancelFollow( csstatus.TEAM_FOLLOW_FAIL )
			else:
				self.teamFollowTimerID = BigWorld.callback( Const.TEAM_FOLLOW_DETECT_INTERVAL, self.team_followDetect )
			return
		if self.position.flatDistTo( captainEntity.position ) > csconst.TEAM_FOLLOW_DISTANCE:
			if not self.team_checkFollow():		# �ȴ�ʱ�䵽
				self.team_cancelFollow( csstatus.TEAM_FOLLOW_FAIL )
			else:
				self.teamFollowTimerID = BigWorld.callback( Const.TEAM_FOLLOW_DETECT_INTERVAL, self.team_followDetect )
			return
		self.followWaitTime = 0					# �Ϸ������ã�������ۼ�

		if self.captainStartPosition == captainEntity.position:	# �ӳ���û��ʼ�ж��������ȴ�
			self.teamFollowTimerID = BigWorld.callback( Const.TEAM_FOLLOW_DETECT_INTERVAL, self.team_followDetect )
			return

		followTarget = BigWorld.entities.get( self.followTargetID )
		if followTarget is None:
			followTarget = captainEntity

		if self.position.flatDistTo( captainEntity.position ) <= Const.TEAM_FOLLOW_BEHIND_DISTANCE:
			self.teamFollowTimerID = BigWorld.callback( Const.TEAM_FOLLOW_DETECT_INTERVAL, self.team_followDetect )
			return

		self.pursueEntity( followTarget, Const.TEAM_FOLLOW_BEHIND_DISTANCE )
		self.teamFollowTimerID = BigWorld.callback( Const.TEAM_FOLLOW_DETECT_INTERVAL, self.team_followDetect )

	def team_followPlayer( self, playerID ):
		"""
		Define method.
		���ո���Ŀ�꿪ʼ�������
		"""
		DEBUG_MSG( "------->>>playerID", playerID )
		self.followTargetID = playerID
		self.team_followDetect()

	def __followPositionConvert( self, targetPosition, distance = Const.TEAM_FOLLOW_BEHIND_DISTANCE ):
		"""
		����λ��ת��

		@param targetPosition : Ŀ�굱ǰλ�ã�Vector3
		rType : ��targetPosition·��ΪConst.TEAM_FOLLOW_BEHIND_DISTANCE�׵�position��Vector3

		�����self.position��targetPosition�ĵ�λ�����ķ�������Ȼ���ģConst.TEAM_FOLLOW_BEHIND_DISTANCE
		"""
		return ( -( targetPosition - self.position ) / self.position.flatDistTo( targetPosition ) ) * distance

	def team_cancelFollow( self, statusID ):
		"""
		�����˳�����
		"""
		self.resetTeamFollow()
		if self.isCaptain():
			self.cell.captainStopFollow()
			return
		self.statusMessage( statusID )
		self.cell.team_cancelFollow()

	def team_leaveSpace( self ):
		"""
		�뿪һ���ռ�
		"""
		if not self.isJoinTeam():
			return
		if not self.isFollowing():
			return
		if self.isCaptain():
			return
		BigWorld.cancelCallback( self.teamFollowTimerID )

	def team_enterSpace( self ):
		"""
		����ռ�
		"""
		if not self.isJoinTeam():
			return
		if not self.isFollowing():
			return
		if self.isCaptain():
			return
		self.team_followDetect()

	def resetTeamFollow( self ):
		"""
		���ÿͻ��˸�������
		"""
		BigWorld.cancelCallback( self.teamFollowTimerID )
		self.followTargetID = 0				# ��������id
		self.teamFollowTimerID = 0			# �����������timeID
		self.captainStartPosition = ( 0, 0, 0 )	# ��ʼ����ʱ�ӳ��ĳ�ʼλ��
		self.followWaitTime = 0				# ����ȴ�ʱ��
		self.stopMove()

	def getTeamFollowList( self ):
		"""
		��ø����б�
		"""
		verifyFunction = lambda entity:entity.effect_state & csdefine.EFFECT_STATE_FOLLOW or entity.effect_state & csdefine.EFFECT_STATE_LEADER and entity.id in self.teamMember
		return [ entity.id for entity in self.entitiesInRange( csconst.TEAM_FOLLOW_DISTANCE, verifyFunction ) ]

	def onLeaveTeamInSpecialSpace( self, remainTime ):
		"""
		define method
		"""
		if self.teamOutSapceTimerID != 0:
			BigWorld.cancelCallback( self.teamOutSapceTimerID )
			self.teamOutSapceTimerID = 0

		if self.copyInterfaceBox:
			self.copyInterfaceBox.dispose()

		# ���Ѳ��ڸø����Ķ����У�����%s����뿪�˸��������ȷ�����������뿪��
		self.copyInterfaceBox = showMessage( mbmsgs[0x0182] %( remainTime ), "", MB_OK, self.backToLastSpace )

		def setBoxMsg( remainTime, msg ):
			"""
			"""
			self.copyInterfaceBox.setMessage( msg )
			if remainTime <= 0:
				self.copyInterfaceBox.dispose()
			
			if remainTime > 0:
				remainTime -= 1
				self.teamOutSapceTimerID = BigWorld.callback( 1, Functor( setBoxMsg, remainTime, mbmsgs[0x0182] %( remainTime ) ) )

		BigWorld.callback( 0, Functor( setBoxMsg, remainTime, mbmsgs[0x0182] %( remainTime ) ) )

	def backToLastSpace( self, rs_id ):
		"""
		"""
		self.cell.backToLastSpace()

	# -------------------------------------------------
	def prepareForTeamInvite( self ) :
		"""
		�ı������״������׼���������״̬
		"""
		rds.statusMgr.setToSubStatus( Define.GST_IN_WORLD, PreInviteTemmateStatus() )

# --------------------------------------------------------------------
# �������״̬
# --------------------------------------------------------------------
from StatusMgr import BaseStatus

class PreInviteTemmateStatus( BaseStatus ) :
	def __init__( self ) :
		BaseStatus.__init__( self )
		rds.ccursor.lock( "banner" )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __leave( self ) :
		"""
		�뿪׼���������״̬
		"""
		rds.statusMgr.leaveSubStatus( Define.GST_IN_WORLD, self.__class__ )
		rds.ccursor.unlock( "banner", "normal" )

	def __invite( self ) :
		"""
		�����������
		"""
		player = BigWorld.player()
		target = BigWorld.target.entity
		if target :
			#rds.targetMgr.bindTarget( target )
			if rds.targetMgr.isVehicleTarget( target ) :					# �ж��Ƿ�������
				horseman = target.getHorseMan()
				if horseman is not None :
					player.inviteJoinTeamNear( horseman )
			elif rds.targetMgr.isRoleTarget( target ) :						# ����Ŀ�������
				player.inviteJoinTeamNear( target )							# �����������


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def handleKeyEvent( self, down, key, mods  ) :
		"""
		׼���������״̬������Ϣ�ڴ˴���
		"""
		if rds.worldCamHandler.handleKeyEvent( down, key, mods ) :			# �����ƶ���ͷ
			return True

		if key == keys.KEY_LEFTMOUSE and mods == 0 :
			if down :
				if rds.ruisMgr.isMouseHitScreen() :
					self.__invite()
			else :
				self.__leave()
			return True
		elif key == keys.KEY_ESCAPE :
			self.__leave()
			return True
		return False

