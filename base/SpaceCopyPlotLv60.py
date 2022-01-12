# -*- coding: gb18030 -*-

# 60 级剧情副本

# common
from bwdebug import *
# base
from SpaceCopy import SpaceCopy


class SpaceCopyPlotLv60( SpaceCopy ) :
	def __init__( self ):
		SpaceCopy.__init__( self )

	def onLoseCell( self ):
		SpaceCopy.onLoseCell( self )
		INFO_MSG( "Copy plot lv60 lose cell." )

	def createCell( self ):
		SpaceCopy.createCell( self )
		INFO_MSG( "Copy plot lv60 create cell." )

	def onGetCell( self ):
		SpaceCopy.onGetCell( self )
		INFO_MSG( "Copy plot lv60 get cell." )
