# -*- coding: gb18030 -*-

# python
import time
# bigworld
import BigWorld
# common
import csconst
import csdefine
import csstatus
from bwdebug import INFO_MSG, ERROR_MSG
# cell
import ECBExtend
from CellSpaceCopyFormulas import spaceCopyFormulas
from Resource.SpaceCopyDataLoader import SpaceCopyDataLoader
g_spaceCopyData = SpaceCopyDataLoader.instance()
#from Love3 import g_spaceCopyData

#spaceCopyFormulas.loadCopiesData( "config/matchablecopies.xml" )
COPIES_ACT_FLAG = {}
for copyLabel,summary in spaceCopyFormulas.getCopiesSummary().items(): 
	COPIES_ACT_FLAG[copyLabel] = summary["copyFlag"]


COPIES_DIFFICUTY = {
	"fu_ben_shen_gui_mi_jing" : ( "WuYaoWangEnterType", csconst.SPACE_COPY_YE_WAI_NIGHTMARE ),
	"fu_ben_wu_yao_qian_shao" : ( "WuYaoQianShaoEnterType", csconst.SPACE_COPY_YE_WAI_NIGHTMARE ),
	"fu_ben_wu_yao_wang_bao_zang" : ( "WuYaoWangEnterType", csconst.SPACE_COPY_YE_WAI_NIGHTMARE ),
}

PUNISHED_SKILL_ID = 323249001											# 加上逃跑惩罚buff的技能
PUNISHED_BUFF_ID = 106001												# 逃跑惩罚buff的ID

class CopyMatcherInterface :

	def __init__( self ) :
		self._expectGuider = False										# 玩家是否愿意担任队伍向导 CELL_PRIVATE
		self._expectedDuties = ()										# 这是玩家选择的职责，不代表玩家能担任这些职责 CELL_PRIVATE
		self._expectedCopies = ()										# 这是玩家选择的副本，不代表玩家能前往这些副本 CELL_PRIVATE
		self._haltedRaidResumed = False									# 重排半路副本 CELL_PRIVATE
		self.labelOfMatchedCopy = ""									# 匹配到的副本 CELL_PUBLIC
		self.insideMatchedCopy = False									# 是否在匹配到的副本内 OWN_CLIENT
		if not hasattr( self, "latestMatchedTime" ) :					# 为了适应测试代码，同时防止覆盖引擎的初始化
			self.latestMatchedTime = 0.0								# 最近一次成功匹配的时间（persistent property）OWN_CLIENT
		self._tid_resumeHaltedRaid = 0									# 确认加入半路副本队伍的timerID
		self._camp = 0

	# ----------------------------------------------------------------
	# functions in common
	# ----------------------------------------------------------------
	def isPunishedForEscape( self ) :
		"""
		是否正在遭受逃跑惩罚
		test:1015
		release:106001
		"""
		#return self.findBuffByBuffID( 1015 ) is not None
		return self.findBuffByBuffID( PUNISHED_BUFF_ID ) is not None

	def punishedForEscape( self ) :
		"""
		因为逃离匹配副本而遭受惩罚
		test skill id: 322208001
		release skill id: 323249001
		"""
		INFO_MSG( "[%s(id:%i)]: I am punished for escaping from matched team." % ( self.getName(), self.id, ) )
		#self.spellTarget( 322208001, self.id )
		self.spellTarget( PUNISHED_SKILL_ID, self.id )

	def isForbiddenToMatchNewTeam( self ) :
		"""
		是否当前被禁止去匹配新的副本队伍，例如：
		1、当前正遭受逃跑惩罚；
		2、当前队伍是半途中断的副本队伍
		"""
		return self.isPunishedForEscape() or self._haltedRaidResumed

	def matchIsCooling( self ) :
		"""
		正在冷却中
		"""
		return self.timeTillLastMatched() < csdefine.TIME_LIMIT_OF_MATCHED_INTERVAL

	def timeTillLastMatched( self ) :
		"""
		time till last matched.
		"""
		return time.time() - self.latestMatchedTime

	def recordMatchedTime( self, matchedTime ) :
		"""
		记录最近匹配时间
		"""
		self.latestMatchedTime = matchedTime							# 记录下最近一次匹配的时间
		self.broadcastMatchedTimeToTeammates()

	def broadcastMatchedTimeToTeammates( self ) :
		"""
		将最近匹配时间发送给队友
		"""
		for teammate in self.getTeamMemberMailboxs() :
			if teammate and teammate.id != self.id :
				teammate.client.updateTeammateMatchedTime( self.id, self.latestMatchedTime )

	def broadcastActFlagsToTeammates( self, modifiedFlag ) :
		"""
		将副本活动标记发送给队友
		"""
		for teammate in self.getTeamMemberMailboxs() :
			if teammate and teammate.id != self.id :
				teammate.client.updateTeammateActFlag( self.id, self.activityFlags, modifiedFlag )


	# ----------------------------------------------------------------
	# about join matcher queue
	# ----------------------------------------------------------------
	def setExpectedDuties( self, duties ) :
		"""
		"""
		self._expectedDuties = tuple( duties )

	def getExpectedDuties( self ) :
		"""
		"""
		return self._expectedDuties[:]

	def setExpectedCopies( self, copies ) :
		"""
		<Define method>
		@type		copies : STRING_TUPLE(python tuple)
		@param		copies : 选择的职责
		"""
		self._expectedCopies = tuple( copies )



	def getExpectedCopies( self ) :
		"""
		"""
		return self._expectedCopies[:]

	def setHaltedRaidResumed( self, resumed ) :
		"""
		<Define method>
		@type		resumed : BOOL
		@param		resumed : 是否是重启被中断的副本
		"""
		self._haltedRaidResumed = resumed

	def onMatchedCopyTeam( self, copyLevel, copyLabel ) :
		"""
		<Define method>
		@type		copyLevel : UINT8
		@param		copyLevel : 匹配到的副本
		@type		copyLabel : STRING
		@param		copyLabel : 匹配到的副本
		"""
		self.labelOfMatchedCopy = copyLabel
		self.recordMatchedTime( time.time() )
		inside = self.labelOfMatchedCopy and self.spaceType == self.labelOfMatchedCopy
		self.setInsideMatchedCopy( inside )

	def setInsideMatchedCopy( self, inside ) :
		"""
		<???Define method>NEW
		暂时在onEnterSpace_接口中调用cmi_onEnterSpace，
		在onLeaveSpace_接口中调用cmi_onLeaveSpace来实现
		进入或离开匹配副本的判断和设置，所以这个接口暂时
		不放到def文件中定义。
		@type		inside : BOOL
		@param		inside : 设置是否在匹配副本内
		"""
		if self.insideMatchedCopy != inside :
			self.insideMatchedCopy = inside

