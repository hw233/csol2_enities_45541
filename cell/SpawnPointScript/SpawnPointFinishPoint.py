# -*- coding: gb18030 -*-

# $Id: SpawnPoint.py,v 1.25 2008-07-18 00:58:22 phw Exp $
"""
"""

import BigWorld
from bwdebug import *
import csdefine
import csconst
from SpawnPoint import SpawnPoint
from ObjectScripts.GameObjectFactory import g_objFactory
import random

TWENTY_MINUTE = 1200 

STOP_FINISH_TEST = 1

class SpawnPointFinishPoint( SpawnPoint ):
	"""
	������߻��Ĺ�ͨ,��������ʱһ���Ը���,����һ������������ʼ��ʱ,��ʱ����ʱ�����й�������ʱһ���Ը���.
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity  )
		selfEntity.addProximityExt( self.initiativeRange )
		selfEntity.addTimer(  TWENTY_MINUTE, 0, STOP_FINISH_TEST )
		selfEntity.stopFinishTest = False

	def entityDead( self, selfEntity ):
		"""
		Define method.
		��������֪ͨ
		"""
		pass

	def createEntity( self, selfEntity, params = {} ):
		"""
		spawn point����ʱ�Զ���ʼ�����еĹ�� 
		
		ע�⣺���´��벻��ֱ�ӷ���initEntity()��ʱ��ִ�У����ڵײ������bug��ԭ����ĳЩ�����selfEntity.position��ֵ����ȷ�������ᵼ�³����Ĺ����޷��ƶ����޷���ɱ����
		phw.2008-02-19: �����ԣ���ʹʹ���ӳ٣���Ȼ���������������
		phw.2008-07-17: ��Ϊ��base�յ�onGetCell()��Ϣ����֪ͨcell��onBaseGotCell()��Ϣ�������ܽ��������
		"""
		#d = { "spawnPos" : selfEntity.position, "spawnMB" : selfEntity.base }
		pass
		

	def onTimer( self, selfEntity, controllerID, userData ):
		"""
		"""
		if userData == STOP_FINISH_TEST:
			selfEntity.stopFinishTest = True


	def onEnterTrapExt( self,selfEntity, entity, range, controllerID ):
		"""
		"""
		if selfEntity.stopFinishTest:
			return
		if len(entity.queryTemp( "pointIDs", [] )) >= self.pointsCount:
			entity.finishRacehorse()
		
		entity.setTemp("pointIDs", [] )