# -*- coding: gb18030 -*-
#
# $Id: TeamEntity.py,v 1.27 2008-03-14 00:49:43 yangkai Exp $

import BigWorld
import time
import csdefine
import csconst
import csstatus
import cschannel_msgs
import Love3
from bwdebug import *
import RoleMatchRecorder
from interface.TeamMatcherInterface import TeamMatcherInterface
from interface.TeamMatchedInterface import TeamMatchedInterface
from interface.DomainTeamInterface import UseTeamForDomainInter
from interface.TeamTurnWarInterface import TeamTurnWarInterface
from interface.TeamCampTurnWarInterface import TeamCampTurnWarInterface

DESTORY_TEAM_TIMER 	= 1 	# ���û��Ӧ���ٶ�����ID
OFFLINE_LEAVE_TIMER = 2 	# ������ߣ����ߴ�����TIMER

class TeamEntity( BigWorld.Base, TeamMatcherInterface, TeamMatchedInterface, UseTeamForDomainInter, TeamTurnWarInterface, TeamCampTurnWarInterface ):
	def __init__( self ):
		BigWorld.Base.__init__( self )
		TeamMatcherInterface.__init__( self )				# ������Ϊ��ͨ����Ĺ���
		TeamMatchedInterface.__init__( self )				# ������Ϊƥ�����Ĺ���
		UseTeamForDomainInter.__init__( self )
		TeamTurnWarInterface.__init__( self )
		TeamCampTurnWarInterface.__init__( self )
		self.member = []	# [(entityID, { ... }),  ], see also join()
		self.captainID = self.teamArg["captainBase"].id		# ��¼�ӳ�entityID
		self.pickUpState = self.teamArg["pickUpState"]
		self.pickUpVal2	 = 2

		self.followList = []	# �����Ա�б�

		# ���ڶ��龺����Ϣ
		self.teamChallengeInfo = csdefine.MATCH_LEVEL_NONE
		self.teamChallengeLevel = None
		self.teamChallengeIsGather = False
		self.teamChallengeRecruit = False

		self.teamCompetitionLevel = None
		self.teamCompetitionGatherFlag = False
		
		# ����PVP
		self.baoZangPVPreqTime = 0
		
		self.yingXiongCampReqTime = 0
		
		# ��Ӷӳ�����
		self.join( self.teamArg["captainDBID"], self.teamArg["captainName"],\
				self.teamArg["captainBase"], self.teamArg["captainRaceclass"], self.teamArg["captainHeadTextureID"] )

		# ������ʱ��
		self.addTimer( csconst.TEAM_FEEDBACK_WAIT_TIME, 0, DESTORY_TEAM_TIMER )

		# ���߼�ʱID
		self.leaveTimerID = 0
		self.leaveDBIDs = {}		# { playerDBID : ( id, logout time ) } #����id����Ҫ��Ϊ�˴������

		del self.teamArg	# ɾ����ʼ������

		# ȡ���������
		try:
			self.teamManager = BigWorld.globalBases["TeamManager"]
		except:
			self.teamManager = None
			ERROR_MSG( "get team manager entity error!" )
			return

		# ע�������
		self.teamManager.register( self.id, self )
	
	def _getMemberInfoByDBID( self, playerDBID ):
		"""
		��ȡentity��mailbox
		@return: �����Ա��entityID����Ϣ�ֵ�
		"""
		for entityID, info in self.member:
			if info["playerDBID"] == playerDBID:
				return entityID, info
		return None, None

	def _notifyPlayerTeamMemberInfo( self, playerBase ):
		"""
		����ҷ������ж����Ա����Ϣ�����������˵�

		@param playerBase: ���BASE
		@type  playerBase: mailbox
		"""
		playerBase.teamInfoNotify( self.captainID, self )
		if playerBase.id != self.captainID :	# ��������ʱ���ӳ�����ʰȡ��ʽ��Ϣ�Ѿ��ƶ�����join��
			playerBase.changePickUpStateNotify( self.pickUpState )
			playerBase.cell.changePickUpQualityNotify( self.pickUpVal2 )
		for entityID, info in self.member:
			playerBase.addTeamMember( info["playerDBID"], entityID, info["playerName"], info["playerBase"], info["playerRaceclass"], info["headTextureID"] )

	def onTimer( self, id, userArg ):
		"""
		ʱ�������
		ʱ��ﵽ
		"""
		# �������������޻ظ�����������
		if DESTORY_TEAM_TIMER == userArg:
			if self.isDestroyed:
				return
			self.delTimer( id )
			# ����С��2�ˣ���������
			#if len(self.member) < 2:
			#	self.disband()

		if OFFLINE_LEAVE_TIMER == userArg:
			# �����ӣ�������dict.items()��������iteritems()����Ϊ��������Ҫɾ��
			for dbid, t in self.leaveDBIDs.items():
				if time.time() - t >= csconst.TEAM_OFFLINE_DURATION:
					# û�����߳�Ա
					id,info = self._getMemberInfoByDBID( dbid )
					self.leave( id, id )

	def isfull( self ):
		return len( self.member ) >= csconst.TEAM_MEMBER_MAX


	#-----------------------------------------------------------
	def join( self, playerDBID, playerName, playerBase, playerRaceclass, headTextureID ):
		"""
		<define>
		�����ӵ�������

		@param playerID: ��ҵ�EntityID
		@type playerID: OBJECT_ID
		@param playerDBID: ���DBID
		@type playerDBID: DATABASE_ID
		@param playerBase: ���BASE
		@type playerBase: mailbox
		@param playerName: �������
		@type playerName: string
		@param playerRaceclass: ���ְҵ
		@type playerRaceclass: INT32
		"""
		# �첽�����ʲô���п��ܷ����������Ҫ�ж϶��������Ƿ�����
		if self.isfull():
			# ������������Ҫ֪ͨ�������ʧ��
			playerBase.client.onStatusMessage( csstatus.TEAM_FULL, "" )
			playerBase.clearTeamInfo()	# ��������������
			return

		# ֪ͨ�������ж����Ա��������Ҽ������
		# ���´�������_notifyPlayerTeamMemberInfo�еĴ����ظ�
		for entityID, info in self.member:
			if info["playerBase"]:
				info["playerBase"].addTeamMember( playerDBID, playerBase.id, playerName, playerBase, playerRaceclass, headTextureID )

		# �����³�Ա��������
		info = {	"playerDBID" : playerDBID,
					"playerName" : playerName,
					"playerBase" : playerBase,
					"playerRaceclass" : playerRaceclass,
					"headTextureID": headTextureID,
					"time" : time.time(), }				# ����ʱ��
		self.member.append( ( playerBase.id, info ) )

		# ��ҽ����������ͻ��˷�����Ϣ  2009-3-25 gjx
		if self.captainID != playerBase.id:
			# ������߷��ͼ��������Ϣ
			captainInfo = self._getPlayerInfoByID( self.captainID )
			captainName = captainInfo["playerName"]
			playerBase.client.onStatusMessage( csstatus.TEAM_JOIN_TEAM_SUCCESS, "(\'%s\',)" % captainName )
			# ��ӳ�������ҽ���������Ϣ
			captain = captainInfo["playerBase"]
			captain.client.onStatusMessage( csstatus.TEAM_ACCEPT_JOIN_TEAM, "(\'%s\',)" % playerName )
			# ���������ڶ�����Ա����ʱ���ӳ����Ͷ���ʰȡ��ʽ����Ϣ
			# ����������Ϊ���ȳ�����ӳɹ���Ϣ������ʾʰȡ��ʽ
			if len( self.member ) == 2 :
				captain.changePickUpStateNotify( self.pickUpState )

		# ֪ͨ�³�Ա�����Ա
		self._notifyPlayerTeamMemberInfo( playerBase )
		# ���и������ϵͳ����ش���
		self.tmi_onMemberJoin( playerDBID, playerBase.id )

		# ���¾�������Ϣ
		if self.teamChallengeLevel:
			playerBase.client.teamChallengeUpInfo( self.teamChallengeInfo )
			playerBase.client.teamChallengeUpLevel( self.teamChallengeLevel[0], self.teamChallengeLevel[1] )

		if self.teamChallengeIsGather:
			playerBase.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE )

		if self.teamChallengeRecruit:
			if len( self.member ) >= csconst.TEAM_MEMBER_MAX: # ��������Ա��ʱ���Զ��˳���ļ
				BigWorld.globalData[ "TeamChallengeMgr" ].cancelRecruitTeam( self )

			playerBase.client.teamChallengeOnRecruit()

		if self.teamCompetitionLevel:
			playerBase.client.teamCompetitionNotify( self.teamCompetitionLevel )

		if self.teamCompetitionGatherFlag:
			playerBase.client.teamCompetitionGather()
			playerBase.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TEAM_COMPETITION )

	def leave( self, srcID, dstID ):
		"""
		define method.
		����ָ�����/������
		1�����srcID == dstID���ʾ�Լ�����ӣ�
		2�����srcID != dstID �� srcID�Ƕӳ����ʾ�ӳ�������ҳ�����

		@param srcID: ʹdstID�뿪�����ID
		@type  srcID: OBJECT_ID
		@param dstID: �뿪��������ID
		@type  dstID: OBJECT_ID
		"""
		# ƥ��ĸ���������ӳ����ˣ�ֻ��ͶƱ����
		if self.isMatchedTeam and srcID != dstID :
			return
		# dstID�п����ǿͻ��˹����Ĳ��������ж���Ϸ��ԣ�
		# ����Զ�̵���leaveʱ��dstID�Ѿ����߳����飬��������Ĳ���ǰ����dstID�Ƿ񻹺Ϸ���11:07 2009-11-4��wsf
		dstInfo = self._getPlayerInfoByID( dstID )
		if dstInfo is None:
			return
		if srcID == dstID or srcID == self.captainID:
			# �Լ���ӻ�ӳ�����
			for entityID, info in self.member:
				# ֪ͨÿһ�����ߵ���ң�˭�뿪�˶���
				if info["playerBase"]:
					info["playerBase"].leaveTeamNotify( srcID, dstID )

			# �������������б��У���cancel���ߴ���
			dbid = dstInfo["playerDBID"]
			if dbid in self.leaveDBIDs:
				self.leaveDBIDs.pop( dbid )
				# ���û�������߶�Ա����ͣ��timer
				if len( self.leaveDBIDs ) == 0:
					self.delTimer( self.leaveTimerID )
					self.leaveTimerID = 0
			self.member.remove( ( dstID, dstInfo ) )	# ɾ����ӵ���Ա
		else:
			# �Ȳ����Լ���ӣ�Ҳ���Ƕӳ�������ֱ�Ӻ���
			return

		# ����С��2�ˣ���������
		#if len(self.member) < 2:
		#	self.disband()
		#	return
		if not dstInfo[ "playerBase" ]:# ���ߵĲ�����
			self.kcikNotOnline( dstInfo["playerDBID"] )
			
		self.leaveFollow( dstID )
		# ���и������ϵͳ����ش���
		self.tmi_onMemberLeave( dstInfo["playerDBID"], dstID )

		# �ָ���Ӿ�������״̬
		if self.teamCompetitionGatherFlag:
			dstInfo[ "playerBase" ].cell.challengeRemoveFlagGather( csconst.TRANSMIT_TYPE_TEAM_COMPETITION )

		# �ָ���Ӿ�����ǰ����������Ϣ
		if self.teamCompetitionLevel:
			dstInfo[ "playerBase" ].client.teamCompetitionNotify( 0 )

		memberNum = len( self.member )	# ���������������Ƿ��ɢ���� modified by����
		if memberNum <= 0 or memberNum == len( self.leaveDBIDs ):	# ͳ�����ߵ��������
			dstInfo[ "playerBase" ].cell.turnWar_setJoinFlag( False )
			self.disband()	# �����ɢ
			return

		# �����ӵ��Ƕӳ�����Ҫ:
		if dstID == self.captainID:
			self._autoSelectCaptain()	# ����ѡ��ӳ���֪ͨ�������г�Ա
			dstInfo[ "playerBase" ].cell.turnWar_setJoinFlag( False )

		# ���ö��龺�����Ľ��
		if self.teamChallengeLevel:
			RoleMatchRecorder.update( dstInfo[ "playerDBID" ], csdefine.MATCH_TYPE_TEAM_ABA, self.teamChallengeInfo, dstInfo[ "playerBase" ] )

		if self.teamChallengeIsGather and dstInfo[ "playerBase" ]:
			dstInfo[ "playerBase" ].cell.challengeRemoveFlagGather( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE )
			
		self.turnWar_onMemberLeave( dstInfo )

	def _autoSelectCaptain( self ):
		"""
		�Զ�ѡ��һ���ӳ����˺���һ�����ڵ��ӳ�ֱ�ӣ��ϣ�����ʱ��ӳ��뿪����
		"""
		maxTime = float( 0x7FFFFFFF )
		captain = 0
		for entityID, info in self.member:
			if info["playerBase"] != None and info["time"] < maxTime:	# ����ʱ�����û�е��ߣ���base mailbox��
				captain = info["playerBase"].id
				maxTime = info["time"]
		self.changeCaptain( captain )

	def changeCaptain( self, newCaptainID ):
		"""
		define method.
		�ƽ��ӳ�Ȩ��

		@param newCaptainID: �¶ӳ���entity id
		@type  newCaptainID: OBJECT_ID
		"""
		self.turnWar_onChangeCaptain( newCaptainID )
			
		self.captainID = newCaptainID
		# ֪ͨ���г�Ա
		for ( entityID, info ) in self.member:
			if info["playerBase"]:
				info["playerBase"].changeCaptainNotify( newCaptainID )

		self.onChangeCaptain( newCaptainID )
		self.tmi_onChangeCaptain( newCaptainID )

	def onChangePickUpQuality( self, val ):
		"""
		define method.
		"""
		# ֪ͨ���г�Ա
		self.pickUpVal2 = val
		for ( entityID, info ) in self.member:
			if info["playerBase"]:
				info["playerBase"].cell.changePickUpQualityNotify( val )


	def onChangeRollQuality( self, val ):
		"""
		define method.
		"""
		# ֪ͨ���г�Ա
		self.pickUpVal2 = val
		for ( entityID, info ) in self.member:
			if info["playerBase"]:
				info["playerBase"].cell.changeRollQualityNotify( val )


	def onChangePickUpState( self, state ):
		"""
		define method.
		����ʰȡ״̬

		@param state: �¶ӳ���entity id
		@type  state: OBJECT_ID
		"""
		self.pickUpState = state
		# ֪ͨ���г�Ա
		for ( entityID, info ) in self.member:
			if info["playerBase"]:
				info["playerBase"].changePickUpStateNotify( state )



	#-----------------------------------------------------------
	def logon( self, playerDBID, playerBase ):
		"""
		define method.
		֪ͨ�����������

		@param playerDBID: ���DBID
		@type playerDBID: DATABASE_ID
		@param playerBase: ���BASE
		@type playerBase: mailbox
		"""
		oldEntityID, info = self._getMemberInfoByDBID( playerDBID )
		if info is None:
			# �Ҳ������ʾ������Ѿ������������
			playerBase.clearTeamInfo()
			return

		dic = dict( self.member )
		self.member.remove( ( oldEntityID, dic[oldEntityID] ) )	# ��ɾ���ɵ������Ϣ

		# ֪ͨ���е����߳�Ա
		for entityID, tempinfo in self.member:
			if tempinfo["playerBase"]:
				tempinfo["playerBase"].rejoinTeam( oldEntityID, playerDBID, playerBase )

		info["playerBase"] = playerBase			# ����playerBase
		self.member.append( ( playerBase.id, info ) )		# ���µ�entityID���¹��������Ϣ

		# ������������ҷ��ͳ�Ա�б�
		self._notifyPlayerTeamMemberInfo( playerBase )

		# �����û�����߳�Ա��û����ص�timer
		if self.leaveTimerID:
			self.leaveDBIDs.pop( playerDBID )

			# û�����߳�Ա���ص�timer
			if len(self.leaveDBIDs) == 0:
				self.delTimer( self.leaveTimerID )
				self.leaveTimerID = 0

		# ���и������ϵͳ����ش���
		self.tmi_onMemberLogon( oldEntityID, playerBase.id, playerDBID )

		# ������Ӿ���������Ϣ
		if self.teamChallengeLevel:
			playerBase.client.teamChallengeUpInfo( self.teamChallengeInfo )
			playerBase.client.teamChallengeUpLevel( self.teamChallengeLevel[0], self.teamChallengeLevel[1] )

		if self.teamChallengeIsGather:
			playerBase.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE )

		if self.teamChallengeRecruit:
			playerBase.client.teamChallengeOnRecruit()

		if self.teamCompetitionLevel:
			playerBase.client.teamCompetitionNotify( self.teamCompetitionLevel )

		if self.teamCompetitionGatherFlag:
			playerBase.client.teamCompetitionGather()
			playerBase.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TEAM_COMPETITION )
		
		if self.baoZangPVPreqTime:
			playerBase.client.baoZangPVPonReq( self.baoZangPVPreqTime )
		
		if self.yingXiongCampReqTime:
			playerBase.client.yingXiongCampOnReq( self.yingXiongCampReqTime )
		
	#-----------------------------------------------------------

	def logout( self, playerDBID ):
		"""
		define method.
		�������

		���̣�
		�ڳ�Ա�б����������Ϊ����״̬
		����֪ͨ������Ա���������

		@param playerDBID: ���DBID
		@type  playerDBID: DATABASE_ID
		"""
		entityID, info = self._getMemberInfoByDBID( playerDBID )
		if info is None:
			return

		# �����ӳ�ԱBASE
		info["playerBase"] = None

		# ��������Ϣ
		self.leaveDBIDs[playerDBID] =  time.time()

		if not self.leaveTimerID:
			self.leaveTimerID = self.addTimer( csconst.TEAM_OFFLINE_DURATION, csconst.TEAM_OFFLINE_DETECT_INTERVAL, OFFLINE_LEAVE_TIMER )

		# ͳ�����ߵ��������
		if len( self.member ) - len( self.leaveDBIDs ) == 0:
			# �����ɢ
			self.disband()
		else:
			# ֪ͨ�����Ա�����������
			for playerID, info in self.member:
				if info["playerBase"]:
					info["playerBase"].logoutNotify( playerDBID )

			if entityID == self.captainID:
				self._autoSelectCaptain()
		# ���и������ϵͳ����ش���
		self.tmi_onMemberLogout( playerDBID )
		
		self.turnWar_onMemLogout()

	#-----------------------------------------------------------
	def disband( self ):
		"""
		define method
		�����ɢ����
		֪ͨ���г�Ա�������ɢ
		"""
		# ���и������ϵͳ����ش���
		self.tmi_onDisband()
		
		# ֪ͨ��Ա��������
		for entityID, info in self.member:
			if info["playerBase"]:
				info["playerBase"].disbandTeamNotify()

		# ��������
		self.teamManager.deregister( self.id )
		if self.teamChallengeLevel:
			BigWorld.globalData[ "TeamChallengeMgr" ].teamDismiss( self.id )
		
		if self.baoZangPVPreqTime:
			BigWorld.globalData[ "BaoZangCopyMgr" ].cancel( self.id, False )
			
		self.turnWar_onDisband()
		
		# ֪ͨ���������ɢ
		self.desSpaceCopyNotify()

		# ��������
		self.destroy()


	def getCaptainDBID( self ):
		"""
		����鳤��DBID
		"""
		for entityID, info in self.member:
			if entityID == self.captainID:
				return info['playerDBID']

		
	# -----------------------------------------------------------------------------------------
	# ��Ӹ��棬13:50 2009-3-13��wsf
	# -----------------------------------------------------------------------------------------
	def startFollow( self ):
		"""
		Define method.
		�ӳ�������Ӹ��档
		"""
		self.followList.append( self.captainID )
		#DEBUG_MSG( "------>>>self.followList.", self.followList )

	def stopFollow( self ):
		"""
		Define method.
		�ӳ�ֹͣ��Ӹ���
		"""
		#DEBUG_MSG( "------>>>self.followList.", self.followList )
		for entityID in self.followList:
			playerInfo = self._getPlayerInfoByID( entityID )
			if playerInfo is None:
				continue
			playerBase = playerInfo[ "playerBase" ]
			if playerBase and hasattr( playerBase, "cell" ):
				playerBase.cell.cancelTeamFollow()
				playerBase.client.onStatusMessage( csstatus.TEAM_FOLLOW_CAPTAIN_STOP, "" )
		self.followList = []

	def isFollowState( self ):
		"""
		�����Ƿ�����Ӹ����С�
		"""
		return len( self.followList ) > 0

	def followCaptain( self, entityID ):
		"""
		Define method.
		���ͬ�����ӳ�����������б�

		@param playerDBID : ��ҵ�dbid
		@type playerDBID : databaseID
		"""
		if not self.isFollowState():
			return
		if entityID in self.followList:
			return
		info = self._getPlayerInfoByID( entityID )
		if info is None:
			return
		info[ "playerBase" ].client.team_followPlayer( self.followList[ -1 ] )	# ���������Ӧ�ø���˭
		self.followList.append( entityID )

	def _getPlayerInfoByID( self, entityID ):
		"""
		ͨ����ҵ�id�����ҵ���Ϣ

		@param entityID : OBJECT_ID
		"""
		for playerID, info in self.member:
			if playerID == entityID:
				return info
		return None

	def cancelFollow( self, entityID ):
		"""
		Define method.
		�˳��������

		@param entityID : ��ҵ�entity id
		@type entityID : OBJECT_ID
		"""
		if entityID not in self.followList:
			return

		if len( self.followList ) == 2:	# һ��2�ˣ�һ���˳��������ɢ
			self.stopFollow()
			return

		#DEBUG_MSG( "-------->>>followList,entityID", self.followList, entityID )
		index = self.followList.index( entityID )
		if index + 1 == len( self.followList ):	# ����Ƕ�β��Ա�˳�����
			self.followList.pop()
		else:								# ��������һ����ҵĸ���Ŀ��
			playerBase = self._getPlayerInfoByID( self.followList[ index + 1 ] )[ "playerBase" ]
			if playerBase:
				playerBase.client.team_followPlayer( self.followList[ index - 1 ] )
			self.followList.remove( entityID )

	def onChangeCaptain( self, newCaptainID ):
		"""
		�ӳ��ı���

		@param newCaptainID : �¶ӳ�id,OBJECT_ID
		"""
		#DEBUG_MSG( "------->>>111newCaptainID,followList", newCaptainID, self.followList )
		if not self.isFollowState():
			return

		if newCaptainID not in self.followList:
			self.stopFollow()
			return

		index = self.followList.index( newCaptainID )
		if index + 1 != len( self.followList ):	# ������Ǹ�����ĩһλ��Ա���ӳ�
			playerBase = None
			playerInfo = self._getPlayerInfoByID( self.followList[ index + 1 ] )
			if playerInfo is not None:
				playerBase = playerInfo[ "playerBase" ]
			if playerBase is not None:
				playerBase.client.team_followPlayer( self.followList[ index - 1 ] )
		self.followList.remove( newCaptainID )
		self.followList.insert( 0, newCaptainID )
		#DEBUG_MSG( "-------->>>222self.followList", self.followList )
		playerBase = self._getPlayerInfoByID( self.followList[ 1 ] )[ "playerBase" ]
		if playerBase:
			playerBase.client.team_followPlayer( newCaptainID )

	def leaveFollow( self, playerID ):
		"""
		�ж�Ա����

		@param playerID : ���߶�Ա��id
		@type playerID : OBJECT_ID
		"""
		#DEBUG_MSG( "-------->>>,playerID", playerID )
		if not self.isFollowState():
			return

		if not playerID in self.followList:
			return

		if playerID == self.captainID:
			self.stopFollow()
		else:
			index = self.followList.index( playerID )
			if index + 1 == len( self.followList ):
				self.followList.pop( index )
				return
			playerBase = self._getPlayerInfoByID( self.followList[ index + 1 ] )[ "playerBase" ]
			if playerBase:
				playerBase.client.team_followPlayer( self.followList[ index - 1 ] )
			self.followList.pop( index )

	def setMessage( self ,statuID ):
		"""
		defined method.
		"""
		for playerID, info in self.member:
				if info["playerBase"]:
					info["playerBase"].client.onStatusMessage( statuID,"" )

	# ---------------------------------------------------------
	# �����̨
	# ---------------------------------------------------------
	def teamChallengeRequestJoin( self, playerDBID, playerName, playerLevel, playerBase, playerRaceclass, headTextureID ):
		# define method
		# �����̨��������Ӷ�Ա
		if len( self.member ) >= csconst.TEAM_MEMBER_MAX:
			BigWorld.globalData[ "TeamChallengeMgr" ].recruitRresult( playerBase, playerLevel, self.id, False )
		else:
			if playerDBID not in [ info[ 1 ][ "playerDBID" ] for info in self.member ]:
				self.join( playerDBID, playerName, playerBase, playerRaceclass, headTextureID )
				playerBase.cell.challengeActivityTransmit( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE )

			BigWorld.globalData[ "TeamChallengeMgr" ].recruitRresult( playerBase, playerLevel, self.id, True )

	def teamChallengeChampion( self, entityDBIDs, minL, maxL, rewardTime):
		# define method
		# ֪ͨ����Ϊ�����̨�ھ�
		championNameStr  = ""

		for playerID, info in self.member:
			if len( entityDBIDs ) != 0 and info[ "playerDBID" ] not in entityDBIDs:
				continue

			if championNameStr:
				championNameStr += "," + info[ "playerName" ]
			else:
				championNameStr = info[ "playerName" ]

			playerBase = info[ "playerBase" ]

			if playerBase:
				playerBase.cell.teamChallengeSetChampion( rewardTime )
				playerBase.client.onStatusMessage( csstatus.TEAM_CHALLENGE_WIN_LAST,  str( ( minL, maxL, ) )  )

		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TEAM_CHALLENGE_WIN_ALL_ROLE%( championNameStr, minL, maxL ), [] )

	def teamChallengeGather( self, round ):
		# define method
		# �����̨����
		self.teamChallengeIsGather = True
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.challengeTeamGather( round )
			playerBase.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE )

	def teamChallengeCloseGather( self ):
		# define method
		# �ر������̨�ļ���
		self.teamChallengeIsGather = False
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.cell.challengeRemoveFlagGather( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE )

	def teamChallengeSetResult( self, result ):
		# define method
		# ���ñ������
		for playerID, info in self.member:
			RoleMatchRecorder.update( info[ "playerDBID" ], csdefine.MATCH_TYPE_TEAM_ABA, result, info[ "playerBase" ] )

	def teamChallengeUpLevel( self, maxLevel, minLevel ):
		# define method
		# ���±����ȼ�
		self.teamChallengeLevel = ( maxLevel, minLevel )
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			if playerBase:
				playerBase.client.teamChallengeUpLevel( maxLevel, minLevel )

	def teamChallengeUpInfo( self, result ):
		# define method
		# ���µ�ǰ���������
		self.teamChallengeInfo = result
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			if playerBase:
				playerBase.client.teamChallengeUpInfo( result )

	def teamChallengeClose( self ):
		# define method
		# �����̨�����
		self.teamChallengeInfo = csdefine.MATCH_LEVEL_NONE
		self.teamChallengeLevel = None

	def teamChallengeOnRecruit( self ):
		# define method
		# ����������ļ
		self.teamChallengeRecruit = True
		for playerID, info in self.member:
			info[ "playerBase" ].client.teamChallengeOnRecruit()

	def teamChallengeCancelRecruit( self ):
		# define method
		# ����ȡ����ļ
		self.teamChallengeRecruit = False
		for playerID, info in self.member:
			info[ "playerBase" ].client.teamChallengeOnCRecruit()

	def teamChallengeRecruitComplete( self ):
		self.teamChallengeRecruit = False
		for playerID, info in self.member:
			info[ "playerBase" ].client.teamChallengeRecruitComplete()

	# ---------------------------------------------------------
	# ��Ӿ���
	# ---------------------------------------------------------
	def teamCompetitionNotify( self,level ):
		"""
		defined method

		��Ӿ������ʼʱ���ô˺��������²�����Ϣ��ÿ����Ա�Ŀͻ���
		@param :level  ����ȼ�
		@type :level   UNIT16
		"""
		self.teamCompetitionLevel = level
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			if playerBase:
				playerBase.client.teamCompetitionNotify( self.teamCompetitionLevel )

	def teamCompetitionGather( self ):
		# define method
		# ��Ӿ������Ͽ�ʼ
		self.teamCompetitionGatherFlag = True
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.teamCompetitionGather()
			playerBase.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TEAM_COMPETITION )

	def teamCompetitionCloseGather( self ):
		# define method

		# �ر���Ӿ����ļ���
		self.teamCompetitionGatherFlag = False
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.cell.challengeRemoveFlagGather( csconst.TRANSMIT_TYPE_TEAM_COMPETITION )

	# ----------------------------------------------------------------
	# extensions of copy matcher.
	# ----------------------------------------------------------------
	def memberDBIDOfID( self, playerID ) :
		"""
		�������ID����
		"""
		info = self._getPlayerInfoByID( playerID )
		if info :
			return info["playerDBID"]
		else :
			return None

	def memberInfoOfDBID( self, playerDBID ) :
		"""
		"""
		return self._getMemberInfoByDBID( playerDBID )[1]

	def memberNames( self ) :
		"""
		��ȡ��Ա������
		"""
		return tuple( [m[1]["playerName"] for m in self.member] )

	def memberNameOfDBID( self, playerDBID ) :
		"""
		��ȡ��DBID��Ӧ�ĳ�Ա����
		"""
		info = self.memberInfoOfDBID( playerDBID )
		if info :
			return info["playerName"]
		else :
			return ""

	def membersOnline( self ) :
		"""
		��ȡ���߳�Ա��mailbox
		"""
		return tuple( [m[1]["playerBase"] for m in self.member if m[1]["playerBase"]] )

	def memberMailboxOfDBID( self, playerDBID ) :
		"""
		��ȡ��DBID��Ӧ�ĳ�Աmailbox
		"""
		info = self.memberInfoOfDBID( playerDBID )
		if info :
			return info["playerBase"]
		else :
			return None

	def memberMailboxOfID( self, playerID ) :
		"""
		��ȡ��id��Ӧ�ĳ�Աmailbox
		"""
		info = self._getPlayerInfoByID( playerID )
		if info :
			return info["playerBase"]
		else :
			return None

	def allMembersAreOnline( self ) :
		"""
		�������г�Ա������
		"""
		return len( self.leaveDBIDs ) == 0

	def contain( self, playerDBID ) :
		"""
		���playerDBID�ǲ��Ƕ�Ա
		"""
		return self.memberInfoOfDBID( playerDBID ) is not None

	def containID( self, playerID ) :
		"""
		���playerID�ǲ��Ƕ�Ա
		"""
		return self._getPlayerInfoByID( playerID ) is not None

	# ----------------------------------------------------------------
	# Ӣ������PVP
	# ----------------------------------------------------------------
	def baoZangReqSucceed( self, teamMB ):
		"""
		define method
		Ӣ�����˸���PVPƥ��ɹ�
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.cell.baoZangReqSucceed( teamMB )

	def baoZangSetRivalTeamIDs( self, rTeamIDs, t ):
		"""
		define method.
		���ն��ֶ�����ԱID
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.cell.baoZangSetRivalTeamIDs( rTeamIDs, t )
	
	def baoZangPVPonReq( self ):
		"""
		define method.
		�������뱦��PVP
		"""
		self.baoZangPVPreqTime = time.time()
			
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.baoZangPVPonReq( self.baoZangPVPreqTime )
	
	def baoZangPVPonCancel( self, isMatch ):
		"""
		define method.
		�����˳�����PVP���Ŷ�
		"""
		self.baoZangPVPreqTime  = 0
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.baoZangPVPonCancel( isMatch )
	
	# ��ӪӢ������
	def yingXiongCampReqSucceed( self, teamMB ):
		"""
		define method
		Ӣ�����˸���PVPƥ��ɹ�
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.cell.yingXiongCampReqSucceed( teamMB )

	def yingXiongCampSetRivalTeamIDs( self, rTeamIDs, t ):
		"""
		define method.
		���ն��ֶ�����ԱID
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.cell.yingXiongCampSetRivalTeamIDs( rTeamIDs, t )
	
	def yingXiongCampOnReq( self ):
		"""
		define method.
		�������뱦��PVP
		"""
		self.yingXiongCampReqTime = time.time()
			
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.yingXiongCampOnReq( self.yingXiongCampReqTime )
	
	def yingXiongCampOnCancel( self, isMatch ):
		"""
		define method.
		�����˳�����PVP���Ŷ�
		"""
		self.yingXiongCampReqTime  = 0
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.yingXiongCampOnCancel( isMatch )
#
# $Log: not supported by cvs2svn $
# Revision 1.26  2008/03/01 00:59:43  zhangyuxing
# ���´��� onTimer�� leave���á� ͨ��DBID ֱ�ӻ��ID ȥ����
#
# Revision 1.25  2008/02/29 07:00:44  zhangyuxing
# ��leave�������棬 �����Զ�ѡ��ӳ������������⣬���޸ġ�
#
# Revision 1.24  2008/02/29 06:39:16  zhangyuxing
# �޸��� leaveDBIDs ��������ݣ� �����һ�� ���ID�� ��Ҫ�Ǵ������
#
# Revision 1.23  2008/02/28 01:06:21  zhangyuxing
# �޸���onTimer �ж� self.leave�Ĵ������
#
# Revision 1.22  2008/02/27 09:21:33  zhangyuxing
# �޸�logout�����ڲ�һ�� ���� �ӳ��Զ����� ������� BUG��
#
# Revision 1.21  2007/12/08 07:54:19  yangkai
# self.member ������{entityID �� info,...}�ĳ� [(entityID,Info),...]
# ͨ��dict([]) he {}.items() ����ת������˳����Ӷ��飬����cell��������ʰȡ��Ʒ
#
# Revision 1.20  2007/11/16 03:41:55  zhangyuxing
# ����������Team�Ľӿ�addMember�ı仯�����ڵ��øýӿ�ʱ�������
# ���ID������
# �޸�BUG����logon�ӿ��У� info�������ⲿʹ���ˣ�����ѭ�������õ�
# ���������޸���������Ϣ��������ѭ����ʹ��tempinfo�����
#
# Revision 1.19  2007/11/15 07:05:55  phw
# method modified: _notifyPlayerTeamMemberInfo(), �����˸�������ҷ��������߶�Աʱ�޷��ҵ������߶�Ա��entityID��bug
#
# Revision 1.18  2007/10/09 07:51:41  phw
# �����������������������Ż�ʵ�ַ�ʽ������������bug
#
# Revision 1.17  2007/06/19 09:26:27  kebiao
# captainID -->
# DATABASE_ID
# to:
# OBJECT_ID
#
# Revision 1.16  2007/06/14 09:25:01  huangyongwei
# һЩ�ɵ���ֵ�ĺ궨�屻�ƶ��� Const ��
#
# Revision 1.15  2007/06/14 03:06:48  panguankong
# �޸Ķ���clientֻʹ��objectID
#
# Revision 1.14  2007/04/04 09:15:36  panguankong
# �޸����������ʱ��
#
# Revision 1.13  2007/04/04 01:00:06  panguankong
# �����������ߺ���ӵĴ�������timer
#
# Revision 1.12  2007/03/01 08:14:58  panguankong
# ����˴��������ʱ���Ҳ����������BASE�����
#
# Revision 1.11  2007/01/31 04:22:57  panguankong
# ȥ����һ����ǰ֪ͨ������Ϣ�Ĵ���
#
# Revision 1.10  2007/01/29 01:37:48  panguankong
# ���ӳ�֪ͨ�ŵ���Ա��Ϣ�����Ժ�
#
# Revision 1.9  2007/01/03 07:41:30  panguankong
# �޸��˶������ӡ�������˿�������������˵���Ϣ��BUG
#
# Revision 1.8  2007/01/03 01:49:19  panguankong
# �޸��˶��鲿��BUG
#
# Revision 1.7  2006/12/29 08:32:08  huangyongwei
# �޸���֪ͨ���߳�Ա��λ��
#
# Revision 1.6  2006/12/20 08:20:54  panguankong
# �޸ġ��ӳ�ID
#
# Revision 1.5  2006/12/20 06:56:29  panguankong
# ������ߡ�������Ϣ֪ͨ
#
# Revision 1.4  2006/11/29 10:25:42  panguankong
# no message
#
# Revision 1.3  2006/11/29 09:26:01  panguankong
# no message
#
# Revision 1.2  2006/11/29 09:02:06  panguankong
# no message
#
# Revision 1.1  2006/11/29 02:05:51  panguankong
# ����˶���ϵͳ
#