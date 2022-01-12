# -*- coding: gb18030 -*-
import copy
import random

import csdefine
import csstatus
import cschannel_msgs

AO_ZHEN_FAILURE_ENTER_NUM = {
	1	:	5,			#2人比赛的时候，即决赛
	2	:	3,			#4人比赛的时候，即半决赛
	4	:	2,			#8人比赛的时候，即1/4决赛
	8	:	1,			#16人比赛的时候，即1/8决赛
	16	:	0,			#32人比赛的时候，即1/16决赛
	32	:	0,			#64人比赛的时候，即1/32决赛
}

class AoZhanPlayerInfo( object ):
	def __init__( self ):
		object.__init__( self )
		self.databaseID = 0
		self.playerName = ""
		self.playerLevel = 0
		self.playerClass = 0
		self.playerMailBox = None
	
	def init( self, databaseID, playerName, playerLevel, playerClass, playerMailBox ):
		self.databaseID = databaseID
		self.playerName = playerName
		self.playerLevel = playerLevel
		self.playerClass = playerClass
		self.playerMailBox = playerMailBox
		
	def getDictFromObj( self, obj ):
		dict = {}
		dict[ "databaseID" ] = obj.databaseID
		dict[ "playerName" ] = obj.playerName
		dict[ "playerLevel" ] = obj.playerLevel
		dict[ "playerClass" ] = obj.playerClass
		dict[ "playerMailBox" ] = obj.playerMailBox
		return dict

	def createObjFromDict( self, dict ):
		obj = AoZhanPlayerInfo()
		obj.init( dict[ "databaseID" ], dict[ "playerName" ], dict[ "playerLevel" ], dict[ "playerClass" ], dict[ "playerMailBox" ] )
		return obj
		
	def isSameType( self, obj ):
		return isinstance( obj, AoZhanPlayerInfo )

class AoZhanRoom( object ):
	"""
	一个房间
	"""
	def __init__( self ):
		object.__init__( self )
		self.aPlayer = 0
		self.bPlayer = 0
		self.failureList = []
		self.score = 0
		self.useTime = 0.0
		self.remainHP = 0
		self.winner = 0
		self.matchType = 0
		self.rIndex = 0
	
	def init( self, mgr, aPlayer, bPlayer, failureList,matchType, index ):
		self.aPlayer = aPlayer
		self.bPlayer = bPlayer
		self.failureList = failureList
		self.matchType = matchType
		self.rIndex = index
		if bPlayer ==0 and len( failureList ) == 0:#轮空
			self.winner = aPlayer
			self.useTime = 0.0
			if mgr.getplayerMailBox( self.winner ):
				mgr.getplayerMailBox( self.winner ).client.onStatusMessage( csstatus.AO_ZHAN_QUN_XIONG_BYE, "" )
		else:
			if mgr.getplayerMailBox( self.aPlayer ):
				mgr.getplayerMailBox( self.aPlayer ).client.onStatusMessage( csstatus.AO_ZHAN_QUN_XIONG_OPEN, "" )
			
			if mgr.getplayerMailBox( self.bPlayer ):
				mgr.getplayerMailBox( self.bPlayer ).client.onStatusMessage( csstatus.AO_ZHAN_QUN_XIONG_OPEN, "" )
			
			if len( self.failureList ):
				for fid in self.failureList:
					if mgr.getplayerMailBox( fid ):
						mgr.getplayerMailBox( fid ).client.onStatusMessage( csstatus.AO_ZHAN_QUN_XIONG_FAILURE_OPEN, "" )
	
	def setResult( self, mgr, winner, score, useTime, remainHP ):
		self.winner = winner
		self.score = score
		self.remainHP = remainHP
		self.useTime = useTime
		if self.aPlayer == winner and self.bPlayer:
			mgr.rewarJoinWin( self.bPlayer )
		elif self.bPlayer == winner and self.aPlayer:
			mgr.rewarJoinWin( self.bPlayer )
			
		if winner and self.matchType != 1: #不是决赛
			mgr.getplayerMailBox( winner ).client.onStatusMessage( csstatus.AO_ZHAN_QUN_XIONG_RESULT, "" )
		
			if self.aPlayer and self.aPlayer != winner:
				mgr.getplayerMailBox( self.aPlayer ).client.onStatusMessage( csstatus.AO_ZHAN_QUN_XIONG_FAILURE, "" )
			
			if self.bPlayer and self.bPlayer != winner:
				mgr.getplayerMailBox( self.bPlayer ).client.onStatusMessage( csstatus.AO_ZHAN_QUN_XIONG_FAILURE, "" )
			
	def isWin( self ):
		if self.winner:
			return True
		else:
			return False
	
	def isJoin( self, playerDBID ):
		if playerDBID == self.aPlayer or playerDBID ==  self.bPlayer or playerDBID in self.failureList:
			return True
		
		return False
	
	def getScore( self ):
		return self.score
	
	def gerRoomKey( self ):
		return self.rIndex
	
	def pickDictToSpace( self ):
		dict = {}
		dict[ "aPlayer" ] = self.aPlayer
		dict[ "bPlayer" ] = self.bPlayer
		dict[ "failureList" ] = self.failureList
		return dict
	
	def getDictFromObj( self, obj ):
		dict = {}
		dict[ "aPlayer" ] = obj.aPlayer
		dict[ "bPlayer" ] = obj.bPlayer
		dict[ "failureList" ] = obj.failureList
		dict[ "score" ] = obj.score
		dict[ "useTime" ] = obj.useTime
		dict[ "remainHP" ] = obj.remainHP
		dict[ "winner" ] = obj.winner
		dict[ "matchType" ] = obj.matchType
		dict[ "rIndex" ] = obj.rIndex
		return dict
	
	def createObjFromDict( self, dict ):
		obj = AoZhanRoom()
		obj.aPlayer = dict[ "aPlayer" ]
		obj.bPlayer = dict[ "bPlayer" ]
		obj.failureList = dict[ "failureList" ]
		obj.score = dict[ "score" ]
		obj.useTime = dict[ "useTime" ]
		obj.remainHP = dict[ "remainHP" ]
		obj.winner = dict[ "winner" ]
		obj.matchType = dict[ "matchType" ]
		obj.rIndex = dict[ "rIndex" ]
		return obj
		
	def isSameType( self, obj ):
		return isinstance( obj, AoZhanRoom )

