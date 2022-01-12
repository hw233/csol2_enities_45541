# -*- coding: gb18030 -*-
#
# $Id: Team.py,v 1.40 2008-08-20 01:23:03 zhangyuxing Exp $

import BigWorld
import csstatus
from bwdebug import *
import csconst
import Const
import csdefine
from TeamRegulation import *
from SlaveDart import SlaveDart
from ObjectScripts.GameObjectFactory import g_objFactory
import ECBExtend
import random


class Team:
	def __init__( self ):
		self.teamMembers = []		# �����Ա��[{"dbID" : 12345, "mailbox" : MAILBOX}, ... ]
		self.captainID = 0			# �ӳ�ID
		self.teamMailbox = None		# �����MAILBOX
		self.pickUpState = csdefine.TEAM_PICKUP_STATE_FREE

		self.pickRegulation = g_pRMgr.createRegulaiton( TEAM_FREE_PICK )
		self.pickRegulation.init( self )
		self.leaveTeamTimer = 0

	# ---------------------------------------------------------------------
	# protected
	# ---------------------------------------------------------------------
	def onAddBuff( self, buff ) :
		"""
		������һ�� buff ʱ������(������ӵ� buff ���͸����ж��ѣ�
		by hyw -- 2008.09.23
		"""
		for member in self.teamMembers :
			member["mailbox"].client.team_onMemberAddBuff( self.id, buff )

	def onRemoveBuff( self, buff ) :
		"""
		ɾ��һ�� buff ʱ�����ã�����ɾ���� buff ֪ͨ�������ж��ѣ�
		by hyw -- 2008.09.23
		"""
		for member in self.teamMembers :
			member["mailbox"].client.team_onMemberRemoveBuff( self.id, buff[ "index" ] )

	def onUpdateBuff( self, index, buff ) :
		"""
		��ĳ�� buff ����ʱ�����ã����Ҹ��µ� buff �������ж��ѣ�
		by hyw -- 2008.09.23
		"""
		for member in self.teamMembers :
			member["mailbox"].client.team_onMemberUpdateBuff( self.id, index, buff )

	def onPetAddBuff( self, buff ):
		"""
		������һ�� buff ʱ������(���ҵĳ�����ӵ� buff ���͸����ж��ѣ�
		"""
		for member in self.teamMembers :
			member["mailbox"].client.team_onMemberPetAddBuff( self.id, buff )

	def onPetRemoveBuff( self, buff ):
		"""
		������һ�� buff ʱ������(���ҵĳ����Ƴ��� buff ֪ͨ���ж��ѣ�
		"""
		for member in self.teamMembers :
			member["mailbox"].client.team_onMemberPetRemoveBuff( self.id, buff )

	def onPetConjureNotifyTeam( self, id, uname, name, modelNumber, species ):
		"""
		�����ٻ�����֪ͨ����
		"""
		for member in self.teamMembers :
			member["mailbox"].client.team_onPetConjureNotify( self.id, id, uname, name, modelNumber, species )

	def onPetWithdrawNotifyTeam( self ):
		"""
		�����ջ�֪ͨ����
		"""
		for member in self.teamMembers :
			member["mailbox"].client.team_onPetWithdrawNotify( self.id )

	# ---------------------------------------------------------------------
	# public
	# ---------------------------------------------------------------------
	def teamInviteFC( self, srcEntityID, playerID ):
		"""
		exposed method.
		����������

		���̣�
		���������CELL������������

		@param playerID: ��ҵ�EntityID
		@type playerID: OBJECT_ID
		"""
		if srcEntityID != self.id:
			return

		# ��ս��������������
		if self.isInSpaceChallenge():
			if self.query( "challengeSpaceType", 0 ) == csconst.SPACE_CHALLENGE_TYPE_MANY:
				if len( self.teamMembers ) >= csconst.SPACE_CHALLENGE_TEAM_MEMBER_MAX:
					self.statusMessage( csstatus.CHALLENGE_SPACE_MANY_MEM_FULL )
					return

			elif self.query( "challengeSpaceType", 0 ) == csconst.SPACE_CHALLENGE_TYPE_SINGLE:
				self.statusMessage( csstatus.CHALLENGE_SPACE_PERSONAL_INVITE_TEAM )
				return

		objPlayer = BigWorld.entities.get( playerID )
		if objPlayer is None:
			#ERROR_MSG( "Not Find Player Entity!")
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_EXIST )		# defined in Role.py
			return

		if objPlayer.isState( csdefine.ENTITY_STATE_PENDING ):
			return

		if objPlayer.isState( csdefine.ENTITY_STATE_QUIZ_GAME ):
			return

		if objPlayer.qieCuoState != csdefine.QIECUO_NONE:
			self.statusMessage( csstatus.TARGET_IS_QIECUO )
			return
		
		if not self.getCurrentSpaceScript().isDiffCampTeam and objPlayer.getCamp() != self.getCamp():
			self.statusMessage( csstatus.TEAMATE_CAMP_DIFFERENT )
			return

		if csconst.TEAM_MEMBER_MAX <= len( self.teamMembers ):
			self.statusMessage( csstatus.TEAM_FULL )
			return

		# �����������Լ�
		if self.id == playerID:
			self.statusMessage( csstatus.TEAM_NOT_INVITE_SELF )
			return

		if objPlayer.isInTeam():
			return

		if not self.isInTeam() or self.isTeamCaptain():
			objPlayer.base.teamInviteBy( self.base, self.getName(), self.getCamp() )
		else:
			captainMB = self.getTeamCaptainMailBox()
			if captainMB:
				captainMB.client.teamInviteByTeammate( objPlayer.getName(), objPlayer.id, self.getName(), self.id )

	def requestJoinTeamNear( self, srcEntityID ):
		"""
		Exposed method.
		�Է�����Ӷ�
		"""
		if self.id == srcEntityID:
			HACK_MSG( "player( %s ) cannot join own team." % self.getName() )
			return

		if not self.isInTeam():
			return

		objPlayer = BigWorld.entities.get( srcEntityID )
		if objPlayer is None:
			return
		
		if not self.getCurrentSpaceScript().isDiffCampTeam and objPlayer.getCamp() != self.getCamp():
			objPlayer.client.onStatusMessage( csstatus.TEAMATE_CAMP_DIFFERENT, "" )
			return

		if not self.isTeamCaptain():
			captainMB = self.getTeamCaptainMailBox()
			if captainMB:
				captainMB.receiveJoinTeamRequest( objPlayer.getName(), objPlayer.raceclass, objPlayer.getLevel(), objPlayer.base )
		else:
			self.base.receiveJoinTeamRequest( objPlayer.getName(), objPlayer.raceclass, objPlayer.getLevel(), objPlayer.base )

	def acceptTeamRequestNear( self, srcEntityID, targetID ):
		"""
		Exposed method.
		���ܶԷ��ļӶ����󣬶Է����Լ���ͬһ��cellApp

		@param targetID : ����Ӷ���������id
		@type targetID : OBJECT_ID
		"""
		if srcEntityID != self.id:
			return
		if targetID == self.id:
			return
		if not self.isTeamCaptain():
			return
		try:
			targetPlayer = BigWorld.entities[targetID]
		except KeyError:
			return
		targetPlayer.base.captainAcceptTeamRequest( self.base )

	def refusePlayerJoinTeam( self, srcEntityID, targetID ):
		"""
		Exposed method.
		�ܾ��Է��ļӶ����󣬶Է����Լ���ͬһ��cellApp

		@param targetID : ����Ӷ���������id
		@type targetID : OBJECT_ID
		"""
		if srcEntityID != self.id:
			return
		if self.targetID == self.id:
			return
		if not self.isTeamCaptain():
			return
		try:
			targetPlayer = BigWorld.entities[targetID]
		except KeyError:
			return
		targetPlayer.client.onStatusMessage( csstatus.TEAM_REQUEST_FORBID, "( \'%s\', )" % self.getName() )
		self.base.addFobidTeamPlayer( targetPlayer.id )

	#---------------------------------------------------------------------------------
	def teamInviteBy( self, inviterBase, inviterName, inviterCamp ):
		"""
		define method.
		��ĳ����������
		"""
		if self.qieCuoState != csdefine.QIECUO_NONE:
			inviterBase.client.onStatusMessage( csstatus.TARGET_IS_QIECUO, "" )
			return
		
		if not self.getCurrentSpaceScript().isDiffCampTeam and inviterCamp != self.getCamp():
			inviterBase.client.onStatusMessage( csstatus.TEAMATE_CAMP_DIFFERENT, "" )
			return

		self.base.teamInvitedToBy( inviterBase, inviterName )

	def teamInviteByTeammate( self, name, target ):
		"""
		define method.
		��������Ŀ��������
		"""
		try:
			targetPlayer = BigWorld.entities[target.id]
		except KeyError:
			return
		if targetPlayer.qieCuoState != csdefine.QIECUO_NONE:
			self.client.onStatusMessage( csstatus.TARGET_IS_QIECUO, "" )
			return

		self.base.teamInviteByTeammate( name, target )

	def addTeamMember( self, dbid, playerBase ):
		"""
		define method.
		���ͳ�Ա����

		���̣�
		�����Ա�б�����ӳ�Ա

		@param dbid: player.databaseID
		@type dbid: DATABASE_ID
		@param playerBase: ���BASE
		@type playerBase: mailbox
		"""
		# ��ӳ�Ա
		self.teamMembers.append( { "dbID" : dbid, "mailbox" : playerBase } )
		for buff in self.attrBuffs :											# ���ҵ� buff �б��͸��½������ѣ�hyw--2008.09.24��
			playerBase.client.team_onMemberAddBuff( self.id, buff )
		actPet = self.pcg_getActPet()
		if actPet:
			pet = actPet.entity
			playerBase.client.addTeamMemberPet( self.id, pet.id, pet.uname, pet.name, pet.modelNumber, pet.species )
			for buff in pet.attrBuffs:		# ���Լ�����buff���͸��½����Ķ���
				playerBase.client.team_onMemberPetAddBuff( self.id, buff )
		self.cmi_onTeammateJoin( playerBase )

	def removeTeamMember( self, playerID ):
		"""
		define method.
		����뿪
		playerIDΪ�Լ�ʱ,disemployΪTrue�Լ�������,False�����ɢ

		���̣�
			�ӳ�Ա�б���ɾ����Ҽ�¼
			֪ͨcell��ָ������뿪

		@param playerID: ��ҵ�EntityID
		@type playerID: OBJECT_ID
		"""
		if playerID == self.id:
			# ��������������棬Ҫ�ж��Ƿ�Ҫ�˳����
			#spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
			#g_objFactory.getObject( spaceLabel ).onLeaveTeam( self )

			# �Լ���ӣ����ڶ����ɢ
			self.disbandTeamNotify()
		else:
			# ��Ա���
			for index, e in enumerate( self.teamMembers ):
				if e["mailbox"].id == playerID:
					self.teamMembers.pop( index )
					return



	def disbandTeamNotify( self ):
		"""
		define method.
		�����ɢ֪ͨ���˷�����self.base����
		"""
		if self.isTeamFollowing():
			self.cancelTeamFollow()
			
		spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
		g_objFactory.getObject( spaceLabel ).onLeaveTeam( self )
		self.teamInfoNotify( 0, None )
		self.teamMembers = []
		self.pft_onLeaveTeam()
		self.ei_onLevelTeam()
		self.cmi_onLeaveTeam()
		self.dt_onLeaveTeam()	# �����ֻظ���

	def teamInfoNotify( self, captainID, teamMailbox ):
		"""
		define method.
		֪ͨ������Ϣ

		@param captainID: �ӳ���ҵ�EntityID
		@type captainID: OBJECT_ID
		@param teamMailbox: ����BASE
		@type teamMailbox: mailbox
		"""
		self.teamMailbox = teamMailbox
		self.captainID = captainID
		if self.teamMailbox:
			self.addFlag( csdefine.ROLE_FLAG_TEAMMING )
		else:
			self.removeFlag( csdefine.ROLE_FLAG_TEAMMING )
		# ͨ�����ñ�ǣ�֪ͨ�ͻ������ͷ����Ƿ����仯
		if self.id == captainID:
			if not self.hasFlag( csdefine.ROLE_FLAG_CAPTAIN ) :
				self.addFlag( csdefine.ROLE_FLAG_CAPTAIN )			# ���öӳ����
		elif self.hasFlag( csdefine.ROLE_FLAG_CAPTAIN ) :
			self.removeFlag( csdefine.ROLE_FLAG_CAPTAIN )			# ȥ���ӳ����
		if self.teamMailbox:
			self.ei_joinTeam()
		else:
			self.ei_onLevelTeam()

	def changeCaptainNotify( self, captainID ):
		"""
		define method.
		�ӳ��ı�

		@param captainID: �ӳ�ID
		@type captainID: OBJECT_ID
		"""
		self.captainID = captainID
		if self.isTeamCaptain():
			self.removeFlag( csdefine.ROLE_FLAG_CAPTAIN )
			if self.isTeamFollowing():
				self.effectStateDec( csdefine.EFFECT_STATE_LEADER )		# �ӳ��ı��ԭ�ӳ��������Ч��״̬
				newCaptain = BigWorld.entities.get( captainID )
				if newCaptain is not None and newCaptain.isTeamFollowing():
					self.effectStateInc( csdefine.EFFECT_STATE_FOLLOW )
					self.actCounterInc( Const.FOLLOW_STATES_ACT_WORD )
					self.spellTarget( csconst.FOLLOW_SKILL_ID, self.id )
					return
		elif self.id == captainID:
			self.addFlag( csdefine.ROLE_FLAG_CAPTAIN )
			if self.isTeamFollowing():
				self.removeAllBuffByID( csconst.FOLLOW_BUFF_ID, [ csdefine.BUFF_INTERRUPT_ON_DIE ] )
				self.effectStateDec( csdefine.EFFECT_STATE_FOLLOW )
				self.effectStateInc( csdefine.EFFECT_STATE_LEADER )
				self.actCounterDec( Const.FOLLOW_STATES_ACT_WORD )

	#---------------------------------------------------------------------------------
	# msg request
	def requestTeammateInfo( self, objPlayerBase ):
		"""
		ȡ״̬

		���̣�
		������״̬�����

		@param objPlayerBase: ���BASE
		@type objPlayerBase: mailbox
		"""
		spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
		objPlayerBase.client.teammateInfoNotify( self.id, self.level, self.HP, self.HP_Max, self.MP, self.MP_Max, 0, spaceLabel, self.position, self.spaceID )# buff

	def requestTeammatePetInfo( self, objPlayerBase ):
		"""
		ȡ״̬

		���̣�
		������״̬�����

		@param objPlayerBase: ���BASE
		@type objPlayerBase: mailbox
		"""
		spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
		actPet = self.pcg_getActPet()
		if actPet:
			if actPet.etype == "MAILBOX":
				return
			pet = actPet.entity
			objPlayerBase.client.teammatePetInfoNotify( self.id, pet.id, pet.uname, pet.name, pet.level, pet.HP, pet.HP_Max, pet.MP, pet.MP_Max, 0, pet.modelNumber, pet.species )

	#---------------------------------------------------------------------------------
	# interface
	def teamMemberName2client( self, baseMailbox ):
		"""
		�����������ָ������Ա

		@param baseMailbox: Ŀ�����base mailbox
		@type  baseMailbox: MAILBOX
		@return:            None
		"""
		baseMailbox.client.teammateNameChange( self.id, self.playerName )

	def teamMemberLevel2client( self, baseMailbox ):
		"""
		��������ȼ��������Ա

		@param baseMailbox: Ŀ�����base mailbox
		@type  baseMailbox: MAILBOX
		@return:            None
		"""
		baseMailbox.client.teammateLevelChange( self.id, self.level )

	def isTeamCaptain( self ):
		"""
		�ж����Ƿ�ӳ���
		������������

		@return: �Ƕӳ��򷵻�True�����򷵻�False��δ���������Ϊ�Ƕӳ�
		@rtype:  BOOL
		"""
		return self.hasFlag( csdefine.ROLE_FLAG_CAPTAIN )

	def getTeamCount( self ):
		"""
		ȡ�ö����Ա����

		@return: �����Ա����
		@rtype:  UINT8
		"""
		return len( self.teamMembers )

	def getAllMemberInRange( self, range, position = None ):
		"""
		�ж��Ƿ����еĶ�Ա����ͬһ��Χ��

		@param    range: ��Χ(�뾶)
		@type     range: FLOAT
		@param position: λ�����ĵ㣬��λ�úͰ뾶����ϳ��ķ�Χ���ܳ�����ҵ�AOI����������һ������ȷ�ģ�
		                 �����ֵΪNone���ʾ���Լ�Ϊ���ġ�
		@type  position: VECTOR3
		@return:         ͬһ��Χ�����ж����Ա�б����û�ж����򷵻�һ�����б�
		@rtype:          ARRAY of Entity
		"""
		if len( self.teamMembers ) == 0:
			return []

		if position is None:
			position = self.position
		members = []
		for e in self.teamMembers:
			entityID = e["mailbox"].id
			entity = BigWorld.entities.get( entityID )
			if not entity or entity.spaceID != self.spaceID:
				continue
			if entity.position.flatDistTo( position ) <= range:
				members.append( entity )
		return members

	def getAllIDNotInRange( self, range, position = None ):
		"""
		���ز���ͬһ����Χ�ڳ�Ա��id
		"""
		teamMemberIDs = self.getTeamMemberIDs()
		allMemberInRange = self.getAllMemberInRange( range, position )

		for member in allMemberInRange:
			teamMemberIDs.remove( member.id )

		return teamMemberIDs

	def allMemberIsInRange( self, range, position = None ):
		"""
		�ж��Ƿ����еĶ�Ա����ͬһ��Χ��

		@param    range: ��Χ(�뾶)
		@type     range: FLOAT
		@param position: λ�����ĵ㣬��λ�úͰ뾶����ϳ��ķ�Χ���ܳ�����ҵ�AOI����������һ������ȷ�ģ�
		                 �����ֵΪNone���ʾ���Լ�Ϊ���ġ�
		@type  position: VECTOR3
		@return:         �ж��������ж�Ա��ͬһ��Χ���򷵻�True�����򷵻�False
		@rtype:          BOOL
		"""
		return len( self.getAllMemberInRange(range, position) ) == self.getTeamCount()

	def getTeamCaptain( self ):
		"""
		ȡ�öӳ���entity

		@return: ����Ѿ�������ڱ������ߵ�ǰ���ڵ�cellApp���ҵ��˶ӳ���entity�򷵻ضӳ���Entityʵ�������򷵻�None
		@rtype:  Entity/None
		"""
		return BigWorld.entities.get( self.captainID )

	def getTeamCaptainDBID( self ):
		"""
		ȡ�öӳ���dbid
		@return: DATABASE_ID
		"""
		for e in self.teamMembers:
			if e["mailbox"].id == self.captainID:
				return e["dbID"]
		return 0L

	def getTeamCaptainMailBox( self ):
		"""
		"""
		for e in self.teamMembers:
			if e["mailbox"].id == self.captainID:
				return e["mailbox"]

		return None


	def getTeamMemberDBIDs( self ):
		"""
		��ȡ���������˵�dbid
		@return: ARRAY of DATABASE_ID
		"""
		return [ e["dbID"] for e in self.teamMembers ]

	def getTeamMemberIDs( self ):
		"""
		��ȡ���������˵�id
		@return: ARRAY of OBJECT_ID
		"""
		return [ e["mailbox"].id for e in self.teamMembers ]

	def getTeamMemberMailboxs( self ):
		"""
		��ȡ���������˵�mailbox
		@return: ARRAY of MAILBOX
		"""
		return [ e["mailbox"] for e in self.teamMembers ]

	def getTeamMailbox( self ) :
		"""
		��ȡ���ڶ���( hyw )
		"""
		return self.teamMailbox

	def isInTeam( self ):
		"""
		�ж��Լ��Ƿ��ڶ�����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.hasFlag( csdefine.ROLE_FLAG_TEAMMING )

	def isCaptain( self ):
		"""
		�ǲ��Ƕӳ�
		"""
		return self.captainID == self.id

	def isTeamMember( self, entity ):
		"""
		�ж�һ��entity�Ƿ�Ϊ�ҵĶ���
		"""
		return self.teamMailbox != None and entity.teamMailbox != None and entity.teamMailbox.id == self.teamMailbox.id

	def getTeamMemberJoinOrder( self, entityID ):
		"""
		��ȡ���Ѽ���˳��
		"""
		for index, e in enumerate( self.teamMembers ):
			if e["mailbox"].id == entityID:
				return index
		return None

	def changePickUpStateNotify( self, state ):
		"""
		define method.
		������Ʒʰȡ��ʽ֪ͨ

		@param state: ���ĵ�ʰȡ��ʽ define in csdefine.py
		@type state: INT8
		"""
		self.pickUpState = state
		if self.pickUpState == csdefine.TEAM_PICKUP_STATE_ORDER:
			self.rollState = True
		self.pickRegulation = g_pRMgr.createRegulaiton( state )

	def onChangeLastPickerNotify( self, teamMembers, entityID ):
		"""
		֪ͨ��Χ�ڵ�����entity�����һ��ʰȡ�����Ըı�
		"""
		for e in teamMembers:
			e.onChangePickUpOrder( entityID )

	def onChangePickUpOrder( self, entityID ):
		"""
		Define Method
		���¶������һ��ʰȡ�ߵ�ID��
		�˷������������еĶ����Ա������ã��ڹ��������󣬹���һ����Χ�ڵĶ���
		��Ա������ô˷����������ڷ�Χ�ڵĶ����Ա�ǲ�����ô˷�����
		@param entityID: �����ԱID
		@type entityID: entityID
		"""
		self.lastPickUpID = entityID

	def getFreePickerIDs( self ):
		"""
		��ȡ����ʰȡ��ʽ��ӵ����
		"""
		return self.getTeamMemberIDs()

	def getOrderPickerID( self, teamMembers ):
		"""
		��ȡ˳��ʰȡ��ʽ��ӵ����
		��ȡ��Χ�ڶ���˳��ʰȡ��ID
		"""
		nextIndex = None
		for index, e in enumerate( self.teamMembers ):
			if e["mailbox"].id == self.lastPickUpID:
				nextIndex = index + 1
				if nextIndex >= len( self.teamMembers ):
					nextIndex = 0
				break
		# �����¼��ID���ڶ����������������ʼ˳��Ϊ�ӳ�
		if nextIndex is None:
			return self.captainID
		newTeamMembers = self.teamMembers[nextIndex:] + self.teamMembers[:nextIndex]
		for e in newTeamMembers:
			entityID = e["mailbox"].id
			entity = BigWorld.entities.get( entityID )
			if entity is None: continue
			if entity not in teamMembers: continue
			return entityID

		# һ�㲻��ִ�е�������ִ�е������ôʰȡ��Ϊ����
		return self.id

	def statusTeamMessage( self, *args ) :
		"""
		"""
		teammates = self.getAllMemberInRange( csconst.ROLE_AOI_RADIUS )	# ֻ���Լ�AOI��Χ�ڵ���ҷ�����Ϣ
		for entity in teammates:
			if entity.isReal():
				entity.statusMessage( *args )
			else:
				entity.remoteCall( "statusMessage", args )

	def team_notifyKillMessage( self, victim ) :
		"""
		֪ͨ�����������victim����ɱ��
		@param		victim : ��ɱ��
		@type		cictim : entity
		"""
		teammates = self.getAllMemberInRange( csconst.ROLE_AOI_RADIUS )	# ֻ���Լ�AOI��Χ�ڵ���ҷ�����Ϣ
		for entity in teammates :
			if entity.id == self.id : continue					# �����Լ�����
			if entity.id == victim.id : continue				# �����ܺ��߷���
			if entity.isReal() :
				if victim.isEntityType( csdefine.ENTITY_TYPE_ROLE ):	# ��������������
					entity.statusMessage( csstatus.ROLE_STATE_KILL_DEAD_BY_TEAMMATE, victim.getName(), self.getName() )
				else:
					entity.statusMessage( csstatus.ACCOUNT_STATE_KILL_BY, victim.getName(), self.getName() )
			else:
				if victim.isEntityType( csdefine.ENTITY_TYPE_ROLE ):	# ��������������
					entity.remoteCall( "statusMessage", ( csstatus.ROLE_STATE_KILL_DEAD_BY_TEAMMATE, victim.getName(), self.getName() ) )
				else:
					entity.remoteCall( "statusMessage", ( csstatus.ACCOUNT_STATE_KILL_BY, victim.getName(), self.getName() ) )

	def team_notifyKilledMessage( self, killer ) :
		"""
		֪ͨ��������ˣ��ұ�killerɱ��
		@param		killer : killer entity
		"""
		if not self.isInTeam() : return
		statusMsgID = 0
		msgParam = ""
		if killer is None :
			msgParam = "(\'%s\',)" % self.getName()
			statusMsgID = csstatus.ACCOUNT_STATE_DEAD
		else :
			msgParam = "(\'%s\',\'%s\')" % ( self.getName(), killer.getName() )
			if killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ) :
				statusMsgID = csstatus.ROLE_BE_KILLED_BY_ROLE
			else :
				statusMsgID = csstatus.ROLE_BE_KILLED_BY_MONSTER

		for tmDict in self.teamMembers :
			if tmDict["dbID"] == self.databaseID : continue		# �����Լ�����
			tmMailbox = tmDict["mailbox"]
			if tmMailbox is None or ( killer is not None and tmMailbox.id == killer.id ): continue				# ����ɱ�ַ���
			if hasattr( tmMailbox, "client" ) :
				tmMailbox.client.onStatusMessage( statusMsgID, msgParam )

	def setTeamPickRegulationVal1( self, val ):
		"""
		"""
		self.pickRegulation.val1 = val


	def setTeamPickRegulationVal2( self, val ):
		"""
		"""
		self.pickRegulation.val2 = val


	def selectTeamPickRegulation( self, srcEntityID, pType ):
		"""
		exposed method

		ѡ�����ʰȡ����
		"""
		if srcEntityID != self.id:
			return
		if not self.isInTeam():
			return
		if not self.isTeamCaptain():
			return

		self.teamMailbox.selectTeamPickRegulation( pType )


	def addTeamMembersTasksItem( self, id, className ):
		"""
		define method
		���������Ա������Ʒ����
		"""
		if not self.isInTeam():
			return
		membersID = []
		for member in self.getAllMemberInRange( DISTANCE_ATTENTION ):
			membersID.append( member.id )
  			entity = BigWorld.entities.get(member.id, None)
  			if entity is not None:
				entity.addTasksItem( id, className )
		entity = BigWorld.entities.get( id, None )
		if entity is not None:
			entity.addTeamMembersID( membersID )


	def buildBoxOwners( self, id, itemBox ):
		"""
		define method
		������Ʒ�Ͷ�Ӧ�������߹�ϵ
		"""
		self.pickRegulation.setItemsOwners( id, self, itemBox )


	def changePickUpQualityNotify( self, val ):
		"""
		define method
		�޸�ʰȡ�����е�Ʒ���޶�
		"""
		self.pickRegulation.val2 = val
		self.client.changePickUpQuality( val )


	def changeRollQualityNotify( self, val ):
		"""
		define method
		�޸�Rollʰȡ�����е�Ʒ���޶�
		"""
		self.pickRegulation.val2 = val
		self.client.changeRollQuality( val )

	# -----------------------------------------------------------------------------------------
	# ��Ӹ��棬13:50 2009-3-13��wsf
	# -----------------------------------------------------------------------------------------
	def leadTeam( self, srcEntityID ):
		"""
		Exposed method.
		�ӳ�������Ӹ��档
		"""
		if not self.hackVerify_( srcEntityID ):
			return

		if not self.isTeamCaptain():
			HACK_MSG( "--->>>Player( %s ) isn't captain!" % self.getName() )
			return

		if not self.isTeamFollowing():
			self.effectStateInc( csdefine.EFFECT_STATE_LEADER )
			#self.spellTarget( csconst.FOLLOW_SKILL_ID, self.id )
			self.getTeamMailbox().startFollow()

		for entity in self.entitiesInRangeExt( csconst.TEAM_FOLLOW_DISTANCE, "Role", self.position ):
			if entity.captainID == self.id and entity.spaceID == self.spaceID and not entity.isTeamFollowing():
				if entity.vehicle and entity.vehicle.__class__ == SlaveDart:
					continue

				entity.client.team_requestFollow()



	def team_replyForFollowRequest( self, srcEntityID, reply ):
		"""
		Exposed method.
		��Ӹ���Ļظ�

		@param reply : True or False
		"""
		if not self.hackVerify_( srcEntityID ):
			return

		captainEntity = self.getTeamCaptain()
		if captainEntity is None or self.id == self.captainID:
			return
		if not captainEntity.isLeadTeam():
			return
		if self._isVend():
			reply = False
			self.statusMessage( csstatus.TEAM_FOLLOW_CANT_VEND )
		elif self.effect_state & csdefine.EFFECT_STATE_SLEEP:
			reply = False
			self.statusMessage( csstatus.TEAM_FOLLOW_CANT_SLEEP )
		elif self.effect_state & csdefine.EFFECT_STATE_VERTIGO:
			reply = False
			self.statusMessage( csstatus.TEAM_FOLLOW_CANT_VERTIGO )
		elif self.effect_state & csdefine.EFFECT_STATE_FIX:
			reply = False
			self.statusMessage( csstatus.TEAM_FOLLOW_CANT_FIX )
		elif self.position.distTo( captainEntity.position ) > csconst.TEAM_FOLLOW_DISTANCE:	# �п��ܶӳ���ʱ�Ѿ�Զȥ
			reply = False

		if not reply:
			self.teamStatusMessage( captainEntity, csstatus.TEAMATE_FOLLOW_REPLY_FALSE, self.getName() )
			return

		entity = BigWorld.entities.get( srcEntityID, None)
		if entity and entity.vehicle and entity.vehicle.__class__ == SlaveDart:
			return

		self.effectStateInc( csdefine.EFFECT_STATE_FOLLOW )
		self.actCounterInc( Const.FOLLOW_STATES_ACT_WORD )
		self.spellTarget( csconst.FOLLOW_SKILL_ID, self.id )
		self.getTeamMailbox().followCaptain( self.id )
		self.teamStatusMessage( captainEntity, csstatus.TEAMATE_FOLLOW_SUCCESS, self.getName() )

	def teamStatusMessage( self, targetBase, statusID, *args ):
		"""
		����ϵͳ��Ϣ��ʾ
		"""
		args = args == () and "" or str( args )
		targetBase.client.onStatusMessage( statusID, args )

	def team_cancelFollow( self, srcEntityID ):
		"""
		Exposed method.
		����˳�����
		"""
		if not self.isInTeam():
			return
		if not self.hackVerify_( srcEntityID ):
			return
		if self.isTeamCaptain():
			return
		if not self.isTeamFollowing():
			return

		self.cancelTeamFollow()
		self.getTeamMailbox().cancelFollow( self.id )	# �����˳���֪ͨTeamEntity

	def cancelTeamFollow( self ):
		"""
		Define method.
		�˳���Ӹ���
		"""
		if not self.isTeamFollowing():
			self.removeAllBuffByID( csconst.FOLLOW_BUFF_ID, [ csdefine.BUFF_INTERRUPT_ON_DIE ] )
			return
		if self.isTeamCaptain():
			self.effectStateDec( csdefine.EFFECT_STATE_LEADER )
		else:
			self.actCounterDec( Const.FOLLOW_STATES_ACT_WORD )
			self.effectStateDec( csdefine.EFFECT_STATE_FOLLOW )
		self.removeAllBuffByID( csconst.FOLLOW_BUFF_ID, [ csdefine.BUFF_INTERRUPT_ON_DIE ] )

	def isTeamFollowing( self ):
		"""
		�Ƿ�����Ӹ�����
		"""
		return csdefine.EFFECT_STATE_FOLLOW & self.effect_state or csdefine.EFFECT_STATE_LEADER & self.effect_state

	def isFollowing( self ):
		"""
		�Ƿ��ڸ���״̬�����Զ�Ա���ԣ�
		"""
		return self.effect_state & csdefine.EFFECT_STATE_FOLLOW

	def isLeadTeam( self ):
		"""
		�Ƿ�����������
		"""
		return csdefine.EFFECT_STATE_LEADER & self.effect_state

	def captainStopFollow( self, srcEntityID ):
		"""
		Exposed method.

		�ӳ�ֹͣ�˸��棬13:50 2009-3-13��wsf
		"""
		if not self.hackVerify_( srcEntityID ):
			return

		if not self.isTeamCaptain():
			return

		self.effectStateDec( csdefine.EFFECT_STATE_LEADER )
		self.removeAllBuffByID( csconst.FOLLOW_BUFF_ID, [ csdefine.BUFF_INTERRUPT_ON_DIE ] )
		self.getTeamMailbox().stopFollow()

	def effectStateChanged( self, effectState, disabled ):
		"""
		Ч���ı�.13:58 2009-3-13��wsf
			@param effectState		:	Ч����ʶ(�����)
			@type effectState		:	integer
			@param disabled		:	Ч���Ƿ���Ч
			@param disabled		:	bool
		"""
		if not disabled:
			return
		if self.isTeamCaptain():	# ��Ӱ��ӳ�
			return
		if not self.isTeamFollowing():
			return
		if not effectState in Const.TEAM_FOLLOW_EFFECT_LIST:
			return

		self.cancelTeamFollow()
		self.getTeamMailbox().cancelFollow( self.id )  # ֪ͨTeamEntity������˸����������

	def onStateChanged( self, old, new ):
		"""
		״̬�л�
		"""
		if self.isTeamCaptain():	# ��Ӱ��ӳ�
			return
		if not self.isTeamFollowing():
			return

		if new == csdefine.ENTITY_STATE_DEAD:	# ������������˳���Ӹ���
			self.cancelTeamFollow()
			self.getTeamMailbox().cancelFollow( self.id )  # ֪ͨTeamEntity������˸����������

	def beforeEnterSpaceDoor( self, destPosition, destDirection ):
		"""
		��������֮ǰ��������
		"""
		if not self.isTeamFollowing():
			return
		if not self.isTeamCaptain():
			return

		for entity in self.entitiesInRangeExt( Const.TEAM_FOLLOW_TRANSPORT_DISTANCE, "Role", self.position ):
			if entity.captainID == self.id and entity.isTeamFollowing():
				entity.followCaptainTransport()

	def npcTeamFollowTransport( self, talkFunc ):
		"""
		��Ӹ��洫��

		@param talkFunc : ���ͶԻ�����ʵ��
		"""
		for entity in self.entitiesInRangeExt( Const.TEAM_FOLLOW_TRANSPORT_DISTANCE, "Role", self.position ):
			if entity.captainID == self.id and entity.isTeamFollowing() and entity.isReal() and entity.spaceID == self.spaceID:	# �����ghost�����ܴ���
				talkFunc.do( entity )

	def followCaptainTransport( self ):
		"""
		Define method.
		�ӳ��������ţ���Ա���洫��
		"""
		if not self.isTeamFollowing():
			return

		self.addTimer( 0.5, 0, ECBExtend.TEAM_FOLLOW_TRANSPORT )

	def team_followTransportCB( self, controllerID, userData ):
		"""
		��Ӵ���timer�ص�
		"""
		if BigWorld.entities.has_key( self.captainID ):
			captainEntity = BigWorld.entities[ self.captainID ]
			self.teleport( captainEntity, captainEntity.position + ( random.randint( -2, 2 ), 0, random.randint( -2, 2 ) ), captainEntity.direction )
		else:
			captainMB = self.getTeamCaptainMailBox()
			if captainMB:
				captainMB.cell.requestCaptainPosition( self )

	def requestCaptainPosition( self, cellMailbox ):
		"""
		Define method.
		�����Ÿ��洫�ͣ�����ӳ���λ��
		"""
		cellMailbox.receiveCaptainPosition( self, self.position )

	def receiveCaptainPosition( self, cellMailbox, position ):
		"""
		Define method.
		��Ӹ�����նӳ���λ����Ϣ
		"""
		self.teleport( cellMailbox, position, ( 0, 0, 0 ) )

	def onLeaveTeamTimer( self, timerID, cbID ):
		"""
		�����뿪���飬��Ҫִ���˳��ռ������
		"""
		newTime = self.queryTemp( 'leaveSpaceTime', 0 ) - 5
		if newTime <= 0:
			spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
			g_objFactory.getObject( spaceLabel ).onLeaveTeamProcess( self )
			self.removeTemp( 'leaveSpaceTime')
		else:
			self.setTemp( 'leaveSpaceTime', newTime )
			self.leaveTeamTimer = self.addTimer( 5, 0, ECBExtend.LEAVE_TEAM_TIMER )
			if not self.isInTeam():
				pass

	def backToLastSpace( self, srcEntityID ):
		"""
		exposed method
		����ֶ�ȷ����Ҫ�˳��ռ�
		"""
		if srcEntityID != self.id:
			return
		spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
		g_objFactory.getObject( spaceLabel ).onLeaveTeamProcess( self )

#
# $Log: not supported by cvs2svn $
# Revision 1.39  2008/08/13 09:08:21  huangdong
# �����˶ӳ��������ж�Ա����Ĺ���
#
# Revision 1.38  2008/08/09 10:04:09  huangdong
# ��������������ģ��
#
# Revision 1.37  2008/05/12 05:12:20  zhangyuxing
# ���������Ϣ֪ͨ
#
# Revision 1.36  2008/03/15 09:22:19  yangkai
# ����������Ϣ֪ͨ����
#
# Revision 1.35  2008/03/14 08:49:34  yangkai
# �����������ʰȡ��Bug
#
# Revision 1.34  2008/03/14 00:58:47  yangkai
# ������˳��ʰȡ�ķ�ʽ
#
# Revision 1.33  2008/02/29 02:05:42  zhangyuxing
# ��client�˷��͵� ��Ա��Ϣ�� spaceID ��Ϊ�� spaceLabel.��Ҫ��client
# ������ͨ��spaceID���Զ������ҵĿռ�λ��
#
# Revision 1.32  2008/02/01 04:11:51  wangshufeng
# �����ѷ���������Ϣʱ�����뷢�͵ȼ�����
#
# Revision 1.31  2007/12/11 10:31:44  huangyongwei
# ����� getTeamMailbox ����
#
# Revision 1.30  2007/12/08 08:18:34  yangkai
# ��Ա����ʱ������Ʒʰȡ������ӳ�һ��
#
# Revision 1.29  2007/12/08 07:56:37  yangkai
# ���:
# ������䷽ʽ���ýӿ�
# �������˳����Ƚӿ�
#
# Revision 1.28  2007/11/16 03:51:09  zhangyuxing
# �ӿڸ��ģ�client.onStatusMessage  to  statusMessage
# �޸�BUG����teamInviteFC��������У���
# ��if self.captainID != self.id :����Ϊ
# ��if self.captainID != self.id and self.captainID != 0:��
# ��˼��˵�����û�����״̬ʱҲ���������������
#
# Revision 1.27  2007/10/09 07:51:55  phw
# �����������������������Ż�ʵ�ַ�ʽ������������bug
#
# Revision 1.26  2007/10/07 07:23:09  phw
# method added:
# 	getTeamMemberDBIDs()
# 	getTeamMemberMailboxs()
# 	getTeamCaptainDBID()
#
# method modified:
# 	getAllMemberInRange()
# 	addTeamMember()
# 	teamMembers�������͸ı䣬�޸���ش���
#
# Revision 1.25  2007/07/26 03:32:09  phw
# ȥ���ˡ�if hasattr( self, "client" )����ش���
#
# Revision 1.24  2007/07/23 05:57:44  phw
# method added: isTeamMember()
#
# Revision 1.23  2007/06/19 09:28:03  kebiao
# �������޷���ȡ�ӳ�entity��BUG
#
# Revision 1.22  2007/06/19 08:33:27  huangyongwei
# self.client.teamNotify( csstatus.TEAM_PLAYER_NOT_EXIST )
#
# --->
# self.statusMessage( csstatus.TEAM_PLAYER_NOT_EXIST )
#
# Revision 1.21  2007/06/14 09:29:16  huangyongwei
# TEAM_PLAYER_NOT_EXIST �Ķ��屻�ƶ��� csstatus ��
#
# Revision 1.20  2007/06/14 09:20:34  panguankong
# ��Ӳ��ֱ�����˵����Ϣ
#
# Revision 1.19  2007/06/14 03:07:29  panguankong
# ���ע��
#
# Revision 1.18  2007/04/02 02:51:46  yangkai
# ���������Ա�뿪���AOIʱ���ͼ����ʾͼ���BUG
#
# Revision 1.17  2007/01/17 09:06:09  phw
# method modified: getAllMemberInRange(), �Ż��˶��Ѳ��ҷ�ʽ
# method removed:
#     getTeamTask()
#     setTeamTaskFB()
#
# Revision 1.16  2006/11/29 09:01:58  panguankong
# no message
#
# Revision 1.15  2006/11/29 08:18:03  panguankong
# �޸���Ϣ
#
# Revision 1.14  2006/11/29 03:38:28  panguankong
# �޸ĸ��˳�����λ��
#
# Revision 1.13  2006/11/29 02:06:30  panguankong
# ����˶���ϵͳ
#
