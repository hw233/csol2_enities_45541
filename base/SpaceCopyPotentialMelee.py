# -*- coding: gb18030 -*-
#

from SpaceCopy import SpaceCopy
from interface.SpaceCopyRaidRecordInterface import SpaceCopyRaidRecordInterface
import Love3
import BigWorld
from bwdebug import *

MONSTER_CALC_TYPE = [ "SpawnPointPotentialMelee", ]
FLAG_CLASS_NAME = [ "20254004" ]

TIMER_ARG_SPAWN_FLAG = 10000

class SpaceCopyPotentialMelee( SpaceCopy, SpaceCopyRaidRecordInterface ):
	"""
	"""
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopy.__init__( self )
		SpaceCopyRaidRecordInterface.__init__( self )
		BigWorld.globalData["PotentialMeleeMgr"].onRegisterSpace( self )
		self.spawnPoints = []
		self.spawnFlag = None #����ˢ�µ�
		self.spawnFlagParams = {}

	def closeSpace( self, deleteFromDB = True ):
		"""
		define method.
		destroy space��Ψһ��ڣ����е�spaceɾ����Ӧ���ߴ˽ӿڣ�
		space�������ڽ�����ɾ��space
		"""
		BigWorld.globalData["PotentialMeleeMgr"].onUnRegisterSpace( self.id )
		SpaceCopy.closeSpace( self, deleteFromDB )

	def onLoseCell( self ):
		"""
		CELL����
		"""
		BigWorld.globalData["PotentialMeleeMgr"].onUnRegisterSpace( self.id )
		SpaceCopy.onLoseCell( self )
	
	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		��������һ��entity��֪ͨ
		@param	entityType		: entity�Ľű����
		@type 	entityType		: String
		@param	entity			: baseEntityʵ��
		"""
		if baseEntity.getName() in FLAG_CLASS_NAME:
			self.spawnFlag = baseEntity
			
		if entityType in MONSTER_CALC_TYPE:
			self.spawnPoints.append( baseEntity )

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
	
	def spawnFlagEntity( self, params ):
		"""
		define method.
		ˢ��ʥ����
		"""
		if self.spawnFlag and self.spawnFlagParams:
			self.spawnFlag.cell.createEntity( params )
		else:
			self.spawnFlagParams = params
			self.addTimer( 2, 0, TIMER_ARG_SPAWN_FLAG )
		
	def spawnMonster( self, batch, params ):
		"""
		define method.
		ˢ������
		"""
		params[ "batch" ] = batch
		for sp in self.spawnPoints:
			sp.cell.createEntity( params )
	
	def onTimer( self, id, userArg ):
		if TIMER_ARG_SPAWN_FLAG == userArg:
			self.spawnFlagEntity( self.spawnFlagParams )
			return
		
		SpaceCopy.onTimer( self, id, userArg )