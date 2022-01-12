# -*- coding: gb18030 -*-
#
# $Id: Team.py,v 1.44 2008-08-07 07:10:40 phw Exp $

import time
import BigWorld
from bwdebug import *
import csdefine
import csstatus
import csconst
import ECBExtend

TEAM_INVITE_TIME_OUT = 30
CLEAR_FOBID_TEAM_TEIM = 300


class Functor:
	def __init__( self, fn, *args ):
		self._fn = fn
		self._args = args

	def __call__( self, *args ):
		self._fn( *( self._args + args ) )

class Team:
	def __init__( self ):
		#self.teamID				# ��¼�Լ������Ķ���ID�������������ʱ�����һض���
		self.captainID = 0			# �ӳ�ID
		self.teamMailBox = None		# ����mailbox
		self._teamMembers = {}		# �����Ա�б�{ playerDBID : playerBaseMailbox, ... }
		self._teamMembersID = {}	# �����Ա�б��ӣ�{ playerDBID : playerID, ... }
		self.pickUpState = csdefine.TEAM_PICKUP_STATE_ORDER

		#self.headTextureID = 0		# �������ߵ�ͷ��ID				���������Role.def�ж��壬����Ҫ������ӿ�����д

		self._inviteTeamTime = 0.0	# �������ʱ��
		self._inviterBase = None	# �����ߵ�BASE MAILBOX�����ڼ�¼��ǰ���Ǳ�˭����������

		self.clearFobidTeamTimerID = 0	# ����ܾ����������ݵ�timerID
		self.refuseTeamPlayerDict = {}		# ���ܾ��Ӷӵ�������ݣ����磺{ ���id:�ܾ�ʱ��, ... }

	def getTeamMailbox(self):
		"""
		ȡ����MailBox
		"""
		return self.teamMailBox

	def getTeamMemberDBID( self, entityID ):
		"""
		���ݶ�Ա��entityID��ȡ���Ӧ��dbid

		@return: databaseID
		"""
		for dbid, id in self._teamMembersID.iteritems():
			if id == entityID:
				return dbid
		return 0

	def getTeamMemberMailbox( self, entityID ):
		"""
		ͨ����ҵ�entity ID��ȡ��Ӧ��mailbox
		"""
		for e in self._teamMembers.itervalues():
			if e == None:
				continue
			if entityID == e.id:
				return e
		return None

	def isInTeam( self ):
		"""
		�ж�����Ƿ����ڶ�����
		"""
		# ʹ��teamID���ж϶�����ʹ��teamMailBox�����ֻ��teamID�Ż���������ߵ�ʱ��洢
		return self.teamID != 0

	def isCaptain( self ):
		"""
		�ǲ��Ƕӳ�
		"""
		return self.captainID == self.id

	def isTeamFull( self ):
		"""
		�Ƿ������Ա
		"""
		return self.teammateAmount() >= csconst.TEAM_MEMBER_MAX

	def teammateAmount( self ) :
		"""
		��Ա����
		"""
		return len( self._teamMembers )

	def teamInviteBy( self, inviterBase, inviterName, inviterCamp ):
		"""
		define method.
		��ĳ���������ӣ�������������ӵ�������ڣ������ǽ������뻹��Զ�����롣

		@param inviterBase: ������BASE
		@type inviterBase: mailbox
		@param inviterName: ����������
		@type inviterName: string
		"""
		if not inviterBase:
			ERROR_MSG("invite player base is none.")
			return

		# ����Ѿ����
		if self.isInTeam():
			inviterBase.client.onStatusMessage( csstatus.TEAM_PLAYER_IN_TEAM, "" )
			return

		# �Ѿ�������������룬��û������ʱЧ
		if self._inviterBase and time.time() - self._inviteTeamTime < TEAM_INVITE_TIME_OUT:
			inviterBase.client.onStatusMessage( csstatus.TEAM_PLAYER_IN_TEAM_INVITE, "" )
			return

		self.cell.teamInviteBy( inviterBase, inviterName, inviterCamp )

	def teamInvitedToBy( self, inviterBase, inviterName ):
		"""
		define method.
		��ĳ����������
		"""
		# ��¼�����߼�����ʱ�䣬�Ա�������������������
		
		self._inviterBase = inviterBase
		self._inviteTeamTime = time.time()

		self.client.teamInviteBy( inviterName )
		#�����������ҷ�����Ϣ
		targetName = self.getName()
		inviterBase.client.onStatusMessage( csstatus.TEAM_INVITE_PLAYER, "(\'%s\',)" % targetName )

	def teamRemoteInviteFC( self, playerName ):
		"""
		exposed method.
		����Զ���������

		@param playerName	: �������
		@type playerName	: string
		"""
		if self.getName() == playerName:
			self.statusMessage( csstatus.TEAM_NOT_INVITE_SELF )
			return
		if self.isInTeam():
			if self.isTeamFull() :
				self.statusMessage( csstatus.TEAM_FULL )
				return

		BigWorld.lookUpBaseByName( "Role", playerName, Functor( self.teamFindPlayerCallback, playerName ) )

	def teamFindPlayerCallback( self, name, target ):
		"""
		�ҵ�Ŀ���������ߣ�target == BASE MAILBOX;
		�ҵ�Ŀ�굫δ���ߣ�target == True;
		����ԭ�����޴˽�ɫ�ȣ���target == False;

		@param name: �������
		@type name: string
		@param target:Ŀ��ʵ��Base
		@type target: mailbox
		"""
		if not isinstance( target, bool ):
			if self.isInTeam():
				if self.isCaptain():
					target.teamInviteBy( self, self.playerName, self.getCamp() )
				else:
					self.cell.teamInviteByTeammate( name, target )
			else:
				target.teamRequestRemote( self, self.getName(), self.level, self.raceclass,self.isInTeam() )
		elif target:# target offline
			#ERROR_MSG( "player offline! Name:", name )
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_EXIST )
		else:	# target not in database
			#ERROR_MSG( "not find player! Name:", name )
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_EXIST )

	def teamInviteByTeammate( self, name, target ):
		"""
		Define method.
		��������Ŀ��������
		"""
		captianMB = self.getTeamMemberMailbox( self.captainID )
		if captianMB:
			captianMB.client.teamInviteByTeammate( name, target.id, self.getName(), self.id )

	def teamRequestRemote( self, inviterMailbox, inviterName, inviterLevel, inviterRaceclass, isInTeam ):
		"""
		Define method.
		Զ���������

		@param inviterMailbox : �����ߵ�mailbox
		@type inviterMailbox : MAILBOX
		@param inviterName : �����ߵ�����
		@type inviterName : STRING
		@param isInTeam : �������Ƿ����ж���
		@type isInTeam : BOOL
		"""
		if self.isInTeam():
			if self.isTeamFull():
				inviterMailbox.client.onStatusMessage( csstatus.TEAM_FULL_REFUSE_JOIN, "" )
				return	
			if isInTeam:							
				inviterMailbox.client.onStatusMessage( csstatus.TEAM_PLAYER_IN_TEAM, "" )
				return
			if self.isCaptain():
				self.client.receiveJoinTeamRequest( inviterName, inviterRaceclass, inviterLevel, inviterMailbox.id )
				inviterMailbox.client.onStatusMessage( csstatus.TEAM_REQUEST_HAD_BEEN_SEND, "" )
			else:
				captianMB = self.getTeamMemberMailbox( self.captainID )
				if captianMB:
					captianMB.client.receiveJoinTeamRequest( inviterName, inviterRaceclass, inviterLevel, inviterMailbox.id )
		else:
			inviterCamp = ( inviterRaceclass & csdefine.RCMASK_CAMP ) >> 20
			self.teamInviteBy( inviterMailbox, inviterName, inviterCamp )

	def receiveJoinTeamRequest( self, playerName, raceclass, level, playerBase ):
		"""
		Define method.
		�ӳ��յ��Ӷ�����
		"""
		
		if playerBase.id in self.refuseTeamPlayerDict:
			playerBase.client.onStatusMessage( csstatus.TEAM_REQUEST_FORBID, "( \'%s\', )" % self.getName() )
			return
			
		if self.isTeamFull():
			# ֪ͨ�����ߣ�������Ķ����������޷�����
			playerBase.client.onStatusMessage( csstatus.TEAM_FULL_REFUSE_JOIN, "" )
			return
		playerBase.client.onStatusMessage( csstatus.TEAM_REQUEST_HAD_BEEN_SEND, "" )	
		self.client.receiveJoinTeamRequest( playerName, raceclass, level, playerBase.id )

	def refusePlayerJoinTeam( self, playerName ):
		"""
		Exposed method.
		�ܾ���ҵļӶ�����

		@param playerID : ���ܾ���ҵ�playerName
		@type playerID : STRING
		"""
		if not self.isCaptain():
			return
		BigWorld.lookUpBaseByName( "Role", playerName, self.lookUpRefuseTeamPlayerCB )

	def lookUpRefuseTeamPlayerCB( self, playerBase ):
		"""
		ͨ�����ֲ��ұ��ܾ����������ֵĻص�
		"""
		if isinstance( playerBase, bool ):
			return
		playerBase.client.onStatusMessage( csstatus.TEAM_REQUEST_FORBID, "( \'%s\', )" % self.getName() )
		self.addFobidTeamPlayer( playerBase.id )

	def addFobidTeamPlayer( self, playerID ):
		"""
		Define method.
		���ӱ��ܾ��������
		"""
		self.refuseTeamPlayerDict[playerID] = time.time()
		if not self.clearFobidTeamTimerID:
			self.clearFobidTeamTimerID = self.addTimer( CLEAR_FOBID_TEAM_TEIM, CLEAR_FOBID_TEAM_TEIM, ECBExtend.TEAM_CLEAR_REFUSE_PLAYER_CBID )

	def onTemer_clearFobidTeamPlayer( self, timerID, userData ):
		"""
		�����ܾ��Ӷ����timer�ص�
		"""
		for playerID, refuseTime in self.refuseTeamPlayerDict.items():
			if refuseTime + CLEAR_FOBID_TEAM_TEIM > time.time():
				del self.refuseTeamPlayerDict[playerID]

		if len( self.refuseTeamPlayerDict ) == 0:
			self.delTimer( self.clearFobidTeamTimerID )
			self.clearFobidTeamTimerID = 0

	def captainAcceptTeamNear( self, captainBase, captainName ):
		"""
		Define method.
		�ӳ������˼Ӷ�����
		"""
		# ����Ѿ����
		if self.isInTeam():
			captainBase.client.onStatusMessage( csstatus.TEAM_PLAYER_IN_TEAM, "" )
			return

		# �Ѿ�������������룬��û������ʱЧ
		if self._inviterBase and time.time() - self._inviteTeamTime < TEAM_INVITE_TIME_OUT:
			captainBase.client.onStatusMessage( csstatus.TEAM_PLAYER_IN_TEAM_INVITE, "" )
			return

		# ��¼�����߼�����ʱ�䣬�Ա�������������������
		self._inviterBase = captainBase
		self._inviteTeamTime = time.time()

		captainBase.replyTeamInvite( True, self.getName(), self )

	def acceptTeamRequset( self, targetName ):
		"""
		Exposed method.
		�ӳ����ռӶ�����

		@param targetName : ͬ���Ŀ������
		@type targetName : STRING
		"""
		if not self.isCaptain():
			return
		if self.isTeamFull():
			return

		BigWorld.lookUpBaseByName( "Role", targetName, self.acceptTeamLookUpCB )

	def acceptTeamLookUpCB( self, playerMailbox ):
		"""
		�ӳ�������ҼӶ����󣬸������ֲ������base mailbox�Ļص�
		"""
		playerMailbox.captainAcceptTeamRequest( self )

	def captainAcceptTeamRequest( self, captainMailbox ):
		"""
		Define method.
		�ӳ������˼Ӷ����󣬸�������������ж��Ƿ�������

		@param captainMailbox : ����Ӷӵ�Ŀ��ӳ�base mailbox
		@type captainMailbox : MAILBOX
		"""
		# ����Ѿ����
		if self.isInTeam():
			captainMailbox.client.onStatusMessage( csstatus.TEAM_PLAYER_IN_TEAM, "" )
			return

		# �Ѿ�������������룬��û������ʱЧ
		if self._inviterBase and time.time() - self._inviteTeamTime < TEAM_INVITE_TIME_OUT:
			captainMailbox.client.onStatusMessage( csstatus.TEAM_PLAYER_IN_TEAM_INVITE, "" )
			return

		# ��¼�����߼�����ʱ�䣬�Ա�������������������
		self._inviterBase = captainMailbox
		self._inviteTeamTime = time.time()

		captainMailbox.replyTeamInvite( True, self.getName(), self )

	#---------------------------------------------------------------------------------
	def replyTeamInviteByFC( self, agree ):
		"""
		exposed method.
		�ɿͻ��˵��ã���������룬��˴˷������ڱ������ߵ�base��ִ�С�

		@param agree:ͬ�����
		@type agree:INT8
		"""
		if self._inviterBase:
			# ���첽�������п��ܵģ�
			# ����Ҳ���֪����ұ�����ʱ�Ƿ�Ҳ�����˱��ˣ���˱���Ҫ�ָ�������
			# ���ȷʵ��Ҫ���������˱���ʱ������������룬
			# �����ڿͻ��˵ı�����ӿ���ֱ���ж�
			if self.isInTeam():
				# �Ѽ������
				self.statusMessage( csstatus.TEAM_SELF_IN_TEAM )
				self._inviterBase.replyTeamInvite( False, self.getName(), self )
				self._inviterBase = None
				self._inviteTeamTime = 0.0
			else:
				# û�м������
				self._inviterBase.replyTeamInvite( agree, self.getName(), self )
				if not agree:
					self._inviterBase = None
					self._inviteTeamTime = 0.0
		else:
			WARNING_MSG( "not invite join to team! name:", self.getName() )

	def replyTeamInvite( self, agree, replierName, replierBase ):
		"""
		define method.
		�������߻ظ������߹�����ӵ����룬��˴˷������������ߵ�base��ִ�С�

		@param replierName: �ظ��ߵ�����
		@type  replierName: string
		@param playerBase: �ظ��ߵ�BASE
		@type  playerBase: mailbox
		"""
		if not agree:
			self.statusMessage( csstatus.TEAM_PLAYER_REFUSE_JOIN )
			return

		# ���ߵ���һ����û�ж���mailbox�ͱ�ʾ���鲻���ڣ���������
		if self.teamMailBox == None:
			self.createSelfTeamLocally()
			# ֪ͨ�������ϵͳ���д���
			self.cmi_onJoinTeam()

		if self.isTeamFull():
			# ֪ͨ�������ߣ�������Ķ����������޷�����
			replierBase.joinFullTeamNotify()
			return
		# ֪ͨ��Ҽ���
		replierBase.joinTeamNotify( self.id, self.teamMailBox )

	def joinFullTeamNotify( self ):
		"""
		define method.
		֪ͨ����Ķ���������ͬʱ���������Ϣ��
		"""
		self._inviterBase = None
		self._inviteTeamTime = 0.0
		self.statusMessage(csstatus.TEAM_FULL_REFUSE_JOIN)

	def joinTeamNotify( self, captainID, teamMailBox ):
		"""
		define method.
		֪ͨ�������߼�����飬��˴˷������ڱ������ߵ�base��ִ��

		@param captainID: �ӳ���EntityID
		@type  captainID: OBJECT_ID
		@param teamMailBox: ����BASE
		@type  teamMailBox: mailbox
		"""
		if self.isInTeam():
			# ������Ѿ�������飬��ǰʲô���鶼����
			return

		# ���������Ǽ����Ѿ������˶���
		# ��˻����ö���mailbox����ȥ�������ߵļ�¼
		self.teamMailBox = teamMailBox
		self.teamID = teamMailBox.id
		self.captainID = captainID
		self._inviterBase = None
		self._inviteTeamTime = 0.0

		# ֪ͨ
		#if hasattr( self, "cell" ):
		#	self.cell.teamInfoNotify( captainDBID, teamMailBox )
		#self.client.teamInfoNotify( teamID, captainID )

		# ���Լ���ӵ�����
		self.teamMailBox.join( self.databaseID, self.playerName, self, self.raceclass, self.headTextureID )
		# ֪ͨ�������ϵͳ���д���
		self.cmi_onJoinTeam()

	#---------------------------------------------------------------------------------

	def addTeamMember( self, playerDBID, entityID, playerName, playerBase, playerRaceclass, headTextureID ):
		"""
		define method.
		��ӳ�Ա����

		���̣�
		�����Ա�б�����ӳ�Ա
		@param entityID:   ��ҵ�ID
		@type  entityID:   object_id
		@param playerDBID: ���DBID
		@type  playerDBID: DATABASE_ID
		@param   entityID: ��Ա��entityID���д�ֵ��ԭ�����¼���Ķ�ԱҲ��Ҫ֪�������ߵĶ�Ա��entityID(�����ߵĶ�Ա��mailboxΪNone)
		@type    entityID: OBJECT_ID
		@param playerBase: ���BASE
		@type  playerBase: mailbox
		@param playerName: �������
		@type  playerName: string
		@param playerRaceclass: ���ְҵ
		@type  playerRaceclass: INT32
		"""
		# ��ӳ�Ա
		self._teamMembers[playerDBID] = playerBase
		self._teamMembersID[playerDBID] = entityID
		# ֪ͨcell��client
		if hasattr( self, "cell" ) and playerBase:		# ֻ��playerBase��ΪNone�����ߣ�ʱ�Ż�֪ͨcell
			self.cell.addTeamMember( playerDBID, playerBase )
		if hasattr( self, "client" ):
			self.client.addTeamMember( entityID, playerDBID, playerName, playerRaceclass, int( playerBase is not None ), headTextureID )

	#---------------------------------------------------------------------------------
	# �����ӡ������������ɢ
	def leaveTeamNotify( self, srcEntityID, dstEntityID ):
		"""
		define method.
		����뿪֪ͨ���˽ӿ���TeamEntity����

		@param srcEntityID: ��ҵ�EntityID
		@type  srcEntityID: OBJECT_ID
		@param dstEntityID: ���DBID
		@type  dstEntityID: DATABASE_ID
		"""
		# ���첽������£�������cell��client���п��ܳ��ֵ�
		if hasattr( self, "cell" ):
			self.cell.removeTeamMember( dstEntityID )
		if hasattr( self, "client" ) and self.client:
			self.client.leaveTeamNotify( dstEntityID, int( srcEntityID != dstEntityID ) )

		if dstEntityID == self.id:
			# �Լ��뿪
			self.clearTeamInfo()
			self._teamMembers.clear()
			self._teamMembersID.clear()
			self.cmi_onLeaveTeam()
		else:
			# �����뿪
			playerDBID = self.getTeamMemberDBID( dstEntityID )
			if playerDBID != 0:
				self._teamMembers.pop( playerDBID )
				self._teamMembersID.pop( playerDBID )

	def leaveTeamFC( self, playerID ):
		"""
		exposed method.
		����Լ���ӻ򿪳������ӡ�
		1�����playerID���Լ�������ӣ�
		2�����playerID�����Լ����Լ��Ƕӳ��򿪳�playerID������
		@param playerID: ���������ID
		@type  playerID: OBJECT_ID
		"""
		if not self.isInTeam():
			# δ�����κζ���
			return

		if self.id != playerID and self.id != self.captainID:
			# �Ȳ����Լ���ӣ�Ҳ���Ƕӳ�������ֱ�Ӻ���
			return

		self.teamMailBox.leave( self.id, playerID )

	#---------------------------------------------------------------------------------
	def disbandTeamFC( self ):
		"""
		exposed method.
		�����ɢ���飬�˷������ڿͻ���

		���̣�
		�������ж�
		��1����Ҳ��Ƕӳ����жϲ���

		�����ö���Ľ�ɢ����
		"""
		if not self.isCaptain():
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_CAPTAIN )
			return
		if self.teamMailBox == None:
			return
		self.teamMailBox.disband()

	def disbandTeamNotify( self ):
		"""
		define method.
		�����ɢ֪ͨ���˷�����TeamEntity����
		"""
		self.clearTeamInfo()
		self._teamMembers.clear()
		self._teamMembersID.clear()
		if hasattr( self, "cell" ):
			self.cell.disbandTeamNotify()
			self.client.disbandTeamNotify()
		self.cmi_onLeaveTeam()

	def clearTeamInfo( self ):
		"""
		define method.
		���������Ϣ���˷���һ������ڶ����ɢ��������ʧ��ʱ��
		�磺����teamMailbox.join()���Լ������ʧ��ʱ�ͻ���ô˷�����
		"""
		self.teamID = 0
		self.captainID = 0
		self.teamMailBox = None

	def changeCaptainFC( self, playerID ):
		"""
		exposed method.
		�ƽ��ӳ�Ȩ�ޣ��˽ӿ���client����

		@param playerID: ���DBID
		@type playerID: DATABASE_ID
		"""
		# �ƽ���Ŀ�겻�����Լ�
		if self.id == playerID:
			return

		# û�м����κζ���
		if not self.isInTeam():
			self.statusMessage( csstatus.TEAM_NOT_IN_TEAM )
			return

		# ���Ƕӳ�
		if not self.isCaptain():
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_CAPTAIN )
			return

		# ������û�д����
		if self.getTeamMemberDBID( playerID ) == 0:
			self.statusMessage( csstatus.TEAM_NOT_IN_TEAM )
			return

		# �ö�Ա������
		if not self.getTeamMemberMailbox( playerID ):
			self.statusMessage( csstatus.TEAM_NOT_ON_LINE )
			return

		self.teamMailBox.changeCaptain( playerID )

	def changeCaptainNotify( self, captainID ):
		"""
		define method.
		�ӳ��ı�

		���̣�
		���ı�ӳ���ǣ������¶ӳ�
		��֪ͨcell���ӳ��ı�

		@param captainID: �ӳ����DBID
		@type  captainID: DATABASE_ID
		"""
		self.captainID = captainID
		# ���첽������£�������cell��client���п��ܳ��ֵ�
		if hasattr( self, "cell" ):
			self.cell.changeCaptainNotify( captainID )
		if hasattr( self, "client" ):
			self.client.changeCaptainNotify( captainID )

	#---------------------------------------------------------------------------------
	# �������
	def logonForTeam( self ):
		"""
		�������
		"""
		# ȡ���������
		try:
			teamManager = BigWorld.globalBases["TeamManager"]
		except:
			teamManager = None
			ERROR_MSG( "get team manager entity error!" )
			return

		teamManager.rejoinTeam( self.teamID, self.databaseID, self )

	def team_onLogout( self ):
		"""
		����������ߴ���
		��������������Ҷ���������ã�������н����������⣬�Ӷ������ڴ�й©
		"""
		if self.teamMailBox:
			self.teamMailBox.logout( self.databaseID )
		self.teamMailBox = None
		self._teamMembers.clear()	# �����������������ڴ�й©

	def teamInfoNotify( self, captainID, teamEntity ):
		"""
		define method.
		���ö�����Ϣ
		@param captainID: ���BASE
		@type  captainID: mailbox
		@param teamEntity: ���BASE�����ֵΪNone�����ʾ���鲻�ٴ���
		@type  teamEntity: mailbox
		"""
		self.teamMailBox = teamEntity
		self.captainID = captainID
		if teamEntity:
			self.teamID = teamEntity.id
		else:
			self.teamID = 0
		self.cell.teamInfoNotify( captainID, teamEntity )
		self.client.teamInfoNotify( teamEntity.id, captainID )

	def rejoinTeam( self, oldEntityID, playerDBID, playerBase ):
		"""
		define method.
		��Ա����

		���̣�
		���޸ĳ�Ա�б�ĳ�Ա����״̬
		��֪ͨcell����Ա����

		@param playerDBID: ���DBID
		@type playerDBID: DATABASE_ID
		@param playerBase: ���BASE
		@type playerBase: mailbox
		"""
		self._teamMembers[playerDBID] = playerBase
		self._teamMembersID[playerDBID] = playerBase.id


		# ���첽������£�������cell��client���п��ܳ��ֵ�
		if hasattr( self, "cell" ):
			self.cell.addTeamMember( playerDBID, playerBase )
		if hasattr( self, "client" ):
			self.client.rejoinTeam( oldEntityID, playerBase.id )

	def logoutNotify( self, playerDBID ):
		"""
		define method.
		��Ա����

		���̣�
		���ڳ�Ա�б����������Ϊ����״̬
		��֪ͨcell�����������

		@param playerDBID: ���DBID
		@type playerDBID: DATABASE_ID
		"""
		# ���첽������£�������cell��client���п��ܳ��ֵ�
		if hasattr( self, "cell" ):
			self.cell.removeTeamMember( self._teamMembers[playerDBID].id )
		if hasattr( self, "client" ):
			self.client.logoutNotify( self._teamMembers[playerDBID].id )

		self._teamMembers[playerDBID] = None

	def changePickUpState( self, state ):
		"""
		exposed method.
		������Ʒʰȡ��ʽ���˽ӿ���client�ӳ�����

		@param state: ���ĵ�ʰȡ��ʽ define in csdefine.py
		@type state: INT8
		"""
		# û�м����κζ���
		if not self.isInTeam():
			self.statusMessage( csstatus.TEAM_NOT_IN_TEAM )
			return

		# ���Ƕӳ�
		if not self.isCaptain():
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_CAPTAIN )
			return

		if self.pickUpState == state: return

		self.teamMailBox.onChangePickUpState( state )


	def changePickUpQuality( self, val ):
		"""
		exposed method.
		"""
		# û�м����κζ���
		if not self.isInTeam():
			self.statusMessage( csstatus.TEAM_NOT_IN_TEAM )
			return

		# ���Ƕӳ�
		if not self.isCaptain():
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_CAPTAIN )
			return

		self.teamMailBox.onChangePickUpQuality( val )


	def changeRollQuality( self, val ):
		"""
		exposed method.
		�ı�ROLL������ж�Ʒ��
		"""
		# û�м����κζ���
		if not self.isInTeam():
			self.statusMessage( csstatus.TEAM_NOT_IN_TEAM )
			return

		# ���Ƕӳ�
		if not self.isCaptain():
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_CAPTAIN )
			return

		self.teamMailBox.onChangeRollQuality( val )



	def changePickUpStateNotify( self, state ):
		"""
		define method.
		������Ʒʰȡ��ʽ֪ͨ

		@param state: ���ĵ�ʰȡ��ʽ define in csdefine.py
		@type state: INT8
		"""
		self.pickUpState = state

		# ���첽������£�������cell��client���п��ܳ��ֵ�
		if hasattr( self, "cell" ):
			self.cell.changePickUpStateNotify( state )
		if hasattr( self, "client" ):
			self.client.changePickUpStateNotify( state )



	#---------------------------------------------------------------------------------
	def requestTeammateInfoFC( self, playerID ):
		"""
		exposed method.
		����ָ����ҵ���Ϣ

		@param playerID: ���ID
		@type  playerID: OBJECT_ID
		"""
		mailbox = self.getTeamMemberMailbox( playerID )
		if mailbox is None:
			ERROR_MSG("other player get member data!")
			return
		mailbox.cell.requestTeammateInfo( self )

	def requestTeammatePetInfoFC( self, playerID ):
		"""
		exposed method.
		����ָ�����ѳ������Ϣ

		@param playerID: ���ID
		@type  playerID: OBJECT_ID
		"""
		mailbox = self.getTeamMemberMailbox( playerID )
		if mailbox is None:
			ERROR_MSG("other player get member data!")
			return
		mailbox.cell.requestTeammatePetInfo( self )

	def teamChat( self, msg, blobArgs ):
		"""
		defined method
		���ģ���RoleChat.py����

		@param       msg: ���������
		@type        msg: STRING
		@param		blobArgs : ��Ϣ�����б�
		@type		blobArgs : BLOB_ARRAY
		@return:          ��
		"""
		if self.teamMailBox is None:
			DEBUG_MSG( "not in team." )
			return

		# �����Ҫ��������ٶȽ������ƣ�����ÿ��ֻ�ܷ�һ����ģ����������������ش���
		# in here, to do

		for mailbox in self._teamMembers.itervalues():
			if mailbox:
				mailbox.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_TEAM, self.id, self.playerName, msg, blobArgs )

	def getTeamMemberIDs( self ):
		"""
		"""
		return self._teamMembersID.values()

	def refuseTeammateInvite( self, targetName, teammateID ):
		"""
		Exposed method.
		�ܾ���������������ҵ��������

		@param taregetName : ���������Ŀ���������
		@type taregetName : STRING
		@param teammateID : ���ѵ�entity id
		@type teammateID : OBJECT_ID
		"""
		teammateMailBox = self.getTeamMemberMailbox( teammateID )
		if teammateMailBox:
			teammateMailBox.client.onStatusMessage( csstatus.TEAM_CAPTAIN_REFUSE_INVITE, "(\'%s\',)" % targetName )

	def createTeamBySelf( self ):
		"""
		Exposed method.
		�Խ�����
		"""
		if self.teamMailBox == None:
			self.createSelfTeamLocally()
			self.statusMessage( csstatus.TEAM_CREATE_SELF_NOTICE )
			# ֪ͨ�������ϵͳ���д���
			self.cmi_onJoinTeam()
		else:
			self.statusMessage( csstatus.TEAM_IN_TEAM_NOT_CREATE_SELF )

	def createSelfTeamLocally( self ) :
		"""
		�ڱ���base�ϴ����Լ��Ķ���
		"""
		if self.teamMailBox is not None :
			WARNING_MSG( "[%s(id:%i)]: I am still in a team(ID:%i)." % ( self.getName(), self.id, self.teamMailBox.id ) )
		teamArg = {	"captainDBID"	: self.databaseID,
					"captainName"	: self.getName(),
					"captainBase"	: self,
					"captainRaceclass"	: self.raceclass,
					"pickUpState"	: csdefine.TEAM_PICKUP_STATE_ORDER,
					"captainHeadTextureID"	: self.headTextureID
					}
		self.teamMailBox = BigWorld.createBaseLocally( "TeamEntity", { "teamArg":teamArg } )
		self.teamID = self.teamMailBox.id
		self.captainID = self.id

# end of method: teamChat()
