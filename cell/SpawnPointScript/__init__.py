# -*- coding: gb18030 -*-
from SmartImport import smartImport

_data = {}
def getScript( spawnType ):
	global _data
	if not _data.has_key( spawnType ):
		_data[ spawnType ] = smartImport( "SpawnPointScript." + spawnType + ":" + spawnType )()
	
	return _data[ spawnType ]