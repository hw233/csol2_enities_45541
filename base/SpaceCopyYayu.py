# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy
from interface.SpaceCopyRaidRecordInterface import SpaceCopyRaidRecordInterface

class SpaceCopyYayu( SpaceCopy, SpaceCopyRaidRecordInterface ):
	"""
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
		SpaceCopyRaidRecordInterface.__init__( self )
		self.spawnPointYayu = None
		self.spawnPointMonstersLeft = []
		self.spawnPointMonstersRight = []
		self.spawnPointBoss = None
		self.spawnPointGuangXiao = None
		self.spawnPointTowerDefense = []

	def addSpawnPointYayu( self, spawnPoint, type ):
		"""
		define method
		"""
		if type == 0:
			self.spawnPointYayu = spawnPoint					# 猰貐刷新点
		elif type == 1:
			self.spawnPointTowerDefense.append( spawnPoint )	# 防御塔刷新点
		else:
			pass
		
	def addSpawnPointMonsters( self, spawnPoint, type ):
		"""
		define method
		"""
		if type == 0:
			self.spawnPointMonstersLeft.append( spawnPoint )	# 左边刷新点
		elif type == 1:
			self.spawnPointMonstersRight.append( spawnPoint )	# 右边刷新点
		elif type == 2:
			self.spawnPointBoss = spawnPoint			# Boss
		else:
			self.spawnPointGuangXiao = spawnPoint		# 传送光效

	def spawnYayu( self, level ):
		"""
		define method
		"""
		self.spawnPointYayu.cell.createEntity( {"level":level} )
		for spawn in self.spawnPointTowerDefense:
			spawn.cell.createEntity( {"level":level} )	# 防御塔跟猰貐同时刷新

	def setYayuID( self, id ):
		"""
		define method
		"""
		self.yayuID = id
		
	def spawnMonster( self, params ):
		"""
		define method
		"""
		params["yayuID"] = self.yayuID
		for iSpawn in self.spawnPointMonstersLeft:
			iSpawn.cell.createEntity( params )

	def spawnBoss( self, params ):
		"""
		define method
		"""
		params["yayuID"] = self.yayuID
		self.spawnPointBoss.cell.createEntity( params )
		
	def spawnGuangXiao( self, params ):
		"""
		define method
		"""
		params["yayuID"] = self.yayuID
		self.spawnPointGuangXiao.cell.createEntity( params )

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
