# -*- coding: gb18030 -*-
#


"""
"""
from Function import Function
import csdefine
import BigWorld
import time
import csstatus
import csconst
from ActivityRecordMgr import g_activityRecordMgr
from ObjectScripts.GameObjectFactory import g_objFactory

CAN_JOIN_CAMP_FENG_HUO_LEVEL = 40

class FuncCampFengHuoLianTianSignUp( Function ):
	"""
	��Ӫ������츱������
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
		player.endGossip( talkEntity )
		
			
		#���û�����
		if player.getLevel() < CAN_JOIN_CAMP_FENG_HUO_LEVEL:
			player.statusMessage( csstatus.CAMP_FENG_HUO_LIAN_TIAN_LEVEL_NOT_ENOUGH )
			return
			
		BigWorld.globalData["CampMgr"].onRequestCampFengHuoSignUp( player.getCamp(), player.databaseID, player.base )
		
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
		return BigWorld.globalData.has_key( "campFengHuo_startSignUp" )

class FuncEnterCampFengHuoLianTian( Function ):
	"""
	������Ӫ������츱��
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
		player.endGossip( talkEntity )
		
			
		#���û�����
		if player.getLevel() < CAN_JOIN_CAMP_FENG_HUO_LEVEL:
			player.statusMessage( csstatus.CAMP_FENG_HUO_LIAN_TIAN_LEVEL_NOT_ENOUGH )
			return
			
		spaceKey = player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		player.set( "CampFengHuoLianTianEnterInfos", ( spaceKey, player.position, player.direction ) )
		BigWorld.globalData["CampMgr"].onRoleRequestEnterCampFHLT( player.getCamp(), player.databaseID, player.base )
		
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
		return BigWorld.globalData.has_key( "campFengHuo_start" )
