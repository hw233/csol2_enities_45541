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

PUNISHED_SKILL_ID = 323249001											# �������ܳͷ�buff�ļ���
PUNISHED_BUFF_ID = 106001												# ���ܳͷ�buff��ID

class CopyMatcherInterface :

	def __init__( self ) :
		self._expectGuider = False										# ����Ƿ�Ը�ⵣ�ζ����� CELL_PRIVATE
		self._expectedDuties = ()										# �������ѡ���ְ�𣬲���������ܵ�����Щְ�� CELL_PRIVATE
		self._expectedCopies = ()										# �������ѡ��ĸ����������������ǰ����Щ���� CELL_PRIVATE
		self._haltedRaidResumed = False									# ���Ű�·���� CELL_PRIVATE
		self.labelOfMatchedCopy = ""									# ƥ�䵽�ĸ��� CELL_PUBLIC
		self.insideMatchedCopy = False									# �Ƿ���ƥ�䵽�ĸ����� OWN_CLIENT
		if not hasattr( self, "latestMatchedTime" ) :					# Ϊ����Ӧ���Դ��룬ͬʱ��ֹ��������ĳ�ʼ��
			self.latestMatchedTime = 0.0								# ���һ�γɹ�ƥ���ʱ�䣨persistent property��OWN_CLIENT
		self._tid_resumeHaltedRaid = 0									# ȷ�ϼ����·���������timerID
		self._camp = 0

	# ----------------------------------------------------------------
	# functions in common
	# ----------------------------------------------------------------
	def isPunishedForEscape( self ) :
		"""
		�Ƿ������������ܳͷ�
		test:1015
		release:106001
		"""
		#return self.findBuffByBuffID( 1015 ) is not None
		return self.findBuffByBuffID( PUNISHED_BUFF_ID ) is not None

	def punishedForEscape( self ) :
		"""
		��Ϊ����ƥ�丱�������ܳͷ�
		test skill id: 322208001
		release skill id: 323249001
		"""
		INFO_MSG( "[%s(id:%i)]: I am punished for escaping from matched team." % ( self.getName(), self.id, ) )
		#self.spellTarget( 322208001, self.id )
		self.spellTarget( PUNISHED_SKILL_ID, self.id )

	def isForbiddenToMatchNewTeam( self ) :
		"""
		�Ƿ�ǰ����ֹȥƥ���µĸ������飬���磺
		1����ǰ���������ܳͷ���
		2����ǰ�����ǰ�;�жϵĸ�������
		"""
		return self.isPunishedForEscape() or self._haltedRaidResumed

	def matchIsCooling( self ) :
		"""
		������ȴ��
		"""
		return self.timeTillLastMatched() < csdefine.TIME_LIMIT_OF_MATCHED_INTERVAL

	def timeTillLastMatched( self ) :
		"""
		time till last matched.
		"""
		return time.time() - self.latestMatchedTime

	def recordMatchedTime( self, matchedTime ) :
		"""
		��¼���ƥ��ʱ��
		"""
		self.latestMatchedTime = matchedTime							# ��¼�����һ��ƥ���ʱ��
		self.broadcastMatchedTimeToTeammates()

	def broadcastMatchedTimeToTeammates( self ) :
		"""
		�����ƥ��ʱ�䷢�͸�����
		"""
		for teammate in self.getTeamMemberMailboxs() :
			if teammate and teammate.id != self.id :
				teammate.client.updateTeammateMatchedTime( self.id, self.latestMatchedTime )

	def broadcastActFlagsToTeammates( self, modifiedFlag ) :
		"""
		���������Ƿ��͸�����
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
		@param		copies : ѡ���ְ��
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
		@param		resumed : �Ƿ����������жϵĸ���
		"""
		self._haltedRaidResumed = resumed

	def onMatchedCopyTeam( self, copyLevel, copyLabel ) :
		"""
		<Define method>
		@type		copyLevel : UINT8
		@param		copyLevel : ƥ�䵽�ĸ���
		@type		copyLabel : STRING
		@param		copyLabel : ƥ�䵽�ĸ���
		"""
		self.labelOfMatchedCopy = copyLabel
		self.recordMatchedTime( time.time() )
		inside = self.labelOfMatchedCopy and self.spaceType == self.labelOfMatchedCopy
		self.setInsideMatchedCopy( inside )

	def setInsideMatchedCopy( self, inside ) :
		"""
		<???Define method>NEW
		��ʱ��onEnterSpace_�ӿ��е���cmi_onEnterSpace��
		��onLeaveSpace_�ӿ��е���cmi_onLeaveSpace��ʵ��
		������뿪ƥ�丱�����жϺ����ã���������ӿ���ʱ
		���ŵ�def�ļ��ж��塣
		@type		inside : BOOL
		@param		inside : �����Ƿ���ƥ�丱����
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
		@param		srcEntityID : ��ҵ�ID���������Զ����룬����def�ж���
		@type		duties : UINT8_TUPLE(python tuple)
		@param		duties : ѡ���ְ��
		@type		copies : STRING_TUPLE(python tuple)
		@param		copies : ѡ���ְ��
		@type		expectGuider : BOOL
		@param		expectGuider : �Ƿ�Ը�ⵣ�ζ�����
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
		@param		srcEntityID : ��ҵ�ID���������Զ����룬����def�ж���
		@type		duties : UINT8_TUPLE(python tuple)
		@param		duties : ѡ���ְ��
		@type		expectGuider : BOOL 
		@param		expectGuider : �Ƿ�Ը�ⵣ�ζ�����
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
		������;�ж�Ա�뿪�󣬿��ɶӳ��ٴη���ƥ�����룬��������
		��Ա����ѡ��ְ��Ŀ��ǡ�
		Ŀǰ������Ҫ���Ϊ���巽������ʱ���ӵ�def�ļ��� 2012-07-01
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
		�ŶӼ������жϵĸ���������Ҫ�жϸ�����¼�Ƿ�������
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
		���Ѽ������
		"""
		if teammateBase.id != self.id :
			teammateBase.client.receiveTeammateMatchInfo( self.id, self.latestMatchedTime, self.activityFlags )


