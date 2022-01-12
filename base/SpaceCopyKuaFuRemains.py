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
		self.spawnPoints 		= {}			# ˢ�µ�			key: �ؿ�
		self.doorSpawnPoints	= {}			# ������			key: �ؿ�
		self.groupSpawnPoints	= {}			# �����ˢ�µ�		key: ���
		self.eventSpawnPoints	= {}			# �¼�����ˢ�µ�	key: �¼����
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

		һ��ˢ�µ㴴��ʱ��ע�ᵽ������baseEntity�ϡ�
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
		ˢ�¹���
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
		����С�֡����������Ϊ�����ж���
		"""
		for spawn in self.groupSpawnPoints[group]:
			spawn.cell.wakeUpMonster()

	def playerEntityAction( self, eventID, actionName ):
		"""
		����NPC������򳡾�����Ķ�����
		"""
		for spawn in self.eventSpawnPoints[eventID]:
			spawn.cell.playerAction( "" )

	def openDoor( self, step ):
		"""
		define method
		����
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
		����С�֡����������Ϊ�����ж���
		"""
		for spawn in self.eventSpawnPoints[csconst.KUA_FU_EVENT_SPAWN_TO_DEADBODY]:
			spawn.cell.remoteCallScript( "wakeUpDeadBody", () )

	def spawnChongzhi( self, eventID, params ):
		"""
		�г���
		"""
		params["level"] = self.copyLevel
		spawn = random.choice( self.eventSpawnPoints[eventID] )
		spawn.cell.createEntity( params )

	def spawnXuanfeng( self, eventID, params ):
		"""
		������
		"""
		spawn = random.choice( self.eventSpawnPoints[eventID] )
		spawn.cell.createEntity( params )

	def spawnTaozhi( self, eventID, params ):
		"""
		������
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
		�������е��¼�
		"""
		if eventID == csconst.KUA_FU_EVENT_JUBI_FLY_TO_SKY:
			print "�ݱȷ���"
			self.changeEntityAILevel( eventID, params )
		elif eventID == csconst.KUA_FU_EVENT_SPAWN_TO_DEADBODY:
			print "ˢ��ʬ��"
			self.spawnDeadBody( eventID, params )
		elif eventID == csconst.KUA_FU_EVENT_CENTER_FIRE_FLY_TO_SKY:
			print "�������"
			self.changeEntityAILevel( eventID, params )
		elif eventID == csconst.KUA_FU_EVENT_FEILIAN_KUI_DI:
			print "�������"
			self.wakeUpDeadBody()
			self.changeEntityAILevel( eventID, params )
		elif eventID == csconst.KUA_FU_EVENT_STONE_DESTROY:
			self.wakeUpGroupMonster( params["group"] )
			self.cell.forwardScriptCall( "fu_ben_kua_fu_shen_dian", "doStoneDestroy", ( self.id, params["group"] ) )
		elif eventID == csconst.KUA_FU_EVENT_ZHAO_CHONGZHI:
			print "�г���"
			self.spawnChongzhi( eventID, {} )
		elif eventID == csconst.KUA_FU_EVENT_XUANFENG:
			print "������"
			self.spawnXuanfeng( eventID, {} )
		elif eventID == csconst.KUA_FU_EVENT_TAOZHI:
			print "������"
			self.spawnTaozhi( eventID, {} )
		elif eventID == csconst.KUA_FU_EVENT_HOU_QING:
			print "�������"
			self.changeEntityAILevel( eventID, params )

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		��ҽ����˿ռ䣬��Ҫ���ݸ���boss�Ļ�ɱ����������
		��Ӧ����ʾ���������ѡ���Ǽ������������뿪������
		@param baseMailbox: ���mailbox
		@type baseMailbox: mailbox
		@param params: ���onEnterʱ��һЩ�������
		@type params: py_dict
		"""
		SpaceCopy.onEnter( self, baseMailbox, params )
		SpaceCopyRaidRecordInterface.onEnter( self, baseMailbox, params )

