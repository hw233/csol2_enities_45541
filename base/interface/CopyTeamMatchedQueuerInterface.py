# -*- coding:gb18030 -*-

# python
import time
# bigworld
import BigWorld
# common
import csdefine
import csstatus
from Function import newUID
from bwdebug import INFO_MSG, ERROR_MSG, WARNING_MSG
# base
import ECBExtend
from BaseSpaceCopyFormulas import spaceCopyFormulas
from CopyMatcherInterface import CopyMatcherInterface


#对应副本的人数要求
"""
COPIES_NUMBER = {
	"fu_ben_shen_gui_mi_jing_3" : 3,
	"fu_ben_shen_gui_mi_jing_5" : 5,
	"fu_ben_wu_yao_qian_shao_3" : 3,
	"fu_ben_wu_yao_qian_shao_5" : 5,
#	"fu_ben_wu_yao_wang_bao_zang" : csdefine.ACTIVITY_FLAGS_WUYAOWANGBAOZANG, 
	"fu_ben_exp_melee_3" : 3,
	"fu_ben_xuan_tian_huan_jie_3" : 3,
	"fu_ben_zheng_jiu_ya_yu_3" : 3,
	"fu_ben_tian_guan_02_5" : 3,
	"fu_ben_xie_long_dong_xue_3" : 3,
	"fu_ben_xie_long_dong_xue_5" : 5,
	"fu_ben_feng_jian_shen_gong_3" : 3,
	"fu_ben_feng_jian_shen_gong_5" : 5,
	"fu_ben_she_hun_mi_zhen_3" : 3,
	"fu_ben_she_hun_mi_zhen_5" : 5,
	"fu_ben_kua_fu_shen_dian_3" : 3,
	"fu_ben_kua_fu_shen_dian_5" : 5,
	"shuijing_3" : 3,
	}
"""
COPIES_NUMBER ={}
for copyLabel,summary in spaceCopyFormulas.getCopiesSummary().items():
	COPIES_NUMBER[copyLabel] = summary["mode"]


