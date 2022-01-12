# -*- coding: gb18030 -*-

"""
神鬼秘境副本
"""

from SpaceCopyMapsTeam import SpaceCopyMapsTeam


class SpaceCopyWuYaoQianShao(SpaceCopyMapsTeam):
	"""
	巫妖前哨脚本
	"""
	def __init__( self ):
		SpaceCopyMapsTeam.__init__( self )
		self.difficulty = 0
		#self.bossID = 0
	
	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		SpaceCopyMapsTeam.load( self, section )
		self.difficulty = section[ "Space" ][ "difficulty" ].asInt
		#self.bossID = section[ "Space" ][ "bossID" ].asString
