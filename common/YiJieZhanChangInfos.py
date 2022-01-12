# -*- coding: gb18030 -*-

#python
import time
#bigworld
import BigWorld
#common
import csdefine
import csconst
#locale_default
import csstatus


# 战场内阵营：天、地、人
FACTION_TIAN					= csdefine.YI_JIE_ZHAN_CHANG_FACTION_TIAN
FACTION_DI						= csdefine.YI_JIE_ZHAN_CHANG_FACTION_DI
FACTION_REN						= csdefine.YI_JIE_ZHAN_CHANG_FACTION_REN

FACTION_NAME = { FACTION_TIAN : "天", FACTION_DI : "地", FACTION_REN : "人" }	# 阵营名称

FINAL_BLOW_FACTION_INTEGRAL 	= 10	# 最后一击阵营获得积分值
FIRST_FACTION_REWARD_INTEGRAL	= 100
SECOND_FACTION_REWARD_INTEGRAL	= 80
THRID_FACTION_REWARD_INTEGRAL	= 50


class BattlegroundMgr( object ) :
	"""
	战场管理器
	"""
	def __init__( self ) :
		self.members = {}																# {  playerDBID : BattlegroundMember(), }
		self.offlineMembers = {}
		self.factions = { FACTION_TIAN	: BattlegroundFaction(),
						  FACTION_DI	: BattlegroundFaction(), 
						  FACTION_REN	: BattlegroundFaction(),
						  }
		self.factions[ FACTION_TIAN ].setFaction( FACTION_TIAN )
		self.factions[ FACTION_DI ].setFaction( FACTION_DI )
		self.factions[ FACTION_REN ].setFaction( FACTION_REN )
		
		self.canAlliance = False
		self.firstBlood = False
		self.firstCreate = False
		self.weakestFaction = 0
		self.enrageTimerID = 0
		self.playerMaxRage = 0
		self.spaceID = 0
	
	def createMemberFromDict( self, datas ) : 
		"""
		创建战场成员
		"""
		member = BattlegroundMember()
		member.initMember( datas )
		playerDBID = datas["databaseID"]
		self.members[ playerDBID ] = member
		faction = datas["faction"]
		self.factions[ faction ].members[ playerDBID ] = member
		#self.broadcastMessage( csstatus.YI_JIE_ZHAN_CHANG_ON_JOIN_FACTION, datas["playerName"], FACTION_NAME[ faction ] )
	
	def deleteMember( self, playerDBID ) :
		"""
		删除战场成员
		"""
		if playerDBID in self.members :
			member = self.members[ playerDBID ]
			del self.factions[ member.faction ].members[ playerDBID ]
			del self.members[ playerDBID ]
		elif playerDBID in self.offlineMembers :
			del self.offlineMembers[ playerDBID ]
	
	def onEnterCopy( self, baseMailbox, params ) :
		"""
		成员进入战场时调用
		"""
		playerDBID = params["databaseID"]
		if playerDBID in self.offlineMembers :
			member = self.offlineMembers[ playerDBID ]
			member.playerMB	= baseMailbox
			member.playerID	= baseMailbox.id
			self.members[ playerDBID ] = member
			self.factions[ member.faction ].members[ playerDBID ] = member
			del self.offlineMembers[ playerDBID ]
			self.checkPlayerRage( playerDBID )
			baseMailbox.client.onAngerPointChanged( member.rage )
			baseMailbox.client.yiJieOnKillDataChanged( member.kill, member.keep, member.maxKeep )
			baseMailbox.cell.yiJieOnEnterAgain( member.faction, member.alliance )
		else :
			datas = {}
			datas["playerMB"] 	= baseMailbox
			datas["playerID"] 	= baseMailbox.id
			datas["databaseID"]	= params["databaseID"]
			datas["playerName"]	= params["playerName"]
			datas["faction"]	= params["faction"]
			self.createMemberFromDict( datas )
			baseMailbox.client.onAngerPointChanged( 0 )
			baseMailbox.client.yiJieOnKillDataChanged( 0, 0, 0 )
			allianceFaction = self.factions[ params["faction"] ].alliance
			baseMailbox.cell.yiJieSetAlliance( allianceFaction )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_YIJIE_PLAYER_TIAN, len( self.factions[ FACTION_TIAN ].members ) )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_YIJIE_PLAYER_DI, len( self.factions[ FACTION_DI ].members ) )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_YIJIE_PLAYER_REN, len( self.factions[ FACTION_REN ].members ) )
	
	def onLeaveCopy( self, playerDBID ) :
		"""
		成员离开战场时调用
		"""
		if playerDBID in self.members :
			member = self.members[ playerDBID ]
			member.playerMB	= None
			member.playerID	= 0
			self.offlineMembers[ playerDBID ] = member
			del self.factions[ member.faction ].members[ playerDBID ]
			del self.members[ playerDBID ]
		
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_YIJIE_PLAYER_TIAN, len( self.factions[ FACTION_TIAN ].members ) )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_YIJIE_PLAYER_DI, len( self.factions[ FACTION_DI ].members ) )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_YIJIE_PLAYER_REN, len( self.factions[ FACTION_REN ].members ) )
	
	def broadcastMessage( self, statusID, *args ) :
		"""
		战场内广播
		"""
		sargs = len( args ) and str( args ) or ""
		for m in self.members.values() :
			m.playerMB.client.onStatusMessage( statusID, sargs )
	
	def onKill( self, deadDBID, killerDBID ) :
		"""
		击杀处理
		"""
		dead = self.members[ deadDBID ]
		killer = self.members[ killerDBID ]
		if not self.firstBlood :
			self.broadcastMessage( csstatus.YI_JIE_ZHAN_CHANG_ON_FIRST_BLOOD, killer.playerName )
			self.firstBlood = True
		
		dead.beKill += 1
		dead.keep = 0
		if dead.rage < self.playerMaxRage :
			dead.rage += 1
			dead.playerMB.client.onAngerPointChanged( dead.rage )
		self.factions[ dead.faction ].beKill += 1
		dead.playerMB.client.yiJieOnKillDataChanged( dead.kill, dead.keep, dead.maxKeep )
		
		killer.kill += 1
		killer.keep += 1
		if killer.keep > killer.maxKeep :
			killer.maxKeep = killer.keep
		killer.playerMB.client.yiJieOnKillDataChanged( killer.kill, killer.keep, killer.maxKeep )
		
		if killer.keep % 5 == 0 :			# 连杀数为 5 的倍数
			self.broadcastMessage( csstatus.YI_JIE_ZHAN_CHANG_ON_KEEP_KILL, killer.playerName, killer.keep )
		if killer.kill % 10 == 0 :			# 杀人数为 10 的倍数
			self.broadcastMessage( csstatus.YI_JIE_ZHAN_CHANG_ON_KILL_MANY, killer.playerName )
		
		self.factions[ killer.faction ].kill += 1
		self.factions[ killer.faction ].lastKillTime = time.time()
		self.addFactionIntegral( killer.faction, 1 )
	
	def checkPlayerRage( self, playerDBID ) :
		"""
		玩家激怒检测
		"""
		if not self.members.has_key( playerDBID ) : return
		member = self.members[ playerDBID ]
		if member.rage == self.playerMaxRage :				# 无双技满怒检测
			member.playerMB.cell.yiJieMaxRage( True )
		if self.factions[ member.faction ].enrage  :		# 阵营激怒检测
			member.playerMB.cell.yiJieFactionEnrage( True )
	
	def resetPlayerRage( self, playerDBID ) :
		"""
		重置玩家怒气点
		"""
		if self.members.has_key( playerDBID ) :
			self.members[ playerDBID ].rage = 0
			self.members[ playerDBID ].playerMB.client.onAngerPointChanged( 0 )
	
	def onPlayerRequestUniqueSpell( self, playerDBID ) :
		"""
		玩家申请释放无双技
		"""
		member = self.members[ playerDBID ]
		if member.rage == self.playerMaxRage :
			member.playerMB.cell.spellTarget( csconst.YI_JIE_ZHAN_CHANG_UNIQUE_SKILL_ID, member.playerID )
	
	def enrage( self, isTrue ) :
		"""
		激发/取消 阵营激怒
		"""
		if isTrue and self.factions[ self.weakestFaction ].alliance :
			return
		for m in self.factions[ self.weakestFaction ].members.values() :
			m.playerMB.cell.yiJieFactionEnrage( isTrue )
		
		self.factions[ self.weakestFaction ].enrage = isTrue
		if isTrue :
			BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_YIJIE_ANGER_FACTION, self.weakestFaction )
			self.broadcastMessage( csstatus.YI_JIE_ZHAN_CHANG_ON_ENRAGE, FACTION_NAME[ self.weakestFaction ] )
		else :
			BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_YIJIE_ANGER_FACTION, 0 )
	
	def checkAllianceConditions( self ) :
		"""
		检查是否符合同盟条件
		"""
		if self.factions[ FACTION_TIAN ].alliance or self.factions[ FACTION_DI ].alliance or self.factions[ FACTION_REN ].alliance :
			return False
		kills = [ self.factions[ FACTION_TIAN ].kill, self.factions[ FACTION_DI ].kill, self.factions[ FACTION_REN ].kill ]
		maxKill = max( kills )
		sumKill = kills[0] + kills[1] + kills[2]
		if sumKill - maxKill >= maxKill : 
			return False
		return True
	
	def beginAlliance( self ) :
		"""
		开始同盟
		"""
		kills = [ self.factions[ FACTION_TIAN ].kill, self.factions[ FACTION_DI ].kill, self.factions[ FACTION_REN ].kill ]
		maxKill = max( kills )
		sumKill = kills[0] + kills[1] + kills[2]
		
		factions = [ FACTION_TIAN, FACTION_DI, FACTION_REN ]
		strongest = factions.pop( kills.index( maxKill ) )
		one = factions[0]
		theOther = factions[1]
		for m in self.factions[ one ].members.values() :
			m.playerMB.cell.yiJieSetAlliance( theOther )
		for m in self.factions[ theOther ].members.values() :
			m.playerMB.cell.yiJieSetAlliance( one )
		self.factions[ one ].alliance = theOther
		self.factions[ theOther ].alliance = one
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_YIJIE_ALLIANCE_FACTIONS, ( one, theOther ) )
		self.broadcastMessage( csstatus.YI_JIE_ZHAN_CHANG_ON_ALLIANCE, FACTION_NAME[ one ], FACTION_NAME[ theOther ], FACTION_NAME[ strongest ] )
	
	def endAlliance( self ) :
		"""
		结束同盟
		"""
		for faction in self.factions.itervalues() :
			if faction.alliance != 0 :
				one = faction.faction
				theOther = faction.alliance
				break
		for faction in self.factions.itervalues() :
			if faction.alliance != 0 :
				for m in faction.members.values() :
					m.playerMB.cell.yiJieSetAlliance( 0 )
				faction.alliance = 0
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_YIJIE_ALLIANCE_FACTIONS, () )
		self.broadcastMessage( csstatus.YI_JIE_ZHAN_CHANG_ON_ALLIANCE_END, FACTION_NAME[ one ], FACTION_NAME[ theOther ] )
	
	def onYiJieStoneCreate( self ) :
		"""
		洪荒灵石生成
		"""
		if not self.firstCreate :
			self.firstCreate = True
			self.broadcastMessage( csstatus.YI_JIE_ZHAN_CHANG_ON_STONE_FIRST_CREATE )
		else :
			self.broadcastMessage( csstatus.YI_JIE_ZHAN_CHANG_ON_STONE_CREATE_AGAIN )
	
	def finalBlowStone( self, playerDBID ) :
		"""
		对洪荒灵石造成最后一击
		"""
		if not self.members.has_key( playerDBID ) : return
		member = self.members[ playerDBID ]
		self.addFactionIntegral( member.faction, FINAL_BLOW_FACTION_INTEGRAL )
		for m in self.factions[ member.faction ].members.values() :
			m.playerMB.cell.systemCastSpell( csconst.YI_JIE_ZHAN_CHANG_STONE_SKILL_ID )
		self.broadcastMessage( csstatus.YI_JIE_ZHAN_CHANG_ON_STONE_DESTROYED, FACTION_NAME[ member.faction ] )
	
	def addFactionIntegral( self, faction, addValue ) :
		"""
		增加阵营积分
		"""
		self.factions[ faction ].integral += addValue
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_YIJIE_SCORE_TIAN, self.factions[ FACTION_TIAN ].integral )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_YIJIE_SCORE_DI, self.factions[ FACTION_DI ].integral )
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_YIJIE_SCORE_REN, self.factions[ FACTION_REN ].integral )
	
	def rankOnCloseActivity( self ) :
		"""
		活动结束时根据本场所获积分从大到小对玩家进行排名，返回排名数据。
		"""
		self.rankFaction()
		roles = self.members.values() + self.offlineMembers.values()
		roles.sort( None, lambda r : r.integral, True )
		for r in self.members.itervalues() :
			r.playerMB.cell.addYiJieZhanChangScore( r.integral )		# 增加玩家异界战场积分
		
		roleInfos = RoleRankInfoArray()
		for index in range( len( roles ) ) :
			role = roles[ index ]
			dict = {
				"rank"		: index + 1,
				"roleName"	: role.playerName,
				"faction"	: FACTION_NAME[ role.faction ],
				"killNum"	: role.kill,
				"keepNum"	: role.maxKeep,
				"score"		: role.integral,
				}
			roleInfo = RoleRankInfo()
			roleInfo.initData( dict )
			roleInfos.append( roleInfo )
		return roleInfos
	
	def rankFaction( self ) :
		"""
		对阵营进行排名，并根据排名奖励玩家对应积分
		"""
		factions = self.factions.values()
		factions.sort( BattlegroundMgr.cmpFaction, None, True )
		
		rewardIntegrals = [ FIRST_FACTION_REWARD_INTEGRAL, SECOND_FACTION_REWARD_INTEGRAL, THRID_FACTION_REWARD_INTEGRAL ]
		for index in range( len( factions ) ) :
			for member in factions[ index ].members.itervalues() :
				member.integral += rewardIntegrals[ index ]
			for offlineMember in self.offlineMembers.itervalues() :
				if offlineMember.faction == factions[ index ].faction :
					offlineMember.integral += rewardIntegrals[ index ]
		
		allMembers = self.members.values() + self.offlineMembers.values()
		for m in allMembers :
			m.integral += m.kill + m.maxKeep
	
	@staticmethod
	def cmpFaction( fx, fy ) :
		"""
		对阵营排名的比较阵营大小函数
		"""
		if fx.integral > fy.integral :
			return 1
		elif fx.integral < fy.integral :
			return -1
		else :
			if fx.kill > fy.kill :
				return 1
			elif fx.kill < fy.kill :
				return -1
			else :
				if fx.beKill < fy.beKill :
					return 1
				elif fx.beKill > fy.beKill :
					return -1
				else :
					if fx.lastKillTime < fy.lastKillTime :
						return 1
					elif fx.lastKillTime > fy.lastKillTime :
						return -1
					else :
						return 0
	
	def getDictFromObj( self, obj ) :
		dict = {
				"members"			: obj.members.values(),
				"offlineMembers"	: obj.offlineMembers.values(),
				"factions"			: obj.factions.values(),
				"firstBlood"		: obj.firstBlood,
				"firstCreate"		: obj.firstCreate,
				"canAlliance"		: obj.canAlliance,
				"weakestFaction"	: obj.weakestFaction,
				"enrageTimerID"		: obj.enrageTimerID,
				"playerMaxRage"		: obj.playerMaxRage,
				"spaceID"			: obj.spaceID,
			}
		return dict
	
	def initData( self, dict ) :
		"""
		用字典 dict 初始化战场成员数据
		"""
		self.firstBlood		= dict[ "firstBlood" ]
		self.firstCreate	= dict[ "firstCreate" ]
		self.canAlliance	= dict[ "canAlliance" ]
		self.weakestFaction	= dict[ "weakestFaction" ]
		self.enrageTimerID	= dict[ "enrageTimerID" ]
		self.playerMaxRage	= dict[ "playerMaxRage" ]
		self.spaceID		= dict[ "spaceID" ]
		
		for m in dict[ "members" ] :
			self.members[ m.databaseID ] = m
		
		for m in dict[ "offlineMembers" ] :
			self.offlineMembers[ m.databaseID ] = m
		
		for f in dict[ "factions" ] :
			self.factions[ f.faction ] = f
	
	def createObjFromDict( self, dict ) :
		obj = BattlegroundMgr()
		obj.initData( dict )
		return obj
	
	def isSameType( self, obj ) :
		return isinstance( obj, BattlegroundMgr )


