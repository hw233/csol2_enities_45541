# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyCityWar.py,v 1.1 2008-08-25 09:28:44 kebiao Exp $

"""
标准场景，也可以作为场景基类
"""

import BigWorld
import Language
from bwdebug import *
import time
import Const
import random
import csstatus
import csdefine
from SpaceCopy import SpaceCopy
import TongBuildingData
tongBuildingDatas = TongBuildingData.instance()
tongBuildingLevel = TongBuildingData.tbl_instance()

# 各建筑物的关键字映射
keyMapping = {
			csdefine.TONG_BUILDING_TYPE_YSDT 	: "ysdt",	# 议事大厅
			csdefine.TONG_BUILDING_TYPE_JK 		: "jk",		# 金库
			csdefine.TONG_BUILDING_TYPE_SSD 	: "ssd",	# 神兽殿
			csdefine.TONG_BUILDING_TYPE_CK 		: "ck",		# 仓库
			csdefine.TONG_BUILDING_TYPE_TJP 	: "tjp",	# 铁匠铺
			csdefine.TONG_BUILDING_TYPE_SD 		: "sd",		# 商店
			csdefine.TONG_BUILDING_TYPE_YJY 	: "yjy",	# 研究院
			}

# 帮会活动 魔物来袭 某怪物与活动级别的映射
campaignMonsterIDMapping = {
			50 	: "20754003",
			70 	: "20754004",
			90 	: "20754005",
			110 : "20754006",
			130 : "20754007",
			150 : "20754008",
		}

# 魔物来袭小怪
campaignMonsterList = ["20724006", "20744007"]

