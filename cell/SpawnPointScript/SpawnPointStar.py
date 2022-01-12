# -*- coding: gb18030 -*-

from bwdebug import *
from SpawnPoint import SpawnPoint
from ObjectScripts.GameObjectFactory import g_objFactory
import random
import time

import csdefine
import Const

class SpawnPointStar( SpawnPoint ):
	"""
	������߻��Ĺ�ͨ,��������ʱһ���Ը���,����һ������������ʼ��ʱ,��ʱ����ʱ�����й�������ʱһ���Ը���.
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity  )
	
	def createEntity( self, selfEntity, params = {} ):
		"""
		"""
		selfEntity.rediviousTimer = 0
		SpawnPoint.createEntity( self, selfEntity, params )
		selfEntity.currentRedivious = 0

	def entityDead( self, selfEntity ):
		"""
		Define method.
		��������֪ͨ
		"""
		selfEntity.currentRedivious += 1
		
		h = time.localtime()[3]
		m = time.localtime()[4]
		
		if h  % 2 == 0:
			rt = 3600 + ( 60 - m ) * 60
		else:
			rt = ( 60 - m ) * 60
		
		if not selfEntity.rediviousTimer:				#��2��Сʱˢ��
			selfEntity.rediviousTimer = selfEntity.addTimer( rt, 0, Const.SPAWN_ON_MONSTER_DIED )