class BattlegroundMember( object ) :
	"""
	战场成员数据
	"""
	def __init__( self ) :
		self.databaseID = 0
		self.playerID	= 0
		self.playerName	= ""
		self.playerMB	= None
		
		self.faction	= 0			# 所属阵营
		self.alliance	= 0			# 同盟阵营
		self.kill		= 0			# 个人杀敌数
		self.keep		= 0			# 连杀数
		self.maxKeep	= 0			# 最高连杀数
		self.beKill		= 0			# 死亡数
		self.integral	= 0			# 获得积分
		self.rage		= 0			# 怒气点
	
	def initMember( self, datas ) :
		"""
		用字典 datas 初始化战场成员数据
		"""
		self.faction	= datas[ "faction" ]
		self.databaseID = datas[ "databaseID" ]
		self.playerID	= datas[ "playerID" ]
		self.playerName	= datas[ "playerName" ]
		self.playerMB	= datas[ "playerMB" ]
	
	def initData( self, dict ) :
		"""
		用字典 dict 初始化战场成员数据
		"""
		self.databaseID = dict[ "databaseID" ]
		self.playerID	= dict[ "playerID" ]
		self.playerName	= dict[ "playerName" ]
		self.playerMB	= dict[ "playerMB" ]
		self.faction	= dict[ "faction" ]
		self.alliance	= dict[ "alliance" ]
		self.kill		= dict[ "kill" ]
		self.keep		= dict[ "keep" ]
		self.maxKeep	= dict[ "maxKeep" ]
		self.beKill		= dict[ "beKill" ]
		self.integral	= dict[ "integral" ]
		self.rage		= dict[ "rage" ]
	
	def getDictFromObj( self, obj ) :
		dict = {
				"databaseID"	: obj.databaseID,
				"playerID"		: obj.playerID,
				"playerName"	: obj.playerName,
				"playerMB"		: obj.playerMB,
				"faction"		: obj.faction,
				"alliance"		: obj.alliance,
				"kill"			: obj.kill,
				"keep"			: obj.keep,
				"maxKeep"		: obj.maxKeep,
				"beKill"		: obj.beKill,
				"integral"		: obj.integral,
				"rage"			: obj.rage,
			}
		return dict
	
	def createObjFromDict( self, dict ) :
		obj = BattlegroundMember()
		obj.initData( dict )
		return obj
	
	def isSameType( self, obj ) :
		return isinstance( obj, BattlegroundMember )
	
