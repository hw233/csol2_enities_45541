# -*- coding: gb18030 -*-

import Language
from SpaceCopy import SpaceCopy

class SpaceCopyChallenge( SpaceCopy ):
	"""
	挑战副本
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
		self._spawnFileDict = {}
	
	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		SpaceCopy.load( self, section )
	
	def getSpaceSpawnFile( self, selfEntity ):
		spaceChallengeGate = selfEntity.params[ "spaceChallengeGate" ]
		if spaceChallengeGate:
			self._spawnFile = "config//server//spawn//hua_shan_spawn//" + str( spaceChallengeGate ) + ".xml"
			return self._spawnFile

		return ""
		
	def getSpawnSection( self ):
		"""
		"""
		return Language.openConfigSection( self._spawnFile )
		