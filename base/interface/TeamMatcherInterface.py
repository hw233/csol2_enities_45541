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
		self.memberBlacklist = {}									# 保存所有队员的黑名单
		self.initiatedCopyLevel = 0									# 排队发起者对应的副本等级
		self.matchedCopy = None										# 匹配成功，正在进行的副本
		self.matchStatus = csdefine.MATCH_STATUS_TEAM_NORMAL
		self.matchedGroupID = 0
		self._camp = 0 
		
		self.__beforeTeamChangeMembers = []                        #记录队伍状态改变前的成员base

	# ----------------------------------------------------------------
	# functions in common
	# ----------------------------------------------------------------
	def setMatchStatus( self, status ) :
		"""
		设置匹配状态
		"""
		self.matchStatus = status

	def isMatchStatus( self, status ) :
		"""
		"""
		return self.matchStatus == status

	def isMatchingInQueue( self ) :
		"""
		是否还在排队者管理器中
		"""
		return self.isMatchStatus( csdefine.MATCH_STATUS_TEAM_MATCHING )

	def isMatchedInQueue( self ) :
		"""
		是否已经成功匹配
		"""
		return self.isMatchStatus( csdefine.MATCH_STATUS_TEAM_MATCHED )

	def isInDutiesSelecting( self ) :
		"""
		是否还在职责选择中
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
		暂时不添加到def文件中
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
		判断玩家的等级是否相符：
		1、如果是之前匹配到的玩家，则忽略等级判断
		2、如果是新队伍，或者不是匹配队伍成员，则
			作等级判断
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
		需要考虑：
		1、是否有人掉线，有则不能发起
		2、发起职责选择后，队伍成员发生改变，则取消此次选择
		3、考虑到网络延时等异常情况，对回复职责选择做一个时延的检查，超出了则取消此次选择
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
		@param		level : 队长的等级
		@type		captainDuties : UINT8_TUPLE
		@param		captainDuties : 担任的职责
		@type		copies : STRING_TUPLE
		@param		copies : 前往的副本数组
		@type		expectGuider : BOOL
		@param		expectGuider : 是否愿意担任队伍向导
		@type		blacklist : STRING_TUPLE
		@param		blacklist : 玩家的黑名单
		"""
		self._camp = camp 
		self.initiatedCopyLevel = spaceCopyFormulas.formatCopyLevel( level )
		self.__initiateSelectingDutiesByMember( self.getCaptainDBID(), level, captainDuties, copies, expectGuider, blacklist )

	def __initiateSelectingDutiesByMember( self, databaseID, level, duties, copies, expectGuider, blacklist ) :
		"""
		@type		databaseID : DATABASE_ID
		@param		databaseID : 玩家的databaseID
		@type		duties : UINT8_TUPLE
		@param		duties : 担任的职责
		@type		copies : STRING_TUPLE
		@param		copies : 前往的副本数组
		@type		expectGuider : BOOL
		@param		expectGuider : 是否愿意担任队伍向导
		@type		blacklist : STRING_TUPLE
		@param		blacklist : 玩家的黑名单
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
		 #目前暂停对职务的判定
		for ( playerId, playerInfo ) in self.member :
			self.__beforeTeamChangeMembers.append( playerInfo["playerBase"] )
			if playerId == self.captainID :
				continue
			
			INFO_MSG( "Notify [%s(id:%i)] to select duties." % ( playerInfo["playerName"], playerId ) )
			playerInfo["playerBase"].initiateSelectingDuties( copies )


	def cancelSelectingDuties( self ) :
		"""
		取消职责选择
		"""
		self.setMatchStatus( csdefine.MATCH_STATUS_TEAM_NORMAL )
		for playerBase in self.__beforeTeamChangeMembers :
			if not playerBase : continue
			playerBase.cancelSelectingDuties()
		del self.__beforeTeamChangeMembers[:]

	def onMemberSelectedDuties( self, playerDBID, duties, expectGuider, blacklist, level ) :
		"""
		<Define method>
		需要考虑：
		1、考虑到网络延时等异常情况，对回复职责选择做一个时延的检查，超出了则此次选择无效
		@type		playerDBID : DATABASE_ID
		@param		playerDBID : 玩家的DBID
		@type		duties : UINT8_TUPLE(python tuple)
		@param		duties : 玩家选择的职责
		@type		expectGuider : BOOL
		@param		expectGuider : 是否愿意担任队伍向导
		@type		blacklist : STRING_TUPLE(python tuple)
		@param		blacklist : 玩家的黑名单
		@type		level : UINT8
		@param		level : 玩家的等级
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
		@param		playerDBID : 玩家的DBID
		"""
		if self.isInDutiesSelecting() and self.contain( playerDBID ) :
			self.broadcastMembers( playerDBID, csstatus.CTM_TEAMMATE_SELECT_EMPTY_DUTY )
			self.matchedFixedMembersSetResumed( False )
			self.cancelSelectingDuties()

	def onMemberSelectingDutyTimeout( self, playerDBID ) :
		"""
		<Define method>
		@type		playerDBID : DATABASE_ID
		@param		playerDBID : 玩家的DBID
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
		"""队员们选择的职责是否是互补的
		"""
		return copyTeamFormulas.dutiesComplementary( self.memberDutiesSelected() )

	def membersAssortWithDuties( self ) :
		"""
		检查队员和职责是不是对应得起来，例如半路队伍有新队员加入时，
		新队员还未选过职责，所以就会出现职责不对应。
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
		以未匹配过的身份加入匹配队列
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
			copyTeamQueuerMgr.onReceiveJoinRequest( self,										# 排队者的mailbox
										self.initiatedCopyLevel,					# 排队者等级
										self.freshMembers(),						# 排队者内部成员的数据
										self.expectedCopies,						# 排队者欲前往的副本
										self.blacklistOfMembers(),					# 排队者的黑名单列表
										self._camp,                                  # 阵营
										False,										# 是否是招募者
										)

	def _joinMatcherAsMatchedAlteredTeam( self ) :
		"""
		匹配队伍，但是发生了人员与职责不匹配的情况，所以要求重新
		选择职责，最终走这个接口加入匹配队列
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
			copyTeamQueuerMgr.onReceiveJoinRequest( self,										# 排队者的mailbox
										self.levelOfMatchedCopy,					# 排队者等级
										self.freshMembers(),						# 排队者内部成员的数据
										(self.labelOfMatchedCopy,),					# 排队者欲前往的副本
										self.blacklistOfMembers(),					# 排队者的黑名单列表
										self._camp,                                  # 阵营
										True,										# 是否是招募者									
										)

	def freshMembers( self ) :
		"""
		生成进入排队队列需要的成员数据
		"""
		members = []
		for playerId, playerInfo in self.member :
			selection = self.memberSelections[ playerInfo["playerDBID"] ]				# 如果没有对应的数据，就让它报错
			members.append( ( playerInfo["playerBase"], playerInfo["playerName"], selection[0], selection[1] ) )	# ( mailbox, name, duties, expectGuider )
			self.__beforeTeamChangeMembers.append( playerInfo["playerBase"] )
		return tuple( members )

	def blacklistOfMembers( self ) :
		"""
		汇总玩家的黑名单列表
		"""
		blacklist = set()
		for l in self.memberBlacklist.itervalues() :
			blacklist.update( l )
		return tuple( blacklist )

	def memberDutiesSelected( self ) :
		"""
		玩家选择的职责
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
		@param		groupID : 匹配小组的ID
		@type		dutyMap : PY_DICT
		@param		dutyMap : 匹配的职责
		@type		copyLabel : STRING
		@param		copyLabel : 副本名称
		@type		copyLevel : UINT8
		@param		copyLevel : 副本等级
		@type		bossesTotal : UINT8
		@param		bossesTotal : 副本BOSS总数
		@type		bossesKilled : UINT8
		@param		bossesKilled : 副本BOSS已击杀数量
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
		玩家加队
		后续工作：在TeamEntity中调用此接口
		需要注意：如果队伍正在排队，则让队伍从管理器移除
				如果正在选择职责，取消选择
				如果正在确认职责，取消确认
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
		玩家离队
		后续工作：在TeamEntity中调用此接口
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
		玩家下线
		后续工作：在TeamEntity中调用此接口
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
		玩家下线重上，需要：
		1、更新匹配信息
		2、刷新是否在副本的标记
		"""
		if self.isMatchedActiveTeam() :
			self._updateMatchedDutyOnMemberLogon( oldEntityID, newEntityID )
			playerBase = self.memberMailboxOfDBID( playerDBID )
			playerBase.cell.onMatchedCopyTeam( self.levelOfMatchedCopy, self.labelOfMatchedCopy )
			playerBase.client.updateMatchedCopyInfo( self.labelOfMatchedCopy, self.levelOfMatchedCopy, self.matchedMembersDuty )

	def tmi_onChangeCaptain( self, newCaptainID ) :
		"""
		队长改变
		"""
		if self.isInDutiesSelecting() :
			self.matchedFixedMembersSetResumed( False )
			self.cancelSelectingDuties()
			self.broadcastMessage( (), csstatus.CTM_DUTY_SELECTION_FAILED )


	def tmi_onDisband( self ) :
		"""
		队伍解散
		队伍销毁前调用：在TeamEntity中调用此接口
		"""
		if self.isMatchingInQueue() :
			self.__broadcastMessageToPlayers( self.__beforeTeamChangeMembers, csstatus.CTM_DUTY_SELECTION_FAILED )
			self.leaveCopyMatcherQueue()
		elif self.isInDutiesSelecting() :
			self.__broadcastMessageToPlayers( self.__beforeTeamChangeMembers, csstatus.CTM_DUTY_SELECTION_FAILED )
			self.cancelSelectingDuties()


	def leaveCopyMatcherQueue( self ) :
		"""
		从排队队列移除
		"""
		copyTeamQueuerMgr = BigWorld.globalData["copyTeamQueuerMgr"]
		copyTeamQueuerMgr.removeQueuer( self.id, csstatus.CTM_LEAVE_QUEUE_IN_COMMON )
		self.setMatchStatus( csdefine.MATCH_STATUS_TEAM_NORMAL )			# 不等回调，这里提前设置为回到普通状态

	def onLeaveCopyMatcherQueue( self, reason ) :
		"""
		<Define method>
		@type		reason : INT32
		@param		reason : 离开的原因（在csstatus中定义）
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
