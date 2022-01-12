# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
import csdefine
import csconst
import Const
from interface.GameObject import GameObject
from ObjectScripts.GameObjectFactory import g_objFactory
import random
from SpawnPoint import SpawnPoint

class SpawnPointControl( SpawnPoint ):
	"""
	���ˢ�µ�������3�����ܣ�1.�ֿɿ��Ʋ�ͣ��ˢ�£�2.���ˢ�µ�Ĺ������󣬿��Ըı�����ˢ��ʱ�䣻3.��AI����������ˢ��
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPoint.initEntity( self, selfEntity  )
		selfEntity.getCurrentSpaceBase().addSpawnPointControl( selfEntity.base )
		
	def entityDead( self, selfEntity ):
		"""
		"""
		# С��0�򲻸���
		if selfEntity.rediviousTime < 0:
			return
		
		elif self.PlotMonsterType == 1:		# �ر����õ�ֵΪ1ʱ����Ҫͨ������������ˢ��
			return
		
		elif not selfEntity.rediviousTimer:					# ���������̣����������󰴵ر�����ʱ��ˢ��
			selfEntity.currentRedivious += 1
			selfEntity.rediviousTimer = selfEntity.addTimer( selfEntity.rediviousTime, 0, Const.SPAWN_ON_MONSTER_DIED )
			return
		
	def createEntity( self, selfEntity, params = {} ):
		"""
		define method
		"""
		SpawnPoint.createEntity( self, selfEntity, params )
		
		if self.PlotMonsterType == 1:
			# ˢ�������ɲ߻����ã�ֵΪ1ʱ���۹���������񣬶��᲻ͣ��ˢ��
			selfEntity.addTimer( self.PlotRediviousTime, 0.0, Const.SPAWN_ON_SERVER_START )