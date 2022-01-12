# -*- coding: gb18030 -*-

# $Id: AIAction.py,v 1.1 2008-03-25 07:43:09 kebiao Exp $

class AIAction:
	def __init__( self ):
		self._id = 0							# AIAction �� id  int
		self._aiDataID = 0						# ����AIAction��AIDataID  int
		self._isActivated = 1					# AIAction�Ƿ񼤻Ĭ�ϼ���

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		self._id = section["id"].asInt
		if section.has_key( "isActivated" ):
			self._isActivated = section["isActivated"].asInt
	
	def getID( self ):
		"""
		ȡ��AIAction id
		"""
		return self._id
		
	def getIsActivated( self ):
		"""
		ȡ��AIAction id
		"""
		return self._isActivated
		
	def setAIDataID( self, aid ):
		"""
		���õ��ø�AIAction ��AIDataID
		"""
		self._aiDataID = aid
	
	def getAIDataID( self ):
		"""
		ȡ�õ�������AIData��id
		"""
		return self._aiDataID

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	ӵ�д�������AI ( ����֧����Ϊ�˵õ���дAI�Ķ�̬���� )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	ִ�д�AICondition��entity
		@type	entity	:	entity
		"""
		pass

#
# $Log: not supported by cvs2svn $
#