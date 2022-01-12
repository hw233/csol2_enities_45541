# -*- coding: gb18030 -*-
import copy
import random

import csdefine
import csstatus
import cschannel_msgs

AO_ZHEN_FAILURE_ENTER_NUM = {
	1	:	5,			#2�˱�����ʱ�򣬼�����
	2	:	3,			#4�˱�����ʱ�򣬼������
	4	:	2,			#8�˱�����ʱ�򣬼�1/4����
	8	:	1,			#16�˱�����ʱ�򣬼�1/8����
	16	:	0,			#32�˱�����ʱ�򣬼�1/16����
	32	:	0,			#64�˱�����ʱ�򣬼�1/32����
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
	һ������
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
		if bPlayer ==0 and len( failureList ) == 0:#�ֿ�
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
			
		if winner and self.matchType != 1: #���Ǿ���
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
	һ�ֱ���
	"""
	def __init__( self, matchType = 0 ):
		object.__init__( self )
		self.joinList = []
		self.failureList = []
		
		self._disInfos = []
		self.matchType = matchType
		
		self.nextWinner = [] #���������б�
		
		self._type = 0
	
	def init( self, winnerList, failureList ):
		self.joinList = winnerList
		self.failureList = failureList
	
	def getRoundRooms( self ):
		return self._disInfos

	def setResult( self, mgr, roomNum, winner, score, useTime, remainHP ):
		"""
		���
		"""
		self._disInfos[ roomNum ].setResult( mgr, winner, score, useTime, remainHP )
	
	def getType( self ):
		return self._type
	
	def getNextList( self ):
		"""
		��ȡ�³�������
		"""
		if not len( self.nextWinner ):
			self.nextWinner = self.calculateNextList()
			
		return self.nextWinner
	
	def calculateNextList( self ):
		return []
	
	def getNextFailure( self ):
		"""
		��ȡ�³�ʧ����
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
	#û��ʧ����
	def __init__( self, matchType ):
		AoZhanRoundBase.__init__( self, matchType )
		self._type = csdefine.AO_ZHAN_ROOM_TYPE_NO_FAILURE
		
	def dis( self, mgr ):
		#����
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
		#������������
		result = []
		for r in self._disInfos:
			result.append( r.winner )
			
		self.nextWinner = copy.deepcopy( result )
		return result

class AoZhanRoundHasFailure( AoZhanRoundBase ):
	#��ʧ����
	def __init__( self, matchType ):
		AoZhanRoundBase.__init__( self, matchType )
		self._type = csdefine.AO_ZHAN_ROOM_TYPE_HAS_FAILURE
	
	def dis( self, mgr ):
		#����
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
		������������
		"""
		result = []
		winList = []
		promotedNum = self._getPromotedNum() # ����������������
		disWinnerLen = len( self.joinList ) #Ҫ����ʤ���ߵ�����
		
		#ȡ�û�ʤ��������
		for r in self._disInfos:
			if r.isWin():
				winList.append( r )
		
		if len( winList ) > promotedNum: #�����ʤ���������ڽ�������
			winList.sort( key = lambda r : r.useTime, reverse = True ) #��ս������ʱ������
			hpSortList = copy.deepcopy( winList )
			hpSortList.sort( key = lambda r : r.remainHP, reverse = False )
			
			wLen = len( winList )
			undetermined = []	#�����б�
			
			for i, item in enumerate( winList ):
				if len( result ) >= promotedNum:
					break
				
				nextItem = winList[ i + 1 ]	#���������ﲻ�����
				if item.useTime <= nextItem.useTime and len( result ) < promotedNum:
					result.append( item.winner )
					remain = promotedNum - len( result )	#��ʣ���ٽ���λ��
					if remain <= 0:
						break
					elif remain < len( undetermined ): #�����������С��ʣ���λ�ã���ȫ�����������
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
							obj = getMaxRemainHP( undetermined ) #����Ѫ������ʤ
							undetermined.remove( obj )
							result.append( obj.winner )
						
						undetermined = []
						break
				else:
					undetermined.append( item )
		else:	#�����ʤ������С�ڽ�������
			result.extend( winList )#�����л�ʤ�������ӽ������б���
				
			if len( self.joinList ) > promotedNum:
				failList = []
				for r in self._disInfos: #ȡ������ʧ�ܷ�����б�
					if not r.isWin():
						failList.append( r )
						
				remain = promotedNum - len( result ) #ȡ��ʣ���������
				
				failList.sort( key = lambda r : r.score, reverse = False ) #���л�������
				undetermined = []	#��������
				for i, item in enumerate( failList ):
					if len( result ) >= promotedNum:
						break
						
					nextItem = failList[ i + 1 ] #������������Զ�������
					if item.score >= nextItem.score:
						result.append( item.aPlayer )
						remain = promotedNum - len( result )	#��ʣ���ٽ���λ��
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
		��ȡʧ������ҵ�ʤ��
		"""
		winNum = 0
		for info in self.infos.itervalues():
			room = info.getEnterRoom( databaseID )
			if room and databaseID in room.failureList and not room.isWin():
				winNum += 1
		
		return winNum
	
	def getMaxJoinFailPlayer( self ):
		"""
		��ȡ����ʧ�ܳ����������
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