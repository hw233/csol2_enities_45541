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

FIGHT_SPACE_NAME = ["city_war_a","city_war_b","city_war_c","city_war_d"]
FINAL_MATCH_SPACE_NAME = "city_war_e"

SPACE_KEY_FORMAT = lambda cityName, round, index : cityName + "_" + str( round ) + "_" + str( index )

CITY_WAR_ROUNDS = int( math.log( csconst.TONG_CITYWAR_SIGNUP_MAX, 2 ) ) # ��ս�ֶ����ִ�

class MasterChiefData( object ):
	def __init__( self ):
		self.reset()
		
	def reset( self ):
		self.uname = ""
		self.title = ""
		self.tongName = ""
		self.raceclass = 0
		self.hairNumber = 0
		self.faceNumber = 0
		self.bodyFDict = { "iLevel":0, "modelNum":0 }
		self.volaFDict = { "iLevel":0, "modelNum":0 }
		self.breechFDict = { "iLevel":0, "modelNum":0 }
		self.feetFDict = { "iLevel":0, "modelNum":0 }
		self.lefthandFDict = { "iLevel":0, "modelNum":0, "stAmount":0 }
		self.righthandFDict = { "iLevel":0, "modelNum":0, "stAmount":0 }
		self.talismanNum = 0
		self.fashionNum = 0
		self.adornNum = 0
	
	def __setitem__( self, name, value ):
		setattr( self, name, value )
	
	def isSet( self ):
		return self.uname
		
	def getDictFromObj( self, obj ):
		dict = {}
		dict[ "uname" ] = obj.uname
		dict[ "title" ] = obj.title
		dict[ "tongName" ] = obj.tongName
		dict[ "raceclass" ] = obj.raceclass
		dict[ "hairNumber" ] = obj.hairNumber
		dict[ "faceNumber" ] = obj.faceNumber
		dict[ "bodyFDict" ] = obj.bodyFDict
		dict[ "volaFDict" ] = obj.volaFDict
		dict[ "breechFDict" ] = obj.breechFDict
		dict[ "feetFDict" ] = obj.feetFDict
		dict[ "lefthandFDict" ] = obj.lefthandFDict
		dict[ "righthandFDict" ] = obj.righthandFDict
		dict[ "talismanNum" ] = obj.talismanNum
		dict[ "fashionNum" ] = obj.fashionNum
		dict[ "adornNum" ] = obj.adornNum
		return dict
		
	def createObjFromDict( self, dict ):
		obj = MasterChiefData()
		obj.uname = dict[ "uname" ]
		obj.title = dict[ "title" ]
		obj.tongName = dict[ "tongName" ]
		obj.raceclass = dict[ "raceclass" ]
		obj.hairNumber = dict[ "hairNumber" ]
		obj.faceNumber = dict[ "faceNumber" ]
		obj.bodyFDict = dict[ "bodyFDict" ]
		obj.volaFDict = dict[ "volaFDict" ]
		obj.breechFDict = dict[ "breechFDict" ]
		obj.feetFDict = dict[ "feetFDict" ]
		obj.lefthandFDict = dict[ "lefthandFDict" ]
		obj.righthandFDict = dict[ "righthandFDict" ]
		obj.talismanNum = dict[ "talismanNum" ]
		obj.fashionNum = dict[ "fashionNum" ]
		obj.adornNum = dict[ "adornNum" ]
		return obj
	
	def isSameType( self, obj ):
		return isinstance( obj, MasterChiefData )
		