class SpaceCopyTongTerritory( SpaceCopy ):
	"""
	帮会领地
	@ivar domainMB:			一个声明的属性，记录了它的领域空间mailbox，用于某些需要通知其领域空间的操作，此接口如果为None则表示当前不可使用
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )

		self.buildings = {}							# 帮会建筑物
		self.npcs = {}								# 副本里的NPC
		self.shenshouMB = None  					# 神兽的base mailbox
		self.campaignMonsterRaidNPCMB = None		# 活动魔物来袭 怪物base mailbox
		self.campaignMonsterMBList = []				# 活动魔物来袭 小怪base mailbox列表
		self.campaignMonsterNum = 0					# 活动魔物来袭，杀死怪物数量（全部怪物杀死后，活动结束）
		self._createNewShenShouTimerID = 0			# 选择了新神兽后创建新神兽的一个时间
		self._npcLocked = False						# 是否锁住了NPC
		self._isFixNagual = True					# 神兽是否处于固定模式(即呆在一个固定位置供奉)
		self._isCampaignMonsterRaidOver = True		# 帮会 魔物来袭活动时间是否结束
		self.feteThings = []						# 帮会祭祀活动中的场景物件列表
		self._shenshouReviveTimeID = 0				# 神兽复活timerID
		self._protectTongNPCList = []				# 保护帮派活动的NPC
		self.isUpdateBuildingModel = 0				# 是否更新帮会建筑模型

		# 当cell成功创建之后，自动调用的例程 相关API:addRoutineOnGetCell() by mushuang
		self._routinesOnGetCell = []				# [ ( routine1, ( arg1, arg2, ... ) ), ( routine2, ( arg1, arg2, ... ) ), ... ]

		# 将自己注册给帮会
		BigWorld.globalData[ "TongManager" ].onRegisterTerritory( self.params["tongDBID"], self )

	def getbuildingLevelByType( self, buildingType ):
		"""
		产生一个实时影射
		"""
		return {
				csdefine.TONG_BUILDING_TYPE_YSDT 	: self.params[ "ysdt_level" ],	# 议事大厅
				csdefine.TONG_BUILDING_TYPE_JK 		: self.params[ "jk_level" ],	# 金库
				csdefine.TONG_BUILDING_TYPE_SSD 	: self.params[ "ssd_level" ],	# 神兽殿
				csdefine.TONG_BUILDING_TYPE_CK 		: self.params[ "ck_level" ],	# 仓库
				csdefine.TONG_BUILDING_TYPE_TJP 	: self.params[ "tjp_level" ],	# 铁匠铺
				csdefine.TONG_BUILDING_TYPE_SD 		: self.params[ "sd_level" ],	# 商店
				csdefine.TONG_BUILDING_TYPE_YJY 	: self.params[ "yjy_level" ],	# 研究院
			}[ buildingType ]

	def activeNagual( self, enemyTongDBID ):
		"""
		激活神兽
		"""
		self._isFixNagual = False
		if self.shenshouMB:
			self.shenshouMB.cell.activeNagual( enemyTongDBID )

	def disableNagual( self ):
		"""
		神兽恢复供奉特性
		"""
		self._isFixNagual = True
		if self.shenshouMB:
			self.shenshouMB.cell.disableNagual()

	def onRobWarStart( self, enemyTongDBID ):
		"""
		define method.
		帮会掠夺战开始
		"""
		self.activeNagual( enemyTongDBID )

		if hasattr( self, "cell" ):
			DEBUG_MSG( "Notify cell rob war starting directly!" )
			self.cell.onStartRobWar( enemyTongDBID )
		else:
			def __notifyCellOnStartRobWar( enemyTongDBID ):
				"""
				通知cell帮会掠夺开始
				"""
				DEBUG_MSG( "Notify cell rob war starting after get cell!" )
				self.cell.onStartRobWar( enemyTongDBID )

			self.addRoutineOnGetCell( __notifyCellOnStartRobWar, [ enemyTongDBID ] )

	def onRobWarStop( self ):
		"""
		define method.
		帮会掠夺战结束
		"""
		self.disableNagual()

		if hasattr( self, "cell" ):
			self.cell.onEndRobWar()

	def onTongDismiss( self ):
		"""
		define method.
		帮会被解散了，准备销毁它的相关数据
		"""
		self.banishPlayer()
		self.startCloseCountDownTimer( 30 )

	def getTongTerritoryEntity( self, key ):
		"""
		获取帮会建筑的entity
		"""
		"""
		以后有需要应该实现
		if key == xxx:
		   return shenshou
		elif key == xxxType:
		   return self.npcs[ key ]
		eilf key == xxxType:
		   return xxxbuild
		"""
		try:
			e = self.npcs[ key ]
		except KeyError:
			ERROR_MSG( " key error! %s" % self.npcs.keys() )
			return None
		return e

	def addRoutineOnGetCell( self, routine, arg ):
		"""
		@addRoutineOnGetCell: 增加一个在OnGetCell中调用的例程
		@routine: 要调用的例程，此对象必须是可调用的
		@arg: list, 指明要传入的参数
		"""
		#self._routinesOnGetCell [ ( routine1, ( arg1, arg2, ... ) ), ( routine2, ( arg1, arg2, ... ) ), ... ]

		assert hasattr( routine, "__call__" ), "routine must be callable!"

		argInTuple = tuple( arg )

		self._routinesOnGetCell.append( ( routine, argInTuple ) )

	def __callRoutinesOnGetCell( self ):
		"""
		在成功获取Cell之后调用已经加入队列的例程
		"""
		for element in self._routinesOnGetCell:
			routine = element[ 0 ]
			argInTuple = element[ 1 ]
			try:
				routine( *argInTuple )
			except:
				ERROR_MSG( "Routine: %s failed!"%routine )

		self._routinesOnGetCell = []

	def onGetCell(self):
		"""
		cell实体创建完成通知，回调callbackMailbox.onSpaceComplete，通知创建完成。
		"""
		SpaceCopy.onGetCell( self )
		self.createShenshouOnGetCell()
		self.createBuildingOnGetCell()

		self.__callRoutinesOnGetCell()

	def createBuildingOnGetCell( self ):
		"""
		cell实体创建完成通知，创建所有的建筑物
		"""
		# 创建所有的建筑
		buildingConfig = self.getScript().tempDatas[ "buildingConfig" ]
		for key, cnf in buildingConfig.iteritems():
			level = self.params[ key + "_level" ]
			type = tongBuildingDatas[ cnf[1] ][ level ][ "type" ]
			if type == csdefine.TONG_BUILDING_TYPE_SSD:
				continue

			self.buildings[ type ] = \
			self.createNPCObject( self.cell, cnf[1], cnf[0][0], cnf[0][1], {"modelNumber" : tongBuildingDatas[ cnf[1] ][ level ][ 'modelNumber' ], \
									 "tempMapping" : { "buildingType" : type } } )

		# 创建所有的NPC
		npcConfig = self.getScript().tempDatas[ "npcConfig" ]
		for key, cnf in npcConfig.iteritems():	# 创建NPC
			level = self.params[ key + "_level" ]
			if level <= 0:
				continue
			param = { "ownTongDBID" : self.params["tongDBID"], "locked" : self._npcLocked, "spawnPos" : cnf[0][0] }
			if key == "ysdt" or key == "jk":
				param[ "locked" ] = False
			self.npcs[ key ] = self.createNPCObject( self.cell, cnf[1], cnf[0][0], cnf[0][1], param )

	def onBuildingLevelChanged( self, tongLevel ):
		"""
		define method.
		改变一个建筑物的级别
		"""
		INFO_MSG( "TONG: Update tong building , tong level is %i" % ( tongLevel ) )
		self.isUpdateBuildingModel = True
		for buildingType in self.buildings:
			buildingLevel = tongBuildingLevel.getBuildingLevel( tongLevel, buildingType )
			data = tongBuildingDatas[ buildingType ][ buildingLevel ]
			self.buildings[ buildingType ].setModelNumber( data[ 'modelNumber' ] )
			self.onBuildingTypeChanged( buildingType, buildingLevel )

	def onBuildingTypeChanged( self, buildingType, currentLevel ):
		"""
		领地中有建筑被改变了 升级或者降级
		"""
		key = keyMapping[ buildingType ]
		self.params[ key + "_level" ] = currentLevel
		DEBUG_MSG( "TONG:building %s changed, currentLevel:%d" % ( key, currentLevel ) )

		if buildingType == csdefine.TONG_BUILDING_TYPE_SSD: # 神兽殿
			self.updateShenShouLevel( currentLevel )

	def createShenshouOnGetCell( self ):
		"""
		cell实体创建完成通知 创建神兽
		"""
		# 创建神兽
		if self.params[ "shenshouType" ] > 0:
			if self.params[ "shenshouReviveTime" ] <= 0:
				self.onCreateShenShou()
			else:
				self.reviveNagual( self.params[ "shenshouReviveTime" ] - time.time() )

	def reviveNagual( self, shenshouReviveTime ):
		"""
		define method.
		神兽被杀了， 开启复活程序
		"""
		DEBUG_MSG( "reviveNagual->shenshouReviveTime %i" % shenshouReviveTime )
		if self.shenshouMB:
			WARNING_MSG( "reviveNagual: shenshou is live." )
			return

		if shenshouReviveTime <= 0:
			shenshouReviveTime = 1

		if self._shenshouReviveTimeID > 0:
			self.delTimer( self._shenshouReviveTimeID )
		self._shenshouReviveTimeID = self.addTimer( shenshouReviveTime, 0, 0 )

	def updateShenShouLevel( self, tongLevel ):
		"""
		更新帮会神兽级别
		"""
		if self.shenshouMB:
			self.shenshouMB.updateLevel( tongLevel )
			if tongLevel <= 0:
				self.shenshouMB = None	# 级别小于0 则删除

	def onShenShouDestroy( self ):
		"""
		define method.
		神兽销毁了
		"""
		self.shenshouMB = None

		# 如果神兽是在掠夺战期间被销毁则通知掠夺战管理器，可能一场战争结束了。
		if BigWorld.globalData.has_key( "TONG_ROB_WAR_START" ):
			BigWorld.globalData[ "TongManager" ].onRobWarOver( self.params["tongDBID"] )

	def lockTerritoryNPC( self ):
		"""
		define method.
		锁住副本里的相关NPC  不再和任何人对话
		"""
		self._npcLocked = True
		for key, npc in self.npcs.iteritems():
			if key != "ysdt" and key != "jk":
				npc.cell.lock()

	def unLockTerritoryNPC( self ):
		"""
		define method.
		打锁住副本里的相关NPC  正常和相关人对话
		"""
		self._npcLocked = False
		for key, npc in self.npcs.iteritems():
			if key != "ysdt" and key != "jk":
				npc.cell.unlock()

	def onTongSelectNewShenShou( self, shenShouType, isReviveing ):
		"""
		define method.
		帮会选择了一个新的神兽
		@param isReviveing	: 神兽是否在复活期
		"""
		if self.shenshouMB:
			self.shenshouMB.updateLevel( 0 )	# 神兽遇到0级则自动销毁

		# 神兽不在复活期间才可以创建
		if not isReviveing:
			if self._createNewShenShouTimerID <= 0:
				self._createNewShenShouTimerID = self.addTimer( 0.5, 1, 0 )

		self.params[ "shenshouType" ] = shenShouType

	def onCreateShenShou( self ):
		"""
		选择创建神兽时间回调
		"""
		# 创建神兽
		shenshou_config = self.getScript().tempDatas[ "shenshou_config" ]
		state = { "spawnPos" : shenshou_config[0][0], \
				  "randomWalkRange" : 6.0, \
				  "level" : self.params[ "ssd_level" ], \
				  "ownTongDBID" : self.params["tongDBID"], \
				  "fixPlace" : shenshou_config[0][0], \
				  "fixDirection" : shenshou_config[0][1], \
				  "tempMapping" : { "spaceClassName" : self.getScript().className, "fixModel" : self._isFixNagual, \
				  "shenshouType" : self.params[ "shenshouType" ] } }

		self.shenshouMB = self.createNPCObject( self.cell, shenshou_config[1][ self.params[ "shenshouType" ] ], \
							shenshou_config[0][0], shenshou_config[0][1], state )

		if BigWorld.globalData.has_key( "TONG_ROB_WAR_START" ):	 # 解决神兽没有创建完成就通知掠夺战开始的问题
			BigWorld.globalData[ "TongManager" ].onRegisterTerritory( self.params["tongDBID"], self )

	def onTimer( self, id, userArg ):
		"""
		"""
		SpaceCopy.onTimer( self, id, userArg )
		if id == self._createNewShenShouTimerID:
			self.delTimer( self._createNewShenShouTimerID )
			self._createNewShenShouTimerID = 0
			self.onCreateShenShou()
		elif id == self._shenshouReviveTimeID:
			self.delTimer( self._shenshouReviveTimeID )
			self._shenshouReviveTimeID = 0
			self.onCreateShenShou()

	def onInitTongItems( self, sdLevel, reset ):
		"""
		初始化商店物品
		"""
		npc = self.getTongTerritoryEntity( "sd" )
		if npc:
			npc.cell.initTongItems( sdLevel, reset )

	def onRegisterTongItem( self, itemID, amount ):
		"""
		define method.
		当领地被创建后， 帮会会把自身研发的物品注册到领地的NPC
		"""
		npc = self.getTongTerritoryEntity( "sd" )
		if npc:
			npc.cell.onRegisterTongItem( itemID, amount )

	#---------------------------------------------------帮会魔物来袭活动------------------------------------------------

	def startCampaign_monsterRaid( self, monsterLevel ):
		"""
		define method.
		开始 魔物来袭活动
		"""
		if not self._isCampaignMonsterRaidOver:
			return

		self._isCampaignMonsterRaidOver = False

		shenshouID = 0
		if self.shenshouMB:
			shenshouID = self.shenshouMB.id

		# 创建怪物
		config = self.getScript().tempDatas[ "campaign_monsterRaid_pos" ]
		state = { "spawnPos" : config[0], \
				  "randomWalkRange" : 6.0, \
				  "level" : monsterLevel, \
				  "tempMapping" : { "shenshouID" : shenshouID } \
				}

		self.campaignMonsterRaidNPCMB = self.createNPCObject( self.cell, campaignMonsterIDMapping[ monsterLevel ], config[0], config[1], state )

		# 刷出小怪
		configs = self.getScript().tempDatas[ "campaign_monsterRaid_poss" ]
		for e in configs:
			state = { "spawnPos" : e[0], \
		  			  "randomWalkRange" : 6.0, \
		  			  "level" : monsterLevel, \
		  			  "tempMapping" : { "shenshouID" : shenshouID } \
					}
			self.campaignMonsterMBList.append( self.createNPCObject( self.cell, random.choice( campaignMonsterList ), e[0], e[1], state ) )
		self.activeNagual( -1 )

	def overCampaign_monsterRaid( self ):
		"""
		define method.
		结束 魔物来袭活动
		"""
		if self._isCampaignMonsterRaidOver:
			return

		self._isCampaignMonsterRaidOver = True
		if self.campaignMonsterRaidNPCMB and hasattr( self.campaignMonsterRaidNPCMB, "cell" ) and self.campaignMonsterRaidNPCMB.cell:
			self.campaignMonsterRaidNPCMB.cell.remoteScriptCall( "campaignOver", () )

		# 小怪消失
		for e in self.campaignMonsterMBList:
			if e and hasattr( e, "cell" ) and e.cell:
				e.cell.remoteScriptCall( "campaignOver", () )

		# 增加一些数据清理工作 by mushuang
		self.campaignMonsterRaidNPCMB = None
		self.campaignMonsterMBList = []
		self.campaignMonsterNum = 0

		self.disableNagual()

	def onCappaign_monsterRaidComplete( self, level, bossName ):
		"""
		define method.
		帮会完成了 魔物来袭活动
		"""
		self.campaignMonsterNum += 1
		if self.campaignMonsterNum != len( self.getScript().tempDatas[ "campaign_monsterRaid_poss" ] ) + 1:	# 魔物来袭，必须杀死boss和所有小怪，活动结束
			return

		if self._isCampaignMonsterRaidOver:
			return

		BigWorld.globalData[ "TongManager" ].onCappaign_monsterRaidComplete( self.params["tongDBID"] )
		self._isCampaignMonsterRaidOver = True
		self.campaignMonsterRaidNPCMB = None
		self.campaignMonsterMBList = []
		self.campaignMonsterNum = 0
		self.disableNagual()
		pos = list( self.getScript().tempDatas[ "campaign_monsterRaid_box_pos" ] )
		monsterID = campaignMonsterIDMapping[ level ]
		boxIDs = list( self.getScript().tempDatas[ "campaign_monster_box_drops" ][ monsterID ] )

		if len( pos ) < len( boxIDs ):
			ERROR_MSG( "box the pos config amount < box is drop amount" )
			return

		for x in xrange( len( boxIDs ) ):
			d = pos.pop( random.randint( 0, len( pos ) - 1 ) )
			params = {
				"tempMapping" : { "bossName" : bossName, "tongDBID" : self.params["tongDBID"] },
				"lifetime" : csdefine.PRIZE_DURATION,
			}
			self.cell.createNPCObject( boxIDs.pop( random.randint( 0, len( boxIDs ) - 1 ) ), d[0], d[1], params )


	#---------------------------------------------------------帮会祭祀活动-----------------------------------------

	def onStartTongFete( self ):
		"""
		define method.
		开始帮会祭祀活动了，  领地可以为该活动做一些相应的准备
		如：投放好场景物件。。
		"""
		self.cell.onStartTongFete()
		self.castFeteThing()
		self.getTongTerritoryEntity( "ysdt" ).cell.openFete()

	def onOverTongFete( self ):
		"""
		define method.
		结束帮会祭祀活动
		"""
		self.cell.onOverTongFete()
		self.getTongTerritoryEntity( "ysdt" ).cell.closeFete()
		self.destroyFeteThing()

	def onTongFeteComplete( self ):
		"""
		define method.
		帮会祭祀活动成功完成了
		"""
		# 刷奖励NPC
		feteRewardNPCData = self.getScript().tempDatas[ "feteDatas" ][ "feteRewardNPC" ]
		self.createNPCObject( self.cell, feteRewardNPCData[0], feteRewardNPCData[1][0], feteRewardNPCData[1][1], { "ownTongDBID":self.params["tongDBID"], "tempMapping" : { "tongDBID" : self.params["tongDBID"] } } )
		self.onOverTongFete()

	def castFeteThing( self ):
		"""
		投放祭祀活动相关场景物件
		"""
		# 刷香炉
		feteThingDatas = self.getScript().tempDatas[ "feteDatas" ][ "feteThingDatas" ]
		for thingID, posData in feteThingDatas.iteritems():
			self.feteThings.append( self.createNPCObject( self.cell, thingID, posData[0], posData[1], { "tempMapping" : { "tongDBID" : self.params["tongDBID"] } } ) )

	def destroyFeteThing( self ):
		"""
		销毁所有祭祀活动场景物件
		"""
		for e in self.feteThings:
			e.destroyCellEntity()
		self.feteThings = []

	#--------------------------------------保护帮会活动-----------------------------------------------------------------------
	def onProtectTongStart( self, protectType ):
		"""
		define method.
		开始保护帮会活动了，  领地可以为该活动做一些相应的准备
		如：投放好所有怪物。。
		"""
		objScript = self.getScript()
		if protectType == csdefine.PROTECT_TONG_NORMAL:
			npcID = objScript.tempDatas[ "protectTong" ][ "npcID" ]
			posdatas = objScript.tempDatas[ "protectTong" ][ "pos" ]
		elif protectType == csdefine.PROTECT_TONG_MID_AUTUMN:
			npcID = objScript.tempDatas[ "protectTong" ][ "protectTongMidAutumnNPCID" ]
			posdatas = objScript.tempDatas[ "protectTong" ][ "midAutumnPos" ]
		else:
			ERROR_MSG( "未知保护帮派类型:( %i ),使用默认类型( %i )配置。" % ( protectType, csdefine.PROTECT_TONG_NORMAL ) )
			npcID = objScript.tempDatas[ "protectTong" ][ "npcID" ]
			posdatas = objScript.tempDatas[ "protectTong" ][ "pos" ]

		for posData in posdatas:
			state = { "spawnPos" : posData[0], \
						#"uname" : "守方统帅", \
						"randomWalkRange" : 6.0, \
						"tempMapping" : { "spaceClassName" : objScript.className }, \
						"level" : 0 \
					}
			self._protectTongNPCList.append( self.createNPCObject( self.cell, npcID, posData[0], posData[1], state ) )
		BigWorld.globalData["ProtectTong"].receiveMonsterCount( len( self._protectTongNPCList ) )

	def onProtectTongEnd( self ):
		"""
		define method.
		结束保护帮会活动
		"""
		for npc in self._protectTongNPCList:
			try:
				npc.cell.onProtectTongOver()
			except:
				pass

		self._protectTongNPCList = []

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		玩家进入了空间
		@param baseMailbox: 玩家mailbox
		@type baseMailbox: mailbox
		@param params: 玩家onEnter时的一些额外参数
		@type params: py_dict
		"""
		SpaceCopy.onEnter( self, baseMailbox, params )
		if not self.isUpdateBuildingModel and params[ "tongDBID" ] == self.params["tongDBID"]:
			self.onBuildingLevelChanged( params[ "tongLevel" ] )	# 加这一行是避免领地没创建时帮会升级，帮会内的建筑模型没同步更新
		for npc in self.npcs.itervalues() :							# 给进入领地的玩家发送npc数据，以便在大地图上能看到
			baseMailbox.client.tong_receiveTerritoryNPCData( self.params["tongDBID"], npc.className )
	
	# ---------------------------------------------帮会特殊商城--------------------------------------------
	def onInitTongSpecialItems( self, tongLevel, reset ):
		"""
		初始化商店物品
		"""
		npc = self.getTongTerritoryEntity( "yjy" )
		if npc:
			npc.cell.initTongSpecialItems( tongLevel, reset )
	
	def onAddSpecialItemReward( self, itemID, amount ):
		"""
		帮会特殊商品注册
		"""
		npc = self.getTongTerritoryEntity( "yjy" )
		if npc:
			npc.cell.onRegisterTongSpecialItem( itemID, amount )
	
	def onSellSpecialItems( self, playerID, itemID, amount ):
		"""
		购买帮会特殊商品回调
		"""
		npc = self.getTongTerritoryEntity( "yjy" )
		if npc:
			npc.cell.onSellSpecialItems( playerID, itemID, amount )
#
# $Log: not supported by cvs2svn $
#
#
