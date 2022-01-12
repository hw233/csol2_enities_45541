# -*- coding: gb18030 -*-

import uuid
import time
import csstatus
import cschannel_msgs
from bwdebug import *
import Love3
from csconst import g_maps_info, g_camp_info
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
import csdefine

SECOND_GLOBAL_NOTICE_INTERVAL = 15 * 60		# 第二次通告间隔 15 * 60
THIRD_GLOBAL_NOTICE_INTERVAL = 10 * 60		# 第三次通告间隔 10 * 60
GLOBAL_NOTICE_TIMER_SECOND = 10011
GLOBAL_NOTICE_TIMER_THIRD = 10021
CITY_WAR_FINAL_LAST_TIME = 60 * 60			# 夺城战决赛持续时间
 
# 参赛人数
CWAR_FINAL_DEFEND_TONG_NUM		= 30	# 守城帮会
CWAR_FINAL_DEFEND_LEAGUE_NUM	= 20	# 守方联盟
CWAR_FINAL_ATTACK_TONG_NUM		= 30	# 攻城帮会
CWAR_FINAL_ATTACK_LEAGUE_NUM	= 15	# 攻方联盟

# 传入位置
DEFEND_TONG_ENTER_POS			= 1		# 攻方传入点
DEFEND_LEAGUES_ENTER_POS		= 2		# 攻方联盟传入点
ATTACK_TONG_ENTER_POS			= 3		# 守方传入点
ATTACK_LEFT_LEAGUES_ENTER_POS	= 4		# 守方联盟1传入点
ATTACK_RIGHT_LEAGUES_ENTER_POS	= 5		# 守方联盟2传入点

