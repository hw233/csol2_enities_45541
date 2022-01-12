# -*- coding: gb18030 -*-


import time
from SpaceCopy import SpaceCopy
from bwdebug import *
import cschannel_msgs
import Love3
import csdefine
import csstatus
import BigWorld


CAN_CALL_AMOUNT				= 6				#能够召唤怪物的召唤物资数量

ARG_ADD_FLAG_INTEGRAL		= 2000

ATTACK_SKILL_ID_DICT					= { 3:111478001, 2:111479001, 1:111480001 }
SPEED_SKILL_ID_DICT					= { 3:111481001, 2:111482001, 1:111483001 }
BUFF_ID_1							= 2002
BUFF_ID_2							= 6001
INTEGRAL_RATE						= 0.15
NOTICE_TIME_LIST					= [ 10*60, 3*60, 1*60 ]

class SpaceCopyTongFengHuoLianTian( SpaceCopy ):
	"""
	帮会夺城战复赛（烽火连天）
	"""
	def __init__(self):
		self.setTemp( "isCurrentFengHuoLianTianOver", False )
		SpaceCopy.__init__( self )
		self.tongCallBoxDict = {}
		self.tongCallMonsterDict = {}
		self.tongTowerDict = {}
		self.tongAltarDict = {}
		self.tongLastIntegralList = {}
	
	def onRoleRelive( self, baseMailbox, tongDBID ):
		if tongDBID == self.params[ "left" ]:
			baseMailbox.cell.tong_onCityWarReliveCallback( self.className, self.getScript().left_playerEnterPoint[ 0 ], self.getScript().left_playerEnterPoint[ 1 ] )
		elif tongDBID == self.params[ "right" ]:
			baseMailbox.cell.tong_onCityWarReliveCallback( self.className, self.getScript().right_playerEnterPoint[ 0 ], self.getScript().right_playerEnterPoint[ 1 ]  )

	def onEnterCommon( self, baseMailbox, params ):
		SpaceCopy.onEnterCommon( self, baseMailbox, params )
		tongDBID = params[ "tongDBID" ]
		roleDBID = params[ "databaseID" ]
		ename = params[ "ename" ]
		BigWorld.globalData[ "TongManager" ].fengHuoLianTianAddEnter( tongDBID, roleDBID )
		
		self.fengHuoLianTianInfos.addMember( tongDBID, roleDBID, ename, baseMailbox )
		tongInfos = {}
		tongInfos[ "left" ] = self.params[ "left" ]
		tongInfos[ "leftTongName" ] = self.params[ "leftTongName" ]
		tongInfos[ "right" ] = self.params[ "right" ]
		tongInfos[ "rightTongName" ] = self.params[ "rightTongName" ]
		if BigWorld.globalData.has_key( "fengHuoLianTianOverTime" ):
			baseMailbox.client.tong_onEnterFengHuoLianTianSpace( BigWorld.globalData[ "fengHuoLianTianOverTime" ], tongInfos )

		if not self.tongCallMonsterDict.has_key( tongDBID ):
			self.tongCallMonsterDict[tongDBID] = { "left":0, "mid":0, "right":0 }
		if not self.tongTowerDict.has_key( tongDBID ):
			self.tongTowerDict[ tongDBID ] = 0
		if not self.tongAltarDict.has_key( tongDBID ):
			self.tongAltarDict[ tongDBID ] = 0
		if self.tongTowerDict[ tongDBID ] != 0 and self.queryTemp( "startTowerAndAltar", False ):
			if not self.queryTemp( "firstTowerDead", False ):
				baseMailbox.cell.systemCastSpell( ATTACK_SKILL_ID_DICT[ 3 ] )
			else:
				baseMailbox.cell.systemCastSpell( ATTACK_SKILL_ID_DICT[ self.tongTowerDict[ tongDBID ] ] )
		if self.tongAltarDict[ tongDBID ] != 0 and self.queryTemp( "startTowerAndAltar", False ):
			if not self.queryTemp( "firstAltarDead", False ):
				baseMailbox.cell.systemCastSpell( SPEED_SKILL_ID_DICT[ 3 ] )
			else:
				baseMailbox.cell.systemCastSpell( SPEED_SKILL_ID_DICT[ self.tongAltarDict[ tongDBID ] ] )
		
		
	def onLeaveCommon( self, baseMailbox, params ):
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		tongDBID = params[ "tongDBID" ]
		roleDBID = params[ "databaseID" ]
		BigWorld.globalData[ "TongManager" ].fengHuoLianTianLeave( tongDBID, roleDBID )
		
		baseMailbox.cell.removeAllBuffByBuffID( BUFF_ID_1, [ csdefine.BUFF_INTERRUPT_NONE ] )
		baseMailbox.cell.removeAllBuffByBuffID( BUFF_ID_2, [ csdefine.BUFF_INTERRUPT_NONE ] )
		self.fengHuoLianTianInfos.leaveMember( tongDBID, roleDBID )

	def closeFengHuoLianTianRoom( self ):
		# 房间关闭
		if self.isOverFengHuoLianTian():
			return
			
		#取出两个帮会的积分，看看哪一个高，然后设置赢的帮会，存储起来用于下一场比赛
		if self.queryTemp( "addIntegralTongDBID" ):
			self.removeTemp( "addIntegralTongDBID" )
			addIntegralTimerID = self.queryTemp( "addIntegralTimerID" )
			self.cancel( addIntegralTimerID )
			
		winner = 0
		winnerIntegral = 0
		faulure = 0
		faulureIntegral = 0
		cityName = self.params[ "cityName" ]
		leftIntegral = self.fengHuoLianTianInfos.getIntegral( self.params[ "left" ] ) # 取出帮会的积分
		rightIntegral = self.fengHuoLianTianInfos.getIntegral( self.params[ "right" ] ) # 取出帮会的积分
		if leftIntegral > rightIntegral:
			winner = self.params[ "left" ]
		elif leftIntegral < rightIntegral:
			winner = self.params[ "right" ]
		else:
			if self.tongLastIntegralList.has_key( self.params[ "left" ] ) and not self.tongLastIntegralList.has_key( self.params[ "right" ] ):
				winner = self.params[ "left" ]
			elif self.tongLastIntegralList.has_key( self.params[ "right" ] ) and not self.tongLastIntegralList.has_key( self.params[ "left" ] ):
				winner = self.params[ "right" ]
			elif self.tongLastIntegralList.has_key( self.params[ "right" ] ) and self.tongLastIntegralList.has_key( self.params[ "left" ] ):
				if self.tongLastIntegralList[ self.params[ "left" ] ] > self.tongLastIntegralList[ self.params[ "right" ] ]:
					winner = self.params[ "left" ] 
				elif self.tongLastIntegralList[ self.params[ "left" ] ] < self.tongLastIntegralList[ self.params[ "right" ] ]:
					winner = self.params[ "right" ]
					
		if not winner:
			failure = self.params[ "left" ] if self.params[ "left" ] else self.params[ "right" ]
		
		if self.params[ "left" ] == winner:
			winnerIntegral = leftIntegral
			faulureIntegral = rightIntegral
		else:
			winnerIntegral = rightIntegral
			faulureIntegral = leftIntegral
			
		BigWorld.globalData[ "TongManager" ].FHLTSetResult( cityName, winner, winnerIntegral, failure, faulureIntegral ) # 
		self.getScript().closeFengHuoLianTianRoom( self )


	def isOverFengHuoLianTian( self ):
		return self.queryTemp( "isCurrentFengHuoLianTianOver", False )

	def addTongFengHuoLianTianIntegral( self, tongDBID, integral ):
		"""
		define method
		添加指定帮会的积分
		"""
		if not self.tongLastIntegralList.has_key( tongDBID ):
			self.tongLastIntegralList[ tongDBID ] = 0
		else:
			self.tongLastIntegralList[ tongDBID ] = self.fengHuoLianTianInfos.getIntegral( tongDBID )
		self.fengHuoLianTianInfos.addIntegral( tongDBID, integral )
		
	def decTongFengHuoLianTianIntegral( self, tongDBID, integral ):
		"""
		define method
		减少指定帮会的积分
		"""
		if not self.tongLastIntegralList.has_key( tongDBID ):
			self.tongLastIntegralList[ tongDBID ] = 0
		else:
			self.tongLastIntegralList[ tongDBID ] = self.fengHuoLianTianInfos.getIntegral( tongDBID )
		self.fengHuoLianTianInfos.decIntegral( tongDBID, integral )

	def addHostilityTongIntegral( self, killerTongDBID, deadTongDBID ):
		"""
		给敌对帮会增加积分
		"""
		if not self.tongLastIntegralList.has_key( killerTongDBID ):
			self.tongLastIntegralList[ killerTongDBID ] = 0
		else:
			self.tongLastIntegralList[ killerTongDBID ] = self.fengHuoLianTianInfos.getIntegral( killerTongDBID )
		integral = int( self.fengHuoLianTianInfos.getIntegral( deadTongDBID ) * INTEGRAL_RATE )
		self.fengHuoLianTianInfos.addIntegral( killerTongDBID, integral )

	def addTongCallBox( self, tongDBID, callBoxAmount ):
		"""
		define method
		添加指定帮会拾取的召唤箱子
		"""
		if self.tongCallBoxDict.has_key( tongDBID ):
			self.tongCallBoxDict[ tongDBID ] = self.tongCallBoxDict[ tongDBID ] + callBoxAmount
			if self.tongCallBoxDict[ tongDBID ] >= CAN_CALL_AMOUNT:
				self.getScript().callXianFengMonster( self, tongDBID )
		else:
			self.tongCallBoxDict[ tongDBID ] = callBoxAmount
		for e in self._players:
			player = BigWorld.entities.get( e.id, None )
			if player and player.tong_dbID == tongDBID:
				tongName = ""
				if tongDBID == self.params[ "left" ]:
					tongName = self.params[ "leftTongName" ]
				elif tongDBID == self.params[ "right" ]:
					tongName = self.params[ "rightTongName" ]
				if self.tongCallBoxDict[ tongDBID ] and self.tongCallBoxDict[ tongDBID ] < CAN_CALL_AMOUNT:
					player.client.onStatusMessage( csstatus.TONG_FENG_HUO_LIAN_TIAN_CALL_BOX_AMOUNT, str( ( tongName, self.tongCallBoxDict[ tongDBID ], CAN_CALL_AMOUNT - self.tongCallBoxDict[ tongDBID ]%CAN_CALL_AMOUNT ) ))
				elif self.tongCallBoxDict[ tongDBID ] and self.tongCallBoxDict[ tongDBID ] >= CAN_CALL_AMOUNT:
					player.client.onStatusMessage( csstatus.TONG_FENG_HUO_LIAN_TIAN_REACH_LIMIT_AMOUNT, str( ( tongName, ) ))
		pass
	
	def decTongCallBoxAmount( self, tongDBID, amount, roadString ):
		if self.tongCallBoxDict.has_key( tongDBID ):
			self.tongCallBoxDict[ tongDBID ] = self.tongCallBoxDict[ tongDBID ] - amount
			if not self.tongCallMonsterDict.has_key( tongDBID ):
				self.tongCallMonsterDict[ tongDBID ] = { "left":0, "mid":0, "right":0 }
				self.tongCallMonsterDict[ tongDBID ][ roadString ] = 1
			else:
				self.tongCallMonsterDict[ tongDBID ][ roadString ] = 1
			self.removeTemp( "isCallingMonster" )
		else:
			ERROR_MSG( "decTongCallBoxAmount Error：the tongDBID %s is not exist" %tongDBID )

	def onMonsterXianFengDie( self, tongDBID, roadString ):
		if self.tongCallMonsterDict.has_key( tongDBID ):
			self.tongCallMonsterDict[ tongDBID ][ roadString ] = 0

	def onRoleBeKill( self, killerTongDBID, killerDBID, deaderTongDBID, deaderDBID ):
		# define method.
		# 有玩家被击杀后回调
		if killerDBID != 0:
			self.fengHuoLianTianInfos.addKill( killerTongDBID, killerDBID ) # 添加击杀次数
			
		self.fengHuoLianTianInfos.addDead( deaderTongDBID, deaderDBID ) # 添加死亡次数

	def addIntegralTimer( self, tongDBID, intervalTime, isFirst ):
		if isFirst:
			self.addTongFengHuoLianTianIntegral( tongDBID, intervalTime )
			self.setTemp( "addIntegralTongDBID", tongDBID )
			addIntegralTimerID = self.addTimer( 1, 0, ARG_ADD_FLAG_INTEGRAL )
			self.setTemp( "addIntegralTimerID", addIntegralTimerID )
		else:
			self.removeTemp( "addIntegralTongDBID" )
			addIntegralTimerID = self.queryTemp( "addIntegralTimerID" )
			self.cancel( addIntegralTimerID )
			self.addTongFengHuoLianTianIntegral( tongDBID, intervalTime )
			self.setTemp( "addIntegralTongDBID", tongDBID )
			addIntegralTimerID = self.addTimer( 1, 0, ARG_ADD_FLAG_INTEGRAL )
			self.setTemp( "addIntegralTimerID", addIntegralTimerID )

	def addSpawnPoint( self, spawnPointBaseMB, belongTong ):
		if belongTong == 0:
			tongKey = "left_tower_and_altar"
		elif belongTong == 1:
			tongKey = "right_tower_and_altar"
		spawnPointBaseMBList = self.queryTemp( tongKey, [] )
		spawnPointBaseMBList.append( spawnPointBaseMB )
		self.setTemp( tongKey, spawnPointBaseMBList )
		tower_and_altar = self.queryTemp( "tower_and_altar", set() )
		tower_and_altar.add( tongKey )
		self.setTemp( "tower_and_altar", tower_and_altar )

	def addTowerNum( self, tongDBID ):
		if not self.tongTowerDict.has_key( tongDBID ):
			self.tongTowerDict[ tongDBID ] = 1
		else:
			self.tongTowerDict[ tongDBID ] = self.tongTowerDict[ tongDBID ] + 1
		pass

	def addAltarNum( self, tongDBID ):
		if not self.tongAltarDict.has_key( tongDBID ):
			self.tongAltarDict[ tongDBID ] = 1
		else:
			self.tongAltarDict[ tongDBID ] = self.tongAltarDict[ tongDBID ] + 1

	def decAltarNum( self, tongDBID ):
		if not self.tongAltarDict.has_key( tongDBID ):
			return
		else:
			if not self.queryTemp( "firstAltarDead", False ):
				self.setTemp( "firstAltarDead", True )
			self.tongAltarDict[ tongDBID ] = self.tongAltarDict[ tongDBID ] - 1
			if self.tongAltarDict[ tongDBID ] == 0:
				for e in self._players:
					player = BigWorld.entities.get( e.id, None )
					if player and player.tong_dbID == tongDBID:
						player.removeAllBuffByBuffID( BUFF_ID_2, [ csdefine.BUFF_INTERRUPT_NONE ] )
			else:
				for e in self._players:
					player = BigWorld.entities.get( e.id, None )
					if player and player.tong_dbID == tongDBID:
						player.systemCastSpell( SPEED_SKILL_ID_DICT[ self.tongAltarDict[ tongDBID ] ] )
	
	def decTowerNum( self, tongDBID ):
		if not self.tongTowerDict.has_key( tongDBID ):
			return
		else:
			if not self.queryTemp( "firstTowerDead", False ):
				self.setTemp( "firstTowerDead", True )
			self.tongTowerDict[ tongDBID ] = self.tongTowerDict[ tongDBID ] - 1
			if self.tongTowerDict[ tongDBID ] == 0:
				for e in self._players:
					player = BigWorld.entities.get( e.id, None )
					if player and player.tong_dbID == tongDBID:
						player.removeAllBuffByBuffID( BUFF_ID_1, [ csdefine.BUFF_INTERRUPT_NONE ] )
			else:
				for e in self._players:
					player = BigWorld.entities.get( e.id, None )
					if player and player.tong_dbID == tongDBID:
						player.systemCastSpell( ATTACK_SKILL_ID_DICT[ self.tongTowerDict[ tongDBID ] ] )

	def onTimer( self, controllerID, userData ):
		if userData == ARG_ADD_FLAG_INTEGRAL:
			tongDBID = self.queryTemp( "addIntegralTongDBID", 0 )
			if tongDBID:
				self.addTongFengHuoLianTianIntegral( tongDBID, 1 )
				self.removeTemp( "addIntegralTongDBID" )
				self.removeTemp( "addIntegralTimerID" )
				self.setTemp( "addIntegralTongDBID", tongDBID )
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

	def noticeTongSituation( self, noticeTime ):
		winner = ""
		leftIntegral = self.fengHuoLianTianInfos.getIntegral( self.params[ "left" ] ) # 取出帮会的积分
		rightIntegral = self.fengHuoLianTianInfos.getIntegral( self.params[ "right" ] ) # 取出帮会的积分
		if leftIntegral > rightIntegral:
			winner = self.params[ "leftTongName" ]
		elif leftIntegral < rightIntegral:
			winner = self.params[ "rightTongName" ]
		
		if noticeTime == NOTICE_TIME_LIST[0]:
			if winner:
				self.noticePlayers( cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_END_NOTICE_1% winner, [] )
			else:
				self.noticePlayers( cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_END_NOTICE_4, [] )
		elif noticeTime == NOTICE_TIME_LIST[1]:
			if winner:
				self.noticePlayers( cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_END_NOTICE_2% winner, [] )
			else:
				self.noticePlayers( cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_END_NOTICE_5, [] )
		elif noticeTime == NOTICE_TIME_LIST[2]:
			if winner:
				self.noticePlayers( cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_END_NOTICE_3% winner, [] )
			else:
				self.noticePlayers( cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_END_NOTICE_6, [] )

