# -*- coding: gb18030 -*-

import time
import csdefine
import csstatus
import BigWorld
import ShareTexts as ST
from bwdebug import ERROR_MSG, INFO_MSG
from BaseSpaceCopyFormulas import spaceCopyFormulas
from spacecopymatcher.CopyTeamFormulas import copyTeamFormulas

class TeamMatcherInterface:

	def __init__( self ) :
		self._latestInitiateTime = 0								# time of the latest initiating selecting duties
		self.memberSelections = {}									# new property:{dbid:(duties, expcetGuider),}
		self.expectedCopies = ()									# expected copies of team
		self.memberBlacklist = {}									# �������ж�Ա�ĺ�����
		self.initiatedCopyLevel = 0									# �Ŷӷ����߶�Ӧ�ĸ����ȼ�
		self.matchedCopy = None										# ƥ��ɹ������ڽ��еĸ���
		self.matchStatus = csdefine.MATCH_STATUS_TEAM_NORMAL
		self.matchedGroupID = 0
		self._camp = 0 
		
		self.__beforeTeamChangeMembers = []                        #��¼����״̬�ı�ǰ�ĳ�Աbase

	# ----------------------------------------------------------------
	# functions in common
	# ----------------------------------------------------------------
	def setMatchStatus( self, status ) :
		"""
		����ƥ��״̬
		"""
		self.matchStatus = status

	def isMatchStatus( self, status ) :
		"""
		"""
		return self.matchStatus == status

	def isMatchingInQueue( self ) :
		"""
		�Ƿ����Ŷ��߹�������
		"""
		return self.isMatchStatus( csdefine.MATCH_STATUS_TEAM_MATCHING )

	def isMatchedInQueue( self ) :
		"""
		�Ƿ��Ѿ��ɹ�ƥ��
		"""
		return self.isMatchStatus( csdefine.MATCH_STATUS_TEAM_MATCHED )

	def isInDutiesSelecting( self ) :
		"""
		�Ƿ���ְ��ѡ����
		"""
		return self.isMatchStatus( csdefine.MATCH_STATUS_TEAM_SELECTING_DUTY )

	def broadcastMessage( self, exceptions, statusID, *args ) :
		"""
		"""
		args = len(args) and str(args) or ""
		for playerBase in self.membersOnline() :
			if playerBase.id not in exceptions :
				playerBase.client.onStatusMessage( statusID, args )
	
	def __broadcastMessageToPlayers( self, playerMBs, statusID, *args ) :
		"""
		"""
		args = args = len(args) and str(args) or ""
		for playerBase in playerMBs :
			if playerBase :
				playerBase.client.onStatusMessage( statusID, args )


	def broadcastMembers( self, majorDBID, statusID, *args ) :
		"""
		"""
		major_args = (ST.CNTITLE_NIN,) + args
		playerBase = self.memberMailboxOfDBID( majorDBID )
		playerBase.client.onStatusMessage( statusID, str(major_args) )
		self.broadcastMessage( (playerBase.id,), statusID, self.memberNameOfDBID(majorDBID), *args )

	def labelOfDuties( self, duties ) :
		"""
		format duties to characters
		"""
		ct_duties = []
		for duty in duties :
			if duty == csdefine.COPY_DUTY_MT :
				ct_duties.append( ST.DUTY_MT )
			elif duty == csdefine.COPY_DUTY_DPS :
				ct_duties.append( ST.DUTY_DPS )
			elif duty == csdefine.COPY_DUTY_HEALER :
				ct_duties.append( ST.DUTY_HEALER )
		return ",".join( ct_duties )