class AoZhanRoundBase( object ):
	"""
	一轮比赛
	"""
	def __init__( self, matchType = 0 ):
		object.__init__( self )
		self.joinList = []
		self.failureList = []
		
		self._disInfos = []
		self.matchType = matchType
		
		self.nextWinner = [] #晋级下轮列表
		
		self._type = 0
	
	def init( self, winnerList, failureList ):
		self.joinList = winnerList
		self.failureList = failureList
	
	def getRoundRooms( self ):
		return self._disInfos

	def setResult( self, mgr, roomNum, winner, score, useTime, remainHP ):
		"""
		结果
		"""
		self._disInfos[ roomNum ].setResult( mgr, winner, score, useTime, remainHP )
	
	def getType( self ):
		return self._type
	
	def getNextList( self ):
		"""
		获取下场参与者
		"""
		if not len( self.nextWinner ):
			self.nextWinner = self.calculateNextList()
			
		return self.nextWinner
	
	def calculateNextList( self ):
		return []
	
	def getNextFailure( self ):
		"""
		获取下场失败者
		"""
		result = list( set( self.joinList ) ^ set( self.getNextList() ) )
		result.extend( self.failureList )
		return result
	
	def getCurRoundFailure( self ):
		return list( set( self.joinList ) ^ set( self.getNextList() ) )
	
	def getEnterRoom( self, playerDBID ):
		for r in self._disInfos:
			if r.isJoin( playerDBID ):
				return r
		
		return None
	
	def _getPromotedNum( self ):
		return self.matchType
	
	def getDictFromObj( self, obj ):
		dict = {}
		dict[ "joinList" ] = obj.joinList
		dict[ "failureList" ] = obj.failureList
		dict[ "_disInfos" ] = obj._disInfos
		dict[ "matchType" ] = obj.matchType
		dict[ "_type" ] = obj._type
		return dict
	
	def createObjFromDict( self, dict ):
		obj = None
		if dict[ "_type" ] == csdefine.AO_ZHAN_ROOM_TYPE_NO_FAILURE:
			obj = AoZhanRoundNoFailure( dict[ "matchType" ] )
		else:
			obj = AoZhanRoundHasFailure( dict[ "matchType" ] )
			
		obj.joinList = dict[ "joinList" ]
		obj.failureList = dict[ "failureList" ]
		obj._disInfos = dict[ "_disInfos" ]
		return obj
		
	def isSameType( self, obj ):
		return isinstance( obj, AoZhanRoundBase )

