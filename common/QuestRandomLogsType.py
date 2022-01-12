# -*- coding: gb18030 -*-
# $Id: QuestRandomLogsType.py,v 1.6 2008-08-29 02:31:46 songpeifang Exp $


class QuestRandomLogsType:
	"""
	����ѭ��������־
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
		�ж��Ƿ���ָ�����������
		
		@return: BOOL
		"""
		return questID in self._questsRandomLog
	
	
	def add( self, questID, record ):
		"""
		����һ������
		
		@param tasks: ����Ŀ���б�
		@type  tasks: QuestDataType
		@return: None
		"""
		self._questsRandomLog[questID] = record
	
	def delete( self, questID ):
		"""
		ɾ��һ�������¼
		"""
		if not self._questsRandomLog.has_key( questID ):
			return		
		del self._questsRandomLog[questID]
	
	def addDeposit( self, questID, deposit ):
		"""
		����Ѻ��
		@param questID:	����ID
		@type  questID: QUESTID
		@param deposit:	����Ѻ��
		@type  deposit:	INT
		"""
		if self.has_randomQuestGroup( questID ):
			self._questsRandomLog[questID].addDeposit( deposit )
	
	def returnDeposit( self, questID ):
		"""
		����Ѻ��
		@param questID:	����ID
		@type  questID: QUESTID
		"""
		if self.has_randomQuestGroup( questID ):
			return self._questsRandomLog[questID].returnDeposit()
		return 0
	
	def addPoint( self, questID, point ):
		"""
		���ӻ���
		@param questID:	����ID
		@type  questID: QUESTID
		@param 	point: �������
		@type 	point: 	INT
		"""
		if self.has_randomQuestGroup( questID ):		
			self._questsRandomLog[questID].addPoint( point )
	
	def takePoint( self, questID ):
		"""
		ȡ�߻���
		@param questID:	����ID
		@type  questID: QUESTID
		"""
		if self.has_randomQuestGroup( questID ):
			return self._questsRandomLog[questID].takePoint()
		return 0
	
	def setSubQTCountRewardRate( self, questID, count, rate ):
		"""
		���û��������������
		"""
		if self.has_randomQuestGroup( questID ):
			self._questsRandomLog[questID].setRandRwdRate( count, rate )
	
	def getSubQTCountRewardRate( self, questID, count ):
		"""
		��ȡ���������������
		"""
		if self.has_randomQuestGroup( questID ):
			return self._questsRandomLog[questID].getRandRwdRate( count )
		return 2.0
	
	def resetSubQTCountRewardRate( self, questID ):
		"""
		���û��������������
		"""
		if self.has_randomQuestGroup( questID ):
			self._questsRandomLog[questID].resetSubQTCountRewardRate()
		
	def addCount( self, questID, count ):
		"""
		���ӵ���ѭ�����������
		@param questID:	����ID
		@type  questID: QUESTID
		@param 	count:  �������
		@type 	count:	INT
		"""
		if self.has_randomQuestGroup( questID ):
			self._questsRandomLog[questID].addCount( count )
	
	
	def getCount( self, questID ):
		"""
		ȡ�õ���ѭ�����������
		@param questID:	����ID
		@type  questID: QUESTID
		"""
		if not self._questsRandomLog.has_key( questID ):
			return 0
		return self._questsRandomLog[questID].getCount()

	def checkStartGroupTime( self, questID ):
		"""
		���������ʼʱ��
		@param questID:	����ID
		@type  questID: QUESTID
		"""
		if not questID in self._questsRandomLog.keys():
			return True
		return self._questsRandomLog[questID].checkStartTime()
	
	def resetGroupQuest( self, questID ):
		"""
		����������
		@param questID:	����ID
		@type  questID: QUESTID
		"""
		if self.has_randomQuestGroup( questID ):
			self._questsRandomLog[questID].reset()
	
	
	def addGroupQuestCount( self, questID ):
		"""
		�������������
		@param questID:	����ID
		@type  questID: QUESTID
		"""
		if self.has_randomQuestGroup( questID ):
			self._questsRandomLog[questID].incDegree()
	
	
	def isGroupQuestRecorded( self, questID ):
		"""
		�Ƿ��Ǽ�¼����������
		@param questID:	����ID
		@type  questID: QUESTID
		"""
		if self.has_randomQuestGroup( questID ):
			return self._questsRandomLog[questID].isRecordedQuest()
		return False
	
	def setGroupQuestRecorded( self, questID, isRecorded ):
		"""
		���ü�¼����������
		@param questID:	����ID
		@type  questID: QUESTID
		"""
		if self.has_randomQuestGroup( questID ):
			self._questsRandomLog[questID].setRecordedQuest( isRecorded )
	
	def resetSingleGroupQuest( self, questID ):
		"""
		���õ�������
		@param questID:	����ID
		@type  questID: QUESTID
		"""
		if self.has_randomQuestGroup( questID ):
			self._questsRandomLog[questID].resetSingle()
	
	def getGroupQuestCount( self, questID ):
		"""
		ȡ����ɶ�����
		@param questID:	����ID
		@type  questID: QUESTID
		"""
		if not self._questsRandomLog.has_key( questID ):
			return 0
		return self._questsRandomLog[questID].getDegree()
	
	def setGroupCurID( self, questID, subQuestID ):
		"""
		����������ID
		@param questID:	����ID
		@type  questID: QUESTID
		@param subQuestID:	������ID
		@type  subQuestID: QUESTID
		"""
		if self.has_randomQuestGroup( questID ):
			self._questsRandomLog[questID].setCurID( subQuestID )
	
	def queryGroupCurID( self, questID ):
		"""
		��ѯ��ǰ������ID
		@param questID:	����ID
		@type  questID: QUESTID
		"""
		return self._questsRandomLog[questID].queryCurID()
	##################################################################
	# BigWorld User Defined Type �Ľӿ�                              #
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
			if value:	# ���valueΪNone���ʾ�����д�����ֱ�Ӻ���
				obj._questsRandomLog[value.getQuestGroupID()] = value
		return obj
	
	def isSameType( self, obj ):
		"""
		"""
		return isinstance( obj, QuestRandomLogsType )
	
instance = QuestRandomLogsType()