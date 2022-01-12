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
		self._matchedGroupID = 0												# 记录成功匹配组的ID
		self._matchStatus = csdefine.MATCH_STATUS_PERSONAL_NORMAL				# 不需要定义
		self._leaveForMatchedTeam = False										# 离开旧队伍，加入新的队伍的标记
		self._joiningMatchedTeam = False										# 加入匹配队伍的标记
		self._tid_confirmMatch = 0												# 职责确认的timerID
		self._tid_selectingDuty = 0												# 职责选择的timerID
		self._tid_resetMatchStatus = 0 											# 5秒延时设置状态
	
	# ----------------------------------------------------------------
	# functions in common
	# ----------------------------------------------------------------
	@staticmethod
	def queuerMgr() :
		"""
		获取排队者管理器
		"""
		return BigWorld.globalData["copyTeamQueuerMgr"]

	def setMatchStatus( self, status ) :
		"""
		Defined method
		设置匹配状态
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
		是否正处在队列中等待匹配
		"""
		return self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_MATCHING )

	def isInCopyMatcherQueue( self ) :
		"""
		是否还在排队者管理器中
		"""
		return self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_MATCHING ) or\
			self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_CONFIRMING ) or\
			self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_MATCHED )

	def isMatchedInQueue( self ) :
		"""
		是否已经成功匹配，并还在队列中
		"""
		return self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_CONFIRMING ) or\
			self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_MATCHED )
	
	def updateAvgQueueingTimeFromServer( self ):
		"""
		<Define method>
		在queuerMgr中同等级段的queuer的总数，根据queuer的个数要估计平均等待时间，每个queuer为29秒
		"""
		self.queuerMgr().querySameLevelQueuersNumber( self, self.level)
	
	def onQuerySameLevelQueuersNumber( self, sameLevelQueuersNumber ) :
		"""
		<Define Method>
		@ type    UINT8
		@ param   正在排队中，且与玩家处于同一等级段的queuer个数
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
		@param		duties : 选择的职责
		@type		copies : STRING_TUPLE(python tuple)
		@param		copies : 选择的职责
		@type		expectGuider : BOOL
		@param		expectGuider : 是否愿意担任队伍向导
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
		@param		duties : 选择的职责
		@type		copies : STRING_TUPLE(python tuple)
		@param		copies : 选择的职责
		@type		expectGuider : BOOL
		@param		expectGuider : 是否愿意担任队伍向导
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
		@param		duties : 选择的职责
		@type		expectGuider : BOOL
		@param		expectGuider : 是否愿意担任队伍向导
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
		获取黑名单中玩家的名字
		"""
		return tuple( r.playerName for r in self.blacklist.itervalues() )

	# ----------------------------------------------------------------
	# about leave matcher queue
	# ----------------------------------------------------------------
	def cmi_onLeaveTeam( self ) :
		"""
		离开队伍
		"""
		if self._leaveForMatchedTeam :
			self.__replyReadyForMatchedTeam()
			self._leaveForMatchedTeam = False
			self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_NORMAL )
		elif self.isMatchingInQueue() :
			self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_NORMAL )		# 在这里设置为普通状态，是因为玩家已经从队伍离开，不会再从队伍那边得到通知
			self.statusMessage( csstatus.CTM_LEAVE_QUEUE_IN_COMMON )
		elif self.isMatchedInQueue() :
			self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_NORMAL )		# 在这里设置为普通状态，是因为玩家已经从队伍离开，不会再从队伍那边得到通知
			self.queuerMgr().onMatchedPlayerCollapse( self._matchedGroupID, self.id )

	def cmi_onJoinTeam( self ) :
		"""
		加入了一个队伍
		"""
		if self._joiningMatchedTeam :
			self._replyJoinMatchedCopyTeam()
			self._joiningMatchedTeam = False
		elif self.isInCopyMatcherQueue() :
			self.leaveQueuerMgr()

	def cmi_onLogout( self ) :
		"""
		玩家下线
		"""
		if self.isMatchingInQueue() and not self.isInTeam() :
			self.queuerMgr().removeQueuer( self.id, csstatus.CTM_LEAVE_QUEUE_SILENTLY )
		elif self.isMatchedInQueue() :
			self.queuerMgr().onMatchedPlayerCollapse( self._matchedGroupID, self.id )
		elif self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_SELECTING_DUTY ) :
			self.cancelSelectingDuties()

	def cmi_onTeamDisband( self ) :
		"""
		队伍解散，目前未在玩家身上做队伍解散后的处理
		"""
		self.cmi_onLeaveTeam()

	def leaveCopyMatcherQueue( self ) :
		"""
		主动离开组队队列
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
		@param		reason : 离开的原因（在csstatus中定义）
		"""
		INFO_MSG( "[%s(id:%i)]:Leave copy matcher callback, reason: 0x%0x" % ( self.getName(), self.id, reason ) )
		self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_NORMAL )
		if reason != csstatus.CTM_LEAVE_QUEUE_SILENTLY :
			self.statusMessage( reason )

	def leaveQueuerMgr( self ) :
		"""
		离开排队者管理器
		"""
		if self.isMatchingInQueue() :
			self.queuerMgr().removeQueuer( self.id, csstatus.CTM_LEAVE_QUEUE_IN_COMMON )
		elif self.isMatchedInQueue() :
			self.queuerMgr().onMatchedPlayerCollapse( self._matchedGroupID, self.id )

	def onRemovedFromQueuerMgr( self, collapserID ) :
		"""
		<Define method>NEW???
		从排队者管理器移除，通知玩家
		"""
		pass


