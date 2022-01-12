# -*- coding: gb18030 -*-
import copy
import math
import random
import BigWorld

import Love3
from bwdebug import *
import csconst
import csstatus
from Message_logger import *
from ActivityLog import g_activityLog as g_aLog
import cschannel_msgs

FIGHT_SPACE_NAME = ["fu_ben_bang_hui_feng_huo_lian_tian","fu_ben_bang_hui_feng_huo_lian_tian","fu_ben_bang_hui_feng_huo_lian_tian","fu_ben_bang_hui_feng_huo_lian_tian"]
FINAL_MATCH_SPACE_NAME = "fu_ben_bang_hui_feng_huo_lian_tian"

SPACE_KEY_FORMAT = lambda cityName, round, index : cityName + "_" + str( round ) + "_" + str( index )

TONG_FENG_HUO_LIAN_TIAN_JOIN_TONG_MAX = 16

FENG_HUO_LIAN_TIAN_ROUNDS = int( math.log( TONG_FENG_HUO_LIAN_TIAN_JOIN_TONG_MAX, 2 ) ) # 城战分多少轮打

class FengHuoLianTianFightData:
	"""
	帮会夺城战复赛（烽火连天）一场战争
	"""
	def __init__( self,  cityName = "", tongDBID_1 = 0, tongDBID_2 = 0 ):
		self.tongDBID_1 = tongDBID_1
		self.tongDBID_2 = tongDBID_2
		self.cityName = cityName
		self.spaceKey = ""
		self.winner = 0
		self.complete = False
		self.tongIntegral_1 = 0
		self.tongIntegral_2 = 0
		
	def initData( self, tongDBID_1, tongDBID_2, tongIntegral_1 = 0, tongIntegral_2 = 0, winner = 0 ):
		self.tongDBID_1 = tongDBID_1
		self.tongDBID_2 = tongDBID_2
		self.tongIntegral_1 = tongIntegral_1
		self.tongIntegral_2 = tongIntegral_2
		self.winner = winner
		
	def startWar( self, mgr, cityName, camp, isFinal = False ):
		self.cityName = cityName
		if self.tongDBID_1 and self.tongDBID_2:
			tong1_name = mgr.getTongNameByDBID( self.tongDBID_1 )
			tong2_name = mgr.getTongNameByDBID( self.tongDBID_2 )
			mgr.onFengHuoLianTianMessage( self.tongDBID_1, csstatus.TONG_FENG_HUO_LIAN_TIAN_START_NOTITY_PRE, csconst.TONG_CITYWAR_CITY_MAPS.get( cityName ), tong2_name )
			mgr.onFengHuoLianTianMessage( self.tongDBID_2, csstatus.TONG_FENG_HUO_LIAN_TIAN_START_NOTITY_PRE, csconst.TONG_CITYWAR_CITY_MAPS.get( cityName ), tong1_name )
		elif self.tongDBID_1 and self.tongDBID_2 == 0:
			self.setWinner( mgr, self.tongDBID_1, 0, 0, isFinal )
			if not isFinal:
				mgr.onFengHuoLianTianMessage( self.tongDBID_1, csstatus.TONG_FENG_HUO_LIAN_TIAN_WAR_BYE  )
		elif self.tongDBID_1 == 0 and self.tongDBID_2:
			self.setWinner( mgr, self.tongDBID_2, 0, 0, isFinal )
			if not isFinal:
				mgr.onFengHuoLianTianMessage( self.tongDBID_2, csstatus.TONG_FENG_HUO_LIAN_TIAN_WAR_BYE  )
				
	def setSpaceKey( self, spaceKey ):
		self.spaceKey = spaceKey
		
	def getSpaceKey( self ):
		return self.spaceKey
		
	def setWinner( self, mgr, winner, winnerIntegral, failure, faulureIntegral, isFinal ):
		self.winner = winner
		if winner == self.tongDBID_1:
			self.tongIntegral_1 = winnerIntegral
			self.tongIntegral_2 = faulureIntegral
		else:
			self.tongIntegral_1 = faulureIntegral
			self.tongIntegral_2 = winnerIntegral
			
		if winner and not self.isComplete():
			tongName = mgr.getTongNameByDBID( winner )
			cityNameWord = csconst.TONG_CITYWAR_CITY_MAPS.get( self.cityName, "test" )
			if isFinal:
				tongCamp = mgr.getTongCampByDBID( dbid )
				mgr.tongFHLTFightInfos[ ( self.cityName, tongCamp ) ].setJoinCityWarTong( mgr, winner, winnerIntegral )
				mgr.tongFHLTFightInfos[ ( self.cityName, tongCamp ) ].setJoinCityWarTong( mgr, failure, faulureIntegral )
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_FENG_HUO_LIAN_TIAN_FINAL_WINN%( tongName, cityNameWord, tongName ), [] )
			else:
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_FENG_HUO_LIAN_TIAN_WINN%( tongName, cityNameWord ), [] )
		
		self.warClose()
	
	def getTongIntegral( self, tongDBID ):
		if tongDBID != 0:
			if self.tongDBID_1 == tongDBID:
				return self.tongIntegral_1
			elif self.tongDBID_2 == tongDBID:
				return self.tongIntegral_2
			
		return 0
	
	def getWinner( self ):
		return self.winner
	
	def warClose( self ):
		self.complete = True
	
	def isComplete( self ):
		return self.complete
	
	def getTongDBIDs( self ):
		return [ self.tongDBID_1, self.tongDBID_2 ]
	
	def getLost( self ):
		lost = []
		if self.winner != self.tongDBID_1:
			lost.append( self.tongDBID_1 )
		
		if self.winner != self.tongDBID_2:
			lost.append( self.tongDBID_2 )
		
		return lost
		
	def onTongDismiss( self, tongDBID ):
		if self.tongDBID_1 == tongDBID:
			self.winner = self.tongDBID_2
		
		if self.tongDBID_2 == tongDBID:
			self.winner = self.tongDBID_1
	
	def getDictFromObj( self, obj ):
		dict = {}
		dict[ "tongDBID_1" ] = obj.tongDBID_1
		dict[ "tongDBID_2" ] = obj.tongDBID_2
		dict[ "tongIntegral_1" ] = obj.tongIntegral_1
		dict[ "tongIntegral_2" ] = obj.tongIntegral_2
		dict[ "winner" ] = obj.winner
		return dict
		
	def createObjFromDict( self, dict ):
		obj = FengHuoLianTianFightData()
		obj.initData( dict[ "tongDBID_1" ], dict[ "tongDBID_2" ], dict[ "tongIntegral_1" ], dict[ "tongIntegral_2" ], dict[ "winner" ] )
		return obj
	
	def isSameType( self, obj ):
		return isinstance( obj, FengHuoLianTianFightData )
		
	
