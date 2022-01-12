# -*- coding: gb18030 -*-
from SpaceCopy import SpaceCopy

YI_JIE_STONE_CLASS_NAME	= "20254098"

class SpaceCopyYiJieZhanChang( SpaceCopy ):
	# 异界战场
	def __init__( self ):
		SpaceCopy.__init__( self )
		self.yiJieStone = None
	
	def spawnYiJieStone( self ) :
		"""
		<define method>
		开始刷洪荒灵石
		"""
		if self.yiJieStone :
			self.yiJieStone.cell.createEntity( { "entityName" : YI_JIE_STONE_CLASS_NAME } )
	
	def addSpawnPointCopy( self, baseMailbox, entityName ) :
		"""
		<define method>
		"""
		if entityName == YI_JIE_STONE_CLASS_NAME :
			self.yiJieStone = baseMailbox