# -*- coding: gb18030 -*-
import BigWorld
import csdefine 
import csconst
from bwdebug import *

class SpaceInfo( object ):
	def __init__( self, spaceKey, spaceID, startTime ):
		object.__init__( self )
		self.spaceKey = spaceKey
		self.spaceID = spaceID
		self.startTime = startTime
		self.memberNum = 0
	
	def convertToDict( self ):
		dict = {}
		dict[ "spaceID" ] = self.spaceID
		dict[ "spaceKey" ] = self.spaceKey
		dict[ "startTime" ] = self.startTime
		dict[ "memberNum" ] = self.memberNum
		return dict

class SpaceInfos( object ):
	def __init__( self, spaceKey ):
		object.__init__( self )
		self.spaceKey = spaceKey
		self.spaceCopyList = {}
	
	def addCopy( self, spaceID, time ):
		info = SpaceInfo( self.spaceKey, spaceID, time )
		self.spaceCopyList[ spaceID ] = info
	
	def playerEnterSpaceCopy( self, spaceID, playerMailbox ):
		self.spaceCopyList[ spaceID ].memberNum += 1
	
	def playerLeaveSpaceCopy( self, spaceID, playerMailbox ):
		if self.spaceCopyList.has_key( spaceID ):
			self.spaceCopyList[ spaceID ].memberNum -= 1
			if self.spaceCopyList[ spaceID ].memberNum < 0:
				self.spaceCopyList[ spaceID ].memberNum = 0
	
	def getDataForObj( self ):
		data = []
		for inf in self.spaceCopyList.itervalues():
			data.append( inf.convertToDict() )
		
		return data
	
class SpaceViewerMgr( BigWorld.Base ):
	def __init__( self ):
		BigWorld.Base.__init__( self )
		self.spaceInfos = {}
		self.registerGlobally( "SpaceViewerMgr", self._onRegisterManager )
	
	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register SpaceViewerMgr Fail!" )
			self.registerGlobally( "SpaceViewerMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["SpaceViewerMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("SpaceViewerMgr Create Complete!")
	
	def regist( self, spaceKey, spaceID, time ):
		if not self.spaceInfos.has_key( spaceKey ):
			infos = SpaceInfos( spaceKey )
			self.spaceInfos[ infos.spaceKey ] = infos
		
		self.spaceInfos[ spaceKey ].addCopy( spaceID, time )
	
	def playerEnterSpaceCopy( self, spaceKey, spaceID, time, playerMailbox ):
		# define method
		self.regist( spaceKey, spaceID, time )
		self.spaceInfos[ spaceKey ].playerEnterSpaceCopy( spaceID, playerMailbox )
		
	def playerLeaveSpaceCopy( self, spaceKey, spaceID, playerMailbox ):
		# define method
		if self.spaceInfos.has_key( spaceKey ):
			self.spaceInfos[ spaceKey ].playerLeaveSpaceCopy( spaceID, playerMailbox )
		
	def requestSpaceInfos( self, spaceKey, playerMailbox ):
		# define method
		infos = []
		if self.spaceInfos.has_key( spaceKey ):
			infos = self.spaceInfos[ spaceKey ].getDataForObj()

		playerMailbox.client.spaceViewerOnReInfos( infos )