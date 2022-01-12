# -*- coding: gb18030 -*-
#

# $Id:  Exp $

from bwdebug import *
import cschannel_msgs
import ShareTexts as ST
from CrondDatas import CrondDatas
import csstatus
import time
import BigWorld
import random
import Love3
import items
import csdefine
import csconst
import ItemTypeEnum
import ShareTexts
import ChatObjParser


g_items = items.instance()
g_CrondDatas = CrondDatas.instance()


MAX_EXAMINATION_TIME  = 1800   											# ����ʱ������(�룩

XIANGSHI_EXAMINATION_TIME  = 3600*9   									# ����ʱ��(�룩��9��Сʱ��
HUISHI_EXAMINATION_TIME  = 3600*4   									# ����ʱ��(�룩��4��Сʱ��
DIANSHI_EXAMINATION_TIME  = 3600*2   									# ����ʱ��(�룩��2��Сʱ��

NO_EXAMINATION = 0														# û�п���
XIANGSHI 	= 3															# ����
HUISHI 		= 4															# ����
DIANSHI 	= 5															# ����

XIANGSHI_SIGN_UP	= 0													# ���Ա���
XIANGSHI_NOTICE		= 1													# �������ڽ���
HUISHI_SIGN_UP		= 2													# ���Ա���
HUISHI_NOTICE		= 3													# �������ڽ���
DIANSHI_SIGN_UP		= 4													# ���Ա���
XIANGSHI_END		= 5													# ���Խ���
HUISHI_END			= 6													# ���Խ���
DIANSHI_END			= 7													# ���Խ���
EXAMINATION_RELOAD 	= 8													# ������������

JU_REN_COUNT		= 20												# �ܲ���20������
JIN_SHI_COUNT		= 10												# �ܲ���10����ʿ���ϵģ�����״Ԫ����̽����


T_ZHUANGYUAN		= 35												# ״Ԫ�ƺŵ�ID
T_BANGYAN			= 34												# ���۳ƺŵ�ID
T_TANHUA			= 33												# ̽���ƺŵ�ID
T_JINSHI			= 32												# ��ʿ�ƺŵ�ID
T_JUREN				= 31												# ���˳ƺŵ�ID

ONE_MINUTE			= 60												# һ����ʱ��

SUNDAY				= 6

RELOAD_CLOCK		= 23

# ����������ʯ��ID
CHU_JI_XINGYUNSHI = 80101033
GAO_JI_XINGYUNSHI = 80101043

