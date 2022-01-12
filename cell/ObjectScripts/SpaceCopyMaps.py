# -*- coding: gb18030 -*-
import time

import BigWorld

import csstatus
import csconst
import csdefine
import Const
from bwdebug import *
from SpaceCopy import SpaceCopy

TIMER_CLOSE_ACT = 1

class SpaceCopyMaps( SpaceCopy ):
	"""
	多地图单人副本脚本
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopy.__init__( self )
		self._spaceMapsInfos = []
		self._spaceMapsNo = 0
		self._spaceLife = 1
		self._closeTime = 1
		self._door = []
		self._doorPosition = ( 0,0, 0)
		self._isPickMembers = 0
		self._copyBossNum = 0
		self._copyMonsterNum = 0
		self._curBossNum  = 0
		self._curMonsterNum = 0
		self._bossID = []
		
		self.difficulty = 0
	
	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopy.load( self, section )
		for idx, item in enumerate( section[ "Space" ][ "spaceMapsInfos" ].values() ):
			className = item[ "className" ].asString
			pos = tuple( [ float(x) for x in item["position"].asString.split() ] )
			direction = tuple( [ float(x) for x in item["direction"].asString.split() ] )
			self._spaceMapsInfos.append( ( className, pos, direction ) )
			if className == self.className:
				self._spaceMapsNo = idx
		
		self._spaceLife = section[ "Space" ][ "spaceLife" ].asInt  # 副本时间(分钟)
		self.difficulty = section[ "Space" ][ "difficulty" ].asInt  # 副本难度
		self._closeTime = section[ "Space" ][ "closeTime" ].asInt  # 副本关闭时间（秒）
				
		self._copyBossNum = section[ "Space" ][ "copyBossNum" ].asInt
		self._copyMonsterNum = section[ "Space" ][ "copyMonsterNum" ].asInt
		self._curBossNum = section[ "Space" ][ "curBossNum" ].asInt
		self._curMonsterNum = section[ "Space" ][ "curMonsterNum" ].asInt
		self._bossID = section[ "Space" ][ "bossID" ].asString.split(";")
		
		# 初始化传送门数据
		if section[ "Space" ].has_key( "doorPoint" ):
			for item in section[ "Space" ][ "doorPoint" ].values():
				doorPro = {}
				doorPro[ "isCreate" ] = item[ "isCreate" ].asInt
				doorPro[ "pos" ] = tuple( [ float(x) for x in item.readString( "pos" ).split() ] )
				doorPro[ "useRectangle" ] = item.readInt( "properties/useRectangle" )
				doorPro[ "radius" ] = item.readFloat( "properties/radius" )
				doorPro[ "volume" ] = item.readVector3( "properties/volume" )
				doorPro[ "modelNumber" ] = item.readString( "properties/modelNumber" )
				doorPro[ "modelScale" ] = item.readFloat( "properties/modelScale" )
				doorPro[ "destSpace" ] = item.readString( "properties/destSpace" )
				
				destPosition = item.readString( "properties/destPosition" )
				doorPro[ "destPosition" ] = tuple( [ float(x) for x in destPosition.split() ] )
				destDirection = item.readString( "properties/destDirection" )
				doorPro[ "destDirection" ] = tuple( [ float(x) for x in destDirection.split() ] )
				
				doorPro[ "nickname" ] = item.readString( "properties/nickname" )
				doorPro[ "uname" ] = item.readString( "properties/uname" )
				self._door.append( doorPro )
	
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		用我自己的数据初始化参数 selfEntity 的数据
		"""
		SpaceCopy.initEntity( self, selfEntity )
		selfEntity.setTemp( "bossCount", self._curBossNum )
		selfEntity.setTemp( "allMonsterCount", self._curMonsterNum )
		life = self._spaceLife * 60 - ( time.time() - selfEntity.createTime )
		selfEntity.addTimer( life, 0, Const.SPACE_TIMER_ARG_LIFE )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, self._copyBossNum - selfEntity.copyStatBoss )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, self._copyMonsterNum - selfEntity.copyStatMonster )
		self.createDoor( selfEntity, True )
	
	def packedDomainData( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		@param entity: 通常为玩家
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		# 返回databaseID，这样space domain能够此数据正确的记录副本的创建者，
		# 且不用担心玩家在短时间内（断）下线后重上时找回副本的问题；
		d = { 'dbID' : entity.databaseID }
		d[ "enterCopyKey" ] = self.className
		d[ "enterCopyNo" ] = self._spaceMapsNo
		return d
	
	def getSpaceBirth( self, gNo = 0 ):
		"""
		获取出生位置
		"""
		return self._spaceMapsInfos[ gNo ]
	
	def getCopyNo( self ):
		"""
		获取当前的地图的编号
		"""
		return self._spaceMapsNo
	
	def getNextSpace( self ):
		"""
		传送到下一张地图
		"""
		if len( self._spaceMapsInfos ) == self._spaceMapsNo:
			return -1
		
		return self._spaceMapsInfos[ self._spaceMapsNo + 1 ]
	
	def createDoor( self, selfEntity, isInit ):
		"""
		创建通往下一张地图的传送门
		"""
		for item in self._door:
			if item[ "isCreate" ] == isInit:
				e = BigWorld.createEntity( "SpaceDoor", selfEntity.spaceID, item[ "pos" ], (0, 0, 0), item )
				if e != None:
					e.modelScale = item[ "modelScale" ]
		
	def onCloseMapsCopy( self, selfEntity ):
		"""
		关闭多地图副本入口
		"""
		for e in selfEntity._players:
			e.client.onStatusMessage( csstatus.SPACE_CLOSE, str( ( self._closeTime, ) ) )
			
		selfEntity.addTimer( self._closeTime, 0.0, Const.SPACE_TIMER_ARG_KICK )
		selfEntity.addTimer( self._closeTime + 5, 0.0, Const.SPACE_TIMER_ARG_CLOSE )
	
	def closeMapsCopy( self, playerEntity ):
		"""
		关闭多地图副本入口(玩家调用)
		"""
		if BigWorld.cellAppData.has_key( selfEntity.getSpaceGlobalKey() ):
			del BigWorld.cellAppData[ selfEntity.getSpaceGlobalKey() ]
			
		BigWorld.globalData[ "SpaceManager" ].remoteCallDomain( self.className, "closeCopyItem", ( { "dbID": playerEntity.databaseID } ) )
	
	def onTimer( self, selfEntity, id, userArg ):
		"""
		时间控制器
		"""
		if userArg == Const.SPACE_TIMER_ARG_LIFE:
			selfEntity.domainMB.closeCopyItem( { "dbID": selfEntity.copyKey } )
		else:
			SpaceCopy.onTimer( self, selfEntity, id, userArg )
	
	def setCopyKillBoss( self, selfEntity, bossNum ):
		"""
		define method
		设置副本BOSS数量
		"""
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, self._copyBossNum - bossNum )
		
	def setCopyKillMonster( self, selfEntity, monsterNum ):
		"""
		define method
		设置副本小怪数量
		"""
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, self._copyMonsterNum - monsterNum )

	def onAllCopyMonsterkilled( self, selfEntity, spaceName ):
		"""
		副本中小怪全部被击杀
		"""
		pass