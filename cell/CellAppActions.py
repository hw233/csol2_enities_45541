# -*- coding: gb18030 -*-

import BigWorld
import csconst


class CellAppActions:
	"""
	"""
	def __init__( self ):
		"""
		"""
		BigWorld.cellAppData["cellApp_%s_%s"%( BigWorld.getWatcher("nub/address"), "actions" )] = self
		BigWorld.globalData["cellApp_%s"%BigWorld.getWatcher("nub/address")] = BigWorld.getWatcher("nub/address")
		
	def entityFunc( self, id, func ):
		"""
		在这个CellApp上，找到指定ID的Entity.执行entity自身的行为。
		"""
		entity = BigWorld.entities.get( int(id), None )
		if entity is None:
			return
		if not entity.isDestroyed:
			getattr( entity, func )()


	def setRespawnRate( self, monsterClassName, rediviousTime ):
		"""
		更新一些出生点的刷怪速度
		"""
		spawnsClass = ["SpawnPoint", 
						"RandomSpawnPoint", 
						"SpawnPointCopy",
						"SpawnPointStar",]
		if monsterClassName == "0":
			for i in BigWorld.entities.values():
				if not i.isReal():
					continue
				if i.__module__ in spawnsClass:
					i.rediviousTime = float(rediviousTime)
		else:
			for i in BigWorld.entities.values():
				if not i.isReal():
					continue
				if i.__module__ in spawnsClass:
					if i.entityName == monsterClassName:
						i.rediviousTime = float( rediviousTime )


g_cellappActions = CellAppActions()