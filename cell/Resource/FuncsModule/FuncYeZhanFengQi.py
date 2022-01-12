# -*- coding: gb18030 -*-

from Function import Function
import csdefine
import BigWorld
import time
import csstatus
import csconst
from ActivityRecordMgr import g_activityRecordMgr
from ObjectScripts.GameObjectFactory import g_objFactory

class FuncYeZhanFengQi( Function ):
	"""
	���뾭���Ҷ�����
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.spaceName = section.readString( "param1" ) # �����ͼclassName
		self.level = section.readInt( "param2" )		#����ȼ�
		self.maxLevel = 110

	def do( self, player, talkEntity = None ):
		"""
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		if player.isActivityCanNotJoin( csdefine.ACTIVITY_YE_ZHAN_FENG_QI ):
			player.statusMessage( csstatus.YE_ZHAN_FENG_QI_ACT_FULL )
			return
		
		objScript = g_objFactory.getObject( self.spaceName )
		if player.level < objScript.minLevel:
			player.statusMessage( csstatus.YE_ZHAN_FENG_QI_ENTER_LEVEL, self.level )
			return
			
		if player.level > objScript.maxLevel:
			player.statusMessage( csstatus.YE_ZHAN_FENG_QI_ENTER_MAX_LEVEL, self.level )
			return
		
		pos, direction = objScript.getRandomEnterPos()
		player.gotoSpace( self.spaceName, pos, direction )

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

