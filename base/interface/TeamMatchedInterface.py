# -*- coding:gb18030 -*-

import time
import BigWorld
import csdefine
import csstatus
import csconst
import ShareTexts as ST
from bwdebug import ERROR_MSG, INFO_MSG

VOTE_PASS = 1										# ͶƱͨ��
VOTE_LOSE = -1										# ͶƱ��ͨ��
VOTE_PENDING = 0									# ͶƱδȷ��

class TeamMatchedInterface :

	def __init__( self ) :
		self.matchedMembersDuty = {}				# ���ƥ�䵽��ְ��{playerID:duty,}��ƥ��Ķ��������������Ч��
		self.levelOfMatchedCopy = 0					# ƥ�丱���ĵȼ����������Ŷӳ��ĸı���ı䣩
		self.labelOfMatchedCopy = ""				# ƥ��ĸ�������
		self.isMatchedTeam = False					# �Ƿ���ƥ��Ķ���
		self.isRaidFinished = False					# �����Ƿ��Ѵ���
		self.kickableTime = 0						# �´ο�ͶƱ���˵�ʱ��
		self.memberIDKicked = 0						# ��ͶƱ�޳��ߵ�ID
		self.kickingVoteFeedback = {}				# ���˱���ظ���{dbid:True/False}
		self._camp = 0                              # ��Ӫ

	def isMatchedActiveTeam( self ) :
		"""
		ƥ������Ȼ��Ч�ĸ�������
		"""
		return self.isMatchedTeam and not self.isRaidFinished

	def turnToMatchedTeam( self, copyLabel, copyLevel, memberToDuty ) :
		"""
		<Define method>
		������ת��Ϊƥ�����
		"""
		self.__updateMatchedDuty( memberToDuty )			# ���ƥ�䵽��ְ��ƥ��Ķ��������������Ч��
		self.levelOfMatchedCopy = copyLevel					# ƥ�丱���ĵȼ����������Ŷӳ��ĸı���ı䣩
		self.labelOfMatchedCopy = copyLabel					# ƥ��ĸ�������
		self.isMatchedTeam = True
		self.isRaidFinished = False
		self._updateKickableTime()							# �ɹ�ƥ��Ķ��飬��������������
		#self.__broadcastMatchedInfoToMembers()

	def __updateMatchedDuty( self, memberToDuty ) :
		"""
		"""
		self.matchedMembersDuty.clear()
		self.matchedMembersDuty.update( memberToDuty )
		#
		#for memberID, duty in memberToDuty.iteritems() :
		#	dbid = self.memberDBIDOfID( memberID )
		#	if dbid is None :
		#		ERROR_MSG( "[MatchedTeamInterface(ID:%i)]: Player(ID: %i) is not in team." % ( self.id, memberID ) )
		#		continue
		#	self.matchedMembersDuty[dbid] = duty

	def _updateMatchedDutyOnMemberLogon( self, oldEntityID, newEntityID ) :
		"""
		������ߺ�entityID�����ı䣬����Ҫ������ƥ���ְ��
		"""
		if oldEntityID in self.matchedMembersDuty :
			self.matchedMembersDuty[newEntityID] = self.matchedMembersDuty.pop( oldEntityID )

	def _updateMatchedDutyOnMemberLeave( self, memberID ) :
		"""
		�����Ӻ���ְ���Ƴ�
		"""
		if memberID in self.matchedMembersDuty :
			del self.matchedMembersDuty[memberID]

	def __broadcastMatchedInfoToMembers( self ) :
		"""
		"""
		for memberBase in self.membersOnline() :
			memberBase.cell.onMatchedCopyTeam( self.levelOfMatchedCopy, self.labelOfMatchedCopy )
			memberBase.client.updateMatchedCopyInfo( self.labelOfMatchedCopy, self.levelOfMatchedCopy, self.matchedMembersDuty )

	def absorbMatchedMembers( self, members ) :
		"""
		<Define method>
		��ƥ�䵽����Ҽ�����飬������ļ��������
		@type		members : ARRAY OF MAILBOX
		@param		members : �³�Ա����
		"""
		if not self.isMatchedActiveTeam() :
			ERROR_MSG( "[MatchedTeam(id:%i)]: I am not matched active team." % self.id )
		elif (len( self.member ) + len( members )) > csconst.TEAM_MEMBER_MAX :
			ERROR_MSG( "[MatchedTeam(id:%i)]: Team will overflow after absorbing %i members, current amount is %i." % \
				( self.id, len( members ), len( self.member ) ) )
		else :
			for member in members :											# �������˼������
				member.joinMatchedCopyTeam( self.captainID, self )

	def turnToNormalTeam( self ) :
		"""
		<Define method>
		������ת��Ϊ��ͨ����
		"""
		self.matchedMembersDuty.clear()
		self.levelOfMatchedCopy = 0
		self.labelOfMatchedCopy = ""
		self.isMatchedTeam = False

	def membersAssortWithFixedDuties( self ) :
		"""
		����Ա��ְ���ǲ��Ƕ�Ӧ�������������·�������¶�Ա����ʱ��
		�¶�Ա��δѡ��ְ�����Ծͻ����ְ�𲻶�Ӧ��
		"""
		if len( self.member ) != len( self.matchedMembersDuty ) :
			return False
		else :
			for ( playerId, playerInfo ) in self.member :
				playerBase = playerInfo["playerBase"]
				if playerBase is None or playerBase.id not in self.matchedMembersDuty :
					return False
			return True

	def isFixedMatchedMember( self, playerDBID ) :
		"""
		�ж�����Ƿ���ƥ�䵽�ĳ�Ա
		"""
		member = self.memberMailboxOfDBID( playerDBID )
		return member and member.id in self.matchedMembersDuty

	def resumeHaltedRaidBy( self, initiatorDBID, teamID, camp ) :
		"""
		<Define method>
		��ȱ��������Ŷ�
		�˹��ܻ�û���
		@type		initiatorDBID : DATABASE_ID
		@param		initiatorDBID : ��ҵ�DBID
		"""
		if not self.contain( initiatorDBID ) :
			ERROR_MSG( "[Team(ID:%i)]: Initiator(DBID %i) requesting to rejoin matcher is not my member." % ( self.id, initiatorDBID ) )
		elif not self.allMembersAreOnline() :
			INFO_MSG( "[Team(ID:%s)]:Not all members online." % self.id )
		elif self.isMatchedActiveTeam() :       #����δ������������ļ����
			self._camp = camp
			self._joinMatcherAsMatchedTeam( teamID, camp )
			"""
			if self.membersAssortWithFixedDuties() :
				self._joinMatcherAsMatchedTeam()
			else :
				self._prepairDutiesSelectionForHaltedRaid()
				self.initiateNewDutiesSelection()
			"""

	def _prepairDutiesSelectionForHaltedRaid( self ) :
		"""
		Ϊ���ű��жϵĸ�����׼��
		"""
		for member in self.membersOnline() :
			if member.id in self.matchedMembersDuty :
				member.cell.setHaltedRaidResumed( True )								# �����ƥ��ĳ�Ա�����������ű�ǣ������ű�ǿ��������������¼���
			else :
				member.cell.setExpectedCopies( (self.labelOfMatchedCopy,) )				# ���������ĳ�Ա��������ƥ��ĸ���

	def _joinMatcherAsMatchedTeam( self, teamID, camp ) :
		"""
		"""
		if not self.allMembersAreOnline() :
			INFO_MSG( "Someone are not online. ID:%s" % str( self.id ) )
		else :
			INFO_MSG( "OK, team is eligible to enter matcher queue. ID:%s" % str( self.id ) )
			try :			
				copyTeamQueuerMgr = BigWorld.globalData["copyTeamQueuerMgr"]
				team = BigWorld.entities[teamID]
				members = []            #[(mailbox, name, duites, expectguider ),]
				for member in team.member :
					ID = member[0]
					DBID = member[1]['playerDBID']
					mailbox = member[1]['playerBase']
					name = member[1]['playerName']
					duties = [csdefine.COPY_DUTY_DPS,]
					expectGuider = False
					copies = [self.labelOfMatchedCopy,]
					members.append((mailbox, name, duties, expectGuider))
				copyTeamQueuerMgr.onReceiveJoinRequest( self,										# �Ŷ��ߵ�mailbox
											self.levelOfMatchedCopy,					# �Ŷ��ߵȼ�
											members,								# �����Ա����
											(self.labelOfMatchedCopy,),					# �Ŷ�����ǰ���ĸ����������ǰ�·���������Ը����ǹ̶���ƥ�丱����
											self.blacklistOfMembers(),					# ����ĺ������б�
											camp,                                  		# ��Ӫ
											True,										# �Ƿ�����ļ��									
											)
			except KeyError, errstr :
				ERROR_MSG( "copyTeamQueuerMgr is not in globalData." )

	def matchedFixedMembersSetResumed( self, resumed ) :
		"""
		"""
		for member in self.membersOnline() :
			if member.id in self.matchedMembersDuty :
				member.cell.setHaltedRaidResumed( resumed )

	def matchedMembers( self ) :
		"""
		���ɽ����ŶӶ�����Ҫ�ĳ�Ա����
		"""
		members = []
		for playerId, playerInfo in self.member :
			duty = self.matchedMembersDuty[ playerInfo["playerBase"].id ]				# ���û�ж�Ӧ�����ݣ�����������
			members.append( ( playerInfo["playerBase"], playerInfo["playerName"], (duty,), True ) )	# ( mailbox, name, duties, expectGuider )
		return tuple( members )

	def onRematchedAsRecruiter( self, groupID ) :
		"""
		<Define method>
		@type		groupID : UID
		@param		groupID : ƥ��С���ID
		��ļ�߼��뵽ƥ����
		"""
		INFO_MSG( "[Team(ID:%s)]: Rematched group %i." % ( self.id, groupID ) )
		self.matchedGroupID = groupID
		self.setMatchStatus( csdefine.MATCH_STATUS_TEAM_MATCHED )
		for playerBase in self.membersOnline() :
			playerBase.onRematchedAsRecruiter( groupID )

	def onRematchedCompleted( self, memberToDuty ) :
		"""
		<Define method>
		�����ٴ�ƥ�������ְ��
		@type	memberToDuty : PY_DICT
		@param	memberToDuty : ��ƥ���ְ��
		"""
		for playerBase in self.membersOnline() :
			playerBase.client.updateMatchedCopyInfo( self.labelOfMatchedCopy, self.levelOfMatchedCopy, memberToDuty )
			if not self.isFixedMatchedMember( self.memberDBIDOfID(playerBase.id) ) :
				playerBase.cell.onMatchedCopyTeam( self.levelOfMatchedCopy, self.labelOfMatchedCopy )
		self.__updateMatchedDuty( memberToDuty )
		self._updateKickableTime()							# �ɹ�ƥ��Ķ��飬��������������


