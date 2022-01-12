# -*- coding: gb18030 -*-

import csdefine
from Time import Time
from bwdebug import INFO_MSG, ERROR_MSG
from gbref import rds
import event.EventCenter as ECenter
from MessageBox import *
from config.client.msgboxtexts import Datas as mbmsgs
from bwdebug import *
import Define

class CopyMatcherInterface :

	def __init__( self ) :
		self.matchStatus = csdefine.MATCH_STATUS_PERSONAL_NORMAL
		self.levelOfMatchedCopy = 0					# 匹配副本的等级（不会随着队长的改变而改变）
		self.labelOfMatchedCopy = ""				# 匹配的副本名称
		self.matchedMembersDuty = {}				# 玩家匹配到的职责（匹配的队伍这个参数才有效）
		self.insideMatchedCopy = False				# 在匹配的副本里
		if not hasattr( self, "latestMatchedTime" ) :	# 为了适应测试代码，同时防止覆盖引擎的初始化
			self.latestMatchedTime = 0					# 最近一次成功匹配的时间（persistent property）OWN_CLIENT
		self.teammatesMatchInfo = {}					# 队友的匹配信息{teammateID:(latestMatchedTime,activityFlags)}
		self.queueingDuties = []						# 队伍匹配过程中的职务列表

	# ----------------------------------------------------------------
	# functions in common
	# ----------------------------------------------------------------
	def setMatchStatus( self, status ) :
		"""
		匹配状态改变，服务器自动通知
		"""
		INFO_MSG( "set %s status to %i" % ( self.getName(), status ) )
		self.matchStatus = status

	def updateMatchStatusFromServer( self, oldStatus, newStatus ) :
		"""
		<Define method>
		@type		oldStatus : UINT8
		@param		oldStatus : 旧状态
		@type		newStatus : UINT8
		@param		newStatus : 新状态
		"""
		self.setMatchStatus( newStatus )
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_STATUS_CHANGE", oldStatus, newStatus )

	def shieldTeamDisbanded(self):
		"""
		<Define method>
		"""
		DEBUG_MSG("EVT_ON_COPYMATCHER_SHIELD_TEAM_DISBANDED")
		ECenter.fireEvent("EVT_ON_COPYMATCHER_SHIELD_TEAM_DISBANDED")
	
	def cancelShieldTeamDisbanded( self ):
		"""
		<Define method>
		"""
		DEBUG_MSG("EVT_ON_COPYMATCHER_CANCAL_SHIELD_TEAM_DISBANDED")
		ECenter.fireEvent("EVT_ON_COPYMATCHER_CANCAL_SHIELD_TEAM_DISBANDED")

	def set_insideMatchedCopy( self, oldValue ) :
		"""
		This method invoked automatically from server when value of insideMatchedCopy changed.
		"""
		INFO_MSG("Inside copy label changed. from %s to %s" % ( oldValue, self.insideMatchedCopy ))
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_INSIDECOPY_CHANGE", oldValue, self.insideMatchedCopy )

	def hideConfirmWindow( self ):
		"""
		<Exposed method>
		"""
		INFO_MSG("hide ConfirmWindow or show matchingWindow")
		ECenter.fireEvent("EVT_ON_COPYMATCHER_HIDE_WINDOW")
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_CONFIRM_TIMEOUT" )

	def isMatchStatus( self, status ) :
		"""
		"""
		return self.matchStatus == status

	def isInMatching( self ) :
		"""
		"""
		return self.matchStatus == csdefine.MATCH_STATUS_PERSONAL_MATCHING

	def isSelectingDuty( self ) :
		"""
		"""
		return self.matchStatus == csdefine.MATCH_STATUS_PERSONAL_SELECTING_DUTY

	def isConfirmingMatch( self ) :
		"""
		"""
		return self.matchStatus == csdefine.MATCH_STATUS_PERSONAL_CONFIRMING

	def isInsideCopy( self ) :
		"""
		"""
		return self.insideMatchedCopy

	def isTeamVacant( self ) :
		"""
		"""
		return len( self.teamMember ) < csconst.TEAM_MEMBER_MAX

	def timeTillCooldown( self ) :
		"""
		离冷却还剩多久（单位：秒）
		"""
		return max( 0, csdefine.TIME_LIMIT_OF_MATCHED_INTERVAL - self.timeTillLastMatched() )

	def cooldownType( self ) :
		"""
		"""
		pass

	def matchIsCooldown( self ) :
		"""
		角色是否在非冷却状态
		"""
		return self.timeTillLastMatched() > csdefine.TIME_LIMIT_OF_MATCHED_INTERVAL

	def timeTillLastMatched( self ) :
		"""
		time till last matched.
		"""
		return Time.time() - self.latestMatchedTime
	
	def teammateIsCooldown( self, teammateID ):
		"""
		队友是否在非冷却状态
		"""
		return self.teammateTillLastMatched( teammateID ) > csdefine.TIME_LIMIT_OF_MATCHED_INTERVAL
	
	def teammateTillLastMatched( self, teammateID ):
		"""
		获取队友已冷却时间
		"""
		mateMatchInfo = self.teammatesMatchInfo.get( teammateID, None )
		if mateMatchInfo:
			return Time.time() - mateMatchInfo[0]

