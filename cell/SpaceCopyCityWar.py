# -*- coding: gb18030 -*-
import time

import BigWorld
import cschannel_msgs
import ShareTexts as ST
import csdefine
import csconst
import csstatus
from bwdebug import *
from SpaceCopy import SpaceCopy
from ObjectScripts.GameObjectFactory import g_objFactory
OCCUPY_NUMS_SKILL_ID = 323187001
OCCUPY_NUMS_BUFF_ID_1  = 62004
OCCUPY_NUMS_BUFF_ID_2  = 1010

TIMER_ARGS_ADD_INTEGRAL = 100001

class SpaceCopyCityWar( SpaceCopy ):
	# 帮会城市战
	def __init__( self ):
		self.setTemp( "isCurrentCityWarOver", False )
		if self.getScript().roomLevel > 0:
			self.setTemp( "isBossDie", False )
			
		SpaceCopy.__init__( self )

	def closeCityWarRoom( self ):
		# 房间关闭
		if self.isOverCityWar():
			return
			
		winner = 0
		cityName = self.params[ "cityName" ]
		leftIntegral = self.warInfos.getIntegral( self.params[ "left" ] ) # 取出帮会的积分
		rightIntegral = self.warInfos.getIntegral( self.params[ "right" ] ) # 取出帮会的积分
		if self.params.has_key( "defend" ):
			if not self.queryTemp( "isBossDie" ): # 若是BOSS没死，则防守方胜利
				winner = self.params[ "defend" ]
			else:
				if leftIntegral == rightIntegral:
					winner = self.warInfos.winner
				elif leftIntegral > rightIntegral:
					winner = self.params[ "left" ]
				else:
					winner = self.params[ "right" ]
					
			self.integralRewardMoney()
		else:
			if leftIntegral > rightIntegral:
				winner = self.params[ "left" ]
			elif leftIntegral < rightIntegral:
				winner = self.params[ "right" ] 
				
		if self.params[ "isFinal" ]:
			self.setChampionReward( winner )
			
		failure = 0
		if not winner:
			failure = self.params[ "left" ] if self.params[ "left" ] else self.params[ "right" ]
			
		BigWorld.globalData[ "TongManager" ].cityWarSetResult( cityName, winner, failure )
		self.warInfos.rewardWinMember( winner )
		self.getScript().closeCityWarRoom( self )
		self.base.onWarOver()
	
	def setChampionReward( self, tong_dbID ):
		if not tong_dbID:
			return
			
		rewardTime = self.params[ "finalRewardTime" ]
		if self.warInfos.infos.has_key( tong_dbID ):
			memberInfos = self.warInfos[ tong_dbID ].members
			for mInfo in memberInfos.itervalues():
				if mInfo.isIn:
					mInfo.mailBox.cell.tong_cityWarSetRewardChampion( rewardTime )
	
	def onEnterCommon( self, baseMailbox, params ):
		tongDBID = params[ "tongDBID" ]
		roleDBID = params[ "databaseID" ]
		ename = params[ "ename" ]
		
		tongInfos = {}
		tongInfos[ "left" ] = self.params[ "left" ]
		tongInfos[ "leftTongName" ] = self.params[ "leftTongName" ]
		tongInfos[ "right" ] = self.params[ "right" ]
		tongInfos[ "rightTongName" ] = self.params[ "rightTongName" ]
		if self.getScript().roomLevel > 0 and self.params.has_key( "defend" ):
			tongInfos[ "defend" ] = self.params[ "defend" ]
			tongInfos[ "defendTongName" ] = self.params[ "defendTongName" ]
			
		baseMailbox.client.tong_onEnterCityWarSpace( int( BigWorld.globalData[ "CityWarOverTime" ] - time.time() ), tongInfos )
		
		self.warInfos.addMember( tongDBID, roleDBID, ename, baseMailbox )
		self.getAttrBuff( baseMailbox, tongDBID )
		
		if not self.params.has_key( "defend" ):
			notPlayerInTongDBID = self.queryTemp( "NotPlayerInTongDBID", 0 )
			if notPlayerInTongDBID == 0:
				self.systemAddIntegral()
			elif notPlayerInTongDBID == tongDBID:
				self.removeTemp( "NotPlayerInTongDBID" )
				addIntegralTimerID = self.queryTemp( "addIntegralTimerID" )
				self.cancel( addIntegralTimerID )
				self.removeTemp( "addIntegralTimerID" )
		
		SpaceCopy.onEnterCommon( self, baseMailbox, params )
	
	def systemAddIntegral( self ):
		# 比赛开始后帮会A成员进入战场，帮会B成员始终不进入战场，帮派A的积分每30秒增加1点，即时刷新		
		leftTongDIBD = self.params[ "left" ]
		rightTongDBID = self.params[ "right" ]
		leftEnter = self.warInfos.countInSpacePlayer( leftTongDIBD )
		rightEnter = self.warInfos.countInSpacePlayer( rightTongDBID )
		if 0 == leftEnter and 0 != rightEnter:
			if self.queryTemp( "NotPlayerInTongDBID", 0 ) == leftTongDIBD:
				return
				
			addIntegralTimerID = self.addTimer( 30, 0, TIMER_ARGS_ADD_INTEGRAL )
			self.setTemp( "NotPlayerInTongDBID", leftTongDIBD )
			self.setTemp( "addIntegralTimerID", addIntegralTimerID )
		elif 0 != leftEnter and 0 == rightEnter:
			if self.queryTemp( "NotPlayerInTongDBID", 0 ) == rightTongDBID:
				return
			
			addIntegralTimerID = self.addTimer( 30, 0, TIMER_ARGS_ADD_INTEGRAL )
			self.setTemp( "NotPlayerInTongDBID", rightTongDBID )
			self.setTemp( "addIntegralTimerID", addIntegralTimerID )
		
	def getAttrBuff( self, baseMailbox, tongDBID ):
		if self.params.has_key( "defend" ) and self.params[ "defend" ]:
			if self.params[ "occupyNum" ] >= 2 and tongDBID != self.params[ "defend" ]:
				baseMailbox.cell.spellTarget( OCCUPY_NUMS_SKILL_ID, baseMailbox.id )
	
	def onLeaveCommon( self, baseMailbox, params ):
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		tongDBID = params[ "tongDBID" ]
		roleDBID = params[ "databaseID" ]
		self.warInfos.leaveMember( tongDBID, roleDBID )
		# 删除BUFF
		baseMailbox.cell.removeAllBuffByBuffID( OCCUPY_NUMS_BUFF_ID_1, [ csdefine.BUFF_INTERRUPT_NONE ] )
		baseMailbox.cell.removeAllBuffByBuffID( OCCUPY_NUMS_BUFF_ID_2, [ csdefine.BUFF_INTERRUPT_NONE ] )
		BigWorld.globalData[ "TongManager" ].cityWarLeave( tongDBID, roleDBID )
		
		if not self.params.has_key( "defend" ):
			self.systemAddIntegral()
	
	def onRoleBeKill( self, killerTongDBID, killerDBID, deaderTongDBID, deaderDBID ):
		# define method.
		# 有玩家被击杀后回调
		if killerDBID != 0:
			self.warInfos.addKill( killerTongDBID, killerDBID ) # 添加击杀次数
			
		self.warInfos.addDead( deaderTongDBID, deaderDBID ) # 添加死亡次数
		if self.params.has_key( "defend" ):
			if killerTongDBID != self.params[ "defend" ] and deaderTongDBID == self.params[ "defend" ]:# 判断不是防守方
				self.warInfos.addIntegral( killerTongDBID, 60 )  # 添加帮会积分
		else:
			self.warInfos.addIntegral( killerTongDBID, 1 )  # 添加帮会积分
			
	def addTongIntegral( self, tongDBID, integral ):
		# define method.
		# 添加指定帮会积分
		if tongDBID != self.params[ "defend" ]:# 判断不是防守方
			self.warInfos.addIntegral( tongDBID, integral )  # 添加帮会积分
	
	def isOverCityWar( self ):
		"""
		城市战争是否结束
		"""
		return self.queryTemp( "isCurrentCityWarOver", False )
	
	def onRoleRelive( self, mailbox, tongDBID ):
		# define method
		# 玩家战场复活
		if tongDBID == self.params[ "left" ]:
			mailbox.cell.tong_onCityWarReliveCallback( self.className, self.getScript().left_playerEnterPoint[ 0 ], self.getScript().left_playerEnterPoint[ 1 ] )
		elif tongDBID == self.params[ "right" ]:
			mailbox.cell.tong_onCityWarReliveCallback( self.className, self.getScript().right_playerEnterPoint[ 0 ], self.getScript().right_playerEnterPoint[ 1 ]  )
		else:
			mailbox.cell.tong_onCityWarReliveCallback( self.className, self.getScript().defend_playerEnterPoint[ 0 ], self.getScript().defend_playerEnterPoint[ 1 ]  )
	
	def integralRewardMoney( self ):
		# 决赛积分兑换帮会资金
		if not self.params.has_key( "defend" ) and self.params[ "defend" ]:
			return
			
		leftTongDBID = self.params[ "left" ]
		rightTongDBID = self.params[ "right" ]
		if leftTongDBID !=0 and self.warInfos.infos.has_key( leftTongDBID ):
			if self.warInfos[ leftTongDBID ].integral:
				BigWorld.globalData[ "TongManager" ].cityWarIntegralReward( leftTongDBID, self.warInfos[ leftTongDBID ].integral )
		
		if rightTongDBID !=0 and self.warInfos.infos.has_key( rightTongDBID ):
			if self.warInfos[ rightTongDBID ].integral:
				BigWorld.globalData[ "TongManager" ].cityWarIntegralReward( rightTongDBID, self.warInfos[ rightTongDBID ].integral )
	
	def onTimer( self, controllerID, userData ):
		if userData == TIMER_ARGS_ADD_INTEGRAL:
			tongDBID = self.queryTemp( "NotPlayerInTongDBID", 0 )
			if self.warInfos.countInSpacePlayer( tongDBID ) == 0:
				allTongKeys = self.warInfos.infos.keys()
				if tongDBID in allTongKeys:
					allTongKeys.remove( tongDBID )
					
				addIntegralTong = allTongKeys[ 0 ]
				self.warInfos.addIntegral( addIntegralTong, 1 )
				self.removeTemp( "NotPlayerInTongDBID" )
				self.removeTemp( "addIntegralTimerID" )
				self.systemAddIntegral()
			return
		
		SpaceCopy.onTimer( self, controllerID, userData )