class CopyTeamMatchedQueuerInterface :
	"""
	Build matched copy in these orders:
	1.notify the queuers to confirm duties and matched copy.
	2.confirm complete, then:
		2.1 if all queuers agree,then:
			2.1.1 if this confrim group is recruiter, transport the non-recruiters
				to exist copy.
			2.1.2 if this confirm group is non-recruiter, then create a new copy and transport
				all matched queuers to new copy.
		2.2 if some queuers disagree,then remove these queuers from matcher and rejoin others to
			matcher with priority.
	3.confirm timeout,then remove the timeout queuers from matcher and rejoin others to
		matcher with priority.
	"""
	def __init__( self ) :
		self.__matchedGroups = {}
		self.__recruiterID2GroupID = {}				# 查询boss击杀数量的组与招募者ID的映射

	def onGroupFormed( self, copyLabel, copyLevel, queuers, dutiesDistribution, recruiter=None ) :
		"""
		添加一个成功匹配的排队组
		"""
		if recruiter is None :
			matchedGroup = FresherGroup(
				copyLabel,
				copyLevel,
				self.__playerToDuty( dutiesDistribution ),
				self.__queuerToPlayer( queuers ),
			 	)
			self.__matchedGroups[ matchedGroup.id ] = matchedGroup
			matchedGroup.startHandling( copyLabel )
		else :
			matchedGroup = RecruiterGroup(
				copyLabel,
				copyLevel,
				self.__playerToDuty( dutiesDistribution ),
				self.__queuerToPlayer( queuers ),
				recruiter.id
			 	)
			self.__matchedGroups[ matchedGroup.id ] = matchedGroup
			matchedGroup.startHandling( copyLabel )

	def __playerToDuty( self, dutiesDistribution ) :
		"""
		"""
		result = {}
		for duty, undertakers in dutiesDistribution.iteritems() :
			for undertaker in undertakers :
				result[undertaker] = duty
		return result

	def __queuerToPlayer( self, queuers ) :
		"""
		"""
		result = {}
		for queuer in queuers :
			result[queuer.id] = queuer.memberMailboxes
		return result
	

	def __onResetMatchStatus( self, groupID, abandonQueuers ) :
		"""
		移除已离开的多个排队者，并让匹配组中的其他排队者重新排队。queuerQuit is queuerID
		方法考虑了异步情况下可能出现的排队者还在但没有匹配组的情况。
		"""
		if self.hasGroup( groupID ) :
			for queuerQuit in abandonQueuers:
				self.removeQueuer( queuerQuit, csstatus.CTM_LEAVE_QUEUE_SILENTLY )
			needRejoinQueuers = []
			allQueuers = tuple( i for i in self.popGroup(groupID)._queuerToPlayer )
			for queuerID in allQueuers :
				if queuerID in abandonQueuers :
					continue
				queuer = self.getQueuerByID( queuerID )
				if queuer :
					INFO_MSG( "smashGroup Queuer(ID %i, recruiter: %s) rejoin copyTeamQueuerMgr." % (queuerID, "YES" if queuer.isRecruiter else "NO") )
					needRejoinQueuers.append( queuer )
				else :
					ERROR_MSG( "smashGroup queuer(ID %i) is not exist." % queuerID )
			
			# 根据优先级排序 needRejoinQueuers，然后再让它们再加入匹配。
			needRejoinQueuers.sort( None,lambda q : q.priorityValue, True )
			for iQueuer in needRejoinQueuers :
				self.queuerRejoinMatcher( iQueuer )
		else :
			for queuerQuit in abandonQueuers :
				if self.hasQueuer( queuerQuit ) :
					self.removeQueuer( queuerQuit, csstatus.CTM_LEAVE_QUEUE_IN_COMMON )
				else :
						ERROR_MSG( "[239 CopyTeamMatchedQueuerInterface]: Matched group(ID:%i) and queuer(ID:%i) not found." % ( groupID, queuerQuit ) )
		

	def onPlayerConfirmMatched( self, groupID, playerID, accept ) :
		"""
		<Define method>
		@type		groupID : UID
		@param		groupID : 匹配小组的ID
		@type		playerID : OBJECT_ID
		@param		playerID : 玩家的ID
		@type		accept : BOOL
		@param		accept : 是否接受
		"""
		group = self.__matchedGroups.get( groupID )
		if group :
			if accept :
				group.onPlayerAcceptMatched( playerID )
			else :
				group.onPlayerAbandonMatched( playerID )
		else :
			WARNING_MSG("[122 CopyTeamMatchedQueuerInterface]: Matched group(ID:%i) not found." % groupID)

	def onPlayerReadyForMatchedTeam( self, groupID, playerID ) :
		"""
		<Define method>
		@type		groupID : UID
		@param		groupID : 匹配小组的ID
		@type		playerID : OBJECT_ID
		@param		playerID : 玩家的ID
		"""
		group = self.__matchedGroups.get( groupID )
		if group :
			group.onPlayerReadyForMatchedTeam( playerID )
		else :
			WARNING_MSG("[136 CopyTeamMatchedQueuerInterface]: Matched group(ID:%i) not found." % groupID)

	def onMatchedNewTeamCreated( self, groupID, captainID, teamMailbox ) :
		"""
		<Define method>
		@type		groupID : UID
		@param		groupID : 匹配小组的ID
		@type		captainID : OBJECT_ID
		@param		captainID : 玩家的ID
		@type		teamMailbox : MAILBOX
		@param		teamMailbox : TeamEntity的mailbox
		"""
		group = self.__matchedGroups.get( groupID )
		if group :
			group.onMatchedTeamCreated( captainID, teamMailbox )
		else :
			ERROR_MSG("[152 CopyTeamMatchedQueuerInterface]: Matched group(ID:%i) not found." % groupID)

	def onPlayerJoinMatchedTeam( self, groupID, playerID ) :
		"""
		<Define method>
		@type		groupID : UID
		@param		groupID : 匹配小组的ID
		@type		playerID : OBJECT_ID
		@param		playerID : 玩家的ID
		"""
		group = self.__matchedGroups.get( groupID )
		if group :
			group.onPlayerJoinMatchedTeam( playerID )
		else :
			WARNING_MSG("[166 CopyTeamMatchedQueuerInterface]: Matched group(ID:%i) not found." % groupID)
	
	def reSetMatchStatus( self, groupID ):
		"""
		<Define method>
		"""
		matchedGroup = self.__matchedGroups[groupID]
		abandonQueuers = []
		for playerMB in matchedGroup.getAllPlayerMB():
			playerMB.hideConfirmWindow()
			if matchedGroup._confirmations.get(playerMB.id) == csdefine.MATCHED_CONFIRM_STATUS_ABANDON:				
				playerMB.setMatchStatus(csdefine.MATCH_STATUS_PERSONAL_NORMAL)
				queuerID = matchedGroup.playerID2QueuerID( playerMB.id )
				if not queuerID in abandonQueuers :
					abandonQueuers.append( queuerID )
			else :
				playerMB.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_MATCHING )
		
		self.__onResetMatchStatus( groupID, abandonQueuers )	
		matchedGroup._confirmations = {}
		matchedGroup._listconfirmations = []
				
	
	
	def queryBossesKilledOfCopy( self, spaceType, groupID, recruiterID ) :
		"""
		"""
		self.__recruiterID2GroupID[recruiterID] = groupID
		BigWorld.globalData["SpaceManager"].queryBossesKilledOfCopyTeam( spaceType, self, recruiterID )

	def onQueryBossesKilledCallback( self, recruiterID, bossesKilled ) :
		"""
		<Define method>
		@type		recruiterID : INT32
		@param		recruiterID : 招募者的ID
		@type		bossesKilled : INT8
		@param		bossesKilled : boss已击杀数量
		"""
		if recruiterID in self.__recruiterID2GroupID :
			group = self.__matchedGroups.get( self.__recruiterID2GroupID[recruiterID] )
			del self.__recruiterID2GroupID[recruiterID]
			if group :
				group.onQueryBossesKilledCallback( bossesKilled )
			else :
				WARNING_MSG("[188 CopyTeamMatchedQueuerInterface]: Matched group maped to recruiter(ID:%i) not found." % recruiterID)
		else :
			ERROR_MSG("[190 CopyTeamMatchedQueuerInterface]: No match groupID to recruiter(ID:%i)." % recruiterID)

	def onMatchedPlayerCollapse( self, groupID, playerID ) :
		"""
		<Define method>
		成功匹配的玩家出现中断导致离开匹配队列
		@type		groupID : UID
		@param		groupID : 匹配小组的ID
		@type		playerID : OBJECT_ID
		@param		playerID : 玩家的ID
		"""
		if self.hasGroup( groupID ) :
			self.__matchedGroups[groupID].onPlayerCollapse( playerID )
		else :
			WARNING_MSG( "[204 CopyTeamMatchedQueuerInterface]: Player(ID:%i) collapsed, but matched group(ID:%i) not found." %\
				( playerID, groupID ) )

	def onMatchedQueuerCollapse( self, groupID, queuerID ) :
		"""
		<Define method>
		成功匹配的排队者出现中断导致离开匹配队列
		@type		groupID : UID
		@param		groupID : 匹配小组的ID
		@type		queuerID : OBJECT_ID
		@param		queuerID : 玩家的ID
		"""
		if self.hasGroup( groupID ) :
			self.__matchedGroups[groupID].onQueuerCollapse( queuerID )
		elif self.hasQueuer( queuerID ) :
			self.removeQueuer( queuerID, csstatus.CTM_LEAVE_QUEUE_IN_COMMON )
			WARNING_MSG( "[220 CopyTeamMatchedQueuerInterface]: Matched group(ID:%i) not found, but queuer(ID:%i) still exist, remove it." %\
				( groupID, queuerID ) )
		else :
			ERROR_MSG( "[223 CopyTeamMatchedQueuerInterface]: Matched group(ID:%i) and queuer(ID:%i) not found." % ( groupID, queuerID ) )

	def smashGroup( self, groupID, queuerQuit ) :
		"""
		移除已离开的排队者，并让匹配组中的其他排队者重新排队。queuerQuit is queuerID
		方法考虑了异步情况下可能出现的排队者还在但没有匹配组的情况。
		"""
		if self.hasGroup( groupID ) :
			self.removeQueuer( queuerQuit, csstatus.CTM_LEAVE_QUEUE_SILENTLY )
			needRejoinQueuers = []
			for queuerID in self.popGroup(groupID).queuerIDsExcept( queuerQuit ) :
				queuer = self.getQueuerByID( queuerID )
				if queuer :
					INFO_MSG( "smashGroup Queuer(ID %i, recruiter: %s) rejoin copyTeamQueuerMgr." % (queuerID, "YES" if queuer.isRecruiter else "NO") )
					needRejoinQueuers.append( queuer )
				else :
					ERROR_MSG( "smashGroup queuer(ID %i) is not exist." % queuerID )
			
			# 根据优先级排序 needRejoinQueuers，然后再让它们再加入匹配。
			needRejoinQueuers.sort( None,lambda q : q.priorityValue, True )
			for iQueuer in needRejoinQueuers :
				self.queuerRejoinMatcher( iQueuer )
		elif self.hasQueuer( queuerQuit ) :
			self.removeQueuer( queuerQuit, csstatus.CTM_LEAVE_QUEUE_IN_COMMON )
			WARNING_MSG( "[236 CopyTeamMatchedQueuerInterface]: Matched group(ID:%i) not found, but queuer(ID:%i) still exist, remove it." %\
				( groupID, queuerQuit ) )
		else :
			ERROR_MSG( "[239 CopyTeamMatchedQueuerInterface]: Matched group(ID:%i) and queuer(ID:%i) not found." % ( groupID, queuerQuit ) )

	def dropGroup( self, groupID ) :
		"""
		匹配组解散
		"""
		if self.hasGroup( groupID ) :
			for queuerID in self.popGroup(groupID).queuerIDsExcept( None ) :
				self.removeQueuer( queuerID, csstatus.CTM_LEAVE_QUEUE_SILENTLY )
		else :
			WARNING_MSG( "[249 CopyTeamMatchedQueuerInterface]: Matched group(ID:%i) not found before it disbands, " % ( groupID, queuerID ) )

	def matchedGroups( self ) :
		"""
		"""
		return self.__matchedGroups.copy()

	def registerGroup( self, group ) :
		"""
		<For debug>
		"""
		self.__matchedGroups[ group.id ] = group

	def removeGroup( self, groupID ) :
		"""
		移除一个匹配组
		"""
		if groupID in self.__matchedGroups :
			del self.__matchedGroups[groupID]

	def popGroup( self, groupID ) :
		"""
		移除一个匹配组
		"""
		return self.__matchedGroups.pop( groupID, None )

	def hasGroup( self, groupID ) :
		"""
		"""
		return groupID in self.__matchedGroups