#	# ----------------------------------------------------------------
	# functions about requesting enter queue.
	# ----------------------------------------------------------------
	def updateMemberBlacklist( self, playerDBID, blacklist ) :
		"""
		"""
		self.memberBlacklist[playerDBID] = blacklist

	def removeMemberBlacklist( self, playerDBID ) :
		"""
		"""
		if playerDBID in self.memberBlacklist :
			del self.memberBlacklist[playerDBID]

	def updateExpectedCopies( self, copies ) :
		"""
		"""
		self.setExpectedCopies( copies )
		self.broadcastCopiesToMembers()

	def setExpectedCopies( self, copies ) :
		"""
		"""
		self.expectedCopies = tuple( copies )

	def broadcastCopiesToMembers( self ) :
		"""
		<Define method>???
		��ʱ����ӵ�def�ļ���
		"""
		for playerBase in self.membersOnline() :
			playerBase.cell.setExpectedCopies( self.expectedCopies )

	def setMemberDuties( self, duties ) :
		"""
		<For Debug Only>
		"""
		self.memberSelections.clear()
		for k, v in duties.iteritems() :
			self.memberSelections[k] = ( v, False )
		assert( self.membersAssortWithDuties() )

	def setMemberBlacklist( self, blacklistMap ) :
		"""
		<For Debug>
		"""
		self.memberBlacklist.clear()
		for playerDBID, blacklist in blacklistMap.iteritems() :
			self.updateMemberBlacklist( playerDBID, blacklist )

	def headingCopiesExplicit( self ) :
		"""
		"""
		return self.isMatchedActiveTeam() or len( self.expectedCopies ) > 0

	def memberLevelValidForQueue( self, playerDBID, level ) :
		"""
		�ж���ҵĵȼ��Ƿ������
		1�������֮ǰƥ�䵽����ң�����Եȼ��ж�
		2��������¶��飬���߲���ƥ������Ա����
			���ȼ��ж�
		"""
		if self.isMatchedActiveTeam() :
			if self.isFixedMatchedMember( playerDBID ) :
				return True
			else :
				return self.levelOfMatchedCopy <= spaceCopyFormulas.formatCopyLevel( level )
		else :
			return self.initiatedCopyLevel <= spaceCopyFormulas.formatCopyLevel( level )

	def canInitiateSelectingDuties( self ) :
		"""
		��Ҫ���ǣ�
		1���Ƿ����˵��ߣ������ܷ���
		2������ְ��ѡ��󣬶����Ա�����ı䣬��ȡ���˴�ѡ��
		3�����ǵ�������ʱ���쳣������Իظ�ְ��ѡ����һ��ʱ�ӵļ�飬��������ȡ���˴�ѡ��
		"""
		if not self.headingCopiesExplicit() :
			ERROR_MSG( "Team dosen't have expected copies." )
			return False
		elif not self.allMembersAreOnline() :
			ERROR_MSG( "Someone are not online." )
			return False
		else :
			return True

	def __prepareNewDutySelection( self ) :
		"""Player initiate others to select their duties.
		"""
		self.memberSelections.clear()
		self.memberBlacklist.clear()
		self._latestInitiateTime = time.time()

	def timeTillLastInitiate( self ) :
		"""
		Pass time from last initiated to select duties.
		"""
		return time.time() - self._latestInitiateTime

	def initiateSelectingDutiesByCaptain( self, level, captainDuties, copies, expectGuider, blacklist, camp ) :
		"""
		<Define method>
		Initiate members to select duties by captain
		@type		level : UINT8
		@param		level : �ӳ��ĵȼ�
		@type		captainDuties : UINT8_TUPLE
		@param		captainDuties : ���ε�ְ��
		@type		copies : STRING_TUPLE
		@param		copies : ǰ���ĸ�������
		@type		expectGuider : BOOL
		@param		expectGuider : �Ƿ�Ը�ⵣ�ζ�����
		@type		blacklist : STRING_TUPLE
		@param		blacklist : ��ҵĺ�����
		"""
		self._camp = camp 
		self.initiatedCopyLevel = spaceCopyFormulas.formatCopyLevel( level )
		self.__initiateSelectingDutiesByMember( self.getCaptainDBID(), level, captainDuties, copies, expectGuider, blacklist )

	def __initiateSelectingDutiesByMember( self, databaseID, level, duties, copies, expectGuider, blacklist ) :
		"""
		@type		databaseID : DATABASE_ID
		@param		databaseID : ��ҵ�databaseID
		@type		duties : UINT8_TUPLE
		@param		duties : ���ε�ְ��
		@type		copies : STRING_TUPLE
		@param		copies : ǰ���ĸ�������
		@type		expectGuider : BOOL
		@param		expectGuider : �Ƿ�Ը�ⵣ�ζ�����
		@type		blacklist : STRING_TUPLE
		@param		blacklist : ��ҵĺ�����
		"""
		if self.allMembersAreOnline() :
			self.updateExpectedCopies( copies )
			self.__prepareNewDutySelection()
			self.setMatchStatus( csdefine.MATCH_STATUS_TEAM_SELECTING_DUTY )
			self.broadcastMembers( databaseID, csstatus.CTM_INITIATE_SELECTING_DUTY )
			self.onMemberSelectedDuties( databaseID, duties, expectGuider, blacklist, level )
			self.__initiateSelectingDutiesExceptCaptain( copies )             
		else :
			INFO_MSG( "[Team(ID:%s)]:Not all member online." % self.id )
			initiator = self.memberMailboxOfDBID( databaseID )
			initiator.client.onStatusMessage( csstatus.CTM_INITIATE_FAIL_ON_OFFLINE_TEAMMATE, "" )
	

	def __initiateSelectingDutiesExceptCaptain( self, copies ) :
		"""
		"""
		 #Ŀǰ��ͣ��ְ����ж�
		for ( playerId, playerInfo ) in self.member :
			self.__beforeTeamChangeMembers.append( playerInfo["playerBase"] )
			if playerId == self.captainID :
				continue
			
			INFO_MSG( "Notify [%s(id:%i)] to select duties." % ( playerInfo["playerName"], playerId ) )
			playerInfo["playerBase"].initiateSelectingDuties( copies )


	def cancelSelectingDuties( self ) :
		"""
		ȡ��ְ��ѡ��
		"""
		self.setMatchStatus( csdefine.MATCH_STATUS_TEAM_NORMAL )
		for playerBase in self.__beforeTeamChangeMembers :
			if not playerBase : continue
			playerBase.cancelSelectingDuties()
		del self.__beforeTeamChangeMembers[:]

	def onMemberSelectedDuties( self, playerDBID, duties, expectGuider, blacklist, level ) :
		"""
		<Define method>
		��Ҫ���ǣ�
		1�����ǵ�������ʱ���쳣������Իظ�ְ��ѡ����һ��ʱ�ӵļ�飬��������˴�ѡ����Ч
		@type		playerDBID : DATABASE_ID
		@param		playerDBID : ��ҵ�DBID
		@type		duties : UINT8_TUPLE(python tuple)
		@param		duties : ���ѡ���ְ��
		@type		expectGuider : BOOL
		@param		expectGuider : �Ƿ�Ը�ⵣ�ζ�����
		@type		blacklist : STRING_TUPLE(python tuple)
		@param		blacklist : ��ҵĺ�����
		@type		level : UINT8
		@param		level : ��ҵĵȼ�
		"""
		if self.memberLevelValidForQueue( playerDBID, level ) :
			self.updateMemberBlacklist( playerDBID, blacklist )
			self.memberSelections[playerDBID] = ( duties, expectGuider )
			self.broadcastMembers( playerDBID, csstatus.CTM_TEAMMATE_SELECT_DUTY, self.labelOfDuties( duties ) )
			if self.allMembersHaveSelectedDuties() :
				self.cancelSelectingDuties()
				if self.isMatchedActiveTeam() :
					self._joinMatcherAsMatchedAlteredTeam(  )
				else :
					self._joinMatcherAsFresher( )
		else :
			ERROR_MSG("Member(DBID: %s ) level is invalid for queue, initiated level: %i, matched level: %i, member level: %i." % \
				( playerDBID, self.initiatedCopyLevel, self.levelOfMatchedCopy, level ) )
			self.broadcastMembers( playerDBID, csstatus.CTM_TEAMMATE_LEVEL_UNMATCHED )
			self.matchedFixedMembersSetResumed( False )
			self.cancelSelectingDuties()

	def onMemberRefuseToSelectDuty( self, playerDBID ) :
		"""
		<Define method>
		@type		playerDBID : DATABASE_ID
		@param		playerDBID : ��ҵ�DBID
		"""
		if self.isInDutiesSelecting() and self.contain( playerDBID ) :
			self.broadcastMembers( playerDBID, csstatus.CTM_TEAMMATE_SELECT_EMPTY_DUTY )
			self.matchedFixedMembersSetResumed( False )
			self.cancelSelectingDuties()

	def onMemberSelectingDutyTimeout( self, playerDBID ) :
		"""
		<Define method>
		@type		playerDBID : DATABASE_ID
		@param		playerDBID : ��ҵ�DBID
		"""
		if self.isInDutiesSelecting() and self.contain( playerDBID ) and ( playerDBID not in self.memberSelections ) :
			self.broadcastMembers( playerDBID, csstatus.CTM_TEAMMATE_SELECT_DUTY_TIMEOUT )
			self.matchedFixedMembersSetResumed( False )
			self.cancelSelectingDuties()


	def allMembersHaveSelectedDuties( self ) :
		"""
		"""
		return len( self.member ) == len( self.memberSelections )

	def membersDutiesSelectedComplementary( self ) :
		"""��Ա��ѡ���ְ���Ƿ��ǻ�����
		"""
		return copyTeamFormulas.dutiesComplementary( self.memberDutiesSelected() )

	def membersAssortWithDuties( self ) :
		"""
		����Ա��ְ���ǲ��Ƕ�Ӧ�������������·�������¶�Ա����ʱ��
		�¶�Ա��δѡ��ְ�����Ծͻ����ְ�𲻶�Ӧ��
		"""
		if len( self.member ) != len( self.memberSelections ) :
			return False
		else :
			for ( playerId, playerInfo ) in self.member :
				if playerInfo["playerDBID"] not in self.memberSelections :
					return False
			return True

	def _joinMatcherAsFresher( self ) :
		"""
		��δƥ�������ݼ���ƥ�����
		"""
		if not self.allMembersAreOnline() :
			INFO_MSG( "Someone are not online. ID:%s" % str( self.id ) )
			self.broadcastMessage( (), csstatus.CTM_CHEKED_FAIL_ON_OFFLINE_TEAMMATE )
		elif not self.membersDutiesSelectedComplementary() :
			ERROR_MSG( "Members duties conflict. ID:%s, duties:%s" % ( str( self.id ), str( self.memberSelections ) ) )
			self.broadcastMessage( (), csstatus.CTM_ON_DUTY_CHEKED_CONFLICT )
		else :
			INFO_MSG( "OK, team is eligible to enter matcher queue. ID:%s" % str( self.id ) )
			self.broadcastMessage( (), csstatus.CTM_ON_DUTY_SELECTION_CHEKED_PASS )
			copyTeamQueuerMgr = BigWorld.globalData["copyTeamQueuerMgr"]
			copyTeamQueuerMgr.onReceiveJoinRequest( self,										# �Ŷ��ߵ�mailbox
										self.initiatedCopyLevel,					# �Ŷ��ߵȼ�
										self.freshMembers(),						# �Ŷ����ڲ���Ա������
										self.expectedCopies,						# �Ŷ�����ǰ���ĸ���
										self.blacklistOfMembers(),					# �Ŷ��ߵĺ������б�
										self._camp,                                  # ��Ӫ
										False,										# �Ƿ�����ļ��
										)

	def _joinMatcherAsMatchedAlteredTeam( self ) :
		"""
		ƥ����飬���Ƿ�������Ա��ְ��ƥ������������Ҫ������
		ѡ��ְ������������ӿڼ���ƥ�����
		"""
		if not self.allMembersAreOnline() :
			INFO_MSG( "Someone are not online. ID:%s" % str( self.id ) )
			self.broadcastMessage( (), csstatus.CTM_CHEKED_FAIL_ON_OFFLINE_TEAMMATE )
		elif not self.membersDutiesSelectedComplementary() :
			ERROR_MSG( "Members duties conflict. ID:%s, duties:%s" % ( str( self.id ), str( self.memberSelections ) ) )
			self.broadcastMessage( (), csstatus.CTM_ON_DUTY_CHEKED_CONFLICT )
		else :
			INFO_MSG( "OK, team is eligible to enter matcher queue. ID:%s" % str( self.id ) )
			self.broadcastMessage( (), csstatus.CTM_ON_DUTY_SELECTION_CHEKED_PASS )
			copyTeamQueuerMgr = BigWorld.globalData["copyTeamQueuerMgr"]
			copyTeamQueuerMgr.onReceiveJoinRequest( self,										# �Ŷ��ߵ�mailbox
										self.levelOfMatchedCopy,					# �Ŷ��ߵȼ�
										self.freshMembers(),						# �Ŷ����ڲ���Ա������
										(self.labelOfMatchedCopy,),					# �Ŷ�����ǰ���ĸ���
										self.blacklistOfMembers(),					# �Ŷ��ߵĺ������б�
										self._camp,                                  # ��Ӫ
										True,										# �Ƿ�����ļ��									
										)

	def freshMembers( self ) :
		"""
		���ɽ����ŶӶ�����Ҫ�ĳ�Ա����
		"""
		members = []
		for playerId, playerInfo in self.member :
			selection = self.memberSelections[ playerInfo["playerDBID"] ]				# ���û�ж�Ӧ�����ݣ�����������
			members.append( ( playerInfo["playerBase"], playerInfo["playerName"], selection[0], selection[1] ) )	# ( mailbox, name, duties, expectGuider )
			self.__beforeTeamChangeMembers.append( playerInfo["playerBase"] )
		return tuple( members )

	def blacklistOfMembers( self ) :
		"""
		������ҵĺ������б�
		"""
		blacklist = set()
		for l in self.memberBlacklist.itervalues() :
			blacklist.update( l )
		return tuple( blacklist )

	def memberDutiesSelected( self ) :
		"""
		���ѡ���ְ��
		"""
		duties = {}
		for k, v in self.memberSelections.iteritems() :
			duties[k] = v[0]
		return duties

	def onJoinCopyMatcherQueue( self ) :
		"""
		<Define method>
		"""
		INFO_MSG( "[Team(ID:%s)]:Join copy matcher callback." % ( self.id ) )
		self.setMatchStatus( csdefine.MATCH_STATUS_TEAM_MATCHING )
		for playerBase in self.membersOnline() :
			playerBase.onJoinCopyMatcherQueue()

	def onRejoinCopyMatcherQueue( self ) :
		"""
		<Define method>
		"""
		INFO_MSG( "[Team(ID:%s)]: Rejoin copy matcher." % ( self.id, ) )
		self.setMatchStatus( csdefine.MATCH_STATUS_TEAM_MATCHING )
		for playerBase in self.membersOnline() :
			playerBase.onRejoinCopyMatcherQueue()

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
		INFO_MSG( "[Team(ID:%s)]: Enter confirming match, matched group %i." % ( self.id, groupID ) )
		self.matchedGroupID = groupID
		self.setMatchStatus( csdefine.MATCH_STATUS_TEAM_MATCHED )
		for playerBase in self.membersOnline() :
			playerBase.enterConfirmingCopyMatched( groupID, dutyMap, copyLabel, copyLevel, bossesTotal, bossesKilled, copies )


