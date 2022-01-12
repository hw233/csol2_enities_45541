# -*- coding: gb18030 -*-
import BigWorld

from bwdebug import *
import Love3

from SpaceCopy import SpaceCopy
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface
from interface.SpaceCopyRaidRecordInterface import SpaceCopyRaidRecordInterface

from ObjectScripts.GameObjectFactory import GameObjectFactory
g_objFactory = GameObjectFactory.instance()

class SpaceCopyXieLongDongXue( SpaceCopy, SpaceCopyYeWaiInterface, SpaceCopyRaidRecordInterface ):
	"""
	а����Ѩ����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopy.__init__( self )
		SpaceCopyYeWaiInterface.__init__( self )
		SpaceCopyRaidRecordInterface.__init__( self )
		self.spawnMonstersList = {}

	def addSpawnPointCopy( self, mailbox, entityName ):
		"""
		define method
		"""
		if self.spawnMonstersList.has_key( entityName ):
			self.spawnMonstersList[entityName].append( mailbox )
		else:
			self.spawnMonstersList[entityName] = [mailbox]

	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		��������һ��entity��֪ͨ
		@param	entityType		: entity�Ľű����
		@type 	entityType		: String
		@param	entity			: baseEntityʵ��
		"""
		if entityType == "SpawnPointCopyYeWai":
			self.addSpawnPointCopy( baseEntity, baseEntity.getName() )

	def checkNeedSpawn( self, sec ):
		"""
		virtual method.
		�ж��Ƿ���Ҫ������ˢ�µ�
		"""
		return SpaceCopyYeWaiInterface.checkNeedSpawn( self, sec ) and SpaceCopy.checkNeedSpawn( self, sec )

	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		һ��������spawnPoint ������ϡ�
		"""
		SpaceCopy.onSpawnPointLoadedOver( self, retCode )
		SpaceCopyYeWaiInterface.onSpawnPointLoadedOver( self, retCode )

	def spawnMonsters( self, params ):
		"""
		define method
		"""
		if params.has_key( "bossID" ):
			bossID = params.pop( "bossID" )
			for e in self.spawnMonstersList[ bossID ]:
				e.cell.createEntity( params )
		else:
			for className, spList in self.spawnMonstersList.iteritems():
				if className in self.bossIDs:
					continue

				for e in spList:
					try:
						e.cell.createEntity( params )
					except:
						pass

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		��ҽ����˿ռ䣬��Ҫ���ݸ���boss�Ļ�ɱ����������
		��Ӧ����ʾ���������ѡ���Ǽ������������뿪������
		@param baseMailbox: ���mailbox
		@type baseMailbox: mailbox
		@param params: ���onEnterʱ��һЩ�������
		@type params: py_dict
		"""
		SpaceCopy.onEnter( self, baseMailbox, params )
		SpaceCopyRaidRecordInterface.onEnter( self, baseMailbox, params )