class BattlegroundFaction ( object ) :
	"""
	战场阵营数据
	"""
	def __init__( self ) :
		self.faction		= 0			# 自身阵营
		self.kill			= 0			# 阵营杀敌总数
		self.beKill			= 0			# 阵营死亡总数
		self.integral		= 0			# 阵营积分
		self.alliance		= 0			# 同盟阵营
		self.enrage			= False		# 是否激怒
		self.lastKillTime	= 0.0		# 阵营最后一次击杀时间
		self.members		= {}		# 阵营玩家集合
	
	def setFaction( self, faction ) :
		"""
		设置自身阵营
		"""
		self.faction	= faction
	
	def initData( self, dict ) :
		"""
		用字典 dict 初始化战场成员数据
		"""
		self.faction		= dict[ "faction" ]
		self.kill			= dict[ "kill" ]
		self.beKill			= dict[ "beKill" ]
		self.integral		= dict[ "integral" ]
		self.alliance		= dict[ "alliance" ]
		self.enrage			= dict[ "enrage" ]
		self.lastKillTime	= dict[ "lastKillTime" ]
		
		for m in dict[ "members" ] :
			self.members[ m.databaseID ] = m
	
	def getDictFromObj( self, obj ) :
		dict = {
				"faction"		: obj.faction,
				"kill"			: obj.kill,
				"beKill"		: obj.beKill,
				"integral"		: obj.integral,
				"alliance"		: obj.alliance,
				"enrage"		: obj.enrage,
				"members"		: obj.members.values(),
				"lastKillTime"	: obj.lastKillTime,
			}
		return dict
	
	def createObjFromDict( self, dict ) :
		obj = BattlegroundFaction()
		obj.initData( dict )
		return obj
	
	def isSameType( self, obj ) :
		return isinstance( obj, BattlegroundFaction )

