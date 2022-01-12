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
		define method，通过spawnPoint找到门entity，打开门entity
		"""
		for e in self.spawnMonstersList[params["entityName"]]:
			e.cell.remoteCallScript( "openDoor", [] )

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		玩家进入了空间，需要根据副本boss的击杀情况给予玩家
		相应的提示，并让玩家选择是继续副本还是离开副本。
		@param baseMailbox: 玩家mailbox
		@type baseMailbox: mailbox
		@param params: 玩家onEnter时的一些额外参数
		@type params: py_dict
		"""
		SpaceCopy.onEnter( self, baseMailbox, params )
		SpaceCopyRaidRecordInterface.onEnter( self, baseMailbox, params )
