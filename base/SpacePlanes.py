# -*- coding: gb18030 -*-

import time
import BigWorld

import Love3
import Language
from bwdebug import *
from MsgLogger import g_logger

from SpaceNormal import SpaceNormal
from interface.ImpPlanesSpace import ImpPlanesSpace

import csstatus
import csdefine
import Const

SPACE_LEAVE_MEMORY_TIMER	= 2001	# space没有玩家时关闭空间TIMERID
SPACE_MAX_PLAYER = 20	#当前位面最大进入人数

class SpacePlanes( SpaceNormal, ImpPlanesSpace ):
	"""
	位面Space
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		super( SpacePlanes, self ).__init__()
		self._spawnInfoRecords = {} #记录刷新点信息
		self.maxPlayer = SPACE_MAX_PLAYER
		self.waiteLoaderSpawnPointPlanes = []
	
	def teleportEntity( self, position, direction, baseMailbox, pickData ):
		"""
		define method.
		传送一个entity到指定的space中
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX,
		@param params: 一些关于该entity进入space的额外参数；
		@type params : PY_DICT = None
		"""
		if self.checkSpaceFull():#判断是否满员
			self.pushPlayerToEnterList( position, direction, baseMailbox, pickData )
		else:
			pickData[ "fullSpaceNumber" ] = self.spaceNumber
			self.domainMB.teleportEntity( position, direction, baseMailbox, pickData )
	
	def _teleportEntityToPlanes( self, position, direction, baseMailbox, pickData ):
		"""
		传送一个entity到指定的space位面中
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX,
		@param params: 一些关于该entity进入space的额外参数；
		@type params : PY_DICT = None
		"""
		ImpPlanesSpace._teleportEntityToPlanes( self, position, direction, baseMailbox, pickData )
	
	def onLeave( self, baseMailbox, params ):
		"""
		define method.
		玩家离开空间
		@param baseMailbox: 玩家mailbox
		@type baseMailbox: mailbox
		@param params: 玩家onLeave时的一些额外参数
		@type params: py_dict
		"""
		isNotify = False
		if self.checkSpaceFull():
			isNotify = True
			
		self.unregisterPlayer( baseMailbox )
		self.getScript().onLeave( self, baseMailbox, params )
		
		if isNotify:
			self.domainMB.setPlanesSpaceNotFull( self.spaceNumber )
		
		planesID = params["planesID"]
		self.destroyPlanes( planesID )

	#----------------------------
	#关于怪物刷出
	#----------------------------
	def _createOneSpawnEntity( self, entityType, sec, matrix ):
		"""
		创建一个spawn entity, 这里的entity指的不一定是SpawnPoint，还有直接创建的有base的entity
		"""
		sec[ "properties" ].writeInt( "planesID", 1 ) #第一次刷出的怪物，位面ID 肯定是1
		e = SpaceNormal._createOneSpawnEntity( self, entityType, sec, matrix )
		return e
	
	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		创建好了一个entity的通知
		@param	entityType		: entity的脚本类别
		@type 	entityType		: String
		@param	entity			: baseEntity实体
		"""
		super( SpaceNormal, self ).onLoadedEntity( entityType, baseEntity )

	def _recordSpawnInfos( self, entityType, section, matrix ):
		"""
		记录刷出entity的数据，用于类似怪物恢复的功能
		"""
		if not self._spawnInfoRecords.has_key( entityType ):
			self._spawnInfoRecords[ entityType ] = []
		self._spawnInfoRecords[ entityType ].append( ( section, matrix ) ) #这里的sec是内存里面的数据，可能会不断的写！被其它地方写了这里保存的也会改变
	
	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		一个副本的spawnPoint 加载完毕。
		"""
		SpaceNormal.onSpawnPointLoadedOver( self, retCode )
		ImpPlanesSpace.onSpawnPointLoadedOver( self, retCode )
	
	def onLoadPlanesEntitiesOver( self, planesID ):
		"""
		virtual method.
		成功加载完一个位面的怪物
		"""
		ImpPlanesSpace.onLoadPlanesEntitiesOver( self, planesID )
	
	#---------------------------------------------------------------------
	#引擎回调
	#---------------------------------------------------------------------
	def onTimer( self, id, userArg ):
		"""
		定时器回调接口
		"""
		super( SpaceNormal, self ).onTimer( id, userArg )
		super( SpacePlanes, self ).onTimer( id, userArg )