#	# teammate match info --------------------------------------------
	# teammate match info
	# ----------------------------------------------------------------
	def receiveTeammateMatchInfo( self, teammateID, latestMatchedTime, activityFlags ) :
		"""
		<Define method>
		一个队员加入时会通过这个方法更新队员的匹配信息
		@type		teammateID : OBJECT_ID
		@param		teammateID : 队友的ID
		@type		lastestMatchedTime : FLOAT
		@param		lastestMatchedTime : 最近一次匹配时间
		@type		activityFlags : INT32
		@param		activityFlags : 副本活动标记
		"""
		INFO_MSG("[%s]: receive teammate(ID:%i) match info: latestMatchedTime %.2f, activityFlags %i" %\
			(self.getName(), teammateID, latestMatchedTime, activityFlags) )
		self.teammatesMatchInfo[teammateID] = ( latestMatchedTime, activityFlags )

	def updateTeammateMatchedTime( self, teammateID, latestMatchedTime ) :
		"""
		<Define method>
		队员的最近匹配时间改变时会通过这个方法更新队员的匹配信息
		@type		lastestMatchedTime : FLOAT
		@param		lastestMatchedTime : 最近一次匹配时间
		"""
		INFO_MSG("[%s]: update teammate(ID:%i) matched time: latestMatchedTime %.2f" %\
			(self.getName(), teammateID, latestMatchedTime) )
		matchInfo = self.teammatesMatchInfo.get( teammateID )
		if matchInfo :
			self.teammatesMatchInfo[teammateID] = ( latestMatchedTime, matchInfo[1] )
		else :
			ERROR_MSG("Player(ID:%i) is not my teammate." % teammateID)

	def updateTeammateActFlag( self, teammateID, activityFlags, modifiedFlag ) :
		"""
		<Define method>
		队员的活动标记改变时会通过这个方法更新队员的匹配信息
		@type		activityFlags : INT32
		@param		activityFlags : 副本活动标记
		@type		modifiedFlag : INT32
		@param		modifiedFlag : 发生改变的活动标记
		"""
		INFO_MSG("[%s]: update teammate(ID:%i) actFlags: activityFlags %i, modifiedFlag %i" %\
			(self.getName(), teammateID, activityFlags, modifiedFlag) )
		matchInfo = self.teammatesMatchInfo.get( teammateID )
		if matchInfo :
			self.teammatesMatchInfo[teammateID] = ( matchInfo[0], activityFlags )
		else :
			ERROR_MSG("Player(ID:%i) is not my teammate." % teammateID)

	def teammateHasConsumedAct( self, teammateID, actFlag ) :
		"""
		队友是否已经消耗完某个活动的参与权限，由于副本和活动混在
		了一起，因此判断某个副本是否还有剩余进入次数也用这个接口
		"""
		if teammateID in self.teammatesMatchInfo :
			return self.teammatesMatchInfo[teammateID][1] & ( 1 << actFlag )
		else :
			ERROR_MSG("Player(ID:%i) is not my teammate." % teammateID)
			return True

	def cmi_onTeammateLeave( self, teammateID ) :
		"""
		队友离队
		"""
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_TEAMMATE_LEAVE", teammateID )

	def cmi_onTeammateJoin( self, teammateID ) :
		"""
		队友加队
		"""
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_TEAMMATE_JOIN", teammateID )

	def cmi_onTeammateLogout( self, teammateID ) :
		"""
		队友下线
		"""
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_TEAMMATE_LOGOUT", teammateID )

	def cmi_onTeammateLogon( self, oldTeammateID, newTeammateID ) :
		"""
		队友上线
		"""
		if oldTeammateID in self.matchedMembersDuty :
			self.matchedMembersDuty[newTeammateID] = self.matchedMembersDuty.pop( oldTeammateID )

	def cmi_onLeaveTeam( self ) :
		"""
		离开队伍
		"""
		if self.labelOfMatchedCopy :
			self.updateMatchedCopyInfo( "", 0, {} )
		#if self.isSelectingDuty() :
		self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_NORMAL )

	def cmi_onJoinTeam( self ) :
		"""
		加入队伍
		"""
		pass
		
	def set_activityFlags( self, oldFalgs ) :
		"""
		活动标记改变
		"""
		INFO_MSG("[%s]: update actFlags: oldFalgs %i, newFlag %i" %\
			(self.getName(), oldFalgs, self.activityFlags ) )

