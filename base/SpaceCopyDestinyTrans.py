# -*- coding: gb18030 -*-

from bwdebug import *
from SpaceCopy import SpaceCopy
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface

class SpaceCopyDestinyTrans( SpaceCopy, SpaceCopyYeWaiInterface ):
	"""
	�����ֻظ���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopy.__init__( self )
		SpaceCopyYeWaiInterface.__init__( self )
		self.createFinish = 0
		self.spawnMonstersList = {}
		self.currParams = None						# ��ʱ��������¼��ǰҪ�����Ĺ������

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
		# virtual method.
		# �ж��Ƿ���Ҫ������ˢ�µ�
		return SpaceCopyYeWaiInterface.checkNeedSpawn( self, sec ) and SpaceCopy.checkNeedSpawn( self, sec )

	def getDifficulty( self ):
		"""
		����SpaceCopyYeWaiInterface�ķ���
		"""
		return 0

	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		һ��������spawnPoint ������ϡ�
		"""
		SpaceCopy.onSpawnPointLoadedOver( self, retCode )
		SpaceCopyYeWaiInterface.onSpawnPointLoadedOver( self, retCode )
		self.createFinish = 1	# spawnPoint������ϱ��

	def addSpawnPointCopy( self, mailbox, entityName ):
		"""
		define method
		"""
		if self.spawnMonstersList.has_key( entityName ):
			self.spawnMonstersList[entityName].append( mailbox )
		else:
			self.spawnMonstersList[entityName] = [mailbox]

	def createSpawnEntities( self, params ):
		"""
		define method
		֪ͨˢ��
		"""
		if not self.currParams:
			self.currParams = params				# ��¼�����㴴������Ĳ���

		if self.createFinish == 1:					# ���������������
			self.createSpawnEntityCopy()
		else:
			self.addTimer( 1.0, 0.0, 100001 )		# �ȴ�������������

	def onTimer( self, id, userArg ):
		"""
		"""
		SpaceCopy.onTimer( self, id, userArg )
		if userArg == 100001:						# �ȴ������������Ϻ�
			self.createSpawnEntities( self.currParams )

	def onBeforeDestroyCellEntity( self ):
		"""
		ɾ��cell entity ǰ����һЩ����
		"""
		self.spawnMonstersList = None

	def createSpawnEntityCopy( self ):
		"""
		��ʼˢ��
		"""
		for className, spawnList in self.spawnMonstersList.iteritems():
			for spawn in spawnList:
				if spawn.getSpawnType() == "SpawnPointCopyYeWai":
					spawn.cell.createEntity( self.currParams )