#	# ----------------------------------------------------------------
	# queuing operations
	# ----------------------------------------------------------------
	def requestEnterCopyMatcherQueue( self, srcEntityID, duties, copies, camp, expectGuider=False ) :
		"""
		<Exposed method>
		@type		srcEntityID : OBJECT_ID
		@param		srcEntityID : 玩家的ID，由引擎自动传入，不在def中定义
		@type		duties : UINT8_TUPLE(python tuple)
		@param		duties : 选择的职责
		@type		copies : STRING_TUPLE(python tuple)
		@param		copies : 选择的职责
		@type		expectGuider : BOOL
		@param		expectGuider : 是否愿意担任队伍向导
		"""
		if self.id != srcEntityID :
			return
		if self.isForbiddenToMatchNewTeam() :
			return
		if self.matchIsCooling() :
			INFO_MSG( "[%s(id:%i)]: match hasn't cooled down." % ( self.getName(), self.id, ) )
			self.statusMessage( csstatus.CTM_MATCHER_INVALID_TO_PLAYER )
			return
		self._expectGuider = expectGuider
		self.setExpectedDuties( duties )
		self.setExpectedCopies( copies )
		self._camp = camp
		self.base.updateAvgQueueingTimeFromServer()
		if not self.isInTeam() :
			self.joinCopyMatcherAsSingle()
		elif self.isCaptain() :
			self.joinCopyMatcherAsCaptain()
		else :
			ERROR_MSG( "[%s(id:%i,captainID:%s)]: Only captain is allowed to join queue."\
				 % ( self.getName(), self.id, self.captainID ) )
			self.statusMessage( csstatus.CTM_CAPTAIN_NEEDED_TO_REQUEST_QUEUING )

	def joinCopyMatcherAsSingle( self ) :
		"""Player requests to enter team matcher queue.
		"""
		if self.expectedDutiesAndCopiesAreValid() :
			INFO_MSG( "[%s(id:%i)]: OK! Duties and copies Verify success, now enter the queue." % ( self.getName(), self.id ) )
			self.base.joinCopyMatcherAsSingle( self._expectedDuties, self._expectedCopies, self._camp, self._expectGuider )

	def joinCopyMatcherAsCaptain( self ) :
		"""Captain and his teammates request to enter team matcher queue.
		"""
		if self.expectedDutiesAndCopiesAreValid() :
			self.base.joinCopyMatcherAsCaptain( self._expectedDuties, self._expectedCopies, self._camp, self._expectGuider )

	def replySelectingDutiesOf( self, srcEntityID, duties, expectGuider ) :
		"""
		<Exposed method>
		@type		srcEntityID : OBJECT_ID
		@param		srcEntityID : 玩家的ID，由引擎自动传入，不在def中定义
		@type		duties : UINT8_TUPLE(python tuple)
		@param		duties : 选择的职责
		@type		expectGuider : BOOL 
		@param		expectGuider : 是否愿意担任队伍向导
		"""
		if self.id != srcEntityID :
			return
		INFO_MSG( "[%s(id:%i)]: I select these duties: %s." % ( self.getName(), self.id, str( duties ) ) )			# DEBUG_GAN
		if self._haltedRaidResumed :
			self.setHaltedRaidResumed( False )
			self.selectToResumeHaltedRaid( duties, expectGuider )
		else :
			self.undertakeDutiesOf( duties, expectGuider )

	def undertakeDutiesOf( self, duties, expectGuider ) :
		"""
		<Define method>???
		基于中途有队员离开后，可由队长再次发起匹配申请，不用再由
		队员重新选择职责的考虑。
		目前还不需要设计为定义方法，暂时不加到def文件中 2012-07-01
		"""
		if self.isInTeam() :
			self._expectGuider = expectGuider
			self.setExpectedDuties( duties )
			if self.expectedDutiesAndCopiesAreValid() :
				self.base.undertakeDutiesOf( self._expectedDuties, self._expectGuider )
		else :
			ERROR_MSG( "[%s(id:%i)]: I don't have a team at all." % ( self.getName(), self.id ) )

	def selectToResumeHaltedRaid( self, duties, expectGuider ) :
		"""
		排队继续被中断的副本，则不需要判断副本记录是否已用完
		"""
		if self.isInTeam() :
			self._expectGuider = expectGuider
			self.setExpectedDuties( duties )
			if self.canUndertakeDutiesOf( duties ) :
				self.base.undertakeDutiesOf( self._expectedDuties, self._expectGuider )
		else :
			ERROR_MSG( "[%s(id:%i)]: I don't have a team at all." % ( self.getName(), self.id ) )

	def expectedDutiesAndCopiesAreValid( self ) :
		"""
		"""
		if not self.canUndertakeDutiesOf( self._expectedDuties ) :
			return False
		elif not self.canGotoCopiesOf( self._expectedCopies ) :
			return False
		else :
			return True

	def canGotoCopiesOf( self, copies ) :
		"""
		"""
		if len( copies ) == 0 :
			INFO_MSG( "[%s(id:%i)]: copies are empty." % ( self.getName(), self.id ) )
			return False
		else :
			for copyLabel in copies :
				if self.haveConsumedCopyOf( copyLabel ) :
					INFO_MSG( "[%s(id:%i)]: I have consumed this copy:%s."\
				 		% ( self.getName(), self.id, str( copyLabel ) ) )
					return False
				elif self.unmatchCopySummary( copyLabel ) :
					INFO_MSG( "[%s(id:%i)]: I don't match this copy:%s."\
				 		% ( self.getName(), self.id, str( copyLabel ) ) )
					return False
			return True

	def canGotoCopyOf( self, copyLabel ) :
		"""
		"""
		return not ( self.haveConsumedCopyOf( copyLabel ) or self.unmatchCopySummary( copylabel ) )

	def haveConsumedCopyOf( self, copyLabel ) :
		"""
		"""
		actFlag = COPIES_ACT_FLAG.get( copyLabel )
		return actFlag is None or self.isActivityCanNotJoin( actFlag )

	def unmatchCopySummary( self, copyLabel ) :
		"""
		"""
		return not spaceCopyFormulas.checkCopyEnterable( self, copyLabel )

	def canUndertakeDutiesOf( self, duties ) :
		"""Verify if i can undertake these duties."""
		if len( duties ) == 0 :
			INFO_MSG( "[%s(id:%i)]: duties are empty." % ( self.getName(), self.id ) )
			return False
		else :
			competentDuties = self.competentDuties()
			for duty in duties :
				if duty not in competentDuties :
					INFO_MSG( "[%s(id:%i,raceclass:%s)]: I can't undertake this duty:%s."\
				 		% ( self.getName(), self.id, self.getClass(), str( duty ) ) )
					return False
			return True

	def canUndertakeDutyOf( self, duty ) :
		"""Verify if i can undertake duty."""
		return duty in self.competentDuties()

	def competentDuties( self ) :
		"""Get all my competent duties."""
		duties = csconst.CLASS_TO_COPY_DUTIES.get( self.getClass() )
		if duties is not None :
			return duties
		else :
			ERROR_MSG( "[%s(id:%i,raceclass:%s)]: Lack competent duty."\
				 		% ( self.getName(), self.id, self.getClass() ) )
			return ()


