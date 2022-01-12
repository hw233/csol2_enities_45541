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

SPACE_LEAVE_MEMORY_TIMER	= 2001	# spaceû�����ʱ�رտռ�TIMERID
SPACE_MAX_PLAYER = 20	#��ǰλ������������

class SpacePlanes( SpaceNormal, ImpPlanesSpace ):
	"""
	λ��Space
	"""
	def __init__(self):
		"""
		���캯����
		"""
		super( SpacePlanes, self ).__init__()
		self._spawnInfoRecords = {} #��¼ˢ�µ���Ϣ
		self.maxPlayer = SPACE_MAX_PLAYER
		self.waiteLoaderSpawnPointPlanes = []
	
	def teleportEntity( self, position, direction, baseMailbox, pickData ):
		"""
		define method.
		����һ��entity��ָ����space��
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX,
		@param params: һЩ���ڸ�entity����space�Ķ��������
		@type params : PY_DICT = None
		"""
		if self.checkSpaceFull():#�ж��Ƿ���Ա
			self.pushPlayerToEnterList( position, direction, baseMailbox, pickData )
		else:
			pickData[ "fullSpaceNumber" ] = self.spaceNumber
			self.domainMB.teleportEntity( position, direction, baseMailbox, pickData )
	
	def _teleportEntityToPlanes( self, position, direction, baseMailbox, pickData ):
		"""
		����һ��entity��ָ����spaceλ����
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX,
		@param params: һЩ���ڸ�entity����space�Ķ��������
		@type params : PY_DICT = None
		"""
		ImpPlanesSpace._teleportEntityToPlanes( self, position, direction, baseMailbox, pickData )
	
	def onLeave( self, baseMailbox, params ):
		"""
		define method.
		����뿪�ռ�
		@param baseMailbox: ���mailbox
		@type baseMailbox: mailbox
		@param params: ���onLeaveʱ��һЩ�������
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
	#���ڹ���ˢ��
	#----------------------------
	def _createOneSpawnEntity( self, entityType, sec, matrix ):
		"""
		����һ��spawn entity, �����entityָ�Ĳ�һ����SpawnPoint������ֱ�Ӵ�������base��entity
		"""
		sec[ "properties" ].writeInt( "planesID", 1 ) #��һ��ˢ���Ĺ��λ��ID �϶���1
		e = SpaceNormal._createOneSpawnEntity( self, entityType, sec, matrix )
		return e
	
	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		��������һ��entity��֪ͨ
		@param	entityType		: entity�Ľű����
		@type 	entityType		: String
		@param	entity			: baseEntityʵ��
		"""
		super( SpaceNormal, self ).onLoadedEntity( entityType, baseEntity )

	def _recordSpawnInfos( self, entityType, section, matrix ):
		"""
		��¼ˢ��entity�����ݣ��������ƹ���ָ��Ĺ���
		"""
		if not self._spawnInfoRecords.has_key( entityType ):
			self._spawnInfoRecords[ entityType ] = []
		self._spawnInfoRecords[ entityType ].append( ( section, matrix ) ) #�����sec���ڴ���������ݣ����ܻ᲻�ϵ�д���������ط�д�����ﱣ���Ҳ��ı�
	
	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		һ��������spawnPoint ������ϡ�
		"""
		SpaceNormal.onSpawnPointLoadedOver( self, retCode )
		ImpPlanesSpace.onSpawnPointLoadedOver( self, retCode )
	
	def onLoadPlanesEntitiesOver( self, planesID ):
		"""
		virtual method.
		�ɹ�������һ��λ��Ĺ���
		"""
		ImpPlanesSpace.onLoadPlanesEntitiesOver( self, planesID )
	
	#---------------------------------------------------------------------
	#����ص�
	#---------------------------------------------------------------------
	def onTimer( self, id, userArg ):
		"""
		��ʱ���ص��ӿ�
		"""
		super( SpaceNormal, self ).onTimer( id, userArg )
		super( SpacePlanes, self ).onTimer( id, userArg )