class FengHuoLianTianItem:
	"""
	帮会夺城战复赛（烽火连天）争夺一个城市
	"""
	def __init__( self ):
		self.cityName = ""
		self.camp = 0
		#self.master = 0
		self.canJoinList = []
		self.roundItemList = []
		self.currentRound = 0
		self.isComplete = False
		self.maxRound = FENG_HUO_LIAN_TIAN_ROUNDS

	def onInit( self, cityName, camp,  master ):
		#self.master = master
		self.cityName = cityName
		self.camp = camp
		
	def resetWar( self ):
		self.canJoinList = []
		self.roundItemList = []
		self.currentRound = 0
		self.isComplete = False
		self.maxRound = FENG_HUO_LIAN_TIAN_ROUNDS
		
	def instance( self, dict ):
		#self.master = dict[ "master" ]
		self.cityName = dict[ "cityName" ]
		self.camp = dict[ "camp" ]
		self.roundItemList = dict[ "roundItemList" ]
	
	def getCityName( self ):
		return self.cityName
	
	def getMgrKey( self ):
		return ( self.cityName, self.camp )

	def searchWar( self, tongDBID ):
		currentWarList = self.roundItemList[ self.currentRound - 1 ]
		for war in currentWarList:
			if tongDBID in war.getTongDBIDs():
				return war
	
		return None
	
	def setJoinCityWarTong( self, mgr, dbid, integral ):
		"""
		设置城战参与者
		"""
		if dbid:
			mgr.setJoinCityWarTong( self.cityName, self.camp, dbid, integral )
	
	def joinUp( self, mgr, tongDBID ):
		# tongDBID : 帮会ID
		if tongDBID not in self.canJoinList:
			self.canJoinList.append( tongDBID )

	def initRoundItem( self ):
		self.roundItemList = []
		join_length = len( self.canJoinList )
		if join_length != 0:
			tempRounds = int( math.log( join_length, 2 ) )
			
			if math.pow( 2, tempRounds ) != join_length:
				self.maxRound = tempRounds + 1
			else:
				self.maxRound = tempRounds

		for i in xrange( self.maxRound ):
			roundItems = []
			roundNums = pow( 2, self.maxRound - i -1 ) # -1的原因是一场比赛进2个人，所以16个人的比赛应该只有8场
			for j in xrange( roundNums ):
				roundItems.append( FengHuoLianTianFightData( self.cityName, 0, 0 ) )
				
			self.roundItemList.append( roundItems )

	def initFistWar( self ):
		# 初始化第一轮比赛的数据
		self.initRoundItem()
		join_length = len( self.canJoinList )
		if join_length == 0 or self.isComplete:
			self.isComplete = True
			return
			
		nextList = copy.deepcopy( self.canJoinList )
		disNum = 0
		disData = []
		
		join_tong_max = TONG_FENG_HUO_LIAN_TIAN_JOIN_TONG_MAX
		
		for i in xrange( TONG_FENG_HUO_LIAN_TIAN_JOIN_TONG_MAX +1 ):
			if pow( 2, i ) >= join_length:
				join_tong_max = pow( 2, i )
				break
		
		for i in xrange( join_tong_max + 1 ):
			disData.append( 0 )
			
		i = 0
		while( len( nextList )):
			tong1 = random.choice( nextList )
			nextList.remove( tong1 )
			disData[ i ] = tong1
			
			if len( nextList ):
				tong2 = random.choice( nextList )
				groud_2 = i + join_tong_max / 2
				DEBUG_MSG("cityName is %s,groud_2 is %s, join_tong_max is %s,nextList is %s"%(self.cityName,groud_2, join_tong_max,nextList))
				disData[ groud_2 ] = tong2
				nextList.remove( tong2 )
			
			i += 1
		
		fistWars = self.roundItemList[ 0 ] # 取出第一轮的所有比赛
		for i, war in enumerate( fistWars ):
			disIndex = i * 2
			war.initData( disData[ disIndex ], disData[ disIndex + 1 ] )
			war.setSpaceKey( random.choice( FIGHT_SPACE_NAME ) )

	def initRoundWar( self, initRound ):
		# 初始化下一轮的数据，非第一轮
		if self.isComplete or initRound > self.maxRound:
			return
			
		preWars = self.roundItemList[ initRound - 2 ]
		currentWars = self.roundItemList[ initRound - 1 ]
		lenGround = len( preWars ) / 2
		disData = []
			
		for war in preWars:
			disData.append( war.getWinner() )
		
		if len( disData ) > 2:
			length = len( disData )
			aData = disData[ 0 : length / 2 ]
			bData = disData[ length / 2 : length ]
			aTempList = list( set( aData ) ^ set( [0] ) )
			bTempList = list( set( bData ) ^ set( [0] ) )
			if len( aTempList ) == 0 and len( bTempList ) >= length / 2:
				i = 0
				while( True ):
					if len( bTempList ):
						disID1 = bTempList.pop(0)
						disData[ i ] = disID1
						if len( bTempList ):
							disID2 = bTempList.pop(0)
							disData[ length / 2 + i ] = disID2
						i += 1
					else:
						break
			
			if len( aTempList ) >= length / 2 and len( bTempList ) == 0:
				i = 0
				while( True ):
					if len( aTempList ):
						disID1 = aTempList.pop(0)
						disData[ i ] = disID1
						if len( aTempList ):
							disID2 = aTempList.pop(0)
							disData[ length / 2 + i ] = disID2
						i += 1
					else:
						break
		
		for i, war in enumerate( currentWars ):
			disIndex = i * 2
			tID1 = disData[ disIndex ]
			nDisIndex = disIndex + 1
			tID2 = disData[ nDisIndex ] if len( disData ) > nDisIndex else 0
			war.initData( tID1, tID2 )
			if initRound == self.maxRound:
				war.setSpaceKey( FINAL_MATCH_SPACE_NAME )
			else:
				war.setSpaceKey( random.choice( FIGHT_SPACE_NAME ) )

	def startWar( self, mgr ):
		# 开启当前轮的比赛
		isFinal = self.isFinal()
		if len( self.canJoinList ) == 0:
			return
		for war in self.roundItemList[ self.currentRound - 1 ]:
			war.startWar( mgr, self.cityName, self.camp, isFinal )
			
	def startNextRound( self, mgr ):
		if self.currentRound != self.maxRound:
			self.currentRound += 1
			if self.currentRound == 1:
				self.initFistWar()
			
			self.startWar( mgr )
			
	def getRound( self ):
		return self.currentRound

	def checkTongHasWar( self, tongDBID ):		
		currentWarList = self.getCurrentTong()
		if tongDBID in currentWarList:
			return True
		
		return False

	def setWinner( self, mgr, winner, winnerIntegral, failure, faulureIntegral ):
		# 设置胜利者，其实failure只是为了防止tongDBID为0的时候出错
		lostList = []
		isFinal = self.isFinal()
		currentWars = self.roundItemList[ self.currentRound - 1 ]
		for war in currentWars:
			if winner in war.getTongDBIDs() or failure != 0 and failure in war.getTongDBIDs():
				war.setWinner( mgr, winner, winnerIntegral, failure, faulureIntegral, isFinal )
				if winner:
					lostTong = war.tongDBID_2 if  war.tongDBID_1 == winner else war.tongDBID_1
					lostList.append( lostTong )
				else:
					lostList.extend( war.getTongDBIDs() )
			
		cityNameWord = csconst.TONG_CITYWAR_CITY_MAPS.get( self.cityName, "test" )
		mgr.onFengHuoLianTianMessage( tongDBID, csstatus.TONG_CITY_WAR_WIN_8, cityNameWord )
		# 向失败的帮会发通告
		for tid in lostList:
			mgr.onFengHuoLianTianMessage( tid, csstatus.TONG_CITY_WAR_FAIL )
		
	def onTimerSetWinner( self, mgr, tongDBID, failure ):
		# 设置胜利者，其实failure只是为了防止tongDBID为0的时候出错
		lostList = []
		isFinal = self.isFinal()
		currentWars = self.roundItemList[ self.currentRound - 1 ]
		for war in currentWars:
			if ( tongDBID in war.getTongDBIDs() or failure != 0 and failure in war.getTongDBIDs() ) and not war.isComplete():
				war.setWinner( mgr, tongDBID, 0, failure, 0, isFinal )
				if tongDBID:
					lostTong = war.tongDBID_2 if  war.tongDBID_1 == tongDBID else war.tongDBID_1
					lostList.append( lostTong )
				else:
					lostList.extend( war.getTongDBIDs() )
			
		cityNameWord = csconst.TONG_CITYWAR_CITY_MAPS.get( self.cityName, "test" )
		mgr.onFengHuoLianTianMessage( tongDBID, csstatus.TONG_CITY_WAR_WIN_8, cityNameWord )
		# 向失败的帮会发通告
		for tid in lostList:
			mgr.onFengHuoLianTianMessage( tid, csstatus.TONG_CITY_WAR_FAIL )
		
	def isAllWarOver( self ):
		DEBUG_MSG( "isAllWarOver:currentRound is %s,length of roundItemList is %s,cityName is %s"%( self.currentRound, len(self.roundItemList), self.cityName ) )
		currentWars = self.roundItemList[ self.currentRound - 1 ]
		for war in currentWars:
			if not war.isComplete():
				return False
		
		return True

	def onTimerCloseWar( self, mgr ):
		# 时间已经到了，没有返回信息，强制关闭战争
		DEBUG_MSG( "onTimerCloseWar:currentRound is %s,length of roundItemList is %s,cityName is %s"%( self.currentRound, len(self.roundItemList), self.cityName ) )
		currentWars = self.roundItemList[ self.currentRound - 1 ]
		for war in currentWars:
			if not war.isComplete():
				failure = war.tongDBID_1 if war.tongDBID_1 else war.tongDBID_2
				self.onTimerSetWinner( mgr, 0, failure )
				
	def isFinal( self ):
		return self.currentRound == self.maxRound

	def isCanJoin( self, tongDBID ):
		return tongDBID in self.canJoinList

	def isWinner( self, tongDBID ):
		if tongDBID in self.canJoinList:
			items = self.roundItemList[ self.currentRound - 1 ]
			for item in items:
				if tongDBID == item.getWinner():
					return True
		return False

	def getCurrentFight( self ):
		return self.roundItemList[ self.currentRound - 1 ]
		
	def getCurrentTong( self ):
		cTongList = []
		if self.currentRound - 1 < 0:
			return cTongList
		for item in self.roundItemList[ self.currentRound - 1 ]:
			cTongList.extend( item.getTongDBIDs() )
			
		return cTongList

	def getSpaceItemKey( self, tongDBID ):
		if not self.checkTongHasWar( tongDBID ): # 该帮会已经没有战斗
			return
			
		index = 0
		items = self.roundItemList[ self.currentRound - 1 ]
		for i, item in enumerate( items ):
			if tongDBID in item.getTongDBIDs():
				index = i
					
		return SPACE_KEY_FORMAT( self.cityName, self.currentRound, index )

	def getTongIndex( self, tongDBID ):
		index = 0
		items = self.roundItemList[ self.currentRound - 1 ]
		for item in items:
			if item.tongDBID_1 == tongDBID:
				index = 1
			
			elif item.tongDBID_2 == tongDBID:
				index = 2
			
		return index

	def getSpaceKey( self, tongDBID ):
		if not self.checkTongHasWar( tongDBID ): # 该帮会已经没有战斗
			return ""
		
		items = self.roundItemList[ self.currentRound - 1 ]
		for item in items:
			if tongDBID in item.getTongDBIDs():
				return item.getSpaceKey()
		
		return ""

	def getTongWinNum( self, tongDBID ):
		# 获取帮会胜利的次数
		winNum = 0
		for round in self.roundItemList:
			for item in round:
				if item.getWinner() == tongDBID:
					winNum += 1
					break
		
		return winNum
	
	def getTongIntegral( self, tongDBID ):
		#获取帮会的总积分
		integral = 0
		for round in self.roundItemList:
			for item in round:
				if tongDBID in item.getTongDBIDs():
					integral += item.getTongIntegral( tongDBID )
					break
		
		return integral

	def getDictFromObj( self, obj ):
		dict = {}
		#dict[ "master" ] = obj.master
		dict[ "camp" ] = obj.camp
		dict[ "cityName" ] = obj.cityName
		dict[ "roundItemList" ] = obj.roundItemList
		return dict
		
	def createObjFromDict( self, dict ):
		obj = FengHuoLianTianItem()
		obj.instance( dict )
		return obj
	
	def isSameType( self, obj ):
		return isinstance( obj, FengHuoLianTianItem )

