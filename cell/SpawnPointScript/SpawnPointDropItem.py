# -*- coding: gb18030 -*-
import BigWorld
from bwdebug import *
import csdefine
import csconst
import Const
from SpawnPoint import SpawnPoint
import random
from items import ItemDataList
g_items = ItemDataList.instance()

class SpawnPointDropItem( SpawnPoint ):
	"""
	������߻��Ĺ�ͨ,��������ʱһ���Ը���,����һ������������ʼ��ʱ,��ʱ����ʱ�����й�������ʱһ���Ը���.
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity  )
		if len( self.itemNames ) == 0:
			spaceType = selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			ERROR_MSG( "space %s: spawn point entity name is Null." % spaceType, selfEntity.position )
			return
		selfEntity.rediviousTime = 10.0												#1���Ӻ�����ˢ

	def entityDead( self, selfEntity ):
		"""
		Define method.
		��������֪ͨ
		"""
		selfEntity.currentRedivious += 1
		if not selfEntity.rediviousTimer:
			selfEntity.rediviousTimer = selfEntity.addTimer( selfEntity.rediviousTime, 0, Const.SPAWN_ON_MONSTER_DIED )
	
	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		��ȡҪ������entity����
		"""
		args = SpawnPoint.getEntityArgs( selfEntity, params )
		
		entityNames = self.itemNames.split("|")
		entityName = entityNames[random.randint( 0, len(entityNames)-1 )]
		args[ "className" ] = entityName
		return args

	def onBaseGotCell( self, selfEntity ):
		"""
		��base�ص�������֪ͨspawn point��base�Ѿ������cell��֪ͨ
		"""
		# ��base�����onGetCell()�ص����ٿ�ʼ������������������ܽ���������ʱ�����㲻��ȷ������
		# ��ǰ������ܿ����ǵײ��bug
		self.createEntity( selfEntity )