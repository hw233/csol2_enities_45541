# -*- coding: gb18030 -*-


import BigWorld
from bwdebug import *
import csdefine
import cschannel_msgs
import Love3
import time
import csstatus
import random
from CrondDatas import CrondDatas
import cPickle
import items
g_items = items.instance()
from MsgLogger import g_logger


g_CrondDatas = CrondDatas.instance()
COMPETITION_MAX_ENTER_PLAYER = 50				# ������������������
COMPETITION_MAX_TONG_ENTER_PLAYER = 1			# ÿ�������������������
SIGNUP_TIME = 55*60		# 55���ӵı���ʱ��
ENTER_TIME = 5*60       # 5���ӵ��볡׼��ʱ��

TONGCOMPETITION_SIGNUP    = 0    # ��Ὰ����ʼ����ʱ��
TONGCOMPETITION_ENTER     = 1    # ��Ὰ����ʼ�볡ʱ��
TONGCOMPETITION_START     = 2    # ��Ὰ��������ʼʱ��

class TongCompetitionMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# ���Լ�ע��ΪglobalDataȫ��ʵ��

		self._signUpTime = SIGNUP_TIME  # �ӿ�ʼ��������ʼ�볡��55����
		self._enterTime = ENTER_TIME    # �ӿ�ʼ�볡��������ʽ��ʼ��5����

		self.registerGlobally( "TongCompetitionMgr", self._onRegisterManager )
		self.entersSpaceTongMember = {}
		self.tempMemberTongInfo = {}
		self.competitionDBIDList = []   # �����μӰ�Ὰ���ĳ�Ա�б�
		self.TongList = []				# ������뾺�����İ���б�
		self.tongEnterMember = {}		# ����һ��ԭʼ���뾺����������б�
		self.leavePlayerName = []		# �����������뿪�������������

	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register TongCompetitionMgr Fail!" )
			# again
			self.registerGlobally( "TongCompetitionMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["TongCompetitionMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("TongCompetitionMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
						"familyCompetition_start_notice" : "onStartNotice",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )

	def onStartNotice( self ):
		"""
		define method.
		���ʼǰ55���ӿ�ʼ��ʾ����
		"""
		self.competitionDBIDList = []
		self.tongEnterMember = {}
		self._signUpTime = SIGNUP_TIME
		self._enterTime  = ENTER_TIME
		self.onTimer( 0, TONGCOMPETITION_SIGNUP )
		INFO_MSG( "TongCompetitionMgr", "notice", "" )

	def onTimer( self, timerID, userArg ):
		"""
		"""
		if userArg == TONGCOMPETITION_SIGNUP:		# 55�����ڱ���

			leftSignUpTime = int( int( self._signUpTime ) / 60 )

			if self._signUpTime > 0 and leftSignUpTime in [ 55, 40, 25, 10, 5 ]:
				# 55(40/25/10/5)���ӷֱ��й�����ʾ
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TONGCOMPETITION_BEGIN_NOTIFY_0 % leftSignUpTime, [] )
			BigWorld.globalData[ "AS_TongCompetition_SignUp" ] = True

			if self._signUpTime == 0:
				self.initTongCompetition( self.competitionDBIDList )		# �жϳ����������İ�����
				if not self.TongList:
					return
				tong = BigWorld.globalData["TongManager"]
				b = BigWorld.entities.get( tong.id )
				for dbid in self.TongList:
					tongEntity = b.findTong( dbid )
					tongEntity.tongCompetitionGather( 1 )
				self.addTimer( 0, 0, TONGCOMPETITION_ENTER )
				if BigWorld.globalData.has_key( "AS_TongCompetition_SignUp" ):
					del BigWorld.globalData[ "AS_TongCompetition_SignUp" ]		# ��Ὰ����������
			else:
				self.addTimer( 60, 0, TONGCOMPETITION_SIGNUP )

			self._signUpTime -= 60

		elif userArg == TONGCOMPETITION_ENTER:		# 5�������볡��ʼ

			leftEnterTime = int( int( self._enterTime ) / 60 )
			
			if self._enterTime > 0 and leftEnterTime in [ 5, 4, 3, 2, 1 ]:
				# 5(4/3/2/1)���ӷֱ��й�����ʾ
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TONGCOMPETITION_BEGIN_NOTIFY_1 % leftEnterTime, [] )

			if self._enterTime <= 0:
				if BigWorld.globalData.has_key( "AS_TongCompetition" ):
					del BigWorld.globalData[ "AS_TongCompetition" ]		# ��Ὰ����������
				self.onStart( )
			else:
				self.addTimer( 60, 0, TONGCOMPETITION_ENTER )

			self._enterTime -= 60

	def onStart( self ):
		"""
		define method.
		5���ӵ��볡ʱ�������,������ʽ��ʼ��
		"""
		if not self.TongList:
			return
		tong = BigWorld.globalData["TongManager"]
		b = BigWorld.entities.get( tong.id )
		for dbid in self.TongList:
			tongEntity = b.findTong( dbid )
			tongEntity.tongCompetitionCloseGather()
		if  BigWorld.globalData.has_key( "AS_TongCompetition" ):
			curTime = time.localtime()
			ERROR_MSG( "tongCompetition is running��%i:%i try open��"%(curTime[3],curTime[4] ) )
			return
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TONGCOMPETITION_BEGIN_NOTIFY, [] )
		INFO_MSG( "TongCompetitionMgr", "start", "" )

	def onEnd( self ):
		"""
		define method.
		��Ὰ�������
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TONGCOMPETITION_END_NOTIFY, [] )
		self.sendAwardToEmail()		# ��������Ͳ��뽱
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TONGCOMPETITION_MAIL_REWARD_NOTICE, [] )
		if BigWorld.globalData.has_key( "AS_TongCompetition" ):
			del BigWorld.globalData[ "AS_TongCompetition" ]
		self.competitionDBIDList = []   # �����μӰ�Ὰ���ĳ�Ա�б����
		self.TongList = []				# ������뾺�����İ���б����
		self.tongEnterMember = {}		# ���Ͳ��뽱�ĳ�Ա�ֵ����
		self.leavePlayerName = []		# �����������뿪����������б����
		INFO_MSG( "TongCompetitionMgr", "end", "" )

	def onEnterSpace(self, spaceMailBox, playerMailBox, TongDBID):
		"""
		define method.
		"""
		if not BigWorld.globalData.has_key( "AS_TongCompetition" ):
			return

		if not self.isTongJoin( TongDBID ):			# �Ƿ�����ʸ�����Ὰ����
			return

		if playerMailBox.id not in self.tempMemberTongInfo:
			ERROR_MSG("can't find player:%d tongID "%playerMailBox.id)
			return

		tong_dbID = self.tempMemberTongInfo[playerMailBox.id]		# ������ڰ���mailbox

		if spaceMailBox.id not in self.entersSpaceTongMember:		# ��������һ���ֵ�
			self.entersSpaceTongMember[spaceMailBox.id] = {}

		if tong_dbID not in self.entersSpaceTongMember[spaceMailBox.id]:		# ��������һ���б�
			self.entersSpaceTongMember[spaceMailBox.id][tong_dbID] = []

		self.entersSpaceTongMember[spaceMailBox.id][tong_dbID].append(playerMailBox)		# ��¼���븱���İ���Ա
		self.tempMemberTongInfo.pop(playerMailBox.id)		# ɾ���Ѿ����븱�������id

	def onLevelSpace(self, spaceMailBox, playerMailBox):
		"""
		define method.
		"""
		try:
			currentSpaceEnterMember = self.entersSpaceTongMember[spaceMailBox.id]
		except KeyError:
			ERROR_MSG("currentTongEnterMember is key error spaceID:%d"%(spaceMailBox.id))
			return

		for tid, playerList in currentSpaceEnterMember.iteritems():
			for index, pm in enumerate(playerList):
				if pm.id == playerMailBox.id:
					self.entersSpaceTongMember[spaceMailBox.id][tid].pop(index)
					if len( currentSpaceEnterMember[tid] ) == 0:
						self.entersSpaceTongMember[spaceMailBox.id].pop(tid)		# ����ð���ڸ���������Ϊ0�������˰��ID
					return

	def teleportEntity( self, domainSpaceMailBox, spaceMailBox, position, direction, playerMailBox, params ):
		"""
		define method.
		"""
		if not BigWorld.globalData.has_key( "AS_TongCompetition" ):
			return
		tong_dbID = params.get("tongDBID", 0)
		if tong_dbID not in self.TongList:
			return
		self.tempMemberTongInfo[ playerMailBox.id ] = tong_dbID
		if spaceMailBox == None:
			domainSpaceMailBox.onSpaceItemEnter( position, direction, playerMailBox, params )
			return

		result = self.checkISCanTeleport(spaceMailBox, playerMailBox, tong_dbID)
		if result != 0:
			playerMailBox.client.onStatusMessage( result, "" )
			return

		self.tempMemberTongInfo[ playerMailBox.id ] = tong_dbID
		domainSpaceMailBox.onSpaceItemEnter( position, direction, playerMailBox, params )

	def checkISCanTeleport( self, spaceMailBox, playerMailBox, tong_dbID ):
		result = 0
		while( True ):
			if tong_dbID == 0 or tong_dbID == None:
				result = csstatus.TONG_COMPETITION_FORBID_MEMBER
				break

			if tong_dbID not in self.TongList:		# ��������������İ���б��ڽ����ܽ��븱��
				result = csstatus.TONG_COMPETETION_NOTICE_10
				break

			if spaceMailBox.id not in self.entersSpaceTongMember:
				break

			if tong_dbID not in self.entersSpaceTongMember[spaceMailBox.id]:
				break

			if len( self.entersSpaceTongMember[spaceMailBox.id][tong_dbID] ) >= COMPETITION_MAX_TONG_ENTER_PLAYER:		# ÿ�����ɽ��������������ܳ���10
				result = csstatus.TONG_COMPETITION_TONG_MEMBER_FULL
				break

			break

		return result

	def countSpaceMember(self, spaceID):
		count = 0
		if spaceID in self.entersSpaceTongMember:
			for pList in self.entersSpaceTongMember[spaceID].values():
				count += len(pList)

		return count

	def onRequestCompetition( self, playerBaseMailbox, tongDBID ):
		"""
		Define method.
		�����μӰ�Ὰ��

		@param playerBaseMailbox : �������߸�������base mailbox
		@type playerBaseMailbox : MAILBOX
		@param tongDBID : �����Ὰ����dbid
		@type tongDBID : DATABASE_ID
		"""
		allowSignUp = BigWorld.globalData.has_key( "AS_TongCompetition_SignUp" )
		if not allowSignUp:
			self.abaStatusMessage( playerBaseMailbox, csstatus.TONG_COMPETETION_NOTICE_1 )
			return
		if tongDBID in self.competitionDBIDList:
			self.abaStatusMessage( playerBaseMailbox, csstatus.TONG_COMPETETION_NOTICE_8 )
			return

		self.competitionDBIDList.append( tongDBID )
		self.onAbaMessage( tongDBID, csstatus.TONG_COMPETETION_NOTICE_5 )
		
		try:
			g_logger.actJoinLog( csdefine.ACTIVITY_BANG_HUI_JING_JI, csdefine.ACTIVITY_JOIN_TONG, tongDBID, self.getTongNameByDBID( tongDBID ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def onAbaMessage( self, tongDBID, statusID, *args ):
		"""
		��Ὰ�����ͳһϵͳͨ�� ��ָ�����ͨ��
		"""
		if args == ():
			tempArgs = ""
		else:
			tempArgs = str( args )

		tong = BigWorld.globalData["TongManager"]
		b = BigWorld.entities.get( tong.id )
		tongEntity = b.findTong( tongDBID )
		if tongEntity:
			tongEntity.onStatusMessage( statusID, tempArgs )

	def abaStatusMessage( self, playerBase, statusID, *args ):
		"""
		��Ὰ��״̬��Ϣ���ͺ���
		"""
		if args == ():
			tempArgs = ""
		else:
			tempArgs = str( args )
		playerBase.client.onStatusMessage( statusID, tempArgs )


	def initTongCompetition( self, competitionDBIDList ):
		"""
		��ʼ����Ὰ�����ݣ���������ʸ�İ�����
		"""
		self.TongList = self.randomGetList( competitionDBIDList )
		if not self.TongList:
			return
		for TongDBID in self.TongList:
			BigWorld.globalData[ "AS_TongCompetition" ] = True

	def randomGetList( self, competitionDBIDList ):
		"""
		���������󣬻�ȡ�����ʸ�İ���б�
		"""
		if 1 <= len( self.competitionDBIDList ) <= 5:		# 5����5�����ڵİ�ᶼ���ʸ�
			for tongDBID in competitionDBIDList:
				self.onAbaMessage( tongDBID, csstatus.TONG_COMPETETION_NOTICE_9 )
			return competitionDBIDList

		if len( self.competitionDBIDList ) > 5:				# �����ȡ5�����
			TongIDList = random.sample( self.competitionDBIDList, 5 )
			for tongDBID in TongIDList:
				self.onAbaMessage( tongDBID, csstatus.TONG_COMPETETION_NOTICE_9 )		# ֪ͨ���鵽�İ��
				for tongDBID in competitionDBIDList:
					if tongDBID not in TongIDList:
						self.onAbaMessage( tongDBID, csstatus.TONG_COMPETETION_NOTICE_10 )		# ֪ͨû���鵽�İ��

			return TongIDList

		else:
			return

	def isTongJoin( self, TongDBID ):
		"""
		TongDBID����Ƿ�����ʸ���뾺����
		"""
		return TongDBID in self.TongList

	def sendAwardToEmail( self ):
		"""
		�����������ͳһ���ͽ������������
		"""
		for e in self.tongEnterMember:
			itemDatas = []
			item = g_items.createDynamicItem( 60101250, 1 )
			if item:
				tempDict = item.addToDict()
				del tempDict["tmpExtra"]	# ȥ����Ʒ�����̵�����
				itemData = cPickle.dumps( tempDict, 2 )
				itemDatas.append( itemData )
				BigWorld.globalData["MailMgr"].send( None, e, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC,"", cschannel_msgs.TONGCOMPETITION_MAIL_REWARD_TITLE, "", 0, itemDatas )

	def setSignUpTime( self, value ):
		"""
		define method.
		���ð�Ὰ��ʣ�౨��ʱ�䣬����GMָ��
		"""
		tong = BigWorld.globalData["TongCompetitionMgr"]
		b = BigWorld.entities.get( tong.id )
		b._signUpTime = value

	def saveTongMemberInfo( self, playerName, playerMailbox, tongDBID ):
		"""
		defined method.

		@param playerName			: �������
		@type playerName			: STRING
		@param playerMailbox			: ���mailbox
		@type playerMailbox			: MAILBOX
		@param tongDBID			: ��ҵİ��ID
		@type tongDBID			: DATABASE_ID

		���������ҵ���Ϣ
		"""
		if playerName not in self.tongEnterMember:
			self.tongEnterMember[ playerName ] = [ playerMailbox, tongDBID ]

	def saveLeaveTongMember( self, playerName ):
		"""
		defined method.

		��¼�������뿪����ҵ�����
		"""
		self.leavePlayerName.append( playerName )

	def sendChampionBox( self, tongDBID ):
		"""
		define method.

		����ǰ�뿪��������ҷ��Źھ�����
		"""
		itemDatas = []
		item = g_items.createDynamicItem( 60101243, 1 )
		if item:
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]	# ȥ����Ʒ�����̵�����
			itemData = cPickle.dumps( tempDict, 2 )
			itemDatas.append( itemData )

		for e in self.leavePlayerName:
			if e in self.tongEnterMember and self.tongEnterMember[e][1] == tongDBID:
				BigWorld.globalData["MailMgr"].send( None, e, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, cschannel_msgs.TONGCOMPETITION_MAIL_WINNER_TITLE, "", "", 0, itemDatas )
		self.leavePlayerName = []