#	# join queue -----------------------------------------------------
	# join queue
	# ----------------------------------------------------------------
	def requestEnterCopyMatcherQueue( self, duties, copies, camp, expectGuider ) :
		"""
		向服务器请求进入副本组队系统
		"""
		self.cell.requestEnterCopyMatcherQueue( duties, copies, camp, expectGuider )

	def selectDutiesOf( self, duties, expectGuider ) :
		"""
		回复服务器的职责选择请求
		"""
		self.cell.replySelectingDutiesOf( duties, expectGuider )

	def notifyToSelectDutiesFromServer( self, copies ) :
		"""
		<Define method>
		"""
		INFO_MSG( "Server notify client(%s) to select duties." % self.getName() )
		ECenter.fireEvent( "EVT_ON_CHANGE_SELECTING_DUTY_STATUS", copies )


	def cancelSelectingDutiesFromServer( self ) :
		"""
		<Define method>
		"""
		INFO_MSG( "Server cancel client(%s) selecting duties." % self.getName() )
		ECenter.fireEvent( "EVT_ON_CANCEL_SELECTING_DUTY_STATUS" )


	def refuseToUndertakeAnyDuty( self ) :
		"""
		拒绝选择职责
		"""
		self.base.refuseToUndertakeAnyDuty()

	def leaveCopyMatcherQueue( self ) :
		"""
		主动要求离开队列
		"""
		if self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_MATCHING ) :
			self.base.leaveCopyMatcherQueue()

	def flashQueueingDutiesFromServer( self, queueingDuties ) :
		"""
		<Define method>
		@type		queueingDuties : UINT8_ARRAY
		@param		queueingDuties : 排队匹配到的职责
		"""
		self.queueingDuties = queueingDuties
		INFO_MSG( "Server update client(%s) duties in queueing group: %s." % ( self.getName(), str( queueingDuties ) ) )
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_FLASH_QUEUE_DUTIES", queueingDuties )

	def updateAvgQueueingTimeFromServer( self, avgTime ) :
		"""
		<Define method>NEW
		@type		avgTime : FLOAT
		@param		avgTime : 平均等待时间
		"""
		INFO_MSG( "Server update client(%s) average queueing duties. time: %.1f" % ( self.getName(), avgTime ) )
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_UPDATE_AVG_QUEUE_TIME", avgTime )

	def onJoinCopyMatcherQueue( self, expectedDuties ) :
		"""
		<Define method>NEW
		@type		expectedDuties : UINT8_TUPLE
		@param		expectedDuties : 在队列中的职责
		"""
		INFO_MSG( "Server notify client(%s) join copy matcher queue with expected duties %s." % ( self.getName(), str( expectedDuties ) ) )


