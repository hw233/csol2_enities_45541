# -*- coding: gb18030 -*-
#
# $Id: EntityCache.py,v 1.99 2009-07-14 02:38:42 kebiao Exp $
"""
"""
import time
import BigWorld
import csdefine
from bwdebug import *

ENTITY_CACHE_TICK = 0.1

# entity ���ȼ��� �� EntityCacheLOD._entityIDs���Ӧ
ENTITY_CACHE_PRIORITY_MAP = {
	csdefine.ENTITY_TYPE_NPC			: 0,
	csdefine.ENTITY_TYPE_MONSTER		: 1,
	csdefine.ENTITY_TYPE_PET			: 2,
	csdefine.ENTITY_TYPE_ROLE			: 3,
}

def onCacheCompleted( entity ):
	"""
	�������������
	@param entity	: ����enterworld��entity
	"""
	BigWorld.callback( 0.05, entity.onCacheCompleted )

class EntityCacheLOD:
	"""
	entity����lod����, 1���������self._entity��һ����
	���ǿ��Ը��ݲ�ͬ�Ļ���������������������ͬ�Ĵ���.
	"""
	def __init__( self, area ):
		self._area = area

	def getArea( self ):
		"""
		��ȡ��lod������ķ�Χ
		"""
		return self._area

	def inside( self, distance ):
		"""
		�Ƿ������lod����
		@param distance	: ��������� ��ͨ���������Ŀ��entity��һ�����룩
		"""
		return distance >= self._area[ 0 ] and  distance <= self._area[ 1 ]

