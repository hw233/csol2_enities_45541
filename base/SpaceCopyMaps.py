# -*- coding: gb18030 -*-
from SpaceCopy import SpaceCopy

class SpaceCopyMaps( SpaceCopy ):
	"""
	多地图副本
	"""
	def __init__( self ):
		SpaceCopy.__init__( self )
		self.cellData[ "copyKey" ] = self.params[ "copyKey" ]
		self.cellData[ "createTime" ] = self.params[ "createTime" ]
		self.cellData[ "copyStatBoss" ] = self.params[ "copyStatBoss" ]
		self.cellData[ "copyStatMonster" ] = self.params[ "copyStatMonster" ]
		