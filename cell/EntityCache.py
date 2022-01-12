# -*- coding: gb18030 -*-
#
# $Id: Monster.py,v 1.99 2009-07-14 02:38:42 kebiao Exp $
"""
"""

import BigWorld
from bwdebug import *

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
		return self._tasks.get( taskType, None )
		
# EntityCache.py