class EntityCache:
	"""
	entity������: �ڴ���entity enterworldʱ�� ����ȫ��������뻺�����洢��
	�����������ȡ��entity��������ݣ� ֱ��entity���ݻ�ȡ��Ϻ����ǲ���
	���������ڿͻ��˳�ʼ�������ӻ������Ƴ���
	"""
	_instance = None
	def __init__( self ):
		assert EntityCache._instance is None
		EntityCache._instance = self
		self._tasks = {}
		self.currHandleEntityID = 0
		self.urgentEntityList = []		# �ȽϽ�����Ҫ����ĵ�entity�����������������_entityIDs���м���

		# ������Ե��б�˳���൱��һ�����ȼ��� ��0~N�� 0Ϊ���ȼ���ߵ�һ�� ��ָ�����ȼ���entity��Ҫ
		# ��ENTITY_CACHE_PRIORITY_MAP�ж������ȼ�˳��
		self._entityIDs = [
							[],	# ��һλ��� npc
							[], # ��һλ��� monster
							[], # ��һλ��� pet
							[], # ��һλ��� role
							[], # ��һλ��� ��������
						]

		# ���ɲ�ͬ����λ�õ�lodȥ����ͬλ�õ�entity�����ݻ�ȡ���ȼ�
		self.lods = []
		distances = [ 0, 20.0, 40.0, 60.0, 10000.0 ]
		lvs = len( distances )
  		for i in xrange( 0, lvs - 1 ):
  	 	 	self.lods.append( EntityCacheLOD( ( distances[ i ], distances[ i + 1 ] ) ) )

		# ��ʼ��������tick
		EntityCacheTickStart()

	@staticmethod
	def instance():
		"""
		��ʵ����ȡģʽ
		"""
		if EntityCache._instance is None:
			EntityCache._instance = EntityCache()
		return EntityCache._instance

	def registerTask( self, task ):
		"""
		ע������
		@param task : �����ʵ��ECTask
		"""
		self._tasks[ task.getType() ] = task

	def getTask( self, taskType ):
		"""
		��ȡ����
		@param task : ��������ECTask._type
		"""
		return self._tasks[ taskType ]

	def hasEntity( self, entityID ):
		"""
		�жϻ������Ƿ���ĳ��entity
		@param entityID	: entity��ID
		"""
		for eidlist in self._entityIDs:
			if entityID in eidlist:
				return True
		return entityID in self.urgentEntityList

	def addUrgent( self, entity ):
		"""
		���һ�����������entity
		"""
		tasks = entity.getCacheTasks()
		DEBUG_MSG( "[%s]addUrgent id %i. currHandleEntityID = %d, entity isCacheOver = %s, tasks = %s" % ( entity, entity.id, self.currHandleEntityID, \
					entity.isCacheOver, tasks ) )

		# ������entity�Ѿ���������ˣ���ô���϶�������������
		self.remove( entity.id )
		if entity.isCacheOver:
			return

		if len( tasks ) <= 0:
			onCacheCompleted( entity )
			return

		self.urgentEntityList.append( entity.id )

	def insert( self, entity ):
		"""
		����һ��enterworld��entity��������
		@param entity	: ����enterworld��entity
		"""
		#DEBUG_MSG( "insert id %i." % entity.id )
		assert( not entity.isCacheOver, "entity is CacheOver!" )

		entity.initCacheTasks()
		tasks = entity.getCacheTasks()

		if len( tasks ) <= 0:
			onCacheCompleted( entity )
			return

		index = -1		# -1 ��list�б�ʾ���һ��λ�ã� ����Ĭ���������һ�����ȼ���
		type = entity.getEntityType()

		# �ж�entity�����ͣ� ����ȡ���ȼ�
		if type in ENTITY_CACHE_PRIORITY_MAP:
			index = ENTITY_CACHE_PRIORITY_MAP[ type ]

		# ���뵽��Ӧ�����ȼ����������
		self._entityIDs[ index ].append( entity.id )

	def remove( self, entityID ):
		"""
		ɾ�������entity
		@param entityID	: entity��ID
		"""
		#DEBUG_MSG( "remove id %i." % entityID )

		# �������������Ķ���ΪҪɾ����entity���������
		if self.currHandleEntityID == entityID:
			self.currHandleEntityID = 0

		for eidList in self._entityIDs:
			if entityID in eidList:
				eidList.remove( entityID )
				return

		# �����Ƿ������ȶ�����
		if entityID in self.urgentEntityList:
			self.urgentEntityList.remove( entityID )

	def processCacheTask( self, player, entity ):
		"""
		����entity������
		"""
		tasks = entity.getCacheTasks()

		try:
			task = tasks[ 0 ]
		except Exception, errstr :
			ERROR_MSG( "[%s]%s, entity:%d, isCacheOver:%s, currHandleEntityID:%d" % ( entity, errstr, entity.id, \
					entity.isCacheOver, self.currHandleEntityID ) )

		# ��������Ƿ���Ч�� ��Ч��ɾ��
		if task.do( player, entity, len( tasks ) <= 1 ):
			tasks.pop( 0 )
			if len( tasks ) <= 0:
				return False

		return True

	def onSelectHandleEntity( self, player ):
		"""
		ѡ��һ�������entity
		"""
		# �ȼ���Ƿ��н���������Ҫ����
		if len( self.urgentEntityList ) > 0:
			self.currHandleEntityID = self.urgentEntityList[ 0 ]
		else:
			for eidList in self._entityIDs:
				rmb = []
				for lod in self.lods:
					for eid in eidList:
						entity = BigWorld.entities.get( eid, None )
						if entity is None:
							rmb.append( eid )
						else:
							distance = player.position.distTo( entity.position )
							if lod.inside( distance ):
								self.currHandleEntityID = eid
								return

				if len( rmb ) > 0:
					#DEBUG_MSG( "remove id %s." % ( rmb ) )
					for r in rmb:
						eidList.remove( r )

	def do( self ):
		"""
		ִ��һ�������lod���� ���������������񶼴�����ϲſ�ʼ������һ������
		"""
		player = BigWorld.player()

		# ����Ƿ��б�ѡ�������δ������ɵ�entity, ���û�о�����ѡ��һ������������ֱ�Ӵ�����ʣ�µ�����
		if self.currHandleEntityID <= 0:
			self.onSelectHandleEntity( player )
			if self.currHandleEntityID <= 0:
				return

		entity = BigWorld.entities.get( self.currHandleEntityID, None )
		if entity:
			if not self.processCacheTask( player, entity ):
				self.remove( entity.id )
		else:
			self.remove( self.currHandleEntityID )

"""
������tick����
"""
def EntityCacheTickStart():
	"""
	tick Ƶ��
	"""
	try:
		EntityCache.instance().do()
	except:
		ERROR_MSG( "unknown error!" )

	BigWorld.callback( ENTITY_CACHE_TICK, EntityCacheTickStart )

# EntityCache.py