class MatchedGroup :
	"""
	匹配成功的组
	"""
	__cc_queuer_mgr = None

	def __init__( self, copyLabel, copyLevel, playerToDuty, queuerToPlayer ) :
		self._id = newUID()
		self._copyLabel = copyLabel
		self._copyLevel = copyLevel
		self._playerToDuty = playerToDuty				# {playerID:duty}
		self._queuerToPlayer = queuerToPlayer			# {queuerID:(playerMB,)}
		self._bossesTotal = spaceCopyFormulas.totalBossesOf( copyLabel )
		self._bossesKilled = 0
		self._confirmations = {}
		self._listconfirmations = []                    # self._confirmations的列表形式，用于客户端有序显示
		self._latestConfirmTime = 0						# time of latest confirming. 
		self._feedbackRecord = []						# 需要全队成员回馈的记录
		self._onFirstPlayerAbandon = True


	@property
	def id( self ) :
		return self._id

	@classmethod
	def queuerMgr( CLS ) :
		if MatchedGroup.__cc_queuer_mgr is None and BigWorld.globalData.has_key( "copyTeamQueuerMgr" ) :
			MatchedGroup.__cc_queuer_mgr = BigWorld.entities.get( BigWorld.globalData["copyTeamQueuerMgr"].id )		# 可以保证本实例跟管理器在同一个baseapp上
		return MatchedGroup.__cc_queuer_mgr

	@classmethod
	def resetQueuerMgr( CLS ) :
		MatchedGroup.__cc_queuer_mgr = None
	
	def getAllPlayerMB( self ):
		allMBs = []
		for queuerMB in self._queuerToPlayer.values():
			for playerMB in queuerMB:
				allMBs.append( playerMB )
		return allMBs
	
	def playerID2PlayerMB( self, playerID ):
		for playerMB in self.getAllPlayerMB():
			if playerMB.id == playerID :
				return playerMB
	
	def startHandling( self, copyLabel ) :
		"""
		开始匹配后的处理
		"""
		pass

	def notifyPlayersAbandon( self, dropoutID ) :
		"""
		通知玩家有人放弃职责确认
		"""
		dropout = self.getMailboxByPlayerID( dropoutID )
		droppedQueuer = self.queuerMgr().getQueuerByID( self.playerID2QueuerID( dropoutID ) )
		dropoutName = "('%s',)" % droppedQueuer.nameOfMember( dropoutID )
		# 告知同一 queuer 内其他玩家已被移除队列
		for playerMB in droppedQueuer.memberMailboxes :
			if playerMB.id != dropout.id :
				playerMB.client.onStatusMessage( csstatus.CTM_REMOVE_QUEUE_FOR_DROP_TEAMMATE, dropoutName )
		# 告知不在同一 queuer 的其他所有玩家已被加入队列前端
		otherQueuers = self._queuerToPlayer.copy()
		del otherQueuers[ self.playerID2QueuerID( dropoutID ) ]
		for queuerMB in otherQueuers.values():
			for playerMB in queuerMB:
				playerMB.client.onStatusMessage( csstatus.CTM_REJOIN_MATCHER_QUEUE, dropoutName )
	

	def _prepareConfirmingMatched( self ) :
		"""
		"""
		self._latestConfirmTime = time.time()
		self._confirmations.clear()
		self._listconfirmations = []
		for playerID in self._playerToDuty.iterkeys() :
			self._confirmations[playerID] = csdefine.MATCHED_CONFIRM_STATUS_PENDING

	def _prepareRecordingFeedback( self ) :
		"""
		准备做回馈记录
		"""
		self._feedbackRecord = []

	def _recordFeedback( self, playerID ) :
		"""
		"""
		if playerID in self._feedbackRecord :
			ERROR_MSG( "[352 MatchedGroup(ID:%i)]:Player(ID:%i) feeds back repeatedly." % ( self.id, playerID ) )
		else :
			self._feedbackRecord.append( playerID )

	def _allMembersHaveFeededBack( self ) :
		"""
		是否全部成员已经反馈
		"""
		MCSTA = csdefine.MATCHED_CONFIRM_STATUS_ACCEPT
		num = len( [playerID for playerID,confirm in self._confirmations.items() if confirm == MCSTA]  )
		if len( self._feedbackRecord ) == COPIES_NUMBER[self._copyLabel] and  \
			num == COPIES_NUMBER[self._copyLabel]:    #正式版
			return True
		else :
			return False
