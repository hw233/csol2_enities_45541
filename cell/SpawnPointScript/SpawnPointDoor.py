# -*- coding: gb18030 -*-
import BigWorld
from bwdebug import *
import csdefine
import csconst
from SpawnPoint import SpawnPoint
from ObjectScripts.GameObjectFactory import g_objFactory
import random

class SpawnPointDoor( SpawnPoint ):
	"""
	�ŵĳ�����
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity  )
		
		#selfEntity.getCurrentSpaceBase().addSpawnPointCopy( selfEntity.base, selfEntity.entityName )
		#ȥ����һ�䣬�������ڶ���SpawnPoint��onBaseGotCellʱ�ͻ�ˢ�����ˡ��žͲ���Ҫ�ӵ�ˢ�µ��б�ȥ�ˡ���Ȼ���������ĳЩ��������

	def createEntity( self, selfEntity, params = {} ):
		"""
		spawn point����ʱ�Զ���ʼ�����еĹ��
		
		ע�⣺���´��벻��ֱ�ӷ���initEntity()��ʱ��ִ�У����ڵײ������bug��ԭ����ĳЩ�����selfEntity.position��ֵ����ȷ�������ᵼ�³����Ĺ����޷��ƶ����޷���ɱ����
		phw.2008-02-19: �����ԣ���ʹʹ���ӳ٣���Ȼ���������������
		phw.2008-07-17: ��Ϊ��base�յ�onGetCell()��Ϣ����֪ͨcell��onBaseGotCell()��Ϣ�������ܽ��������
		"""
		args = self.getEntityArgs( selfEntity, params )
		entity = self._createEntity( selfEntity, args, 1 )[0] # ֻ����һ��
		selfEntity.setTemp( "spawnEntityID", entity.id )

	def openDoor( self, selfEntity, switchAct = True ):
		"""
		����
		"""
		door = BigWorld.entities.get( selfEntity.queryTemp( "spawnEntityID", 0 ) )
		if door:
			if switchAct:
				door.isOpen = True if not door.isOpen else False
				return

			door.isOpen = True