# -*- coding: gb18030 -*-

"""
"""
import csstatus
import cschannel_msgs
import ShareTexts as ST
import sys
import csdefine
from Function import Function

class FuncTreasureMap( Function ):
	"""
	ʵ����NPC�Ի�ʱ�õ�һ��ģ����ֽ��
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._reqLevel = section.readInt( "param1" )
		self._reqMoney = section.readInt( "param2" )
		self._itemID = section.readInt( "param3" )

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		if player.iskitbagsLocked():	# ����������by����
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		if self._reqLevel > player.level:
			player.statusMessage( csstatus.ROLE_TELPORT_NOT_ENOUGH_LEVEL, self._reqLevel )
			return
		if self._reqMoney > 0:
			if not player.payMoney( self._reqMoney, csdefine.CHANGE_MONEY_TREASUREMAP ):
				player.setGossipText( cschannel_msgs.TONGCITYWAR_VOICE_15 )
				player.sendGossipComplete( talkEntity.id )
				return
		item = player.createDynamicItem( self._itemID )
		player.addItem( item, csdefine.ADD_ITEM_QUEST )			# �����һ��ģ����ֽ��
		item.generateLocation( player )	# ���ɱ���λ������
		Function.do( self, player, talkEntity )

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

