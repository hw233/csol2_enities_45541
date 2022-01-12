# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy

SPAWN_AFTER_A_SECOND	= 3001		# 一秒后刷怪timer

class CopyTemplate( SpaceCopy ):
	"""
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
		self.spawnMonstersList = {}
		self.spawnMonstersParams = {}
	
	def copyTemplate_addSpawnPoint( self, mailbox, monsterType ):
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
		if not self.isSpawnPointLoaderOver :						# 刷新点未加载完成，1 秒后再次尝试刷怪
			timerID = self.addTimer( 1, 0, SPAWN_AFTER_A_SECOND )
			self.spawnMonstersParams[ timerID ] = params
			return
		for i in self.spawnMonstersList[ params["monsterType"] ]:
			i.cell.createEntity( params )
	
	def onTimer( self, id, userArg ):
		"""
		"""
		# 一秒后尝试刷怪处理
		if userArg == SPAWN_AFTER_A_SECOND :
			self.spawnMonsters( self.spawnMonstersParams[ id ] )
			del self.spawnMonstersParams[ id ]

		SpaceCopy.onTimer( self, id, userArg )

