# -*- coding: gb18030 -*-
# $Id: QuestRandomRecordType.py,v 1.1 2008-01-09 04:04:43 zhangyuxing Exp $

import time
from bwdebug import *

class QuestRandomRecordType:
	"""
	һ��ѭ�������¼
	"""
	def __init__( self ):
		"""
		"""
		self.questGroupID = 0		# ������ID
		self.count = 0				# �����У�������������
		self.deposit = 0			# Ѻ������
		self.point = 0				# ����ֵ
		self.startTime = 0 			# ������ʼʱ��
		self.degree = 0				# ��ɵ������� ����ʵ��һ����
		self.curID = 0				# ��ǰ������ID
		self.taskType = 0			# ����Ŀ������
		self.randRwdRate = ""		# �����������������(��ʽ����Ϊ"count_1:rate1|count_2:rate2"��"3:0.5|4:0.6")
		self.isRecorded = False		# �Ƿ��Ƕ�ȡ�ļ�¼(Ĭ�������ΪFalse��ʾ�������Ļ�����)
		
	
	def init( self, id ):
		"""
		"""
		self.questGroupID = id

	
	def getDegree( self ):
		"""
		ȡ��������������
		@return: INT
		"""
		return self.degree
	
	def incDegree( self ):
		"""
		���������
		"""
		self.degree += 1
	
	def isRecordedQuest( self ):
		"""
		�Ƿ��¼��������
		"""
		return self.isRecorded
	
	def setRecordedQuest( self, isRecorded ):
		"""
		���ü�¼
		"""
		self.isRecorded = isRecorded
		
	def getQuestGroupID( self ):
		"""
		ȡ��������ID
		"""
		return self.questGroupID
	
	def addCount( self, count):
		"""
		���ӵ�������������
		"""
		self.count += count
	
	def getCount( self ):
		"""
		��õ�������������
		"""
		return self.count
		
	def setRandRwdRate( self, count, rate ):
		"""
		���û��������������
		"""
		rateStr = str( rate )[0:6]
		key = "count_" + str( count )
		randRwdRate = key + ":" + rateStr
		randRwdRateIndex = self.randRwdRate.find( key )
		if randRwdRateIndex != -1:
			# ԭ���Ѿ�������ģ�Ҫ���
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
		��ȡ���������������
		"""
		rwdRate = 2.0	# ������ʱ��������1.0�����ﷵ��2.0��ʾ�����н���
		key = "count_" + str( count )
		randRwdRateIndex = self.randRwdRate.find( key )
		if randRwdRateIndex != -1:
			# ע�⣬������Ϊ�����������10��������Ϊ0-9�����Բ���Ҫ����count_1��count_11��ì��
			keyLen = len( key )
			rwdRateData = self.randRwdRate[randRwdRateIndex:].split("|")[0]
			try:
				rwdRate = float( rwdRateData.split(":")[1] )
			except IndexError:
				ERROR_MSG( "���������������¼�ĵ�%s�εļ�¼����ȷ!" % count )
		return rwdRate
		
	def resetSubQTCountRewardRate( self ):
		"""
		���û��������������
		"""
		self.randRwdRate = ""
		
	def addDeposit( self, deposit ):
		"""
		����Ѻ��
		"""
		self.deposit += deposit
	
	def returnDeposit( self ):
		"""
		����Ѻ��
		"""
		deposit = self.deposit
		self.deposit = 0
		return deposit
	
	def addPoint( self, point ):
		"""
		���ӻ���
		"""
		self.point += point
	
	def takePoint( self ):
		"""
		ȡ�߻���
		"""
		point = self.point
		self.point = 0
		return point

	def reset( self ):
		"""
		�������ݣ����ÿ�ʼʱ��Ϊ���죬���õ�ǰ��ɴ���Ϊ0
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
		��������ʱ���뵱ǰʱ���Ƿ���ͬһ��
		@return: bool
		"""
		year, month, day = time.localtime()[:3]
		curr = year * 10000 + month * 100 + day
		return curr == self.startTime
	
	def resetSingle( self ):
		"""
		���õ���ѭ��������Ϣ
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
	# BigWorld User Defined Type �Ľӿ�                              #
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