class AoZhanRoundNoFailure( AoZhanRoundBase ):
	#没有失败者
	def __init__( self, matchType ):
		AoZhanRoundBase.__init__( self, matchType )
		self._type = csdefine.AO_ZHAN_ROOM_TYPE_NO_FAILURE
		
	def dis( self, mgr ):
		#分配
		disList = copy.deepcopy( self.joinList )
		index = 0
					
		while len( disList ):
			aPlayer = random.choice( disList )
			disList.remove( aPlayer )
			bPlayer = 0
			if len( disList ):
				bPlayer = random.choice( disList )
				disList.remove( bPlayer )
			
			room = AoZhanRoom()
			room.init( mgr, aPlayer, bPlayer, [], self.matchType, index )
			index += 1
			self._disInfos.append( room )
	
	def calculateNextList( self ):
		#计算下轮名单
		result = []
		for r in self._disInfos:
			result.append( r.winner )
			
		self.nextWinner = copy.deepcopy( result )
		return result

class AoZhanRoundHasFailure( AoZhanRoundBase ):
	#有失败者
	def __init__( self, matchType ):
		AoZhanRoundBase.__init__( self, matchType )
		self._type = csdefine.AO_ZHAN_ROOM_TYPE_HAS_FAILURE
	
	def dis( self, mgr ):
		#分配
		disList = copy.deepcopy( self.joinList )
		disFailureList = copy.deepcopy( self.failureList )
		index = 0
		while len( disList ):
			wPlayer = random.choice( disList )
			disList.remove( wPlayer )
			fNum = AO_ZHEN_FAILURE_ENTER_NUM[ self.matchType ]
			flist= []
			for i in xrange( fNum ):
				if not len(disFailureList):
					break
				fPlayer = random.choice( disFailureList )
				disFailureList.remove( fPlayer )
				flist.append( fPlayer )
			
			room = AoZhanRoom()
			room.init( mgr, wPlayer, 0, flist, self.matchType, index )
			index += 1
			self._disInfos.append( room )
	
	def calculateNextList( self ):
		"""
		计算下轮名单
		"""
		result = []
		winList = []
		promotedNum = self._getPromotedNum() # 当场比赛晋级人数
		disWinnerLen = len( self.joinList ) #要分配胜利者的名单
		
		#取得获胜房间名单
		for r in self._disInfos:
			if r.isWin():
				winList.append( r )
		
		if len( winList ) > promotedNum: #如果获胜的名单大于晋级名单
			winList.sort( key = lambda r : r.useTime, reverse = True ) #按战斗结束时间排序
			hpSortList = copy.deepcopy( winList )
			hpSortList.sort( key = lambda r : r.remainHP, reverse = False )
			
			wLen = len( winList )
			undetermined = []	#待定列表
			
			for i, item in enumerate( winList ):
				if len( result ) >= promotedNum:
					break
				
				nextItem = winList[ i + 1 ]	#理论上这里不会出错
				if item.useTime <= nextItem.useTime and len( result ) < promotedNum:
					result.append( item.winner )
					remain = promotedNum - len( result )	#还剩多少晋级位置
					if remain <= 0:
						break
					elif remain < len( undetermined ): #如果待定里面小于剩余晋位置，则全加入晋级名单
						for it in undetermined:
							result.append( it.winner )
						
						undetermined = []
					else:
						def getMaxRemainHP( objList ):
							maxRemainHP = None 
							for obj in objList:
								if not maxRemainHP:
									maxRemainHP = obj
								else:
									if maxRemainHP.remainHP > obj.remainHP:
										maxRemainHP = obj
							return maxRemainHP
										
						for i in xrange( remain ):
							obj = getMaxRemainHP( undetermined ) #根据血量来获胜
							undetermined.remove( obj )
							result.append( obj.winner )
						
						undetermined = []
						break
				else:
					undetermined.append( item )
		else:	#如果获胜的名单小于晋级名单
			result.extend( winList )#把所有获胜名单都加进晋级列表中
				
			if len( self.joinList ) > promotedNum:
				failList = []
				for r in self._disInfos: #取得所有失败房间的列表
					if not r.isWin():
						failList.append( r )
						
				remain = promotedNum - len( result ) #取得剩余晋级名额
				
				failList.sort( key = lambda r : r.score, reverse = False ) #进行积分排序
				undetermined = []	#待定名单
				for i, item in enumerate( failList ):
					if len( result ) >= promotedNum:
						break
						
					nextItem = failList[ i + 1 ] #理论上这里永远不会出错
					if item.score >= nextItem.score:
						result.append( item.aPlayer )
						remain = promotedNum - len( result )	#还剩多少晋级位置
						if remain < len( undetermined ):
							for it in undetermined:
								result.append( it.aPlayer )
							
							undetermined = []
						else:
							for i in xrange( remain ):
								randomWinner = random.choice( undetermined )
								undetermined.remove( randomWinner )
								result.append( randomWinner.winner )
							
							undetermined = []
							break
					else:
						undetermined.append( item )
						
		self.nextWinner = copy.deepcopy( result )
		return result