#	# kick out teammate-----------------------------------------------
	# kick out teammate operations
	# ----------------------------------------------------------------
	def _updateKickableTime( self ) :
		"""
		�����´ο�������ʱ��
		"""
		self.kickableTime = time.time() + csdefine.TIME_LIMIT_OF_KICKING_INTERVAL

	def kickingIsCooling( self ) :
		"""
		������ʱ��������ȴ
		"""
		return self._timeTillKickable() > 0

	def _timeTillKickable( self ) :
		"""
		������˻�ʣ���
		"""
		return self.kickableTime - time.time()

	def __strsformat( self, secs ):
		"""
		������ת��ΪXX��XX��
		"""
		m, s = divmod( secs, 60 )
		if m > 0:
			return "%i%s%i%s"%(m, ST.CHTIME_MINUTE, s, ST.CHTIME_SECOND)
		else:
			return "%i%s"%(s, ST.CHTIME_SECOND)

	def _prepairForKickingVote( self ) :
		"""
		"""
		self.kickingVoteFeedback.clear()

	def _recordKickingVote( self, playerID, agree ) :
		"""
		"""
		self.kickingVoteFeedback[playerID] = agree

	def _agreeKickingAmount( self ) :
		"""
		"""
		return self.kickingVoteFeedback.values().count( True )

	def _judgeVote( self, total, voted, agree ) :
		"""
		��ͶƱ��������о�
		��������ͬ�⣬ͨ��
		�������Ϸ��ԣ���ͨ��
		��΢ƫ��һ�²�ͨ�������������4����ͶƱ�������������Ͷ��
		����Ʊ����ͨ���������������Ͷ��ͬ�⣬������ҪһƱ
		ͬ���ͨ����
		return: 0��δȷ����1��ͨ����-1����ͨ��
		"""
		if agree > total / 2.0 :
			return VOTE_PASS
		elif ( voted - agree ) >= total / 2.0 :
			return VOTE_LOSE
		else :
			return VOTE_PENDING

	def initiateVoteForKickingMember( self, initiatorID, suffererID, reason ) :
		"""
		<Define method>
		@type	initiatorID : OBJECT_ID
		@param	initiatorID : ͶƱ���˷����ߵ�ID
		@type	suffererID : OBJECT_ID
		@param	suffererID : ���޳������ID
		@type	reason : STRING
		@param	reason : �޳�����
		"""
		if not self.isMatchedTeam :
			ERROR_MSG( "[Team(ID:%i)]: Only matched team supports voting to kick member out." % self.id )
		elif self.kickingIsCooling() :
			INFO_MSG( "[Team(ID:%i)]: It will be able to kick member out in %.1f second." % ( self.id, self._timeTillKickable() ) )
			initiator = self.memberMailboxOfID( initiatorID )
			if initiator:
				initiator.client.onStatusMessage( csstatus.CTM_CANT_KICK_TEAMMATE_IN_COOLING, "(\'%s\',)"%self.__strsformat(self._timeTillKickable()) )
		elif self.containID( initiatorID ) and self.containID( suffererID ) :
			self._prepairForKickingVote()
			self.memberIDKicked = suffererID
			for member in self.membersOnline() :
				if member.id != initiatorID and member.id != suffererID :
					member.client.notifyToVoteForKickingTeammate( initiatorID, suffererID, reason )
			self.memberVoteForKicking( initiatorID, True )						# ��ȷ��������ͬ��
		else :
			ERROR_MSG("Team(ID:%i) not contain member(ID:%i) or member(ID:%i)" % ( self.id ,initiatorID, suffererID ))

	def memberVoteForKicking( self, playerID, agree ) :
		"""
		<Define method>
		@type	playerID : OBJECT_ID
		@param	playerID : ͶƱ��ҵ�ID
		@type	agree : BOOL
		@param	agree : �Ƿ�ͬ��
		"""
		if not self.isMatchedTeam :
			ERROR_MSG( "[Team(ID:%i)]: Only matched team supports voting to kick out member." % self.id )
			return
		self._recordKickingVote( playerID, agree )
		result = self.checkForKickingVote()
		if result == VOTE_PASS :												# ͶƱͨ��
			sufferer = self.memberMailboxOfID( self.memberIDKicked )
			if sufferer :														# �޳�һ�����ߵĶ���
				sufferer.cell.leaveTeamOnKicked()
			elif self.containID( self.memberIDKicked ) :						# �޳�һ�����ߵĶ���
				self.leave( self.memberIDKicked, self.memberIDKicked )
			self.cancelVoteForKicking()
			self._updateKickableTime()											# ͶƱ����ͨ����Ҫ����ʱ������ٴ�ͶƱ		
			self._prepairForKickingVote()	
		elif result == VOTE_LOSE :												# ͶƱ��ͨ��
			INFO_MSG( "[Team(ID:%i)]: Vote for kicking %i is not pass." % ( self.id, self.memberIDKicked ) )
			self.cancelVoteForKicking()
			self._prepairForKickingVote()

	def checkForKickingVote( self ) :
		"""
		����ͶƱ������
		��������ͶƱ����Ч�����޳��Ķ��󲻻����ͶƱ
		return: 0��δȷ����1��ͨ����-1����ͨ��
		"""
		# ��������һ������Ϊ���޳��߲�����ͶƱ
		return self._judgeVote( len( self.member )-1, len( self.kickingVoteFeedback ), self._agreeKickingAmount() )

	def cancelVoteForKicking( self ) :
		"""
		"""
		for member in self.membersOnline() :
			if member.id != self.memberIDKicked and member.id not in self.kickingVoteFeedback :
				member.client.cancelVoteForKicking()


