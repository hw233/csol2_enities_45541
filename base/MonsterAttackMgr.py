# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
import cschannel_msgs
from Content import Content
import Love3
import random
import csdefine
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()

from config.server import MonsterAttackConfig

MONSTER_GROUP = 4							#4波怪物

DROP_BOX_RATE = 0.7							#掉落宝箱概率


monsterAttackConfig = MonsterAttackConfig.Datas


class MonsterAttackContent( Content ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		self.val1 = 0
		self.val2 = 0
		self.spawns = []

	def init( self, obj, spawns ):
		"""
		"""
		setattr( obj, self.key, 0 )
		self.spawns = spawns
		self.val1 = 0
		self.val2 = 1

	def onContent( self, obj ):
		"""
		内容执行
		"""
		for i in self.spawns:
			i.cell.createEntityNormal()

class firstContent( MonsterAttackContent ):
	"""
	#刷第一波怪物
	"""
	def __init__( self ):
		"""
		"""
		MonsterAttackContent.__init__( self )
		self.key = "firstContent"




	def beginContent( self, obj ):
		"""
		内容开始
		"""
		smallBossName = obj.activityConfigs[obj.curArea]["group"][obj.curGroup]["smallBossName"]
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_ONE_NOTICE_01%smallBossName, [] )



	def doConditionChange(  self, obj, params ):
		"""
		对条件进行处理
		"""
		if "monsterType" in params:
			if params["monsterType"] == 1:
				smallBossName = obj.activityConfigs[obj.curArea]["group"][obj.curGroup]["smallBossName"]
				spaceName = obj.activityConfigs[obj.curArea]["name"]
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_ONE_NOTICE_02%( smallBossName, spaceName ), [] )
				for iSpawn in self.spawns:
					if random.random() < DROP_BOX_RATE:
						iSpawn.cell.spawnBox()
				return True
		return False


class SecondContent( MonsterAttackContent ):
	"""
	#刷第二波怪物
	"""
	def __init__( self ):
		"""
		"""
		MonsterAttackContent.__init__( self )
		self.key = "secondContent"


	def beginContent( self, obj ):
		"""
		内容开始
		"""
		smallBossName = obj.activityConfigs[obj.curArea]["group"][obj.curGroup]["smallBossName"]
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_TWO_NOTICE_01%smallBossName, [] )


	def doConditionChange(  self, obj, params ):
		"""
		对条件进行处理
		"""
		if "monsterType" in params:
			if params["monsterType"] == 1:
				smallBossName = obj.activityConfigs[obj.curArea]["group"][obj.curGroup]["smallBossName"]
				spaceName = obj.activityConfigs[obj.curArea]["name"]
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_TWO_NOTICE_02%( smallBossName, spaceName ), [] )
				for iSpawn in self.spawns:
					if random.random() < DROP_BOX_RATE:
						iSpawn.cell.spawnBox()
				obj.spawnBoxs[obj.curArea][obj.curGroup].cell.remoteCallScript( "spawnSpecialBox", [ csdefine.SPECIAL_BOX_01 ] )
				return True
		return False


class ThirdContent( MonsterAttackContent ):
	"""
	#刷第三波怪物
	"""
	def __init__( self ):
		"""
		"""
		MonsterAttackContent.__init__( self )
		self.key = "thirdContent"




	def beginContent( self, obj ):
		"""
		内容开始
		"""
		smallBossName = obj.activityConfigs[obj.curArea]["group"][obj.curGroup]["smallBossName"]
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_THREE_NOTICE_01%smallBossName, [] )

	def doConditionChange(  self, obj, params ):
		"""
		对条件进行处理
		"""
		if "monsterType" in params:
			if params["monsterType"] == 1:
				smallBossName = obj.activityConfigs[obj.curArea]["group"][obj.curGroup]["smallBossName"]
				spaceName = obj.activityConfigs[obj.curArea]["name"]
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_THREE_NOTICE_02%( smallBossName, spaceName ), [] )
				for iSpawn in self.spawns:
					if random.random() < DROP_BOX_RATE:
						iSpawn.cell.spawnBox()
				obj.spawnBoxs[obj.curArea][obj.curGroup].cell.remoteCallScript( "spawnSpecialBox", [ csdefine.SPECIAL_BOX_02 ] )
				return True
		return False