#	# ----------------------------------------------------------------
	# splitter
	# ----------------------------------------------------------------
	def containPlayer( self, playerID ) :
		"""
		是否是组内成员
		"""
		return self.playerID2QueuerID( playerID ) is not None

	def containQueuer( self, queuerID ) :
		"""
		是否是组内成员
		"""
		return queuerID in self._queuerToPlayer

	def queuersNeedConfirmed( self ) :
		"""
		需要进行职责确认的排队者成员
		"""
		return ()

	def membersNeedConfirmed( self ) :
		"""
		需要进行职责确认的玩家成员
		"""
		return ()

	def playerMailboxes( self ) :
		"""
		获取所有玩家的mailbox
		"""
		mailboxes = []
		for playerMailboxes in self._queuerToPlayer.itervalues() :
			mailboxes.extend( playerMailboxes )
		return mailboxes

	def playerID2QueuerID( self, playerID ) :
		"""
		"""
		for queuerID, playerMailboxes in self._queuerToPlayer.iteritems() :
			for mb in playerMailboxes :
				if mb.id == playerID :
					return queuerID
		return None

	def queuerIDsExcept( self, queuerID ) :
		"""
		"""
		return tuple( i for i in self._queuerToPlayer if i != queuerID )

	def getMailboxByPlayerID( self, playerID ) :
		"""
		"""
		for mb in self.playerMailboxes() :
			if mb.id == playerID :
				return mb
		return None

