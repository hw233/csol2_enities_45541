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

class FuncTongFengHuoLianTian( Function ):
	"""
	���������츱��
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
		if not player.isJoinTong():
			player.statusMessage( csstatus.TONG_FENG_HUO_LIAN_TIAN_NOT_TONG )
			return
			
		spaceKey = player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		player.set( "TongFengHuoLianTianEnterInfos", ( spaceKey, player.position, player.direction ) )
		BigWorld.globalData["TongManager"].onRoleSelectEnterFHLT( player.tong_dbID, player.base, spaceKey )
		
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
		return BigWorld.globalData.has_key( "fengHuoLianTianOverTime" )