class NormalFourthContent( MonsterAttackContent ):
	"""
	#普通第四波怪物
	"""
	def __init__( self ):
		"""
		"""
		MonsterAttackContent.__init__( self )
		self.key = "NormalFourthContent"


	def beginContent( self, obj ):
		"""
		内容开始
		"""
		smallBossName = obj.activityConfigs[obj.curArea]["group"][obj.curGroup]["smallBossName"]
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_FOUR_NOTICE_01%smallBossName, [] )


	def doConditionChange(  self, obj, params ):
		"""
		对条件进行处理
		"""
		if "monsterType" in params:
			if params["monsterType"] == 2:
				smallBossName = obj.activityConfigs[obj.curArea]["group"][obj.curGroup]["smallBossName"]
				spaceName = obj.activityConfigs[obj.curArea]["name"]
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_FOUR_NOTICE_02%( smallBossName, spaceName ), [] )
				for iSpawn in self.spawns:
					if random.random() < DROP_BOX_RATE:
						iSpawn.cell.spawnBox()
				obj.spawnBoxs[obj.curArea][obj.curGroup].cell.remoteCallScript( "spawnSpecialBox", [ csdefine.SPECIAL_BOX_03 ] )
				obj.spawnBuffs[obj.curArea].cell.remoteCallScript( "addAreaPlayerBuff", [] )
				return True
		return False


class FengmingFourthContent( MonsterAttackContent ):
	"""
	#凤鸣第四波怪物
	"""
	def __init__( self ):
		"""
		"""
		MonsterAttackContent.__init__( self )
		self.key = "FengmingFourthContent"
		self.val2 = 2

	def init( self, obj, spawns ):
		"""
		"""
		setattr( obj, self.key, 0 )
		self.spawns = spawns
		self.val1 = 0
		self.val2 = 2

	def beginContent( self, obj ):
		"""
		内容开始
		"""
		smallBossName = obj.activityConfigs[obj.curArea]["group"][obj.curGroup]["smallBossName"]
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_FOUR_NOTICE_01%smallBossName, [] )


	def doConditionChange(  self, obj, params ):
		"""
		对条件进行处理
		"""
		if "monsterType" in params:
			if params["monsterType"] == 2:
				self.val1 += 1
				if self.val1 < self.val2:
					return False
				smallBossName = obj.activityConfigs[obj.curArea]["group"][obj.curGroup]["smallBossName"]
				spaceName = obj.activityConfigs[obj.curArea]["name"]
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_FOUR_NOTICE_02%( smallBossName, spaceName ), [] )
				for iSpawn in self.spawns:
					if random.random() < DROP_BOX_RATE:
						iSpawn.cell.spawnBox()
				obj.spawnBoxs[obj.curArea][obj.curGroup].cell.remoteCallScript( "spawnSpecialBox", [ csdefine.SPECIAL_BOX_03 ] )
				obj.spawnBuffs[obj.curArea].cell.remoteCallScript( "addAreaPlayerBuff", [] )
				return True
		return False


class MonsterAttackMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )

		# 把自己注册为globalData全局实体
		self.registerGlobally( "MonsterAttackMgr", self._onRegisterManager )
		self.activityConfigs 		= monsterAttackConfig
		self.curArea				= ""
		self.curGroup				= 1
		self.spawns 				= {}		#such as {	"feilaishi"	:{1:[],2:[],3:[],4:[],},"banquanxiang"	:{}, ... }
		self.spawnBuffs				= {}
		self.spawnBoxs				= {}
		#常规怪物攻城内容
		self.normalContents			= {
										1:firstContent(),
										2:SecondContent(),
										3:ThirdContent(),
										4:NormalFourthContent(),
									}
		#凤鸣怪物攻城内容
		self.fengmingContents		= {
										1:firstContent(),
										2:SecondContent(),
										3:ThirdContent(),
										4:FengmingFourthContent(),
									}
		self.contents = {}


	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register MonsterAttackMgr Fail!" )
			# again
			self.registerGlobally( "MonsterAttackMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["MonsterAttackMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("MonsterAttackMgr Create Complete!")

			self.registerCrond()


	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"MonsterAttackMgr_start_notice" : "onStartNotice",
					  	"MonsterAttackMgr_start" : "onStart",
					  	"MonsterAttackMgr_end" : "onEnd",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )
		


	def addSpawnPoint( self, spawnPointMB, spaceLabel, group, part ):
		"""
		define method
		"""
		if spaceLabel not in self.spawns:
			self.spawns[spaceLabel] = {}

		if group not in self.spawns[spaceLabel]:
			self.spawns[spaceLabel][group] = {}

		if part not in self.spawns[spaceLabel][group]:
			self.spawns[spaceLabel][group][part] = []

		self.spawns[spaceLabel][group][part].append( spawnPointMB )

	def addSpawnPointBuff( self, spawnPointMB, spaceLabel ):
		"""
		define method
		"""
		if spaceLabel not in self.spawnBuffs:
			self.spawnBuffs[spaceLabel] = spawnPointMB


	def addSpawnPointBox( self, spawnPointMB, spaceLabel, group ):
		"""
		define method
		"""
		if spaceLabel not in self.spawnBoxs:
			self.spawnBoxs[spaceLabel] = {}

		if group not in self.spawnBoxs[spaceLabel]:
			self.spawnBoxs[spaceLabel][group] = spawnPointMB


	def initContent( self ):
		"""
		"""
		global MonsterContentList
		areaConfig = self.activityConfigs[self.curArea]
		areaSpawns = self.spawns[self.curArea]

		for i in xrange( 1, MONSTER_GROUP + 1 ):
			part = random.choice( areaSpawns[i].keys() )
			self.contents[i].init( self, areaSpawns[i][part] )


	def run( self ):
		"""
		"""
		self.initContent()
		self.contents[self.curGroup].doContent( self )




	def onStart( self ):
		"""
		define method.
		活动开始
		"""
		if BigWorld.globalData.has_key( "AS_MonsterAttack" ):
			curTime = time.localtime()
			ERROR_MSG( "怪物攻城活动正在进行，%i点%i分试图再次开始怪物攻城。"%(curTime[3],curTime[4] ) )
			return
		BigWorld.globalData[ "AS_MonsterAttack" ] = True
		if self.curArea == "":
			self.onStartNotice()
		self.run()

	def onEnd( self ):
		"""
		define method.
		活动结束
		"""
		# 防止服务器在活动开始时间之后启动 则找不到该标记
		if not BigWorld.globalData.has_key( "AS_MonsterAttack" ):
			curTime = time.localtime()
			ERROR_MSG( "怪物攻城活动已经结束，%i点%i分试图再次结束怪物攻城。"%(curTime[3],curTime[4] ) )
			return
		if BigWorld.globalData.has_key( "AS_MonsterAttack" ):
			del BigWorld.globalData[ "AS_MonsterAttack" ]
		if self.curGroup <= MONSTER_GROUP:
			bossName = self.activityConfigs[self.curArea]["bossName"]
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_END_NOTICE_02%bossName, [] )
			for iContent in self.contents.values():
				for iSpawn in iContent.spawns:
					iSpawn.cell.remoteCallScript( "onAttackEnd", [] )
		self.contents = {}
		self.curArea = ""
		self.curGroup = 1

	def onStartNotice( self ):
		"""
		define method.
		活动开始通知
		"""
		if self.curArea == "":
			self.curArea = random.choice( self.activityConfigs.keys() )
			if self.curArea == "fengming":
				self.contents = self.fengmingContents
			else:
				self.contents = self.normalContents
		spaceName = self.activityConfigs[self.curArea]["name"]
		bossName = self.activityConfigs[self.curArea]["bossName"]
		if self.curArea == "fengming":
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_FENGMING_NOTICE_01, [] )
		else:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_NOTICE_01%( bossName, spaceName, spaceName ), [] )
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_NOTICE_02, [] )


	def onMonsterDied( self, params ):
		"""
		"""
		if BigWorld.globalData.has_key( "AS_MonsterAttack" ):
			if self.curGroup in self.contents:
				self.contents[self.curGroup].onConditionChange( self, params )


	def onContentFinish( self ):
		"""
		"""
		self.curGroup += 1
		if self.curGroup > MONSTER_GROUP:
			spaceName = self.activityConfigs[self.curArea]["name"]
			bossName = self.activityConfigs[self.curArea]["bossName"]
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MONSTER_ATTACK_CONTENT_END_NOTICE_01%( spaceName, bossName, spaceName ), [] )
		else:
			self.contents[self.curGroup].doContent( self )



def test():
	"""
	"""
	ma = BigWorld.entities[BigWorld.globalData["MonsterAttackMgr"].id]
	ma.onStartNotice()
	ma.onStart()
	return ma