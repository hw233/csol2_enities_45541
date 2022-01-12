# -*- coding: gb18030 -*-
import copy
import random
from SpaceCopy import SpaceCopy
from AoZhanData import AoZhanData

class SpaceCopyAoZhan( SpaceCopy ):
	# 鏖战群雄
	def __init__( self ):
		SpaceCopy.__init__( self )
		self.cellData[ "enterNumber" ] = self.params.pop( "enterNumber" )
		self.cellData[ "matchType" ] = self.params.pop( "matchType" )
		self.cellData[ "roundTime" ] = self.params[ "roundTime" ]
		battleData = {}
		battleData[ "aPlayer" ] = {}
		battleData[ "aPlayer" ][ "dbid" ] = self.params.pop( "aPlayer", 0 )
		battleData[ "aPlayer" ][ "mailBox" ] = None
		
		battleData[ "bPlayer" ] = {}
		battleData[ "bPlayer" ][ "dbid" ] = self.params.pop( "bPlayer", 0 )
		battleData[ "bPlayer" ][ "mailBox" ] = None
		
		battleData[ "failureList" ] = []
		
		failureList = self.params.pop( "failureList", [] )
		for i in failureList:
			fdict = {}
			fdict[ "dbid" ] = i
			fdict[ "mailBox" ] = None
			battleData[ "failureList" ].append( fdict )
		
		obj = AoZhanData()
		self.cellData[ "battleData" ] = obj.createObjFromDict( battleData )