# -*- coding: gb18030 -*-

import ResMgr
import Function

#path = "universes\zly_ying_ke_cun"



def heightFixed( path ):
	chunkfiles = Function.searchFile( path, [".chunk"] )
	for iChunkFile in chunkfiles:
		sec = ResMgr.openSection( iChunkFile )
		for iSec in sec.values():
			if not iSec.has_key("portal"):
				continue;
			if not iSec["portal"].has_key("chunk"):
				continue;
			chunkName = iSec["portal"]["chunk"].asString
			if chunkName == "heaven" or chunkName == "earth":
				print "old value:",iSec["d"].asString
				iSec.writeFloat( "d", -20000.0 )
		sec.save()