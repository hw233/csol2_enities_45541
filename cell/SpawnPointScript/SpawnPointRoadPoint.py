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
import ECBExtend


class SpawnPointRoadPoint( SpawnPoint ):
	"""
	������߻��Ĺ�ͨ,��������ʱһ���Ը���,����һ������������ʼ��ʱ,��ʱ����ʱ�����й�������ʱһ���Ը���.
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity  )
		trapRange = selfEntity.queryTemp( "trapRange" )
		selfEntity.addProximityExt( trapRange )

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

	def onEnterTrapExt( self, selfEntity, entity, range, controllerID ):
		"""
		"""
		if not entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			return
		
		pointIndex = selfEntity.queryTemp( "pointIndex" )
		endPoint = selfEntity.queryTemp( "endPoint" )
		entity.addRacePointIndex( pointIndex, endPoint )

	def onBaseGotCell( self, selfEntity ):
		"""
		"""
		pass