#	# raid over ----------------------------------------------------
	# raid over
	# ----------------------------------------------------------------
	def onMatchedCopyClosed( self ) :
		"""
		<Define method>
		�����ر�ʱ����
		"""
		INFO_MSG( "[Team(ID:%i)]: matched copy is closed." % self.id )
		if self.isMatchedActiveTeam() :
			self.onMatchedRaidFinished()

	def onMatchedRaidFinished( self ) :
		"""
		<Define method>
		����Raid����ʱ����
		"""
		INFO_MSG( "[Team(ID:%i)]: raid of matched copy is finished." % self.id )
		self.clearQueueingOnRaidOver()
		if self.isMatchedActiveTeam() :
			self.turnToNormalTeam()
			self.isRaidFinished = True
			for member in self.membersOnline() :
				member.cell.onMatchedRaidFinished()

	def clearQueueingOnRaidOver( self ) :
		"""
		"""
		if self.isInDutiesSelecting() :
			self.cancelSelectingDuties()
			self.matchedFixedMembersSetResumed( False )
		elif self.isMatchingInQueue() :
			self.leaveCopyMatcherQueue()
		elif self.isMatchedInQueue() :
			mgr = BigWorld.globalData["copyTeamQueuerMgr"]
			mgr.onMatchedQueuerCollapse( self.matchedGroupID, self.id )
