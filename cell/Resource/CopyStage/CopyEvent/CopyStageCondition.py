# -*- coding: gb18030 -*-


class CopyStageCondition :
	def __init__( self ) :
		self._id		= 0				# CopyStageCondition �� id						int
		self._eventID	= 0				# ���� CopyStageCondition �� CopyStageEvent �� id	int
	
	def init( self, section ) :
		"""
		<virtual method>
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		self._id = section["id"].asInt
	
	def getID( self ) :
		"""
		ȡ�� CopyStageCondition �� id
		"""
		return self._id
	
	def setEventID( self, eid ) :
		"""
		���õ��� CopyStageCondition �� CopyStageEvent �� id
		"""
		self._eventID = eid
	
	def getEventID( self ) :
		"""
		ȡ�õ��� CopyStageCondition �� CopyStageEvent �� id
		"""
		return self._eventID
	
	def check( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	ִ�д� CopyStageEvent �� spaceEntity
		@type	spaceEntity ��	�ռ� entity
		@param	params		:	�����¼��Ķ������ �� ����֧����Ϊ�˵õ������¼��Ķ�̬���� ��
		@type	params		 :	PY_DICT
		"""
		return True
