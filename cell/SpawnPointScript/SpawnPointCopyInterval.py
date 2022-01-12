# -*- coding: gb18030 -*-

"""
�����й�����������ͣ���������������Ҫֱ�Ӵ������������������Ҫ������intervalTimeʱ��󣬳���һ�����ֱ������Ϊ��spawnNum
"""

import BigWorld
from bwdebug import *
import csdefine
import csconst
import random
from SpawnPoint import SpawnPoint

class SpawnPointCopyInterval( SpawnPoint ):
	"""
	�����й������������
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPoint.initEntity( self, selfEntity  )
		
	def entityDead( self, selfEntity ):
		"""
		Define method.
		��������֪ͨ
		"""
		pass	# ������������Ҫ����

	def onBaseGotCell( self, selfEntity ):
		"""
		��base�ص�������֪ͨspawn point��base�Ѿ������cell��֪ͨ
		"""
		# ��base�����onGetCell()�ص����ٿ�ʼ������������������ܽ���������ʱ�����㲻��ȷ������
		# ��ǰ������ܿ����ǵײ��bug
		pass	# ������������㣬����Ҫ����������Ĺ���

	def getEntityArgs( self, selfEntiy, params = {} ):
		args = SpawnPoint.getEntityArgs( self, selfEntiy, params )
		
		entityNameList = []
		entityOddsList = []
		for e in self.entityName.split( ";" ):
			entityNameList.append( str( e.split( ":" )[0] ) )
			entityOddsList.append( int( e.split( ":" )[1] ) )
			
		args[ "className" ] = getRandomElement( entityNameList, entityOddsList )
		return args
	
	def createEntity( self,selfEntity, params = {} ):
		"""
		��ʼ������
		"""
		SpawnPoint.createEntity( self, selfEntity, params )
		# ���������һ�����self.spawnNum��1
		spawnNum = selfEntity.queryTemp( "spawnNum", 0 )
		spawnNum -= 1
		selfEntity.setTemp( "spawnNum", spawnNum )
		if spawnNum > 0:
			intervalTime = selfEntity.queryTemp( "intervalTime", 0 )
			assert intervalTime > 0
			self.addTimer( intervalTime, 0, Const.SPAWN_ON_SERVER_START )	# ���intervalTime�󣬳���һ������