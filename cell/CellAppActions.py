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
		�����CellApp�ϣ��ҵ�ָ��ID��Entity.ִ��entity�������Ϊ��
		"""
		entity = BigWorld.entities.get( int(id), None )
		if entity is None:
			return
		if not entity.isDestroyed:
			getattr( entity, func )()


	def setRespawnRate( self, monsterClassName, rediviousTime ):
		"""
		����һЩ�������ˢ���ٶ�
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