class RoleRankInfo( object ) :
	"""
	玩家排行数据,( 活动结束后显示玩家排行时需要的数据 )
	"""
	def __init__( self ) :
		self.rank		= 0			# 玩家名次
		self.roleName	= ""		# 玩家名称
		self.faction	= ""		# 所属阵营名称
		self.killNum	= 0			# 个人杀敌数
		self.keepNum	= 0			# 最高连杀数
		self.score		= 0			# 本场所获积分
	
	def initData( self, dict ) :
		"""
		用字典 dict 初始化玩家排行数据
		"""
		self.rank		= dict[ "rank" ]
		self.roleName	= dict[ "roleName" ]
		self.faction	= dict[ "faction" ]
		self.killNum	= dict[ "killNum" ]
		self.keepNum	= dict[ "keepNum" ]
		self.score		= dict[ "score" ]
	
	def getDictFromObj( self, obj ) :
		dict = {
				"rank"		: obj.rank,
				"roleName"	: obj.roleName,
				"faction"	: obj.faction,
				"killNum"	: obj.killNum,
				"keepNum"	: obj.keepNum,
				"score"		: obj.score,
			}
		return dict
	
	def createObjFromDict( self, dict ) :
		obj = RoleRankInfo()
		obj.initData( dict )
		return obj
	
	def isSameType( self, obj ) :
		return isinstance( obj, RoleRankInfo )

