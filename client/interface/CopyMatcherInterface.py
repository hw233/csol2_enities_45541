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
		self.levelOfMatchedCopy = 0					# ƥ�丱���ĵȼ����������Ŷӳ��ĸı���ı䣩
		self.labelOfMatchedCopy = ""				# ƥ��ĸ�������
		self.matchedMembersDuty = {}				# ���ƥ�䵽��ְ��ƥ��Ķ��������������Ч��
		self.insideMatchedCopy = False				# ��ƥ��ĸ�����
		if not hasattr( self, "latestMatchedTime" ) :	# Ϊ����Ӧ���Դ��룬ͬʱ��ֹ��������ĳ�ʼ��
			self.latestMatchedTime = 0					# ���һ�γɹ�ƥ���ʱ�䣨persistent property��OWN_CLIENT
		self.teammatesMatchInfo = {}					# ���ѵ�ƥ����Ϣ{teammateID:(latestMatchedTime,activityFlags)}
		self.queueingDuties = []						# ����ƥ������е�ְ���б�

	# ----------------------------------------------------------------
	# functions in common
	# ----------------------------------------------------------------
	def setMatchStatus( self, status ) :
		"""
		ƥ��״̬�ı䣬�������Զ�֪ͨ
		"""
		INFO_MSG( "set %s status to %i" % ( self.getName(), status ) )
		self.matchStatus = status

	def updateMatchStatusFromServer( self, oldStatus, newStatus ) :
		"""
		<Define method>
		@type		oldStatus : UINT8
		@param		oldStatus : ��״̬
		@type		newStatus : UINT8
		@param		newStatus : ��״̬
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
		����ȴ��ʣ��ã���λ���룩
		"""
		return max( 0, csdefine.TIME_LIMIT_OF_MATCHED_INTERVAL - self.timeTillLastMatched() )

	def cooldownType( self ) :
		"""
		"""
		pass

	def matchIsCooldown( self ) :
		"""
		��ɫ�Ƿ��ڷ���ȴ״̬
		"""
		return self.timeTillLastMatched() > csdefine.TIME_LIMIT_OF_MATCHED_INTERVAL

	def timeTillLastMatched( self ) :
		"""
		time till last matched.
		"""
		return Time.time() - self.latestMatchedTime
	
	def teammateIsCooldown( self, teammateID ):
		"""
		�����Ƿ��ڷ���ȴ״̬
		"""
		return self.teammateTillLastMatched( teammateID ) > csdefine.TIME_LIMIT_OF_MATCHED_INTERVAL
	
	def teammateTillLastMatched( self, teammateID ):
		"""
		��ȡ��������ȴʱ��
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
		һ����Ա����ʱ��ͨ������������¶�Ա��ƥ����Ϣ
		@type		teammateID : OBJECT_ID
		@param		teammateID : ���ѵ�ID
		@type		lastestMatchedTime : FLOAT
		@param		lastestMatchedTime : ���һ��ƥ��ʱ��
		@type		activityFlags : INT32
		@param		activityFlags : ��������
		"""
		INFO_MSG("[%s]: receive teammate(ID:%i) match info: latestMatchedTime %.2f, activityFlags %i" %\
			(self.getName(), teammateID, latestMatchedTime, activityFlags) )
		self.teammatesMatchInfo[teammateID] = ( latestMatchedTime, activityFlags )

	def updateTeammateMatchedTime( self, teammateID, latestMatchedTime ) :
		"""
		<Define method>
		��Ա�����ƥ��ʱ��ı�ʱ��ͨ������������¶�Ա��ƥ����Ϣ
		@type		lastestMatchedTime : FLOAT
		@param		lastestMatchedTime : ���һ��ƥ��ʱ��
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
		��Ա�Ļ��Ǹı�ʱ��ͨ������������¶�Ա��ƥ����Ϣ
		@type		activityFlags : INT32
		@param		activityFlags : ��������
		@type		modifiedFlag : INT32
		@param		modifiedFlag : �����ı�Ļ���
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
		�����Ƿ��Ѿ�������ĳ����Ĳ���Ȩ�ޣ����ڸ����ͻ����
		��һ������ж�ĳ�������Ƿ���ʣ��������Ҳ������ӿ�
		"""
		if teammateID in self.teammatesMatchInfo :
			return self.teammatesMatchInfo[teammateID][1] & ( 1 << actFlag )
		else :
			ERROR_MSG("Player(ID:%i) is not my teammate." % teammateID)
			return True

	def cmi_onTeammateLeave( self, teammateID ) :
		"""
		�������
		"""
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_TEAMMATE_LEAVE", teammateID )

	def cmi_onTeammateJoin( self, teammateID ) :
		"""
		���ѼӶ�
		"""
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_TEAMMATE_JOIN", teammateID )

	def cmi_onTeammateLogout( self, teammateID ) :
		"""
		��������
		"""
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_TEAMMATE_LOGOUT", teammateID )

	def cmi_onTeammateLogon( self, oldTeammateID, newTeammateID ) :
		"""
		��������
		"""
		if oldTeammateID in self.matchedMembersDuty :
			self.matchedMembersDuty[newTeammateID] = self.matchedMembersDuty.pop( oldTeammateID )

	def cmi_onLeaveTeam( self ) :
		"""
		�뿪����
		"""
		if self.labelOfMatchedCopy :
			self.updateMatchedCopyInfo( "", 0, {} )
		#if self.isSelectingDuty() :
		self.setMatchStatus( csdefine.MATCH_STATUS_PERSONAL_NORMAL )

	def cmi_onJoinTeam( self ) :
		"""
		�������
		"""
		pass
		
	def set_activityFlags( self, oldFalgs ) :
		"""
		���Ǹı�
		"""
		INFO_MSG("[%s]: update actFlags: oldFalgs %i, newFlag %i" %\
			(self.getName(), oldFalgs, self.activityFlags ) )

