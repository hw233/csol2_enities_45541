# -*- coding:gb18030 -*- 

import BigWorld
from Function import Function
import csdefine
import csconst

class FuncDartPointQuery( Function ):
	"""
	镖局积分查询
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		self.positiveTalk = section.readString( "param1" )	# 积分大于50的对话
		self.negativeTalk = section.readString( "param2" )	# 积分小于50的对话
		self.equalTalk = section.readString( "param3" )		# 积分等于50的对话
		
	def valid( self, playerEntity, talkEntity = None ):
		"""
		此对话只对分出阵营的玩家可见
		"""
		if playerEntity.hasFlag( csdefine.ROLE_FLAG_XL_DARTING ) or \
			playerEntity.hasFlag( csdefine.ROLE_FLAG_CP_DARTING ):
				return True
		return False
		
	def do( self, playerEntity, talkEntity ):
		"""
		"""
		dartPointDict = eval( BigWorld.getSpaceDataFirstForKey( playerEntity.spaceID, csconst.SPACE_SPACEDATA_DART_POINT ) )
		if playerEntity.hasFlag( csdefine.ROLE_FLAG_XL_DARTING ):
			point = dartPointDict[csdefine.ROLE_FLAG_XL_DARTING]
		else:
			point = dartPointDict[csdefine.ROLE_FLAG_CP_DARTING]
			
		if point > csconst.DART_INITIAL_POINT:
			talkContent = self.positiveTalk % point
		elif point < csconst.DART_INITIAL_POINT:
			talkContent = self.negativeTalk % point
		else:
			talkContent = self.equalTalk % point
		playerEntity.setGossipText( talkContent )
		playerEntity.sendGossipComplete( talkEntity.id )
		
class FuncDartSpaceInfoQuery( Function ):
	"""
	所在地图所发出的镖车数量查询
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		self.talkString = section.readString( "param1" )	# 查询结果对话内容
		
	def valid( self, playerEntity, talkEntity ):
		return True
		
	def do( self, playerEntity, talkEntity ):
		"""
		"""
		playerEntity.setTemp( "DartSpaceInfoQuery_talkNPCID", talkEntity.id )
		playerEntity.setTemp( "DartSpaceInfoQuery_talkString", self.talkString )
		spaceLabel = BigWorld.getSpaceDataFirstForKey( playerEntity.spaceID, csconst.SPACE_SPACEDATA_KEY )
		BigWorld.globalData['DartManager'].querySpaceDartInfo( playerEntity.base, spaceLabel, talkEntity.getFaction() )
		