# -*- coding: gb18030 -*-

from bwdebug import *
import BigWorld
import Const
import ECBExtend
import csdefine
import csstatus

import csconst

# 临时退出副本的位置
TEMP_FORET_POSITION = ( 98.295, 12.108, 135.196 )
TEMP_FORET_DIRECTION = ( 0, 0, 0.1964 )
TEMP_FORET_SPACE = "fengming"



class RoleShuijingSpaceInterface:
	# 水晶副本的接口
	def __init__( self ):
		pass
	
	def shuijingSpaceOnStart( self, shuijingKey, checkPoint, spaceName, enterPosition, enterDirection ):
		if self.isInTeam():
			self.addActivityCount( csdefine.ACTIVITY_SHUI_JING )
		
		self.shuijingKey = shuijingKey
		self.shuijingSpaceGoToCheckPoint( checkPoint, spaceName, enterPosition, enterDirection )
		
	def shuijingSpaceGoToCheckPoint( self, checkPoint, spaceName, enterPosition, enterDirection ):
		self.set( "shuijing_checkPoint", checkPoint )
		self.gotoSpace( spaceName, enterPosition, enterDirection )
	
	def shuijingSpaceIsTimeOut( self ):
		self.shuijingKey = ""
	
	def shuijingSpacePassDoor( self ):
		if self.shuijingKey:
			BigWorld.globalData[ "ShuijingManager" ].passCheckPointDoor( self.shuijingKey )
		else:
			ERROR_MSG( "player id is %s,shuijingKey is %s"%( self.id, self.shuijingKey ) )
			
	def shuijingSpaceOnEnd( self ):
		self.remove("shuijing_checkPoint" )
		self.shuijingKey = ""
		self.gotoSpace( TEMP_FORET_SPACE, TEMP_FORET_POSITION, TEMP_FORET_DIRECTION )

	def shuiJingGetRevivePosition( self, spaceLabel ):
		spaceEntity = BigWorld.entities.get( self.getCurrentSpaceBase().id, None )
		if spaceEntity:
			pos = spaceEntity.getScript().getRevivePosition( spaceEntity )
			return pos
		else:
			return ( 0, 0, 0 )