class ImperialExaminationsMgr( BigWorld.Base ):
	"""
	"""
	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )

		self.playersQuestionDict = {}										# such as { "playerName": ( questionID, startTime ), ...}

		self.jurenDict 		= {}											# �����б� such as { rightRate: dbid, ...}
		self.jinshiDict 	= {}											# ��ʿ�б� such as { rightRate: dbid, ...}
		self._zhuangyuan 	= ""											# ״Ԫ
		self._bangyan 		= ""											# ����
		self._tanhua 		= ""											# ̽��

		self._examinationType = NO_EXAMINATION								# ��ǰ���ڽ��еĿ������ͣ�3�����ԣ�4�����ԣ�5�����ԣ�
		self._todayExamType = NO_EXAMINATION								# ����Ŀ������ͣ�3�����ԣ�4�����ԣ�5�����ԣ�
		self._examLostTime	= 0												# �����ѹ���ʱ��
		# ���Լ�ע��ΪglobalDataȫ��ʵ��
		self.registerGlobally( "ImperialExaminationsMgr", self._onRegisterManager )

	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register ImperialExaminationsMgr Fail!" )
			# again
			self.registerGlobally( "ImperialExaminationsMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["ImperialExaminationsMgr"] = self			# ע�ᵽ���еķ�������
			INFO_MSG("ImperialExaminationsMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
						"ImperialExaminationsMgr_reset" : "onReset",
						"ImperialExaminationsMgr_xiangshi_start" : "onXiangshiStart",
						"ImperialExaminationsMgr_xiangshi_end" : "onXiangshiEnd",
						"ImperialExaminationsMgr_huishi_start" : "onHuishiStart",
						"ImperialExaminationsMgr_huishi_end" : "onHuishiEnd",
						"ImperialExaminationsMgr_dianshi_start" : "onDianshiStart",
						"ImperialExaminationsMgr_dianshi_end" : "onDianshiEnd",
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )


		BigWorld.globalData["Crond"].addAutoStartScheme( "ImperialExaminationsMgr_xiangshi_start", self, "onXiangshiStart" )
		BigWorld.globalData["Crond"].addAutoStartScheme( "ImperialExaminationsMgr_huishi_start", self, "onHuishiStart" )
		BigWorld.globalData["Crond"].addAutoStartScheme( "ImperialExaminationsMgr_dianshi_start", self, "onDianshiStart" )


	def onReset( self ):
		"""
		define method.
		ȫ�������
		"""
		self.jurenDict = {}
		self.jinshiDict = {}
		self._examinationType = NO_EXAMINATION
		self._zhuangyuan = ""
		self._bangyan = ""
		self._tanhua = ""
		INFO_MSG( "ImperialExaminationsMgr", "reset", "" )

	def huiShiReset( self ):
		"""
		���Ի����
		"""
		self.jurenDict = {}

	def dianShiReset( self ):
		"""
		���Ի����
		"""
		self.jinshiDict = {}
		self._zhuangyuan = ""
		self._bangyan = ""
		self._tanhua = ""

	def queryKejuState( self ):
		"""
		"""
		xiangshi = BigWorld.globalData.has_key( "AS_XiangshiActivityStart" )
		huishi = BigWorld.globalData.has_key( "AS_HuishiActivityStart" )
		dianshi = BigWorld.globalData.has_key( "AS_DianshiActivityStart" )

		return xiangshi or huishi or dianshi

	def onXiangshiStart( self ):
		"""
		define method.
		���Կ�ʼ
		"""
		if self.queryKejuState():
			curTime = time.localtime()
			ERROR_MSG( "Examination is in process��%i :%i try to turn on again"%(curTime[3],curTime[4] ) )
			return
		self.onTimer( 0, XIANGSHI_SIGN_UP )
		INFO_MSG( "ImperialExaminationsMgr", "start", "xiang shi" )

	def onXiangshiEnd( self ):
		"""
		define method.
		���Խ���
		"""
		if not BigWorld.globalData.has_key( "AS_XiangshiActivityStart" ):
			curTime = time.localtime()
			ERROR_MSG( "country examination was over, %i:%i try to turn on again"%(curTime[3],curTime[4] ) )
			return
		self.onTimer( 0, XIANGSHI_END )
		INFO_MSG( "ImperialExaminationsMgr", "end", "xiang shi" )

	def onHuishiStart( self ):
		"""
		define method.
		���Կ�ʼ
		"""
		if self.queryKejuState():
			curTime = time.localtime()
			ERROR_MSG( "Examination Activity is in process��%i:%i try to turn on again"%(curTime[3],curTime[4] ) )
			return
		BigWorld.globalData[ "IE_HuiShi_Reward_DBID_List" ] = []	# ��ջ��Խ��������б�
		self.onTimer( 0, HUISHI_SIGN_UP )
		INFO_MSG( "ImperialExaminationsMgr", "start", "hui shi" )

	def onHuishiEnd( self ):
		"""
		define method.
		���Խ���
		"""
		if not BigWorld.globalData.has_key( "AS_HuishiActivityStart" ):
			curTime = time.localtime()
			ERROR_MSG( "sum examination was over��%i:%i try to turn on again"%(curTime[3],curTime[4] ) )
			return

		self.onTimer( 0, HUISHI_END )
		INFO_MSG( "ImperialExaminationsMgr", "end", "hui shi" )

	def onDianshiStart( self ):
		"""
		define method.
		���Կ�ʼ
		"""
		if self.queryKejuState():
			curTime = time.localtime()
			ERROR_MSG( "palarm examination is in process��%i:%i try to turn on again"%(curTime[3],curTime[4] ) )
			return
			BigWorld.globalData[ "IE_DianShi_Reward_DBID_List" ] = []	# ��յ��Խ��������б�
		self.onTimer( 0, DIANSHI_SIGN_UP )
		INFO_MSG( "ImperialExaminationsMgr", "start", "dian shi" )

	def onDianshiEnd( self ):
		"""
		define method.
		���Խ���
		"""
		if not BigWorld.globalData.has_key( "AS_DianshiActivityStart" ):
			curTime = time.localtime()
			ERROR_MSG( "palarm examination was over��%i:%i try to turn on again"%(curTime[3],curTime[4] ) )
			return
		self.onTimer( 0, DIANSHI_END )
		INFO_MSG( "ImperialExaminationsMgr", "end", "dian shi" )

	def addPlayerQuestion( self, playerName, questionID ):
		"""
		define method
		"""
		self.playersQuestionDict[playerName] = ( questionID, time.time() )

	def requestPlayerQuestion( self, NPCCellMailBox, playerBaseMailbox, playerName, answerID  ):
		"""
		define method
		ѯ�ʵ�ǰ��һش�����ĸ���Ŀ��ͬʱ������Ŀ��NPCһ����Ӧ��
		"""
		if self.playersQuestionDict.has_key( playerName ):
			questionID, startTime = self.playersQuestionDict[playerName]
			if startTime - time.time() <= MAX_EXAMINATION_TIME:				#�ش�����δ��ʱ
				NPCCellMailBox.remoteScriptCall( "receivePlayerQuestionInfo", ( playerBaseMailbox, questionID, answerID ) )
				del self.playersQuestionDict[playerName]

	def onTimer( self, id, userArg ):
		"""
		"""
		if userArg == XIANGSHI_SIGN_UP:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_KJKS_BEGIN_FOR_UP_LEVEL, [] )
			self._examinationType = XIANGSHI
			self._todayExamType = XIANGSHI
			BigWorld.globalData[ "AS_XiangshiActivityStart" ] = True
			self._examLostTime += 3600
			self.addTimer( 3600, 0, XIANGSHI_NOTICE )
		elif userArg == XIANGSHI_NOTICE:
			if self._examLostTime < XIANGSHI_EXAMINATION_TIME and BigWorld.globalData.has_key("AS_XiangshiActivityStart" ) and BigWorld.globalData["AS_XiangshiActivityStart" ] == True:
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_KJKS_DOING_FOR_UP_LEVEL, [] )
				self.addTimer( 3600, 0, XIANGSHI_NOTICE )
			self._examLostTime += 3600
		elif userArg == HUISHI_SIGN_UP:
			self.huiShiReset()
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_KJKS_BEGIN_FOR_XIUCAI, [] )
			self._examinationType = HUISHI
			self._todayExamType = HUISHI
			BigWorld.globalData[ "AS_HuishiActivityStart" ] = True
			self._examLostTime += 3600
			self.addTimer( 3600, 0, HUISHI_NOTICE )
		elif userArg == HUISHI_NOTICE:
			if self._examLostTime < HUISHI_EXAMINATION_TIME and BigWorld.globalData.has_key("AS_HuishiActivityStart" ) and BigWorld.globalData["AS_HuishiActivityStart"] == True:
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_KJKS_DOING_FOR_XIUCAI, [] )
				self.addTimer( 3600, 0, HUISHI_NOTICE )
			self._examLostTime += 3600
		elif userArg == DIANSHI_SIGN_UP:
			self.dianShiReset()
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_KJKS_DOING_FOR_DIANSHI, [] )
			self._examinationType = DIANSHI
			self._todayExamType = DIANSHI
			BigWorld.globalData[ "AS_DianshiActivityStart" ] = True
		elif userArg == XIANGSHI_END:
			self._examinationType = NO_EXAMINATION
			self._examLostTime = 0
			del BigWorld.globalData[ "AS_XiangshiActivityStart" ]
		elif userArg == HUISHI_END:
			del BigWorld.globalData[ "AS_HuishiActivityStart" ]
			jurenDBIDList = self.calcExamResults()
			BigWorld.globalData[ "IE_HuiShi_Reward_DBID_List" ] = jurenDBIDList
			jurenNameListStr = ""
			for dbID in jurenDBIDList:
				content = cschannel_msgs.KE_JU_VOICE_19
				try:
					playerName = self.jurenDict[dbID][2]
				except KeyError:
					ERROR_MSG( "ju ren dict jurenDict databaseID %s is a None player" % dbID )
					return
				BigWorld.globalData['MailMgr'].send( None, playerName, 1, 2, cschannel_msgs.KE_JU_VOICE_22, cschannel_msgs.KE_JU_VOICE_23, content, 0, "" )
				jurenNameListStr += ( playerName + "," )
			self._examinationType = NO_EXAMINATION
			self._examLostTime = 0
			huishiOverMsg = cschannel_msgs.BCT_KJKS_NO_JUREN
			if jurenNameListStr != "":
				huishiOverMsg = cschannel_msgs.BCT_KJKS_CELEBRATE_FOR_JUREN % jurenNameListStr
			Love3.g_baseApp.anonymityBroadcast( huishiOverMsg, [] )
		elif userArg == DIANSHI_END:
			del BigWorld.globalData[ "AS_DianshiActivityStart" ]
			leadMembers = self.calcExamResults()
			jinShiDBIDList = leadMembers.copy().keys()	# �����jinShiDBIDList���������˽�ʿ��������״Ԫ�����ۡ�̽��������Ĵ��뽫����������޳�
			BigWorld.globalData[ "IE_DianShi_Reward_DBID_List" ] = jinShiDBIDList
			if len( jinShiDBIDList ) >= 1:
				# �ӽ�ʿ�б���ѡ����һ����Ϊ״Ԫ
				try:
					dbID = self.getBestResultDB( leadMembers )
					playerName = self.jinshiDict[dbID][2]
					self._zhuangyuan = playerName
					jinShiDBIDList.remove( dbID )
					leadMembers.pop( dbID )
					if self.jinshiDict.has_key( dbID ):
						self.jinshiDict.pop( dbID )
					content = cschannel_msgs.KE_JU_VOICE_25
					BigWorld.globalData['MailMgr'].send( None, playerName, 1, 2, cschannel_msgs.KE_JU_VOICE_21, cschannel_msgs.KE_JU_VOICE_24, content, 0, "" )
				except KeyError:
					ERROR_MSG( "jin shi dict jinshiDict databaseID %s is None player" % dbID )
					return
			if len( jinShiDBIDList ) >= 1:
				# ѡ��״Ԫ�󣬴�ʣ��Ľ�ʿ�б���ѡ����һ������Ϊ����
				try:
					dbID = self.getBestResultDB( leadMembers )
					playerName = self.jinshiDict[dbID][2]
					self._bangyan = playerName
					jinShiDBIDList.remove( dbID )
					leadMembers.pop( dbID )
					if self.jinshiDict.has_key( dbID ):
						self.jinshiDict.pop( dbID )
					content = cschannel_msgs.KE_JU_VOICE_26
					BigWorld.globalData['MailMgr'].send( None, playerName, 1, 2, cschannel_msgs.KE_JU_VOICE_21, cschannel_msgs.KE_JU_VOICE_24, content, 0, "" )
				except KeyError:
					ERROR_MSG( "jin shi dict jinshiDict databaseID %s is None player" % dbID )
					return
			if len( jinShiDBIDList ) >= 1:
				# ѡ����ۺ󣬴�ʣ��Ľ�ʿ�б���ѡ����һ������Ϊ̽��
				# ʣ��ľ��ǽ�ʿ��
				try:
					dbID = self.getBestResultDB( leadMembers )
					playerName = self.jinshiDict[dbID][2]
					self._tanhua = playerName
					jinShiDBIDList.remove( dbID )
					leadMembers.pop( dbID )
					if self.jinshiDict.has_key( dbID ):
						self.jinshiDict.pop( dbID )
					content = cschannel_msgs.KE_JU_VOICE_27
					BigWorld.globalData['MailMgr'].send( None, playerName, 1, 2, cschannel_msgs.KE_JU_VOICE_21, cschannel_msgs.KE_JU_VOICE_24, content, 0, "" )
				except KeyError:
					ERROR_MSG( "jin shi dict jinshiDict databaseID %s is None player" % dbID )
					return

			jinShiNameListStr = ""
			for dbID in jinShiDBIDList:
				content = cschannel_msgs.KE_JU_VOICE_20
				try:
					playerName = self.jinshiDict[dbID][2]
				except KeyError:
					ERROR_MSG( "jin shi dict jinshiDict databaseID %s is None player" % dbID )
					return
				BigWorld.globalData['MailMgr'].send( None, playerName, 1, 2, cschannel_msgs.KE_JU_VOICE_21, cschannel_msgs.KE_JU_VOICE_24, content, 0, "" )
				jinShiNameListStr += ( playerName + "," )

			# ���˵��н��ģ�ʣ�����ģ���mail֪ͨ����
			for jinShiDbID, tupleValue in self.jinshiDict.items():
				playerName = tupleValue[2]
				if jinShiDbID in jinShiDBIDList: continue
				if playerName in [ self._zhuangyuan, self._bangyan, self._tanhua ]: continue
				content = cschannel_msgs.KE_JU_VOICE_28
				BigWorld.globalData['MailMgr'].send( None, playerName, 1, 2, cschannel_msgs.KE_JU_VOICE_21, cschannel_msgs.KE_JU_VOICE_24, content, 0, "" )

			self._examinationType = NO_EXAMINATION
			self._examLostTime = 0
			dianshiOverMsg = cschannel_msgs.BCT_KJKS_CELEBRATE_FOR_JINSHI
			if jinShiNameListStr != "":
				Love3.g_baseApp.anonymityBroadcast( dianshiOverMsg % jinShiNameListStr, [] )
			else:
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_KJKS_NO_JINSHI, [] )
			if self._zhuangyuan == "":
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_KJHS_NO_1, [] )
			else:
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_KJHS_TOP_1%self._zhuangyuan, [] )
			if self._bangyan == "":
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_KJHS_NO_2, [] )
			else:
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_KJHS_TOP_2%self._bangyan, [] )
			if self._tanhua == "":
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_KJHS_NO_3, [] )
			else:
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_KJHS_TOP_3%self._tanhua, [] )
			if self._zhuangyuan == "" and self._bangyan == "" and self._tanhua == "":
				return
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_KJKS_TOP_THREE_NOTIFY, [] )


	def requestIEExpReward( self, mailBox, playerName, level, isRight, count, gameYield ):
		"""
		define method
		�ƾٵĽ�������
		count:���
		"""
		#player = BigWorld.entities[ mailBox.id ]
		itemID = 0
		exp = 0
		eType = self._examinationType
		if NO_EXAMINATION == eType:
			return
		if eType == XIANGSHI:
			exp = csconst.ACTIVITY_GET_EXP( csdefine.ACTIVITY_EXAMINATION_XIANGSHI, level, count )
		elif eType == HUISHI:
			exp = csconst.ACTIVITY_GET_EXP( csdefine.ACTIVITY_EXAMINATION_HUISHI, level, count )
		elif eType == DIANSHI:
			exp = csconst.ACTIVITY_GET_EXP( csdefine.ACTIVITY_EXAMINATION_DIANSHI, level, count )

		if isRight:
			# Ӧ�߻�Ҫ��CSOL-2603�������⽱�����ʸ�Ϊ5% 2009-02-05 SongPeifang
			if random.random() <= 0.05 * gameYield:
				# Ӧ�߻�Ҫ��CSOL-2603�������⽱�����ʸ�Ϊ5% 2009-02-05 SongPeifang
				# ���⽱���ɾ����Ϊ��Ʒ��CSOL-2628��
				# �����50%�ļ��ʻ�����飬20%�ļ��ʻ�ô�����ϣ�20%�ļ��ʻ�õͼ����˱�ʯ��10%�ļ��ʻ�ø߼����˱�ʯ
				mailBox.cell.giveKJReward( eType )
		else:
			exp = exp * 0.3

		exp = int( exp + 0.5 )
		mailBox.cell.onAddIEExpReward( exp )
		# ���Я�������������ﾭ���1/4
		mailBox.pcg_addActPetExp( exp/4 )

	def submitResults( self, playerDBID, correctRate, examTime, playerName ):
		"""
		Define method.
		�����������ύ������
		"""
		if self._todayExamType == HUISHI:
			# �ƾٻ���
			if self.jurenDict.has_key( playerDBID ):
				examData = self.jurenDict[playerDBID]
				if examData[0] < correctRate or ( examData[0] == correctRate and examTime < examData[1] ):
					# ֻ�е��ɼ���֮ǰ�ĺõ�����²ŻḲ��֮ǰ�ĳɼ�
					self.jurenDict[playerDBID] = ( correctRate, examTime, playerName )
			else:
				self.jurenDict[playerDBID] = ( correctRate, examTime, playerName )
		elif self._todayExamType == DIANSHI:
			# �ƾٵ���
			self.jinshiDict[playerDBID] = ( correctRate, examTime, playerName )

	def calcExamResults( self ):
		"""
		���������㿼�Խ��
		ʱ��̡�׼ȷ�ʸߵĽ���
		�����̫�����ˣ����ã���ʱ�����Ҫ��д������
		"""
		calcCount = 0
		calcingResults = {}
		leadMembers = {}		# { databaseID:(correctRate, examTime, playerName) }
		if self._todayExamType == HUISHI:
			calcingResults = self.jurenDict.copy()
			calcCount = JU_REN_COUNT
		elif self._todayExamType == DIANSHI:
			calcingResults = self.jinshiDict.copy()
			calcCount = JIN_SHI_COUNT
		if len( calcingResults ) <= calcCount:
			# �μӵ��˶�����calcCount��
			calcCount = len( calcingResults )
		if calcCount == 0:
			return leadMembers

		def func( a, b ):
			if a[1][0] == b[1][0]:
				return cmp( a[1][1], b[1][1] )
			else:
				return cmp( b[1][0], a[1][0] )

		memberVector = calcingResults.items()
		memberVector.sort( cmp = func )
		memberVector = memberVector[:calcCount]
		return dict( memberVector )
		
	def getBestResultDB( self, leadMembers ):
		"""
		leadMembers
		"""
		if len( leadMembers ) == 0:
			return -1
		tempRate = leadMembers.values()[0][0]
		leastTime = leadMembers.values()[0][1]
		topResultDBID = -1
		for dbID, tupleValue in leadMembers.iteritems():
			if tupleValue[0] > tempRate:
				tempRate = tupleValue[0]
				topResultDBID = dbID
			if tupleValue[0] == tempRate and tupleValue[1] <= leastTime:
				leastTime = tupleValue[1]
				topResultDBID = dbID
		return topResultDBID

	def requestIETitleReward( self, playerMB, playerDatabaseID, playerName, ieType, zhuangyuanItemID, isItemsbagFull ):
		"""
		Define method.
		�����ȡ�ƺŽ���
		��������ڿƾٽ�����֮��
		"""
		if playerMB == None:
			ERROR_MSG( "empty MAILBOX can't get Examinate title reward��" )
			return

		#if not BigWorld.entities.has_key( playerMB.id ):
		#	ERROR_MSG( "IDΪ%s������޷���ȡ�ƾٳƺŽ�������Ϊ�䲻���ڡ�" % playerMB.id )
		#	return

		#player = BigWorld.entities[ playerMB.id ]
		if ieType == HUISHI and self.jurenDict.has_key( playerDatabaseID ):
			playerMB.cell.addTitle( T_JUREN )
			self.jurenDict.pop( playerDatabaseID )
			huishiRewardDBIDList = BigWorld.globalData[ "IE_HuiShi_Reward_DBID_List" ]
			if playerDatabaseID in huishiRewardDBIDList:
				del huishiRewardDBIDList[playerDatabaseID]
				BigWorld.globalData[ "IE_HuiShi_Reward_DBID_List" ] = huishiRewardDBIDList
		elif ieType == DIANSHI:
			if not self.jinshiDict.has_key( playerDatabaseID ):
				if self._zhuangyuan == playerName:
					if isItemsbagFull:
						playerMB.client.onStatusMessage( csstatus.IE_BAG_FULL, "" )
						return
					item = g_items.createDynamicItem( zhuangyuanItemID, 1 )
					if item!= None:
						# ״Ԫ�������⽱��(��ƷID�ɲ߻��ڶԻ�����)
						#item.setBindType( ItemTypeEnum.CBT_PICKUP, playerMB )
						playerMB.cell.addItem( item, csdefine.ADD_ITEM_REQUESTIETITLE )
					playerMB.cell.addTitle( T_ZHUANGYUAN )
					self._zhuangyuan = ""
				elif self._bangyan == playerName:
					playerMB.cell.addTitle( T_BANGYAN )
					self._bangyan = ""
				elif self._tanhua == playerName:
					playerMB.cell.addTitle( T_TANHUA )
					self._tanhua = ""
			else:
				playerMB.cell.addTitle( T_JINSHI )
				self.jinshiDict.pop( playerDatabaseID )
			dianshiRewardDBIDList = BigWorld.globalData[ "IE_DianShi_Reward_DBID_List" ]
			if playerDatabaseID in dianshiRewardDBIDList:
				dianshiRewardDBIDList.remove( playerDatabaseID )
				BigWorld.globalData[ "IE_DianShi_Reward_DBID_List" ] = dianshiRewardDBIDList