# -*- coding: gb18030 -*-
#
#

from bwdebug import *
import BigWorld
import csdefine
import csconst
import csstatus



class AbaPlayerDataType( dict ):
	"""
	帮会擂台赛副本玩家信息数据
	"""
	def __init__( self ):
		"""
		"""
		pass


	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		abaPlayerList = []
		dAbaPlayers = { "items":abaPlayerList }
		for playerDBID, abaPlayerItem in obj.iteritems():
			abaPlayerList.append( abaPlayerItem )
		return dAbaPlayers


	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.

		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = AbaPlayerDataType()
		for abaPlayerItem in dict[ "items" ]:
			playerDBID = abaPlayerItem[ "playerDBID" ]
			obj[ playerDBID ] = abaPlayerItem
		return obj


	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, AbaPlayerDataType )


	def isPlayerExist( self, playerDBID ):
		"""
		玩家是否已经存在，即玩家曾经进过副本
		"""
		return self.has_key( playerDBID )


	def addPlayer( self, playerDBID, playerName, playerInitBuyPoint, tongDBID, tongName, baseMailbox  ):
		"""
		增加一个玩家数据
		"""
		self[ playerDBID ] = { "playerDBID":playerDBID,
								"playerName":playerName,
								"buyPoints":playerInitBuyPoint,
								"killNum":0,
								"beKilledNum":0,
								"tongDBID":tongDBID,
								"tongName":tongName,
								"baseMB":baseMailbox,
							}
		baseMailbox.client.tong_updateAbaBuyPoint( playerInitBuyPoint )

	def updateRecord( self, killerDBID, beKillerDBID ):
		"""
		玩家的战果报表放生变化

		@param killerDBID : 杀人者的dbid
		@type killerDBID : DATABASE_ID
		@param beKillerDBID : 被杀者的dbid
		@type beKillerDBID : DATABASE_ID
		"""
		self[ killerDBID ][ "killNum" ] += 1
		self[ beKillerDBID ][ "beKilledNum" ] += 1

		for playerItem in self.itervalues():	# 所有玩家，更新战果表
			if playerItem["baseMB"]:
				playerItem["baseMB"].client.updatePlayerAbaRecord( self[killerDBID]["playerName"], self[killerDBID]["killNum"], self[killerDBID]["beKilledNum"], self[killerDBID]["tongDBID"] )
				playerItem["baseMB"].client.updatePlayerAbaRecord( self[beKillerDBID]["playerName"],self[beKillerDBID]["killNum"],self[beKillerDBID]["beKilledNum"],self[beKillerDBID]["tongDBID"] )

	def logonAgain( self, playerDBID, baseMailbox, tongDBID ):
		"""
		玩家重新登录
		"""
		self[ playerDBID ][ "baseMB" ] = baseMailbox
		self[ playerDBID ][ "tongDBID" ] = tongDBID
		playerInitBuyPoint = self[ playerDBID ]["buyPoints"]
		baseMailbox.client.tong_updateAbaBuyPoint( playerInitBuyPoint )
	
	def endEnter( self,round,persistTime):
		"""
		结束入场时候该函数被副本调用
		"""
		for key,info in self.iteritems():
			playerBase = info["baseMB"]
			if not playerBase:
				continue
			level = BigWorld.entities[ playerBase.id ].getLevel()
			playerBase.client.tong_onInitRemainAbaTime( persistTime,round )		# 初始化玩家客户端擂台赛数据:擂台赛剩余时间
			BigWorld.globalData["TongManager"].recordJoinPlayer( info["playerName"],playerBase,level )
			
			player = BigWorld.entities[ playerBase.id ]
			player.lockPkMode()
			player.setSysPKMode( csdefine.PK_CONTROL_PROTECT_TONG )	#强制玩家进入帮会pk 状态

	def updatePlayerAbaRecord( self, baseMailbox, playerDBID ):
		"""
		把战果表更新到指定玩家客户端

		@param baseMailbox : 玩家base mailbox
		@param baseMailbox : MAILBOX
		"""
		for playerDBID, abaPlayerItem in self.iteritems():
			baseMailbox.client.updatePlayerAbaRecord( abaPlayerItem["playerName"], abaPlayerItem["killNum"], abaPlayerItem["beKilledNum"], abaPlayerItem["tongDBID"] )

		for playerItem in self.itervalues():	# 同时，把自己的信息更新给其他玩家
			if playerItem["baseMB"]:
				playerItem["baseMB"].client.updatePlayerAbaRecord( self[playerDBID]["playerName"], self[playerDBID]["killNum"], self[playerDBID]["beKilledNum"], self[playerDBID]["tongDBID"] )

	def removePlayer( self, playerDBID ):
		"""
		移除一个玩家数据
		"""
		if self.has_key( playerDBID ):
			del self[ playerDBID ]


	def playerLeave( self, playerDBID ):
		"""
		玩家离开副本，tongDBID，为了判断--是否帮会的所有成员离开；但是，要保存其他数据

		@param playerDBID : 玩家dbid
		@param playerDBID : DATABASE_ID
		"""
		self[ playerDBID ][ "tongDBID" ] = 0
		self[ playerDBID ][ "baseMB" ] = None

	def isTongAllPlayerLeave( self, tongDBID ):
		"""
		是否帮会的所有成员离开了
		"""
		for playerItem in self.itervalues():
			if playerItem["tongDBID"] == tongDBID:
				return False
		return True


	def getPlayerTongDBID( self, playerDBID ):
		"""
		获得玩家的帮会dbid
		"""
		return self[ playerDBID ][ "tongDBID" ]


	def getPlayerTongName( self, playerDBID ):
		"""
		由玩家的dbid获得玩家的帮会名字
		"""
		return self[ playerDBID ][ "tongName" ]


	def updateTongAbaPoint( self, tongName, point,tongDBID ):
		"""
		更新帮会积分到每一个玩家的客户端
		"""
		for playerItem in self.itervalues():
			if playerItem["baseMB"]:
				playerItem["baseMB"].client.updateTongAbaPoint( tongName, point, tongDBID )


	def onTongAbaOver( self, awardLevel, winnerTongDBID ):
		"""
		擂台赛结束后续处理，给玩家加上相应奖励，给所有玩家加上无敌buff

		@param awardLevel : 比赛轮次，据此决定奖励级别
		@type awardLevel : INT8
		@param winnerDBID : 胜利帮会的dbid
		@type winnerDBID : DATABASE_ID
		"""
		for playerItem in self.itervalues():
			playerBase = playerItem["baseMB"]
			if playerBase is None:
				continue

			if BigWorld.entities.has_key( playerBase.id ):
				player = BigWorld.entities[ playerBase.id ]
					
				if playerItem["tongDBID"] == winnerTongDBID and winnerTongDBID != 0:
					if not BigWorld.globalData.has_key("TongAba_signUp_one"):		# 如果是只有一个帮会报名的情况，不给胜利奖
						winExp =  ( int( pow( player.level,1.2 ) * 5 ) + 25 ) * 70 * ( 4 * awardLevel + 6 )	# 获胜奖励经验值
						player.addExp( winExp,csdefine.REWARD_TONG_ABA_EXP )
					if awardLevel == csdefine.ABATTOIR_FINAL or BigWorld.globalData.has_key("TongAba_signUp_one"):		# 如果是只有一个帮会报名的情况，同样给予冠军奖
						if BigWorld.globalData.has_key( "tongAbattoirChampionDBID" ):
							temp = BigWorld.globalData[ "tongAbattoirChampionDBID" ]
							temp.append( player.databaseID )
							BigWorld.globalData[ "tongAbattoirChampionDBID" ] = temp
					
				player.unLockPkMode()
				player.setPkMode( player.id, csdefine.PK_CONTROL_PROTECT_PEACE )
				player.lockPkMode()
				player.client.tong_onTongAbaOver()
	
	def onTelportPlayer( self ):
		"""
		玩家离开副本的处理
		"""
		for playerItem in self.itervalues():
			playerBase = playerItem["baseMB"]
			if playerBase is None:
				continue
			
			if BigWorld.entities.has_key( playerBase.id ):
				BigWorld.entities[ playerBase.id ].tong_onAbattoirOver()
			else:
				playerBase.cell.tong_onAbattoirOver()

	def spellProtect( self ):
		"""
		加上无敌buff
		"""
		for playerItem in self.itervalues():
			playerBase = playerItem["baseMB"]
			if playerBase is None:
				continue

			if BigWorld.entities.has_key( playerBase.id ):
				player = BigWorld.entities[ playerBase.id ]
				player.spellTarget( 122156001, player.id )		# 给玩家加上无敌buff
			else:
				playerBase.cell.remoteCall( "spellTarget", ( 122156001, playerBase.id ) )

	def hasPlayer( self ):
		"""
		副本中是否还有玩家
		"""
		for playerItem in self.itervalues():
			if playerItem["baseMB"] is not None:
				return True
		return False


instance = AbaPlayerDataType()
