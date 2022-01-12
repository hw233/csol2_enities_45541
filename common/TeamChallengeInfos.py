# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
	
class TeamChallengeInfos:
	"""
	组队擂台队伍数据
	"""
	def __init__( self ):
		self.infos = {}
		self.dbidToMailBox = {}
		
	def instance( self, dict ):
		teamInfos = dict[ "infos" ]
		for info in teamInfos:
			self.infos[ info[ "teamID" ] ] = info[ "playerIDs" ]
		
		dbidInfos = dict[ "dbidToMailBox" ]
		for info in dbidInfos:
			self.dbidToMailBox[ info[ "playerDBID" ] ] = info[ "playerBase" ]
	
	def add( self, teamID, playerDBID, playerBase ):
		if self.infos.has_key( teamID ):
			if playerDBID not in self.infos[ teamID ]:
				self.infos[ teamID ].append( playerDBID )
		else:
			self.infos[ teamID ] = [ playerDBID, ]
		
		
		if not self.dbidToMailBox.has_key( playerDBID ):
			self.dbidToMailBox[ playerDBID ] = playerBase
	
	def remove( self, teamID, playerDBID ):
		if self.infos.has_key( teamID ):
			if playerDBID in self.infos[ teamID ]:
				self.infos[ teamID ].remove( playerDBID )
		else:
			for teamID, dbIDs in self.infos.iteritems():
				if playerDBID in dbIDs:
					dbIDs.remove( playerDBID )
		
		if self.dbidToMailBox.has_key( playerDBID ):
			self.dbidToMailBox.pop( playerDBID )
	
	def findTeamID( self, playerDBID ):
		for teamID, dbIDs in self.infos.iteritems():
			if playerDBID in dbIDs:
				return teamID
		
		return None
	
	def __getitem__( self, teamID ):
		return self.infos[ teamID ]
			
	def getDictFromObj( self, obj ):
		dict = {}
		teamInfos = []
		for teamID, dbIDs in obj.infos.iteritems():
			teamDict = {}
			teamDict[ "teamID" ] = teamID
			teamDict[ "playerIDs" ] = dbIDs
			teamInfos.append( teamDict )
		
		dict[ "infos" ] = teamInfos
		
		dbidInfos = []
		for dbid, mailBox in obj.dbidToMailBox.iteritems():
			dbidDict = {}
			dbidDict[ "playerDBID" ] = dbid
			dbidDict[ "playerBase" ] = mailBox
			dbidInfos.append( dbidDict )
		
		dict[ "dbidToMailBox" ] = dbidInfos
		return dict
		
	def createObjFromDict( self, dict ):
		obj = TeamChallengeInfos()
		obj.instance( dict )
		return obj
	
	def isSameType( self, obj ):
		return isinstance( obj, TeamChallengeInfos )
		
instance = TeamChallengeInfos()
