# -*- coding: gb18030 -*-

# ------------------------------------------------
# from common
from bwdebug import INFO_MSG
# from cell
import Resource.CopyStageData
# ------------------------------------------------


class CopyStageEvent :
	def __init__( self ) :
		self._id			= 0				# 副本事件	的 id			csdefine 中定义
		self._indexInStage	= -1			# 在 CopyStageBase 中的 index，用于找到该实例。
		self._stageInCopy	= -1			# 所属 CopyStageBase 在副本中的 index
		self._conditions	= []			# 副本事件 	的 执行条件		array of instances of the CopyStageCondition
		self._actions		= []			# 副本事件	的 执行行为		array of instances of the CopyStageAction
	
	def init( self, section ) :
		"""
		<virtual method>
		@param	section :	存储数据的数据段
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
		设置副本事件的 id
		"""
		self._id = eventType
		for action in self._actions :
			action.setEventID( eventType )
	
	def getID( self ) :
		"""
		取得副本事件的 id
		"""
		return self._id
	
	def getAction( self, indexInEvent ) :
		"""
		获取 action 实例
		"""
		return self._actions[ indexInEvent ]
	
	def setIndexInStage( self, index ) :
		"""
		设置自身在所属 CopyStageBase 中的 index
		"""
		self._indexInStage = index
		for action in self._actions :
			action.setEventInStage( index )
	
	def getIndexInStage( self ) :
		"""
		取得自身在所属 CopyStageBase 中的 index
		"""
		return self._indexInStage
	
	def setStageInCopy( self, index ) :
		"""
		设置所属 CopyStageBase 在副本中的 index
		"""
		self._stageInCopy = index
		for action in self._actions :
			action.setStageInCopy( index )
	
	def getStageInCopy( self ) :
		"""
		取得所属 CopyStageBase 在副本中的 index
		"""
		return self._stageInCopy
	
	def check( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity :	空间 entity
		"""
		# 判断是否满足所有条件
		for condition in self._conditions :
			result = condition.check( spaceEntity, params )
			if not result :
				return False
		
		return True
	
	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		# 执行所有行为
		copyName = spaceEntity.getScript().className
		spaceID = spaceEntity.spaceID
		stageInfo = self._stageInCopy + 1
		eventInfo = self._indexInStage + 1
		
		for action in self._actions :
			actionInfo = self._actions.index( action ) + 1
			INFO_MSG( " %s spaceId %s stage%s eventType : %s , %sst event, %sst action doAction " % ( copyName, spaceID, stageInfo, self._id, eventInfo, actionInfo ) )
			action.doAction( spaceEntity, params )
	