class AoZhanDataMgr( object ):
	def __init__( self ):
		self.joinDatas = {}
		self.infos = {}
	
	def addJoin( self, playerDBID, playerName, playerLevel, playerClass, playerMailBox ):
		playerInfos = AoZhanPlayerInfo()
		playerInfos.init( playerDBID, playerName, playerLevel, playerClass, playerMailBox )
		self.joinDatas[ playerDBID ] = playerInfos

	def getplayerMailBox( self, playerDBID ):
		if self.joinDatas.has_key( playerDBID ):
			return self.joinDatas[ playerDBID ].playerMailBox
		
		return None
	
	def getPlayerName( self, playerDBID ):
		if self.joinDatas.has_key( playerDBID ):
			return self.joinDatas[ playerDBID ].playerName
		
		return ""
	
	def getPlayerLevel( self, playerDBID ):
		if self.joinDatas.has_key( playerDBID ):
			return self.joinDatas[ playerDBID ].playerLevel
		
		return 0

	def getPlayerClass( self, playerDBID ):
		if self.joinDatas.has_key( playerDBID ):
			return self.joinDatas[ playerDBID ].playerClass
		
		return 0
	
	def getFailPlayerWinNum( self, databaseID ):
		"""
		获取失败组玩家的胜场
		"""
		winNum = 0
		for info in self.infos.itervalues():
			room = info.getEnterRoom( databaseID )
			if room and databaseID in room.failureList and not room.isWin():
				winNum += 1
		
		return winNum
	
	def getMaxJoinFailPlayer( self ):
		"""
		获取参与失败场数最多的玩家
		"""
		maxJoinPlayer = 0
		maxJoinRound = 0
		for info in self.joinDatas.itervalues():
			if self.getFailPlayerWinNum( info.databaseID ) > maxJoinRound:
				maxJoinPlayer = info
		
		return maxJoinPlayer
	
	def getFaulureJoinRound( self, databaseID ):
		joinNum = 0
		for info in self.infos.itervalues():
			room = info.getEnterRoom( databaseID )
			if room and databaseID in room.failureList:
				joinNum += 1
		
		return joinNum
	
	def getWinnerJoinRound( self, databaseID ):
		joinNum = 0
		for info in self.infos.itervalues():
			room = info.getEnterRoom( databaseID )
			if room and ( databaseID == room.aPlayer or databaseID == room.aPlayer ):
				joinNum += 1
		
		return joinNum
	
	
	def resert( self ):
		self.joinDatas = {}
		self.infos = {}
	
	def getDictFromObj( self, obj ):
		dict = {}
		dict[ "joinDatas" ] = obj.joinDatas.values()
		dict[ "infos" ] = obj.infos.values()
		return dict
	
	def createObjFromDict( self, dict ):
		obj = AoZhanDataMgr()
		for d in dict[ "joinDatas" ]:
			obj.joinDatas[ d.databaseID ] = d
		
		for info in dict[ "infos" ]:
			obj.infos[ info.matchType ] = info

		return obj
		
	def isSameType( self, obj ):
		return isinstance( obj, AoZhanDataMgr )
		
g_aoZhanPlayerData = AoZhanPlayerInfo()
g_aoZhanRoomData = AoZhanRoom()
g_aoZhanRoundData = AoZhanRoundBase()
g_aoZhanMgr = AoZhanDataMgr()