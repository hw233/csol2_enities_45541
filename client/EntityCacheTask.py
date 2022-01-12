# -*- coding: gb18030 -*-
#
# $Id: Monster.py,v 1.99 2009-07-14 02:38:42 kebiao Exp $
"""
"""

import BigWorld
import csdefine
from bwdebug import *
import EntityCache

g_entityCache = EntityCache.EntityCache.instance()
REGISTER_ENTITY_CACHE_TASK = g_entityCache.registerTask

class ECTask:
	"""
	任务基础类
	"""
	def __init__( self, taskType = 0 ):
		self._type = taskType				# 这个任务的类别

	def setType( self, type ):
		self._type = type

	def getType( self ):
		return self._type

	def do( self, refEntity, targetEntity, isLastTask ):
		"""
		virtual method.
		执行相应的任务
		@param refEntity 	: 参考entity， 通常是player
		@param targetEntity : 被参考entity
		"""
		targetEntity.cell.requestEntityData( refEntity.id, self.getType(), isLastTask )
		return True


# 注册任务 ( 普通任务使用ECTask就行了, 有特殊操作的任务应该重写一个类)
REGISTER_ENTITY_CACHE_TASK( ECTask( csdefine.ENTITY_CACHE_TASK_TYPE_MONSTER0 ) )
REGISTER_ENTITY_CACHE_TASK( ECTask( csdefine.ENTITY_CACHE_TASK_TYPE_NPCOBJECT0 ) )
REGISTER_ENTITY_CACHE_TASK( ECTask( csdefine.ENTITY_CACHE_TASK_TYPE_NPCOBJECT1 ) )
REGISTER_ENTITY_CACHE_TASK( ECTask( csdefine.ENTITY_CACHE_TASK_TYPE_COMBATUNIT0 ) )
REGISTER_ENTITY_CACHE_TASK( ECTask( csdefine.ENTITY_CACHE_TASK_TYPE_PET0 ) )
# EntityCache.py
