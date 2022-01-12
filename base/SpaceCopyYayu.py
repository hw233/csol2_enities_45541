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
			self.spawnPointYayu = spawnPoint					# �m؅ˢ�µ�
		elif type == 1:
			self.spawnPointTowerDefense.append( spawnPoint )	# ������ˢ�µ�
		else:
			pass
		
	def addSpawnPointMonsters( self, spawnPoint, type ):
		"""
		define method
		"""
		if type == 0:
			self.spawnPointMonstersLeft.append( spawnPoint )	# ���ˢ�µ�
		elif type == 1:
			self.spawnPointMonstersRight.append( spawnPoint )	# �ұ�ˢ�µ�
		elif type == 2:
			self.spawnPointBoss = spawnPoint			# Boss
		else:
			self.spawnPointGuangXiao = spawnPoint		# ���͹�Ч

	def spawnYayu( self, level ):
		"""
		define method
		"""
		self.spawnPointYayu.cell.createEntity( {"level":level} )
		for spawn in self.spawnPointTowerDefense:
			spawn.cell.createEntity( {"level":level} )	# ���������m؅ͬʱˢ��

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
		��ҽ����˿ռ䣬��Ҫ���ݸ���boss�Ļ�ɱ����������
		��Ӧ����ʾ���������ѡ���Ǽ������������뿪������
		@param baseMailbox: ���mailbox
		@type baseMailbox: mailbox
		@param params: ���onEnterʱ��һЩ�������
		@type params: py_dict
		"""
		SpaceCopy.onEnter( self, baseMailbox, params )
		SpaceCopyRaidRecordInterface.onEnter( self, baseMailbox, params )
