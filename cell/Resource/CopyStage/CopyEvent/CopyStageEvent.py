# -*- coding: gb18030 -*-

# ------------------------------------------------
# from common
from bwdebug import INFO_MSG
# from cell
import Resource.CopyStageData
# ------------------------------------------------


class CopyStageEvent :
	def __init__( self ) :
		self._id			= 0				# �����¼�	�� id			csdefine �ж���
		self._indexInStage	= -1			# �� CopyStageBase �е� index�������ҵ���ʵ����
		self._stageInCopy	= -1			# ���� CopyStageBase �ڸ����е� index
		self._conditions	= []			# �����¼� 	�� ִ������		array of instances of the CopyStageCondition
		self._actions		= []			# �����¼�	�� ִ����Ϊ		array of instances of the CopyStageAction
	
	def init( self, section ) :
		"""
		<virtual method>
		@param	section :	�洢���ݵ����ݶ�
		@type	section :	PyDataSection
		"""
		if section.has_key( "condition" ) :
			for sec in section[ "condition" ].values() :
				copyStageConditions = Resource.CopyStageData.copyStageConditon_instance()
				inst = copyStageConditions[ sec["id"].asInt ]()
				inst.init( sec )
				self._conditions.append( inst )
		
		if section.has_key( "action" ) :
			for sec in section[ "action" ].values() :
				copyStageActions = Resource.CopyStageData.copyStageAction_instance()
				inst = copyStageActions[ sec["id"].asInt ]()
				inst.init( sec )
				self._actions.append( inst )
				inst.setIndexInEvent( len( self._actions )-1 )
	
	def setID( self, eventType ) :
		"""
		���ø����¼��� id
		"""
		self._id = eventType
		for action in self._actions :
			action.setEventID( eventType )
	
	def getID( self ) :
		"""
		ȡ�ø����¼��� id
		"""
		return self._id
	
	def getAction( self, indexInEvent ) :
		"""
		��ȡ action ʵ��
		"""
		return self._actions[ indexInEvent ]
	
	def setIndexInStage( self, index ) :
		"""
		�������������� CopyStageBase �е� index
		"""
		self._indexInStage = index
		for action in self._actions :
			action.setEventInStage( index )
	
	def getIndexInStage( self ) :
		"""
		ȡ������������ CopyStageBase �е� index
		"""
		return self._indexInStage
	
	def setStageInCopy( self, index ) :
		"""
		�������� CopyStageBase �ڸ����е� index
		"""
		self._stageInCopy = index
		for action in self._actions :
			action.setStageInCopy( index )
	
	def getStageInCopy( self ) :
		"""
		ȡ������ CopyStageBase �ڸ����е� index
		"""
		return self._stageInCopy
	
	def check( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	ִ�д� CopyStageEvent �� spaceEntity
		@type	spaceEntity :	�ռ� entity
		"""
		# �ж��Ƿ�������������
		for condition in self._conditions :
			result = condition.check( spaceEntity, params )
			if not result :
				return False
		
		return True
	
	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	ִ�д� CopyStageEvent �� spaceEntity
		@type	spaceEntity ��	�ռ� entity
		"""
		# ִ��������Ϊ
		copyName = spaceEntity.getScript().className
		spaceID = spaceEntity.spaceID
		stageInfo = self._stageInCopy + 1
		eventInfo = self._indexInStage + 1
		
		for action in self._actions :
			actionInfo = self._actions.index( action ) + 1
			INFO_MSG( " %s spaceId %s stage%s eventType : %s , %sst event, %sst action doAction " % ( copyName, spaceID, stageInfo, self._id, eventInfo, actionInfo ) )
			action.doAction( spaceEntity, params )
	
