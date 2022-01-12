# -*- coding: gb18030 -*-

from bwdebug import *
import BigWorld
import random
import time

import csdefine
import csconst
import csstatus
import utils
import Const

from SpaceCopy import SpaceCopy

TIME_ARG_SECOND_ADD_SCORE = 1

SCORE_KILL		= 80	#击杀
SCORE_SECOND	= 1		#时间

class SpaceCopyAoZhan( SpaceCopy ):
	# 鏖战群雄
	def __init__( self ):
		SpaceCopy.__init__( self )

	def onEnterCommon( self, baseMailbox, params ):
		"""
		进入
		"""
		SpaceCopy.onEnterCommon( self, baseMailbox, params )
		self.battleData.regitsterMB( params[ "databaseID" ], baseMailbox )
	
	def activityStart( self ):
		"""
		define method.
		活动开始
		"""
		self.userTime = time.time()
		enterNum = self.battleData.getEnterNum()
		if enterNum > 1:
			self.addTimer( 1.0, 1.0, TIME_ARG_SECOND_ADD_SCORE )
			self.getScript().activityStart( self )
			aPlayer = self.__convertToEntity( self.battleData.aPlayer.mailBox )
			bPlayer = self.__convertToEntity( self.battleData.bPlayer.mailBox )
			if aPlayer:
				aPlayer.position = ( -2.178, 9.063, 40.911 )
			if bPlayer:
				bPlayer.position = ( -2.178, 9.063, -8.099 )
			
			for f in self.battleData.failureList:
				if f.mailBox:
					fPlayer = self.__convertToEntity( f.mailBox )
					if fPlayer:
						fPlayer.position = ( -2.178, 9.063, -8.099 )
			
		else:
			if enterNum == 0:#全不进
				if self.matchType == csdefine.AO_ZHAN_ROOM_TYPE_NO_FAILURE:
					winner = random.choice( [ self.battleData.aPlayer.dbid, self.battleData.bPlayer.dbid ] )
					BigWorld.globalData[ "AoZhanQunXiongMgr" ].setResult( self.enterNumber, winner, 0, 0.0, 0 )
				else:
					BigWorld.globalData[ "AoZhanQunXiongMgr" ].setResult( self.enterNumber, 0, 0, 0.0, 0 )
					
			elif enterNum == 1:#只进1方
				if self.matchType == csdefine.AO_ZHAN_ROOM_TYPE_NO_FAILURE: #没有失败组比赛
					if self.battleData.aPlayer.mailBox:
						aPlayer = self.__convertToEntity( self.battleData.aPlayer.mailBox )
						remainHP = 0
						if aPlayer:
							remainHP = aPlayer.HP
						BigWorld.globalData[ "AoZhanQunXiongMgr" ].setResult( self.enterNumber, self.battleData.aPlayer.dbid, self.score, 0.0, remainHP )
					else:
						bPlayer = self.__convertToEntity( self.battleData.bPlayer.mailBox )
						remainHP = 0
						if bPlayer:
							remainHP = bPlayer.HP
						BigWorld.globalData[ "AoZhanQunXiongMgr" ].setResult( self.enterNumber, self.battleData.bPlayer.dbid, self.score, 0.0, remainHP )
				else:#不是1V1的比赛
					if self.battleData.aPlayer.mailBox:
						aPlayer = self.__convertToEntity( self.battleData.aPlayer.mailBox )
						remainHP = 0
						if aPlayer:
							remainHP = aPlayer.HP
						BigWorld.globalData[ "AoZhanQunXiongMgr" ].setResult( self.enterNumber, self.battleData.aPlayer.dbid, self.score, 0.0, remainHP )
			
			for e in self._players:
				e.client.onStatusMessage( csstatus.AO_ZHAN_QUN_XIONG_NOT_ENTER, "" )
				
			self.getScript().closeActivity( self )


	def closeActivity( self ):
		"""
		define method
		关闭活动
		"""
		self.getScript().closeActivity( self )
		if self.matchType == csdefine.AO_ZHAN_ROOM_TYPE_NO_FAILURE: #是否第一轮
			aPlayer = self.__convertToEntity( self.battleData.aPlayer.mailBox )
			bPlayer = self.__convertToEntity( self.battleData.bPlayer.mailBox )
			useTime = time.time() - self.userTime
			if aPlayer and bPlayer:
				if aPlayer.HP > bPlayer.HP:
					BigWorld.globalData[ "AoZhanQunXiongMgr" ].setResult( self.enterNumber, self.battleData.aPlayer.dbid, self.score, useTime, aPlayer.HP )
				else:
					BigWorld.globalData[ "AoZhanQunXiongMgr" ].setResult( self.enterNumber, self.battleData.bPlayer.dbid, self.score, useTime, bPlayer.HP )
			elif aPlayer:
				BigWorld.globalData[ "AoZhanQunXiongMgr" ].setResult( self.enterNumber, self.battleData.aPlayer.dbid, self.score, useTime, aPlayer.HP )
			elif bPlayer:
				BigWorld.globalData[ "AoZhanQunXiongMgr" ].setResult( self.enterNumber, self.battleData.bPlayer.dbid, self.score, useTime, bPlayer.HP )
			else:
				BigWorld.globalData[ "AoZhanQunXiongMgr" ].setResult( self.enterNumber, 0, 0, 0.0, 0 )
	
	def onRoleBeKill( self, diePlayer, killerBase ):
		"""
		define method
		有玩家被击杀
		"""
		useTime = time.time() - self.userTime
		if self.matchType == csdefine.AO_ZHAN_ROOM_TYPE_NO_FAILURE:
			if self.battleData.aPlayer.mailBox.id == diePlayer.id:
				bPlayer = self.__convertToEntity( self.battleData.bPlayer.mailBox )
				remainHP = 0
				if bPlayer:
					remainHP = bPlayer.HP
					
				BigWorld.globalData[ "AoZhanQunXiongMgr" ].setResult( self.enterNumber, self.battleData.bPlayer.dbid, self.score, useTime, remainHP )
				self.getScript().closeActivity( self )
				self.matchEnd = True
				return
			
			elif self.battleData.bPlayer.mailBox.id == diePlayer.id:
				aPlayer = self.__convertToEntity( self.battleData.aPlayer.mailBox )
				remainHP = 0
				if aPlayer:
					remainHP = aPlayer.HP
					
				BigWorld.globalData[ "AoZhanQunXiongMgr" ].setResult( self.enterNumber, self.battleData.aPlayer.dbid, self.score, useTime, remainHP )
				self.getScript().closeActivity( self )
				self.matchEnd = True
				return
		else:
			if self.battleData.aPlayer.mailBox.id == diePlayer.id:
				aPlayer = self.__convertToEntity( self.battleData.aPlayer.mailBox )
				remainHP = 0
				if aPlayer:
					remainHP = aPlayer.HP
					
				BigWorld.globalData[ "AoZhanQunXiongMgr" ].setResult( self.enterNumber, 0, self.score, useTime, remainHP )
				self.getScript().closeActivity( self )
				self.matchEnd = True
				return
			else:
				for i, f in enumerate( self.battleData.failureList ):
					if f.mailBox.id == diePlayer.id:
						self.score += SCORE_KILL
						self.gFailureDieNum +=1
						break
						
				if self.gFailureDieNum >= len( self.battleData.failureList ):
					self.getScript().closeActivity( self )
					self.matchEnd = True
						
	def __convertToEntity( self, mailBox ):
		if mailBox:
			return BigWorld.entities.get( mailBox.id, None )
		
		return None
	
	def playerExit( self, pMB ):
		"""
		define method
		玩家退出
		"""
		if self.matchEnd:
			return
		
		useTime = time.time() - self.userTime
		if self.matchType == csdefine.AO_ZHAN_ROOM_TYPE_NO_FAILURE:
			if self.battleData.aPlayer.mailBox.id == playerMB.id:
				bPlayer = self.__convertToEntity( self.battleData.bPlayer.mailBox )
				remainHP = 0
				if bPlayer:
					remainHP = bPlayer.HP
					
				BigWorld.globalData[ "AoZhanQunXiongMgr" ].setResult( self.enterNumber, self.battleData.bPlayer.dbid, self.score, useTime, remainHP )
				self.getScript().closeActivity( self )
				self.matchEnd = True
				return
			
			elif self.battleData.bPlayer.mailBox.id == playerMB.id:
				aPlayer = self.__convertToEntity( self.battleData.aPlayer.mailBox )
				remainHP = 0
				if bPlayer:
					remainHP = aPlayer.HP
					
				BigWorld.globalData[ "AoZhanQunXiongMgr" ].setResult( self.enterNumber, self.battleData.aPlayer.dbid, self.score, useTime, remainHP )
				self.getScript().closeActivity( self )
				self.matchEnd = True
				return
		
		else:
			if self.battleData.aPlayer.mailBox.id == playerMB.id:
				aPlayer = self.__convertToEntity( self.battleData.aPlayer.mailBox )
				remainHP = 0
				if aPlayer:
					remainHP = aPlayer.HP
					
				BigWorld.globalData[ "AoZhanQunXiongMgr" ].setResult( self.enterNumber, 0, self.score, useTime, remainHP )
				self.getScript().closeActivity( self )
				self.matchEnd = True
				return
			else:
				for i, f in enumerate( self.battleData.failureList ):
					if f.mailBox.id == playerMB.id:
						del self.battleData.failureList[ i ]
	
	def onTimer( self, timerID, timerArg ):
		if timerArg == TIME_ARG_SECOND_ADD_SCORE:
			if not self.matchEnd:
				self.score += SCORE_SECOND
				
		SpaceCopy.onTimer( self, timerID, timerArg )