class CityWarFightData( object ):
	# һ��ս��
	def __init__( self,  cityName = "", tongDBID_1 = 0, tongDBID_2 = 0 ):
		self.tongDBID_1 = tongDBID_1
		self.tongDBID_2 = tongDBID_2
		self.cityName = cityName
		self.spaceKey = ""
		self.winner = 0
		self.complete = False
		
	def initData( self, tongDBID_1, tongDBID_2, winner = 0 ):
		self.tongDBID_1 = tongDBID_1
		self.tongDBID_2 = tongDBID_2
		self.winner = winner
	
	def startWar( self, mgr, cityName, isFinal = False ):
		self.cityName = cityName
		if self.tongDBID_1 and self.tongDBID_2:
			tong1_name = mgr.getTongNameByDBID( self.tongDBID_1 )
			tong2_name = mgr.getTongNameByDBID( self.tongDBID_2 )
			mgr.onWarMessage( self.tongDBID_1, csstatus.TONG_CITYWAR_START_NOTITY_PRE, csconst.TONG_CITYWAR_CITY_MAPS.get( cityName ), tong2_name )
			mgr.onWarMessage( self.tongDBID_2, csstatus.TONG_CITYWAR_START_NOTITY_PRE, csconst.TONG_CITYWAR_CITY_MAPS.get( cityName ), tong1_name )
		elif self.tongDBID_1 and self.tongDBID_2 == 0:
			self.setWinner( mgr, self.tongDBID_1, isFinal )
			if not isFinal:
				mgr.onWarMessage( self.tongDBID_1, csstatus.TONG_CITY_WAR_BYE  )
		elif self.tongDBID_1 == 0 and self.tongDBID_2:
			self.setWinner( mgr, self.tongDBID_2, isFinal )
			if not isFinal:
				mgr.onWarMessage( self.tongDBID_2, csstatus.TONG_CITY_WAR_BYE  )
	
	def startFinalWar( self, mgr, cityName, master ):
		self.cityName = cityName
		if not master:
			self.startWar( mgr, cityName, True )
		else:
			cityNameWord = csconst.TONG_CITYWAR_CITY_MAPS.get( cityName )
			mgr.onWarMessage( master, csstatus.TONG_CITY_WAR_FINAL_ENTER, cityNameWord )
			if not self.tongDBID_1 and not self.tongDBID_2:
				self.setWinner( mgr, master, True )
			else:
				if self.tongDBID_1:
					mgr.onWarMessage( self.tongDBID_1, csstatus.TONG_CITY_WAR_FINAL_ENTER, cityNameWord )
				
				if self.tongDBID_2:
					mgr.onWarMessage( self.tongDBID_2, csstatus.TONG_CITY_WAR_FINAL_ENTER, cityNameWord )
	
	def setSpaceKey( self, spaceKey ):
		self.spaceKey = spaceKey
	
	def getSpaceKey( self ):
		return self.spaceKey
	
	def setWinner( self, mgr, dbid, isFinal  ):
		if dbid and not self.isComplete():
			tongName = mgr.getTongNameByDBID( dbid )
			cityNameWord = csconst.TONG_CITYWAR_CITY_MAPS.get( self.cityName, "test" )
			if isFinal:
				mgr.tongCityWarFightInfos[ self.cityName ].setMaster( mgr, dbid )
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_CITY_WAR_FINAL_WINN%( tongName, cityNameWord, tongName ), [] )
			else:
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_CITY_WAR_WINN%( tongName, cityNameWord ), [] )
			
		self.winner = dbid
		self.warClose()
	
	def getWinner( self ):
		return self.winner
	
	def warClose( self ):
		self.complete = True
	
	def isComplete( self ):
		return self.complete
	
	def getLost( self ):
		lost = []
		if self.winner != self.tongDBID_1:
			lost.append( self.tongDBID_1 )
		
		if self.winner != self.tongDBID_2:
			lost.append( self.tongDBID_2 )
		
		return lost
	
	def getTongDBIDs( self ):
		return [ self.tongDBID_1, self.tongDBID_2 ]
	
	def onTongDismiss( self, tongDBID ):
		if self.tongDBID_1 == tongDBID:
			self.winner = self.tongDBID_2
		
		if self.tongDBID_2 == tongDBID:
			self.winner = self.tongDBID_1
	
	def getDictFromObj( self, obj ):
		dict = {}
		dict[ "tongDBID_1" ] = obj.tongDBID_1
		dict[ "tongDBID_2" ] = obj.tongDBID_2
		dict[ "winner" ] = obj.winner
		return dict
		
	def createObjFromDict( self, dict ):
		obj = CityWarFightData()
		obj.initData( dict[ "tongDBID_1" ], dict[ "tongDBID_2" ], dict[ "winner" ] )
		return obj
	
	def isSameType( self, obj ):
		return isinstance( obj, CityWarFightData )

