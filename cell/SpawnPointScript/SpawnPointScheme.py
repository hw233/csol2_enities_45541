# -*- coding: gb18030 -*-
# ��ͨ����ճ̿��Ƶ�ˢ�µ� by ���� 17:32 2010-10-13

import Const
from bwdebug import *
from ObjectScripts.GameObjectFactory import g_objFactory
from SpawnPoint import SpawnPoint

class SpawnPointScheme( SpawnPoint ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPoint.initEntity( self, selfEntity  )
		
	def createEntity( self, selfEntity, params = {} ):
		"""
		spawn point����ʱ�Զ���ʼ�����еĹ��
		
		ע�⣺���´��벻��ֱ�ӷ���initEntity()��ʱ��ִ�У����ڵײ������bug��ԭ����ĳЩ�����selfEntity.position��ֵ����ȷ�������ᵼ�³����Ĺ����޷��ƶ����޷���ɱ����
		phw.2008-02-19: �����ԣ���ʹʹ���ӳ٣���Ȼ���������������
		phw.2008-07-17: ��Ϊ��base�յ�onGetCell()��Ϣ����֪ͨcell��onBaseGotCell()��Ϣ�������ܽ��������
		"""
		selfEntity.base.registeToScheme()
		if not self.isCanSpawn( selfEntity ):
			return
		self.rediviousEntity( selfEntity, params )
		
	def rediviousEntity( self, selfEntity, params = {} ):
		"""
		���������������Ĺ���
		"""
		if not self.isCanSpawn( selfEntity ):
			return
			
		SpawnPoint.rediviousEntity( self, selfEntity )
		
	def startSpawn( self, selfEntity ):
		"""
		define method
		��ʼˢ��entity/ˢ�³�entity
		"""	
		selfEntity.setTemp( "canSpawn", True )
		selfEntity.currentRedivious = 1
		self.createEntity( selfEntity )
		
	def stopSpawn( self, selfEntity ):
		"""
		define method
		ֹͣˢ��entity/������ˢ�³�����entity
		"""
		selfEntity.setTemp( "canSpawn", False )
		if len( self.createdEntityIDs ) <= 0:
			return
		entities = self.entitiesInRangeExt( selfEntity.randomWalkRange )
		for e in entities:
			if not e.id in self.createdEntityIDs:
				continue
			if e.isReal():
				e.destroy()
			else:
				e.remoteCall( "destroy",[] )
		self.createdEntityIDs = []
	
	def isCanSpawn( self, selfEntity ):
		return selfEntity.queryTemp( "canSpawn", False )
	
	def onBaseGotCell( self, selfEntity ):
		"""
		��ʼ����ʱ�䲻ˢ��
		"""
		pass