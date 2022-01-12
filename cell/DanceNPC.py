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
		self.canCheck = False  #True表示在玩家放空间技能会判定，否则即使放技能，也不会被NPC判定
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
		if self.isWitnessed: #在玩家视野范围内
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
		if self.isWitnessed: #在玩家视野范围内
			self.planesOtherClients( "playDanceAction", ([danceActions[self.getCurrentDanceListItem()],], 0) )#练习的时候是没有时间限制的	
		else:
			ERROR("player AOI is too small, can't find danceNPC!")
		self.testDanceActivity()

	def nextRound(self, srcEntityID):
		#exposed method 
		#挑战或练习，先看结果是不是挑战成功或失败，再判断单局
		print "nextRound", self.danceType, self.roleCurSkillID, self.roleCurSkillID, self.getCurrentDanceListItem(), self.danceList
		if self.canCheck:
			if self.danceType and (self._timer != 0): #挑战斗舞时成功与失败的判定，必需在timer有效期内才判断
				if self.currentResult:
					self.say(cschannel_msgs.CHALLENGEDANCE_VERYGOOD)
					self.isRight()
				else:
					self.say(cschannel_msgs.CHALLENGEDANCE_LOSE)
					self.isWrong()
				self.planesOtherClients( "playDanceAction", ([danceActions[self.getCurrentDanceListItem()], self.getTime()]) )
				self.testDanceActivity()
			elif not self.danceType:#练习斗舞的判定
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
				
		if self.getCurrentDanceListItem(): #弹出最前面一个，进入下一轮
			self.danceList.remove(self.getCurrentDanceListItem())
		INFO_MSG("isRight self.danceList is %s"%self.danceList)
	
	def isWrong(self):
		if self.danceType:
			self._timer = 0
		self.comoboPoint = 0 #连击数清零
		self.onConditionChange()
		#self.currentContextResult(False)
		if self.danceType:
			self.challengeFailed()
		INFO_MSG("isWrong self.danceList is %s"%self.danceList)
		
	def getCurrentDanceListItem(self):
		if self.danceList:
			return self.danceList[0]
		if not self.danceType:
			self.danceList = self.setDanceList() #练习斗舞时列表动作已经全部做完，玩家继续做，需要生成新的动作列表，挑战斗舞不会走到这一步
		return self.danceList[0]
		
	def currentContextResult(self, result):
		if result:#当前挑战正确，都会把列表头的动作去掉，并且正确的连击会+1
			if self.getCurrentDanceListItem():
				self.danceList.pop(self.getCurrentDanceListItem())
				self.comoboPoint += 1				
		else:#当前挑战失败
			if self.DanceType:	
				self.challengeFailed()
			self.comoboPoint = 0 #连击数清零
		#更新客户端连击次数	
		self.planesOtherClients( "refreshDanceComobo", (self.comoboPoint,) )
		#在练习模式下，如果self.danceList is None,重新设置self.danceList
		if (not self.danceType) and (not self.danceList):
			self.danceList = self.setDanceList()
		
			
	def finishPlayAction(self, srcEntityID):
		#exposed method
		if self.danceType:#斗舞
			time = self.getTime() + 0.5  #加的0.5秒属于延时，主要考虑网络延时
			self._timer = self.addTimer(time, 0, self.challengeFailed)#只有在斗舞时才添加超时的Timer
			
	def getTime(self):
		#服务器验证加0.5秒延时
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
			return True #挑战斗舞成功
		return False  #挑战斗舞失败

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
			return 30  #挑战金牌舞王需要的连击次数要求
		elif self.challengeIndex < 5:
			return 25 #挑战银牌舞王需要的连击次数要求
		elif self.challengeIndex < 10:
			return 20 #挑战铜牌舞王需要的连击次数要求
		elif self.challengeIndex < 20:
			return 10 #挑战候选舞王需要的连击次数要求
		
	def challengeFailed(self):
		self.say(cschannel_msgs.CHALLENGEDANCE_LOSE)
		self.getCurrentSpaceBase().cell.noticeChallengeResult(False)#让副本通告玩家最终挑战失败
		
	def challengeSuccess(self):
		self.say(cschannel_msgs.CHALLENGEDANCE_WIN)
		self.getCurrentSpaceBase().cell.noticeChallengeResult(True)		#让副本通告玩家最终挑战成功
	
	def setDanceChallengeIndex(self, challengeIndex):
		#define method
		self.challengeIndex = challengeIndex
		
	def cancelParctice(self, srcEntityID):
		#exposed method
		self.canCheck = False
		
	def cancelChallenge(self):
		"""
		在cell/Role.py中调用
		"""
		self._timer = 0 #取消验证计时timer
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
		#测试时，提示当前动作是第几式
		if BigWorld.globalData.has_key("ASDanceMgr"):
			if BigWorld.globalData["ASDanceMgr"]:
				self.say(cschannel_msgs.DANCEITEM%self.getCurrentDanceListItem())
		