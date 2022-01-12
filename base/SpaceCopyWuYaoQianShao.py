# -*- coding: gb18030 -*-
import random
import BigWorld

from SpaceCopyMaps import SpaceCopyMaps
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface
from interface.SpaceCopyRaidRecordInterface import SpaceCopyRaidRecordInterface
from ObjectScripts.GameObjectFactory import GameObjectFactory
g_objFactory = GameObjectFactory.instance()
from bwdebug import *

import Love3

class SpaceCopyWuYaoQianShao( SpaceCopyMaps, SpaceCopyRaidRecordInterface ):
	"""
	����ǰ�ڸ���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopyMaps.__init__( self )
		SpaceCopyRaidRecordInterface.__init__( self )
		self.__currSpawnID	= 0						# ��ʱ����	:	���ڳ�����ʼ��ʱ��¼��ǰ���ص�spawnPoint����
		self.cellData['teamLevel'] = self.params['teamLevel']
		self.cellData['teamMaxLevel'] = self.params['teamMaxLevel']
		self.spawnPointCopyDict = {}				# ��¼���������й�������� such as:{ "className" : [ spawnPointCopy.base, ... ], ... }
		self.createFinish = 0						# ���spawnPoint�Ƿ�������
		#self.spawnEntityParamsDict = {}				# ��¼�����㴴������ʱ���� such as:{ "className": params }
		#self.spawnEntityIDDict = {}					# ��¼������ĳ������entity��id��such as { entityName : [ id1,id2,... ],... }
		#self.spawnPointDoorDict = {}				# ��¼������SpawnPointDoor������ such as:{ "className" : [ SpawnPointDoor.base, ... ], ... }
		self.currParams = None						# ��ʱ��������¼��ǰҪ�����Ĺ������

	def onGetCell(self):
		"""
		cellʵ�崴�����֪ͨ���ص�callbackMailbox.onSpaceComplete��֪ͨ������ɡ�
		"""
		# create spawn point into this space on other thread.
		if len( self.getScript().getSpaceSpawnFile( self ) ) == 0:
			WARNING_MSG( "space %s no spawn file specified." % self.className )
		else:
			Love3.g_spawnLoader.registerSpace( self )		# �ӵ�������

		# space cell �������ͨ��
		self.domainMB.onSpaceGetCell( self.spaceNumber )

	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		��������һ��entity��֪ͨ
		@param	entityType		: entity�Ľű����
		@type 	entityType		: String
		@param	entity			: baseEntityʵ��
		"""
		if entityType == "SpawnPointCopyYeWai" or entityType == "SpawnPointCopyWuYaoQianShao":
			self.addSpawnPointCopy( baseEntity, baseEntity.getName() )

	def getDifficulty( self ):
		return self.getScript().difficulty

	def checkNeedSpawn( self, sec ):
		# virtual method.
		# �ж��Ƿ���Ҫ������ˢ�µ�
		return SpaceCopyMaps.checkNeedSpawn( self, sec )

	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		һ��������spawnPoint ������ϡ�
		"""
		SpaceCopyMaps.onSpawnPointLoadedOver( self, retCode )
		self.createFinish = 1	# spawnPoint������ϱ��
		

	def addSpawnPointCopy( self, baseMailBox, entityName ):
		"""
		�ѳ��������space.spawnPointCopyDict��
		"""
		if self.spawnPointCopyDict.has_key( entityName ):
			self.spawnPointCopyDict[entityName].append( baseMailBox )
		else:
			self.spawnPointCopyDict[entityName] = [baseMailBox]

	def createSpawnEntities( self, params ):
		"""
		֪ͨspawnPoingCopy�������
		"""
		if not self.createFinish:
			self.addTimer( 1.0, 0.0, 10001 )	# �ȴ�������������
			if not self.currParams:
				self.currParams = params
			return

		if params.has_key( "bossID" ):
			for spawnPointCopy in self.spawnPointCopyDict[ params[ "bossID" ] ]:
				spawnPointCopy.cell.createEntity( params )	# spawnPointCopyˢ��������
		else:
			for className, spList in self.spawnPointCopyDict.iteritems():
				if className in self.getScript().bossID:
					continue

				for e in spList:
					e.cell.createEntity( params )

		self.currParams = None

	def onTimer( self, id, userArg ):
		"""
		"""
		SpaceCopyMaps.onTimer( self, id, userArg )

		if userArg == 10001:	# �ȴ������������Ϻ��ٴι������
			self.createSpawnEntities( self.currParams )

	def onBeforeDestroyCellEntity( self ):
		"""
		ɾ��cell entity ǰ����һЩ����
		"""
		self.spawnPointCopyDict = None

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
		SpaceCopyMaps.onEnter( self, baseMailbox, params )
		SpaceCopyRaidRecordInterface.onEnter( self, baseMailbox, params )
