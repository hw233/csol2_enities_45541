# -*- coding: gb18030 -*-

# NPCAccumLoader.py, 2012-09-06  added by dqh

import Language
from bwdebug import *

class DestransDatasLoader:
	"""
	棋盘数据加载器
	"""
	_instance = None
	_configPath = "config/client/DestransClientDatas.xml"
	
	def __init__( self ):
		assert DestransDatasLoader._instance is None
		DestransDatasLoader._instance = self
		self._datas = {}
		self._desDatas = {}
		self._loadConfig( self._configPath )
	
	def _loadConfig( self, configPath ):
		section = Language.openConfigSection( configPath )
		if section is None:return
		for node in section.values():
			boardNum = node.readInt( "boardNum" )
			index = node.readInt( "index" )
			piece = {}
			piece["evtID"] = node.readInt( "evtID" )
			piece["top"] = node.readInt( "top" )
			piece["bottom"] = node.readInt( "bottom" )
			piece["left"] = node.readInt( "left" )
			piece["right"] = node.readInt( "right" )
			piece["steps"] = self.__getSteps( node )
			piece["describe"] = node.readString( "describe" )
			if boardNum in self._datas:
				self._datas[boardNum].update( {index:piece} )
			else:
				self._datas[boardNum] = {index:piece}
		Language.purgeConfig( configPath )
	
	def __getSteps( self, node ):
		steps = []
		stepStr = node.readString("steps")
		if len( stepStr ) > 0:
			numbers = stepStr.split("|")
			for number in numbers:
				if number == "":continue
				steps.append( int(number ) )
		return steps
	
	def getPieces( self, boardNum ):
		"""
		获取某个棋盘信息
		"""
		try: 
			return self._datas[boardNum]
		except KeyError:
			return None
	
	def getDescribe( self, boardNum, index ):
		"""
		获取事件描述
		"""
		pieceDatas = self.getPieces( boardNum )
		if pieceDatas is None:return ""
		piece = pieceDatas.get( index, None )
		if piece is None:return ""
		return piece["describe"]
	
	def getPieceInfo( self, boardNum, step ):
		"""
		获取某个棋盘信息
		"""
		pieces = self.getPieces( boardNum )
		if pieces:
			for index, piece in pieces.items():
				if step in piece["steps"]:
					return ( index, piece )

	@staticmethod
	def instance():
		"""
		"""
		if DestransDatasLoader._instance is None:
			DestransDatasLoader._instance = DestransDatasLoader()
		return DestransDatasLoader._instance

destransDatasLoader = DestransDatasLoader.instance()