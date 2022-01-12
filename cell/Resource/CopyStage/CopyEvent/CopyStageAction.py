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
		self._id			= 0			# CopyStageAction 的 id						int
		self._name			= ""
		self._delayTime 	= 0			# 延迟调用该行为的时间，为 0 表示不延迟，直接调用。
		
		self._eventID		= 0			# 调用 CopyStageAction 的 CopyStageEvent 的 id	int
		self._indexInEvent	= -1		# 在 CopyStageEvent 中的 index，用于找到该行为实例。
		self._eventInStage	= -1		# 所属 CopyStageEvent 实例在 CopyStageBase 中的 index，用于找到所属 CopyStageEvent 实例。
		self._stageInCopy	= -1		# 所属 CopyStageBase 实例在 CopyTemplate 中的 index，用于找到所属 CopyStageBase 实例。
	
	def init( self, section ) :
		"""
		<virtual method>
		@param	section :	存储数据的数据段
		@type	section :	PyDataSection
		"""
		self._id 		= section["id"].asInt
		self._delayTime = section.readInt("delayTime")
	
	def getID( self ) :
		"""
		取得 CopyStageAction 的 id
		"""
		return self._id
	
	def setEventID( self, eid ) :
		"""
		设置调用 CopyStageAction 的 CopyStageEvent 的 id
		"""
		self._eventID = eid
	
	def getEventID( self ) :
		"""
		取得调用 CopyStageAction 的 CopyStageEvent 的 id
		"""
		return self._eventID
	
	def setIndexInEvent( self, index ) :
		"""
		设置该行为实例在 CopyStageEvent 中的 index
		"""
		self._indexInEvent = index
	
	def getIndexInEvent( self ) :
		"""
		取得该行为实例在 CopyStageEvent 中的 index
		"""
		return self._indexInEvent
	
	def setEventInStage( self, index ) :
		"""
		设置该行为所属 CopyStageEvent 实例在 CopyStageBase 中的 index
		"""
		self._eventInStage = index
	
	def getEventInStage( self ) :
		"""
		取得该行为所属 CopyStageEvent 实例在 CopyStageBase 中的 index
		"""
		return self._eventInStage
	
	def setStageInCopy( self, index ) :
		"""
		设置所属 CopyStageBase 实例在副本中的 index
		"""
		self._stageInCopy = index
	
	def getStageInCopy( self ) :
		"""
		取得所属 CopyStageBase 实例在副本中的 index
		"""
		return self._stageInCopy
	
	def doAction( self, spaceEntity, params ) :
		"""
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
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
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		pass

