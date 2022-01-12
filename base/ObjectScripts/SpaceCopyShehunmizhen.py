# -*- coding: gb18030 -*-


from SpaceCopyMapsTeam import SpaceCopyMapsTeam

class SpaceCopyShehunmizhen( SpaceCopyMapsTeam ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopyMapsTeam.__init__( self )
		self.difficulty = 0

	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		SpaceCopyMapsTeam.load( self, section )
		self.difficulty = section[ "Space" ][ "difficulty" ].asInt