#	# ----------------------------------------------------------------
	# update teammate match info
	# ----------------------------------------------------------------
	def cmi_onTeammateJoin( self, teammateBase ) :
		"""
		队友加入队伍
		"""
		if teammateBase.id != self.id :
			teammateBase.client.receiveTeammateMatchInfo( self.id, self.latestMatchedTime, self.activityFlags )


#	# ----------------------------------------------------------------
	# about leave team
	# ----------------------------------------------------------------
	def cmi_onLeaveTeam( self ) :
		"""
		退出了队伍
		"""
		self.handleAfterLeaveTeam()
		if self._haltedRaidResumed :
			self.setHaltedRaidResumed( False )
		if self.labelOfMatchedCopy :
			self.labelOfMatchedCopy = ""
		if self.insideMatchedCopy :
			self.leaveMatchedCopy()

	def handleLeaveTeamOnGiveUpMatch( self ) :
		"""
		放弃半路副本而离队的处理
		"""
		if self.matchIsCooling() :
			self.recordMatchedTime( 0.0 )						# 不记录这次的匹配时间

	def handleLeaveTeamActive( self ) :
		"""
		主动离开队伍的处理
		"""
		if self.labelOfMatchedCopy and self.matchIsCooling() :
			self.punishedForEscape()						# 还没冷却就退队，加上逃跑惩罚

	def handleLeaveTeamOnVoteKicked( self ) :
		"""
		被投票踢出队伍
		"""
		pass

	def handleAfterLeaveTeam( self ) :
		"""
		离队处理
		"""
		reason = self.popTemp( "CMI_Leave_Team_Reason" )
		if reason == csdefine.LEAVE_TEAM_ABANDON_MATCH :
			self.handleLeaveTeamOnGiveUpMatch()
		elif reason == csdefine.LEAVE_TEAM_VOTE_KICKED :
			self.handleLeaveTeamOnVoteKicked()
		else :
			self.handleLeaveTeamActive()

