# -*- coding: gb18030 -*-
from SmartImport import smartImport

_data = {}
def getScript( spawnType ):
	global _data
	if not _data.has_key( spawnType ):
		mod = smartImport( "SpawnPointScript." + spawnType + ":" + spawnType )
		_data[ spawnType ] = mod()
	
	return _data[ spawnType ]

def createEntity( spawnType, args, spaceEntity, position, direction ):
	"""
	����һ���µ�SpawnPoint
	"""
	script = getScript( spawnType )
	if script:
		return script.createEntity( args , spaceEntity, position, direction )
		
	return None