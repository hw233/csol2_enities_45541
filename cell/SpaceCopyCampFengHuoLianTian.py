# -*- coding: gb18030 -*-


import time
from SpaceCopy import SpaceCopy
from csconst import g_camp_info
from bwdebug import *
import cschannel_msgs
import Love3
import csdefine
import csstatus
import BigWorld
import Const


CAN_CALL_AMOUNT				= 6				#能够召唤怪物的召唤物资数量

ARG_ADD_FLAG_INTEGRAL		= 2000

ATTACK_SKILL_ID_DICT					= { 3:111478001, 2:111479001, 1:111480001 }
SPEED_SKILL_ID_DICT					= { 3:111481001, 2:111482001, 1:111483001 }
BUFF_ID_1							= 2002
BUFF_ID_2							= 6001
INTEGRAL_RATE						= 0.15
NOTICE_TIME_LIST					= [ 10*60, 3*60, 1*60 ]

#金钱，经验以及机缘奖励值
#第一名：金钱（暂定10金）、经验（暂定50w）、机缘（暂定100）
#胜者奖：金钱（暂定5金）、经验（暂定30w）、机缘（暂定10）
#败者参与奖：金钱（暂定2金）、经验（暂定10w）、机缘（暂定5）
FIRST_PLAYER_MONEY = 100000
FIRST_PLAYER_EXP = 500000
FIRST_PLAYER_JI_YUAN = 100
VICTORY_CAMP_MONEY = 50000
VICTORY_CAMP_EXP = 300000
VICTORY_CAMP_JI_YUAN = 10
FAILURE_CAMP_MONEY = 20000
FAILURE_CAMP_EXP = 100000
FAILURE_CAMP_JI_YUAN = 5