class FengHuoLianTianItems:
	def __init__( self ):
		self.infos = {}
	
	def instance( self, dict ):
		infos = dict[ "infos" ]
		for record in infos:
			self.infos[ record.getMgrKey() ] = record
			
	def addCity( self, cityName, camp, master = 0 ):
		cityKey = ( cityName, camp )
		if self.infos.has_key( cityKey ) or not cityName:
			return
			
		fItem = FengHuoLianTianItem()
		fItem.onInit( cityName, camp, master )
		self.infos[ cityKey ] = fItem
		
	def isCanJoin( self, tongDBID ):
		for cityName, item in self.infos.iteritems():
			if item.isCanJoin( tongDBID ):
				return cityName
		
		return None

	def isFull( self, cityName, camp ):
		return len( self.infos[ ( cityName, camp ) ].canJoinList ) >= TONG_FENG_HUO_LIAN_TIAN_JOIN_TONG_MAX

	def joinUp( self, mgr, cityName, camp, tondDBID ):
		self.infos[ ( cityName, camp ) ].joinUp( mgr, tondDBID )

	def reset( self ):
		for item in self.infos.itervalues():
			item.resetWar()

	def startWar( self, mgr ):
		# 开启预赛
		for item in self.infos.itervalues():
			item.startNextRound( mgr )

	def getJoinCityName( self, tongDBID ):
		for key, item in self.infos.iteritems():
			if tongDBID in item.canJoinList:
				return key[0]
		
		return ""
	
	def getJoinKey( self, tongDBID ):
		for key, item in self.infos.iteritems():
			if tongDBID in item.canJoinList:
				return key
		
		return ""

	def __getitem__( self, key ):
		return self.infos[ key ]
	
	def getDictFromObj( self, obj ):
		dict = {}
		dict[ "infos" ] = obj.infos.values()
		return dict
		
	def createObjFromDict( self, dict ):
		obj = FengHuoLianTianItems()
		obj.instance( dict )
		return obj
	
	def isSameType( self, obj ):
		return isinstance( obj, FengHuoLianTianItems )


fengHuoLianTianFightIns = FengHuoLianTianFightData()
fengHuoLianTianItemIns = FengHuoLianTianItem()
fengHuoLianTianItemsIns = FengHuoLianTianItems()