#	# ----------------------------------------------------------------
	# about enter or leave space copy.
	# ----------------------------------------------------------------
	def cmi_onEnterSpace( self ) :
		"""
		"""
		if self.labelOfMatchedCopy and self.spaceType == self.labelOfMatchedCopy :
			self.setInsideMatchedCopy( True )
		if self.isCaptain():
			self.client.shieldTeamDisbanded()

	def cmi_onLeaveSpace( self ) :
		"""
		"""
		if self.insideMatchedCopy :
			self.setInsideMatchedCopy( False )
		if self.isCaptain():
			self.client.cancelShieldTeamDisbanded()

	def shuttleMatchedCopy( self, srcEntityID, enter ) :
		"""
		<Exposed method>???
		传入或者传出匹配副本
		@type	enter : BOOL
		@param	enter : 进入还是离开匹配副本
		"""
		if self.id != srcEntityID :
			return
		if enter :
			self.enterMatchedCopy()
		else :
			self.leaveMatchedCopy()

	def enterMatchedCopy( self ) :
		"""
		请求进入匹配副本
		"""
		if self.insideMatchedCopy :
			ERROR_MSG( "[%s(id:%i)]: I am already in matched copy." % ( self.getName(), self.id ) )
		elif self.labelOfMatchedCopy :
			self.gotoSpace( self.labelOfMatchedCopy, *g_spaceCopyData.birthDataOfCopy(self.labelOfMatchedCopy) )

	def leaveMatchedCopy( self ) :
		"""
		请求离开匹配副本
		"""
		if self.insideMatchedCopy :
			self.gotoForetime()
		else :
			ERROR_MSG( "[%s(id:%i)]: I am not in matched copy currently." % ( self.getName(), self.id ) )

	def teleportCopyOnMatched( self, copyLabel ) :
		"""
		<Define method>???
		传送到匹配的副本
		@type	copyLabel : STRING
		@param	copyLabel : 匹配副本的标签
		"""
		self.setTemp( "CMI_Teleport_On_Match", 1 )								# 设置匹配后自动传送副本标记
		if copyLabel in COPIES_DIFFICUTY :
			self.setTemp( *COPIES_DIFFICUTY[copyLabel] )
		self.gotoSpace( copyLabel, *g_spaceCopyData.birthDataOfCopy(copyLabel) )

	def onEnterMatchedCopy( self, copyLabel, bossesKilled ) :
		"""
		<Define method>
		传送到匹配的副本后回调
		@type	copyLabel : STRING
		@param	copyLabel : 匹配副本的标签
		@type	bossesKilled : UINT8
		@param	bossesKilled : boss击杀数量
		"""
		if self.popTemp("CMI_Teleport_On_Match") :
		#	if self.isCaptain(): #屏蔽队长解散队伍的权限
				#self.client.shieldTeamDisbanded()
			if bossesKilled != 0 :
				INFO_MSG( "[%s(id:%i)]: Space is not pure, ask player continue or quit." % ( self.getName(), self.id, ) )
				bossesTotal = spaceCopyFormulas.totalBossesOf( copyLabel )
				self.client.notifyToConfirmHaltedRaid( copyLabel, bossesKilled, bossesTotal )
				self._tid_resumeHaltedRaid = self.addTimer( csdefine.TIME_LIMIT_OF_CONFIRM_RESUMING, 0, ECBExtend.CTM_CONFIRM_RESUMING_HALTED_RAID )
			else :
				self.addActivityCount( COPIES_ACT_FLAG[copyLabel] )

	def onLeaveMatchedCopy( self ):
		"""
		<Define method>
		"""
		#if self.isCaptain():
			#self.client.cancelShieldTeamDisbanded() #取消屏蔽队长解散队伍的权限
		pass

	def onTimer_joinHaltedRaid( self, timerID, cbid ) :
		"""
		确认加入半路副本的匹配队伍时间到
		"""
		assert( self._tid_resumeHaltedRaid == timerID )
		assert( ECBExtend.CTM_CONFIRM_RESUMING_HALTED_RAID == cbid )
		self.partakeInHaltedRaid()
		self._tid_resumeHaltedRaid = 0

	def confirmJoiningHaltedRaid( self, srcEntityID, agree ) :
		"""
		<Exposed method>???
		传入或者传出匹配副本
		@type	agree : BOOL
		@param	agree : 确认是否加入半路副本，用于玩家传入匹配的半路
						副本时，给予玩家再次匹配确认框。
		"""
		if srcEntityID != self.id :
			return
		if self._tid_resumeHaltedRaid :
			self.cancel( self._tid_resumeHaltedRaid )
			self._tid_resumeHaltedRaid = 0
			if agree :
				self.partakeInHaltedRaid()
			else :
				self.giveUpHaltedRaid()
		else :
			INFO_MSG( "[%s(id:%i)]: Confirm halted raid timeout." % ( self.getName(), self.id, ) )
			self.statusMessage( csstatus.CTM_RESUME_RAID_TIMEOUT )

	def partakeInHaltedRaid( self ) :
		"""
		同意加入匹配到的副本
		"""
		if self.labelOfMatchedCopy :
			self.addActivityCount( COPIES_ACT_FLAG[self.labelOfMatchedCopy] )

	def giveUpHaltedRaid( self ) :
		"""
		放弃加入匹配到的半路副本
		"""
		if self.labelOfMatchedCopy :
			if self.isInTeam() :
				self.setTemp( "CMI_Leave_Team_Reason", csdefine.LEAVE_TEAM_ABANDON_MATCH )
				self.teamMailbox.leave( self.id, self.id )
			elif self.insideMatchedCopy :
				self.leaveMatchedCopy()

	def leaveTeamOnKicked( self ) :
		"""
		<Define method>
		被投票踢出队伍
		"""
		if self.isInTeam() :
			self.setTemp( "CMI_Leave_Team_Reason", csdefine.LEAVE_TEAM_VOTE_KICKED )
			self.teamMailbox.leave( self.id, self.id )

	def onMatchedRaidFinished( self ) :
		"""
		<Define method>
		副本raid结束时调用
		"""
		self.labelOfMatchedCopy = ""
		if self.isCaptain():
			self.client.cancelShieldTeamDisbanded()
		self.client.onMatchedRaidFinished()
		
