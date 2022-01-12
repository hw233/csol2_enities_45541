# -*- coding: gb18030 -*-
# debug toolkit by mushuang 

"""
get( id )���൱��BigWorld.entities[id]

getSpaceName( spaceType )�����ݿռ����ͻ�ȡ���Ŀռ��������磺getSpaceName( "fengming" )

getSpaceTypeAndNpcPos( npcID )������npcID�ҳ�npc���ĸ��ռ��ʲô�ط������磺getSpaceTypeAndNpcPos( "123456" )

queryAct( talkKey )������talkKey��talkFunction�ؼ��֣��ҳ��ṩ�����npc���ĸ���ͼ��ʲôλ�ã����磺queryAct( "enterBeforeNirvana" )(�ҳ�����10������npc��ʲôλ��)

clearSpawnPoint()���������spawnPoint

listSpawnPoint()���г���ǰ�г�����ĵ�ͼ

listSpaceType()���г����пռ��������Ӧ��������

setSpawnPoint( spaceType )������ĳ����ͼ�ĳ����㣬����setSpawnPoint( "fengming" )���ɹ��᷵��True
"""

import BigWorld
from Resource.FuncsModule import m_functions as actDict
import ResMgr
import Function
import os
from config.NPCDatas.NPCDatas import Datas as npcPosition

NPC_TALK_PATH = r"entities/locale_default/config/server/gameObject/NPCTalk.xml"
SPAWN_FILE_PATH = r"entities/locale_default/config/server/spawn"
SPACE_FILE_PATH = r"entities/locale_default/config/server/gameObject/space"
SPAWN_POINT_BK = r"spawnPoint.dat"
BIGMAP_PATH = r"entities/locale_default/config/client/bigmap/bigmaps.xml"


class Info:
	def __init__( self ):
		self.npcID = 0
		self.spaceType = ""
		self.spaceName = ""
		self.npcPos = ( 0, 0, 0 )
	def __str__( self ):
		if self.spaceName != "":
			fmtStr ="npcID:%s\nspaceType:%s\nspaceName:%s\nnpcPosition:%s\n"
			return fmtStr % ( self.npcID, self.spaceType, self.spaceName, self.npcPos )
			
		else :
			fmtStr ="npcID:%s\nspaceType:%s\nnpcPosition:%s\n"
			return fmtStr % ( self.npcID, self.spaceType, self.npcPos )

	
def getSpaceName( spaceType ):
	spaceFiles = Function.searchFile( SPACE_FILE_PATH, ".xml" )
	for spaceFile in spaceFiles:
		rootSection = ResMgr.openSection( spaceFile )
		# find in space files 
		if rootSection.has_key( "spaceName" ) and rootSection[ "className" ].asString == spaceType:
			return rootSection["spaceName"].asString
			
	# find in bigmap.xml
	rootSection = ResMgr.openSection( BIGMAP_PATH )
	for key,sect in rootSection.items():
		if key == spaceType:
			return sect.asString
	# there is no such spaceType really
	return ""


def getSpaceTypeAndNpcPos( npcID ):
	"""
	getSpaceTypeAndNpcPos( npcID ):
	@return: ( spaceType, npcPos )
	"""
	for spaceType,npcDict in npcPosition.iteritems():
		if str(npcID) in npcDict:
			npcPos = npcDict[ str(npcID) ][ "position" ]
			return ( spaceType, npcPos )
	return ( "UnknownSpaceType", ( 0, 0, 0 ) )

def queryAct( actKey ):
	"""
	queryAct( actKey ):
	"""
	actKey = actKey.strip()
	if not actKey in actDict :
		return False
	npcTalk = ResMgr.openSection( NPC_TALK_PATH )
	npcID = 0
	for section in npcTalk.values():
		npcID = section[ "npcID" ].asInt
		for item in section[ "talks" ].values():
			if item.has_key( "functions" ):
				for it in item[ "functions" ].values():
					if it[ "key" ].asString == actKey:
						result = Info()
						result.npcID = npcID						
						result.spaceName = getSpaceName( result.spaceType )
						( result.spaceType, result.npcPos ) = getSpaceTypeAndNpcPos( npcID )
						print result
						return result.npcPos
						
						
						
def get(id):
	"""
	get(id)
	@return: Entity reference
	"""
	return BigWorld.entities[id]

def clearSpawnPoint():
	"""
	clearSpawnPoint():
	@use: clear all spawn point in all maps
	"""
	spaceFiles = Function.searchFile( SPACE_FILE_PATH, ".xml" )
	fs = open( SPAWN_POINT_BK, "a" )
	for spaceFile in spaceFiles:
		rootSection = ResMgr.openSection( spaceFile )
		if rootSection.has_key( "spawnFile" ) and rootSection[ "spawnFile" ].asString != "" :
			fs.write( rootSection["className"].asString + " " + rootSection[ "spawnFile" ].asString + "\n" )
			rootSection[ "spawnFile" ].asString = ""
			rootSection.save()
			print rootSection["className"].asString, "purged!"
	fs.close()

def listSpawnPoint():
	spaceFiles = Function.searchFile( SPACE_FILE_PATH, ".xml" )
	for spaceFile in spaceFiles:
		rootSection = ResMgr.openSection( spaceFile )
		if rootSection.has_key( "spawnFile" ) and rootSection[ "spawnFile" ].asString != "":
			print rootSection["className"].asString, rootSection["spawnFile"].asString

def listSpaceType():
	spaceFiles = Function.searchFile( SPACE_FILE_PATH, ".xml" )
	spaces = {} # spaceType:spaceName
	for spaceFile in spaceFiles:
		rootSection = ResMgr.openSection( spaceFile )
		spaces[ rootSection["className"].asString ] = getSpaceName( rootSection["className"].asString )
	
	for k,v in spaces.iteritems():
		print k,v

def setSpawnPoint( spaceType ):
	"""
	setSpawnPoint( spaceType )
	@use: active spawn point in a specified map
	"""
	spaceFiles = Function.searchFile( SPACE_FILE_PATH, ".xml" )
	
	spawnDict = {}
	for spaceFile in spaceFiles:
		rootSection = ResMgr.openSection( spaceFile )
		spawnDict[ rootSection[ "className" ].asString ] = spaceFile
		if rootSection[ "className" ] == spaceType and rootSection.has_key( "spawnFile" ) and rootSection[ "spawnFile" ].asString != "":
			return True
	
	if not spaceType in spawnDict: return False	
	
	# find out spawn point record in backup file
	fs = open( SPAWN_POINT_BK, "a+" )
	lines = fs.readlines()
	className = ""
	spawnFile = ""
	for line in lines:
		className,spawnFile = line.split()
		if className == spaceType:
			rootSection = ResMgr.openSection( spawnDict[ spaceType ] )
			rootSection[ "spawnFile" ].asString = spawnFile
			rootSection.save()
			
			# update backup file, removing corresponding line from it
			fs.truncate(0)
			for line in lines:
				className,spawnFile = line.split()
				if className == spaceType: continue
				fs.write( line )
			fs.close()
			return True
	
	fs.close()
	return False


