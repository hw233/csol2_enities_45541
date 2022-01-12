# -*- coding: gb18030 -*-

import BigWorld
import cschannel_msgs
import ShareTexts as ST
import Language
from bwdebug import *
import time
import Love3
import Const
import csstatus
from SpaceCopy import SpaceCopy
CITY_WAR_SPAWN_POINT = [ "SpawnPointCityWar", ] # 城战刷新点

class SpaceCopyCityWar( SpaceCopy ):
	# 帮会城市战
	def __init__(self):
		SpaceCopy.__init__( self )
		self.rightTongCount = 0
		self.leftTongCount = 0
		self.enterRecord = {}
		self.isClose = False
		self.bossBaseMB = None	# 只有统帅房间才有用
		self.cityWarSpawnPoint = []
		
	def onGetCell(self):
		# cell实体创建完成通知，回调callbackMailbox.onSpaceComplete，通知创建完成。
		SpaceCopy.onGetCell( self )
		if self.params.has_key( "CityWarLevelUp" ):
			self.cell.onCityWarLevelUp()
	
	def closeCityWarRoom( self ):
		# define method.
		# 提前结束掉某场战争 由tongmanager 关闭所有房间
		if self.isClose:
			return
			
		self.isClose = True
		self.onWarOver()
		self.cell.closeCityWarRoom()
	
	def checkNeedSpawn( self, sec ):
		if sec.readString( "type" ) in CITY_WAR_SPAWN_POINT:
			if self.getScript().getRoomLevel < 1:
				return False
				
			if not self.params.has_key( "defend" ):
				return False
			
			belong = sec[ "properties" ].readString( "belong" )
			if belong:
				belongTongDBID = self.params.get( belong ) # belong : left / right / defend
				if belongTongDBID:
					sec[ "properties" ].writeInt( "belongTongDBID", belongTongDBID )
				else:
					return False
		
		return SpaceCopy.checkNeedSpawn( self, sec )
	
	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		创建好了一个entity的通知
		@param	entityType		: entity的脚本类别
		@type 	entityType		: String
		@param	entity			: baseEntity实体
		"""
		if entityType in CITY_WAR_SPAWN_POINT:
			self.cityWarSpawnPoint.append( baseEntity )
	
	def onWarOver( self ):
		# define method
		# 城战结束，停止战争
		for spMailbox in self.cityWarSpawnPoint:
			spMailbox.cell.onCityWarOver()