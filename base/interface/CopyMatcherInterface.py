# -*- coding: gb18030 -*-

# python
import random
# BigWorld
import BigWorld
# common
import csdefine
import csstatus
from bwdebug import ERROR_MSG, INFO_MSG, WARNING_MSG
# base
import ECBExtend



class CopyMatcherInterface :
	"""
	"""
	def __init__( self ) :
		self._matchedGroupID = 0												# ��¼�ɹ�ƥ�����ID
		self._matchStatus = csdefine.MATCH_STATUS_PERSONAL_NORMAL				# ����Ҫ����
		self._leaveForMatchedTeam = False										# �뿪�ɶ��飬�����µĶ���ı��
		self._joiningMatchedTeam = False										# ����ƥ�����ı��
		self._tid_confirmMatch = 0												# ְ��ȷ�ϵ�timerID
		self._tid_selectingDuty = 0												# ְ��ѡ���timerID
		self._tid_resetMatchStatus = 0 											# 5����ʱ����״̬
	
	# ----------------------------------------------------------------
	# functions in common
	# ----------------------------------------------------------------
	@staticmethod
	def queuerMgr() :
		"""
		��ȡ�Ŷ��߹�����
		"""
		return BigWorld.globalData["copyTeamQueuerMgr"]

	def setMatchStatus( self, status ) :
		"""
		Defined method
		����ƥ��״̬
		"""
		if self._matchStatus != status :
			oldStatus = self._matchStatus
			self._matchStatus = status
			self.client.updateMatchStatusFromServer( oldStatus, self._matchStatus )

	def isMatchStatus( self, status ) :
		"""
		"""
		return self._matchStatus == status

	def isMatchingInQueue( self ) :
		"""
		�Ƿ������ڶ����еȴ�ƥ��
		"""
		return self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_MATCHING )

	def isInCopyMatcherQueue( self ) :
		"""
		�Ƿ����Ŷ��߹�������
		"""
		return self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_MATCHING ) or\
			self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_CONFIRMING ) or\
			self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_MATCHED )

	def isMatchedInQueue( self ) :
		"""
		�Ƿ��Ѿ��ɹ�ƥ�䣬�����ڶ�����
		"""
		return self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_CONFIRMING ) or\
			self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_MATCHED )
	
	def updateAvgQueueingTimeFromServer( self ):
		"""
		<Define method>
		��queuerMgr��ͬ�ȼ��ε�queuer������������queuer�ĸ���Ҫ����ƽ���ȴ�ʱ�䣬ÿ��queuerΪ29��
		"""
		self.queuerMgr().querySameLevelQueuersNumber( self, self.level)
	
	def onQuerySameLevelQueuersNumber( self, sameLevelQueuersNumber ) :
		"""
		<Define Method>
		@ type    UINT8
		@ param   �����Ŷ��У�������Ҵ���ͬһ�ȼ��ε�queuer����
		"""
		avgTime = 300
		if sameLevelQueuersNumber < 14:
			avgTime = ( 14 - sameLevelQueuersNumber ) * random.randint(23,39)
		elif sameLevelQueuersNumber == 14 :
			avgTime = 120
		else:
			avgTime = ( sameLevelQueuersNumber % 14 ) * random.randint(23,39)
		INFO_MSG("updateAvgQueueingTimeFromServer avgTime is %d." % avgTime)
		self.client.updateAvgQueueingTimeFromServer( avgTime )
		
	

	# ----------------------------------------------------------------
	# about join matcher queue
	# ----------------------------------------------------------------
	def joinCopyMatcherAsSingle( self, duties, copies, camp, expectGuider ) :
		"""
		<Define method>
		@type		duties : UINT8_TUPLE(python tuple)
		@param		duties : ѡ���ְ��
		@type		copies : STRING_TUPLE(python tuple)
		@param		copies : ѡ���ְ��
		@type		expectGuider : BOOL
		@param		expectGuider : �Ƿ�Ը�ⵣ�ζ�����
		"""
		if self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_NORMAL ) :
			members = ((self,self.getName(),duties,expectGuider),)				# ( ( mailbox, name, duties,expectGuider ), )
			self.queuerMgr().onReceiveJoinRequest( self, self.level, members, copies, self.blacklistOfName(), camp, False )
		else :
			WARNING_MSG( "[%s(id:%i)]: I am in match status %i, but still try to join matcher." %\
				 ( self.getName(), self.id, self._matchStatus,) )

	def joinCopyMatcherAsCaptain( self, duties, copies, camp, expectGuider ) :
		"""
		<Define method>
		@type		duties : UINT8_TUPLE(python tuple)
		@param		duties : ѡ���ְ��
		@type		copies : STRING_TUPLE(python tuple)
		@param		copies : ѡ���ְ��
		@type		expectGuider : BOOL
		@param		expectGuider : �Ƿ�Ը�ⵣ�ζ�����
		"""
		if self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_NORMAL ) :
			team = self.getTeamMailbox()
			if team is None :
				ERROR_MSG( "[%s(id:%i)]: Team(teamID:%i) not found." % ( self.getName(), self.id, self.teamID ) )
			else :
				team.initiateSelectingDutiesByCaptain( self.level, duties, copies, expectGuider, self.blacklistOfName(), camp )
		else :
			WARNING_MSG( "[%s(id:%i)]: I am in match status %i, but still try to join matcher." %\
				 ( self.getName(), self.id, self._matchStatus,) )

	def undertakeDutiesOf( self, duties, expectGuider ) :
		"""
		<Define method>
		@type		duties : UINT8_TUPLE(python tuple)
		@param		duties : ѡ���ְ��
		@type		expectGuider : BOOL
		@param		expectGuider : �Ƿ�Ը�ⵣ�ζ�����
		"""
		team = self.getTeamMailbox()
		if team is None :
			ERROR_MSG( "[%s(id:%i)]: Team(teamID:%i) not found." % ( self.getName(), self.id, self.teamID ) )
		else :
			team.onMemberSelectedDuties( self.databaseID, duties, expectGuider, self.blacklistOfName(), self.level )

	def refuseToUndertakeAnyDuty( self ) :
		"""
		<Exposed method>
		"""
		team = self.getTeamMailbox()
		if team is None :
			ERROR_MSG( "[%s(id:%i)]: Team(teamID:%i) not found." % ( self.getName(), self.id, self.teamID ) )
		else :
			team.onMemberRefuseToSelectDuty( self.databaseID )

	def onJoinCopyMatcherQueue( self ) :
		"""
		<Define method>
		"""
		INFO_MSG( "[%s(id:%i)]:Join copy matcher callback." % ( self.getName(), self.id) )
		self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_MATCHING )
		self.statusMessage( csstatus.CTM_JOIN_MATCHER_QUEUE )

	def onRejoinCopyMatcherQueue( self ) :
		"""
		<Define method>
		"""
		INFO_MSG( "[%s(id:%i)]: Rejoin copy matcher." % ( self.getName(), self.id ) )
		self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_MATCHING )

	def blacklistOfName( self ) :
		"""
		��ȡ����������ҵ�����
		"""
		return tuple( r.playerName for r in self.blacklist.itervalues() )

	# ----------------------------------------------------------------
	# about leave matcher queue
	# ----------------------------------------------------------------
	def cmi_onLeaveTeam( self ) :
		"""
		�뿪����
		"""
		if self._leaveForMatchedTeam :
			self.__replyReadyForMatchedTeam()
			self._leaveForMatchedTeam = False
			self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_NORMAL )
		elif self.isMatchingInQueue() :
			self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_NORMAL )		# ����������Ϊ��ͨ״̬������Ϊ����Ѿ��Ӷ����뿪�������ٴӶ����Ǳߵõ�֪ͨ
			self.statusMessage( csstatus.CTM_LEAVE_QUEUE_IN_COMMON )
		elif self.isMatchedInQueue() :
			self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_NORMAL )		# ����������Ϊ��ͨ״̬������Ϊ����Ѿ��Ӷ����뿪�������ٴӶ����Ǳߵõ�֪ͨ
			self.queuerMgr().onMatchedPlayerCollapse( self._matchedGroupID, self.id )

	def cmi_onJoinTeam( self ) :
		"""
		������һ������
		"""
		if self._joiningMatchedTeam :
			self._replyJoinMatchedCopyTeam()
			self._joiningMatchedTeam = False
		elif self.isInCopyMatcherQueue() :
			self.leaveQueuerMgr()

	def cmi_onLogout( self ) :
		"""
		�������
		"""
		if self.isMatchingInQueue() and not self.isInTeam() :
			self.queuerMgr().removeQueuer( self.id, csstatus.CTM_LEAVE_QUEUE_SILENTLY )
		elif self.isMatchedInQueue() :
			self.queuerMgr().onMatchedPlayerCollapse( self._matchedGroupID, self.id )
		elif self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_SELECTING_DUTY ) :
			self.cancelSelectingDuties()

	def cmi_onTeamDisband( self ) :
		"""
		�����ɢ��Ŀǰδ����������������ɢ��Ĵ���
		"""
		self.cmi_onLeaveTeam()

	def leaveCopyMatcherQueue( self ) :
		"""
		�����뿪��Ӷ���
		<Exposed method>
		"""
		if self.isMatchingInQueue() :
			if not self.isInTeam() :
				self.queuerMgr().removeQueuer( self.id, csstatus.CTM_LEAVE_QUEUE_IN_COMMON )
			elif self.isCaptain() :
				self.queuerMgr().removeQueuer( self.getTeamMailbox().id, csstatus.CTM_LEAVE_QUEUE_IN_COMMON )
			else :
				ERROR_MSG( "[%s(id:%i,captainID:%s)]: Only captain is allowed to leave queue."\
					 % ( self.getName(), self.id, self.captainID ) )
		elif self.isMatchedInQueue() :
			self.queuerMgr().onMatchedPlayerCollapse( self._matchedGroupID, self.id )

	def onLeaveCopyMatcherQueue( self, reason ) :
		"""
		<Define method>
		@type		reason : INT32
		@param		reason : �뿪��ԭ����csstatus�ж��壩
		"""
		INFO_MSG( "[%s(id:%i)]:Leave copy matcher callback, reason: 0x%0x" % ( self.getName(), self.id, reason ) )
		self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_NORMAL )
		if reason != csstatus.CTM_LEAVE_QUEUE_SILENTLY :
			self.statusMessage( reason )

	def leaveQueuerMgr( self ) :
		"""
		�뿪�Ŷ��߹�����
		"""
		if self.isMatchingInQueue() :
			self.queuerMgr().removeQueuer( self.id, csstatus.CTM_LEAVE_QUEUE_IN_COMMON )
		elif self.isMatchedInQueue() :
			self.queuerMgr().onMatchedPlayerCollapse( self._matchedGroupID, self.id )

	def onRemovedFromQueuerMgr( self, collapserID ) :
		"""
		<Define method>NEW???
		���Ŷ��߹������Ƴ���֪ͨ���
		"""
		pass


