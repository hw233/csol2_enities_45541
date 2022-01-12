# -*- coding: gb18030 -*-
import BigWorld
from bwdebug import *
import csdefine
import csconst
from SpawnPoint import SpawnPoint
from ObjectScripts.GameObjectFactory import g_objFactory
import random

class SpawnPointCopyDoor( SpawnPoint ):
	"""
	�ŵĳ�����
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity  )
		selfEntity.getCurrentSpaceBase().addSpawnPoint( selfEntity.base, selfEntity.queryTemp( "monsterType" ) )

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

	def openDoor( self, selfEntity ):
		"""
		����
		"""
		door = BigWorld.entities.get( selfEntity.queryTemp( "spawnEntityID", 0 ) )
		if door:
			if door.isOpen != True:
				door.isOpen = True