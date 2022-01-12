# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy

class SpaceCopyDragon( SpaceCopy ):
	"""
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
		self.spawnMonstersList = {}

	def addSpawnPointCopyDragon( self, mailbox, monsterType ):
		"""
		define method
		"""
		if self.spawnMonstersList.has_key( monsterType ):
			self.spawnMonstersList[monsterType].append( mailbox )
		else:
			self.spawnMonstersList[monsterType] = [mailbox]
	
	
	def spawnMonsters( self, params ):
		"""
		define method
		"""
		for i in self.spawnMonstersList[params["monsterType"]]:
			i.cell.createEntity( { "level":params["copyLevel"] } )
	
	