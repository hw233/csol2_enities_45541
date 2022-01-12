# -*- coding: gb18030 -*-
import csdefine

class AoZhanPlayerInfo( object ):
	def __init__( self ):
		object.__init__( self )
		self.dbid = 0
		self.mailBox = None
	
	def init( self, dbid, mailbox = None ):
		self.dbid = dbid
		self.mailBox = mailbox
		
	def getDict( self ):
		dict = {}
		dict[ "dbid" ] = self.dbid
		dict[ "mailBox" ] = self.mailBox
		return dict
		
	@staticmethod
	def createObjFromDict( dict ):
		obj = AoZhanPlayerInfo()
		obj.init( dict[ "dbid" ], dict[ "mailBox" ] )
		return obj
		
	def isSameType( self, obj ):
		return isinstance( obj, AoZhanPlayerInfo )
	
		
class AoZhanData( object ):
	def __init__( self ):
		object.__init__( self )
		self.aPlayer = None
		self.bPlayer = None
		self.failureList = []
		self.score = 0 #第一轮对打是没有积分的
	
	def initData( self, aPlayerDBID, bPlayerDBID, failureList ):
		self.aPlayer = AoZhanPlayerInfo()
		self.aPlayer.init( aPlayerDBID )
		self.bPlayer = AoZhanPlayerInfo()
		self.bPlayer.init( bPlayerDBID )
		for f in failureList:
			fplayer = AoZhanPlayerInfo()
			fplayer.init( f )
			self.failureList.append( fplayer )
	
	def regitsterMB( self, playerDBID, playerMB ):
		if self.aPlayer.dbid == playerDBID:
			self.aPlayer.mailBox = playerMB
		
		if self.bPlayer.dbid == playerDBID:
			self.bPlayer.mailBox = playerMB
		
		for f in self.failureList:
			if f.dbid == playerDBID:
				f.mailBox = playerMB

	def setPkMode( self ):
		if self.aPlayer and self.aPlayer.mailBox:
			self.__setPkMode( self.aPlayer.mailBox, csdefine.PK_CONTROL_PROTECT_ACT_1 )
		
		if self.bPlayer and self.bPlayer.mailBox:
			self.__setPkMode( self.bPlayer.mailBox, csdefine.PK_CONTROL_PROTECT_ACT_2 )
			
		for f in self.failureList:
			if f.mailBox:
				self.__setPkMode( f.mailBox, csdefine.PK_CONTROL_PROTECT_ACT_3 )
	
	def resertPkMode( self ):
		if self.aPlayer and self.aPlayer.mailBox:
			self.__setPkMode( self.aPlayer.mailBox, csdefine.PK_CONTROL_PROTECT_PEACE )
		
		if self.bPlayer and self.bPlayer.mailBox:
			self.__setPkMode( self.bPlayer.mailBox, csdefine.PK_CONTROL_PROTECT_PEACE )
			
		for f in self.failureList:
			if f.mailBox:
				self.__setPkMode( f.mailBox, csdefine.PK_CONTROL_PROTECT_PEACE )
	
	def getEnterNum( self ):
		# 获取进入了几方
		result = 0
		if self.aPlayer and self.aPlayer.mailBox:
			result += 1
		
		if self.bPlayer and self.bPlayer.mailBox:
			result += 1
		
		for f in self.failureList:
			if f.mailBox:
				result += 1
				break
		
		return result
	
	def __setPkMode( self, mailBox, pkmode ):
		mailBox.cell.setSysPKMode( pkmode )
	
	def getDictFromObj( self, obj ):
		dict = {}
		dict[ "aPlayer" ] = obj.aPlayer.getDict()
		dict[ "bPlayer" ] = obj.bPlayer.getDict()
		failureList = []
		for f in obj.failureList:
			failureList.append( f.getDict() )
		dict[ "failureList" ] = failureList
		return dict
	
	def createObjFromDict( self, dict ):
		obj = AoZhanData()
		obj.aPlayer = AoZhanPlayerInfo.createObjFromDict( dict[ "aPlayer" ] )
		obj.bPlayer = AoZhanPlayerInfo.createObjFromDict( dict[ "bPlayer" ] )
		for f in dict[ "failureList" ]:
			obj.failureList.append( AoZhanPlayerInfo.createObjFromDict( f ) )
			
		return obj
		
	def isSameType( self, obj ):
		return isinstance( obj, AoZhanData )

g_aoZhanData = AoZhanData()