#	# join queue -----------------------------------------------------
	# join queue
	# ----------------------------------------------------------------
	def requestEnterCopyMatcherQueue( self, duties, copies, camp, expectGuider ) :
		"""
		�������������븱�����ϵͳ
		"""
		self.cell.requestEnterCopyMatcherQueue( duties, copies, camp, expectGuider )

	def selectDutiesOf( self, duties, expectGuider ) :
		"""
		�ظ���������ְ��ѡ������
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
		�ܾ�ѡ��ְ��
		"""
		self.base.refuseToUndertakeAnyDuty()

	def leaveCopyMatcherQueue( self ) :
		"""
		����Ҫ���뿪����
		"""
		if self.isMatchStatus( csdefine.MATCH_STATUS_PERSONAL_MATCHING ) :
			self.base.leaveCopyMatcherQueue()

	def flashQueueingDutiesFromServer( self, queueingDuties ) :
		"""
		<Define method>
		@type		queueingDuties : UINT8_ARRAY
		@param		queueingDuties : �Ŷ�ƥ�䵽��ְ��
		"""
		self.queueingDuties = queueingDuties
		INFO_MSG( "Server update client(%s) duties in queueing group: %s." % ( self.getName(), str( queueingDuties ) ) )
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_FLASH_QUEUE_DUTIES", queueingDuties )

	def updateAvgQueueingTimeFromServer( self, avgTime ) :
		"""
		<Define method>NEW
		@type		avgTime : FLOAT
		@param		avgTime : ƽ���ȴ�ʱ��
		"""
		INFO_MSG( "Server update client(%s) average queueing duties. time: %.1f" % ( self.getName(), avgTime ) )
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_UPDATE_AVG_QUEUE_TIME", avgTime )

	def onJoinCopyMatcherQueue( self, expectedDuties ) :
		"""
		<Define method>NEW
		@type		expectedDuties : UINT8_TUPLE
		@param		expectedDuties : �ڶ����е�ְ��
		"""
		INFO_MSG( "Server notify client(%s) join copy matcher queue with expected duties %s." % ( self.getName(), str( expectedDuties ) ) )


