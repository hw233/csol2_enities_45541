# -*- coding: gb18030 -*-
#

"""
"""
import time
import BigWorld
import csdefine
import csconst
from bwdebug import *
from SpaceCopy import SpaceCopy
import Const
import csstatus
from DanceKingInfos import DanceKingData

class SpaceCopyDanceHall( SpaceCopy ):
	def __init__(self):
		SpaceCopy.__init__(self)
		self.spawnPointBases = {}
		
	def setDanceHallInfo(self, index, dbid, modelInfo):
		#define method
		param = ( dbid, self.spaceNumber, index, modelInfo )
		BigWorld.globalData["DanceMgr"].setDanceHallInfo(param)
		
	def registerDanceKingSpawnPoint(self, locationIndex, spawnpointDancekingBase):
		#define method
		#1到19是舞王的，20到39是当前副本的普通位置的
		self.spawnPointBases.update({locationIndex: spawnpointDancekingBase})
		if len(self.spawnPointBases.keys()) == 39:#表明刷新点加载完毕,注册base到管理器
			INFO_MSG("SpaceCopyDanceHall spaceNumber[%d] add 39 spawnpoints over.they are %s"%(self.spaceNumber,self.spawnPointBases))
			BigWorld.globalData["DanceMgr"].registerDanceHallBase(self.base)  #创建时注册到管理器，统一管理
	
	def spawnDanceKing( self, index, modelInfo ):
		#define method
		if self.spawnPointBases.has_key(index):
			if modelInfo:
				self.spawnPointBases[index].cell.remoteCallScript( "spawnNPCDanceKing", [ self.getDanceKingObj(modelInfo) ] )
			else:
				self.spawnPointBases[index].cell.remoteCallScript( "spawnNoNpcDanceKing", [] )
					
	def getDanceKingObj(self, roleInfo):
		obj = DanceKingData()
		obj[ "uname" ] = roleInfo["roleName"]		
		obj[ "level" ] = roleInfo["level"]
		obj[ "tongName" ] = roleInfo["tongName"]
		obj[ "raceclass" ] = roleInfo["raceclass"]
		obj[ "hairNumber" ] = roleInfo["hairNumber"]
		obj[ "faceNumber" ] = roleInfo["faceNumber"]
		obj[ "bodyFDict" ] = roleInfo["bodyFDict"]
		obj[ "volaFDict" ] = roleInfo["volaFDict"]
		obj[ "breechFDict" ] = roleInfo["breechFDict"]
		obj[ "feetFDict" ] = roleInfo["feetFDict"]
		obj[ "lefthandFDict" ] = roleInfo["lefthandFDict"]
		obj[ "righthandFDict" ] = roleInfo["righthandFDict"]
		obj[ "talismanNum" ] = roleInfo["talismanNum"]
		obj[ "fashionNum" ] = roleInfo["fashionNum"]
		obj[ "adornNum" ] = roleInfo["adornNum"]
		obj[ "headTextureID" ] = roleInfo["headTextureID"]	
		return obj	
			
	def onDestroy( self ):
		"""
		cell 被删除时发生
		"""
		BigWorld.globalData["DanceMgr"].removeDanceHallBase(self.base)  #销毁时，在管理器中去掉
		SpaceCopy.onDestroy( self )
	
		
		
