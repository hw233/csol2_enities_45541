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


# �״̬
ACTIVITY_STATE_START			= 1
ACTIVITY_STATE_JOIN_TIME_OVER	= 2
ACTIVITY_STATE_END				= 3

# ս������Ӫ���졢�ء���
FACTION_TIAN					= csdefine.YI_JIE_ZHAN_CHANG_FACTION_TIAN
FACTION_DI						= csdefine.YI_JIE_ZHAN_CHANG_FACTION_DI
FACTION_REN						= csdefine.YI_JIE_ZHAN_CHANG_FACTION_REN

SPACE_CLASS_NAME = "fu_ben_yi_jie_zhan_chang"

class YiJieZhanChangMgr( BigWorld.Base ) :
	# ���ս��������
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
		self.__needShowYiJieScoreOnLogin = {}		# ��Ҫ������ʱ��ʾ�����ְ���������ֵ� { playerDBID : roleInfos }
		
		# ս����Ϣ��ս������Աս����δ��Աս�����ڲ��ֵ���ʽΪ { spaceNumber : BattleInfo( spaceNumber, self.__maxPlayer ) , }
		self.__battlegroundInfos = { "atFullStrength" : {}, "notAtFull" : {} }
		self.initConfigData( self.getScript() )
	
	def _onRegisterManager( self, complete ) :
		"""
		ע��ȫ�� Base �Ļص�����
		@param complete :	��ɱ�־
		@type  complete :	bool
		"""
		if not complete :
			ERROR_MSG( "Register YiJieZhanChangMgr Fail !" )
			self.registerGlobally( "YiJieZhanChangMgr", self._onRegisterManager )
		else :
			BigWorld.globalData["YiJieZhanChangMgr"] = self			# ע�ᵽ���еķ�������
			INFO_MSG("YiJieZhanChangMgr Create Complete !")
			self.__registerCrond()
	
	def __registerCrond( self ) :
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
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
		��ʼ��������������
		"""
		self.__minLevel		= objScript.minLevel
		self.__maxLevel		= objScript.maxLevel
		self.__minPlayer	= objScript.minPlayer
		self.__maxPlayer	= objScript.maxPlayer
		
		infos	= objScript.enterInfos
		self.__enterInfos = { FACTION_TIAN : infos[0], FACTION_DI : infos[1], FACTION_REN : infos[2] }
	
	def __initBattlegroundData( self ) :
		"""
		���ʼʱ��ʼ��ս������
		"""
		self.__battlegroundInfos = { "atFullStrength" : {}, "notAtFull" : {} }
		self.__needShowYiJieScoreOnLogin = {}
		
	
	def getBattlegroundItemKey( self, level ) :
		"""
		��ȡ key
		"""
		return None
	
	def onNotice( self ) :
		"""
		<define method>
		���ʼǰ��ϵͳ����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.WIZCOMMAND_YI_JIE_ZHAN_CHANG_NOTICE, [] )
		INFO_MSG( "YiJieZhanChangMgr","onNotice" )
	
	def onStart( self ) :
		"""
		<define method>
		���ʼ
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
		֪ͨ���з��ϵȼ���������һ��ʼ
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
		�볡ʱ�����
		"""
		self.__activityState = ACTIVITY_STATE_JOIN_TIME_OVER
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.WIZCOMMAND_YI_JIE_ZHAN_CHANG_JOIN_TIME_OVER, [] )
		INFO_MSG( "YiJieZhanChangMgr","onJoinTimeOver" )
	
	def onEnd( self ) :
		"""
		<define method>
		�����
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
		����������ս��
		"""
		# �ȼ�С�� self.__minLevel ���ܽ���
		level = params["level"]
		if level < self.__minLevel :
			baseMailbox.client.onStatusMessage( csstatus.YI_JIE_ZHAN_CHANG_ENTER_LEVEL, str( (self.__minLevel,) ) )
			return
		# �����볡ʱ���ڲ��ܽ���
		if self.__activityState == ACTIVITY_STATE_JOIN_TIME_OVER :
			baseMailbox.client.onStatusMessage( csstatus.YI_JIE_ZHAN_CHANG_JOIN_TIME_OVER, "" )
			return
		elif self.__activityState == ACTIVITY_STATE_END :
			baseMailbox.client.onStatusMessage( csstatus.YI_JIE_ZHAN_CHANG_ACTIVITY_END, "" )
			return
		# �����Ҳ��ܽ���
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
		������µ�¼��ʱ��,�������ս��
		"""
		lastOfflinePlayerInfo = self.__getLastOfflinePlayerInfo( params["dbID"] )
		params["lastOfflinePlayerInfo"] = lastOfflinePlayerInfo
		domainBase.teleportEntityToYiJieOnLogin( baseMailbox, params )
	
	def playerExit( self, spaceNumber, pMB ) :
		"""
		<define method>
		����˳�����
		"""
		pass
	
	def __getTargetSpaceNumber( self ) :
		"""
		��ȡҪ�����Ŀ��ս��,���翪����δ��Ա��ս��
		"""
		# ����ѡ�����紴��������������ս����û���򷵻� None
		if self.__battlegroundInfos["notAtFull"] :
			return self.__battlegroundInfos["notAtFull"].keys()[0]
		else :
			return None
	
	def __getLastOfflinePlayerInfo( self, playerDBID ) :
		"""
		��ȡ��һ������ʱ�������Ϣ ( spaceNumber, faction )
		"""
		battlegroundInfos = self.__battlegroundInfos["notAtFull"].values() + self.__battlegroundInfos["atFullStrength"].values()
		for info in battlegroundInfos :
			if info.hasPlayer( playerDBID ) :
				return ( info.spaceNumber, info.getPlayerFaction( playerDBID ) )
		return None
	
	def addNewSpaceNumber( self, spaceNumber ) :
		"""
		<define method>
		���һ���µ�ս��
		"""
		if not self.__battlegroundInfos["notAtFull"].has_key( spaceNumber ) :
			self.__battlegroundInfos["notAtFull"][spaceNumber] = BattlegroundInfo( spaceNumber, self.__maxPlayer )
	
	def removeSpaceNumber( self, spaceNumber ) :
		"""
		<define method>
		ɾ��һ��ս��
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
		��ҽ���ս���ص�
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
		����뿪ս���ص�
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
		�ر�ָ���ĸ���
		"""
		BigWorld.globalData[ "SpaceManager" ].remoteCallDomain( self.spaceType, "closeSpaceCopy", [ spaceNumber ] )
	
	def addNeedShowYiJieScorePlayer( self, playerDBID, roleInfos ) :
		"""
		<define method>
		���һ����Ҫ������ʾ�����ְ�����
		"""
		self.__needShowYiJieScoreOnLogin[ playerDBID ] = roleInfos
	
	def removeNeedShowYiJieScorePlayer( self, playerDBID ) :
		"""
		<define method>
		ɾ��һ����Ҫ������ʾ�����ְ�����
		"""
		if playerDBID in self.__needShowYiJieScoreOnLogin :
			del self.__needShowYiJieScoreOnLogin[ playerDBID ]
	
	def queryNeedShowYiJieScore( self, playerDBID, playerCellMB ) :
		"""
		<define method>
		��ѯ����Ƿ���Ҫ��ʾ�����ְ����
		"""
		if playerDBID in self.__needShowYiJieScoreOnLogin :
			roleInfos = self.__needShowYiJieScoreOnLogin[ playerDBID ]
			playerCellMB.onQueryNeedShowYiJieScore( roleInfos )
			del self.__needShowYiJieScoreOnLogin[ playerDBID ]

	def getFactionEnterInfos( self, faction ):
		"""
		ȡ��ָ����Ӫ�Ľ���λ��
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
	ս����Ϣ
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
		ս����������
		"""
		return len( self.__tian ) +  len( self.__di ) + len( self.__ren )
	
	
	def addOnePlayer( self, playerDBID, faction ) :
		"""
		���һ�����
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
		ɾ��һ�����
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
		��������Ӫ
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
		���¿�ѡ����Ӫ
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



