# -*- coding: gb18030 -*-
import time

import BigWorld

import csstatus
import csconst
import csdefine
import Const
from bwdebug import *
from SpaceCopy import SpaceCopy

TIMER_CLOSE_ACT = 1

class SpaceCopyMaps( SpaceCopy ):
	"""
	���ͼ���˸����ű�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopy.__init__( self )
		self._spaceMapsInfos = []
		self._spaceMapsNo = 0
		self._spaceLife = 1
		self._closeTime = 1
		self._door = []
		self._doorPosition = ( 0,0, 0)
		self._isPickMembers = 0
		self._copyBossNum = 0
		self._copyMonsterNum = 0
		self._curBossNum  = 0
		self._curMonsterNum = 0
		self._bossID = []
		
		self.difficulty = 0
	
	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		SpaceCopy.load( self, section )
		for idx, item in enumerate( section[ "Space" ][ "spaceMapsInfos" ].values() ):
			className = item[ "className" ].asString
			pos = tuple( [ float(x) for x in item["position"].asString.split() ] )
			direction = tuple( [ float(x) for x in item["direction"].asString.split() ] )
			self._spaceMapsInfos.append( ( className, pos, direction ) )
			if className == self.className:
				self._spaceMapsNo = idx
		
		self._spaceLife = section[ "Space" ][ "spaceLife" ].asInt  # ����ʱ��(����)
		self.difficulty = section[ "Space" ][ "difficulty" ].asInt  # �����Ѷ�
		self._closeTime = section[ "Space" ][ "closeTime" ].asInt  # �����ر�ʱ�䣨�룩
				
		self._copyBossNum = section[ "Space" ][ "copyBossNum" ].asInt
		self._copyMonsterNum = section[ "Space" ][ "copyMonsterNum" ].asInt
		self._curBossNum = section[ "Space" ][ "curBossNum" ].asInt
		self._curMonsterNum = section[ "Space" ][ "curMonsterNum" ].asInt
		self._bossID = section[ "Space" ][ "bossID" ].asString.split(";")
		
		# ��ʼ������������
		if section[ "Space" ].has_key( "doorPoint" ):
			for item in section[ "Space" ][ "doorPoint" ].values():
				doorPro = {}
				doorPro[ "isCreate" ] = item[ "isCreate" ].asInt
				doorPro[ "pos" ] = tuple( [ float(x) for x in item.readString( "pos" ).split() ] )
				doorPro[ "useRectangle" ] = item.readInt( "properties/useRectangle" )
				doorPro[ "radius" ] = item.readFloat( "properties/radius" )
				doorPro[ "volume" ] = item.readVector3( "properties/volume" )
				doorPro[ "modelNumber" ] = item.readString( "properties/modelNumber" )
				doorPro[ "modelScale" ] = item.readFloat( "properties/modelScale" )
				doorPro[ "destSpace" ] = item.readString( "properties/destSpace" )
				
				destPosition = item.readString( "properties/destPosition" )
				doorPro[ "destPosition" ] = tuple( [ float(x) for x in destPosition.split() ] )
				destDirection = item.readString( "properties/destDirection" )
				doorPro[ "destDirection" ] = tuple( [ float(x) for x in destDirection.split() ] )
				
				doorPro[ "nickname" ] = item.readString( "properties/nickname" )
				doorPro[ "uname" ] = item.readString( "properties/uname" )
				self._door.append( doorPro )
	
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		�����Լ������ݳ�ʼ������ selfEntity ������
		"""
		SpaceCopy.initEntity( self, selfEntity )
		selfEntity.setTemp( "bossCount", self._curBossNum )
		selfEntity.setTemp( "allMonsterCount", self._curMonsterNum )
		life = self._spaceLife * 60 - ( time.time() - selfEntity.createTime )
		selfEntity.addTimer( life, 0, Const.SPACE_TIMER_ARG_LIFE )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, self._copyBossNum - selfEntity.copyStatBoss )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, self._copyMonsterNum - selfEntity.copyStatMonster )
		self.createDoor( selfEntity, True )
	
	def packedDomainData( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		@param entity: ͨ��Ϊ���
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		# ����databaseID������space domain�ܹ���������ȷ�ļ�¼�����Ĵ����ߣ�
		# �Ҳ��õ�������ڶ�ʱ���ڣ��ϣ����ߺ�����ʱ�һظ��������⣻
		d = { 'dbID' : entity.databaseID }
		d[ "enterCopyKey" ] = self.className
		d[ "enterCopyNo" ] = self._spaceMapsNo
		return d
	
	def getSpaceBirth( self, gNo = 0 ):
		"""
		��ȡ����λ��
		"""
		return self._spaceMapsInfos[ gNo ]
	
	def getCopyNo( self ):
		"""
		��ȡ��ǰ�ĵ�ͼ�ı��
		"""
		return self._spaceMapsNo
	
	def getNextSpace( self ):
		"""
		���͵���һ�ŵ�ͼ
		"""
		if len( self._spaceMapsInfos ) == self._spaceMapsNo:
			return -1
		
		return self._spaceMapsInfos[ self._spaceMapsNo + 1 ]
	
	def createDoor( self, selfEntity, isInit ):
		"""
		����ͨ����һ�ŵ�ͼ�Ĵ�����
		"""
		for item in self._door:
			if item[ "isCreate" ] == isInit:
				e = BigWorld.createEntity( "SpaceDoor", selfEntity.spaceID, item[ "pos" ], (0, 0, 0), item )
				if e != None:
					e.modelScale = item[ "modelScale" ]
		
	def onCloseMapsCopy( self, selfEntity ):
		"""
		�رն��ͼ�������
		"""
		for e in selfEntity._players:
			e.client.onStatusMessage( csstatus.SPACE_CLOSE, str( ( self._closeTime, ) ) )
			
		selfEntity.addTimer( self._closeTime, 0.0, Const.SPACE_TIMER_ARG_KICK )
		selfEntity.addTimer( self._closeTime + 5, 0.0, Const.SPACE_TIMER_ARG_CLOSE )
	
	def closeMapsCopy( self, playerEntity ):
		"""
		�رն��ͼ�������(��ҵ���)
		"""
		if BigWorld.cellAppData.has_key( selfEntity.getSpaceGlobalKey() ):
			del BigWorld.cellAppData[ selfEntity.getSpaceGlobalKey() ]
			
		BigWorld.globalData[ "SpaceManager" ].remoteCallDomain( self.className, "closeCopyItem", ( { "dbID": playerEntity.databaseID } ) )
	
	def onTimer( self, selfEntity, id, userArg ):
		"""
		ʱ�������
		"""
		if userArg == Const.SPACE_TIMER_ARG_LIFE:
			selfEntity.domainMB.closeCopyItem( { "dbID": selfEntity.copyKey } )
		else:
			SpaceCopy.onTimer( self, selfEntity, id, userArg )
	
	def setCopyKillBoss( self, selfEntity, bossNum ):
		"""
		define method
		���ø���BOSS����
		"""
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, self._copyBossNum - bossNum )
		
	def setCopyKillMonster( self, selfEntity, monsterNum ):
		"""
		define method
		���ø���С������
		"""
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, self._copyMonsterNum - monsterNum )

	def onAllCopyMonsterkilled( self, selfEntity, spaceName ):
		"""
		������С��ȫ������ɱ
		"""
		pass