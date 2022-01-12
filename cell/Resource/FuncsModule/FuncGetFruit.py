# -*- coding:gb18030 -*-

from Function import Function
import csstatus
import csdefine
from bwdebug import *
import Const
import BigWorld

class FuncGetFruit( Function ):
	"""
	��Ϧ��������������ȡ
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self._itemID = section.readInt( "param1" )

	def valid( self, playerEntity, talkEntity = None ):
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

	def do( self, playerEntity, talkEntity = None ):
		"""
		ִ��һ������

		@param playerEntity: ���
		@type  playerEntity: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		playerEntity.endGossip( talkEntity )
		if talkEntity is None:
			ERROR_MSG( "player( %s ) talk entity is None." % player.getName() )
			return
		# �ж���Ƿ���
		if not BigWorld.globalData.has_key( "FruitStart" ):
			playerEntity.statusMessage( csstatus.ROLE_TANABATA_QUIZ_NOT_START )
			return

		# �ж�����Ƿ���ȡ����Ľ���
		lastTakeTime = playerEntity.queryRoleRecord( "getFruitTime" )
		lt = time.localtime()
		curT = str( lt[1] ) + "+" + str( lt[2] )

		if lastTakeTime == curT:
			playerEntity.client.onStatusMessage( csstatus.FRUIT_HAVE_GET, "" )
			return

		item = playerEntity.createDynamicItem( self._itemID )
		if item is None: return

		checkReult = playerEntity.checkItemsPlaceIntoNK_( [item] )
		if checkReult != csdefine.KITBAG_CAN_HOLD:
			playerEntity.statusMessage( csstatus.FRUIT_GET_BAG_FULL )
			return
		playerEntity.addItem( item, reason = csdefine.ADD_ITEM_GET_FRUIT )
		playerEntity.setRoleRecord( "getFruitTime", curT )