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
	���������
	"""
	def __init__( self, taskType = 0 ):
		self._type = taskType				# �����������

	def setType( self, type ):
		self._type = type

	def getType( self ):
		return self._type

	def do( self, refEntity, targetEntity, isLastTask ):
		"""
		virtual method.
		ִ����Ӧ������
		@param refEntity 	: �ο�entity�� ͨ����player
		@param targetEntity : ���ο�entity
		"""
		targetEntity.cell.requestEntityData( refEntity.id, self.getType(), isLastTask )
		return True


# ע������ ( ��ͨ����ʹ��ECTask������, ���������������Ӧ����дһ����)
REGISTER_ENTITY_CACHE_TASK( ECTask( csdefine.ENTITY_CACHE_TASK_TYPE_MONSTER0 ) )
REGISTER_ENTITY_CACHE_TASK( ECTask( csdefine.ENTITY_CACHE_TASK_TYPE_NPCOBJECT0 ) )
REGISTER_ENTITY_CACHE_TASK( ECTask( csdefine.ENTITY_CACHE_TASK_TYPE_NPCOBJECT1 ) )
REGISTER_ENTITY_CACHE_TASK( ECTask( csdefine.ENTITY_CACHE_TASK_TYPE_COMBATUNIT0 ) )
REGISTER_ENTITY_CACHE_TASK( ECTask( csdefine.ENTITY_CACHE_TASK_TYPE_PET0 ) )
# EntityCache.py
