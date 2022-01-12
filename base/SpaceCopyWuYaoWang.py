# -*- coding: gb18030 -*-
import random
import BigWorld

from bwdebug import *
from SpaceCopy import SpaceCopy
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface
from interface.SpaceCopyRaidRecordInterface import SpaceCopyRaidRecordInterface
from ObjectScripts.GameObjectFactory import GameObjectFactory

import Love3

g_objFactory = GameObjectFactory.instance()

BAO_ZANG_WEI_BING				= [ "20732008", "20722043" ]		# ����������������className
WU_YAO_WANG						= [ "20742059", "20742060", "20742061" ]		# ��������className

class SpaceCopyWuYaoWang( SpaceCopy, SpaceCopyYeWaiInterface, SpaceCopyRaidRecordInterface ):
	"""
	���������ظ���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopy.__init__( self )
		SpaceCopyYeWaiInterface.__init__( self )
		SpaceCopyRaidRecordInterface.__init__( self )
		self.__currSpawnID	= 0						# ��ʱ����	:	���ڳ�����ʼ��ʱ��¼��ǰ���ص�spawnPoint����
		self.spawnPointCopyDict = {}				# ��¼���������й�������� such as:{ "className" : [ spawnPointCopy.base, ... ], ... }
		self.spawnEntityParamsDict = {}				# ��¼�����㴴������ʱ���� such as:{ "className": params }

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
		self.addTimer( 1.0, 0.0, 100001 )
		for cid in BAO_ZANG_WEI_BING:
			self.spawnEntityParamsDict[ cid ] = { "level": self.params[ "teamLevel" ] }

		for cid in WU_YAO_WANG:
			self.spawnEntityParamsDict[ cid ] = { "level": self.params[ "teamLevel" ] }

	def addSpawnPointCopy( self, baseMailBox, entityName ):
		"""
		�ѳ��������space.spawnPointCopyDict��
		"""
		if self.spawnPointCopyDict.has_key( entityName ):
			self.spawnPointCopyDict[entityName].append( baseMailBox )
		else:
			self.spawnPointCopyDict[entityName] = [baseMailBox]

	def createSpawnEntities( self ):
		"""
		ˢ�µ������ϣ���ʼˢ������
		"""
		for entityName in self.spawnPointCopyDict.keys():
			self.createSpawnEntityCopy( entityName, self.spawnEntityParamsDict[entityName] )

	def createSpawnEntityCopy( self, entityName, params ):
		"""
		֪ͨspawnPoingCopy�������
		"""
		for spawnPointCopy in self.spawnPointCopyDict[entityName]:
			spawnPointCopy.cell.createEntity( params )	# spawnPointCopyˢ������

	def onTimer( self, id, userArg ):
		"""
		"""
		SpaceCopy.onTimer( self, id, userArg )

		if userArg == 100001:
			self.createSpawnEntities()

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