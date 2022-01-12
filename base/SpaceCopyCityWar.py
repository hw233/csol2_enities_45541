# -*- coding: gb18030 -*-

import BigWorld
import cschannel_msgs
import ShareTexts as ST
import Language
from bwdebug import *
import time
import Love3
import Const
import csstatus
from SpaceCopy import SpaceCopy
CITY_WAR_SPAWN_POINT = [ "SpawnPointCityWar", ] # ��սˢ�µ�

class SpaceCopyCityWar( SpaceCopy ):
	# ������ս
	def __init__(self):
		SpaceCopy.__init__( self )
		self.rightTongCount = 0
		self.leftTongCount = 0
		self.enterRecord = {}
		self.isClose = False
		self.bossBaseMB = None	# ֻ��ͳ˧���������
		self.cityWarSpawnPoint = []
		
	def onGetCell(self):
		# cellʵ�崴�����֪ͨ���ص�callbackMailbox.onSpaceComplete��֪ͨ������ɡ�
		SpaceCopy.onGetCell( self )
		if self.params.has_key( "CityWarLevelUp" ):
			self.cell.onCityWarLevelUp()
	
	def closeCityWarRoom( self ):
		# define method.
		# ��ǰ������ĳ��ս�� ��tongmanager �ر����з���
		if self.isClose:
			return
			
		self.isClose = True
		self.onWarOver()
		self.cell.closeCityWarRoom()
	
	def checkNeedSpawn( self, sec ):
		if sec.readString( "type" ) in CITY_WAR_SPAWN_POINT:
			if self.getScript().getRoomLevel < 1:
				return False
				
			if not self.params.has_key( "defend" ):
				return False
			
			belong = sec[ "properties" ].readString( "belong" )
			if belong:
				belongTongDBID = self.params.get( belong ) # belong : left / right / defend
				if belongTongDBID:
					sec[ "properties" ].writeInt( "belongTongDBID", belongTongDBID )
				else:
					return False
		
		return SpaceCopy.checkNeedSpawn( self, sec )
	
	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		��������һ��entity��֪ͨ
		@param	entityType		: entity�Ľű����
		@type 	entityType		: String
		@param	entity			: baseEntityʵ��
		"""
		if entityType in CITY_WAR_SPAWN_POINT:
			self.cityWarSpawnPoint.append( baseEntity )
	
	def onWarOver( self ):
		# define method
		# ��ս������ֹͣս��
		for spMailbox in self.cityWarSpawnPoint:
			spMailbox.cell.onCityWarOver()