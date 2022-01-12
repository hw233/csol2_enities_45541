# -*- coding: gb18030 -*-

# common
from bwdebug import *
# base
from SpaceCopy import SpaceCopy


class SpaceCopySingle( SpaceCopy ):
	"""
	单人地图
	"""
	def __init__( self ):
		SpaceCopy.__init__( self )