# -*- coding: utf-8 -*-
# This is an example of how to place an Entity in the world via BigBang. On the
# Entity panel, select Creature and place the Entity in the world by pressing
# enter. The placeholder model refered to by modelName() will be placed into the
# BigBang representation of the world and the Entity will be placed into the
# appropriate chunk file when the world is saved. Game script can then be used
# to load the entities into the game world. See BigWorld.fetchEntitiesFromChunks
# in BaseApp's Python API.

import SpawnPoint

class SpawnPointStar( SpawnPoint.SpawnPoint ):
	def getEnums_entityName( self ):
		return SpawnPoint.keyname2name_monster

# MonsterSpawnPoint.py
