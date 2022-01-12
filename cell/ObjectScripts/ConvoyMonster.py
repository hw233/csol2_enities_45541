from Monster import Monster
class ConvoyMonster( Monster ):
	"""
	"""
	def __init__( self ):
		Monster.__init__( self )
		self.ownerID = 0
	def setOwner( self, playerID ):
		self.ownerID = playerID

	def doGoBack( self, selfEntity ):
		"""
		"""
		pass


	def doRandomWalk( self, selfEntity ):
		"""
		"""
		pass
