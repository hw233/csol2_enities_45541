# -*- coding: gb18030 -*-


class CopyStageCondition :
	def __init__( self ) :
		self._id		= 0				# CopyStageCondition 的 id						int
		self._eventID	= 0				# 调用 CopyStageCondition 的 CopyStageEvent 的 id	int
	
	def init( self, section ) :
		"""
		<virtual method>
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		self._id = section["id"].asInt
	
	def getID( self ) :
		"""
		取得 CopyStageCondition 的 id
		"""
		return self._id
	
	def setEventID( self, eid ) :
		"""
		设置调用 CopyStageCondition 的 CopyStageEvent 的 id
		"""
		self._eventID = eid
	
	def getEventID( self ) :
		"""
		取得调用 CopyStageCondition 的 CopyStageEvent 的 id
		"""
		return self._eventID
	
	def check( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		return True