#	# ----------------------------------------------------------------
	# about leave team
	# ----------------------------------------------------------------
	def cmi_onLeaveTeam( self ) :
		"""
		�˳��˶���
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
		������·��������ӵĴ���
		"""
		if self.matchIsCooling() :
			self.recordMatchedTime( 0.0 )						# ����¼��ε�ƥ��ʱ��

	def handleLeaveTeamActive( self ) :
		"""
		�����뿪����Ĵ���
		"""
		if self.labelOfMatchedCopy and self.matchIsCooling() :
			self.punishedForEscape()						# ��û��ȴ���˶ӣ��������ܳͷ�

	def handleLeaveTeamOnVoteKicked( self ) :
		"""
		��ͶƱ�߳�����
		"""
		pass

	def handleAfterLeaveTeam( self ) :
		"""
		��Ӵ���
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
		������ߴ���ƥ�丱��
		@type	enter : BOOL
		@param	enter : ���뻹���뿪ƥ�丱��
		"""
		if self.id != srcEntityID :
			return
		if enter :
			self.enterMatchedCopy()
		else :
			self.leaveMatchedCopy()

	def enterMatchedCopy( self ) :
		"""
		�������ƥ�丱��
		"""
		if self.insideMatchedCopy :
			ERROR_MSG( "[%s(id:%i)]: I am already in matched copy." % ( self.getName(), self.id ) )
		elif self.labelOfMatchedCopy :
			self.gotoSpace( self.labelOfMatchedCopy, *g_spaceCopyData.birthDataOfCopy(self.labelOfMatchedCopy) )

	def leaveMatchedCopy( self ) :
		"""
		�����뿪ƥ�丱��
		"""
		if self.insideMatchedCopy :
			self.gotoForetime()
		else :
			ERROR_MSG( "[%s(id:%i)]: I am not in matched copy currently." % ( self.getName(), self.id ) )

	def teleportCopyOnMatched( self, copyLabel ) :
		"""
		<Define method>???
		���͵�ƥ��ĸ���
		@type	copyLabel : STRING
		@param	copyLabel : ƥ�丱���ı�ǩ
		"""
		self.setTemp( "CMI_Teleport_On_Match", 1 )								# ����ƥ����Զ����͸������
		if copyLabel in COPIES_DIFFICUTY :
			self.setTemp( *COPIES_DIFFICUTY[copyLabel] )
		self.gotoSpace( copyLabel, *g_spaceCopyData.birthDataOfCopy(copyLabel) )

	def onEnterMatchedCopy( self, copyLabel, bossesKilled ) :
		"""
		<Define method>
		���͵�ƥ��ĸ�����ص�
		@type	copyLabel : STRING
		@param	copyLabel : ƥ�丱���ı�ǩ
		@type	bossesKilled : UINT8
		@param	bossesKilled : boss��ɱ����
		"""
		if self.popTemp("CMI_Teleport_On_Match") :
		#	if self.isCaptain(): #���ζӳ���ɢ�����Ȩ��
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
			#self.client.cancelShieldTeamDisbanded() #ȡ�����ζӳ���ɢ�����Ȩ��
		pass

	def onTimer_joinHaltedRaid( self, timerID, cbid ) :
		"""
		ȷ�ϼ����·������ƥ�����ʱ�䵽
		"""
		assert( self._tid_resumeHaltedRaid == timerID )
		assert( ECBExtend.CTM_CONFIRM_RESUMING_HALTED_RAID == cbid )
		self.partakeInHaltedRaid()
		self._tid_resumeHaltedRaid = 0

	def confirmJoiningHaltedRaid( self, srcEntityID, agree ) :
		"""
		<Exposed method>???
		������ߴ���ƥ�丱��
		@type	agree : BOOL
		@param	agree : ȷ���Ƿ�����·������������Ҵ���ƥ��İ�·
						����ʱ����������ٴ�ƥ��ȷ�Ͽ�
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
		ͬ�����ƥ�䵽�ĸ���
		"""
		if self.labelOfMatchedCopy :
			self.addActivityCount( COPIES_ACT_FLAG[self.labelOfMatchedCopy] )

	def giveUpHaltedRaid( self ) :
		"""
		��������ƥ�䵽�İ�·����
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
		��ͶƱ�߳�����
		"""
		if self.isInTeam() :
			self.setTemp( "CMI_Leave_Team_Reason", csdefine.LEAVE_TEAM_VOTE_KICKED )
			self.teamMailbox.leave( self.id, self.id )

	def onMatchedRaidFinished( self ) :
		"""
		<Define method>
		����raid����ʱ����
		"""
		self.labelOfMatchedCopy = ""
		if self.isCaptain():
			self.client.cancelShieldTeamDisbanded()
		self.client.onMatchedRaidFinished()
		
