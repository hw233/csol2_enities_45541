# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy
from interface.SpaceCopyRaidRecordInterface import SpaceCopyRaidRecordInterface

class SpaceCopyFJSG( SpaceCopy, SpaceCopyRaidRecordInterface ):
	"""
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
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

	def spawnMonsters( self, params ):
		"""
		define method
		"""
		entityName = params["entityName"]
		params.pop("entityName")
		for e in self.spawnMonstersList[entityName]:
			e.cell.createEntity( params )

	def openDoor( self, params ):
		"""
		define method��ͨ��spawnPoint�ҵ���entity������entity
		"""
		for e in self.spawnMonstersList[params["entityName"]]:
			e.cell.remoteCallScript( "openDoor", [] )

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