#	# ----------------------------------------------------------------
	# handle after matched successfully
	# ----------------------------------------------------------------
	def onRematchedAsRecruiter( self, groupID ) :
		"""
		<Define method>
		@type		groupID : UID
		@param		groupID : ƥ��С���ID
		��ļ���ٴγɹ�ƥ��
		"""
		INFO_MSG( "[%s(id:%i)]: Join matched group %i." % ( self.getName(), self.id, groupID ) )
		self._matchedGroupID = groupID
		self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_MATCHED )

	def enterConfirmingCopyMatched( self, groupID, dutyMap, copyLabel, copyLevel, bossesTotal, bossesKilled, copies ) :
		"""
		<Define method>
		@type		groupID : UID
		@param		groupID : ƥ��С���ID
		@type		dutyMap : PY_DICT
		@param		dutyMap : ƥ���ְ��
		@type		copyLabel : STRING
		@param		copyLabel : ��������
		@type		copyLevel : UINT8
		@param		copyLevel : �����ȼ�
		@type		bossesTotal : UINT8
		@param		bossesTotal : ����BOSS����
		@type		bossesKilled : UINT8
		@param		bossesKilled : ����BOSS�ѻ�ɱ����
		"""
		#dutyMap�Ⱥ�������ְ��ʱʹ�ã���ʱ������ͳһ��DPS����
		duty = csdefine.COPY_DUTY_DPS
		INFO_MSG( "[%s(id:%i)]: Enter match confirming, matched group %i." % ( self.getName(), self.id, groupID ) )
		self._matchedGroupID = groupID
		self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_CONFIRMING )       #�ÿͻ�����Ӧ���븱��ȷ�Ͻ���
		self.client.notifyToConfirmCopyMatchedFromServer( duty, copyLabel, copyLevel, bossesTotal, bossesKilled, copies )
		self._tid_confirmMatch = self.addTimer( csdefine.TIME_LIMIT_OF_MATCHED_CONFIRM, 0, ECBExtend.TIMEOUT_CBID_OF_MATCHED_CONFIRM )

	
	def initiateSelectingDuties( self, copies ):
		"""
		<Defined method>
		@type		copies : STRING_TUPLE
		@param		copies : ǰ���ĸ�������		
		"""	
		if self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_SELECTING_DUTY ) : #��δ����ʱ���ӳ����·���ְ��ѡ���ȳ���
			self.cancelSelectingDuties()
		self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_SELECTING_DUTY )
		INFO_MSG( "[%s(id:%i)]: Enter selecting duties, teamID %i." % ( self.getName(), self.id, self.teamID ) )
		self.client.notifyToSelectDutiesFromServer( copies )
		self._tid_selectingDuty = self.addTimer( csdefine.TIME_LIMIT_OF_DUTIES_SELECTION, 0, ECBExtend.TIMEOUT_CBID_OF_DUTIES_SELECTION )

	def cancelSelectingDuties( self ):
		"""
		<Defined method>
		@type		copies : STRING_TUPLE
		@param		copies : ǰ���ĸ�������		
		"""	
		if self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_SELECTING_DUTY ) :
			self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_NORMAL )
			INFO_MSG( "[%s(id:%i)]: Cancel selecting duties." % ( self.getName(), self.id ) )
			self.client.cancelSelectingDutiesFromServer()
		if self._tid_selectingDuty :
			self.delTimer( self._tid_selectingDuty )
			self._tid_selectingDuty = 0

	
	def addResetMatchTimer( self ):
		"""
		<Defined method>
		"""	
		self._tid_resetMatchStatus = self.addTimer( csdefine.TIME_RESET_MATCH_STATUS, 0, ECBExtend.TIME_CBID_OF_RESET_MATCH_STATUS )
	
	def onTime_reSetMatchStatus( self, timerID, cbid  ):
		self.queuerMgr().reSetMatchStatus( self._matchedGroupID )
	
	def hideConfirmWindow( self ):
		"""
		<Define method>
		"""
		self.client.hideConfirmWindow()


	def onTimer_matchedConfirmTimeout( self, timerID, cbid ) :
		"""
		"""
		self.client.onMatchedConfirmTimeout()
		self.__replyMatchedConfirmToMgr( False )
		self._tid_confirmMatch = 0

	
	def onTimer_dutiesSelectionTimeout( self, timerID, cbid ) :
		"""
		"""
		team = self.getTeamMailbox()
		if team is None :
			ERROR_MSG( "team isn't exit but [%s(id:%i)] is also in selecting" % ( self.getName(), self.id ) )
			self.cancelSelectingDuties()
		else :
			team.onMemberSelectingDutyTimeout( self.databaseID )
	

	def confirmCopyMatchedFromClient( self, accept ) :
		"""
		<Exposed method>
		@type		accept : BOOL
		@param		accept : �Ƿ���ܱ���ƥ��
		"""
		#if self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_MATCHED ) :
		INFO_MSG("self._tid_confirmMatch: %i" % self._tid_confirmMatch )
		if self._tid_confirmMatch :
			self.__replyMatchedConfirmToMgr( accept )
			#��ʱ�Ͱ�timerȡ��
			self.delTimer( self._tid_confirmMatch )
			self._tid_confirmMatch = 0
		else :
			INFO_MSG( "[%s(id:%i)]: Matched confirm timeout." % ( self.getName(), self.id ) )
			self.statusMessage( csstatus.CTM_MATCHED_CONFIRM_TIMEOUT )

		"""
		else :
			ERROR_MSG( "[%s(id:%i)]:Not confirming status currently but status %i." %\
				( self.getName(), self.id, self._matchStatus ) )
		"""

	def __replyMatchedConfirmToMgr( self, accept ) :
		"""
		reply current matched confirming to queuer mgr.
		"""
		self.queuerMgr().onPlayerConfirmMatched( self._matchedGroupID, self.id, accept )

	def __replyReadyForMatchedTeam( self ) :
		"""
		���߹���������׼���ü���ƥ�����
		"""
		self.queuerMgr().onPlayerReadyForMatchedTeam( self._matchedGroupID, self.id )

	def onMatchedConfirmSuccessfully( self ) :
		"""
		<Define method>
		ְ��ȷ�ϳɹ�
		"""
		self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_MATCHED )
		if self.isInTeam() :
			self._leaveForMatchedTeam = True							# �������ǴӾɶ����Ƴ����Ա���뵽ƥ����飬
																		# �������ֶ��뿪���飬�����������з�����
																		# ���ֶ��뿪����������Ҳ�������뿪�ɶ����
																		# ���¶���Ĵ���
			self.getTeamMailbox().leave( self.id, self.id )					# �Ӿɶ����뿪
		self.__replyReadyForMatchedTeam()

	def createMatchedCopyTeam( self ) :
		"""
		<Define method>
		�����¸�������
		ע���ߵ�����ʱ��teamMailbox���ڵ�������п��ܳ��֣���Ȼǰ
		���Ѿ��öӳ���ɢ�˶��飬���ǽ����ž�֪ͨ�����¶����ˣ�����
		���첽��������ܽ�ɢ�����֪ͨ��û������Ѿ�Ҫ�����¶����ˡ�
		���ǣ��Ƿ����������teamMailbox���ڵ����ʱ��ֱ�Ӱ�teamMailbox
		��������������ܻᵼ���������û����Ӷ��������⡣
		��ʱ����취���������teamMailbox���ڵ����������ʱһ��ʱ���ٴ�
		��������¼���Դ������ڴﵽһ����������ʧ��ʱ�ٱ���
		# --------------------------------------------------
		Ŀǰ�Ѿ�ʹ����һ�ַ�ʽ�Ա�֤����ڳɹ��뿪�ɵĶ���֮���ٽ���
		�����¶����Լ������¶���Ĳ�������������ͳ������ƥ�����Ҿ�
		���뿪�˾ɶ��飬Ȼ��Ž��д����¶���Ĳ�����
		"""
		if self.isInTeam() :
			ERROR_MSG( "[%s(id:%i)]: I am still in a team when trying to create matched copy team." % ( self.getName(), self.id ) )
			return
		#self.createSelfTeamAnywhere( self._onMatchedCopyTeamCreated )				# ���Լ���������
		self.createSelfTeamLocally()												# �ڱ�base�ϴ�������
		self.queuerMgr().onMatchedNewTeamCreated( self._matchedGroupID, self.id, self.getTeamMailbox() )

	def createSelfTeamAnywhere( self, callback ) :
		"""
		�����Լ��Ķ���
		"""
		teamArg = {	"captainDBID"	: self.databaseID,
					"captainName"	: self.getName(),
					"captainBase"	: self,
					"captainRaceclass"	: self.raceclass,
					"pickUpState"	: csdefine.TEAM_PICKUP_STATE_ORDER,
					"captainHeadTextureID"	: self.headTextureID
					}
		BigWorld.createBaseAnywhere( "TeamEntity", { "teamArg":teamArg }, callback )

	def _onMatchedCopyTeamCreated( self, teamMailbox ) :
		"""
		��������ص�
		"""
		if teamMailbox is None :
			ERROR_MSG( "[%s(id:%i)]: Create matched copy team fail." % ( self.getName(), self.id ) )
		else :
			self.teamMailBox = teamMailbox
			self.teamID = teamMailBox.id
			self.captainID = self.id
			self.queuerMgr().onMatchedNewTeamCreated( self._matchedGroupID, self.id, self.getTeamMailbox() )

	def joinMatchedCopyTeam( self, captainID, teamMailbox ) :
		"""
		<Define method>
		��Ҽ���ƥ����¶���
		@type		captainID : OBJECT_ID
		@param		captainID : �³�Ա����
		@type		teamMailbox : MAILBOX
		@param		teamMailbox : mailbox of teamEntity
		"""
		if self.isInTeam() :
			ERROR_MSG( "[%s(id:%i)]: I am still in a team when joining matched copy team." % ( self.getName(), self.id ) )
		else :
			self._joiningMatchedTeam = True
			self.joinTeamNotify( captainID, teamMailbox )

	def _replyJoinMatchedCopyTeam( self ) :
		"""
		���߹��������ѳɹ������¶���
		"""
		self.queuerMgr().onPlayerJoinMatchedTeam( self._matchedGroupID, self.id )

	def teleportCopyOnMatched( self, copyLabel ) :
		"""
		<Define method>
		���͵�ƥ��ĸ�������������ƥ�����̽�����ƥ��״̬����Ϊ��ͨ״̬
		@type	copyLabel : STRING
		@param	copyLabel : ƥ�丱���ı�ǩ
		"""
		self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_NORMAL )
		#�ڴ��͵�ʱ���жϣ�����ڸ����⣬�Ŵ��ͣ�������ȷ�Ͽ�
		self.cell.teleportCopyOnMatched( copyLabel )


	# ----------------------------------------------------------------
	# handle after enter copy successfully
	# ----------------------------------------------------------------
	def resumeHaltedRaid( self, teamID, camp ) :
		"""
		<Exposed method>
		���������Լ����жϵĸ���
		"""
		"""
		if self.isInCopyMatcherQueue() :
			WARNING_MSG( "[%s(id:%i)]: I am in %i status, no halted raid can be resumed." % ( self.getName(), self.id, self._matchStatus ) )
		else :
		"""
		team = self.getTeamMailbox()
		if team is None :
			ERROR_MSG( "[%s(id:%i)]: Team(teamID:%i) not found." % ( self.getName(), self.id, self.teamID ) )
		else :
			team.resumeHaltedRaidBy( self.databaseID, teamID, camp )


#	# kick out teammate ----------------------------------------------
	# kick out teammate operations
	# ----------------------------------------------------------------
	def initiateVoteForKickingTeammate( self, suffererID, reason ) :
		"""
		<Exposed method>
		@type	suffererID : OBJECT_ID
		@param	suffererID : �޳������ID
		@type	reason : STRING
		@param	reason : �޳�����
		"""
		if self.id == suffererID :								# ����ͶƱ���Լ�
			WARNING_MSG( "[%s(id:%i)]: Can't vote to kick self out." % ( self.getName(), self.id, ) )
			return
		elif self.isInTeam() :
			self.getTeamMailbox().initiateVoteForKickingMember( self.id, suffererID, reason )

	def voteForKickingTeammateFromClient( self, agree ) :
		"""
		<Exposed method>
		@type	agree : BOOL
		@param	agree : �Ƿ�ͬ��
		"""
		if self.isInTeam() :
			self.getTeamMailbox().memberVoteForKicking( self.id, agree )
