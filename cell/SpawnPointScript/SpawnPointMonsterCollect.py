# -*- coding: gb18030 -*-
# ���������ù����ˢ�µ� by ���� 10:43 2011-1-14

from bwdebug import *
from SpawnPointSpecial import SpawnPointSpecial

class SpawnPointMonsterCollect( SpawnPointSpecial ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPointSpecial.initEntity( self, selfEntity  )
	
	def createEntity( self, selfEntity, params = {} ):
		"""
		define method
		ָ���������͡�������Ʒˢ��
		"""
		self.rediviousEntity( selfEntity, params )