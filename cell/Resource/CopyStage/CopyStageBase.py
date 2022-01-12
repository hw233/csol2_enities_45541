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

NEXT_STAGE			= 999				#��һ�����ݵ�timerArg

WAIT 					= 10				#�ȴ�һ��ˢ��
END_WAIT 				= 60				#1���Ӻ��뿪����

"""
�� CopyStageBase�� �������Ǹ�����һ�����ݡ�

����Ѹ�����ɷֳɶ������ݡ�

��Щ���ݣ�����˳��һ������ִ�У��򸱱���ɡ�

"""
class CopyStageBase :
	def __init__( self ) :
		self._events		= {}			# { eventType : [ CopyStageEvent, ] }
		self._indexInCopy	= -1			# �ڸ����е������������ҵ��� CopyStageBase ʵ��
	
	def init( self, section ) :
		"""
		<virtual method>
		@param	section :	�洢���ݵ����ݶ�
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
		�������������������е� index
		"""
		self._indexInCopy = index
		for copyStageEvents in self._events.itervalues() :
			for copyStageEvent in copyStageEvents :
				copyStageEvent.setStageInCopy( index )
	
	def getIndexInCopy( self ) :
		"""
		ȡ�����������������е� index
		"""
		return self._indexInCopy
	
	def beginStage( self, spaceEntity ) :
		"""
		���ݿ�ʼ
		<virtual method>
		@param	spaceEntity :	ִ�д� CopyStage �� spaceEntity
		@type	spaceEntity :	�ռ� entity
		"""
		copyName = spaceEntity.getScript().className
		stageIndex = spaceEntity.getScript().getCurrentStageIndex( spaceEntity )
		INFO_MSG( " %s spaceID %s stage%s beginStage " % ( copyName, spaceEntity.spaceID, stageIndex+1 ) )
		self.doAllEvent( spaceEntity, csdefine.COPY_EVENT_ON_BEGIN_STAGE, {} )
	
	def eventCommonCheck( self, spaceEntity, event, params ) :
		"""
		�����ж�
		"""
		if spaceEntity.isDestroyed or not spaceEntity.isReal() or not event.check( spaceEntity, params ) :
			return False
		return True
	
	def addEvent( self, eventType, event ) :
		"""
		���һ�� CopyStageEvent
		"""
		if eventType in self._events :
			self._events[ eventType ].append( event )
			event.setIndexInStage( len( self._events[ eventType ] ) -1 )
		else :
			self._events[ eventType ] = [ event ]
			event.setIndexInStage( 0 )
	
	def getEvent( self, eventType, indexInStage ) :
		"""
		��ȡ CopyStageEvent ʵ��
		"""
		return self._events[ eventType ][ indexInStage ]
	
	def doAllEvent( self, spaceEntity, eventType, params ) :
		"""
		����� stage �ϵ������¼�����Ϊ eventType ���¼�
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
		���ݽ���
		"""
		copyName = spaceEntity.getScript().className
		stageIndex = spaceEntity.getScript().getCurrentStageIndex( spaceEntity )
		INFO_MSG( " %s spaceId %s stage%s endStage " % ( copyName, spaceEntity.spaceID, stageIndex+1 ) )
		spaceEntity.getScript().doNextStage( spaceEntity )

