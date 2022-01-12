# -*- coding: gb18030 -*-
#
#$Id:$

"""
14:23 2008-9-11,by wangshufeng
"""
"""
2010.11
家族擂台移植为帮会擂台 by cxm
"""
import BigWorld
from bwdebug import *
import csdefine
import csconst
import csstatus
import Const
import time
from SpaceCopyTeam import SpaceCopyTeam


GO_OUT_TIMER = 11
END_ENTER_TIMER = 1111

class SpaceCopyTongAba( SpaceCopyTeam ):
	"""
	帮会擂台赛副本空间
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopyTeam.__init__( self )
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = True
		self.right_playerEnterPoint = ()	# 擂台赛副本right方进入点
		self.left_playerEnterPoint = ()		# 擂台赛副本left方进入点
		self.right_chapmanPoint = ()		# ( position, direction )，right方商人的位置
		self.left_chapmanPoint = ()			# ( position, direction )，left方商人的位置
		self.left_relivePoints = []			# left方复活点
		self.right_relivePoints = []		# right方复活点


	def load( self, section ):
		"""
		从配置中加载数据

		@type section : PyDataSection
		@param section : python data section load from npc's coonfig file
		"""
		SpaceCopyTeam.load( self, section )

		# right方复活点
		data = section[ "Space" ][ "right_playerEnterPoint" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.right_playerEnterPoint = ( pos, direction )
		data = section[ "Space" ][ "left_playerEnterPoint" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.left_playerEnterPoint = ( pos, direction )

		# right方商人NPC位置
		data = section[ "Space" ][ "right_chapmanPoint" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.right_chapmanPoint = ( pos, direction )

		# left方复活点
		data = section[ "Space" ][ "left_relivePoint1" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.left_relivePoints.append( ( pos, direction ) )
		data = section[ "Space" ][ "left_relivePoint2" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.left_relivePoints.append( ( pos, direction ) )
		data = section[ "Space" ][ "left_relivePoint3" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.left_relivePoints.append( ( pos, direction ) )

		# right方复活点
		data = section[ "Space" ][ "right_relivePoint1" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.right_relivePoints.append( ( pos, direction ) )
		data = section[ "Space" ][ "right_relivePoint2" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.right_relivePoints.append( ( pos, direction ) )
		data = section[ "Space" ][ "right_relivePoint3" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.right_relivePoints.append( ( pos, direction ) )

		# left方商人NPC位置
		data = section[ "Space" ][ "left_chapmanPoint" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		self.left_chapmanPoint = ( pos, direction )

		# 战场商人的NPCID
		self.chapmanNPCID = section[ "Space" ][ "chapmanNPCID" ].asString
		# 进入者最小级别限制
		self.enterLimitLevel = section[ "Space" ][ "enterLimitLevel" ].asInt
		# 某人被杀扣除帮会积分
		self.bekillPunish = section[ "Space" ][ "bekillPunish" ].asInt
		# 帮会初始总积分
		self.initTotalMark = section[ "Space" ][ "initTotalMark" ].asInt
		# 玩家第一次进入的初始购买积分
		self.playerInitBuyMark = section[ "Space" ][ "playerInitBuyMark" ].asInt
		# 玩家死亡一次增加购买积分
		self.playerOnDiedAddBuyMark = section[ "Space" ][ "playerOnDiedAddBuyMark" ].asInt


	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		用我自己的数据初始化参数 selfEntity 的数据
		"""
		DEBUG_MSG( "---------->>>" )
		# 创建战场商人NPC
		selfEntity.createNPCObject( self.chapmanNPCID, self.right_chapmanPoint[0], self.right_chapmanPoint[1], { "tempMapping" : {"isRight" : True } } )
		selfEntity.createNPCObject( self.chapmanNPCID, self.left_chapmanPoint[0], self.left_chapmanPoint[1], { "tempMapping" : {"isRight" : False } } )

		BigWorld.globalData["TongManager"].requestAbaData( selfEntity.base )


	def packedDomainData( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		@param entity: 通常为玩家
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		# 返回databaseID，这样space domain能够此数据正确的记录副本的创建者，
		# 且不用担心玩家在短时间内（断）下线后重上时找回副本的问题；
		return { 'tongDBID' : entity.tong_dbID }


	def checkDomainIntoEnable( self, entity ):
		"""
		在cell上检查该空间进入的条件
		"""
		info = time.localtime()

		if entity.tong_grade <= 0 or entity.tong_dbID <= 0:
			return csstatus.SPACE_MISS_NOTTONG
		elif entity.level < self.enterLimitLevel:
			return csstatus.TONG_NO_WAR_LEVEL
		return csstatus.SPACE_OK


	def packedSpaceDataOnEnter( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于在玩家上线时需要在指定的space创建cell而获取数据；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		packDict = SpaceCopyTeam.packedSpaceDataOnEnter( self, entity )
		packDict[ "tongDBID" ] = entity.tong_dbID
		packDict[ "tongName" ] = entity.tongName
		packDict[ "playerName" ] = entity.getName()
		packDict[ "playerDBID" ] = entity.databaseID
		return packDict


	def isTongPunish( self, selfEntity, tongDBID ):
		"""
		帮会是否在被惩罚状态

		@param selfEntity : 脚本对应的entity
		@type selfEntity : ENTITY
		@param tongDBID : 家族dbid
		@type tongDBID : DATABASE_ID
		"""
		return False


	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.client.tong_onEnterAbaSpace()
		if selfEntity.queryTemp( "createTime", 0 ) == 0:
			selfEntity.setTemp("createTime", BigWorld.time() )
			restTime = 5 * 60 - selfEntity.getAbaTimeInfo()
			selfEntity.addTimer( restTime, 0, END_ENTER_TIMER )
		playerDBID = params[ "playerDBID" ]
		tongDBID = params[ "tongDBID" ]
		tongName = params[ "tongName" ]
		playerName = params[ "playerName" ]

		tongDBID1 = selfEntity.params["tongDBID1"]
		tongDBID2 = selfEntity.params["tongDBID2"]

		if tongDBID == selfEntity.params["tongDBID1"]:
			tongName = selfEntity.params["tongName1"]
		elif tongDBID == selfEntity.params["tongDBID2"]:
			tongName = selfEntity.params["tongName2"]

		if selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID ):		# 副本中没有本帮会的玩家
			if tongDBID not in selfEntity.abaPointRecord:				# 本帮会没有积分记录（没有帮会玩家进过副本）
				selfEntity.abaPointRecord[ tongDBID ] = self.initTotalMark
			selfEntity.abaPlayers.updateTongAbaPoint( tongName,selfEntity.abaPointRecord[ tongDBID ], tongDBID )
			BigWorld.globalData[ "TongManager" ].addEnterTong( tongDBID )

		if tongDBID1 != 0:
			if selfEntity.abaPointRecord.has_key( tongDBID1 ):
				baseMailbox.client.updateTongAbaPoint( selfEntity.params["tongName1"], selfEntity.abaPointRecord[ tongDBID1 ], selfEntity.params["tongDBID1"] )
			else:
				baseMailbox.client.updateTongAbaPoint( selfEntity.params["tongName1"], 0, selfEntity.params["tongDBID1"] )
		if tongDBID2 != 0:
			if selfEntity.abaPointRecord.has_key( tongDBID2 ):
				baseMailbox.client.updateTongAbaPoint( selfEntity.params["tongName2"], selfEntity.abaPointRecord[ tongDBID2 ], selfEntity.params["tongDBID2"] )
			else:
				baseMailbox.client.updateTongAbaPoint( selfEntity.params["tongName2"], 0, selfEntity.params["tongDBID2"] )

		if selfEntity.abaPlayers.isPlayerExist( playerDBID ):				# 如果玩家曾进来过
			selfEntity.abaPlayers.logonAgain( playerDBID, baseMailbox, tongDBID )	# 更新玩家的mailbox、tongDBID
		else:
			selfEntity.abaPlayers.addPlayer( playerDBID, playerName, self.playerInitBuyMark, tongDBID, tongName, baseMailbox )	# 第一次进来的玩家

		# 对每一个进入副本的玩家更新战果表，防止出现先进来的玩家看不到后进来的玩家的积分数据
		for player in selfEntity.abaPlayers.keys():
			selfEntity.abaPlayers.updatePlayerAbaRecord( selfEntity.abaPlayers[player]["baseMB"], selfEntity.abaPlayers[player]["playerDBID"] )

		player = baseMailbox.cell
		if BigWorld.entities.has_key( baseMailbox.id ):
			player = BigWorld.entities[ baseMailbox.id  ]

		if tongDBID == selfEntity.params["tongDBID1"]:	# 实在复杂啊
			if selfEntity.params["isRight"]:
				player.setTemp( "aba_right", True )
			else:
				player.setTemp( "aba_right", False )
		else:
			if selfEntity.params["isRight"]:
				player.setTemp( "aba_right", False )
			else:
				player.setTemp( "aba_right", True )

		player.setTemp( "tong_aba_sclass", selfEntity.className )			# 设置玩家所在副本的脚本名字，以便玩家和副本不在同一个server时可以找回副本

		player.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )
		player.lockPkMode()														#锁定pk模式，不能设置

		player.addHP( player.HP_Max )
		player.addMP( player.MP_Max )

		BigWorld.globalData[ "TongManager" ].onMemberEnter( tongDBID )

	def endEnter( self,selfEntity ):
		persistTime = selfEntity.getAbaTimeInfo()
		round = selfEntity.getAbaRound()
		selfEntity.abaPlayers.endEnter( round,persistTime )

		if self.isCurrentAbaOver( selfEntity ):
			return
		#if len( selfEntity.abaPointRecord ) == 1:		# 只有一个帮会进过副本，提前结束该场比赛
		#	self.onTongAbaOver( selfEntity )
		#	return
		tongDBID1 = selfEntity.params["tongDBID1"]
		tongDBID2 = selfEntity.params["tongDBID2"]

		if BigWorld.globalData.has_key("TongAba_signUp_one"):		# 只有一个帮会报名，入场结束马上结束当前副本
			selfEntity.setTemp( "tongAbaOver", True )
			if selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID1 ):
				BigWorld.globalData[ "TongManager" ].updateEnterTong( tongDBID1 )
				return
			else:
				selfEntity.abaPlayers.onTongAbaOver( selfEntity.abaRound, tongDBID1 )
				BigWorld.globalData[ "TongManager" ].onTongAbaOverFromSpace( tongDBID1,True )
				selfEntity.addTimer( 2, 0, GO_OUT_TIMER )		# 2秒钟后，把人传送出去
				return

		if selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID1 ) or selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID2 ):	# 有两个帮会进入副本，但是有一个在比赛开始前就跑光了，提前结束该场比赛
			selfEntity.setTemp( "tongAbaOver", True ) 	# 记录本场战争已经结束
			selfEntity.abaPlayers.spellProtect()
			selfEntity.addTimer( 2, 0, GO_OUT_TIMER )		# 2秒钟后，把人传送出去
			if selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID1 ) and not selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID2 ):
				selfEntity.abaPlayers.onTongAbaOver( selfEntity.abaRound, tongDBID2 )
				BigWorld.globalData[ "TongManager" ].onTongAbaOverFromSpace( tongDBID2,True )
				#BigWorld.globalData[ "TongManager" ].updateEnterTong( tongDBID1 )
			elif not selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID1 ) and selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID2 ):
				selfEntity.abaPlayers.onTongAbaOver( selfEntity.abaRound, tongDBID1 )
				BigWorld.globalData[ "TongManager" ].onTongAbaOverFromSpace( tongDBID1,True )
				#BigWorld.globalData[ "TongManager" ].updateEnterTong( tongDBID2 )
			elif selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID1 ) and selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID2 ):
				BigWorld.globalData[ "TongManager" ].onTongAbaOverFromSpaceNoWinner( tongDBID1,tongDBID2,True )
				#BigWorld.globalData[ "TongManager" ].updateEnterTong( tongDBID1 )
				#BigWorld.globalData[ "TongManager" ].updateEnterTong( tongDBID2 )

	def isCurrentAbaOver( self, selfEntity ):
		"""
		是否本副本战争已经结束
		"""
		return selfEntity.queryTemp( "tongAbaOver", False )

	def isAllAbaOver( self ):
		"""
		是否擂台赛时间已经结束了
		"""
		return BigWorld.globalData["tongAbaStep"]


	def packedSpaceDataOnLeave( self, entity ):
		"""
		获取entity离开时，向所在的space发送离开该space消息的额外参数；
		@param entity: 想要向space entity发送离开该space消息(onLeave())的entity（通常为玩家）
		@return: dict，返回要离开的space所需要的entity数据。如，有些space可能会需要比较离开的玩家名字与当前记录的玩家的名字，这里就需要返回玩家的playerName属性
		"""
		packDict = SpaceCopyTeam.packedSpaceDataOnLeave( self, entity )
		packDict[ "playerDBID" ] = entity.databaseID
		packDict[ "playerName" ] = entity.playerName
		packDict[ "tongDBID" ] = entity.tong_dbID
		return packDict

	def onLeaveCommon( self, selfEntity, baseMailbox, params  ):
		"""
		一个entity准备离开space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onLeave()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 要离开此space的entity mailbox
		@param params: dict; 离开此space时需要的附加数据。此数据由当前脚本的packedDataOnLeave()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopyTeam.onLeaveCommon( self, selfEntity, baseMailbox, params  )
		player = baseMailbox.cell
		if BigWorld.entities.has_key( baseMailbox.id ):
			player = BigWorld.entities[ baseMailbox.id  ]
			player.unLockPkMode()		# 解锁pk模式（找到/没找到playerEntity的解锁必须分开，否则：setPkMode可能在unLockPkMode之前执行）
		else:
			player.unLockPkMode()		# 解锁pk模式
		player.setSysPKMode( 0 )

		playerDBID = params["playerDBID"]
		tongDBID = params["tongDBID"]
		player.addHP( player.HP_Max )
		player.addMP( player.MP_Max )
		player.tong_clearWarItems()
		#player.spellTarget( 122155001, player.id )

		baseMailbox.client.tong_onLeaveWarSpace()

		if not self.isCurrentAbaOver( selfEntity ):
			BigWorld.globalData[ "TongManager" ].onMemberLeave( tongDBID )
		BigWorld.globalData["TongManager"].recordRound( playerDBID, csdefine.MATCH_TYPE_TONG_ABA, selfEntity.getAbaRound(), baseMailbox )

		selfEntity.abaPlayers.playerLeave( playerDBID )		# 清除离开玩家数据

		if selfEntity.getAbaTimeInfo() >= 5 * 60:
			baseMailbox.client.onStatusMessage( csstatus.TONG_COMPETETION_LEAVE,"" )

		if tongDBID == selfEntity.params["tongDBID1"]:
			tongName = selfEntity.params["tongName1"]
		elif tongDBID == selfEntity.params["tongDBID2"]:
			tongName = selfEntity.params["tongName2"]

		# 是否家族成员中途全部离开，结束当前副本的比赛
		if selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID ):
			selfEntity.abaPlayers.updateTongAbaPoint( tongName, -1 , tongDBID )
			DEBUG_MSG( "--------->>>time", BigWorld.time() )
			if selfEntity.getAbaTimeInfo() >= 5 * 60:			# 在比赛过程中，如果一个帮会跑光了，提前结束比赛
				self.onTongAbaOver( selfEntity )
			else:
				BigWorld.globalData[ "TongManager" ].updateEnterTong( tongDBID )

	def onPlayerDied( self, selfEntity, killerDBID, killer, beKillerDBID, beKiller ):
		"""
		玩家死亡，重新计算积分
		"""
		# 如果战争已经结束 那么不允许再计算积分
		if self.isCurrentAbaOver( selfEntity ) or self.isAllAbaOver():
			return

		kTongDBID = selfEntity.abaPlayers.getPlayerTongDBID( killerDBID )
		bkTongDBID = selfEntity.abaPlayers.getPlayerTongDBID( beKillerDBID )

		# 是自己帮会人杀的不扣分
		if kTongDBID == bkTongDBID:
			return

		# 更新玩家的战果报表
		selfEntity.abaPlayers.updateRecord( killerDBID, beKillerDBID )
		# 被杀者，增加购买物品的积分
		self.changeAbaBuyPoints( selfEntity, beKiller, beKillerDBID, self.playerOnDiedAddBuyMark )

		# 该家族人被杀了,扣除100分
		selfEntity.abaPointRecord[ bkTongDBID ] -= self.bekillPunish
		tongName = selfEntity.abaPlayers.getPlayerTongName( beKillerDBID )
		if selfEntity.abaPointRecord[ bkTongDBID ] <= 0:
			selfEntity.abaPointRecord[ bkTongDBID ] = 0
			self.onTongAbaOver( selfEntity )
			selfEntity.abaPlayers.updateTongAbaPoint( tongName, -1,bkTongDBID )
		else:
			selfEntity.abaPlayers.updateTongAbaPoint( tongName, selfEntity.abaPointRecord[ bkTongDBID ],bkTongDBID )

		# 通知这些帮会成员某某被杀；或者杀了某某
		self.sendTongWarPlayerDieInfo( False, bkTongDBID, beKillerDBID )
		if kTongDBID > 0:
			self.sendTongWarPlayerDieInfo( True, kTongDBID, killerDBID )

	def sendTongWarPlayerDieInfo( self, isKiller, tongDBID, playerDBID ):
		"""
		通知某帮会 某个成员杀了一个敌人,或者被敌人杀了
		"""
		k = "tong.%i" % tongDBID
		try:
			tongMailbox = BigWorld.globalData[ k ]
		except KeyError:
			ERROR_MSG( "tong %s not found." % k )
			return
		tongMailbox.onWarKillerPlayer( isKiller, playerDBID )		# 使用统一的接口，不需重新定义

	def onTongAbaOver( self, selfEntity ):
		"""
		擂台赛结束了，给玩家加上相应奖励，通知管理器
		"""
		if self.isCurrentAbaOver( selfEntity ):
			return
		#if self.isAllAbaOver():
		#	return
		selfEntity.setTemp( "tongAbaOver", True ) 	# 记录本场战争已经结束
		selfEntity.abaPlayers.spellProtect()
		winnerDBID = self.getWinnerDBID( selfEntity )
		if winnerDBID != 0:
			BigWorld.globalData[ "TongManager" ].onTongAbaOverFromSpace( winnerDBID, False )				# 通知擂台管理器，某场战争提前结束了
		else:
			tongDBID1 = selfEntity.params["tongDBID1"] #selfEntity.abaPointRecord.keys()
			tongDBID2 = selfEntity.params["tongDBID2"]
			BigWorld.globalData[ "TongManager" ].onTongAbaOverFromSpaceNoWinner( tongDBID1, tongDBID2, False )				# 通知擂台管理器，某场战争结束了,没有胜利者

		selfEntity.abaPlayers.onTongAbaOver( selfEntity.abaRound, winnerDBID )

		selfEntity.addTimer( 2 * 60, 0, GO_OUT_TIMER )		# 2分钟后，把人传送出去

	def getWinnerDBID( self, selfEntity ):
		"""
		取胜利帮会的dbid
		"""
		winnerDBID = 0
		tongDBID1 = selfEntity.params["tongDBID1"]
		tongDBID2 = selfEntity.params["tongDBID2"]
		if selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID1 ) and not selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID2 ):
			winnerDBID = tongDBID2
			return winnerDBID
		if selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID2 ) and not selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID1 ):
			winnerDBID = tongDBID1
			return winnerDBID
		if selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID1 ) and selfEntity.abaPlayers.isTongAllPlayerLeave( tongDBID2 ):
			return winnerDBID


		pointList = selfEntity.abaPointRecord.values()
		# 如果2个家族都在
		pointReverseDict = dict( map( None, selfEntity.abaPointRecord.values(), selfEntity.abaPointRecord.keys() ) )
		if pointList[0] > pointList[1]:
			winnerDBID = pointReverseDict[pointList[0]]
		elif pointList[0] < pointList[1]:
			winnerDBID = pointReverseDict[pointList[1]]
		return winnerDBID

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if userArg == END_ENTER_TIMER:
			self.endEnter( selfEntity )
		elif userArg == GO_OUT_TIMER:
			selfEntity.abaPlayers.onTelportPlayer()
			selfEntity.addTimer( 10.0, 0.0, Const.SPACE_TIMER_ARG_CLOSE )		# 需要延迟10s关闭副本
			return
		else:
			SpaceCopyTeam.onTimer( self, selfEntity, id, userArg )

		tongAbaOverTimer = selfEntity.queryTemp( "tongAbaOverTimer" )
		if tongAbaOverTimer == id:
			selfEntity.cancel( selfEntity.queryTemp( "tongAbaOverTimer" ) )
			checkPlayerCount = selfEntity.queryTemp( "checkPlayerCount", 0 )
			if checkPlayerCount <= 0:
				self.onTongAbaOver( selfEntity )
				# 检测到没人了,那么关闭副本
				if not selfEntity.abaPlayers.hasPlayer():
					selfEntity.base.closeSpace( True )
				else:
					selfEntity.setTemp( "checkPlayerCount", 1 )
					selfEntity.setTemp( "tongAbaOverTimer", selfEntity.addTimer( 2 * 60, 0, 1 ) )
			elif checkPlayerCount == 1:
				# 结束3分钟后 不管玩家是否自动离开 都将直接踢出
				selfEntity.setTemp( "checkPlayerCount", 2 )
				selfEntity.setTemp( "tongAbaOverTimer", selfEntity.addTimer( 1 * 60, 0, 1 ) )
			elif checkPlayerCount == 2:
				selfEntity.base.closeSpace( True )

	def onPlayerRelive( self, selfEntity, playerID, playerDBID ):
		"""
		做个复活回调， 主要是在副本结束后 角色未复活， 副本会施放无敌BUFF，
		等角色复活后 会处于无保护状态， 所以
		回调到副本， 副本会给他重新加上
		"""
		if self.isCurrentAbaOver( selfEntity ) or self.isAllAbaOver():
			if BigWorld.entities.has_key( playerID ):
				BigWorld.entities[ playerID ].spellTarget( 122156001, playerID )
			else:
				try:
					selfEntity.abaPlayers[ playerDBID ][ "baseMB" ].cell.spellTarget( 122156001, playerID )
				except:
					DEBUG_MSG( "-------->>>player's databaseID( %i ) not in the space." % playerDBID )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡
		"""
		if not killer:	# 没找到杀人者，非正常死亡不处理，直接返回
			DEBUG_MSG( "player( %s ) has been killed,can't find killer." % role.getName() )
			return
		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = killer.getOwner()
			if owner.etype == "MAILBOX" : return
			killer = owner.entity
		if killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if role.tong_dbID == killer.tong_dbID:
				role.calcPkValue( killer )
			else:
				spaceBase = role.getCurrentSpaceBase()
				spaceEntity = BigWorld.entities.get( spaceBase.id )
				if spaceEntity and spaceEntity.isReal():
					self.onPlayerDied( spaceEntity, killer.databaseID, killer, role.databaseID, role )
				else:
					spaceBase.cell.remoteScriptCall( "onPlayerDied", ( killer.databaseID, killer, role.databaseID, role ) )
				#role.tong_warItemsDropOnDied()

	def onNPCDealItemChangeAbaMark( self, selfEntity, player, databaseID, mark, state ):
		"""
		由与NPC买或者卖商品导致的积分改变
		"""
		ret = 1
		if state == 0: # 玩家买了1个战场物品
			if selfEntity.abaPlayers[ databaseID ]["buyPoints"] < mark:
				ret = 0
			else:
				self.changeAbaPointRecord( selfEntity, databaseID, player.tong_dbID, -mark )
				self.changeAbaBuyPoints( selfEntity, player, databaseID, -mark )
			player.onTongAbaBuyFromNPCCallBack( ret )
			#----------------------------------------------------------------
		elif state == 1: # 玩家买了1个以上战场物品
			if selfEntity.abaPlayers[ databaseID ]["buyPoints"] < mark:
				ret = 0
			else:
				self.changeAbaPointRecord( selfEntity, databaseID, player.tong_dbID, -mark )
				self.changeAbaBuyPoints( selfEntity, player, databaseID, -mark )
			player.onTongAbaBuyArrayFromNPCCallBack( ret )
			#----------------------------------------------------------------
		elif state == 2: # 玩家出售了战场物品 增加积分
			self.changeAbaPointRecord( selfEntity, databaseID, player.tong_dbID, mark )

	def changeAbaPointRecord( self, selfEntity, databaseID, tongDBID, mark ):
		"""
		帮会积分变更
		"""
		tongName = selfEntity.abaPlayers.getPlayerTongName( databaseID )
		selfEntity.abaPointRecord[ tongDBID ] += mark
		if selfEntity.abaPointRecord[ tongDBID ] <= 0:
			selfEntity.abaPointRecord[ tongDBID ] = 0
			self.onTongAbaOver( selfEntity )
			selfEntity.abaPlayers.updateTongAbaPoint( tongName, -1,tongDBID )
			return

		selfEntity.abaPlayers.updateTongAbaPoint( tongName, selfEntity.abaPointRecord[ tongDBID ],tongDBID )

	def changeAbaBuyPoints( self, selfEntity, player, databaseID, mark ):
		"""
		角色的购买积分
		"""
		selfEntity.abaPlayers[ databaseID ]["buyPoints"] += mark
		player.client.tong_updateAbaBuyPoint( selfEntity.abaPlayers[ databaseID ]["buyPoints"] )