class SpaceCopyCampFengHuoLianTian( SpaceCopy ):
	"""
	阵营烽火连天
	"""
	def __init__(self):
		self.setTemp( "isCurrentFengHuoLianTianOver", False )
		SpaceCopy.__init__( self )
		self.campCallBoxDict = {}
		self.campCallMonsterDict = {}
		self.campTowerDict = {}
		self.campAltarDict = {}
		self.campLastIntegralList = {}
	
	def onRoleRelive( self, baseMailbox, camp ):
		if camp == self.params[ "left" ]:
			baseMailbox.cell.onRoleReviveCallBack( self.className, self.getScript().left_playerEnterPoint[ 0 ], self.getScript().left_playerEnterPoint[ 1 ] )
		elif camp == self.params[ "right" ]:
			baseMailbox.cell.onRoleReviveCallBack( self.className, self.getScript().right_playerEnterPoint[ 0 ], self.getScript().right_playerEnterPoint[ 1 ]  )

	def onEnterCommon( self, baseMailbox, params ):
		SpaceCopy.onEnterCommon( self, baseMailbox, params )
		camp = params[ "camp" ]
		roleDBID = params[ "dbid" ]
		ename = params[ "ename" ]
		#BigWorld.globalData[ "CampMgr" ].campFengHuoAddEnter( camp, roleDBID )
		
		self.campFengHuoInfos.addMember( camp, roleDBID, ename, baseMailbox )
		campInfos = {}
		campInfos[ "left" ] = self.params[ "left" ]
		campInfos[ "right" ] = self.params[ "right" ]
		if BigWorld.globalData.has_key( "campFengHuoOverTime" ):
			baseMailbox.client.camp_onEnterFengHuoLianTianSpace( BigWorld.globalData[ "campFengHuoOverTime" ], campInfos )

		if not self.campCallMonsterDict.has_key( camp ):
			self.campCallMonsterDict[camp] = { "left":0, "mid":0, "right":0 }
		if not self.campTowerDict.has_key( camp ):
			self.campTowerDict[ camp ] = 0
		if not self.campAltarDict.has_key( camp ):
			self.campAltarDict[ camp ] = 0
		if self.campTowerDict[ camp ] != 0 and self.queryTemp( "startTowerAndAltar", False ):
			if not self.queryTemp( "firstTowerDead", False ):
				baseMailbox.cell.systemCastSpell( ATTACK_SKILL_ID_DICT[ 3 ] )
			else:
				baseMailbox.cell.systemCastSpell( ATTACK_SKILL_ID_DICT[ self.campTowerDict[ camp ] ] )
		if self.campAltarDict[ camp ] != 0 and self.queryTemp( "startTowerAndAltar", False ):
			if not self.queryTemp( "firstAltarDead", False ):
				baseMailbox.cell.systemCastSpell( SPEED_SKILL_ID_DICT[ 3 ] )
			else:
				baseMailbox.cell.systemCastSpell( SPEED_SKILL_ID_DICT[ self.campAltarDict[ camp ] ] )
		
		
	def onLeaveCommon( self, baseMailbox, params ):
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		camp = params[ "camp" ]
		roleDBID = params[ "dbid" ]
		#BigWorld.globalData[ "CampMgr" ].campFengHuoLeave( camp, roleDBID )
		
		baseMailbox.cell.removeAllBuffByBuffID( BUFF_ID_1, [ csdefine.BUFF_INTERRUPT_NONE ] )
		baseMailbox.cell.removeAllBuffByBuffID( BUFF_ID_2, [ csdefine.BUFF_INTERRUPT_NONE ] )
		self.campFengHuoInfos.leaveMember( camp, roleDBID )

	def closeCampFengHuoRoom( self ):
		# 房间关闭
		if self.isOverFengHuoLianTian():
			return
			
		#取出两个阵营的积分，看看哪一个高，然后设置赢的阵营，存储起来用于下一场比赛
		if self.queryTemp( "addIntegralCamp" ):
			self.removeTemp( "addIntegralCamp" )
			addIntegralTimerID = self.queryTemp( "addIntegralTimerID" )
			self.cancel( addIntegralTimerID )
			
		winner = 0
		winnerIntegral = 0
		failure = 0
		failureIntegral = 0
		leftIntegral = self.campFengHuoInfos.getIntegral( self.params[ "left" ] ) # 取出阵营的积分
		rightIntegral = self.campFengHuoInfos.getIntegral( self.params[ "right" ] ) # 取出阵营的积分
		if leftIntegral > rightIntegral:
			winner = self.params[ "left" ]
			failure = self.params[ "right" ]
		elif leftIntegral < rightIntegral:
			winner = self.params[ "right" ]
			failure = self.params[ "left" ]
		else:
			if self.campLastIntegralList.has_key( self.params[ "left" ] ) and not self.campLastIntegralList.has_key( self.params[ "right" ] ):
				winner = self.params[ "left" ]
				failure = self.params[ "right" ]
			elif self.campLastIntegralList.has_key( self.params[ "right" ] ) and not self.campLastIntegralList.has_key( self.params[ "left" ] ):
				winner = self.params[ "right" ]
				failure = self.params[ "left" ]
			elif self.campLastIntegralList.has_key( self.params[ "right" ] ) and self.campLastIntegralList.has_key( self.params[ "left" ] ):
				if self.campLastIntegralList[ self.params[ "left" ] ] > self.campLastIntegralList[ self.params[ "right" ] ]:
					winner = self.params[ "left" ]
					failure = self.params[ "right" ]
				elif self.campLastIntegralList[ self.params[ "left" ] ] < self.campLastIntegralList[ self.params[ "right" ] ]:
					winner = self.params[ "right" ]
					failure = self.params[ "left" ]
					
		playerName = self.campFengHuoInfos.findMaxKillPlayerName()
		if winner:
			BigWorld.globalData[ "CampMgr" ].campFHLTReward( winner, failure, playerName )
		DEBUG_MSG( "winner is %s,failure is %s"%( winner, failure ) )
		
		#if self.params[ "left" ] == winner:
		#	winnerIntegral = leftIntegral
		#	faulureIntegral = rightIntegral
		#else:
		#	winnerIntegral = rightIntegral
		#	faulureIntegral = leftIntegral
			
		playerName = self.campFengHuoInfos.findMaxKillPlayerName()
		self.sendReward( winner, failure, playerName )
		self.getScript().closeCampFengHuoRoom( self )

	def sendReward( self, winner, failure, playerName ):
		for e in self._players:
			player = BigWorld.entities.get( e.id, None )
			if player.getName() == playerName:
				moneyNum = FIRST_PLAYER_MONEY
				expNum = FIRST_PLAYER_EXP
				jiyuanNum = FIRST_PLAYER_JI_YUAN
			else:
				if winner == 0:
					moneyNum = FAILURE_CAMP_MONEY
					expNum = FAILURE_CAMP_EXP
					jiyuanNum = FAILURE_CAMP_JI_YUAN
				else:
					if player.getCamp() == winner:
						moneyNum = VICTORY_CAMP_MONEY
						expNum = VICTORY_CAMP_EXP
						jiyuanNum = VICTORY_CAMP_JI_YUAN
					elif player.getCamp() == failure:
						moneyNum = FAILURE_CAMP_MONEY
						expNum = FAILURE_CAMP_EXP
						jiyuanNum = FAILURE_CAMP_JI_YUAN
			self.sendRoleReward( player, moneyNum, expNum, jiyuanNum )
		pass

	def sendRoleReward( self, playerEntity, moneyNum, expNum, jiyuanNum ):
		playerEntity.activity_gainMoney( moneyNum, csdefine.CHANGE_MONEY_CAMP_FENG_HUO )
		playerEntity.addExp( expNum, csdefine.CHANGE_EXP_CAMP_FENG_HUO )
		playerEntity.base.remoteCall( "set_jiyuan", ( jiyuanNum, ) )
		pass

	def isOverFengHuoLianTian( self ):
		return self.queryTemp( "isCurrentFengHuoLianTianOver", False )

	def addCampFengHuoLianTianIntegral( self, camp, integral ):
		"""
		define method
		添加指定阵营的积分
		"""
		if not self.campLastIntegralList.has_key( camp ):
			self.campLastIntegralList[ camp ] = 0
		else:
			self.campLastIntegralList[ camp ] = self.campFengHuoInfos.getIntegral( camp )
		self.campFengHuoInfos.addIntegral( camp, integral )
		
	def decCampFengHuoLianTianIntegral( self, camp, integral ):
		"""
		define method
		减少指定阵营的积分
		"""
		if not self.campLastIntegralList.has_key( camp ):
			self.campLastIntegralList[ camp ] = 0
		else:
			self.campLastIntegralList[ camp ] = self.campFengHuoInfos.getIntegral( camp )
		self.campFengHuoInfos.decIntegral( camp, integral )

	def addHostilityCampIntegral( self, killerCamp, deadCamp ):
		"""
		给敌对阵营增加积分
		"""
		if not self.campLastIntegralList.has_key( killerCamp ):
			self.campLastIntegralList[ killerCamp ] = 0
		else:
			self.campLastIntegralList[ killerCamp ] = self.campFengHuoInfos.getIntegral( killerCamp )
		integral = int( self.campFengHuoInfos.getIntegral( deadCamp ) * INTEGRAL_RATE )
		self.campFengHuoInfos.addIntegral( killerCamp, integral )

	def addCampCallBox( self, camp, callBoxAmount ):
		"""
		define method
		添加指定阵营拾取的召唤箱子
		"""
		if self.campCallBoxDict.has_key( camp ):
			self.campCallBoxDict[ camp ] = self.campCallBoxDict[ camp ] + callBoxAmount
			if self.campCallBoxDict[ camp ] >= CAN_CALL_AMOUNT:
				self.getScript().callXianFengMonster( self, camp )
		else:
			self.campCallBoxDict[ camp ] = callBoxAmount
		for e in self._players:
			player = BigWorld.entities.get( e.id, None )
			if player and player.getCamp() == camp:
				campName = ""
				if camp in [ csdefine.ENTITY_CAMP_TAOISM, csdefine.ENTITY_CAMP_DEMON ]:
					campName = g_camp_info[ camp ]
				if self.campCallBoxDict[ camp ] and self.campCallBoxDict[ camp ] < CAN_CALL_AMOUNT:
					player.client.onStatusMessage( csstatus.CAMP_FENG_HUO_CALL_BOX_AMOUNT, str( ( campName, self.campCallBoxDict[ camp ], CAN_CALL_AMOUNT - self.campCallBoxDict[ camp ]%CAN_CALL_AMOUNT ) ))
				elif self.campCallBoxDict[ camp ] and self.campCallBoxDict[ camp ] >= CAN_CALL_AMOUNT:
					player.client.onStatusMessage( csstatus.CAMP_FENG_HUO_REACH_LIMIT_AMOUNT, str( ( campName, ) ))
		pass
	
	def decCampCallBoxAmount( self, camp, amount, roadString ):
		if self.campCallBoxDict.has_key( camp ):
			self.campCallBoxDict[ camp ] = self.campCallBoxDict[ camp ] - amount
			if not self.campCallMonsterDict.has_key( camp ):
				self.campCallMonsterDict[ camp ] = { "left":0, "mid":0, "right":0 }
				self.campCallMonsterDict[ camp ][ roadString ] = 1
			else:
				self.campCallMonsterDict[ camp ][ roadString ] = 1
			self.removeTemp( "isCallingMonster" )
		else:
			ERROR_MSG( "decCampCallBoxAmount Error：the camp %s is not exist" %camp )

	def onMonsterXianFengDie( self, camp, roadString ):
		if self.campCallMonsterDict.has_key( camp ):
			self.campCallMonsterDict[ camp ][ roadString ] = 0

	def onRoleBeKill( self, killerCamp, killerDBID, deaderCamp, deaderDBID ):
		# define method.
		# 有玩家被击杀后回调
		if killerDBID != 0:
			self.campFengHuoInfos.addKill( killerCamp, killerDBID ) # 添加击杀次数
			
		self.campFengHuoInfos.addDead( deaderCamp, deaderDBID ) # 添加死亡次数

	def addIntegralTimer( self, camp, intervalTime, isFirst ):
		if isFirst:
			self.addCampFengHuoLianTianIntegral( camp, intervalTime )
			self.setTemp( "addIntegralCamp", camp )
			addIntegralTimerID = self.addTimer( 1, 0, ARG_ADD_FLAG_INTEGRAL )
			self.setTemp( "addIntegralTimerID", addIntegralTimerID )
		else:
			self.removeTemp( "addIntegralCamp" )
			addIntegralTimerID = self.queryTemp( "addIntegralTimerID" )
			self.cancel( addIntegralTimerID )
			self.addCampFengHuoLianTianIntegral( camp, intervalTime )
			self.setTemp( "addIntegralCamp", camp )
			addIntegralTimerID = self.addTimer( 1, 0, ARG_ADD_FLAG_INTEGRAL )
			self.setTemp( "addIntegralTimerID", addIntegralTimerID )

	def addSpawnPoint( self, spawnPointBaseMB, belongCamp ):
		if belongCamp == csdefine.ENTITY_CAMP_TAOISM:
			campKey = "left_tower_and_altar"
		elif belongCamp == csdefine.ENTITY_CAMP_DEMON:
			campKey = "right_tower_and_altar"
		spawnPointBaseMBList = self.queryTemp( campKey, [] )
		spawnPointBaseMBList.append( spawnPointBaseMB )
		self.setTemp( campKey, spawnPointBaseMBList )
		tower_and_altar = self.queryTemp( "tower_and_altar", set() )
		tower_and_altar.add( campKey )
		self.setTemp( "tower_and_altar", tower_and_altar )

	def addTowerNum( self, camp ):
		if not self.campTowerDict.has_key( camp ):
			self.campTowerDict[ camp ] = 1
		else:
			self.campTowerDict[ camp ] = self.campTowerDict[ camp ] + 1
		pass

	def addAltarNum( self, camp ):
		if not self.campAltarDict.has_key( camp ):
			self.campAltarDict[ camp ] = 1
		else:
			self.campAltarDict[ camp ] = self.campAltarDict[ camp ] + 1

	def decAltarNum( self, camp ):
		if not self.campAltarDict.has_key( camp ):
			return
		else:
			if not self.queryTemp( "firstAltarDead", False ):
				self.setTemp( "firstAltarDead", True )
			self.campAltarDict[ camp ] = self.campAltarDict[ camp ] - 1
			if self.campAltarDict[ camp ] == 0:
				for e in self._players:
					player = BigWorld.entities.get( e.id, None )
					if player and player.getCamp() == camp:
						player.removeAllBuffByBuffID( BUFF_ID_2, [ csdefine.BUFF_INTERRUPT_NONE ] )
			else:
				for e in self._players:
					player = BigWorld.entities.get( e.id, None )
					if player and player.getCamp() == camp:
						player.systemCastSpell( SPEED_SKILL_ID_DICT[ self.campAltarDict[ camp ] ] )
	
	def decTowerNum( self, camp ):
		if not self.campTowerDict.has_key( camp ):
			return
		else:
			if not self.queryTemp( "firstTowerDead", False ):
				self.setTemp( "firstTowerDead", True )
			self.campTowerDict[ camp ] = self.campTowerDict[ camp ] - 1
			if self.campTowerDict[ camp ] == 0:
				for e in self._players:
					player = BigWorld.entities.get( e.id, None )
					if player and player.getCamp() == camp:
						player.removeAllBuffByBuffID( BUFF_ID_1, [ csdefine.BUFF_INTERRUPT_NONE ] )
			else:
				for e in self._players:
					player = BigWorld.entities.get( e.id, None )
					if player and player.getCamp() == camp:
						player.systemCastSpell( ATTACK_SKILL_ID_DICT[ self.campTowerDict[ camp ] ] )

	def onTimer( self, controllerID, userData ):
		if userData == ARG_ADD_FLAG_INTEGRAL:
			camp = self.queryTemp( "addIntegralCamp", 0 )
			if camp:
				self.addCampFengHuoLianTianIntegral( camp, 1 )
				self.removeTemp( "addIntegralCamp" )
				self.removeTemp( "addIntegralTimerID" )
				self.setTemp( "addIntegralCamp", camp )
				addIntegralTimerID = self.addTimer( 1, 0, ARG_ADD_FLAG_INTEGRAL )
				self.setTemp( "addIntegralTimerID", addIntegralTimerID )
		else:
			SpaceCopy.onTimer( self, controllerID, userData )

	def noticePlayers( self, msg, blobArgs ):
		"""
		defined method
		在系统频道通知副本内的玩家
		@param					msg : 消息内容
		@type					msg : STRING
		@type				blobArgs: BLOB_ARRAY
		@param				blobArgs: 消息参数列表
		"""
		for e in self._players:
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", msg, blobArgs )

	def noticeCampSituation( self, noticeTime ):
		winner = ""
		leftIntegral = self.campFengHuoInfos.getIntegral( self.params[ "left" ] ) # 取出阵营的积分
		rightIntegral = self.campFengHuoInfos.getIntegral( self.params[ "right" ] ) # 取出阵营的积分
		if leftIntegral > rightIntegral:
			winner = g_camp_info[ self.params[ "left" ] ]
		elif leftIntegral < rightIntegral:
			winner = g_camp_info[ self.params[ "right" ] ]
		
		if noticeTime == NOTICE_TIME_LIST[0]:
			if winner:
				self.noticePlayers( cschannel_msgs.CAMP_FENG_HUO_END_NOTICE_1% winner, [] )
			else:
				self.noticePlayers( cschannel_msgs.CAMP_FENG_HUO_END_NOTICE_4, [] )
		elif noticeTime == NOTICE_TIME_LIST[1]:
			if winner:
				self.noticePlayers( cschannel_msgs.CAMP_FENG_HUO_END_NOTICE_2% winner, [] )
			else:
				self.noticePlayers( cschannel_msgs.CAMP_FENG_HUO_END_NOTICE_5, [] )
		elif noticeTime == NOTICE_TIME_LIST[2]:
			if winner:
				self.noticePlayers( cschannel_msgs.CAMP_FENG_HUO_END_NOTICE_3% winner, [] )
			else:
				self.noticePlayers( cschannel_msgs.CAMP_FENG_HUO_END_NOTICE_6, [] )