class RoleRankInfoArray( object ) :
	"""
	玩家排行数据数组
	"""
	def __init__( self ) :
		self.roleInfos		= []			# 排行数据列表
	
	def __getitem__( self, key ) :
		return self.roleInfos[ key ]
	
	def __setitem( self, key, value ) :
		self.roleInfos[ key ] = value
	
	def __len__( self ) :
		return len( self.roleInfos )
	
	def __iter__( self ) :
		return iter( self.roleInfos )
	
	def append( self, roleInfo ) :
		self.roleInfos.append( roleInfo )
	
	def initData( self, dict ) :
		"""
		用字典 dict 初始化玩家排行数据
		"""
		self.roleInfos = dict[ "roleInfos" ]
	
	def getDictFromObj( self, obj ) :
		dict = { "roleInfos" : obj.roleInfos,}
		return dict
	
	def createObjFromDict( self, dict ) :
		obj = RoleRankInfoArray()
		obj.initData( dict )
		return obj
	
	def isSameType( self, obj ) :
		return isinstance( obj, RoleRankInfoArray )

yiJieMemberIns 		= BattlegroundMember()
yiJieFactionIns 	= BattlegroundFaction()
yiJieMgrIns 		= BattlegroundMgr()

yiJieRoleInfoIns		= RoleRankInfo()
yiJieRoleInfoArrayIns	= RoleRankInfoArray()