#	# after matched --------------------------------------------------
	# after matched
	# ----------------------------------------------------------------
	def notifyToConfirmCopyMatchedFromServer( self, duty, copyLabel, copyLevel, bossesTotal, bossesKilled, copies ) :
		"""
		<Define method>
		@type		duty : UINT8
		@param		duty : ƥ���ְ��
		@type		copyLabel : STRING
		@param		copyLabel : ��������
		@type		copyLevel : UINT8
		@param		copyLevel : �����ȼ�
		@type		bossesTotal : UINT8
		@param		bossesTotal : ����BOSS����
		@type		bossesKilled : UINT8
		@param		bossesKilled : ����BOSS�ѻ�ɱ����
		"""
		INFO_MSG( "Server notify client(%s) to confirm matched.(duty:%i,copyLabel:%s,copyLevel:%s,bosses total:%i,bosses killed:%i)"\
			 % ( self.getName(), duty, copyLabel, copyLevel, bossesTotal, bossesKilled ) )
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_NOTIFY_CONFIRM", duty, copyLabel, copyLevel, bossesTotal, bossesKilled, copies )

	def confirmCopyMatched( self, accept ) :
		"""
		ȷ��ƥ��
		"""
		self.base.confirmCopyMatchedFromClient( accept )

	def receiveMatchedInfomationFromServer( self, info, copyLabelNum ) :
		"""
		<Define method>
		����ƥ����ҵ���Ϣ
		@type		info : python dict
		@param		info : ����ƥ����ҵ�ƥ����Ϣ
		"""
		INFO_MSG( "Server notify client(%s) matched members.(members:%s)" % ( self.getName(), str( info ) ) )
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_RECEIVE_MATCHED_INFO", info, copyLabelNum )

	def updateMatchedConfirmationFromServer( self, plyaerID, needConfirms, confirmation, copyLabelNum ) :
		"""
		<Define method>
		����������ҵ�ְ��ȷ�����
		@type		playerID : OBJECT_ID
		@param		playerID : ��ҵ�ID
		@type		confirmation : UINT8
		@param		confirmation : ְ��ȷ��״̬
		"""
		INFO_MSG( "Server update client(%s) confirmation of matched member.(copyLabelNum:%i,confirmation:%s)"\
			 % ( self.getName(), needConfirms, confirmation ) )
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_UPDATE_CONFIRM_INFO", plyaerID, needConfirms, confirmation, copyLabelNum )

	def onMatchedConfirmTimeout( self ) :
		"""
		<Define method>
		ְ��ȷ�ϳ�ʱ
		"""
		INFO_MSG( "Server notify matched confirm timeout.( player: %s, id: %i )"\
			 % ( self.getName(), self.id ) )
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_CONFIRM_TIMEOUT" )

	def set_latestMatchedTime( self, oldTime ) :
		"""
		<Define method>
		@type		time : FLOAT
		@param		time : ���һ��ƥ���ʱ��
		"""
		INFO_MSG( "[%s]: latestMatchedTime changed, current is %f"\
			 % ( self.getName(), self.latestMatchedTime ) )

	def updateMatchedCopyInfo( self, copyLabel, copyLevel, memberToDuty ) :
		"""
		<Define method>
		@type		copyLabel : STRING
		@param		copyLabel : ��������
		@type		copyLevel : UINT8
		@param		copyLevel : �����ȼ�
		@type		memberToDuty : PY_DICT
		@param		memberToDuty : ��Աְ��
		"""
		INFO_MSG( "Server update client(%s) matched info, copy label: %s, copy level: %i, duty map: %s"\
			 % ( self.getName(), copyLabel, copyLevel, str( memberToDuty ) ) )
		self.labelOfMatchedCopy = copyLabel
		self.levelOfMatchedCopy = copyLevel
		self.matchedMembersDuty = memberToDuty
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_UPDATE_MATCHED_COPYINFO", copyLabel, copyLevel, memberToDuty )

	def resumeHaltedRaid( self, teamID, camp ) :
		"""
		�Ŷ������Լ����жϵĸ���
		"""
		self.base.resumeHaltedRaid( self.teamID, self.getCamp() )

	def notifyToConfirmHaltedRaid( self, copyLabel, bossesKilled, bossesTotal ) :
		"""
		<Define method>
		ȷ���Ƿ�Ҫ������ļ�ߵİ�·��������Ҫʹ��1���ӵ���ʱȷ�ϴ���
		@type		copyLabel : STRING
		@param		copyLabel : ��������
		@type		bossesKilled : UINT8
		@param		bossesKilled : ����BOSS�ѻ�ɱ����
		@type		bossesTotal : UINT8
		@param		bossesTotal : ����BOSS����
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
		�ظ�ȷ�ϼ����·����
		"""
		self.cell.confirmJoiningHaltedRaid( agree )

	def shuttleMatchedCopy( self, enter ) :
		"""
		���롢����ƥ�丱��
		"""
		self.cell.shuttleMatchedCopy( enter )

#	# kickiing vote --------------------------------------------------
	# ͶƱ������ز���
	# ----------------------------------------------------------------
	def initiateVoteForKickingTeammate( self, suffererID, reason ) :
		"""
		�����޳����ѵ�ͶƱ
		"""
		self.base.initiateVoteForKickingTeammate( suffererID, reason )

	def notifyToVoteForKickingTeammate( self, initiatorID, suffererID, reason ) :
		"""
		<Exposed method>
		@type	initiatorID : OBJECT_ID
		@param	initiatorID : ͶƱ���˷����ߵ�ID
		@type	suffererID : OBJECT_ID
		@param	suffererID : ���޳������ID
		@type	reason : STRING
		@param	reason : �޳�����
		"""
		INFO_MSG( "Someone(%i) initiate %s(%i) to vote for kicking teammate(%i) with reason %s."\
			 % ( initiatorID, self.getName(), self.id, suffererID, reason ) )
		ECenter.fireEvent( "EVT_ON_KICKVOTE_WND_SHOW", initiatorID, suffererID, reason )

	def voteToKickTeammate( self, agree ) :
		"""
		ͶƱ�޳�����
		"""
		self.base.voteForKickingTeammateFromClient( agree )

	def cancelVoteForKicking( self ) :
		"""
		<Define method>
		��ֹ����ͶƱ
		"""
		INFO_MSG( "Cancel %s voting for kicking from server." % self.getName() )
		ECenter.fireEvent( "EVT_ON_COPYMATCHER_CANCEL_VOTE_KICKING" )


#	# on raid finish -------------------------------------------------
	# on raid finish
	# ----------------------------------------------------------------
	def onMatchedRaidFinished( self ) :
		"""
		<Define method>
		������֪ͨƥ�䵽�ĸ���Raid������
		"""
		INFO_MSG( "Matched raid is finished." )
		self.updateMatchedCopyInfo( "", 0, {} )

	def gainRightToResumeHaltedRaid( self ) :
		"""
		<Define method>NEW
		������ű��жϵĸ���Raid���ʸ�
		"""
		pass