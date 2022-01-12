# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy

SPAWN_AFTER_A_SECOND	= 3001		# һ���ˢ��timer

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
		if not self.isSpawnPointLoaderOver :						# ˢ�µ�δ������ɣ�1 ����ٴγ���ˢ��
			timerID = self.addTimer( 1, 0, SPAWN_AFTER_A_SECOND )
			self.spawnMonstersParams[ timerID ] = params
			return
		for i in self.spawnMonstersList[ params["monsterType"] ]:
			i.cell.createEntity( params )
	
	def onTimer( self, id, userArg ):
		"""
		"""
		# һ�����ˢ�ִ���
		if userArg == SPAWN_AFTER_A_SECOND :
			self.spawnMonsters( self.spawnMonstersParams[ id ] )
			del self.spawnMonstersParams[ id ]

		SpaceCopy.onTimer( self, id, userArg )

