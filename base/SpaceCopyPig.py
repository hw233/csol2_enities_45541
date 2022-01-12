# -*- coding: gb18030 -*-

from SpaceCopy import SpaceCopy
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface

class SpaceCopyPig( SpaceCopy, SpaceCopyYeWaiInterface ):
	"""
	����
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
		SpaceCopyYeWaiInterface.__init__( self )
		self.spawnPointCopyDict = {}
		self.createFinish = 0
		self.currParams = None			# ��ʱ��������¼��ǰҪ�����Ĺ������

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

	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		һ��������spawnPoint ������ϡ�
		"""
		SpaceCopy.onSpawnPointLoadedOver( self, retCode )
		SpaceCopyYeWaiInterface.onSpawnPointLoadedOver( self, retCode )
		self.createFinish = 1	# spawnPoint������ϱ��

	def addSpawnPointCopy( self, baseMailBox, entityName ):
		"""
		�ѳ��������space.spawnPointCopyDict��
		"""
		if self.spawnPointCopyDict.has_key( entityName ):
			self.spawnPointCopyDict[entityName].append( baseMailBox )
		else:
			self.spawnPointCopyDict[entityName] = [baseMailBox]

	def spawnMonsters( self, params ):
		"""
		define method
		"""
		self.currParams = params					# ��¼�����㴴������Ĳ���

		if self.createFinish == 1:					# ���������������
			self.createSpawnEntity()
		else:
			self.addTimer( 1.0, 0.0, 100001 )		# �ȴ�������������

	def onTimer( self, id, userArg ):
		"""
		"""
		SpaceCopy.onTimer( self, id, userArg )
		if userArg == 100001:						# �ȴ������������Ϻ�
			self.spawnMonsters( self.currParams )
	
	def createSpawnEntity( self ):
		"""
		��ʼˢ��
		"""
		if self.currParams.has_key( "bossIDs" ):
			bossIDs = self.currParams.pop( "bossIDs" )
			for id in bossIDs:
				for spawnMB in self.spawnPointCopyDict[ id ]:
					spawnMB.cell.createEntity( self.currParams )
		else:
			for className, spawnList in self.spawnPointCopyDict.iteritems():
				if className in self.bossIDs:
					continue
			
				for e in spawnList:
					e.cell.createEntity( self.currParams )