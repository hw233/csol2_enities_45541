# -*- coding: gb18030 -*-

"""
�����й�����������ͣ���������������Ҫֱ�Ӵ������������������Ҫ�����������д���ˣ��ѳ�������id֪ͨ�����ڵ�space
"""

import BigWorld
from bwdebug import *
from ObjectScripts.GameObjectFactory import g_objFactory
from SpawnPointCopyYeWai import SpawnPointCopyYeWai
import Math

GUI_YING_SHI		= "20322020"
FU_HUO_GUI_YING_SHI = "20322022"

class SpawnPointCopyWuYaoQianShao( SpawnPointCopyYeWai ):
	"""
	�����й�����������ͣ��ѳ�������id֪ͨ�����ڵ�space
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPointCopyYeWai.initEntity( self, selfEntity )

	def entityDead( self, selfEntity ):
		"""
		Define method.
		��������֪ͨ
		"""
		pass

	def wuyaoqiangshao_entityDead( self, selfEntity, currentPosition, currentDirection ):
		"""
		Define method.
		��������֪ͨ
		"""
		self.setTemp( "currentPosition", tuple( currentPosition ) )
		self.setTemp( "currentDirection", tuple( currentDirection ) )
		
		# �ҵ�����ʵ��
		if BigWorld.cellAppData.has_key( "spaceID.%i" % selfEntity.spaceID ):	# ��ֹ������destroy�󣬹��︴��
			spaceBase = BigWorld.cellAppData["spaceID.%i" % selfEntity.spaceID]
			try:
				spaceEntity = BigWorld.entities[ spaceBase.id ]
			except:
				DEBUG_MSG( "not find the spaceEntity!" )

			if spaceEntity.isNotRevive:		# ����������ٳ�������
				return

			selfEntity.currentRedivious += 1

			if selfEntity.entityName == GUI_YING_SHI:		# ������ֻ�ó�������Ϊ��Ӱʨ�ĳ����㸴�����
				if not selfEntity.rediviousTimer:
					selfEntity.rediviousTimer = selfEntity.addTimer( selfEntity.rediviousTime, 0, Const.SPAWN_ON_MONSTER_DIED )

	def createEntity( self, selfEntity, params = {} ):
		"""
		��ʼ������
		"""
		
		# �ҵ�����ʵ��
		spaceBase = BigWorld.cellAppData["spaceID.%i" % selfEntity.spaceID]
		try:
			spaceEntity = BigWorld.entities[ spaceBase.id ]
		except:
			DEBUG_MSG( "not find the spaceEntity!" )

		# �������е�entity
		args = self.getEntityArgs( selfEntity, params )
		for i in xrange( selfEntity.rediviousTotal ):
			entity = g_objFactory.getObject( selfEntity.entityName ).createEntity( selfEntity.spaceID, selfEntity.position, selfEntity.direction, args )
			if params.pop( "isReal", False ):	# �����������㣬�����Ĺ�������Ĺ�Ӱʨ
				entity.setTemp( "isReal", True )	# ����Ӱʨ��һ�����
				continue	# ��Ĺ�Ӱʨ����ҪaddSpawnEntityID()
				
			spaceEntity.base.addSpawnEntityID( selfEntity.entityName, entity.id )

	def rediviousEntity( self, selfEntity, params = {} ):
		"""
		virtual method.
		���������������Ĺ���
		"""
		selfEntity.rediviousTimer = 0
		args = self.getEntityArgs( selfEntity, params )

		# �ҵ�����ʵ��
		spaceBase = BigWorld.cellAppData["spaceID.%i" % selfEntity.spaceID]
		try:
			spaceEntity = BigWorld.entities[ spaceBase.id ]
		except:
			DEBUG_MSG( "not find the spaceEntity!" )
			
		if spaceEntity.isNotRevive:		# ����������ٳ�������
			selfEntity.currentRedivious = 0
			return
		
		currentPosition = self.queryTemp( "currentPosition" )
		currentDirection = self.queryTemp( "currentDirection" )
		args[ "spawnPos" ] = currentPosition
		for i in xrange( selfEntity.currentRedivious ):
			entity = g_objFactory.getObject( FU_HUO_GUI_YING_SHI ).createEntity( selfEntity.spaceID, currentPosition, currentDirection, args)	# �����Ӱʨ
			spaceEntity.base.addSpawnEntityID( FU_HUO_GUI_YING_SHI, entity.id )
			
		selfEntity.currentRedivious = 0