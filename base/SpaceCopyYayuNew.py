# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy
from interface.SpaceCopyRaidRecordInterface import SpaceCopyRaidRecordInterface

class SpaceCopyYayuNew( SpaceCopy, SpaceCopyRaidRecordInterface ):
	"""
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
		SpaceCopyRaidRecordInterface.__init__( self )
		self.spawnPointYayu = None
		self.spawnPointMonsters = []
		self.spawnPointBoss = None

	def addSpawnPointYayu( self, spawnPoint, type ):
		"""
		define method
		"""
		self.spawnPointYayu = spawnPoint
		
	def addSpawnPointMonsters( self, spawnPoint, type ):
		"""
		define method
		"""
		
		if type == 0:
			self.spawnPointMonsters.append( spawnPoint )	# ��ͨС��
		elif type == 1:
			self.spawnPointBoss = spawnPoint				# Boss

	def spawnYayu( self, level ):
		"""
		define method
		"""
		self.spawnPointYayu.cell.createEntity( { "level":level } )

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
		for iSpawn in self.spawnPointMonsters:
			iSpawn.cell.createEntity( params )

	def spawnBoss( self, params ):
		"""
		define method
		"""
		params["yayuID"] = self.yayuID
		self.spawnPointBoss.cell.createEntity( params )
		

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