#	# -------------------------------------------------
	# confirming infomation
	# -------------------------------------------------
	def timeTillLastConfirm( self ) :
		"""
		"""
		return time.time() - self._latestConfirmTime

	def confirmTimeout( self ) :
		"""
		"""
		return False
		#return self.timeTillLastConfirm() > csdefine.TIME_LIMIT_OF_MATCHED_CONFIRM

	def initiateConfirmingMatched( self ) :
		"""
		"""
		self._prepareConfirmingMatched()
		for queuer in self.queuersNeedConfirmed() :
			queuer.mailbox.enterConfirmingCopyMatched(
				self.id,
				self._playerToDuty,
				self._copyLabel,
				self._copyLevel,
				self._bossesTotal,
				self._bossesKilled,
				queuer.copies,
				)
				
	def onPlayerAcceptMatched( self, playerID ) :
		"""
		玩家接受此次匹配
		"""
		self.updateConfirmation( playerID, True )
		self.broadcastConfirmationToOthers( playerID )
		self.sendConfirmationsToPlayer( playerID )
		if playerID not in self._feedbackRecord:
			self._feedbackRecord.append(playerID)
		if self._allMembersHaveFeededBack() :
			self.onConfirmSuccessfully()	


	def onPlayerAbandonMatched( self, playerID ) :
		"""
		玩家放弃了此次匹配，则将其从队列移除，并将其他玩家以高优先级
		重新加入队列
		由于重新加入副本组队是即时的，而设置新状态是在5秒后，还是可能出现已经加入副本组队，而且匹配好后，再次弹出确认进入副本的框
		"""
		if not self.containPlayer( playerID ) :
			ERROR_MSG( "[464 MatchedGroup(ID:%i)]:Player(ID:%i) is not my member." % ( self.id, playerID ) )
		else :
			self.updateConfirmation( playerID, False )
			self.broadcastConfirmationToOthers( playerID )	
			playerMB = self.playerID2PlayerMB( playerID )
			playerMB.client.onStatusMessage( csstatus.CTM_REMOVE_QUEUE_FOR_DROP_SINGLE, "" )
			if not self._onFirstPlayerAbandon :
				return
			self._onFirstPlayerAbandon = False
			self.notifyPlayersAbandon( playerID )
			playerMB.addResetMatchTimer()

	
	def onConfirmSuccessfully( self ) :
		"""
		"""
		pass

	def allMembersAcceptMatched( self ) :
		"""
		是否所有玩家都确认接受了分派的职责
		"""
		return self.allConfirmationsAreAcceptance()

	def allMembersRepliedConfirmation( self ) :
		"""
		是否所有玩家都回复了职责确认
		"""
		if len( self._confirmations ) != len( self._playerToDuty ) :
			return False
		for r in self._confirmations.itervalues() :
			if r == csdefine.MATCHED_CONFIRM_STATUS_PENDING :
				return False
		return True

	def allConfirmationsAreAcceptance( self ) :
		"""
		是否有玩家不接受职责确认
		"""
		for r in self._confirmations.itervalues() :
			if r != csdefine.MATCHED_CONFIRM_STATUS_ACCEPT :
				return False
		return True

	def updateConfirmation( self, playerID, accept ) :
		"""
		"""
		if accept :
			self._confirmations[playerID] = csdefine.MATCHED_CONFIRM_STATUS_ACCEPT
			self._listconfirmations.append((playerID,csdefine.MATCHED_CONFIRM_STATUS_ACCEPT))
		else :
			self._confirmations[playerID] = csdefine.MATCHED_CONFIRM_STATUS_ABANDON
			self._listconfirmations.append((playerID,csdefine.MATCHED_CONFIRM_STATUS_ABANDON))

	def broadcastConfirmationToOthers( self, playerID ) :
		"""
		"""
		confirmation = self._confirmations
		for playerMB in self.membersNeedConfirmed() :
			if playerMB.id != playerID :
				INFO_MSG("517 broadcastConfirmationToOthers playerMB.id = %i " % playerMB.id)
				playerMB.client.updateMatchedConfirmationFromServer( playerID,len(self.membersNeedConfirmed()), self._listconfirmations, COPIES_NUMBER[self._copyLabel] )

	def sendConfirmationsToPlayer( self, playerID ) :
		"""
		将全部职责确认信息发送给玩家
		"""
		playerMB = self.getMailboxByPlayerID( playerID )
		playerMB.client.receiveMatchedInfomationFromServer( self._listconfirmations, COPIES_NUMBER[self._copyLabel] )

	def matchedInfomation( self ) :
		"""
		"""
		info = {}
		for playerID, confirmation in self._confirmations.iteritems() :
			info[playerID] =  confirmation 
		return info

	def onPlayerReadyForMatchedTeam( self, playerID ) :
		"""
		玩家成功离开旧队伍，准备加入匹配队伍
		"""
		if playerID not in self._feedbackRecord:
			self._recordFeedback( playerID )
		if self._allMembersHaveFeededBack() :     #全部确认，准备传送
			self.onMembersReadyForMatchedTeam()      
		else :
			ERROR_MSG( "[542 MatchedGroup(ID:%i)]: Player(ID:%i) leaved team is not my member." % ( self.id, playerID ) )

	def onMembersReadyForMatchedTeam( self ) :
		"""
		所有成员已准备好加入新队伍
		"""
		pass

	def onPlayerJoinMatchedTeam( self, playerID ) :
		"""
		"""
		if self.containPlayer( playerID ) :
			self._recordFeedback( playerID )
			if self._allMembersHaveFeededBack() :
				self.onAllMembersHaveJoinedMatchedTeam()
		else :
			ERROR_MSG( "[558 MatchedGroup(ID:%i)]:Player(ID:%i) joined team is not my member." % ( self.id, playerID ) )

	def onAllMembersHaveJoinedMatchedTeam( self ) :
		"""
		所有成员已成功加入匹配副本
		"""
		self.teleportCopy()
		self.onMatchedCompleted()
		self.queuerMgr().dropGroup( self.id )  #在副本结束之前，信息应该保存，有可能用于副本内补充人员

	def teleportCopy( self ) :
		"""
		将所有成员传送副本
		"""
		pass

	def onMatchedCompleted( self ) :
		"""
		匹配工作已全部完成了
		"""
		pass

	def onPlayerCollapse( self, playerID ) :
		"""
		玩家离开匹配组
		"""
		if self.containPlayer( playerID ) :
			if self.allMembersRepliedConfirmation() :
				self.queuerMgr().smashGroup( self.id, self.playerID2QueuerID( playerID ) )
			else :
				self.onPlayerAbandonMatched( playerID )
		else :
			ERROR_MSG( "[590 MatchedGroup(ID:%i)]:Player(ID:%i) joined team is not my member." % ( self.id, playerID ) )

	def onQueuerCollapse( self, queuerID ) :
		"""
		排队者离开匹配组
		"""
		if self.containQueuer( queuerID ) :
			self.queuerMgr().smashGroup( self.id, queuerID )
		else :
			ERROR_MSG( "[599 MatchedGroup(ID:%i)]:Player(ID:%i) joined team is not my member." % ( self.id, playerID ) )



