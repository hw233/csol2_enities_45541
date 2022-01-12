# -*- coding: gb18030 -*-

# $Id: AIAction.py,v 1.1 2008-03-25 07:43:09 kebiao Exp $

class AIAction:
	def __init__( self ):
		self._id = 0							# AIAction 的 id  int
		self._aiDataID = 0						# 调用AIAction的AIDataID  int
		self._isActivated = 1					# AIAction是否激活，默认激活

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		self._id = section["id"].asInt
		if section.has_key( "isActivated" ):
			self._isActivated = section["isActivated"].asInt
	
	def getID( self ):
		"""
		取得AIAction id
		"""
		return self._id
		
	def getIsActivated( self ):
		"""
		取得AIAction id
		"""
		return self._isActivated
		
	def setAIDataID( self, aid ):
		"""
		设置调用该AIAction 的AIDataID
		"""
		self._aiDataID = aid
	
	def getAIDataID( self ):
		"""
		取得调用它的AIData的id
		"""
		return self._aiDataID

	def do( self, ai, entity ):
		"""
		vitural method
		@param	ai		: 	拥有此条件的AI ( 做此支持是为了得到或写AI的动态数据 )
		@type	ai		:	AI of instance, AIBase
		@param	entity	: 	执行此AICondition的entity
		@type	entity	:	entity
		"""
		pass

#
# $Log: not supported by cvs2svn $
#