class CityWarFinalBattleField:
	"""
	夺城战决赛战场
	"""
	def __init__( self, mgr, spaceName, camp ):
		self.spaceName = spaceName
		self.camp = camp						# 阵营
		self.cityWarManager = mgr				# 管理器
		self.uidKey = str( uuid.uuid1() )
		self.warInfos = {}						# { "defend": { tongDBID: maxNum,  tongDBID: maxNum }}
		self.entryTong = {}						# { "defend": tongDBID, "attack": tongDBID }
		self.spaceDomain = None
		self.initEntryTongs( )
		self.cityWarEnter = {}					# { tongDBID: [ plaerID, plaerID ]}

	def initEntryTongs( self ):
		"""
		初始化参赛帮会
		"""
		self.warInfos[ "defend" ] = {}			# 守城方
		self.warInfos[ "attack"] = {}			# 攻城方
		
		defendTong, attackTong = self.getQuarterFinalRecord( )
		self.entryTong[ "defend" ] =  defendTong
		self.entryTong[ "attack" ] =  attackTong
		
		self.warInfos[ "defend" ][ defendTong ] = { "maxNum": CWAR_FINAL_DEFEND_TONG_NUM, "enterPos": DEFEND_TONG_ENTER_POS, "tongName": self.cityWarManager.getTongNameByDBID( defendTong ), }
		self.warInfos[ "attack" ][ attackTong ] = { "maxNum": CWAR_FINAL_ATTACK_TONG_NUM, "enterPos": ATTACK_TONG_ENTER_POS, "tongName": self.cityWarManager.getTongNameByDBID( attackTong ), }
		
		defendLeagues = self.cityWarManager.getBattleLeagueByTongDBID( defendTong )
		attackLeagues = self.cityWarManager.getBattleLeagueByTongDBID( attackTong )
		if len( defendLeagues ) > 1:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: Defend tong %i has more than one league %s!" % ( defendTong, defendLeagues) )
			return
		if len( attackLeagues ) > 2:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: Attack tong %i has more than two league %s!" % ( attackTong, attackLeagues) )
			return
		
		if len( defendLeagues ) == 1:
			self.warInfos[ "defend" ][ defendLeagues[ 0 ] ] = { "maxNum": CWAR_FINAL_DEFEND_LEAGUE_NUM,"enterPos": DEFEND_LEAGUES_ENTER_POS, "tongName": self.cityWarManager.getTongNameByDBID( defendLeagues[ 0 ] ), }
		
		attackLeaguePos = ATTACK_LEFT_LEAGUES_ENTER_POS
		for tongDBID in attackLeagues:
			self.warInfos[ "attack"][ tongDBID ] = { "maxNum": CWAR_FINAL_ATTACK_LEAGUE_NUM, "enterPos": attackLeaguePos, "tongName": self.cityWarManager.getTongNameByDBID( tongDBID ), }
			attackLeaguePos += 1
		
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: Init city war final battleField, warInfos is %s " % self.warInfos )

	def getQuarterFinalRecord( self ):
		"""
		获取半决赛中的决胜帮会
		"""
		defendTong, attackTong = 0, 0
		tongRecord = self.cityWarManager.getQuarterFinalRecord( self.camp, self.spaceName )
		for tongDBID, rank in tongRecord.iteritems():
			if rank == 1:
				defendTong = tongDBID
			elif rank == 2:
				attackTong = tongDBID
		return defendTong, attackTong

	def checkTongQualification( self, tongDBID ):
		"""
		检查帮会的参赛资格
		"""
		for key, item in self.warInfos.iteritems():
			if tongDBID in item.keys():
				return True
		return False

	def getEnterTongInfo( self, tongDBID ):
		"""
		获取帮会信息( 最大进入人数和进入位置 )
		"""
		for key, item in self.warInfos.iteritems():
			for dbid in item.keys():
				if dbid == tongDBID:
					return item[ dbid ]["maxNum"], item[ dbid ]["enterPos"]
		return 0

	def onRoleEnterSpace( self,spaceDomain, baseMailbox, params ):
		"""
		玩家进入空间,确定进入位置
		"""
		if not self.spaceDomain:
			self.spaceDomain = spaceDomain

			params[ "tongInfos"] = self.warInfos
			defendTong, attackTong = self.entryTong[ "defend" ], self.entryTong[ "attack" ]
			params[ "defend" ] = defendTong
			params[ "attack" ] = attackTong

		islogin = params.has_key( "login" )
		tongDBID = params[ "tongDBID" ]
		roleDBID = params[ "roleDBID" ]

		maxNum, enterPos = self.getEnterTongInfo( tongDBID )
		# 进入空间人数检测
		if tongDBID in self.cityWarEnter and  len( self.cityWarEnter[ tongDBID ] ) > maxNum:
			baseMailbox.cell.statusMessage( csstatus.TONG_CITY_WAR_CANT_ENTER_PLAYER_LIMIT )
			return
		
		if islogin:
			baseMailbox.logonSpaceInSpaceCopy()
			return

		params[ "spaceKey" ] = self.uidKey
		params[ "enterPos"] = self.getEnterTongInfo( tongDBID )[ 1 ]
		self.spaceDomain.onRoleEnterSpace( baseMailbox, params )
		self.cityWarFinalAddEnter( tongDBID, roleDBID, baseMailbox )

	def onRoleLeaveSpace( self, tongDBID, roleDBID ):
		"""
		玩家离开战场
		"""
		if tongDBID not in self.cityWarEnter:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: tongDBID %i is not in my field, spaceName %s, camp %i" % (tongDBID, self.spaceName, self.camp ))
			return
		for tongDBID, item in self.cityWarEnter.iteritems():
			for info in item:
				if info[ 0 ] == roleDBID:
					self.cityWarEnter[ tongDBID ].remove( info )

	def  cityWarFinalAddEnter( self, tongDBID, roleDBID, baseMB ):
		"""
		夺城战决赛参赛人员
		"""
		if tongDBID not in self.cityWarEnter:
			self.cityWarEnter[ tongDBID ] = []
		self.cityWarEnter[ tongDBID ].append( ( roleDBID, baseMB ) )

	def battleFieldReset( self ):
		"""
		战场重置
		"""
		self.resetEntryTongs()

	def resetEntryTongs( self ):
		"""
		重置参赛帮会,联盟帮会可进入战场数量不再发生改变
		"""
		oldDefendTong = self.entryTong[ "defend" ]
		oldAttackTong = self.entryTong[ "attack" ]
		self.entryTong[ "defend" ] = oldAttackTong
		self.entryTong[ "attack" ] = oldDefendTong
		
		newWarInfos = {}
		newWarInfos[ "defend" ] = {}			# 守城方
		newWarInfos[ "attack"] = {}			# 攻城方
		
		for key, item in self.warInfos.iteritems():
			# 守城方将变为攻城方
			if key == "defend":
				for tongDBID in item.keys():
					maxNum = item[ tongDBID ][ "maxNum" ]
					if tongDBID == oldDefendTong:
						enterPos = ATTACK_TONG_ENTER_POS
					else:
						enterPos = ATTACK_LEFT_LEAGUES_ENTER_POS
					newWarInfos[ "attack"][ tongDBID ] = { "maxNum": maxNum, "enterPos":  enterPos }
			# 攻城方变成守城方
			elif key == "attack":
				for tongDBID in item.keys():
					maxNum = item[ tongDBID ]
					if tongDBID == oldAttackTong:
						enterPos = DEFEND_TONG_ENTER_POS
					else:
						enterPos = DEFEND_LEAGUES_ENTER_POS
					newWarInfos[ "defend" ][ tongDBID ] = { "maxNum": maxNum, "enterPos": enterPos }
		
		self.warInfos = newWarInfos

	def closeBattleField( self ):
		"""
		关闭战场
		"""
		self.spaceDomain.closeAllSpace()

	def sendMessage2Alliance( self, tong_dbID, speakerID, speakerName, msg, blobArgs ):
		
		"""
		广播玩家的发言内容到战场中的同盟成员的 client
		"""
		battleKey = ""
		for key, item in self.warInfos.iteritems():
			if tong_dbID in item.keys():
				battleKey= key
				break
		if not battleKey:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: %i not in this battle, spaceName %s, camp %i" % ( tong_dbID, self.spaceName, self.camp ) )
			return
		battleLeagues = self.warInfos[ battleKey ].keys()
		for tongDBID, item in self.cityWarEnter.iteritems():
			if tongDBID in battleLeagues:
				for info in item:
					info[ 1 ].client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_TONG_CITY_WAR, speakerID, speakerName, msg, blobArgs )