# ----------------------------------------------------------------
# implement the fresher matched group.
# ----------------------------------------------------------------
class FresherGroup( MatchedGroup ) :

	def __init__( self, copyLabel, copyLevel, playerToDuty, queuerToPlayer ) :
		MatchedGroup.__init__( self, copyLabel, copyLevel, playerToDuty, queuerToPlayer )

	def startHandling( self, copyLabel ) :
		"""
		开始匹配后的处理
		"""
		MatchedGroup.startHandling( self, copyLabel )
		self.initiateConfirmingMatched(  )
		

	def queuersNeedConfirmed( self ) :
		"""
		需要进行职责确认的排队者成员
		"""
		return tuple( self.queuerMgr().getQueuerByID(i) for i in self._queuerToPlayer )

	def membersNeedConfirmed( self ) :
		"""
		"""
		return self.playerMailboxes()
	
	def onConfirmSuccessfully( self ) :
		"""
		"""
		INFO_MSG( "[644 FresherGroup(%i)]: Members confirm successfully." % self.id )
		self._prepareRecordingFeedback()
		for player in self.playerMailboxes() :
			player.onMatchedConfirmSuccessfully()

	def onMembersReadyForMatchedTeam( self ) :
		"""
		所有成员已准备好加入新队伍
		"""
		INFO_MSG( "[653 FresherGroup(%i)]: Members are ready for matched team." % self.id )
		self.createMatchedTeam()
			
	def createMatchedTeam( self ) :
		"""
		"""
		guider = self.choiceTeamGuider()
		guider.createMatchedCopyTeam()

	def __memberToDuty( self ) :
		"""
		"""
		result = {}
		for member in self.playerMailboxes() :
			result[member] = self._playerToDuty[member.id]
		return result

	def choiceTeamGuider( self ) :
		"""
		"""
		candidate = None
		for queuerID in self._queuerToPlayer.iterkeys() :
			queuer = self.queuerMgr().getQueuerByID( queuerID )
			for candidate, expectGuider in queuer.guiderCandidates :
				if expectGuider : return candidate  #有人当领队，就返回
		return self.getAllPlayerMB()[0] #如果匹配组成员都没有选择当领队，就挑第一个人当队长
		

	def onMatchedTeamCreated( self, captainID, teamMailbox ) :
		"""
		队伍创建成功
		"""
		INFO_MSG( "[701 FresherGroup(%i)]: Matched team has been created." % self.id )
		if self.containPlayer( captainID ) :
			self._prepareRecordingFeedback()
			for member in self.playerMailboxes() :
				if member.id != captainID :
					member.joinMatchedCopyTeam( captainID, teamMailbox )							# 把其他人加入队伍
			teamMailbox.turnToMatchedTeam( self._copyLabel, self._copyLevel, self._playerToDuty )	# 将队伍转变为副本匹配队伍
			self.onPlayerJoinMatchedTeam( captainID )												# 通知队长已成功加入匹配队伍
		else :
			ERROR_MSG( "[710 FresherGroup(ID:%i)]:Captain(ID:%i) is not my member." % ( self.id, captainID ) )

	def teleportCopy( self ) :
		"""
		将成员直接传送到副本
		"""
		INFO_MSG( "[716 FresherGroup(%i)]: Members teleport to copy." % self.id )
		for player in self.playerMailboxes() :
			player.teleportCopyOnMatched( self._copyLabel )

	def onMatchedCompleted( self ) :
		"""
		匹配工作已全部完成了，做最后的通知
		"""
		for member in self.playerMailboxes() :
			member.cell.onMatchedCopyTeam( self._copyLevel, self._copyLabel )							# 匹配副本更新到cell
			member.client.updateMatchedCopyInfo( self._copyLabel, self._copyLevel, self._playerToDuty )	# 这样更新比在TeamEntity中更新更好，