#	# ----------------------------------------------------------------
	# about leave matcher queue
	# ----------------------------------------------------------------
	def tmi_onMemberJoin( self, playerDBID, playerID ) :
		"""
		��ҼӶ�
		������������TeamEntity�е��ô˽ӿ�
		��Ҫע�⣺������������Ŷӣ����ö���ӹ������Ƴ�
				�������ѡ��ְ��ȡ��ѡ��
				�������ȷ��ְ��ȡ��ȷ��
		"""
		if self.isMatchingInQueue() :
			self.__broadcastMessageToPlayers( self.__beforeTeamChangeMembers, csstatus.CTM_DUTY_SELECTION_FAILED )
			self.leaveCopyMatcherQueue()
		elif self.isInDutiesSelecting() :
			self.matchedFixedMembersSetResumed( False )
			self.__broadcastMessageToPlayers( self.__beforeTeamChangeMembers, csstatus.CTM_DUTY_SELECTION_FAILED )
			self.cancelSelectingDuties()


	def tmi_onMemberLeave( self, playerDBID, playerID ) :
		"""
		������
		������������TeamEntity�е��ô˽ӿ�
		"""
		self.removeMemberBlacklist( playerDBID )
		self._updateMatchedDutyOnMemberLeave( playerID )
		if self.isMatchingInQueue() :
			self.__broadcastMessageToPlayers( self.__beforeTeamChangeMembers, csstatus.CTM_DUTY_SELECTION_FAILED )
			self.leaveCopyMatcherQueue()
		elif self.isInDutiesSelecting() :
			self.matchedFixedMembersSetResumed( False )
			self.__broadcastMessageToPlayers( self.__beforeTeamChangeMembers, csstatus.CTM_DUTY_SELECTION_FAILED )
			self.cancelSelectingDuties()
	

	def tmi_onMemberLogout( self, playerDBID ) :
		"""
		�������
		������������TeamEntity�е��ô˽ӿ�
		"""
		if self.isMatchingInQueue() :
			self.__broadcastMessageToPlayers( self.__beforeTeamChangeMembers, csstatus.CTM_DUTY_SELECTION_FAILED )
			self.leaveCopyMatcherQueue()
		elif self.isInDutiesSelecting() :
			self.matchedFixedMembersSetResumed( False )
			self.__broadcastMessageToPlayers( self.__beforeTeamChangeMembers, csstatus.CTM_DUTY_SELECTION_FAILED )
			self.cancelSelectingDuties()

	def tmi_onMemberLogon( self, oldEntityID, newEntityID, playerDBID ) :
		"""
		����������ϣ���Ҫ��
		1������ƥ����Ϣ
		2��ˢ���Ƿ��ڸ����ı��
		"""
		if self.isMatchedActiveTeam() :
			self._updateMatchedDutyOnMemberLogon( oldEntityID, newEntityID )
			playerBase = self.memberMailboxOfDBID( playerDBID )
			playerBase.cell.onMatchedCopyTeam( self.levelOfMatchedCopy, self.labelOfMatchedCopy )
			playerBase.client.updateMatchedCopyInfo( self.labelOfMatchedCopy, self.levelOfMatchedCopy, self.matchedMembersDuty )

	def tmi_onChangeCaptain( self, newCaptainID ) :
		"""
		�ӳ��ı�
		"""
		if self.isInDutiesSelecting() :
			self.matchedFixedMembersSetResumed( False )
			self.cancelSelectingDuties()
			self.broadcastMessage( (), csstatus.CTM_DUTY_SELECTION_FAILED )


	def tmi_onDisband( self ) :
		"""
		�����ɢ
		��������ǰ���ã���TeamEntity�е��ô˽ӿ�
		"""
		if self.isMatchingInQueue() :
			self.__broadcastMessageToPlayers( self.__beforeTeamChangeMembers, csstatus.CTM_DUTY_SELECTION_FAILED )
			self.leaveCopyMatcherQueue()
		elif self.isInDutiesSelecting() :
			self.__broadcastMessageToPlayers( self.__beforeTeamChangeMembers, csstatus.CTM_DUTY_SELECTION_FAILED )
			self.cancelSelectingDuties()


	def leaveCopyMatcherQueue( self ) :
		"""
		���ŶӶ����Ƴ�
		"""
		copyTeamQueuerMgr = BigWorld.globalData["copyTeamQueuerMgr"]
		copyTeamQueuerMgr.removeQueuer( self.id, csstatus.CTM_LEAVE_QUEUE_IN_COMMON )
		self.setMatchStatus( csdefine.MATCH_STATUS_TEAM_NORMAL )			# ���Ȼص���������ǰ����Ϊ�ص���ͨ״̬

	def onLeaveCopyMatcherQueue( self, reason ) :
		"""
		<Define method>
		@type		reason : INT32
		@param		reason : �뿪��ԭ����csstatus�ж��壩
		"""
		INFO_MSG( "[Team(ID:%s)]:Leave copy matcher callback, reason: %s" % ( self.id, reason ) )
		self.setMatchStatus( csdefine.MATCH_STATUS_TEAM_NORMAL )
		for playerBase in self.membersOnline() :
			playerBase.onLeaveCopyMatcherQueue( reason )



	# ----------------------------------------------------------------
	# handle after matched successfully
	# ----------------------------------------------------------------


	# ----------------------------------------------------------------
	# functions teleport members in or out matched copy.
	# ----------------------------------------------------------------
	def teloportMemberToMatchedCopy( self, playerDBID ) :
		"""
		"""
		if self.matchedCopy == None :
			ERROR_MSG( "[Team(ID:%s)]: matched copy is None." % ( self.id, ) )
		elif self.contain( playerDBID ) :
			player = self.memberMailboxOfDBID( playerDBID )
			player.gotoSpace( self.matchedCopy, (0, 0, 0), (0, 0, 0) )


	# ----------------------------------------------------------------
	# functions about voting to kick out teammate.
	# ----------------------------------------------------------------


	# ----------------------------------------------------------------
	# functions about requesting leave queue.
	# ----------------------------------------------------------------
