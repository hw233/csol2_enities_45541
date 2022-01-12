# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy

class SpaceCopyJueDiFanJi( SpaceCopy ):
	"""
	绝地反击活动副本
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )

	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		SpaceCopy.load( self, section )
		
		data = section[ "Space" ][ "right_playerEnterPoint" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.right_playerEnterPoint = ( pos, direction )
		
		data = section[ "Space" ][ "left_playerEnterPoint" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.left_playerEnterPoint = ( pos, direction )
