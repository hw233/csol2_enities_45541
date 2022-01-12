# -*- coding: gb18030 -*-
# $Id: QuestRandomLogsType.py,v 1.6 2008-08-29 02:31:46 songpeifang Exp $


class QuestRandomLogsType:
	"""
	所有循环任务日志
	"""
	def __init__( self ):
		"""
		"""
		self._questsRandomLog = {}
		
	def __getitem__( self, questID ):
		return self._questsRandomLog[questID]

	def __len__( self ):
		return len( self._questsRandomLog )
	
	def __setitem__( self, key, value ):
		
		self._questsRandomLog[key] = value
		
	def __delitem__( self, key ):
		"""
		"""
		if not self._questsRandomLog.has_key( key ):
			return
		del self._questsRandomLog[key]
	
	def has_randomQuestGroup( self, questID ):
		"""
		判断是否有指定的随机任务
		
		@return: BOOL
		"""
		return questID in self._questsRandomLog
	
	
	def add( self, questID, record ):
		"""
		加入一个任务
		
		@param tasks: 任务目标列表
		@type  tasks: QuestDataType
		@return: None
		"""
		self._questsRandomLog[questID] = record
	
	def delete( self, questID ):
		"""
		删除一条任务记录
		"""
		if not self._questsRandomLog.has_key( questID ):
			return		
		del self._questsRandomLog[questID]
	
	def addDeposit( self, questID, deposit ):
		"""
		增加押金
		@param questID:	任务ID
		@type  questID: QUESTID
		@param deposit:	任务押金
		@type  deposit:	INT
		"""
		if self.has_randomQuestGroup( questID ):
			self._questsRandomLog[questID].addDeposit( deposit )
	
	def returnDeposit( self, questID ):
		"""
		反还押金
		@param questID:	任务ID
		@type  questID: QUESTID
		"""
		if self.has_randomQuestGroup( questID ):
			return self._questsRandomLog[questID].returnDeposit()
		return 0
	
	def addPoint( self, questID, point ):
		"""
		增加积分
		@param questID:	任务ID
		@type  questID: QUESTID
		@param 	point: 任务积分
		@type 	point: 	INT
		"""
		if self.has_randomQuestGroup( questID ):		
			self._questsRandomLog[questID].addPoint( point )
	
	def takePoint( self, questID ):
		"""
		取走积分
		@param questID:	任务ID
		@type  questID: QUESTID
		"""
		if self.has_randomQuestGroup( questID ):
			return self._questsRandomLog[questID].takePoint()
		return 0
	
	def setSubQTCountRewardRate( self, questID, count, rate ):
		"""
		设置环任务奖励随机概率
		"""
		if self.has_randomQuestGroup( questID ):
			self._questsRandomLog[questID].setRandRwdRate( count, rate )
	
	def getSubQTCountRewardRate( self, questID, count ):
		"""
		获取环任务奖励随机概率
		"""
		if self.has_randomQuestGroup( questID ):
			return self._questsRandomLog[questID].getRandRwdRate( count )
		return 2.0
	
	def resetSubQTCountRewardRate( self, questID ):
		"""
		重置环任务奖励随机概率
		"""
		if self.has_randomQuestGroup( questID ):
			self._questsRandomLog[questID].resetSubQTCountRewardRate()
		
	def addCount( self, questID, count ):
		"""
		增加单组循环子任务次数
		@param questID:	任务ID
		@type  questID: QUESTID
		@param 	count:  单组次数
		@type 	count:	INT
		"""
		if self.has_randomQuestGroup( questID ):
			self._questsRandomLog[questID].addCount( count )
	
	
	def getCount( self, questID ):
		"""
		取得单组循环字任务次数
		@param questID:	任务ID
		@type  questID: QUESTID
		"""
		if not self._questsRandomLog.has_key( questID ):
			return 0
		return self._questsRandomLog[questID].getCount()

	def checkStartGroupTime( self, questID ):
		"""
		检查组任务开始时间
		@param questID:	任务ID
		@type  questID: QUESTID
		"""
		if not questID in self._questsRandomLog.keys():
			return True
		return self._questsRandomLog[questID].checkStartTime()
	
	def resetGroupQuest( self, questID ):
		"""
		重置组任务
		@param questID:	任务ID
		@type  questID: QUESTID
		"""
		if self.has_randomQuestGroup( questID ):
			self._questsRandomLog[questID].reset()
	
	
	def addGroupQuestCount( self, questID ):
		"""
		增加组任务次数
		@param questID:	任务ID
		@type  questID: QUESTID
		"""
		if self.has_randomQuestGroup( questID ):
			self._questsRandomLog[questID].incDegree()
	
	
	def isGroupQuestRecorded( self, questID ):
		"""
		是否是记录过的组任务
		@param questID:	任务ID
		@type  questID: QUESTID
		"""
		if self.has_randomQuestGroup( questID ):
			return self._questsRandomLog[questID].isRecordedQuest()
		return False
	
	def setGroupQuestRecorded( self, questID, isRecorded ):
		"""
		设置记录过的组任务
		@param questID:	任务ID
		@type  questID: QUESTID
		"""
		if self.has_randomQuestGroup( questID ):
			self._questsRandomLog[questID].setRecordedQuest( isRecorded )
	
	def resetSingleGroupQuest( self, questID ):
		"""
		重置单组任务
		@param questID:	任务ID
		@type  questID: QUESTID
		"""
		if self.has_randomQuestGroup( questID ):
			self._questsRandomLog[questID].resetSingle()
	
	def getGroupQuestCount( self, questID ):
		"""
		取得完成多少组
		@param questID:	任务ID
		@type  questID: QUESTID
		"""
		if not self._questsRandomLog.has_key( questID ):
			return 0
		return self._questsRandomLog[questID].getDegree()
	
	def setGroupCurID( self, questID, subQuestID ):
		"""
		设置子任务ID
		@param questID:	任务ID
		@type  questID: QUESTID
		@param subQuestID:	子任务ID
		@type  subQuestID: QUESTID
		"""
		if self.has_randomQuestGroup( questID ):
			self._questsRandomLog[questID].setCurID( subQuestID )
	
	def queryGroupCurID( self, questID ):
		"""
		查询当前子任务ID
		@param questID:	任务ID
		@type  questID: QUESTID
		"""
		return self._questsRandomLog[questID].queryCurID()
	##################################################################
	# BigWorld User Defined Type 的接口                              #
	##################################################################
	def getDictFromObj( self, obj ):
		"""
		"""
		
		items = []
		d = { "values":items }
		for k, v in obj._questsRandomLog.iteritems():
			items.append( v )
		return d
	
	
	def createObjFromDict( self, dict ):
		"""
		"""
		obj = QuestRandomLogsType()
		for value in dict["values"]:
			if value:	# 如果value为None则表示数据有错，将会直接忽略
				obj._questsRandomLog[value.getQuestGroupID()] = value
		return obj
	
	def isSameType( self, obj ):
		"""
		"""
		return isinstance( obj, QuestRandomLogsType )
	
instance = QuestRandomLogsType()