#	# after matched --------------------------------------------------
	# after matched
	# ----------------------------------------------------------------
	def notifyToConfirmCopyMatchedFromServer( self, duty, copyLabel, copyLevel, bossesTotal, bossesKilled, copies ) :
		"""
		<Define method>
		@type		duty : UINT8
		@param		duty : 匹配的职责
		@type		copyLabel : STRING
		@param		copyLabel : 副本名称
		@type		copyLevel : UINT8
		@param		copyLevel : 副本等级
		@type		bossesTotal : UINT8
		@param		bossesTotal : 副本BOSS总数
		@type		bossesKilled : UINT8
		@param		bossesKilled : 副本BOSS已击杀数量
		"""
		INFO_MSG( "Server notify client(%s) to confirm matched.(duty:%i,copyLabel:%s,copyLevel:%s,bosses total:%i,bosses killed:%i)"\
			 % ( self.getName(), duty, copyLabel, copyLevel, bossesTotal, bossesKilled ) )
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_NOTIFY_CONFIRM", duty, copyLabel, copyLevel, bossesTotal, bossesKilled, copies )

	def confirmCopyMatched( self, accept ) :
		"""
		确认匹配
		"""
		self.base.confirmCopyMatchedFromClient( accept )

	def receiveMatchedInfomationFromServer( self, info, copyLabelNum ) :
		"""
		<Define method>
		接收匹配玩家的信息
		@type		info : python dict
		@param		info : 所有匹配玩家的匹配信息
		"""
		INFO_MSG( "Server notify client(%s) matched members.(members:%s)" % ( self.getName(), str( info ) ) )
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_RECEIVE_MATCHED_INFO", info, copyLabelNum )

	def updateMatchedConfirmationFromServer( self, plyaerID, needConfirms, confirmation, copyLabelNum ) :
		"""
		<Define method>
		更新其他玩家的职责确认情况
		@type		playerID : OBJECT_ID
		@param		playerID : 玩家的ID
		@type		confirmation : UINT8
		@param		confirmation : 职责确认状态
		"""
		INFO_MSG( "Server update client(%s) confirmation of matched member.(copyLabelNum:%i,confirmation:%s)"\
			 % ( self.getName(), needConfirms, confirmation ) )
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_UPDATE_CONFIRM_INFO", plyaerID, needConfirms, confirmation, copyLabelNum )

	def onMatchedConfirmTimeout( self ) :
		"""
		<Define method>
		职责确认超时
		"""
		INFO_MSG( "Server notify matched confirm timeout.( player: %s, id: %i )"\
			 % ( self.getName(), self.id ) )
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_CONFIRM_TIMEOUT" )

	def set_latestMatchedTime( self, oldTime ) :
		"""
		<Define method>
		@type		time : FLOAT
		@param		time : 最后一次匹配的时间
		"""
		INFO_MSG( "[%s]: latestMatchedTime changed, current is %f"\
			 % ( self.getName(), self.latestMatchedTime ) )

	def updateMatchedCopyInfo( self, copyLabel, copyLevel, memberToDuty ) :
		"""
		<Define method>
		@type		copyLabel : STRING
		@param		copyLabel : 副本名称
		@type		copyLevel : UINT8
		@param		copyLevel : 副本等级
		@type		memberToDuty : PY_DICT
		@param		memberToDuty : 队员职责
		"""
		INFO_MSG( "Server update client(%s) matched info, copy label: %s, copy level: %i, duty map: %s"\
			 % ( self.getName(), copyLabel, copyLevel, str( memberToDuty ) ) )
		self.labelOfMatchedCopy = copyLabel
		self.levelOfMatchedCopy = copyLevel
		self.matchedMembersDuty = memberToDuty
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_UPDATE_MATCHED_COPYINFO", copyLabel, copyLevel, memberToDuty )

	def resumeHaltedRaid( self, teamID, camp ) :
		"""
		排队组人以继续中断的副本
		"""
		self.base.resumeHaltedRaid( self.teamID, self.getCamp() )

	def notifyToConfirmHaltedRaid( self, copyLabel, bossesKilled, bossesTotal ) :
		"""
		<Define method>
		确认是否要继续招募者的半路副本，需要使用1分钟倒计时确认窗口
		@type		copyLabel : STRING
		@param		copyLabel : 副本名称
		@type		bossesKilled : UINT8
		@param		bossesKilled : 副本BOSS已击杀数量
		@type		bossesTotal : UINT8
		@param		bossesTotal : 副本BOSS总数
		"""
		INFO_MSG( "Server confirms client(%s) to join recruiter copy %s. bossesKilled: %i, bossesTotal: %i."\
			 % ( self.getName(), copyLabel, bossesKilled, bossesTotal ) )
		copyFormulas = rds.spaceCopyFormulas
		copiesSummary = copyFormulas.getCopiesSummary()
		summary = copiesSummary.get( copyLabel )
		if summary is None:return
		copyName = summary["copyName"]
		def notarize( id ) :
			agree = False
			if id == RS_YES :
				agree = True
				self.confirmJoiningHaltedRaid( agree )
		msg = mbmsgs[0x0f13]%( copyName, bossesKilled, bossesTotal )
		showAutoHideMessage( 60, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def confirmJoiningHaltedRaid( self, agree ) :
		"""
		回复确认加入半路副本
		"""
		self.cell.confirmJoiningHaltedRaid( agree )

	def shuttleMatchedCopy( self, enter ) :
		"""
		传入、传出匹配副本
		"""
		self.cell.shuttleMatchedCopy( enter )

#	# kickiing vote --------------------------------------------------
	# 投票踢人相关操作
	# ----------------------------------------------------------------
	def initiateVoteForKickingTeammate( self, suffererID, reason ) :
		"""
		发起剔除队友的投票
		"""
		self.base.initiateVoteForKickingTeammate( suffererID, reason )

	def notifyToVoteForKickingTeammate( self, initiatorID, suffererID, reason ) :
		"""
		<Exposed method>
		@type	initiatorID : OBJECT_ID
		@param	initiatorID : 投票踢人发起者的ID
		@type	suffererID : OBJECT_ID
		@param	suffererID : 被剔除对象的ID
		@type	reason : STRING
		@param	reason : 剔除理由
		"""
		INFO_MSG( "Someone(%i) initiate %s(%i) to vote for kicking teammate(%i) with reason %s."\
			 % ( initiatorID, self.getName(), self.id, suffererID, reason ) )
		ECenter.fireEvent( "EVT_ON_KICKVOTE_WND_SHOW", initiatorID, suffererID, reason )

	def voteToKickTeammate( self, agree ) :
		"""
		投票剔除队友
		"""
		self.base.voteForKickingTeammateFromClient( agree )

	def cancelVoteForKicking( self ) :
		"""
		<Define method>
		终止踢人投票
		"""
		INFO_MSG( "Cancel %s voting for kicking from server." % self.getName() )
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_CANCEL_VOTE_KICKING" )


#	# on raid finish -------------------------------------------------
	# on raid finish
	# ----------------------------------------------------------------
	def onMatchedRaidFinished( self ) :
		"""
		<Define method>
		服务器通知匹配到的副本Raid结束了
		"""
		INFO_MSG( "Matched raid is finished." )
		self.updateMatchedCopyInfo( "", 0, {} )

	def gainRightToResumeHaltedRaid( self ) :
		"""
		<Define method>NEW
		获得重排被中断的副本Raid的资格
		"""
		pass