#	# ----------------------------------------------------------------
	# handle after matched successfully
	# ----------------------------------------------------------------
	def onRematchedAsRecruiter( self, groupID ) :
		"""
		<Define method>
		@type		groupID : UID
		@param		groupID : 匹配小组的ID
		招募者再次成功匹配
		"""
		INFO_MSG( "[%s(id:%i)]: Join matched group %i." % ( self.getName(), self.id, groupID ) )
		self._matchedGroupID = groupID
		self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_MATCHED )

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
		#dutyMap等后期新增职责时使用，暂时不处理，统一用DPS代替
		duty = csdefine.COPY_DUTY_DPS
		INFO_MSG( "[%s(id:%i)]: Enter match confirming, matched group %i." % ( self.getName(), self.id, groupID ) )
		self._matchedGroupID = groupID
		self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_CONFIRMING )       #让客户端响应进入副本确认界面
		self.client.notifyToConfirmCopyMatchedFromServer( duty, copyLabel, copyLevel, bossesTotal, bossesKilled, copies )
		self._tid_confirmMatch = self.addTimer( csdefine.TIME_LIMIT_OF_MATCHED_CONFIRM, 0, ECBExtend.TIMEOUT_CBID_OF_MATCHED_CONFIRM )

	
	def initiateSelectingDuties( self, copies ):
		"""
		<Defined method>
		@type		copies : STRING_TUPLE
		@param		copies : 前往的副本数组		
		"""	
		if self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_SELECTING_DUTY ) : #还未撤销时，队长重新发起职责选择，先撤销
			self.cancelSelectingDuties()
		self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_SELECTING_DUTY )
		INFO_MSG( "[%s(id:%i)]: Enter selecting duties, teamID %i." % ( self.getName(), self.id, self.teamID ) )
		self.client.notifyToSelectDutiesFromServer( copies )
		self._tid_selectingDuty = self.addTimer( csdefine.TIME_LIMIT_OF_DUTIES_SELECTION, 0, ECBExtend.TIMEOUT_CBID_OF_DUTIES_SELECTION )

	def cancelSelectingDuties( self ):
		"""
		<Defined method>
		@type		copies : STRING_TUPLE
		@param		copies : 前往的副本数组		
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
		@param		accept : 是否接受本次匹配
		"""
		#if self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_MATCHED ) :
		INFO_MSG("self._tid_confirmMatch: %i" % self._tid_confirmMatch )
		if self._tid_confirmMatch :
			self.__replyMatchedConfirmToMgr( accept )
			#超时就把timer取消
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
		告诉管理器，已准备好加入匹配队伍
		"""
		self.queuerMgr().onPlayerReadyForMatchedTeam( self._matchedGroupID, self.id )

	def onMatchedConfirmSuccessfully( self ) :
		"""
		<Define method>
		职责确认成功
		"""
		self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_MATCHED )
		if self.isInTeam() :
			self._leaveForMatchedTeam = True							# 标记玩家是从旧队伍移除，以便加入到匹配队伍，
																		# 而不是手动离开队伍，如果这个过程中发生玩
																		# 家手动离开队伍的情况，也当作是离开旧队伍加
																		# 入新队伍的处理。
			self.getTeamMailbox().leave( self.id, self.id )					# 从旧队伍离开
		self.__replyReadyForMatchedTeam()

	def createMatchedCopyTeam( self ) :
		"""
		<Define method>
		创建新副本队伍
		注：走到这里时，teamMailbox还在的情况极有可能出现，虽然前
		面已经让队长解散了队伍，但是紧接着就通知创建新队伍了，所以
		在异步情况，可能解散队伍的通知还没到达就已经要创建新队伍了。
		考虑：是否可以在遇到teamMailbox还在的情况时，直接把teamMailbox
		清除掉？这样可能会导致离队流程没走完从而出现问题。
		临时解决办法，如果遇到teamMailbox还在的情况，则延时一段时间再创
		建，并记录尝试次数，在达到一定次数还是失败时再报错。
		# --------------------------------------------------
		目前已经使用另一种方式以保证玩家在成功离开旧的队伍之后再进行
		创建新队伍以及加入新队伍的操作，管理器会统计所有匹配的玩家均
		已离开了旧队伍，然后才进行创建新队伍的操作。
		"""
		if self.isInTeam() :
			ERROR_MSG( "[%s(id:%i)]: I am still in a team when trying to create matched copy team." % ( self.getName(), self.id ) )
			return
		#self.createSelfTeamAnywhere( self._onMatchedCopyTeamCreated )				# 先自己创建队伍
		self.createSelfTeamLocally()												# 在本base上创建队伍
		self.queuerMgr().onMatchedNewTeamCreated( self._matchedGroupID, self.id, self.getTeamMailbox() )

	def createSelfTeamAnywhere( self, callback ) :
		"""
		创建自己的队伍
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
		创建队伍回调
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
		玩家加入匹配的新队伍
		@type		captainID : OBJECT_ID
		@param		captainID : 新成员名称
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
		告诉管理器，已成功加入新队伍
		"""
		self.queuerMgr().onPlayerJoinMatchedTeam( self._matchedGroupID, self.id )

	def teleportCopyOnMatched( self, copyLabel ) :
		"""
		<Define method>
		传送到匹配的副本，到此整个匹配流程结束，匹配状态设置为普通状态
		@type	copyLabel : STRING
		@param	copyLabel : 匹配副本的标签
		"""
		self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_NORMAL )
		#在传送的时候判断，如果在副本外，才传送，并弹出确认框
		self.cell.teleportCopyOnMatched( copyLabel )


	# ----------------------------------------------------------------
	# handle after enter copy successfully
	# ----------------------------------------------------------------
	def resumeHaltedRaid( self, teamID, camp ) :
		"""
		<Exposed method>
		请求组人以继续中断的副本
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
		@param	suffererID : 剔除对象的ID
		@type	reason : STRING
		@param	reason : 剔除理由
		"""
		if self.id == suffererID :								# 不能投票踢自己
			WARNING_MSG( "[%s(id:%i)]: Can't vote to kick self out." % ( self.getName(), self.id, ) )
			return
		elif self.isInTeam() :
			self.getTeamMailbox().initiateVoteForKickingMember( self.id, suffererID, reason )

	def voteForKickingTeammateFromClient( self, agree ) :
		"""
		<Exposed method>
		@type	agree : BOOL
		@param	agree : 是否同意
		"""
		if self.isInTeam() :
			self.getTeamMailbox().memberVoteForKicking( self.id, agree )
