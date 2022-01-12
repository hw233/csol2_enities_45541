# -*- coding: gb18030 -*-
import time
import uuid
import random

import BigWorld
import csstatus
from bwdebug import *

LINE_TIME = 60 * 30 # 排队时间

class ReqTeamInfos( object ):
	def __init__( self, teamMB, level, camp ):
		self.teamMB = teamMB
		self.level = level
		self.camp = camp
	
	def notifyOpenCopy( self, teamMB ):
		# 匹配成功，通知集合
		self.teamMB.yingXiongCampReqSucceed( teamMB )
	
	def getTeamID( self ):
		return self.teamMB.id

class CampYingXiongCopyMgr:
	# 英雄联盟副本管理器
	def __init__( self ):
		self.yingXiong_reqList = []
		self.yingXiong_matchTimers = {}
	
	def yingXiong_req( self, baseEntity, teamMailBox, level, camp ):
		"""
		define method
		"""
		for i in self.yingXiong_reqList:
			if teamMailBox.id == i.getTeamID():
				baseEntity.client.onStatusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_HAVE_JOIN,"" )
				return
				
		self.yingXiong_reqList.append( ReqTeamInfos( teamMailBox, level, camp ) )
		teamMailBox.yingXiongCampOnReq()
		self.yingXiong_startMatching()
		timerID = self.addTimer( LINE_TIME, 0, teamMailBox.id  )
		self.yingXiong_matchTimers[ timerID ] = teamMailBox.id
	
	def yingXiong_cancel( self,  tid, isMatch ):
		"""
		define method.
		取消排队
		"""
		for t in self.yingXiong_reqList:
			if t.teamMB.id == tid:
				self.yingXiong_reqList.remove( t )
				t.teamMB.yingXiongCampOnCancel( isMatch )
				break

	def yingXiong_startMatching( self ):
		"""
		开始匹配
		"""
		if len( self.yingXiong_reqList ) < 2:
			return
		
		matchTeam = self.yingXiong_reqList[ 0 ]
		self.__match( matchTeam )
	
	def __match( self, matchTeam ):
		isMatchSucceedOne = False
		for t in self.yingXiong_reqList:
			if matchTeam == t:
				continue
				
			if abs( t.level - matchTeam.level ) <= 3 and matchTeam.camp != t.camp:
				matchTeam.notifyOpenCopy( t.teamMB )
				t.notifyOpenCopy( matchTeam.teamMB )
				self.yingXiong_cancel( t.teamMB.id, True )
				self.yingXiong_cancel( matchTeam.teamMB.id, True )
				isMatchSucceedOne = True
				break
				
		if isMatchSucceedOne:
			self.yingXiong_startMatching()
	
	def onTimer( self, id, userArg ):
		if self.yingXiong_matchTimers.has_key( id ):
			self.yingXiong_cancel( self.yingXiong_matchTimers[ id ], False )