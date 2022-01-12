# -*- coding: gb18030 -*-
from bwdebug import *
import cschannel_msgs
import BigWorld
import Love3
import csdefine
import csconst
import time
import csstatus
from DanceKingInfos import DanceKingData
import cPickle
NEXT = 1401
DANCETIMELIMIT 				= 8*60*60
class DanceMgr( BigWorld.Base):
	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		
		self.spaceMailboxes = []  #[spaceMailbox,] ,��ս����ϰ���˸�����mailbox
		self.dancingKingInfos = {} #{"modelInfo":None ,"Time":0 , "isChallenge":False, "dbid":0}
		self.setDancingKingInfos() #��ʼ��������Ϣ
		self.playerMailboxes = {}
		self.playerDanceTimeInfos = {}  #{playerName:{DKType:1-5, "danceStart": time, "danceEnd":time, "danceKingStart":time, "danceKingEnd":time}} DKType��������
		self.danceTimeOutTimerID = 	None   #������һ��Ҫ���ŵ�timer
		self.danceKingTimeOutTimerID = None	#������һ��Ҫ���������ŵ�timer
		self.DanceHallInfos = {}   #{dbid:(spaceNumber, index, modelInfo)}
		self.DanceHallBases = []   #[mailbox]
		self.danceHallSpaceDomainBase = []
		self.danceKingMailboxes = {}  #1��19������ģ�͵���Ϣ{location:mailbox}
		self.registerGlobally( "DanceMgr", self._onRegisterManager )
		#���δ���ʱû��isCreate
		self.loadDanceKingInfoFromDB()
		BigWorld.globalData["ASDanceMgr"] = {}
		
	
	def testDanceActivity(self,  personLimit, timeLimit, flag):
		#define method
		#personLimit:����������������
		#timeLimit:����ʱ������
		#flag: �������ƺ�ʱ�������Ƿ�ʹ��Ĭ������, FalseΪʹ��Ĭ�����ã�TrueΪʹ�� personLimit, timeLimit��������
		if flag:
			BigWorld.globalData["ASDanceMgr"].update({"personLimit":personLimit})
			DANCETIMELIMIT = timeLimit
			BigWorld.globalData["ASDanceMgr"] = BigWorld.globalData["ASDanceMgr"]
			INFO_MSG("""reset BigWorld.globalData["ASDanceMgr"] is %s."""%BigWorld.globalData["ASDanceMgr"])
		else:
			BigWrold.globalData["ASDanceMgr"] = {}
			DANCETIMELIMIT = 8*60*60
			BigWorld.globalData["ASDanceMgr"] = BigWorld.globalData["ASDanceMgr"]
		
	
	def setDancingKingInfos(self):
		for i in range(1, 20):
			self.dancingKingInfos[i] = {"modelInfo":None ,"Time":0 , "isChallenge":False, "dbid":0}

	def setDanceHallInfo(self, param):
		#define method 
		#param = ( dbid, self.spaceNumber, index, modelInfo )
		if not self.DanceHallInfos.has_key(param[0]):
			self.DanceHallInfos = {param[0]:(0,0,None)}
		self.DanceHallInfos[param[0]] = (param[1], param[2], param[3]) 

	def setModelInfo(self, playerModelInfo, challengeIndex, playerBase, dbid):
		"""
		define method 
		modelInfo: ����ģ����ص���Ϣ������������֣��Ǹ��ֵ�
		Time: ������ս�ɹ�ʱ��
		isChallenge :	�����Ƿ���������ս��������ս���Ͳ�����ս
		���޸���λ�õĶ�Ӧ��Ϣ�����޸����¾���������ĵ���ʱ��
		"""
		if not challengeIndex:
			ERROR_MSG("player's Dance Data is Wrong!")		
		newKingName = playerModelInfo["roleName"]
		#����Ѿ�������������ȡ��������
		level = playerModelInfo["level"]
		if self.playerInDanceKings(newKingName):
			self.getDanceExp(newKingName, playerBase, True ,level) #��ȡ�Ѿ����������ľ���
		elif self.getDanceTime(newKingName ,False):   
			self.getDanceExp(newKingName, playerBase, False ,level)   #��ȡ��ͨλ�õľ���
			playerBase.cell.loseDancePosition(self.getDancePosition(dbid)) #ȥ����ͨλ�õ�ģ��
			if dbid in self.DanceHallInfos:
				self.DanceHallInfos.pop(dbid)  #������������ȥ����Ϊ��������ͨλ����Ϣ
		#oldKingName = self.dancingKingInfos[challengeIndex]["modelInfo"]["roleName"]
		#����������Ѿ��ڰ��ϣ��Ѱ���������ԭ����λ��ȥ��
		if self.playerInDanceKings(newKingName):
			index = self.playerInDanceKings(newKingName)
			self.spawnDanceKing(index, None)
			self.dancingKingInfos[index] = {"modelInfo":None ,"Time":0 , "isChallenge":False, "dbid":0}
			self.updatePlayerClient(index)
			
		if self.dancingKingInfos[challengeIndex]["modelInfo"]: #֪ͨ������
			oldKingName = self.dancingKingInfos[challengeIndex]["modelInfo"]["roleName"]
			self.leaveDanceKing(oldKingName)
			
		#����������
		self.becomeDanceKing(newKingName, playerModelInfo, challengeIndex, dbid, playerBase)
		self.updatePlayerClient(challengeIndex)


	def becomeDanceKing(self, playerName, playerModelInfo, challengeIndex, dbid, playerBase):
		self.dancingKingInfos[challengeIndex] = {"modelInfo":playerModelInfo ,"Time":time.time(),"isChallenge":False, "dbid":dbid}	#����������Ϣ
		self.playerDanceTimeInfos[playerName]["danceEnd"] = time.time()
		self.playerDanceTimeInfos[playerName]["danceKingStart"] = time.time()
		self.playerDanceTimeInfos[playerName]["danceKingEnd"] = time.time() + DANCETIMELIMIT
		self.playerDanceTimeInfos[playerName]["DKType"] = self.danceKineLevel(challengeIndex)
		assert challengeIndex > 0 and challengeIndex < 19, "DanceMgr about DanceKing's index is error index%d!"%challengeIndex
		self.spawnDanceKing(challengeIndex, playerModelInfo)  #ˢ������

		#self.danceKingMailboxes[challengeIndex].cell.spawnNPCDanceKing(self.getDanceKingObj(playerModelInfo))

	def getDancePosition(self, dbid):
		if self.DanceHallInfos.has_key(dbid):
			return self.DanceHallInfos[dbid][1]
		ERROR_MSG("DanceMgr DanceHallInfos Data is %s !!!!!!!!!can not get position, but can becomeDanceKing!"%self.DanceHallInfos)
		return 0
		
	def getFreeDancePosition(self, dbid):
		for index in xrange(20,40):
			if index not in self.getSameSpaceNumberInfos(dbid):
				return index
		ERROR_MSG("could not find free position in this DanceCopy!")
		

	def spawnDanceKing(self, index, modelInfo):
		for danceHallBase in self.DanceHallBases:
			danceHallBase.cell.spawnDanceKing(index, modelInfo)

				
	def getDanceKingObj(self, roleInfo):
		obj = DanceKingData()
		obj[ "uname" ] = roleInfo["roleName"]		
		obj[ "level" ] = roleInfo["level"]
		obj[ "tongName" ] = roleInfo["tongName"]
		obj[ "raceclass" ] = roleInfo["raceclass"]
		obj[ "hairNumber" ] = roleInfo["hairNumber"]
		obj[ "faceNumber" ] = roleInfo["faceNumber"]
		obj[ "bodyFDict" ] = roleInfo["bodyFDict"]
		obj[ "volaFDict" ] = roleInfo["volaFDict"]
		obj[ "breechFDict" ] = roleInfo["breechFDict"]
		obj[ "feetFDict" ] = roleInfo["feetFDict"]
		obj[ "lefthandFDict" ] = roleInfo["lefthandFDict"]
		obj[ "righthandFDict" ] = roleInfo["righthandFDict"]
		obj[ "talismanNum" ] = roleInfo["talismanNum"]
		obj[ "fashionNum" ] = roleInfo["fashionNum"]
		obj[ "adornNum" ] = roleInfo["adornNum"]
		obj[ "headTextureID" ] = roleInfo["headTextureID"]	
		return obj	
	
	def leaveDanceKing(self, playerName):
		index = self.playerInDanceKings(playerName)
		modelInfo = self.dancingKingInfos[index]["modelInfo"]  #��ʱ����modelInfo
		self.playerDanceTimeInfos[playerName]["danceKingEnd"] = time.time()
		self.playerDanceTimeInfos[playerName]["danceStart"] = time.time()
		self.playerDanceTimeInfos[playerName]["danceEnd"] = time.time() + DANCETIMELIMIT
		self.dancingKingInfos[index] = {"modelInfo":None ,"Time":0 , "isChallenge":False, "dbid":0}
		assert index > 0 and index < 19, "DanceMgr about DanceKing's index is error index%d!"%index
		self.spawnDanceKing(index, None)
		
		BigWorld.lookupBaseByName("Role", playerName, self.loseDanceKingCb)
		BigWorld.globalData["MailMgr"].send(None, 
											playerName, 
											csdefine.MAIL_TYPE_QUICK, 
											csdefine.MAIL_SENDER_TYPE_NPC, 
											"", 
											cschannel_msgs.DANCETITLE, 
											cschannel_msgs.LOSEDANCEKING, 
											0, 
											[])

	def loseDanceKingCb(self, playerBase):
		#ȥ������ս�ɹ��ߵ�buff
		if playerBase is None: #ͨ������û���ҵ�baseMailbox����Ҳ�����
			return 	
		playerBase.client.onStatusMessage(csstatus.JING_WU_SHI_KE_LOSE_DANCEKING, "")
		
	def danceKingTimeOutCb(self, playerBase):
		if playerBase is None: #ͨ������û���ҵ�baseMailbox����Ҳ�����
			return 	
		playerBase.cell.setTemp("getDancePositionNow", True)
		playerBase.client.onStatusMessage(csstatus.JING_WU_SHI_KE_KING_TIMEOUT, "")	
		
	def danceTimeOutCb(self, playerBase):
		if playerBase is None: #ͨ������û���ҵ�baseMailbox����Ҳ�����
			return 	
		playerBase.client.onStatusMessage(csstatus.JING_WU_SHI_KE_TIMEOUT, "")				
	
	def addDanceExpTime(self, playerName):
		#define method
		if not self.playerDanceTimeInfos.has_key(playerName):
			self.playerDanceTimeInfos = {playerName:{"danceStart":0, "danceEnd":0, "DKType":csdefine.DANCER_NONE, "danceKingStart":0, "danceKingEnd":0}}
		self.playerDanceTimeInfos[playerName]["danceStart"] = time.time() #������ͨ�����Ŀ�ʼʱ��
		self.playerDanceTimeInfos[playerName]["danceEnd"] = time.time() + DANCETIMELIMIT #������ͨ�����Ľ���ʱ��
		
	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register DanceMgr Fail!" )
			self.registerGlobally( "DanceMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["DanceMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("DanceMgr Create Complete!")		
	
	def registerDanceHallSpaceDomain(self, base):
		#define method
		INFO_MSG("self.danceHallSpaceDomainBase is %s"%base)		
		self.danceHallSpaceDomainBase = base

	def getExistSpaceNumber(self):
		tmp = []
		if self.DanceHallInfos:
			for value[0] in self.DanceHallInfos.values():
				if value[0]  not in tmp:
					tmp.append(value[0])
		return tmp
	
	def registerSpace( self, spaceMailbox ):
		#define method
		#spaceMailbox ,spacecopydance mailbox  ���˸���mailbox
		if spaceMailbox not in self.spaceMailboxes:
			self.spaceMailboxes.append(spaceMailbox)
		else:#�����ϲ����ߵ�����
			ERROR_MSG("spaceMailbox(%i)register to DanceMgr failed!"%spaceMailbox.id)
			
	def removeSpace( self, spaceMailbox ):
		#define method
		#spaceMailbox ,spacecopydance mailbox ���˸���mailbox
		if spaceMailbox in self.spaceMailboxes:
			self.spaceMailboxes.remove(spaceMailbox)
		else:
			ERROR_MSG("DanceMgr remove spaceMailbox(%i) failed!"%spaceMailbox.id)
			
	def indexIsChallenged(self, baseMailbox, challengeIndex, canChallenge):
		#define method 
		if self.dancingKingInfos[challengeIndex]["modelInfo"]:
			self.dancingKingInfos[challengeIndex]["isChallenge"] = canChallenge #True��ʾ������������ս�������˲�����ս
			baseMailbox.cell.gotoDanceChallengeSpace(challengeIndex)
		else : #��ǰλ��û���˵�ʱ��
			baseMailbox.cell.challengeSuccess()

	def canGetDancePosition(self, playerBase, index, dbid, playerName ):
		#define method 
		if index < 20 or index > 39:
			ERROR_MSG("player[%s] get position's index[%d] is not in index 20 to 39"%(playerName, index))
			return 
		if self.playerInDanceKings(playerName):
			playerBase.client.onStatusMessage(csstatus.JING_WU_SHI_DANCEKING, "")
			return 
		if self.getSameSpaceNumberInfos(dbid) is not None and playerName in [ value["roleName"] for value in self.getSameSpaceNumberInfos(dbid).values()]:
			playerBase.client.onStatusMessage(csstatus.JING_WU_SHI_KE_GET_POSITION, "")
			return 
		if index in self.getSameSpaceNumberInfos(dbid): #��ǰλ���Ѿ�����
			playerBase.client.onStatusMessage(csstatus.JING_WU_SHI_KE_POSITION_HAS_PERSON ,"")
			return 
		if self.getDanceTime(playerName, False) or self.getDanceTime(playerName, True):  # ����δ��ȡ
			playerBase.client.onStatusMessage(csstatus.JING_WU_SHI_KE_EXP_NOT_GET, "")
			return 
		else:
			playerBase.client.canGetDancePositionCb(index)
			playerBase.client.onStatusMessage(csstatus.JING_WU_SHI_KE_GET_POSITION_INDEX, str((index,)))

	def canChallengeDanceKing(self, playerBase, challengeIndex, playerName):
		"""
		DANCE_CAN_CHALLENGE					= 1		#��ʾ������ս
		DANCE_IN_PROTECT_TIME				= 2		#��ʾ���ڱ���ʱ��
		DANCE_IS_CHALLENGED					= 3		#��ʾ��������ս
		DANCE_CHALLENGE_MYSELF				= 4		#��ʾ��ս�Լ�
		DANCE_CHALLENGE_LOWER_LEVEL_DANCER	= 5		#��ʾ��ս�͵ȼ��������Լ�Ҳ������
		DANCE_POSITION_IS_EMPTY				= 6		#��ʾ��ǰλ��û���������Լ�����ֱ�ӳ�Ϊ����
		DANCE_EXP_NOT_GET				= 7		#��ʾ��ǰ��δ��ȡ�ľ���
		DANCEK_NOT_GET_POSITION				= 8		#��ʾδ��ȡλ��
		"""
		if not self.isGetPosition(playerName):
			playerBase.client.canChallengeDanceKingCb( challengeIndex ,csdefine.DANCEK_NOT_GET_POSITION )
			playerBase.client.onStatusMessage(csstatus.JING_WU_SHI_KE_NOT_GET_POSITION ,"")
			return 
		"""			
		elif self.getDanceTime(playerName, False):
			playerBase.client.canChallengeDanceKingCb( challengeIndex ,csdefine.DANCE_EXP_NOT_GET )
			playerBase.client.onStatusMessage(csstatus.JING_WU_SHI_KE_EXP_NOT_GET, "")
			return 
		"""
		if self.dancingKingInfos[challengeIndex]["modelInfo"] is None:
			if self.playerInDanceKings(playerName):
				playerBase.client.canChallengeDanceKingCb( challengeIndex ,csdefine.DANCE_POSITION_IS_EMPTY )
				#playerBase.cell.noticeChallengeResult( csdefine.DANCE_CAN_CHALLENGE )#ֱ����ս�ɹ�
				return
		if self.dancingKingInfos[challengeIndex]["modelInfo"] is not None:
			if playerName == self.dancingKingInfos[challengeIndex]["modelInfo"]["roleName"]: #��ս�Լ�
				playerBase.client.canChallengeDanceKingCb( challengeIndex ,csdefine.DANCE_CHALLENGE_MYSELF )
				return
		if self.playerInDanceKings(playerName): #��ս�͵ȼ�����
			if self.danceKineLevel(challengeIndex) > self.danceKineLevel(self.playerInDanceKings(playerName)): 
				playerBase.client.canChallengeDanceKingCb( challengeIndex ,csdefine.DANCE_CHALLENGE_LOWER_LEVEL_DANCER )
				return
		if time.time() - self.dancingKingInfos[challengeIndex]["Time"] < csdefine.DANCE_IN_PROTECT_TIME :
			playerBase.client.canChallengeDanceKingCb( challengeIndex ,csdefine.DANCE_IN_PROTECT_TIME )	
			return
		if time.time() - self.dancingKingInfos[challengeIndex]["Time"] >= csdefine.DANCE_IN_PROTECT_TIME :
			if self.dancingKingInfos[challengeIndex]["isChallenge"]:
				playerBase.client.canChallengeDanceKingCb( challengeIndex ,csdefine.DANCE_IS_CHALLENGED )
				return
			else:
				playerBase.client.canChallengeDanceKingCb( challengeIndex ,csdefine.DANCE_CAN_CHALLENGE )
				return
		else:
			ERROR_MSG("DanceMgr about canChallengeDanceKing could't find this condition!")

	def danceKineLevel(self, index):
		"""
		DANCER_GOLDEN	= 1		#��������
		DANCER_SILVER	= 2		#��������
		DANCER_COPPER	= 3		#ͭ������
		DANCER_CANDIDATE	= 4		#��ѡ����
		DANCER_NONE		= 0		#δ�ϰ�		
		"""
		if index == 1:
			return csdefine.DANCER_GOLDEN #��������
		elif index < 5:
			return csdefine.DANCER_SILVER #��������
		elif index < 10:
			return csdefine.DANCER_COPPER #ͭ������
		elif index < 20:
			return csdefine.DANCER_CANDIDATE #��ѡ����
		else:
			return csdefine.DANCER_NONE #�������� 
		

	def playerNameToIndex(self):
		temp = {}
		if self.dancingKingInfos is None:
			return temp
		for index, dancingKingInfo in self.dancingKingInfos.items():
			if dancingKingInfo["modelInfo"] is not None:
				temp.update({dancingKingInfo["modelInfo"]["roleName"] : index})
		return temp
	
	def playerInDanceKings(self, playerName):
		#����������λ�ã���0����ʾ����������
		if self.playerNameToIndex() is None:
			return 0
		for key,value in self.playerNameToIndex().items():
			if key == playerName:
				return value     
		return 0
		
	def sendDanceKingInfos(self, cellMailBox):
		#define method
		#������������Ϣ�����
		#�ȴ�����DancingKingInfos�����ʱ�����DancingKingInfos����Ĵ󲿷ֶ��ǿգ����Բ��÷��͵���Ϣ
		cellMailBox.requestDancingKingInfos(self.dancingKingInfos)

	def dealDancingKingInfos(self):
		tmp = {}
		if self.dancingKingInfos is None:
			return tmp
		for index in self.dancingKingInfos.keys():
			if self.dancingKingInfos[index]["modelInfo"]:
				tmp.update({index:self.dancingKingInfos[index]})
		return tmp
	
	def addPlayerMailbox(self, dbid, mailbox):
		#define method
		self.playerMailboxes.update({dbid:mailbox})
		
	def removePlayerMailbox(self, dbid):
		#define method		
		if dbid in self.playerMailboxes:
			self.playerMailboxes.pop(dbid)
			
	def updatePlayerClient(self, challengeIndex):
		#���¿ͻ��˵���Ϣ
		for dbid, mailbox in self.playerMailboxes.items():
			mailbox.client.addDancingKingInfo(challengeIndex,self.dancingKingInfos[challengeIndex])
			#mailbox.client.updateDanceKingModel(challengeIndex, self.dancingKingInfos[challengeIndex]["modelInfo"])
			DEBUG_MSG("update info to client��%s, challengeIndex is %d, dancingKingInfo is %s!"%(mailbox, challengeIndex, self.dancingKingInfos[challengeIndex]))

	def queryDanceExp(self, playerName, playerBase, type, level):
		#define method 
		#type��BOOL ��Ϊ0��ʾ��������ͨ���飬1Ϊ�������顣
		exp = int(self.calDanceExp(playerName, type, level)/60)
		if type:
			playerBase.client.onStatusMessage( csstatus.JING_WU_SHI_KE_QUERYDANCEKINGEXP, str((exp,)) )
		else:
			playerBase.client.onStatusMessage(csstatus.JING_WU_SHI_KE_QUERYDANCEEXP, str((exp,)) )
			
	def getDanceExp(self, playerName, playerBase, type ,level):
		#define method
		#type��BOOL ��Ϊ0��ʾ��������ͨ���飬1Ϊ�������顣
		exp = int(self.calDanceExp(playerName, type, level)/60)
		playerBase.cell.getDanceExp(exp ,type)
		if self.playerDanceTimeInfos.has_key(playerName):
			self.playerDanceTimeInfos[playerName]["danceStart"] = time.time()
		
		if type:
			playerBase.client.onStatusMessage(csstatus.JING_WU_SHI_KE_GETDANCEKINGEXP, str((exp,)) )
		else:
			playerBase.client.onStatusMessage(csstatus.JING_WU_SHI_KE_GETDANCEEXP, str((exp,)) )

	def calDanceExp(self, playerName, type, level):
		#���㵱ǰ��þ��� 
		return self.getDanceTime(playerName, type) * self.DKTypeRatito(playerName) * self.getDanceMinExp(level)  
			
	def getDanceTime(self, playerName, type):
		#type��BOOL ��Ϊ0��ʾ��������ͨ���飬1Ϊ�������顣
		lasttime = 0
		if self.playerDanceTimeInfos.has_key(playerName):
			lasttime = self.timeOutLast(playerName, type)
		INFO_MSG("player[%s] getDanceTime is %d, type is %d"%(playerName ,lasttime , type))
		return lasttime
		
	def timeOutLast(self, playerName, type):
		#���㵱ǰ�����ۻ�ʱ��
		lasttime = 0 
		if not self.playerDanceTimeInfos.has_key(playerName):
			return lasttime
		if type: #����
			if self.playerDanceTimeInfos[playerName]["danceKingEnd"] <= self.playerDanceTimeInfos[playerName]["danceKingStart"]:
				lasttime = 0 
			elif time.time() >= self.playerDanceTimeInfos[playerName]["danceKingEnd"]: 
				lasttime = self.playerDanceTimeInfos[playerName]["danceKingEnd"] - self.playerDanceTimeInfos[playerName]["danceKingStart"]
			else:
				lasttime = time.time() - self.playerDanceTimeInfos[playerName]["danceKingStart"]
		else: #��ͨ		
			if self.playerDanceTimeInfos[playerName]["danceEnd"] <= self.playerDanceTimeInfos[playerName]["danceStart"]:
				lasttime = 0 
			elif time.time() >= self.playerDanceTimeInfos[playerName]["danceEnd"]: 
				lasttime = self.playerDanceTimeInfos[playerName]["danceEnd"] - self.playerDanceTimeInfos[playerName]["danceStart"]
			else:
				lasttime = time.time() - self.playerDanceTimeInfos[playerName]["danceStart"]
		INFO_MSG("cal dancetime type��%d, playerName is %s"%(type, playerName))
		return lasttime 

	def getDanceMinExp(self, level):
		return 3.5 * pow(level, 1.5) + 9
			
	def DKTypeRatito(self, playerName):
		if not self.playerDanceTimeInfos.has_key(playerName):
			return 0
		if self.playerDanceTimeInfos[playerName]["DKType"] == csdefine.DANCER_GOLDEN:
			ratito = csdefine.DANCER_GOLDEN_RATITO 
		elif self.playerDanceTimeInfos[playerName]["DKType"] == csdefine.DANCER_SILVER:
			ratito = csdefine.DANCER_SILVER_RATITO
		elif self.playerDanceTimeInfos[playerName]["DKType"] == csdefine.DANCER_COPPER:
			ratito = csdefine.DANCER_COPPER_RATITO
		elif self.playerDanceTimeInfos[playerName]["DKType"] == csdefine.DANCER_CANDIDATE:
			ratito = csdefine.DANCER_CANDIDATE_RATITO
		else:
			ratito = csdefine.DANCER_NONE_RATITO
		return ratito
			
	def calDanceTimeForTimer(self):
		if not self.getTimeOutList(False):
			self.danceTimeOutTimerID = self.addTimer(DANCETIMELIMIT, 0, DANCENEXT)  #����б�Ϊ�վͼ�һ��8Сʱ��timer
		self.danceTimeOutTimerID = self.addTimer(self.getDanceTimeOut(False), 0, DANCENEXT)

	def calDanceKingTimeForTimer(self):
		if not self.getTimeOutList(True):
			self.danceKingTimeOutTimerID = self.addTimer(DANCETIMELIMIT, 0, DANCEKINGNEXT)  #����б�Ϊ�վͼ�һ��8Сʱ��timer
		self.danceKingTimeOutTimerID = self.addTimer(self.getDanceTimeOut(True), 0, DANCEKINGNEXT)		
			
	def getDanceTimeOut(self, type):
		#return [[playerName, endtime],][0][1] - time.time()
		if self.playerDanceTimeInfos is None:
			return None
		tmp = []
		for playerName in self.playerDanceTimeInfos.keys():
			if self.getDanceTime(playerName, type):			
				if type:
					tmp.append([playerName, self.playerDanceTimeInfos[playerName]["danceKingEnd"]])
				else:
					tmp.append([playerName, self.playerDanceTimeInfos[playerName]["danceEnd"]])
		tmp = sorted(tmp, key = lambda item : item[1])
		return tmp[0][1] - time.time() 
	
	def onTimer( self, id, userArg ):
		if userArg == DANCENEXT:
			self.danceTimeOver()
		elif userArg == DANCEKINGNEXT:
			self.danceKingTimeOver()
		self.calDanceTimeForTimer()	 #��ͨ��timer
		self.calDanceKingTimeForTimer()  #������timer
		
	def danceTimeOver(self):
		if self.getTimeOutList(False) is not None:
			playerName = self.getTimeOutList(False)[0][0]
			BigWorld.globalData["MailMgr"].send(None, 
												playerName, 
												csdefine.MAIL_TYPE_QUICK, 
												csdefine.MAIL_SENDER_TYPE_NPC, 
												"", 
												cschannel_msgs.DANCETITLE, 
												cschannel_msgs.DANCEKINGTIMEOUT, 
												0, 
												[])
			INFO_MSG("DanceMgr send mail to playerName:%s when danceTimeOver!"%playerName)
			BigWorld.lookupBaseByName("Role", playerName, self.danceTimeOutCb)
			BigWorld.lookUpDBIDByName("Role", playerName, self.lookUpDBIDByNameCb)
			
	def lookUpDBIDByNameCb(self, dbid):
		#����ͨλ��ʱ�䵽��֮��ȥ��DanceHallInfos�еĶ�Ӧdbid��Ϣ
		if dbid is not None:
			if dbid in self.DanceHallInfos:
				self.DanceHallInfos.pop(dbid)
				self.danceHallSpaceDomainBase.removeDBIDToSpaceNumber(dbid)
	
	def danceKingTimeOver(self):
		if self.getTimeOutList(True) is not None:
			playerName = self.getTimeOutList(True)[0][0]				
			if self.playerDanceTimeInfos[playerName]["DKType"] > csdefine.DANCER_NONE:	
				BigWorld.globalData["MailMgr"].send(None, 
													playerName,
													csdefine.MAIL_TYPE_QUICK, 
													csdefine.MAIL_SENDER_TYPE_NPC, 
													"", 
													cschannel_msgs.DANCETITLE, 
													cschannel_msgs.DANCETIMEOUT, 
													0, 
													[])
				INFO_MSG("DanceMgr send mail to playerName:%s when danceKingTimeOver!"%playerName)
				BigWorld.lookupBaseByName("Role", playerName, self.danceKingTimeOutCb)				
				
	def getAllModelInfos(self, dbid):
		#get index 1 to 39 modelInfo
		tmp = {}
		for i in xrange(20):  #danceKingModels
			if self.dancingKingInfos.has_key(i):
				tmp.update({i:self.dancingKingInfos[i]["modelInfo"]})
			else:
				tmp.update({i:None})
		tmp.update(self.getDanceModelInfos(dbid))  #danceModel
		return tmp

	def getDanceModelInfos(self, dbid):
		#get index 20 to 39 modelInfo
		tmp = {}
		for i in range(20, 40):
			if self.getSameSpaceNumberInfos(dbid) is None:
				tmp.update({i:None})
			elif not self.getSameSpaceNumberInfos(dbid).has_key(i):
				tmp.update({i:None})
			else:
				tmp.update({i:self.getSameSpaceNumberInfos(dbid)[i]})
		return tmp	
		
		
	def getSameSpaceNumberInfos(self, dbid):
		# self.DanceHallInfos = {dbid:{(spaceNumber, index, modelInfo)}	
		# return {index:modelInfo} 
		tmp = {}	
		if not self.DanceHallInfos.has_key(dbid):
			return tmp
		spaceNumber = self.DanceHallInfos[dbid][0]
		for k, v in self.DanceHallInfos.items():
			if v[0] == spaceNumber:
				tmp.update({v[1]:v[2]})
		return tmp
		
	def isGetPosition(self, playerName):
		#�Ƿ��ȡλ��
		if not self.playerDanceTimeInfos.has_key(playerName):
			return False
		if time.time() < self.playerDanceTimeInfos[playerName]["danceEnd"] or time.time() < self.playerDanceTimeInfos[playerName]["danceKingEnd"]:
			return True
		return False
		
	def registerDanceModelSpawnPoint(self, locationIndex, baseMailbox):
		#define method
		#baseMailbox: SpawnPointDanceModel's base
		# ����������1��19������ģ�͵�ˢ�µ�
		if not self.danceKingMailboxes.has_key( locationIndex ):
			self.danceKingMailboxes.update({locationIndex:baseMailbox})	
		else:
			self.danceKingMailboxes[locationIndex] = baseMailbox
			
	#------------------------------------------------------------------------------------------
	def onDestroy( self ):
		"""
		�����ٵ�ʱ����������
		"""
		self.save()

	#------------------------------------------------------------------------------------------
	def save( self ):
		"""
		��������Ҫ����
		"""
		self.writeToDB()

	#------------------------------------------------------------------------------------------
	def loadDanceKingInfoFromDB( self ):
		"""
		�����ݿ���س�Ա��Ϣ
		"""
		cmd = "select id, sm_dancingKingInfos, sm_playerDanceTimeInfos  from tbl_DanceMgr" 
		BigWorld.executeRawDatabaseCommand( cmd, self.loadDanceKingInfoFromDB_Callback )

	def loadDanceKingInfoFromDB_Callback( self, results, dummy, error ):
		"""
		���س�Ա��Ϣ ���ݿ�ص�
		"""
		if (error):
			ERROR_MSG( error )
			return

		if len( results ) <= 0:
			# �������ԭ�������ĳ��ɾ�����ʺ�
			DEBUG_MSG( "tbl_DanceMgr is None or not create!"  )
		else:
			
			print "loadDanceKingInfoFromDB_Callback results = ",results
			self.dancingKingInfos = cPickle.loads(results[0][1])
			self.playerDanceTimeInfos = cPickle.loads(results[0][2])
			print "111111111111111 dancingKingInfos",self.dancingKingInfos,self.playerDanceTimeInfos
			
			
	#------------------------------------------------------------------------------------------
	def queryTemp( self, key, default = None ):
		"""
		���ݹؼ��ֲ�ѯ��ʱmapping����֮��Ӧ��ֵ

		@return: ����ؼ��ֲ������򷵻�defaultֵ
		"""
		try:
			return self.tempMapping[key]
		except KeyError:
			return default

	def setTemp( self, key, value ):
		"""
		define method.
		��һ��key��дһ��ֵ

		@param   key: �κ�PYTHONԭ����(����ʹ���ַ���)
		@param value: �κ�PYTHONԭ����(����ʹ�����ֻ��ַ���)
		"""
		self.tempMapping[key] = value

	def popTemp( self, key, default = None ):
		"""
		�Ƴ�������һ����key���Ӧ��ֵ
		"""
		return self.tempMapping.pop( key, default )

	def removeTemp( self, key ):
		"""
		define method.
		�Ƴ�һ����key���Ӧ��ֵ
		@param   key: �κ�PYTHONԭ����(����ʹ���ַ���)
		"""
		self.tempMapping.pop( key, None )

	#------------------------------------------------------------------------------------------

	def registerDanceHallBase(self, danceHallBase):
		#define method
		self.DanceHallBases.append(danceHallBase)
		#ˢ��������ģ��
		for index in self.dancingKingInfos.keys():
			modelInfo = self.dancingKingInfos[index]["modelInfo"]
			danceHallBase.cell.spawnDanceKing(index, modelInfo)

		
	def removeDanceHallBase(self, danceHallBase):
		#define method
		if danceHallBase in self.DanceHallBases:
			self.DanceHallBases.remove(danceHallBase)
		
	#-------------------------------------------------------------------------------------------------
	
	def enterDanceHall(self, dbid, danceHallbase, playerName, playerBase):
		#define method
		for index, modelInfo in self.getDanceModelInfos(dbid).items():
			danceHallbase.cell.spawnDanceKing(index, modelInfo)
		if self.getDanceTime(playerName, False):#�Ѿ���λ��
			if self.getDancePosition(dbid): 
				if playerName == self.DanceHallInfos[dbid][2]["roleName"]:
					playerBase.client.canGetDancePositionCb(self.getDancePosition(dbid))
					INFO_MSG("player[%s] get DancePosition[%d]."%(playerName, self.getDancePosition(dbid)))
			else:
				playerBase.client.canGetDancePositionCb(self.getFreeDancePosition(dbid))
				INFO_MSG("player[%s] get Free DancePosition[%d]."%(playerName, self.getFreeDancePosition(dbid)))
				
	def updateDanceHall(self, dbid, modelInfo, danceHallbase):
		#define.
		danceHallbase.cell.spawnDanceKing(index, modelInfo)
		
	def getLoseDanceKingPosition(self, dbid, playerBase):
		#define method
		playerBase.client.canChallengeDanceKingCb(self.getFreeDancePosition(dbid))
		
				

	
			
			