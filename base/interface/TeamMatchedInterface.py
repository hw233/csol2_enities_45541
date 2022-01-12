# -*- coding:gb18030 -*-

import time
import BigWorld
import csdefine
import csstatus
import csconst
import ShareTexts as ST
from bwdebug import ERROR_MSG, INFO_MSG

VOTE_PASS = 1										# 投票通过
VOTE_LOSE = -1										# 投票不通过
VOTE_PENDING = 0									# 投票未确定

class TeamMatchedInterface :

	def __init__( self ) :
		self.matchedMembersDuty = {}				# 玩家匹配到的职责{playerID:duty,}（匹配的队伍这个参数才有效）
		self.levelOfMatchedCopy = 0					# 匹配副本的等级（不会随着队长的改变而改变）
		self.labelOfMatchedCopy = ""				# 匹配的副本名称
		self.isMatchedTeam = False					# 是否是匹配的队伍
		self.isRaidFinished = False					# 副本是否已打完
		self.kickableTime = 0						# 下次可投票踢人的时间
		self.memberIDKicked = 0						# 被投票剔除者的ID
		self.kickingVoteFeedback = {}				# 踢人表决回复：{dbid:True/False}
		self._camp = 0                              # 阵营

	def isMatchedActiveTeam( self ) :
		"""
		匹配且依然有效的副本队伍
		"""
		return self.isMatchedTeam and not self.isRaidFinished

	def turnToMatchedTeam( self, copyLabel, copyLevel, memberToDuty ) :
		"""
		<Define method>
		将队伍转变为匹配队伍
		"""
		self.__updateMatchedDuty( memberToDuty )			# 玩家匹配到的职责（匹配的队伍这个参数才有效）
		self.levelOfMatchedCopy = copyLevel					# 匹配副本的等级（不会随着队长的改变而改变）
		self.labelOfMatchedCopy = copyLabel					# 匹配的副本名称
		self.isMatchedTeam = True
		self.isRaidFinished = False
		self._updateKickableTime()							# 成功匹配的队伍，不允许立刻踢人
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
		玩家上线后entityID发生改变，所以要更新其匹配的职责
		"""
		if oldEntityID in self.matchedMembersDuty :
			self.matchedMembersDuty[newEntityID] = self.matchedMembersDuty.pop( oldEntityID )

	def _updateMatchedDutyOnMemberLeave( self, memberID ) :
		"""
		玩家离队后将其职责移除
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
		将匹配到的玩家加入队伍，用于招募队伍组人
		@type		members : ARRAY OF MAILBOX
		@param		members : 新成员名称
		"""
		if not self.isMatchedActiveTeam() :
			ERROR_MSG( "[MatchedTeam(id:%i)]: I am not matched active team." % self.id )
		elif (len( self.member ) + len( members )) > csconst.TEAM_MEMBER_MAX :
			ERROR_MSG( "[MatchedTeam(id:%i)]: Team will overflow after absorbing %i members, current amount is %i." % \
				( self.id, len( members ), len( self.member ) ) )
		else :
			for member in members :											# 把其他人加入队伍
				member.joinMatchedCopyTeam( self.captainID, self )

	def turnToNormalTeam( self ) :
		"""
		<Define method>
		将队伍转变为普通队伍
		"""
		self.matchedMembersDuty.clear()
		self.levelOfMatchedCopy = 0
		self.labelOfMatchedCopy = ""
		self.isMatchedTeam = False

	def membersAssortWithFixedDuties( self ) :
		"""
		检查队员和职责是不是对应得起来，例如半路队伍有新队员加入时，
		新队员还未选过职责，所以就会出现职责不对应。
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
		判断玩家是否是匹配到的成员
		"""
		member = self.memberMailboxOfDBID( playerDBID )
		return member and member.id in self.matchedMembersDuty

	def resumeHaltedRaidBy( self, initiatorDBID, teamID, camp ) :
		"""
		<Define method>
		残缺副本组队排队
		此功能还没完成
		@type		initiatorDBID : DATABASE_ID
		@param		initiatorDBID : 玩家的DBID
		"""
		if not self.contain( initiatorDBID ) :
			ERROR_MSG( "[Team(ID:%i)]: Initiator(DBID %i) requesting to rejoin matcher is not my member." % ( self.id, initiatorDBID ) )
		elif not self.allMembersAreOnline() :
			INFO_MSG( "[Team(ID:%s)]:Not all members online." % self.id )
		elif self.isMatchedActiveTeam() :       #副本未结束并且是招募队伍
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
		为重排被中断的副本作准备
		"""
		for member in self.membersOnline() :
			if member.id in self.matchedMembersDuty :
				member.cell.setHaltedRaidResumed( True )								# 如果是匹配的成员，则设置重排标记，有重排标记可跳过副本进入记录检查
			else :
				member.cell.setExpectedCopies( (self.labelOfMatchedCopy,) )				# 如果是新组的成员，则设置匹配的副本

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
				copyTeamQueuerMgr.onReceiveJoinRequest( self,										# 排队者的mailbox
											self.levelOfMatchedCopy,					# 排队者等级
											members,								# 队伍成员数据
											(self.labelOfMatchedCopy,),					# 排队者欲前往的副本（由于是半路副本，所以副本是固定的匹配副本）
											self.blacklistOfMembers(),					# 队伍的黑名单列表
											camp,                                  		# 阵营
											True,										# 是否是招募者									
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
		生成进入排队队列需要的成员数据
		"""
		members = []
		for playerId, playerInfo in self.member :
			duty = self.matchedMembersDuty[ playerInfo["playerBase"].id ]				# 如果没有对应的数据，就让它报错
			members.append( ( playerInfo["playerBase"], playerInfo["playerName"], (duty,), True ) )	# ( mailbox, name, duties, expectGuider )
		return tuple( members )

	def onRematchedAsRecruiter( self, groupID ) :
		"""
		<Define method>
		@type		groupID : UID
		@param		groupID : 匹配小组的ID
		招募者加入到匹配组
		"""
		INFO_MSG( "[Team(ID:%s)]: Rematched group %i." % ( self.id, groupID ) )
		self.matchedGroupID = groupID
		self.setMatchStatus( csdefine.MATCH_STATUS_TEAM_MATCHED )
		for playerBase in self.membersOnline() :
			playerBase.onRematchedAsRecruiter( groupID )

	def onRematchedCompleted( self, memberToDuty ) :
		"""
		<Define method>
		更新再次匹配后的玩家职责
		@type	memberToDuty : PY_DICT
		@param	memberToDuty : 新匹配的职责
		"""
		for playerBase in self.membersOnline() :
			playerBase.client.updateMatchedCopyInfo( self.labelOfMatchedCopy, self.levelOfMatchedCopy, memberToDuty )
			if not self.isFixedMatchedMember( self.memberDBIDOfID(playerBase.id) ) :
				playerBase.cell.onMatchedCopyTeam( self.levelOfMatchedCopy, self.labelOfMatchedCopy )
		self.__updateMatchedDuty( memberToDuty )
		self._updateKickableTime()							# 成功匹配的队伍，不允许立刻踢人


#	# kick out teammate-----------------------------------------------
	# kick out teammate operations
	# ----------------------------------------------------------------
	def _updateKickableTime( self ) :
		"""
		设置下次可再踢人时间
		"""
		self.kickableTime = time.time() + csdefine.TIME_LIMIT_OF_KICKING_INTERVAL

	def kickingIsCooling( self ) :
		"""
		可踢人时间正在冷却
		"""
		return self._timeTillKickable() > 0

	def _timeTillKickable( self ) :
		"""
		离可踢人还剩多久
		"""
		return self.kickableTime - time.time()

	def __strsformat( self, secs ):
		"""
		将秒数转换为XX分XX秒
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
		对投票结果进行判决
		半数以上同意，通过
		半数以上反对，不通过
		稍微偏向一下不通过，例如队伍有4个人投票，如果有两个先投了
		反对票，则不通过，如果有两个先投了同意，则还再需要一票
		同意才通过。
		return: 0，未确定；1，通过；-1，不通过
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
		@param	initiatorID : 投票踢人发起者的ID
		@type	suffererID : OBJECT_ID
		@param	suffererID : 被剔除对象的ID
		@type	reason : STRING
		@param	reason : 剔除理由
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
			self.memberVoteForKicking( initiatorID, True )						# 先确定发起者同意
		else :
			ERROR_MSG("Team(ID:%i) not contain member(ID:%i) or member(ID:%i)" % ( self.id ,initiatorID, suffererID ))

	def memberVoteForKicking( self, playerID, agree ) :
		"""
		<Define method>
		@type	playerID : OBJECT_ID
		@param	playerID : 投票玩家的ID
		@type	agree : BOOL
		@param	agree : 是否同意
		"""
		if not self.isMatchedTeam :
			ERROR_MSG( "[Team(ID:%i)]: Only matched team supports voting to kick out member." % self.id )
			return
		self._recordKickingVote( playerID, agree )
		result = self.checkForKickingVote()
		if result == VOTE_PASS :												# 投票通过
			sufferer = self.memberMailboxOfID( self.memberIDKicked )
			if sufferer :														# 剔除一个在线的队友
				sufferer.cell.leaveTeamOnKicked()
			elif self.containID( self.memberIDKicked ) :						# 剔除一个掉线的队友
				self.leave( self.memberIDKicked, self.memberIDKicked )
			self.cancelVoteForKicking()
			self._updateKickableTime()											# 投票踢人通过后要隔段时间才能再次投票		
			self._prepairForKickingVote()	
		elif result == VOTE_LOSE :												# 投票不通过
			INFO_MSG( "[Team(ID:%i)]: Vote for kicking %i is not pass." % ( self.id, self.memberIDKicked ) )
			self.cancelVoteForKicking()
			self._prepairForKickingVote()

	def checkForKickingVote( self ) :
		"""
		踢人投票结果检查
		半数以上投票才有效，被剔除的对象不会参与投票
		return: 0，未确定；1：通过；-1：不通过
		"""
		# 总人数减一，是因为被剔除者不参与投票
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
		副本关闭时调用
		"""
		INFO_MSG( "[Team(ID:%i)]: matched copy is closed." % self.id )
		if self.isMatchedActiveTeam() :
			self.onMatchedRaidFinished()

	def onMatchedRaidFinished( self ) :
		"""
		<Define method>
		副本Raid结束时调用
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