class CityWarItem( object ):
	# һ���������
	def __init__( self ):
		self.cityName = ""
		self.master = 0
		self.signUpList = []
		self.roundItemList = []
		self.currentRound = 0
		self.chiefData = MasterChiefData()
		self.spawnPointMasterList = []
		self.isComplete = False
	
	def onInit( self, cityName, master ):
		self.master = master
		self.cityName = cityName
	
	def resetWar( self ):
		self.signUpList = []
		self.roundItemList = []
		self.currentRound = 0
		self.isComplete = False
	
	def instance( self, dict ):
		self.master = dict[ "master" ]
		self.cityName = dict[ "cityName" ]
		self.roundItemList = dict[ "roundItemList" ]
		self.chiefData = dict[ "chiefData" ]
	
	def getCityName( self ):
		return self.cityName
	
	def searchWar( self, tongDBID ):
		currentWarList = self.roundItemList[ self.currentRound - 1 ]
		for war in currentWarList:
			if tongDBID in war.getTongDBIDs():
				return war
		
		if self.master == tongDBID and self.currentRound == CITY_WAR_ROUNDS:
			return currentWarList[0]
	
		return None
	
	def setMaster( self, mgr, master ):
		self.master = master
		if self.master:
			mgr.setCityNewMaster( self.cityName, master )
	
	def getMaster( self ):
		return self.master
	
	def isMaster( self, tongDBID ):
		if tongDBID == 0:
			return False
		return tongDBID == self.master
		
	def signUp( self, mgr, tongDBID ):
		# tongDBID : ���ID
		# playerBase : �����ˣ�����/��������
		if tongDBID not in self.signUpList:
			self.signUpList.append( tongDBID )
	
	def initRoundItem( self ):
		self.roundItemList = []
		for i in xrange( CITY_WAR_ROUNDS ):
			roundItems = []
			roundNums = pow( 2, CITY_WAR_ROUNDS - i - 1 )
			for j in xrange( roundNums ):
				roundItems.append( CityWarFightData( self.cityName, 0, 0 ) )
				
			self.roundItemList.append( roundItems )
	
	def initFistWar( self ):
		# ��ʼ����һ�ֱ���������
		self.initRoundItem()
		if len( self.signUpList ) == 0 or self.isComplete:
			self.isComplete = True
			return
			
		nextList = copy.deepcopy( self.signUpList )
		disNum = 0
		disData = []
		
		for i in xrange( csconst.TONG_CITYWAR_SIGNUP_MAX ):
			disData.append( 0 )
			
		for i in xrange( CITY_WAR_ROUNDS + 1 ):
			tong1 = random.choice( nextList )
			nextList.remove( tong1 )
			disData[ i ] = tong1
			
			if len( nextList ):
				tong2 = random.choice( nextList )
				groud_2 = i + csconst.TONG_CITYWAR_SIGNUP_MAX / 2
				disData[ groud_2 ] = tong2
				nextList.remove( tong2 )
			
			if not len( nextList ):
				break
		
		fistWars = self.roundItemList[ 0 ] # ȡ����һ�ֵ����б���
		for i, war in enumerate( fistWars ):
			disIndex = i * 2
			war.initData( disData[ disIndex ], disData[ disIndex + 1 ] )
			war.setSpaceKey( random.choice( FIGHT_SPACE_NAME ) )
	
	def initRoundWar( self, initRound ):
		# ��ʼ����һ�ֵ����ݣ��ǵ�һ��
		if self.isComplete or initRound > CITY_WAR_ROUNDS:
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
			if len( aTempList ) == 0 and len( bTempList ) >= 2:
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
			
			if len( aTempList ) >= 2 and len( bTempList ) == 0:
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
			if initRound == CITY_WAR_ROUNDS:
				war.setSpaceKey( FINAL_MATCH_SPACE_NAME )
			else:
				war.setSpaceKey( random.choice( FIGHT_SPACE_NAME ) )
	
	def startWar( self, mgr ):
		# ������ǰ�ֵı���
		for war in self.roundItemList[ self.currentRound - 1 ]:
			war.startWar( mgr, self.cityName, False )
	
	def startFinalWar( self, mgr ):
		self.roundItemList[ CITY_WAR_ROUNDS - 1 ][ 0 ].startFinalWar( mgr, self.cityName, self.master )
	
	def startNextRound( self, mgr ):
		if self.currentRound != CITY_WAR_ROUNDS - 1:
			self.currentRound += 1
			if self.currentRound == 1:
				self.initFistWar()
			
			self.startWar( mgr )
	
	def startFinalRound( self, mgr ):
		if self.currentRound == CITY_WAR_ROUNDS - 1:
			self.currentRound = CITY_WAR_ROUNDS
			self.startFinalWar( mgr )
		
	def getRound( self ):
		return self.currentRound
	
	def checkTongHasWar( self, tongDBID ):		
		currentWarList = self.getCurrentTong()
		if tongDBID in currentWarList:
			return True
		
		if self.currentRound == CITY_WAR_ROUNDS and  tongDBID == self.master:
			return True
		
		return False
		
	def setWinner( self, mgr, tongDBID, failure ):
		# ����ʤ���ߣ���ʵfailureֻ��Ϊ�˷�ֹtongDBIDΪ0��ʱ�����
		lostList = []
		
		if self.currentRound == CITY_WAR_ROUNDS: # ��ǰ�Ǿ���
			war = self.roundItemList[ self.currentRound - 1 ][ 0 ]#�����϶�ֻ��һ��ս��
			if not war.isComplete():
				if tongDBID ==  self.master or tongDBID == 0:
					lostList.extend( war.getTongDBIDs() )
				else:
					dbids = war.getTongDBIDs()
					if tongDBID in dbids:
						dbids.remove( tongDBID )
						
					dbids = list( set( dbids ) ^ set( [0] ) )
					lostList.append( self.master )
					lostList.extend( dbids )
					
				war.setWinner( mgr, tongDBID, True )
		else:
			currentWars = self.roundItemList[ self.currentRound - 1 ]
			for war in currentWars:
				if ( tongDBID in war.getTongDBIDs() or failure != 0 and failure in war.getTongDBIDs() ) and not war.isComplete():
					war.setWinner( mgr, tongDBID, False )
					if tongDBID:
						lostTong = war.tongDBID_2 if  war.tongDBID_1 == tongDBID else war.tongDBID_1
						lostList.append( lostTong )
					else:
						lostList.extend( war.getTongDBIDs() )
				
			cityNameWord = csconst.TONG_CITYWAR_CITY_MAPS.get( self.cityName, "test" )
			if self.currentRound == CITY_WAR_ROUNDS - 1:
				mgr.onWarMessage( tongDBID, csstatus.TONG_CITY_WAR_WIN_4, cityNameWord )
			else:
				mgr.onWarMessage( tongDBID, csstatus.TONG_CITY_WAR_WIN_8, cityNameWord )
		# ��ʧ�ܵİ�ᷢͨ��
		for tid in lostList:
			mgr.onWarMessage( tid, csstatus.TONG_CITY_WAR_FAIL )
		
		ceaseMatchTongs = copy.deepcopy( lostList )
		if len( self.roundItemList ) == self.currentRound + 1:
			ceaseMatchTongs.append( self.master )
			
		mgr.onCeaseMatchMessage( ceaseMatchTongs )
	
	def isAllWarOver( self ):
		currentWars = self.roundItemList[ self.currentRound - 1 ]
		for war in currentWars:
			if not war.isComplete():
				return False
		
		return True
	
	def onTimerCloseWar( self, mgr ):
		# ʱ���Ѿ����ˣ�û�з�����Ϣ��ǿ�ƹر�ս��
		currentWars = self.roundItemList[ self.currentRound - 1 ]
		for war in currentWars:
			if not war.isComplete():
				failure = war.tongDBID_1 if war.tongDBID_1 else war.tongDBID_2
				self.setWinner( mgr, 0, failure )
		
	def isSignUp( self, tongDBID ):
		return tongDBID in self.signUpList
		
	def isFinal( self ):
		return self.currentRound == CITY_WAR_ROUNDS
	
	def isWinner( self, tongDBID ):
		if tongDBID in self.signUpList:
			items = self.roundItemList[ self.currentRound - 1 ]
			for item in items:
				if tongDBID == item.getWinner():
					return True
		return False
	
	def onTongDismiss( self, tongDBID, isUnderway ):
		if tongDBID == self.master:
			self.master = 0
			self.chiefData.reset()
			for mailbox in self.spawnPointMasterList:
				mailbox.cell.spawnNoMasterNpc()
		
		#items = self.roundItemList[ self.currentRound - 1 ]
		#for item in items:
		#	item.onTongDismiss( tongDBID )
	
	def getCurrentFight( self ):
		return self.roundItemList[ self.currentRound - 1 ]
	
	def getCurrentTong( self ):
		cTongList = []
		for item in self.roundItemList[ self.currentRound - 1 ]:
			cTongList.extend( item.getTongDBIDs() )
			
		return cTongList
			
	def getSpaceItemKey( self, tongDBID ):
		if not self.checkTongHasWar( tongDBID ): # �ð���Ѿ�û��ս��
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
			
			elif hasattr( item, master ) and item.getMaster() == tongDBID:
				index = 3
		
		return index
		
	def getSpaceKey( self, tongDBID ):
		if not self.checkTongHasWar( tongDBID ): # �ð���Ѿ�û��ս��
			return ""
		
		items = self.roundItemList[ self.currentRound - 1 ]
		for item in items:
			if tongDBID in item.getTongDBIDs():
				return item.getSpaceKey()
		
		if tongDBID == self.master and self.isFinal():
			return FINAL_MATCH_SPACE_NAME
		
		return ""
	
	def getTongWinNum( self, tongDBID ):
		# ��ȡ���ʤ���Ĵ���
		winNum = 0
		for round in self.roundItemList:
			for item in round:
				if item.getWinner() == tongDBID:
					winNum += 1
					break
		
		return winNum
	
	def setMasterChiefInfo( self, chiefInfos ):
		self.chiefData = chiefInfos
		self.chiefData[ "title" ] = cschannel_msgs.TONG_CITY_WAR_MASTER_TITLE % csconst.TONG_CITYWAR_CITY_MAPS.get( self.cityName )
		for spawnPoint in self.spawnPointMasterList:
			spawnPoint.cell.spawnCityMaster( self.chiefData )
	
	def addSpawnMaster( self, mailbox ):
		self.spawnPointMasterList.append( mailbox )
		if self.chiefData.isSet():
			mailbox.cell.remoteCallScript( "spawnCityMaster", [ self.chiefData, ] )
		else:
			mailbox.cell.remoteCallScript( "spawnNoMasterNpc", [] )
	
	def delCityMaster( self ):
		# ɾ������
		self.master = 0
		for mailbox in self.spawnPointMasterList:
			mailbox.cell.spawnNoMasterNpc()
		
	def getDictFromObj( self, obj ):
		dict = {}
		dict[ "master" ] = obj.master
		dict[ "cityName" ] = obj.cityName
		dict[ "roundItemList" ] = obj.roundItemList
		dict[ "chiefData" ] = obj.chiefData
		return dict
		
	def createObjFromDict( self, dict ):
		obj = CityWarItem()
		obj.instance( dict )
		return obj
	
	def isSameType( self, obj ):
		return isinstance( obj, CityWarItem )
		
