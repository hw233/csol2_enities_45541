# -*- coding: gb18030 -*-

import random

import BigWorld

from SpacePlanes import SpacePlanes

from config.server.PickAnimaTrapConfig import Datas as datas_config

PICK_ANIMA_ENTITY_TYPE = "TrapPickAnima"
PICK_ANIMA_TRAP_MODEL_NUMBER = "gw7235_1"
PICK_ANIMA_ZHADAN_MODEL_NUMBER = "gw7611_1"

class SpacePlanesPickAnima( SpacePlanes ):
	"""
	拾取灵气副本
	"""
	def __init__( self ):
		super( SpacePlanesPickAnima, self ).__init__()
	
	def onLoadPlanesEntitiesOver( self, planesID ):
		"""
		"""
		SpacePlanes.onLoadPlanesEntitiesOver( self, planesID )
		self.spawnAnimaTraps( planesID )
	
	def spawnAnimaTraps( self, planesID ):
		"""
		刷出灵气配置entity
		"""
		for trapData in datas_config:
			lingQiNum = trapData[ "lingQi" ]
			zhaDanNum = trapData[ "zhadan" ]
			posList = eval( trapData[ "posList" ] )
			usePosList = []
			for i in xrange( lingQiNum ):
				newPosList = list( set( posList ) ^ set( usePosList ) )
				if not len( newPosList ):
					break
				pos = random.choice( newPosList )
				self._crateAnimaTrapEntity( pos, planesID )
				usePosList.append( pos )
			
			for j in xrange( zhaDanNum ):
				newPosList = list( set( posList ) ^ set( usePosList ) )
				if not len( newPosList ):
					break
				pos = random.choice( newPosList )
				self._createZhaDanEntity( pos, planesID )
				usePosList.append( pos )
				
	def _crateAnimaTrapEntity( self, pos, planesID ):
		createArgs = {}
		createArgs[ "planesID" ] = planesID
		createArgs[ "modelNumber" ] = PICK_ANIMA_TRAP_MODEL_NUMBER
		createArgs[ "modelScale" ] = 1.0
		createArgs[ "trapRange" ] = 2.0
		createArgs[ "rewardPotential" ] = 5
		createArgs[ "createOnCell" ] = self.cell
		createArgs[ "position" ] = pos
		createArgs[ "direction" ] = (0, 0, 0)
		newEntity = BigWorld.createBaseLocally( PICK_ANIMA_ENTITY_TYPE, createArgs )
		self.addPlanesSpawnEntity( planesID, newEntity )
	
	def _createZhaDanEntity( self, pos, planesID ):
		createArgs = {}
		createArgs[ "planesID" ] = planesID
		createArgs[ "modelNumber" ] = PICK_ANIMA_ZHADAN_MODEL_NUMBER
		createArgs[ "modelScale" ] = 1.0
		createArgs[ "createOnCell" ] = self.cell
		createArgs[ "radius" ] = 2.0
		createArgs[ "position" ] = pos
		createArgs[ "direction" ] = (0, 0, 0)
		createArgs[ "enterSpell" ] = 721036001
		createArgs[ "isDisposable" ] = True
		newEntity = BigWorld.createBaseLocally( "SkillTrap", createArgs )
		self.addPlanesSpawnEntity( planesID, newEntity )