class TongCityWarFinalManager:
	"""
	帮会夺城战决赛
	"""
	def __init__( self ):
		self.cityWarBattlefield = {}	# 每个阵营一个战场 { 阵营：( 战场,key ) }
		self.cityWarFinalSpaceBases = []

	#-----------------------------------------------------任务计划相关------------------------------------------
	def onManagerInitOver( self ):
		"""
		virtual method.
		管理器初始化完毕
		"""
		self.tongCityWarFinalManager_registerCrond()
	
	def tongCityWarFinalManager_registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
					  	"TongCityWarFinalManager_notice"			: "onCityWarFinalNotice",			# 城战决赛通知
					  	"TongCityWarFinalManager_start" 			: "onCityWarFinalStart", 			# 城战决赛开始
					  	"TongCityWarFinalManager_end" 				: "onCityWarFinalEnd", 				# 城战决赛结束
					  }
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )

	def initCityWarFinalInfos( self ):
		"""
		初始化夺城战决赛的参赛帮会
		"""
		self.cityWarFinalRecords = []
		for item in self.tongFHLTRecords:
			dict = {}
			entryTong = {}
			spaceName = item[ "spaceName" ]
			tongInfos = item[ "tongInfos" ]
			tongInfos.sort( key = lambda e: e[ "integral"], reverse = True )	# 根据积分排序
			for tongInfo in tongInfos:
				camp = self.getTongCampByDBID( tongInfo[ "tongDBID" ] )
				if camp not in entryTong:
					entryTong[ camp ] = []
				entryTong[ camp ].append( tongInfo )							# 根据阵营分类
			
			dict[ "spaceName" ] = spaceName
			dict[ "tongInfos" ] = {}
			for camp in entryTong:
				dict[ "camp" ] = camp
				dict[ "tongInfos" ] = entryTong[ camp ][ :2 ]					# 只选择每个阵营前两名
			
			self.cityWarFinalInfos.append( dict )

	def getQuarterFinalRecord( self, camp = 0, spaceName = "" ):
		"""
		define method
		获取半决赛（烽火连天）的结果
		"""
		tongRecord = {}
		for item in self.cityWarFinalInfos:
			if camp and item[ "camp" ] != camp:
				continue
			if spaceName and item[ "spaceName" ] != spaceName:
				continue
			
			tongInfos = item[ "tongInfos" ]
			for info in tongInfos:
				tongDBID = info[ "tongDBID" ]
				rand = tongInfos.index( info ) + 1
				tongRecord[ tongDBID ] = rand
		
		return tongRecord

	def onCityWarFinalNotice( self ):
		"""
		define method
		城战决赛通知
		30分钟、15分钟、5分钟各一次
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_CITY_WAR_FINAL_NOTIFY % ( 30 ), [] )			# 活动开始前30分钟第一次公告
		self.addTimer( SECOND_GLOBAL_NOTICE_INTERVAL, 0, GLOBAL_NOTICE_TIMER_SECOND )

	def onCityWarFinalStart( self ):
		"""
		define method
		城战决赛开始
		"""
		if BigWorld.globalData.has_key( "TONG_CITY_WAR_FINAL_END_TIME" ):
			return
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_CITY_WAR_FINAL_START_NOTIFY, [] )			# 活动开始公告
		BigWorld.globalData[ "TONG_CITY_WAR_FINAL_END_TIME" ] = time.time() + CITY_WAR_FINAL_LAST_TIME
		self.initCityWarBattleField()

	def initCityWarBattleField( self ):
		"""
		初始化帮会战场，每个城市的每个阵营一个战场
		"""
		for item in self.cityWarFinalInfos:
			spaceName = item[ "spaceName" ]
			camp = item[ "camp" ]
			battleField = CityWarFinalBattleField( self, spaceName, camp )
			if spaceName not in self.cityWarBattlefield:
				self.cityWarBattlefield[ spaceName] = {}
			self.cityWarBattlefield[ spaceName ][ camp ] = ( battleField, battleField.uidKey )

	def onCityWarFinalEnd( self ):
		"""
		define method
		城战决赛结束
		"""
		if BigWorld.globalData.has_key( "TONG_CITY_WAR_FINAL_END_TIME" ):
			del BigWorld.globalData[ "TONG_CITY_WAR_FINAL_END_TIME" ]
		 
		# 关闭所有战场
		self.closeAllBattleField()

	def onTimer( self, timerID, userArg ):
		"""
		"""
		if userArg == GLOBAL_NOTICE_TIMER_SECOND:			# 活动开始前15分钟第二次公告
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_CITY_WAR_FINAL_NOTIFY % ( 15 ), [] )
			self.addTimer( THIRD_GLOBAL_NOTICE_INTERVAL, 0, GLOBAL_NOTICE_TIMER_THIRD )

		elif userArg == GLOBAL_NOTICE_TIMER_THIRD:			# 活动开始前5分钟第三次公告
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_CITY_WAR_FINAL_NOTIFY % ( 5 ), [] )

	def requestEnterCityWarFinal( self, tongDBID, playerBaseMB, camp, spaceName, spaceKey ):
		"""
		define method
		对话请求进入帮会夺城战决赛
		"""
		DEBUG_MSG( "TONG_CITY_WAR: Role %i, tong %i, request enter city final！spaceName %s, spaceKey %s" % ( playerBaseMB.id, tongDBID, spaceName, spaceKey ) )
		
		# 决赛是否开始
		if not BigWorld.globalData.has_key( "TONG_CITY_WAR_FINAL_END_TIME" ):
			self.statusMessage( playerBaseMB,  csstatus.TONG_CITY_WAR_NO_WAR )
			return
		
		if spaceName not in self.cityWarBattlefield.keys():
			self.statusMessage( playerBaseMB,  csstatus.TONG_CITY_WAR_CANNOT_ENTER )
			return
		
		# 是否有参赛资格
		battleField = self.cityWarBattlefield[ spaceName ][ camp ][ 0 ]
		if not battleField.checkTongQualification( tongDBID ):
			self.statusMessage( playerBaseMB,  csstatus.TONG_CITY_WAR_CANNOT_ENTER )
			return
		
		playerBaseMB.cell.tong_gotoCityWar( spaceKey )

	def onEnterCityWarFinalSpace( self, spaceDomain, baseMailbox, params ):
		"""
		define method
		由SpaceDomain调用过来
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: Begin teleport %i to cityFianl space, params is %s " % ( baseMailbox.id, params ) )
		
		spaceName = params[ "spaceName" ]
		battleField = self.cityWarBattlefield[ spaceName ][ params[ "camp" ] ][ 0 ]
		battleField.onRoleEnterSpace( spaceDomain, baseMailbox, params )

	def requestBattleFieldReset( self, uidKey ):
		"""
		define method
		请求战场重置
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: %s request to reset battle field!" % uidKey )
		battleField = self.getBattleFieldByUIDKey( uidKey )
		if battleField:
			battleField.battleFieldReset()
		else:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: Can't find battle field by uidKey %s" % uidKey )

	def getBattleFieldByUIDKey( self, uidKey ):
		"""
		根据uidKey查找战场
		"""
		for spaceName, item in self.cityWarBattlefield.iteritems():
			for camp, battle in item.iteritems():
				if battle[ 1 ] ==  uidKey:
					battleField = battle[ 0 ]
					return battleField
		return None

	def cityWarFinalLeave( self, uidKey, tongDBID, roleDBID ):
		"""
		define method
		玩家离开战场
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: %s has role leave space, tongDBID %i, roleDBID %i " % ( uidKey, tongDBID, roleDBID ) )
		battleField = self.getBattleFieldByUIDKey( uidKey )
		if battleField:
			battleField.onRoleLeaveSpace( tongDBID, roleDBID )
		else:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: Can't find battle field by uidKey %s" % uidKey )

	def closeAllBattleField( self ):
		"""
		关闭所有战场
		"""
		for spaceBase in self.cityWarFinalSpaceBases:
			spaceBase.cell.onCityWarFinalEnd()

	def registerCityWarFinalSpaceBase( self, spaceBase ):
		"""
		define method
		注册战场空间
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: Space %i register self on manager" % spaceBase.id )
		self.cityWarFinalSpaceBases.append( spaceBase )

	def unRegisterCityWarFianlSpaceBase( self, spaceBase ):
		"""
		define method
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: Space %i unregister self on manager" % spaceBase.id )
		for space in self.cityWarFinalSpaceBases:
			if space.id == spaceBase.id:
				self.cityWarFinalSpaceBases.remove( space )
		
	def onGetCityWarFinalRecords( self, uidKey, integrations, winner ):
		"""
		define method
		获得帮会夺城战积分
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: Tong manager get city war final integration %s "  % integrations )
		battleField = self.getBattleFieldByUIDKey( uidKey )
		if not battleField:
			return
		spaceName = battleField.spaceName
		camp = battleField.camp
		for record in integrations:
			self.setCityWarFinalRecords( spaceName, camp, record )
		
		cityName = g_maps_info[ spaceName ]
		tongName = self.getTongNameByDBID( winner )
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_CITY_WAR_FINAL_END_NOTIFY % ( tongName,cityName, g_camp_info[ camp ], ), [] )

	def setCityWarFinalRecords( self, cityName, camp, record ):
		"""
		设置帮会夺城战结果
		"""
		isFind = False
		for infos in self.cityWarFinalRecords:
			if infos[ "spaceName" ] == cityName:
				infos[ "tongInfos" ].append( record )
				isFind = True
				break
		
		if not isFind:
			self.cityWarFinalRecords.append( { "spaceName" : cityName, "tongInfos" : [ record ] } )
		
		self.writeToDB()
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: Set city war final record: cityName: %s, camp %i, record %s, result %s" % ( cityName, camp, record, self.cityWarFinalRecords ) )

	def sendMessage2Alliance( self, tong_dbID, speakerID, speakerName, msg, blobArgs ):
		
		"""
		define method.
		广播玩家的发言内容到同盟成员的 client
		@param				chid	: 广播频道 ID
		@type				chid	: INT8
		@param				spkID	: OBJECT_ID
		@type				spkID	: 发言者 entityID
		@param				spkName : 源说话者名字
		@type				spkName : STRING
		@param				msg		: 消息内容
		@type				msg		: STRING
		@type				blobArgs: BLOB_ARRAY
		@param				blobArgs: 消息参数列表
		@return						: 一个声明了的方法，没有返回值
		成员.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_TONG_CITY_WAR, speakerID, speakerName, msg, blobArgs )
		"""
		battleField = self.getBattleFieldByTongDBID( tong_dbID )
		if battleField:
			battleField.sendMessage2Alliance( tong_dbID, speakerID, speakerName, msg, blobArgs )

	def getBattleFieldByTongDBID( self, tong_dbID ):
		"""
		帮会帮会ID找到战场
		"""
		spaceName = ""
		camp = self.getTongCampByDBID( tong_dbID )
		battleLeagues = self.getBattleLeagueByTongDBID( tong_dbID )
		for item in self.cityWarFinalInfos:
			spaceName = item[ "spaceName" ]
			tongInfos = item[ "tongInfos" ]
			for info in tongInfos:
				tongDBID = info[ "tongDBID" ]
				if tongDBID == tong_dbID or tongDBID in battleLeagues:
					battleField = self.cityWarBattlefield[ spaceName ][ camp ][ 0 ]
					return battleField
		return None
