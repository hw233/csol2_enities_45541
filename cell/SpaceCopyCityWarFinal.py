# -*- coding: gb18030 -*-

import time
import Const
import csdefine
import csstatus
import cschannel_msgs
from bwdebug import *
from SpaceCopy import SpaceCopy
from TongCityWarInfos import TongCityWarInfo

CITY_WAR_BATTLE_BASE_SKILL	= { '20322222':{ 1: 1, 2: 2 },
								'20322223':{ 1: 1, 2: 2 },
								'20322224':{ 1: 1, 2: 2 },
								'20322225':{ 1: 1, 2: 2 }, }		# { 战斗据点className:{ 资源点个数：技能ID } }
WAIT_BATTLE_FIELD_RESET_TIME		= 60 * 3								# 战场重置时间
ROLE_DIED_ITERGRATION				= 10

class SpaceCopyCityWarFinal( SpaceCopy ):
	"""
	帮会夺城战决赛
	"""
	def __init__( self ):
		SpaceCopy.__init__( self )
		self.baseInfos = {}					# { baseType: [ mailBox:belong, ] }
		self.resetTimer = 0
		self.teleportBases = {}				# 有传送功能的据点 { mailBox:className, }
		self.initBattleField()
		self.msgs = []						# 要发送的消息 { "times": 次数， "msg": ( msgKey, *args ), "timerID": 1 }

	def initBattleField( self ):
		"""
		初始化战场数据
		"""
		self.tongInfos = self.params[ "tongInfos"]	# 所有参赛帮会 { "defend":[ ]}
		self.defend = self.params[ "defend" ]
		self.attack = self.params[ "attack" ]
		self.activatedBattleBase = []				# 被激活过的战斗据点（ 战斗据点被激活 = 被占领 ）
		self.flagGuardDamageRecord = {}				# 护旗将伤害统计
		self.diedFlagGuard = []						# 被杀死的护旗将
		for tongDBID in [ self.defend, self.attack ]:
			warInfo = TongCityWarInfo()
			warInfo.init( tongDBID )
			self.warInfos.infos[ tongDBID ] = warInfo

	def onEnterCommon( self, baseMailbox, params ):
		"""
		进入空间
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: Role %i enter space, params is %s " % ( baseMailbox.id, params ) )
		SpaceCopy.onEnterCommon( self, baseMailbox, params )
		
		tongDBID = params[ "tongDBID" ]
		roleDBID = params[ "roleDBID" ]
		roleName = params[ "roleName" ]

		warDict = {}
		# 为了复用接口tong_onEnterCityWarSpace，left表示攻城方，right表示守城方
		warDict[ "left" ] = self.defend
		warDict[ "leftTongName" ] = self.tongInfos[ "defend" ][ self.defend ][ "tongName"]
		warDict[ "right" ] = self.attack
		warDict[ "rightTongName" ] = self.tongInfos[ "attack" ][ self.attack ][ "tongName" ]
		
		dict = {}
		dict[ "left" ] = {}
		dict[ "right" ] = {}
		for key, item in self.tongInfos.iteritems():
			for tDBID in item.keys():
				if key == 'defend':
					dict[ "left" ][ tDBID ] = item[ tDBID ][ "tongName" ]
				else:
					dict[ "right" ][ tDBID ] = item[ tDBID][ "tongName" ]
		warDict[ "tongInfos" ] = dict
		baseMailbox.client.tong_onEnterCityWarSpace( int( BigWorld.globalData[ "TONG_CITY_WAR_FINAL_END_TIME" ] - time.time() ), warDict )
		
		self.warInfos.addMember( tongDBID, roleDBID, roleName, baseMailbox )
		self.addBelongBuff( tongDBID, baseMailbox )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		离开空间
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		tongDBID = params[ "tongDBID" ]
		roleDBID = params[ "databaseID" ]
		self.warInfos.leaveMember( tongDBID, roleDBID )
		BigWorld.globalData[ "TongManager" ].cityWarFinalLeave( self.params[ "uidKey"], tongDBID, roleDBID )

	def addBelongBuff( self, tongDBID, baseMailbox ):
		"""
		添加Buff，根据占领的战斗据点不同添加不同的Buff
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: Role %i, tong %i add buff on enter space." % ( baseMailbox.id, tongDBID ))
		belong = self.getTongBelong( tongDBID )
		if not belong:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: tong %i belong to None" % ( tongDBID ))
			return
		
		occupiedBattleBase = self.getOccupiedBattleBase( belong)
		if not occupiedBattleBase:
			return
		
		for className, amount in occupiedBattleBase.iteritems():
			skillID = CITY_WAR_BATTLE_BASE_SKILL[ className ][ amount ]
			baseMailbox.cell.spellTarget(  skillID, baseMailbox.id )

	def spellBuffAllPlayer( self, skillID, belong ):
		"""
		给所有人施放一个Buff
		"""
		for tongDBID, info in self.warInfos.infos.iteritems():
			tongBelong = self.getTongBelong( tongDBID )
			if tongBelong != belong:
				continue
			for roleDBID, member in info.members.iteritems():
				roleMB = member.mailBox
				role = BigWorld.entities.get( roleMB.id )
				if role:
					role.spellTarget( skillID, role.id )
				else:
					roleMB.cell.spellTarget( skillID, roleMB.id )

	def getTongBelong( self, tongDBID ):
		"""
		获取帮会ID的归属（攻城方还是守城方）
		"""
		for key, item in self.tongInfos.iteritems():
			if tongDBID in item.keys():
				if key == "defend":
					return csdefine.CITY_WAR_FINAL_FACTION_DEFEND
				if key == "attack":
					return csdefine.CITY_WAR_FINAL_FACTION_ATTACK
		return 0
	
	# ---------------------------- 据点处理 -----------------------------------------
	def onCityWarBaseCreated( self, baseMB, baseType, belong, className ):
		"""
		define method
		据点创建
		@param mailBox: 	据点mailBox
		@param baseType:	据点类型
		@param belong:		归属状态
		"""
		dict = {}
		dict[ baseMB ] = belong
		if baseType not in self.baseInfos:
			self.baseInfos[ baseType ] = []
		if baseType == csdefine.CITY_WAR_FINAL_BASE_HEROMONU:	# 英灵碑只有在有新的创建时才清空
			self.baseInfos[ baseType ] = []
		self.baseInfos[ baseType ].append( dict )
		if baseType in [ csdefine.CITY_WAR_FINAL_BASE_BATTLE, csdefine.CITY_WAR_FINAL_BASE_FLAG, csdefine.CITY_WAR_FINAL_BASE_HEROMONU ]:
			if baseMB not in self.teleportBases:
				self.teleportBases[ baseMB ] = ""
			self.teleportBases[ baseMB ] = className 

	def updateBaseBelong( self, baseType, baseID, belong ):
		"""
		更新据点归属
		"""
		for item in self.baseInfos[ baseType ]:
			for mb in item.keys():
				if baseID == mb.id:
					item[ mb ] = belong
		
		if baseType == csdefine.CITY_WAR_FINAL_BASE_BATTLE:		# 判断是否要激活插旗点
			if baseID not in self.activatedBattleBase:
				self.activatedBattleBase.append( baseID ) 
			if not self.queryTemp( "FLAG_ACTIVATED", False ):	# 插旗点未被激活
				if len( self.activatedBattleBase ) == len( self.baseInfos[ csdefine.CITY_WAR_FINAL_BASE_BATTLE ] ):
					self.activeFlag()
		
		if baseType in [ csdefine.CITY_WAR_FINAL_BASE_BATTLE, csdefine.CITY_WAR_FINAL_BASE_FLAG, csdefine.CITY_WAR_FINAL_BASE_HEROMONU ]:	# 更新同阵营据点信息
			self.updateBaseBelongsInfo( baseID, belong )

	def spawnCityWarBase( self, type, belong ):
		"""
		刷新指定类型的据点
		"""
		params = {}
		params[ "monsterType" ] = type
		params[ "belong"] = belong
		self.base.spawnMonster( params )

	def updateBaseBelongsInfo( self, baseID, newBelong ):
		"""
		更新同阵营据点信息( 传送用 )
		"""
		types = [ csdefine.CITY_WAR_FINAL_BASE_BATTLE, csdefine.CITY_WAR_FINAL_BASE_FLAG ]
		baseClassNames = []
		for type, item in self.baseInfos.iteritems():
			if type not in types:
				continue
			for info in item:
				for mb, belong in info.iteritems():
					if belong == newBelong:
						baseClassNames.append( self.teleportBases[ mb ] )
		
		for baseMB, className in self.teleportBases.iteritems():
			if className in baseClassNames:
				baseMB.cell.updateSameBelongs( baseClassNames )

	# ---------------------------- 资源据点 -----------------------------------------
	def onRoleOccupyResource( self, casterID, resourceMB ):
		"""
		define method
		玩家占领资源点( 拾取占领 )
		"""
		caster = BigWorld.entities.get( casterID )
		if not caster:
			return
		belong = self.getTongBelong( caster.tong_dbID )
		resourceMB.onOccupied( belong )

	def onResourceBaseOccupied( self, baseType, baseID, ownerID, belong ):
		"""
		define method
		资源据点被占领
		"""
		self.updateBaseBelong( baseType, baseID, belong )
		
		owner = BigWorld.entities.get( ownerID )
		if not owner:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: Can't get the owner %i " % ( ownerID ) )
			return

		if not owner.belong:
			return
		amount = owner.getResourceBaseBelong( owner.belong )
		if amount > 0:
			self.onBattleSubResourceChanged( owner.className, amount, owner.belong )
			return

		if owner.getResourceBaseBelong( belong ) == 2:
			self.onBattleSubResourceChanged(  owner.className, 2, belong )

	def onBattleSubResourceChanged( self,className, amount, belong ):
		"""
		资源点占领发生变化
		"""
		skillID = CITY_WAR_BATTLE_BASE_SKILL[ className ][ amount ]
		self.spellBuffAllPlayer( skillID, belong )

	# ---------------------------- 战斗据点 -----------------------------------------
	def onBattleBaseOccupied( self, baseType, baseID, className, belong, amount ):
		"""
		define method
		战斗据点被占领
		"""
		self.updateBaseBelong( baseType, baseID, belong )
		skillID = CITY_WAR_BATTLE_BASE_SKILL[ className ][ amount ]
		self.spellBuffAllPlayer( skillID, belong )

	def getOccupiedBattleBase( self, belong ):
		"""
		获取己方已占领的战斗据点{ 据点className: 数量 }
		"""
		occupiedBattleBase = {}
		if not csdefine.CITY_WAR_FINAL_BASE_BATTLE in self.baseInfos:
			return
		for item in self.baseInfos[ csdefine.CITY_WAR_FINAL_BASE_BATTLE ]:
			for mb, value in item.iteritems():
				if value == belong:
					battleBase = BigWorld.entities.get( mb.id )
					if not battleBase:
						continue
					if battleBase.className not in occupiedBattleBase.keys():
						occupiedBattleBase[ battleBase.className ] = 0
					occupiedBattleBase[ battleBase.className ] += 1
		
		return occupiedBattleBase
	
	# ----------------------------- 插旗点、护旗将 ----------------------------------
	def activeFlag( self ):
		"""
		激活插旗点
		"""
		self.getScript().statusMessageAllPlayer( self, csstatus.TONG_CITY_WAR_FLAG_ACTIVATED, "" )
		flagMB = self.baseInfos[ csdefine.CITY_WAR_FINAL_BASE_FLAG ][0].keys()[0]
		flagMB.cell.onActivated( )

	def onFlagActivated( self, baseType ):
		"""
		define method
		插旗点通知space自己已经被激活,刷新护旗将
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: Flag base has benn activated, begin to notify base spawn flagGuard!")
		self.setTemp( "FLAG_ACTIVATED", True )
		belong = csdefine.CITY_WAR_FINAL_FACTION_NONE
		self.spawnCityWarBase( csdefine.CITY_WAR_FINAL_BASE_FLAG_GUARD, belong )

	def onBaseFlagOccupied( self, baseType, baseID, belong ):
		"""
		define method
		插旗点被占领
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: Flag base has benn occupied by %i!" % belong )
		self.updateBaseBelong( baseType, baseID, belong )
		self.setTemp( "FLAG_OCCUPANT", belong )
		# 重新刷护旗将
		self.spawnCityWarBase( csdefine.CITY_WAR_FINAL_BASE_FLAG_GUARD, belong )
		if belong == csdefine.CITY_WAR_FINAL_FACTION_ATTACK:
			self.activeHeroMonu()

	def recordFlagGuardDamage( self, guardID, killerID, damage ):
		"""
		define method
		记录护旗将的伤害( 只需要记录某一方的总伤害，不需要记录单个人给护旗将造成的伤害 )
		"""
		killer = BigWorld.entities.get( killerID )
		if not killer:
			return
		belong = self.getTongBelong( killer.tong_dbID )
		
		if belong not in self.flagGuardDamageRecord:
			self.flagGuardDamageRecord[ belong ] = 0
		self.flagGuardDamageRecord[ belong ] += damage

	def onFlagGuardDied( self, guardID, integral, killerID ):
		"""
		define method
		护旗将死亡
		"""
		self.diedFlagGuard.append( guardID )
		
		guardNum = len( self.baseInfos[ csdefine.CITY_WAR_FINAL_BASE_FLAG_GUARD] )
		if len( self.diedFlagGuard ) == guardNum:
			self.onAllFlagGuardDied( killerID )
		
		killer = BigWorld.entities.get( killerID )
		if not killer:
			return

		self.addIntegral( killer.tong_dbID, integral )

	def onAllFlagGuardDied( self, killerID ):
		"""
		所有护旗将已经死亡
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: All flag guard has benn died!")
		self.diedFlagGuard = []
		self.baseInfos[ csdefine.CITY_WAR_FINAL_BASE_FLAG_GUARD ] = []
		flagMB, belong = self.baseInfos[ csdefine.CITY_WAR_FINAL_BASE_FLAG ][0].iteritems().next() 
		
		# 插旗点未被占领，根据对护旗将造成的伤害统计计算归属
		if not belong:
			DEBUG_MSG( "TONG_CITY_WAR_FINAL: Flag base is not occupied, cal top damage!")
			flagMB.cell.onOccupied( self.getTopDamageBelong() )
			return
		
		# 插旗点被占领，只需要杀死对方护旗将就可以抢夺插旗点
		killer = BigWorld.entities.get( killerID )
		if killer:
			newBelong = self.getTongBelong( killer.tong_dbID )
			DEBUG_MSG( "TONG_CITY_WAR_FINAL: Flag base has been occupied, old belong is %i, new is %i!" % ( belong, newBelong ) )
			flagMB.cell.onOccupied( newBelong )

	def getTopDamageBelong( self ):
		"""
		获取伤害最高的帮会
		"""
		maxDamge = max( self.flagGuardDamageRecord.values() )
		for belong,damage in self.flagGuardDamageRecord.iteritems():
			if damage == maxDamge:
				return belong

	# ----------------------------- 英灵碑 ------------------------------------------
	def activeHeroMonu( self ):
		"""
		激活英灵碑（英灵碑存储的是刷新的baseMB）
		"""
		self.getScript().statusMessageAllPlayer( self, csstatus.TONG_CITY_WAR_HERO_MONU_ACTIVATED, "" )
		heroMonuMB = self.baseInfos[ csdefine.CITY_WAR_FINAL_BASE_HEROMONU ][0].keys()[0]
		heroMonuMB.cell.onActivated( )

	def onHeroMonuDied( self, monuID, killerID ):
		"""
		define method
		英灵碑死亡
		"""
		killer = BigWorld.entities.get( killerID )
		if not killer:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: HeroMonu %i died, but can't get killer %i " % ( monuID, killerID) )
			return
		
		belong = self.getTongBelong( killer.tong_dbID )
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: HeroMonu has been killed by %i, belong is %i" % ( killerID, belong ) )
		# 复活英灵碑
		self.reviveHeroMonu( belong )
		self.onHeroMonuOccupied( csdefine.CITY_WAR_FINAL_BASE_HEROMONU, monuID, belong, killer.tongName )

	def reviveHeroMonu( self, belong ):
		"""
		复活英灵碑（指定归属）
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: Reveive HeroMonu , belong is %i" % belong )
		self.spawnCityWarBase( csdefine.CITY_WAR_FINAL_BASE_HEROMONU, belong )

	def onHeroMonuOccupied( self, baseType, monuID, belong, tongName ):
		"""
		英灵碑被占领
		"""
		self.updateBaseBelong( baseType, monuID, belong )
		
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: HeroMonu has benn occupied by tong %s, belong %i, resetTimer %i" % ( tongName, belong, self.resetTimer ) )
		if belong == csdefine.CITY_WAR_FINAL_FACTION_ATTACK and not self.resetTimer:
			self.onConditionChange( {} )
			self.getScript().statusMessageAllPlayer( self, csstatus.TONG_CITY_WAR_HERO_MONU_OCCUPIED, str( ( tongName, WAIT_BATTLE_FIELD_RESET_TIME / 60 ) ) )
			DEBUG_MSG( "TONG_CITY_WAR_FINAL:Start battle field reset timer !")
		else:
			self.baseOccupiedNotice( baseType, cschannel_msgs.CITY_WAR_FINAL_HERO_MONU, belong )

	def battleFieldReset( self ):
		"""
		英灵碑被攻城方占领，战场重置
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: Battle field reset!")
		self.getScript().statusMessageAllPlayer( self, csstatus.TONG_CITY_WAR_BATTLE_FIELD_RESET, "" )
		self.getHeroMonuOccupationReward() 			# 计算占领英灵碑获得的积分奖励
		BigWorld.globalData[ "TongManager" ].requestBattleFieldReset( self.params[ "uidKey" ] )	# 通知管理器战场重置
		self.resetCityWarFinalBase()				# 重置所有据点数据
		self.resetBattleField()						# 重置战场数据
		self.teleportPlayerToBelongBase()			# 将所有玩家传送到其所属出生点
		self.resetSpaceDatas()

	def getHeroMonuOccupationReward( self ):
		"""
		成功占领英灵碑后可以获得守城方当前积分的10%积分作为奖励
		"""
		defendIntegral = 0
		for tongDBID in self.tongInfos[ "defend" ]:
			defendIntegral += self.warInfos.getIntegral( tongDBID )
		if self.attack:
			self.addIntegral( self.attack, int( defendIntegral * 0.1 ) )

	def resetBattleField( self ):
		"""
		重置战场
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: begin to reset battle field datas!")
		oldDefend= self.defend
		self.defend = self.attack
		self.attack = oldDefend
		self.getScript().resetTongInfos( self )

	def resetCityWarFinalBase( self ):
		"""
		重置所有据点
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: begin to reset cityWarBase info!")
		for type, baseList in self.baseInfos.iteritems():
			if type in [ csdefine.CITY_WAR_FINAL_BASE_RESOURCE, csdefine.CITY_WAR_FINAL_LIGHT_WALL ]:	# 资源据点通过战斗据点去通知重置
				continue
			for item in baseList:
				for mb in item.keys():
					mb.cell.cityWarBaseReset()

	def teleportPlayerToBelongBase( self ):
		"""
		将所有玩家传送到其所属出生点
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: begin to teleport role to belong spawnPos!")
		self.getScript().teleportPlayerToBelongBase( self )

	def resetSpaceDatas( self ):
		"""
		重置空间数据( 护旗将做销毁处理 )
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL:  Reset space datas!")
		self.diedFlagGuard = []
		self.baseInfos[ csdefine.CITY_WAR_FINAL_BASE_FLAG_GUARD ] = []
		self.resetTimer = 0

	# ----------------------------- 积分处理 ----------------------------------------
	def addIntegral( self, tongDBID, integral, belongVal = 0 ):
		"""
		define method
		添加积分
		@param belongVal: 通过AI添加积分传入的是belong值，即1或2（攻方或守方）
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: %i add integral %i " % ( tongDBID, integral ) )
		if self.queryTemp( "BATTLE_FIELD_RESET", False ):		# 战场重置期间，不计算积分
			return
		belong = belongVal
		if tongDBID:
			belong = self.getTongBelong( tongDBID )
		
		if not belong:
			return
		
		if self.queryTemp( "FLAG_OCCUPANT", 0 ) == belong:		# 占领插旗点，积分翻倍
			integral = integral * 2
		
		if belong == csdefine.CITY_WAR_FINAL_FACTION_ATTACK:
			tongDBID = self.attack
		else:
			tongDBID = self.defend
		
		self.warInfos.addIntegral( tongDBID, integral )

	def onRoleBeKill( self, killerTongDBID, killerDBID, deaderTongDBID, deaderDBID ):
		"""
		define method
		有玩家被击杀后回调
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: ( Role %i, tong %i ) has been killed by ( Role %i, tong %i )" % ( deaderDBID, deaderTongDBID, killerDBID, killerTongDBID ))
		if killerDBID != 0:
			self.warInfos.addKill( killerTongDBID, killerDBID ) # 添加击杀次数
		
		self.warInfos.addDead( deaderTongDBID, deaderDBID ) # 添加死亡次数
		self.addIntegral( killerTongDBID, ROLE_DIED_ITERGRATION )  # 添加帮会积分

	def onRoleRelive( self, mailbox, tongDBID ):
		"""
		define method
		玩家战场复活
		"""
		self.getScript().onRoleRelive( self, mailbox, tongDBID )

	def onCityWarFinalEnd( self ):
		"""
		define method
		夺城战活动结束
		"""
		DEBUG_MSG( "TONG_CITY_WAR_FINAL: TongManager infos to close space!")
		self.setTemp( "BATTLE_FIELD_RESET", True )		# 停止计算积分
		self.calFinalIntegration()		# 计算最终积分
		self.getScript().closeSpace( self )

	def calFinalIntegration( self ):
		"""
		计算积分
		"""
		integrations = []
		for tongDBID in [ self.attack, self.defend ]:
			dict = { "tongDBID" : tongDBID, "integral": self.warInfos.getIntegral( tongDBID ), "date": int(time.time()) }
			integrations.append( dict )
		
		DEBUG_MSG( "TONG_CITY_WAR_FINAL:Activity end, cal integration %s! winner %i" % ( integrations, self.warInfos.winner ) )
		BigWorld.globalData[ "TongManager" ].onGetCityWarFinalRecords( self.params[ "uidKey" ], integrations, self.warInfos.winner )

	def destroyLightWall( self ):
		"""
		销毁光墙( 副本存储的是光墙的刷新点的base )
		"""
		for spawnList in  self.baseInfos[ csdefine.CITY_WAR_FINAL_LIGHT_WALL ]:
			for spMB, belong in spawnList.iteritems():
				spMB.cell.remoteCallScript( "destroySpawnMonster", [] )

	def spawnLightWall( self ):
		"""
		刷新光墙
		"""
		self.spawnCityWarBase( csdefine.CITY_WAR_FINAL_LIGHT_WALL, 0 )

	def baseOccupiedNotice( self, baseType, baseName, belong ):
		"""
		define method
		据点被占领通知
		"""
		if baseType == csdefine.CITY_WAR_FINAL_BASE_FLAG_GUARD:
			if belong == csdefine.CITY_WAR_FINAL_FACTION_ATTACK:
				msg = csstatus.TONG_CITY_WAR_FINAL_FLAG_GUARD_DIED1
			else:
				msg = csstatus.TONG_CITY_WAR_FINAL_FLAG_GUARD_DIED2
		else:
			if belong == csdefine.CITY_WAR_FINAL_FACTION_ATTACK:
				msg = csstatus.TONG_CITY_WAR_FINAL_BASE_OCCUPIED1
			else:
				msg = csstatus.TONG_CITY_WAR_FINAL_BASE_OCCUPIED2
		
		self.getScript().statusMessageAllPlayer( self, msg, str( ( baseName, ) ) )
