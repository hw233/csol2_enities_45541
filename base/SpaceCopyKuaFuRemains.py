# -*- coding: gb18030 -*-

from SpaceCopy import SpaceCopy
from interface.SpaceCopyRaidRecordInterface import SpaceCopyRaidRecordInterface
import csconst
import random
import csdefine
import cschannel_msgs



class SpaceCopyKuaFuRemains( SpaceCopy, SpaceCopyRaidRecordInterface ):
	"""
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
		SpaceCopyRaidRecordInterface.__init__( self )
		self.spawnPoints 		= {}			# 刷新点			key: 关卡
		self.doorSpawnPoints	= {}			# 传送门			key: 关卡
		self.groupSpawnPoints	= {}			# 组关联刷新点		key: 组号
		self.eventSpawnPoints	= {}			# 事件关联刷新点	key: 事件编号
		self.addTimer( csconst.KUA_FU_ACTIVITY_TIME, 0.0, 100001 )
		self.copyLevel = 0


	def onTimer( self, id, userArg ):
		"""
		"""
		SpaceCopy.onTimer( self, id, userArg )

		k = 0
		if userArg == 100001:
				for i in self._players.values():
					i.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.KUA_FU_SHEN_DIAN_TIME_OVER, [] )
				self.addTimer( 20, 0.0, 100002 )
		if userArg == 100002:
			for i in self._players.values():
				i.cell.gotoForetime()

	def addSpawnPoint( self, params ):
		"""
		define method
		spawnPoint, step, entityType, group, event, isSpawnOnStep

		一个刷新点创建时，注册到副本的baseEntity上。
		"""
		spawnPoint 		= params["spawnPoint"]
		step 			= params["step"]
		entityType 		= params["entityType"]
		group 			= params["group"]
		event 			= params["event"]
		isSpawnOnStep 	= params["isSpawnOnStep"]

		if step not in self.spawnPoints:
			self.spawnPoints[step] = []
		self.spawnPoints[step].append( ( spawnPoint, isSpawnOnStep ) )

		if entityType == csconst.KUA_FU_ENTITY_TYPE_DOOR:
			if step not in self.doorSpawnPoints:
				self.doorSpawnPoints[step] = []
			self.doorSpawnPoints[step].append( spawnPoint )

		if group != 0:
			if group not in self.groupSpawnPoints:
				self.groupSpawnPoints[group] = []
			self.groupSpawnPoints[group].append( spawnPoint )

		if event != 0:
			if event not in self.eventSpawnPoints:
				self.eventSpawnPoints[event] = []
			self.eventSpawnPoints[event].append( spawnPoint )

	def spawnMonster( self, params ):
		"""
		define method
		刷新怪物
		"""
		step = params["step"]
		if step not in self.spawnPoints:
			return
		if self.copyLevel == 0:
			self.copyLevel = params["level"]

		for spawn, isSpawnOnStep in self.spawnPoints[step]:
			if isSpawnOnStep:
				spawn.cell.createEntity( params )

	def wakeUpGroupMonster( self, group ):
		"""
		唤醒小怪。（以组号做为唤醒判定）
		"""
		for spawn in self.groupSpawnPoints[group]:
			spawn.cell.wakeUpMonster()

	def playerEntityAction( self, eventID, actionName ):
		"""
		播放NPC，怪物或场景物件的动作。
		"""
		for spawn in self.eventSpawnPoints[eventID]:
			spawn.cell.playerAction( "" )

	def openDoor( self, step ):
		"""
		define method
		打开门
		"""
		for spawn in self.doorSpawnPoints[step]:
			spawn.cell.remoteCallScript( "openDoor", [] )

	def spawnDeadBody( self, eventID, params ):
		"""
		"""
		for spawn in self.eventSpawnPoints[eventID]:
			spawn.cell.createEntity( params )

	def wakeUpDeadBody( self ):
		"""
		唤醒小怪。（以组号做为唤醒判定）
		"""
		for spawn in self.eventSpawnPoints[csconst.KUA_FU_EVENT_SPAWN_TO_DEADBODY]:
			spawn.cell.remoteCallScript( "wakeUpDeadBody", () )

	def spawnChongzhi( self, eventID, params ):
		"""
		招虫子
		"""
		params["level"] = self.copyLevel
		spawn = random.choice( self.eventSpawnPoints[eventID] )
		spawn.cell.createEntity( params )

	def spawnXuanfeng( self, eventID, params ):
		"""
		招旋风
		"""
		spawn = random.choice( self.eventSpawnPoints[eventID] )
		spawn.cell.createEntity( params )

	def spawnTaozhi( self, eventID, params ):
		"""
		招桃子
		"""
		spawn = random.choice( self.eventSpawnPoints[eventID] )
		spawn.cell.createEntity( params )

	def changeEntityAILevel( self, eventID, params ):
		"""
		"""
		for spawn in self.eventSpawnPoints[eventID]:
			spawn.cell.changeEntityAILevel( params )


	def eventHandle( self, eventID, params ):
		"""
		define method
		处理副本中的事件
		"""
		if eventID == csconst.KUA_FU_EVENT_JUBI_FLY_TO_SKY:
			print "据比飞天"
			self.changeEntityAILevel( eventID, params )
		elif eventID == csconst.KUA_FU_EVENT_SPAWN_TO_DEADBODY:
			print "刷新尸体"
			self.spawnDeadBody( eventID, params )
		elif eventID == csconst.KUA_FU_EVENT_CENTER_FIRE_FLY_TO_SKY:
			print "火球冲天"
			self.changeEntityAILevel( eventID, params )
		elif eventID == csconst.KUA_FU_EVENT_FEILIAN_KUI_DI:
			print "飞廉跪地"
			self.wakeUpDeadBody()
			self.changeEntityAILevel( eventID, params )
		elif eventID == csconst.KUA_FU_EVENT_STONE_DESTROY:
			self.wakeUpGroupMonster( params["group"] )
			self.cell.forwardScriptCall( "fu_ben_kua_fu_shen_dian", "doStoneDestroy", ( self.id, params["group"] ) )
		elif eventID == csconst.KUA_FU_EVENT_ZHAO_CHONGZHI:
			print "招虫子"
			self.spawnChongzhi( eventID, {} )
		elif eventID == csconst.KUA_FU_EVENT_XUANFENG:
			print "招旋风"
			self.spawnXuanfeng( eventID, {} )
		elif eventID == csconst.KUA_FU_EVENT_TAOZHI:
			print "招桃子"
			self.spawnTaozhi( eventID, {} )
		elif eventID == csconst.KUA_FU_EVENT_HOU_QING:
			print "后卿回跑"
			self.changeEntityAILevel( eventID, params )

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		玩家进入了空间，需要根据副本boss的击杀情况给予玩家
		相应的提示，并让玩家选择是继续副本还是离开副本。
		@param baseMailbox: 玩家mailbox
		@type baseMailbox: mailbox
		@param params: 玩家onEnter时的一些额外参数
		@type params: py_dict
		"""
		SpaceCopy.onEnter( self, baseMailbox, params )
		SpaceCopyRaidRecordInterface.onEnter( self, baseMailbox, params )

