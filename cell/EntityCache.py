# -*- coding: gb18030 -*-
#
# $Id: Monster.py,v 1.99 2009-07-14 02:38:42 kebiao Exp $
"""
"""

import BigWorld
from bwdebug import *

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
		return self._tasks.get( taskType, None )
		
# EntityCache.py
