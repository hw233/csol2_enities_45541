# -*- coding: gb18030 -*-

# ------------------------------------------------
# from engine
import BigWorld
# ------------------------------------------------
# from common
import csdefine
import csstatus
from bwdebug import INFO_MSG
# ------------------------------------------------
# from cell
import Const
import Resource.CopyStageData
import Resource.CopyStage.CopyEvent.CopyStageEvent as CopyStageEvent

# ------------------------------------------------

NEXT_STAGE			= 999				#下一个内容的timerArg

WAIT 					= 10				#等待一会刷怪
END_WAIT 				= 60				#1分钟后离开场景

"""
类 CopyStageBase， 描述的是副本的一项内容。

这里把副本组成分成多项内容。

这些内容，按照顺序一个个的执行，则副本完成。

"""
class CopyStageBase :
	def __init__( self ) :
		self._events		= {}			# { eventType : [ CopyStageEvent, ] }
		self._indexInCopy	= -1			# 在副本中的索引，用于找到该 CopyStageBase 实例
	
	def init( self, section ) :
		"""
		<virtual method>
		@param	section :	存储数据的数据段
		@type	section :	PyDataSection
		"""
		for sec in section.values() :
			eventType = sec[ "type" ].asInt
			
			for childSec in sec[ "items" ].values() :
				stageEvent = CopyStageEvent.CopyStageEvent()
				stageEvent.init( childSec )
				stageEvent.setID( eventType )
				self.addEvent( eventType, stageEvent )
	
	def setIndexInCopy( self, index ) :
		"""
		设置自身在所属副本中的 index
		"""
		self._indexInCopy = index
		for copyStageEvents in self._events.itervalues() :
			for copyStageEvent in copyStageEvents :
				copyStageEvent.setStageInCopy( index )
	
	def getIndexInCopy( self ) :
		"""
		取得自身在所属副本中的 index
		"""
		return self._indexInCopy
	
	def beginStage( self, spaceEntity ) :
		"""
		内容开始
		<virtual method>
		@param	spaceEntity :	执行此 CopyStage 的 spaceEntity
		@type	spaceEntity :	空间 entity
		"""
		copyName = spaceEntity.getScript().className
		stageIndex = spaceEntity.getScript().getCurrentStageIndex( spaceEntity )
		INFO_MSG( " %s spaceID %s stage%s beginStage " % ( copyName, spaceEntity.spaceID, stageIndex+1 ) )
		self.doAllEvent( spaceEntity, csdefine.COPY_EVENT_ON_BEGIN_STAGE, {} )
	
	def eventCommonCheck( self, spaceEntity, event, params ) :
		"""
		条件判断
		"""
		if spaceEntity.isDestroyed or not spaceEntity.isReal() or not event.check( spaceEntity, params ) :
			return False
		return True
	
	def addEvent( self, eventType, event ) :
		"""
		添加一个 CopyStageEvent
		"""
		if eventType in self._events :
			self._events[ eventType ].append( event )
			event.setIndexInStage( len( self._events[ eventType ] ) -1 )
		else :
			self._events[ eventType ] = [ event ]
			event.setIndexInStage( 0 )
	
	def getEvent( self, eventType, indexInStage ) :
		"""
		获取 CopyStageEvent 实例
		"""
		return self._events[ eventType ][ indexInStage ]
	
	def doAllEvent( self, spaceEntity, eventType, params ) :
		"""
		处理该 stage 上的所有事件类型为 eventType 的事件
		"""
		copyName = spaceEntity.getScript().className
		stageIndex = spaceEntity.getScript().getCurrentStageIndex( spaceEntity )
		
		if self._events.has_key( eventType ) :
			INFO_MSG( " %s spaceId %s stage%s doAllEvent [ eventType : %s ] " % ( copyName, spaceEntity.spaceID, stageIndex+1, eventType ) )
			index = 0
			for event in self._events[ eventType ] :
				index += 1
				if self.eventCommonCheck( spaceEntity, event, params ) :
					INFO_MSG( " %s spaceId %s stage%s doAllEvent, eventType : %s ,the %sst event do " % ( copyName, spaceEntity.spaceID, stageIndex+1, eventType, index ) )
					event.do( spaceEntity, params )
	
	def endStage( self, spaceEntity ) :
		"""
		内容结束
		"""
		copyName = spaceEntity.getScript().className
		stageIndex = spaceEntity.getScript().getCurrentStageIndex( spaceEntity )
		INFO_MSG( " %s spaceId %s stage%s endStage " % ( copyName, spaceEntity.spaceID, stageIndex+1 ) )
		spaceEntity.getScript().doNextStage( spaceEntity )

