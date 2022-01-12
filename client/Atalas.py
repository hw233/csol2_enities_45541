# -*- coding: gb18030 -*-
#
# $Id: Atalas.py,v 1.1 2006-04-28 13:13:10 wanhaipeng Exp $

"""
图标Atalas。
"""

import BigWorld
import ResMgr
from utils import *
from bwdebug import *


class AtalasIcon:
	def __init__( self, texture, sect ):
		self.texture = texture
		self.name = sect.name
		self.uvtl = sect.readVector2( "uvtl" )
		self.uvbr = sect.readVector2( "uvbr" )

	def _u( self, u ):
		return self.uvtl.x + u * ( self.uvbr.x - self.uvtl.x )

	def _v( self, v ):
		return self.uvtl.y + v * ( self.uvbr.y - self.uvtl.y )

	def _uv( self, uv ):
		return ( self._u( uv[0] ), self._v( uv[1] ) )

	def _pixelSnap( self, gui ):
		pos = gui.position
		(w, h) = BigWorld.screenSize()
		pos.x = int(pos.x * w) / w
		pos.y = int(pos.y * h) / h
		gui.position = pos

	def settle( self, gui, om ):
		"""
			param om:		Original Mapping
		"""
		gui.textureName = self.texture
		gui.mapping = ( self._uv( om[0] ), self._uv( om[1] ), self._uv( om[2] ), self._uv( om[3] ) )


g_atalasIcons = {}

def loadAtalasIcons():
	global g_atalasIcons
	if len(g_atalasIcons) > 0:							# 不要重复Load
		return
	sect = ResMgr.openSection( "icons/atalas" )
	for (name, atalasSect) in sect.items():
		if not name.endswith( ".xml" ):
			continue
		texture = "icons/atalas/" + name.replace( ".xml", ".dds" )
		for (name, iconSect) in atalasSect._atalas.items():
			g_atalasIcons[name] = AtalasIcon( texture, iconSect )
	ResMgr.purge( "icons/atalas" )

def setIcon( gui, texture, om = ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)) ):
	global g_atalasIcons
	basename = texture[texture.rfind("/") + 1:texture.rfind(".")].lower()
	try:
		g_atalasIcons[basename].settle( gui, om )
		return True
	except KeyError, ke:
		return False


#
# $Log: not supported by cvs2svn $
#