class RecruiterGroup( MatchedGroup ) :

	def __init__( self, copyLabel, copyLevel, playerToDuty, queuerToPlayer, recruiterID ) :
		MatchedGroup.__init__( self, copyLabel, copyLevel, playerToDuty, queuerToPlayer )
		self._recruiterID = recruiterID

	def non_recruiters( self ) :
		"""
		"""
		mailboxes = []
		for queuerID, playerMailboxes in self._queuerToPlayer.iteritems() :
			if queuerID != self._recruiterID :
				mailboxes.extend( playerMailboxes )
		return mailboxes

	def recruiters( self ) :
		"""
		"""
		mailboxes = []
		for queuerID, playerMailboxes in self._queuerToPlayer.iteritems() :
			if queuerID == self._recruiterID :
				mailboxes.extend( playerMailboxes )
		return mailboxes
	
	def recruitingQueuer( self ) :
		"""
		"""
		return self.queuerMgr().getQueuerByID( self._recruiterID )
	
	
	def queuersNeedConfirmed( self ) :
		"""
		"""
		return tuple( self.queuerMgr().getQueuerByID(i) for i in self._queuerToPlayer if i != self._recruiterID )

	def membersNeedConfirmed( self ) :
		"""
		"""
		return self.non_recruiters()

	def startHandling( self, copyLabel ) :
		"""
		开始匹配后的处理
		"""
		MatchedGroup.startHandling( self, copyLabel )
		self.recruitingQueuer().mailbox.onRematchedAsRecruiter( self.id )							# 通知招募者加入匹配组
		self.queryBossesKilled()

	def queryBossesKilled( self ) :
		"""
		"""
		INFO_MSG( "[791 RecruiterGroup(ID:%i)]: Now query the killed bosses count." % self.id )
		self.queuerMgr().queryBossesKilledOfCopy( self._copyLabel, self.id, self._recruiterID )		# 招募者一定是TeamEntity，所以recruiterID就是队伍ID

	def onQueryBossesKilledCallback( self, bossesKilled ) :
		"""
		查询副本boss击杀数量回调
		"""
		self._bossesKilled = bossesKilled
		self.initiateConfirmingMatched()

	def initiateConfirmingMatched( self ) :
		"""
		重写发起职责确认的方法，可能招募者队伍自己组满了
		再发起排队，这样就没有需要确认匹配的成员。
		"""
		MatchedGroup.initiateConfirmingMatched( self )
		self._confirmations = {}  #准备记录confirm
		self._listconfirmations = []
		self._prepareRecordingFeedback()
		for mb in self.recruiters() :
			self.updateConfirmation( mb.id, True )   #直接将招募者加入confirm
		if self.allMembersAcceptMatched() :         #这个没有，既然是招募组，一般都是少人，除了自己手动组了其它成员
			self.onConfirmSuccessfully()

	def onConfirmSuccessfully( self ) :
		"""
		"""
		INFO_MSG( "[815 RecruiterGroup(ID:%i)]: non-recruiters confirms successfully." % self.id )
		   
		for player in self.non_recruiters() :
			INFO_MSG("[818 RecruiterGroup(ID:%i)] contain non-recruiter : %i" %( self.id, player.id ) )
			player.onMatchedConfirmSuccessfully()
		for player in self.recruiters() :
			INFO_MSG("[822 RecruiterGroup(ID:%i)] contain recruiter : %i" %( self.id, player.id ) )
			self.onPlayerReadyForMatchedTeam( player.id )
			
	def onMembersReadyForMatchedTeam( self ) :
		"""
		所有成员已准备好加入新队伍
		"""
		INFO_MSG( "[830 RecruiterGroup(ID:%i)]: non-recruiters are ready for matched team." % self.id )
		self.combineGroup()

	def combineGroup( self ) :
		"""
		combine the non-recuriter to the recruiter team.
		"""
		self._prepareRecordingFeedback()
		self.recruitingQueuer().mailbox.absorbMatchedMembers( self.non_recruiters() )		# 将非招募成员加入到招募者队伍
		for player in self.recruiters() :
			self.onPlayerJoinMatchedTeam( player.id )

	def teleportCopy( self ) :
		"""
		将成员直接传送到副本
		"""
		INFO_MSG( "[846 RecruiterGroup(ID:%i)]: non-recruiters teleport to copy." % self.id )
		for player in self.non_recruiters() :
			player.teleportCopyOnMatched( self._copyLabel )

	def onMatchedCompleted( self ) :
		"""
		匹配工作已全部完成了，做最后的通知
		"""
		self.recruitingQueuer().mailbox.onRematchedCompleted( self._playerToDuty )
		for player in self.non_recruiters() :
			player.cell.onMatchedCopyTeam( self._copyLevel, self._copyLabel )							# 匹配副本更新到cell
			player.client.updateMatchedCopyInfo( self._copyLabel, self._copyLevel, self._playerToDuty )	# 这样更新比在TeamEntity中更新更好，