# -*- coding: gb18030 -*-
#


"""
"""
from Function import Function
import csdefine
import BigWorld
import time
import math
import random
import Math
import csstatus
import utils
from bwdebug import *

from ObjectScripts.GameObjectFactory import g_objFactory

ENTERN_SHUIJING_MENBER_DISTANCE = 30.0
#SHUIJING_POSITION = ( 15.221, 19.823, -21.644 )
SHUIJING_POSITION = ( -37.092, 0.116, 40.691 )


class FuncShuijing( Function ):
	"""
	����ˮ������
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.level = section.readInt( "param1" )										#����ȼ�
		self.recordKey = "shuijing_record"
		self.spaceName = "shuijing"


	def do( self, player, talkEntity = None ):
		"""
		����ˮ��������
		����
			�������������Ѷ�Ա����������
				������鵱ǰû�и�����
				Ҫ��������Ƕӳ���
				�ﵽ�ȼ�Ҫ��
				������������3�ˡ�
				�����Աû�н���������ġ�
			������������ֻ���Լ�һ���˽�ȥ��
				����ӡ�
				�ж��鸱�����ڡ�

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
					
		#��ҵȼ�����
		if self.level > player.level:
			player.statusMessage( csstatus.SHUIJING_LEVEL_NOT_ARRIVE, self.level )
			return
		
		if not BigWorld.globalData.has_key('AS_shuijingStart') or not BigWorld.globalData["AS_shuijingStart"]:
			#ˮ���û�п���
			player.statusMessage( csstatus.SHUIJING_IS_NOT_OPEN )
			return
		
		#���û�����
		if not player.isInTeam():
			player.statusMessage( csstatus.SHUIJING_NEED_TEAM )
			return

		if BigWorld.globalData.has_key( 'Shuijing_%i'%player.getTeamMailbox().id ):
			if player.isActivityCanNotJoin( csdefine.ACTIVITY_SHUI_JING )  and player.query( "lastShuijintTeamID", 0 ) != player.getTeamMailbox().id:
				player.statusMessage( csstatus.SHUIJING_FORBID_TWICE )
				return
			shuijingKey = BigWorld.globalData[ "Shuijing_%i"%player.getTeamMailbox().id ]
			BigWorld.globalData[ "ShuijingManager" ].reEnter( shuijingKey, player.base )
#			player.gotoSpace(self.spaceName, SHUIJING_POSITION, (0,0,0))
		else:
			#����û�и��������ߴ�������
			if not player.isTeamCaptain():
				player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
				return
			
			entities = []
			dbidList = []
			pList = player.getAllMemberInRange( ENTERN_SHUIJING_MENBER_DISTANCE )
#			if not len( pList ) >= 3 :
			if len( pList ) != 3 :
				player.statusMessage( csstatus.SHUIJING_ROLE_IS_ENOUGH_MEMBER )
				return
			for i in pList:
				if i.level < self.level:
					player.statusMessage( csstatus.ROLE_MEMBER_HAS_NOT_SHUIJING_LEVEL )
					return
				if i.isActivityCanNotJoin( csdefine.ACTIVITY_SHUI_JING ) :
					player.statusMessage( csstatus.SHUIJING_HAS_ENTERED_TODAY )
					return
				entities.append( i.base )
				dbidList.append( i.databaseID )
			pList.remove( player )
			player.set( "lastShuijintTeamID", player.getTeamMailbox().id )
			player.set( "shuijing_checkPoint", 1 )
#			player.gotoSpace(self.spaceName, SHUIJING_POSITION, (0,0,0))
			for i in pList:
				i.set( "lastShuijintTeamID", player.getTeamMailbox().id )
				i.set( "shuijing_checkPoint", 1 )
#				i.gotoSpace(self.spaceName, SHUIJING_POSITION, (0,0,0))
			
			BigWorld.globalData[ "ShuijingManager" ].onRequestShuijing( entities, dbidList, player.getLevel(), player.getTeamMailbox() )

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True

class FuncShuijingCallEntity( Function ):
	"""
	ˮ�������Ի��ٻ����������ͬʱ��ʼ��һ��ˢ��
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.classNameList = section.readString( "param1" ).split( ";" )						# className�б�
		self.mountList = section.readString( "param2" ).split( ";" )							# ÿ��className��Ӧ�Ĺ�������
		self.positionAndDirectionLists = section.readString( "param3" ).split( ";" )

	def do( self, player, talkEntity = None ):
		"""
		ˮ�������Ի��ٻ����������ͬʱ��ʼ��һ��ˢ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		try:
			spaceEntity = BigWorld.entities[ player.getCurrentSpaceBase().id ]
		except KeyError, errStr :
			EXCEHOOK_MSG( errStr )
			return
		spaceEntity.startSpawnMonsterByTalk( player.id, self.classNameList, self.mountList, self.positionAndDirectionLists )

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		try:
			spaceEntity = BigWorld.entities[ player.getCurrentSpaceBase().id ]
		except KeyError, errStr :
			EXCEHOOK_MSG( errStr )
			return
		if spaceEntity.queryTemp( "shuijing_callEntity", 0 ):
			return True
		else:
			return False

class FuncLeaveShuijing( Function ):
	"""
	�뿪ˮ������
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )


	def do( self, player, talkEntity = None ):
		"""
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if player.isInTeam():
			if player.shuijingKey:
				BigWorld.globalData[ "ShuijingManager" ].playerLeave( player.shuijingKey, player.base )
			player.endGossip( talkEntity )
			return
		player.endGossip( talkEntity )


	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True

