# -*- coding: gb18030 -*-

# ------------------------------------------------
# from python
import copy
# ------------------------------------------------
# from common
from Function import Functor

# ------------------------------------------------

class CopyStageAction :
	def __init__( self ) :
		self._id			= 0			# CopyStageAction �� id						int
		self._name			= ""
		self._delayTime 	= 0			# �ӳٵ��ø���Ϊ��ʱ�䣬Ϊ 0 ��ʾ���ӳ٣�ֱ�ӵ��á�
		
		self._eventID		= 0			# ���� CopyStageAction �� CopyStageEvent �� id	int
		self._indexInEvent	= -1		# �� CopyStageEvent �е� index�������ҵ�����Ϊʵ����
		self._eventInStage	= -1		# ���� CopyStageEvent ʵ���� CopyStageBase �е� index�������ҵ����� CopyStageEvent ʵ����
		self._stageInCopy	= -1		# ���� CopyStageBase ʵ���� CopyTemplate �е� index�������ҵ����� CopyStageBase ʵ����
	
	def init( self, section ) :
		"""
		<virtual method>
		@param	section :	�洢���ݵ����ݶ�
		@type	section :	PyDataSection
		"""
		self._id 		= section["id"].asInt
		self._delayTime = section.readInt("delayTime")
	
	def getID( self ) :
		"""
		ȡ�� CopyStageAction �� id
		"""
		return self._id
	
	def setEventID( self, eid ) :
		"""
		���õ��� CopyStageAction �� CopyStageEvent �� id
		"""
		self._eventID = eid
	
	def getEventID( self ) :
		"""
		ȡ�õ��� CopyStageAction �� CopyStageEvent �� id
		"""
		return self._eventID
	
	def setIndexInEvent( self, index ) :
		"""
		���ø���Ϊʵ���� CopyStageEvent �е� index
		"""
		self._indexInEvent = index
	
	def getIndexInEvent( self ) :
		"""
		ȡ�ø���Ϊʵ���� CopyStageEvent �е� index
		"""
		return self._indexInEvent
	
	def setEventInStage( self, index ) :
		"""
		���ø���Ϊ���� CopyStageEvent ʵ���� CopyStageBase �е� index
		"""
		self._eventInStage = index
	
	def getEventInStage( self ) :
		"""
		ȡ�ø���Ϊ���� CopyStageEvent ʵ���� CopyStageBase �е� index
		"""
		return self._eventInStage
	
	def setStageInCopy( self, index ) :
		"""
		�������� CopyStageBase ʵ���ڸ����е� index
		"""
		self._stageInCopy = index
	
	def getStageInCopy( self ) :
		"""
		ȡ������ CopyStageBase ʵ���ڸ����е� index
		"""
		return self._stageInCopy
	
	def doAction( self, spaceEntity, params ) :
		"""
		@param	spaceEntity :	ִ�д� CopyStageEvent �� spaceEntity
		@type	spaceEntity ��	�ռ� entity
		@param	params		:	�����¼��Ķ������ �� ����֧����Ϊ�˵õ������¼��Ķ�̬���� ��
		@type	params		 :	PY_DICT
		"""
		newParams = copy.deepcopy( params )
		if self._delayTime > 0 :
			newParams[ "eventType" ] = self._eventID
			newParams[ "eventInStage" ] = self._eventInStage
			newParams[ "actionInEvent" ] = self._indexInEvent
			newParams[ "stageInCopy" ] = self._stageInCopy
			spaceEntity.addUserTimer( self._delayTime, 0, 0, newParams )
		else :
			self.do( spaceEntity, newParams )
	
	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	ִ�д� CopyStageEvent �� spaceEntity
		@type	spaceEntity ��	�ռ� entity
		@param	params		:	�����¼��Ķ������ �� ����֧����Ϊ�˵õ������¼��Ķ�̬���� ��
		@type	params		 :	PY_DICT
		"""
		pass