class CityWarItems( object ):
	def __init__( self ):
		self.infos = {}
	
	def instance( self, dict ):
		infos = dict[ "infos" ]
		for record in infos:
			self.infos[ record.getCityName() ] = record
	
	def isMaster( self, tongDBID ):
		for cityName, item in self.infos.iteritems():
			if item.getMaster() == tongDBID:
				return cityName
		
		return None
		
	def addCity( self, cityName, master = 0 ):
		if self.infos.has_key( cityName ):
			return 
			
		c = CityWarItem()
		c.onInit( cityName, master )
		self.infos[ cityName ] = c
	
	def isSignUp( self, tongDBID ):
		for cityName, item in self.infos.iteritems():
			if item.isSignUp( tongDBID ):
				return cityName
		
		return None
	
	def isFull( self, cityName ):
		return len( self.infos[ cityName].signUpList ) >= csconst.TONG_CITYWAR_SIGNUP_MAX
	
	def signUp( self, mgr, cityName, tondDBID ):
		self.infos[ cityName ].signUp( mgr, tondDBID )
	
	def reset( self ):
		for item in self.infos.itervalues():
			item.resetWar()
	
	def startWar( self, mgr ):
		# ����Ԥ��
		for item in self.infos.itervalues():
			item.startNextRound( mgr )
	
	def startFinalWar( self, mgr ):
		# ��������
		for item in self.infos.itervalues():
			item.startFinalRound( mgr )
	
	def onTongDismiss( self, tongDBID, isUnderway ):
		# ����ɢ�ص�
		for item in self.infos.itervalues():
			item.onTongDismiss( tongDBID, isUnderway )
	
	def getJoinCityName( self, tongDBID ):
		for cityName, item in self.infos.iteritems():
			if tongDBID in item.signUpList or item.getMaster() == tongDBID:
				return cityName
		
		return ""
	
	def setMasterChiefInfo( self, tongDBID, chiefInfos ):
		for item in self.infos.itervalues():
			if item.getMaster() == tongDBID:
				item.setMasterChiefInfo( chiefInfos )
	
	def __getitem__( self, cityName ):
		return self.infos[ cityName ]
	
	def getDictFromObj( self, obj ):
		dict = {}
		dict[ "infos" ] = obj.infos.values()
		return dict
		
	def createObjFromDict( self, dict ):
		obj = CityWarItems()
		obj.instance( dict )
		return obj
	
	def isSameType( self, obj ):
		return isinstance( obj, CityWarItems )

masterChiefIns = MasterChiefData()
cityWarFightIns = CityWarFightData()
cityWarItemIns = CityWarItem()
cityWarItemsIns = CityWarItems()
