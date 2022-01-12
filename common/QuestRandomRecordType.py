# -*- coding: gb18030 -*-
# $Id: QuestRandomRecordType.py,v 1.1 2008-01-09 04:04:43 zhangyuxing Exp $

import time
from bwdebug import *

class QuestRandomRecordType:
	"""
	一组循环任务记录
	"""
	def __init__( self ):
		"""
		"""
		self.questGroupID = 0		# 组任务ID
		self.count = 0				# 单组中，完成子任务次数
		self.deposit = 0			# 押金数量
		self.point = 0				# 积分值
		self.startTime = 0 			# 组任务开始时间
		self.degree = 0				# 完成的组数。 （真实的一天内
		self.curID = 0				# 当前子任务ID
		self.taskType = 0			# 任务目标类型
		self.randRwdRate = ""		# 环任务随机奖励概率(格式必须为"count_1:rate1|count_2:rate2"如"3:0.5|4:0.6")
		self.isRecorded = False		# 是否是读取的记录(默认情况下为False表示是正常的环任务)
		
	
	def init( self, id ):
		"""
		"""
		self.questGroupID = id

	
	def getDegree( self ):
		"""
		取得任务完成组次数
		@return: INT
		"""
		return self.degree
	
	def incDegree( self ):
		"""
		组次数增长
		"""
		self.degree += 1
	
	def isRecordedQuest( self ):
		"""
		是否记录过的任务
		"""
		return self.isRecorded
	
	def setRecordedQuest( self, isRecorded ):
		"""
		设置记录
		"""
		self.isRecorded = isRecorded
		
	def getQuestGroupID( self ):
		"""
		取得组任务ID
		"""
		return self.questGroupID
	
	def addCount( self, count):
		"""
		增加单组的子任务次数
		"""
		self.count += count
	
	def getCount( self ):
		"""
		获得单组的子任务次数
		"""
		return self.count
		
	def setRandRwdRate( self, count, rate ):
		"""
		设置环任务奖励随机概率
		"""
		rateStr = str( rate )[0:6]
		key = "count_" + str( count )
		randRwdRate = key + ":" + rateStr
		randRwdRateIndex = self.randRwdRate.find( key )
		if randRwdRateIndex != -1:
			# 原来已经储存过的，要清除
			fStr = self.randRwdRate[ :randRwdRateIndex + len( key ) + 1 ]
			bStr = self.randRwdRate[ randRwdRateIndex + len( key ) + 1: ]
			sperateIndex = bStr.find( "|" )
			if sperateIndex != -1:
				bStr = rateStr + bStr[ sperateIndex: ]
			else:
				bStr = rateStr
			self.randRwdRate = fStr + bStr
		else:
			self.randRwdRate = ( self.randRwdRate + "|" + randRwdRate )
	
	def getRandRwdRate( self, count ):
		"""
		获取环任务奖励随机概率
		"""
		rwdRate = 2.0	# 奖励的时候随机最大到1.0，这里返回2.0表示不会有奖励
		key = "count_" + str( count )
		randRwdRateIndex = self.randRwdRate.find( key )
		if randRwdRateIndex != -1:
			# 注意，这里因为环任务最多是10环，索引为0-9，所以不需要考虑count_1和count_11的矛盾
			keyLen = len( key )
			rwdRateData = self.randRwdRate[randRwdRateIndex:].split("|")[0]
			try:
				rwdRate = float( rwdRateData.split(":")[1] )
			except IndexError:
				ERROR_MSG( "环任务随机奖励记录的第%s次的记录不正确!" % count )
		return rwdRate
		
	def resetSubQTCountRewardRate( self ):
		"""
		重置环任务奖励随机概率
		"""
		self.randRwdRate = ""
		
	def addDeposit( self, deposit ):
		"""
		增加押金
		"""
		self.deposit += deposit
	
	def returnDeposit( self ):
		"""
		反还押金
		"""
		deposit = self.deposit
		self.deposit = 0
		return deposit
	
	def addPoint( self, point ):
		"""
		增加积分
		"""
		self.point += point
	
	def takePoint( self ):
		"""
		取走积分
		"""
		point = self.point
		self.point = 0
		return point

	def reset( self ):
		"""
		重置数据，设置开始时间为今天，设置当前完成次数为0
		"""
		year, month, day = time.localtime()[:3]
		self.startTime = year * 10000 + month * 100 + day
		self.degree = 0
		self.count = 0
		self.deposit = 0
		self.point = 0
		self.taskType = 0
		self.isRecorded = False
	
	def checkStartTime( self ):
		"""
		检查接任务时间与当前时间是否是同一天
		@return: bool
		"""
		year, month, day = time.localtime()[:3]
		curr = year * 10000 + month * 100 + day
		return curr == self.startTime
	
	def resetSingle( self ):
		"""
		重置单组循环任务信息
		"""
		self.count = 0
		self.deposit = 0
		self.point = 0
	
	def setCurID( self, id ):
		self.curID = id
	
	def queryCurID( self ):
		return self.curID
	
	def setTaskType( self, taskType ):
		self.taskType = taskType

	def getTaskType( self ):
		return self.taskType

	##################################################################
	# BigWorld User Defined Type 的接口                              #
	##################################################################
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.
		
		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		if isinstance( obj, dict ):	
			return obj
		return { "questGroupID" : obj.questGroupID, "count" : obj.count, "deposit" : obj.deposit, "point" : obj.point, "startTime":obj.startTime, "degree":obj.degree, "curID": obj.curID, "taskType": obj.taskType, "randRwdRate": obj.randRwdRate, "isRecorded": obj.isRecorded }
		
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = QuestRandomRecordType()
		obj.questGroupID = dict["questGroupID"]
		obj.count = dict["count"]
		obj.deposit = dict["deposit"]
		obj.point = dict["point"]
		obj.startTime = dict["startTime"]
		obj.degree	= dict["degree"]
		obj.curID = dict["curID"]
		obj.taskType = dict["taskType"]
		obj.randRwdRate = dict["randRwdRate"]
		obj.isRecorded = dict["isRecorded"]
		return obj
	
	def isSameType( self, obj ):
		"""
		"""
		return isinstance( obj, ( QuestRandomRecordType, dict ) )
	
	def copy( self ):
		"""
		"""
		record = QuestRandomRecordType()
		record.questGroupID = self.questGroupID
		record.count = self.count
		record.deposit = self.deposit
		record.point = self.point
		record.startTime = self.startTime
		record.degree = self.degree
		record.curID = self.curID
		record.taskType = self.taskType
		record.randRwdRate = self.randRwdRate
		record.isRecorded = self.isRecorded
		return record
		
instance = QuestRandomRecordType()