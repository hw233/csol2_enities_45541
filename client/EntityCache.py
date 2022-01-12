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

# entity 优先级表 与 EntityCacheLOD._entityIDs相对应
ENTITY_CACHE_PRIORITY_MAP = {
	csdefine.ENTITY_TYPE_NPC			: 0,
	csdefine.ENTITY_TYPE_MONSTER		: 1,
	csdefine.ENTITY_TYPE_PET			: 2,
	csdefine.ENTITY_TYPE_ROLE			: 3,
}

def onCacheCompleted( entity ):
	"""
	缓冲器处理完毕
	@param entity	: 进入enterworld的entity
	"""
	BigWorld.callback( 0.05, entity.onCacheCompleted )

class EntityCacheLOD:
	"""
	entity缓冲lod级别, 1级别处于最靠近self._entity的一环。
	我们可以根据不同的环的特性做出与其他环不同的处理.
	"""
	def __init__( self, area ):
		self._area = area

	def getArea( self ):
		"""
		获取本lod所代表的范围
		"""
		return self._area

	def inside( self, distance ):
		"""
		是否处于这个lod环中
		@param distance	: 距离参数， （通常是玩家与目标entity的一个距离）
		"""
		return distance >= self._area[ 0 ] and  distance <= self._area[ 1 ]

class EntityCache:
	"""
	entity缓冲器: 在大量entity enterworld时， 我们全部将其放入缓冲器存储，
	并向服务器获取该entity的相关数据， 直到entity数据获取完毕后我们才让
	其真正的在客户端初始化，并从缓冲器移除。
	"""
	_instance = None
	def __init__( self ):
		assert EntityCache._instance is None
		EntityCache._instance = self
		self._tasks = {}
		self.currHandleEntityID = 0
		self.urgentEntityList = []		# 比较紧急需要处理的的entity放置于这里。它优先于_entityIDs所有级别

		# 这个属性的列表顺序相当于一个优先级， 从0~N， 0为优先级最高的一级 被指明优先级的entity需要
		# 在ENTITY_CACHE_PRIORITY_MAP中定义优先级顺序
		self._entityIDs = [
							[],	# 这一位存放 npc
							[], # 这一位存放 monster
							[], # 这一位存放 pet
							[], # 这一位存放 role
							[], # 这一位存放 其他所有
						]

		# 生成不同区段位置的lod去处理不同位置的entity的数据获取优先级
		self.lods = []
		distances = [ 0, 20.0, 40.0, 60.0, 10000.0 ]
		lvs = len( distances )
  		for i in xrange( 0, lvs - 1 ):
  	 	 	self.lods.append( EntityCacheLOD( ( distances[ i ], distances[ i + 1 ] ) ) )

		# 开始缓冲器的tick
		EntityCacheTickStart()

	@staticmethod
	def instance():
		"""
		单实例获取模式
		"""
		if EntityCache._instance is None:
			EntityCache._instance = EntityCache()
		return EntityCache._instance

	def registerTask( self, task ):
		"""
		注册任务
		@param task : 任务的实例ECTask
		"""
		self._tasks[ task.getType() ] = task

	def getTask( self, taskType ):
		"""
		获取任务
		@param task : 任务的类别ECTask._type
		"""
		return self._tasks[ taskType ]

	def hasEntity( self, entityID ):
		"""
		判断缓冲器是否有某个entity
		@param entityID	: entity的ID
		"""
		for eidlist in self._entityIDs:
			if entityID in eidlist:
				return True
		return entityID in self.urgentEntityList

	def addUrgent( self, entity ):
		"""
		添加一个紧急处理的entity
		"""
		tasks = entity.getCacheTasks()
		DEBUG_MSG( "[%s]addUrgent id %i. currHandleEntityID = %d, entity isCacheOver = %s, tasks = %s" % ( entity, entity.id, self.currHandleEntityID, \
					entity.isCacheOver, tasks ) )

		# 如果这个entity已经处理完毕了，那么它肯定不在其他表中
		self.remove( entity.id )
		if entity.isCacheOver:
			return

		if len( tasks ) <= 0:
			onCacheCompleted( entity )
			return

		self.urgentEntityList.append( entity.id )

	def insert( self, entity ):
		"""
		插入一个enterworld的entity到缓冲器
		@param entity	: 进入enterworld的entity
		"""
		#DEBUG_MSG( "insert id %i." % entity.id )
		assert( not entity.isCacheOver, "entity is CacheOver!" )

		entity.initCacheTasks()
		tasks = entity.getCacheTasks()

		if len( tasks ) <= 0:
			onCacheCompleted( entity )
			return

		index = -1		# -1 在list中表示最后一个位置， 我们默认他是最后一个优先级别
		type = entity.getEntityType()

		# 判断entity的类型， 并获取优先级
		if type in ENTITY_CACHE_PRIORITY_MAP:
			index = ENTITY_CACHE_PRIORITY_MAP[ type ]

		# 加入到相应的优先级处理队列中
		self._entityIDs[ index ].append( entity.id )

	def remove( self, entityID ):
		"""
		删除掉这个entity
		@param entityID	: entity的ID
		"""
		#DEBUG_MSG( "remove id %i." % entityID )

		# 如果被锁定处理的对象为要删除的entity则擦除锁定
		if self.currHandleEntityID == entityID:
			self.currHandleEntityID = 0

		for eidList in self._entityIDs:
			if entityID in eidList:
				eidList.remove( entityID )
				return

		# 看看是否在优先队列里
		if entityID in self.urgentEntityList:
			self.urgentEntityList.remove( entityID )

	def processCacheTask( self, player, entity ):
		"""
		处理entity的任务
		"""
		tasks = entity.getCacheTasks()

		try:
			task = tasks[ 0 ]
		except Exception, errstr :
			ERROR_MSG( "[%s]%s, entity:%d, isCacheOver:%s, currHandleEntityID:%d" % ( entity, errstr, entity.id, \
					entity.isCacheOver, self.currHandleEntityID ) )

		# 检查任务是否还有效， 无效则删除
		if task.do( player, entity, len( tasks ) <= 1 ):
			tasks.pop( 0 )
			if len( tasks ) <= 0:
				return False

		return True

	def onSelectHandleEntity( self, player ):
		"""
		选择一个处理的entity
		"""
		# 先检查是否有紧急任务需要处理
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
		执行一个最近的lod级别， 当这个级别类的任务都处理完毕才开始处理下一个级别。
		"""
		player = BigWorld.player()

		# 检查是否有被选择处理而还未处理完成的entity, 如果没有就重新选择一个出来，否则直接处理它剩下的任务
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
缓冲器tick触发
"""
def EntityCacheTickStart():
	"""
	tick 频率
	"""
	try:
		EntityCache.instance().do()
	except:
		ERROR_MSG( "unknown error!" )

	BigWorld.callback( ENTITY_CACHE_TICK, EntityCacheTickStart )

# EntityCache.py
