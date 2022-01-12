# -*- coding: gb18030 -*-
#
"""
"""
import BigWorld
from bwdebug import *
import csdefine
import csconst
import ECBExtend
from NPC import NPC
import time
import random
from CPUCal import CPU_CostCal
import cschannel_msgs 
danceActions = {1:"dance1_1", 2:"dance2_1", 3:"dance3_1", 4:"dance4_1" ,5:"dance5_1"}
skillIDToAction = {csconst.DanceSkill1:1, csconst.DanceSkill2:2, csconst.DanceSkill3:3, csconst.DanceSkill4:4, csconst.DanceSkill5:5 }
msg = {1:cschannel_msgs.CHALLENGEDANCE_DANCE1, 2:cschannel_msgs.CHALLENGEDANCE_DANCE2, 3:cschannel_msgs.CHALLENGEDANCE_DANCE3, 4:cschannel_msgs.CHALLENGEDANCE_DANCE4, 5:cschannel_msgs.CHALLENGEDANCE_DANCE5 }
class DanceNPC( NPC ):
	"""
	
	"""
	def __init__( self ):
		NPC.__init__(self)
		self.danceType = False
		self.danceList = self.setDanceList()
		self.challengeIndex = 0
		self._timer = 0
		self.canCheck = False  #True��ʾ����ҷſռ似�ܻ��ж�������ʹ�ż��ܣ�Ҳ���ᱻNPC�ж�
		self.currentResult = False
		self.roleCurSkillID = 0 
		self.getCurrentSpaceBase().cell.regesiterNPC(self)
		self.onConditionChange()
		

	def setDanceList(self):
		return [random.randint(1,5) for i in range(30)]
		
	def startDanceChallenge(self, challengeIndex):
		self.setDanceChallengeIndex(challengeIndex)
		self.danceType = True
		self.canCheck = True
		self.danceList = self.setDanceList() 
		self._timer = 0 
		if self.isWitnessed: #�������Ұ��Χ��
			self.planesOtherClients( "playDanceAction", ([danceActions[self.getCurrentDanceListItem()], self.getTime()]) )
		else:
			ERROR("player AOI is too small, can't find danceNPC!")
		self.testDanceActivity()
		
	def startDancePractice(self, challengeIndex):
		self.setDanceChallengeIndex(challengeIndex)
		self.danceType = False
		self.canCheck = True
		self.danceList = self.setDanceList() 
		self._timer = 0 
		if self.isWitnessed: #�������Ұ��Χ��
			self.planesOtherClients( "playDanceAction", ([danceActions[self.getCurrentDanceListItem()],], 0) )#��ϰ��ʱ����û��ʱ�����Ƶ�	
		else:
			ERROR("player AOI is too small, can't find danceNPC!")
		self.testDanceActivity()

	def nextRound(self, srcEntityID):
		#exposed method 
		#��ս����ϰ���ȿ�����ǲ�����ս�ɹ���ʧ�ܣ����жϵ���
		print "nextRound", self.danceType, self.roleCurSkillID, self.roleCurSkillID, self.getCurrentDanceListItem(), self.danceList
		if self.canCheck:
			if self.danceType and (self._timer != 0): #��ս����ʱ�ɹ���ʧ�ܵ��ж���������timer��Ч���ڲ��ж�
				if self.currentResult:
					self.say(cschannel_msgs.CHALLENGEDANCE_VERYGOOD)
					self.isRight()
				else:
					self.say(cschannel_msgs.CHALLENGEDANCE_LOSE)
					self.isWrong()
				self.planesOtherClients( "playDanceAction", ([danceActions[self.getCurrentDanceListItem()], self.getTime()]) )
				self.testDanceActivity()
			elif not self.danceType:#��ϰ������ж�
				if self.currentResult:
					self.say(cschannel_msgs.CHALLENGEDANCE_VERYGOOD)
					self.isRight()
				else:
					self.say(cschannel_msgs.CHALLENGEDANCE_REDO)
					self.isWrong()	
				self.planesOtherClients( "playDanceAction", ([danceActions[self.getCurrentDanceListItem()],], 0) )
				self.testDanceActivity()
				

	def isRight(self):
		if self.danceType:
			self._timer = 0
		#self.currentContextResult(True)
		self.comoboPoint += 1
		self.onConditionChange()
		if self.challengeResult():
			self.challengeSuccess()			
				
		if self.getCurrentDanceListItem(): #������ǰ��һ����������һ��
			self.danceList.remove(self.getCurrentDanceListItem())
		INFO_MSG("isRight self.danceList is %s"%self.danceList)
	
	def isWrong(self):
		if self.danceType:
			self._timer = 0
		self.comoboPoint = 0 #����������
		self.onConditionChange()
		#self.currentContextResult(False)
		if self.danceType:
			self.challengeFailed()
		INFO_MSG("isWrong self.danceList is %s"%self.danceList)
		
	def getCurrentDanceListItem(self):
		if self.danceList:
			return self.danceList[0]
		if not self.danceType:
			self.danceList = self.setDanceList() #��ϰ����ʱ�б����Ѿ�ȫ�����꣬��Ҽ���������Ҫ�����µĶ����б���ս���費���ߵ���һ��
		return self.danceList[0]
		
	def currentContextResult(self, result):
		if result:#��ǰ��ս��ȷ��������б�ͷ�Ķ���ȥ����������ȷ��������+1
			if self.getCurrentDanceListItem():
				self.danceList.pop(self.getCurrentDanceListItem())
				self.comoboPoint += 1				
		else:#��ǰ��սʧ��
			if self.DanceType:	
				self.challengeFailed()
			self.comoboPoint = 0 #����������
		#���¿ͻ�����������	
		self.planesOtherClients( "refreshDanceComobo", (self.comoboPoint,) )
		#����ϰģʽ�£����self.danceList is None,��������self.danceList
		if (not self.danceType) and (not self.danceList):
			self.danceList = self.setDanceList()
		
			
	def finishPlayAction(self, srcEntityID):
		#exposed method
		if self.danceType:#����
			time = self.getTime() + 0.5  #�ӵ�0.5��������ʱ����Ҫ����������ʱ
			self._timer = self.addTimer(time, 0, self.challengeFailed)#ֻ���ڶ���ʱ����ӳ�ʱ��Timer
			
	def getTime(self):
		#��������֤��0.5����ʱ
		if self.comoboPoint <= 10:
			return 8
		elif self.comoboPoint <= 20:
			return 5
		elif self.comoboPoint <= 25:
			return 3
		elif self.comoboPoint <=30:
			return 2
			
	def challengeResult(self):
		if self.comoboPoint >= self.getNeedPoints():
			return True #��ս����ɹ�
		return False  #��ս����ʧ��

	def checkDanceResult(self, skillID):
		result = None
		if self.canCheck:
			self.roleCurSkillID = skillID
			if self.danceType:
				if skillIDToAction[skillID] == self.getCurrentDanceListItem():
					result = True
				else:
					result = False
			else:
				if skillIDToAction[skillID] == self.getCurrentDanceListItem():
					result = True
				else:
					result = False		
			self.currentResult = result	


	def getNeedPoints(self):
		if self.challengeIndex == 1:
			return 30  #��ս����������Ҫ����������Ҫ��
		elif self.challengeIndex < 5:
			return 25 #��ս����������Ҫ����������Ҫ��
		elif self.challengeIndex < 10:
			return 20 #��սͭ��������Ҫ����������Ҫ��
		elif self.challengeIndex < 20:
			return 10 #��ս��ѡ������Ҫ����������Ҫ��
		
	def challengeFailed(self):
		self.say(cschannel_msgs.CHALLENGEDANCE_LOSE)
		self.getCurrentSpaceBase().cell.noticeChallengeResult(False)#�ø���ͨ�����������սʧ��
		
	def challengeSuccess(self):
		self.say(cschannel_msgs.CHALLENGEDANCE_WIN)
		self.getCurrentSpaceBase().cell.noticeChallengeResult(True)		#�ø���ͨ�����������ս�ɹ�
	
	def setDanceChallengeIndex(self, challengeIndex):
		#define method
		self.challengeIndex = challengeIndex
		
	def cancelParctice(self, srcEntityID):
		#exposed method
		self.canCheck = False
		
	def cancelChallenge(self):
		"""
		��cell/Role.py�е���
		"""
		self._timer = 0 #ȡ����֤��ʱtimer
		self.challengeFailed()

	def onConditionChange(self):
		params = {}
		params["comoboPoint"] = self.comoboPoint
		if self.danceType: 
			params["timeLimit"] = self.getTime() + time.time()
		else :
			params["timeLimit"] = 0
		self.getCurrentSpaceBase().cell.onConditionChange(params)
		
	def testDanceActivity(self):
		#����ʱ����ʾ��ǰ�����ǵڼ�ʽ
		if BigWorld.globalData.has_key("ASDanceMgr"):
			if BigWorld.globalData["ASDanceMgr"]:
				self.say(cschannel_msgs.DANCEITEM%self.getCurrentDanceListItem())
		