# -*- coding: gb18030 -*-

import random
import Language
from bwdebug import *
from SpaceCopyTeam import SpaceCopyTeam

class SpaceCopyDestinyTrans( SpaceCopyTeam ):
	"""
	天命轮回副本
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopyTeam.__init__( self )
		self.enterPos = ()
		self.enterDir = ()
		self.spawnFileList = []
		self.bossID = ""
		self._spawnFile = ""

	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		SpaceCopyTeam.load( self, section )
		enterPos = section[ "Space" ][ "enterPos" ]
		self.enterPos = eval( enterPos[ "pos" ].asString )
		self.enterDir = eval( enterPos[ "direction" ].asString )
		if section[ "Space" ].has_key( "bossID"):
			self.bossID = section[ "Space" ][ "bossID" ].readString( "className" )
		
		if not section[ "Space" ].has_key("spawn"):
			ERROR_MSG( "SpaceCopyDestinyTrans:spawn config is None." )
		else:
			for file in section[ "Space" ]["spawn"].values():
				if not file.has_key("spawnFile"):
					ERROR_MSG( "SpaceCopyDestinyTrans:spawnFile config is None." )
					break
				self.spawnFileList.append( file["spawnFile"].asString )

		self.registerSelfToMgr()
		
	def registerSelfToMgr( self ):
		"""
		把自己注册到管理器
		"""
		if BigWorld.globalData.has_key( "SpaceDestinyTransMgr" ):
			BigWorld.globalData["SpaceDestinyTransMgr"].registerSpaceInfo( self.className, self.enterPos, self.enterDir, self.bossID )
		else: #如果管理器没启动
			destinyTransSpaceList = []
			destinyTransSpaceList.append( ( self.className, self.enterPos, self.enterDir, self.bossID ) )
			if BigWorld.globalData.has_key( "DestinyTransSpaceList" ):
				destinyTransSpaceList.extend( BigWorld.globalData[ "DestinyTransSpaceList" ] )
			
			BigWorld.globalData["DestinyTransSpaceList"] = destinyTransSpaceList

	def getSpaceSpawnFile( self, selfEntity ):
		"""
		获取出生点文件
		"""
		if not self._spawnFile:
			self._spawnFile = random.sample( self.spawnFileList, 1 )[0]
		INFO_MSG( " spawnFile is %s " % self._spawnFile )
		return self._spawnFile

	def getSpawnSection( self ):
		"""
		"""
		return Language.openConfigSection( self._spawnFile )