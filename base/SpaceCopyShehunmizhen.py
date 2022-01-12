# -*- coding: gb18030 -*-
import Love3
from bwdebug import *
from SpaceCopyMaps import SpaceCopyMaps
from interface.SpaceCopyRaidRecordInterface import SpaceCopyRaidRecordInterface

class SpaceCopyShehunmizhen( SpaceCopyMaps, SpaceCopyRaidRecordInterface ):
	"""
	�������
	"""
	def __init__(self):
		SpaceCopyMaps.__init__( self )
		SpaceCopyRaidRecordInterface.__init__( self )
		self.__currSpawnID	= 0						# ��ʱ����	:	���ڳ�����ʼ��ʱ��¼��ǰ���ص�spawnPoint����
		self.cellData['teamLevel'] = self.params['teamLevel']
		self.cellData['teamMaxLevel'] = self.params['teamMaxLevel']
		self.spawnList = {}
		self.createFinish = False						# ���spawnPoint�Ƿ�������
		self.currParams = None							# ��ʱ��������¼��ǰҪ�����Ĺ������

	def onGetCell(self):
		"""
		cellʵ�崴�����֪ͨ���ص�callbackMailbox.onSpaceComplete��֪ͨ������ɡ�
		"""
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
		if entityType == "SpawnPointCopyYeWai":
			self.addSpawnPointCopy( baseEntity, baseEntity.getName() )

	def getDifficulty( self ):
		return self.getScript().difficulty

	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		һ��������spawnPoint ������ϡ�
		"""
		SpaceCopyMaps.onSpawnPointLoadedOver( self, retCode )
		self.createFinish = True	# spawnPoint������ϱ��

	def addSpawnPointCopy( self, baseMailBox, entityName ):
		"""
		�ѳ��������space.spawnPointCopyDict��
		"""
		if self.spawnList.has_key( entityName ):
			self.spawnList[entityName].append( baseMailBox )
		else:
			self.spawnList[entityName] = [baseMailBox]

	def spawnMonsters( self, params ):
		"""
		define method
		"""
		if not self.createFinish:
			self.addTimer( 1.0, 0.0, 10001 )	# �ȴ�������������
			if not self.currParams:
				self.currParams = params
			return
		
		for className, spList in self.spawnList.iteritems():
			for e in spList:
				e.cell.createEntity( params )

	def onTimer( self, id, userArg ):
		"""
		"""
		SpaceCopyMaps.onTimer( self, id, userArg )

		if userArg == 10001:	# �ȴ������������Ϻ��ٴι������
			self.spawnMonsters( self.currParams )

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

	def onBeforeDestroyCellEntity( self ):
		"""
		ɾ��cell entity ǰ����һЩ����
		"""
		self.spawnList = None