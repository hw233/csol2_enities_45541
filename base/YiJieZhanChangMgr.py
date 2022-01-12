# -*- coding: gb18030 -*-

# python
import random
import time
# bigworld
import BigWorld
# common
from bwdebug import INFO_MSG,WARNING_MSG,ERROR_MSG
import csdefine
import csconst
# locale_default
import csstatus
import cschannel_msgs
# base
import Love3
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
from ObjectScripts.GameObjectFactory import g_objFactory


# 活动状态
ACTIVITY_STATE_START			= 1
ACTIVITY_STATE_JOIN_TIME_OVER	= 2
ACTIVITY_STATE_END				= 3

# 战场内阵营：天、地、人
FACTION_TIAN					= csdefine.YI_JIE_ZHAN_CHANG_FACTION_TIAN
FACTION_DI						= csdefine.YI_JIE_ZHAN_CHANG_FACTION_DI
FACTION_REN						= csdefine.YI_JIE_ZHAN_CHANG_FACTION_REN

SPACE_CLASS_NAME = "fu_ben_yi_jie_zhan_chang"

class YiJieZhanChangMgr( BigWorld.Base ) :
	# 异界战场管理器
	def __init__( self ) :
		BigWorld.Base.__init__( self )
		self.registerGlobally( "YiJieZhanChangMgr", self._onRegisterManager )
		self.spaceType = SPACE_CLASS_NAME
		self.__activityState = ACTIVITY_STATE_END
		
		self.__minLevel		= 0
		self.__maxLevel		= 0
		self.__minPlayer	= 0
		self.__maxPlayer	= 0
		self.__enterInfos	= None
		self.__needShowYiJieScoreOnLogin = {}		# 需要在上线时显示异界积分榜界面的玩家字典 { playerDBID : roleInfos }
		
		# 战场信息，战场分满员战场和未满员战场，内部字典形式为 { spaceNumber : BattleInfo( spaceNumber, self.__maxPlayer ) , }
		self.__battlegroundInfos = { "atFullStrength" : {}, "notAtFull" : {} }
		self.initConfigData( self.getScript() )
	
	def _onRegisterManager( self, complete ) :
		"""
		注册全局 Base 的回调函数
		@param complete :	完成标志
		@type  complete :	bool
		"""
		if not complete :
			ERROR_MSG( "Register YiJieZhanChangMgr Fail !" )
			self.registerGlobally( "YiJieZhanChangMgr", self._onRegisterManager )
		else :
			BigWorld.globalData["YiJieZhanChangMgr"] = self			# 注册到所有的服务器中
			INFO_MSG("YiJieZhanChangMgr Create Complete !")
			self.__registerCrond()
	
	def __registerCrond( self ) :
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"YiJieZhanChang_notice" : "onNotice",
						"YiJieZhanChang_start" : "onStart",
						"YiJieZhanChang_JoinTimeOver" : "onJoinTimeOver",
						"YiJieZhanChang_end" : "onEnd",
						}
		
		for taskName,callbackName in taskEvents.iteritems() :
			for cmd in g_CrondDatas.getTaskCmds( taskName ) :
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )
		BigWorld.globalData["Crond"].addAutoStartScheme( "YiJieZhanChang_start", self, "onStart" )
	
	def getScript( self ) :
		return g_objFactory.getObject( self.spaceType )
	
	def initConfigData( self, objScript ) :
		"""
		初始化副本配置数据
		"""
		self.__minLevel		= objScript.minLevel
		self.__maxLevel		= objScript.maxLevel
		self.__minPlayer	= objScript.minPlayer
		self.__maxPlayer	= objScript.maxPlayer
		
		infos	= objScript.enterInfos
		self.__enterInfos = { FACTION_TIAN : infos[0], FACTION_DI : infos[1], FACTION_REN : infos[2] }
	
	def __initBattlegroundData( self ) :
		"""
		活动开始时初始化战场数据
		"""
		self.__battlegroundInfos = { "atFullStrength" : {}, "notAtFull" : {} }
		self.__needShowYiJieScoreOnLogin = {}
		
	
	def getBattlegroundItemKey( self, level ) :
		"""
		获取 key
		"""
		return None
	
	def onNotice( self ) :
		"""
		<define method>
		活动开始前的系统公告
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.WIZCOMMAND_YI_JIE_ZHAN_CHANG_NOTICE, [] )
		INFO_MSG( "YiJieZhanChangMgr","onNotice" )
	
	def onStart( self ) :
		"""
		<define method>
		活动开始
		"""
		if self.__activityState == ACTIVITY_STATE_START :
			WARNING_MSG( " YiJieZhanChang activity already start! " )
			return
		self.__activityState = ACTIVITY_STATE_START
		BigWorld.globalData["YiJieZhanChang_StartTime"] = time.time()
		self.__initBattlegroundData()
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.WIZCOMMAND_YI_JIE_ZHAN_CHANG_START, [] )
		self.__broadcastAllLevelSatisfyPlayers()
		INFO_MSG( "YiJieZhanChangMgr","onStart" )
	
	def __broadcastAllLevelSatisfyPlayers( self ) :
		"""
		通知所有符合等级条件的玩家活动开始
		"""
		for player in Love3.g_baseApp.iterOnlinePlayers() :
			if hasattr( player, "level" ) :
				if player.level > self.__minLevel :
					player.client.yiJieShowSignUp()
			else :
				player.cell.yiJieCheckShowSignUp()
	
	def onJoinTimeOver( self ) :
		"""
		<define method>
		入场时间结束
		"""
		self.__activityState = ACTIVITY_STATE_JOIN_TIME_OVER
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.WIZCOMMAND_YI_JIE_ZHAN_CHANG_JOIN_TIME_OVER, [] )
		INFO_MSG( "YiJieZhanChangMgr","onJoinTimeOver" )
	
	def onEnd( self ) :
		"""
		<define method>
		活动结束
		"""
		self.__activityState = ACTIVITY_STATE_END
		if BigWorld.globalData.has_key( "YiJieZhanChang_StartTime" ) :
			del BigWorld.globalData["YiJieZhanChang_StartTime"]
		spaceNumberList = self.__battlegroundInfos["atFullStrength"].keys() + self.__battlegroundInfos["notAtFull"].keys()
		BigWorld.globalData[ "SpaceManager" ].remoteCallDomain( self.spaceType, "activityEnd", [ spaceNumberList, ] )
		INFO_MSG( "YiJieZhanChangMgr","onEnd" )
	
	def requestEnterSpace( self, domainBase, position, direction, baseMailbox, params ) :
		"""
		<define method>
		玩家申请进入战场
		"""
		# 等级小于 self.__minLevel 不能进入
		level = params["level"]
		if level < self.__minLevel :
			baseMailbox.client.onStatusMessage( csstatus.YI_JIE_ZHAN_CHANG_ENTER_LEVEL, str( (self.__minLevel,) ) )
			return
		# 不在入场时间内不能进入
		if self.__activityState == ACTIVITY_STATE_JOIN_TIME_OVER :
			baseMailbox.client.onStatusMessage( csstatus.YI_JIE_ZHAN_CHANG_JOIN_TIME_OVER, "" )
			return
		elif self.__activityState == ACTIVITY_STATE_END :
			baseMailbox.client.onStatusMessage( csstatus.YI_JIE_ZHAN_CHANG_ACTIVITY_END, "" )
			return
		# 组队玩家不能进入
		if params.has_key( "teamID" ) :
			baseMailbox.client.onStatusMessage( csstatus.YI_JIE_ZHAN_CHANG_TEAM_ABANDON, "" )
			return
		# 
		targetSpaceNumber = self.__getTargetSpaceNumber()
		faction = None
		if targetSpaceNumber == None :
			factions = [ FACTION_TIAN, FACTION_DI, FACTION_REN ]
			faction = random.choice( factions )
		else :
			faction = self.__battlegroundInfos["notAtFull"][targetSpaceNumber].getRandomFaction()
		params["spaceKey"] = targetSpaceNumber
		params["faction"] = faction
		pos,dir = self.__enterInfos[ faction ]
		domainBase.teleportEntityToYiJie( pos, dir, baseMailbox, params )
	
	def requestEnterSpaceOnLogin( self, domainBase, baseMailbox, params ) :
		"""
		<define method>
		玩家重新登录的时候,申请进入战场
		"""
		lastOfflinePlayerInfo = self.__getLastOfflinePlayerInfo( params["dbID"] )
		params["lastOfflinePlayerInfo"] = lastOfflinePlayerInfo
		domainBase.teleportEntityToYiJieOnLogin( baseMailbox, params )
	
	def playerExit( self, spaceNumber, pMB ) :
		"""
		<define method>
		玩家退出副本
		"""
		pass
	
	def __getTargetSpaceNumber( self ) :
		"""
		获取要进入的目标战场,最早开启且未满员的战场
		"""
		# 规则：选择最早创建且人数不满的战场，没有则返回 None
		if self.__battlegroundInfos["notAtFull"] :
			return self.__battlegroundInfos["notAtFull"].keys()[0]
		else :
			return None
	
	def __getLastOfflinePlayerInfo( self, playerDBID ) :
		"""
		获取上一次离线时的玩家信息 ( spaceNumber, faction )
		"""
		battlegroundInfos = self.__battlegroundInfos["notAtFull"].values() + self.__battlegroundInfos["atFullStrength"].values()
		for info in battlegroundInfos :
			if info.hasPlayer( playerDBID ) :
				return ( info.spaceNumber, info.getPlayerFaction( playerDBID ) )
		return None
	
	def addNewSpaceNumber( self, spaceNumber ) :
		"""
		<define method>
		添加一个新的战场
		"""
		if not self.__battlegroundInfos["notAtFull"].has_key( spaceNumber ) :
			self.__battlegroundInfos["notAtFull"][spaceNumber] = BattlegroundInfo( spaceNumber, self.__maxPlayer )
	
	def removeSpaceNumber( self, spaceNumber ) :
		"""
		<define method>
		删除一个战场
		"""
		if self.__battlegroundInfos["atFullStrength"].has_key( spaceNumber ) :
			del self.__battlegroundInfos["atFullStrength"][spaceNumber]
		
		elif self.__battlegroundInfos["notAtFull"].has_key( spaceNumber ) :
			del self.__battlegroundInfos["notAtFull"][spaceNumber]
		else :
			ERROR_MSG("spaceNumber %s isn't exit." % spaceNumber )
			
	def onPlayerEnterBattleground( self, playerDBID, spaceNumber, faction ) :
		"""
		<define method>
		玩家进入战场回调
		"""
		if self.__battlegroundInfos["notAtFull"].has_key( spaceNumber ) :
			self.__battlegroundInfos["notAtFull"][spaceNumber].addOnePlayer( playerDBID, faction )
			if self.__battlegroundInfos["notAtFull"][spaceNumber].totalPlayerNumber == self.__maxPlayer :
				self.__battlegroundInfos["atFullStrength"][spaceNumber] = self.__battlegroundInfos["notAtFull"][spaceNumber]
				del self.__battlegroundInfos["notAtFull"][spaceNumber]
		else :
			self.__battlegroundInfos["notAtFull"][spaceNumber] = BattlegroundInfo( spaceNumber, self.__maxPlayer )
			self.__battlegroundInfos["notAtFull"][spaceNumber].addOnePlayer( playerDBID, faction )
	
	def onPlayerLeaveBattleground( self, playerDBID, spaceNumber ) :
		"""
		<define method>
		玩家离开战场回调
		"""
		if self.__battlegroundInfos["atFullStrength"].has_key( spaceNumber ) :
			self.__battlegroundInfos["atFullStrength"][spaceNumber].delOnePlayer( playerDBID )
			self.__battlegroundInfos["notAtFull"][spaceNumber] = self.__battlegroundInfos["atFullStrength"][spaceNumber]
			del self.__battlegroundInfos["atFullStrength"][spaceNumber]
		
		elif self.__battlegroundInfos["notAtFull"].has_key( spaceNumber ) :
			self.__battlegroundInfos["notAtFull"][spaceNumber].delOnePlayer( playerDBID )
		else :
			ERROR_MSG( "Leave battleground [spaceNumber : %s] isn't exit." % spaceNumber )
		
		if self.__battlegroundInfos["notAtFull"][spaceNumber].totalPlayerNumber < self.__minPlayer :
			self.closeSpaceCopy( spaceNumber )

	def closeSpaceCopy( self, spaceNumber ) :
		"""
		<define method>
		关闭指定的副本
		"""
		BigWorld.globalData[ "SpaceManager" ].remoteCallDomain( self.spaceType, "closeSpaceCopy", [ spaceNumber ] )
	
	def addNeedShowYiJieScorePlayer( self, playerDBID, roleInfos ) :
		"""
		<define method>
		添加一名需要上线显示异界积分榜的玩家
		"""
		self.__needShowYiJieScoreOnLogin[ playerDBID ] = roleInfos
	
	def removeNeedShowYiJieScorePlayer( self, playerDBID ) :
		"""
		<define method>
		删除一名需要上线显示异界积分榜的玩家
		"""
		if playerDBID in self.__needShowYiJieScoreOnLogin :
			del self.__needShowYiJieScoreOnLogin[ playerDBID ]
	
	def queryNeedShowYiJieScore( self, playerDBID, playerCellMB ) :
		"""
		<define method>
		查询玩家是否需要显示异界积分榜界面
		"""
		if playerDBID in self.__needShowYiJieScoreOnLogin :
			roleInfos = self.__needShowYiJieScoreOnLogin[ playerDBID ]
			playerCellMB.onQueryNeedShowYiJieScore( roleInfos )
			del self.__needShowYiJieScoreOnLogin[ playerDBID ]

	def getFactionEnterInfos( self, faction ):
		"""
		取得指定阵营的进入位置
		"""
		if faction == FACTION_TIAN :
			return self.__enterInfos[0]
		elif faction == FACTION_DI :
			return self.__enterInfos[1]
		elif faction == FACTION_REN :
			return self.__enterInfos[2]
		else :
			ERROR_MSG( "faction %s isn't exit." % faction )
			return None


class BattlegroundInfo :
	"""
	战场信息
	"""
	def __init__( self, spaceNumber, maxPlayer ) :
		self.spaceNumber = spaceNumber
		self.__maxPlayer = maxPlayer
		self.__tian = []
		self.__di = []
		self.__ren = []
		self.__factions = [ FACTION_TIAN, FACTION_DI, FACTION_REN ]
		
	
	@property
	def totalPlayerNumber( self ) :
		"""
		战场内总人数
		"""
		return len( self.__tian ) +  len( self.__di ) + len( self.__ren )
	
	
	def addOnePlayer( self, playerDBID, faction ) :
		"""
		添加一个玩家
		"""
		if self.totalPlayerNumber == self.__maxPlayer :
			ERROR_MSG( "the battleground [sapceNumber : %s] is at full strength." % self.spaceNumber  )
			return
		if self.hasPlayer( playerDBID ) :
			ERROR_MSG( "the player [dbID : %s] is already in battleground [sapceNumber : %s] is at full strength." % ( playerDBID, self.spaceNumber ) )
			return
		if faction == FACTION_TIAN :
			self.__tian.append( playerDBID )
		elif faction == FACTION_DI :
			self.__di.append( playerDBID )
		else :
			self.__ren.append( playerDBID )
		
	def delOnePlayer( self, playerDBID ) :
		"""
		删除一个玩家
		"""
		factions = [ self.__tian, self.__di, self.__ren ]
		for faction in factions :
			if playerDBID in faction :
				faction.remove( playerDBID )
				return
		ERROR_MSG( "player [dbID : %s] isn't in the battleground [sapceNumber : %s]." % ( playerDBID, self.spaceNumber ) )
	
	def hasPlayer( self, playerDBID ) :
		total = self.__tian + self.__di + self.__ren
		return playerDBID in total
	
	def getPlayerFaction( self, playerDBID ) :
		if playerDBID in self.__tian :
			return FACTION_TIAN
		elif playerDBID in self.__di :
			return FACTION_DI
		elif playerDBID in self.__ren :
			return FACTION_REN
		else :
			return None
	
	def getRandomFaction( self ) :
		"""
		获得随机阵营
		"""
		self.__updateCanChoiceFactions()
		faction = None
		if self.__factions :
			faction =  random.choice( self.__factions )
			self.__factions.remove( faction )
		else :
			self.__factions = [ FACTION_TIAN, FACTION_DI, FACTION_REN ]
			faction =  random.choice( self.__factions )
			self.__factions.remove( faction )
		return faction

	def __updateCanChoiceFactions( self ) :
		"""
		更新可选的阵营
		"""
		if len( self.__tian ) == self.__maxPlayer / 3 and  ( FACTION_TIAN in self.__factions ):
			self.__factions.remove( FACTION_TIAN )
		if len( self.__di ) == self.__maxPlayer / 3 and  ( FACTION_DI in self.__factions ) :
			self.__factions.remove( FACTION_DI )
		if len( self.__ren ) == self.__maxPlayer / 3 and  ( FACTION_REN in self.__factions ) :
			self.__factions.remove( FACTION_REN )
		
		if self.totalPlayerNumber == 1 :
			self.__factions = [ FACTION_TIAN, FACTION_DI, FACTION_REN ]
			if self.__tian :
				self.__factions.remove( FACTION_TIAN )
			elif self.__di :
				self.__factions.remove( FACTION_DI )
			else :
				self.__factions.remove( FACTION_REN )



