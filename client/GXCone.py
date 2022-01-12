# -*- coding: gb18030 -*-

import BigWorld

# $Id: GXCone.py,v 1.2 2005-11-25 02:35:51 wanhaipeng Exp $

class GXCone( BigWorld.Entity ):
	def __init__( self ):
		BigWorld.Entity.__init__( self )

	def pushData( self, data ):
		print "GXCone:pushData.", len(data)
