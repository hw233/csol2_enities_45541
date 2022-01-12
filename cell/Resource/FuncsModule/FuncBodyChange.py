# -*- coding: gb18030 -*-
#
"""
 ��������ĶԻ� 2009-01-17 SongPeifang
"""
#

from bwdebug import *
import cschannel_msgs
import ShareTexts as ST
from Function import Function
import csdefine
import csstatus
import sys
from MsgLogger import g_logger

class FuncLoginBCGame( Function ):
	"""
	�����μӱ������
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self._p1 = section.readString( "param1" )	# Ҫ���ż�ɾ����ֽ����Ʒ itemId1|itemId2|itemId3|itemId4|itemId5
		self._reqireItems = self._p1.split( '|' )	# ��Ҫ����ƷID���� type:str
		if len( self._reqireItems ) == 0:
			ERROR_MSG( "������������Ի��������ô���" )

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if talkEntity == None:
			ERROR_MSG( "δ֪�����Ҳ������������NPC��" )
			return

		if not talkEntity.canLogin():
			# �����Ѿ�����
			player.setGossipText( cschannel_msgs.BIAN_SHEN_VOICE_1 )
			player.sendGossipComplete( talkEntity.id )
			return

		if talkEntity.isPlayerLogin( player ):
			# ����Ѿ���������
			player.setGossipText( cschannel_msgs.BIAN_SHEN_VOICE_2 )
			player.sendGossipComplete( talkEntity.id )
			for i in self._reqireItems:
				card = player.findItemFromNKCK_( int(i) )	# �ж��Ƿ��Ѿ���ֽ����
				if card == None:
					card = player.createDynamicItem( int(i) )
					player.addItemAndNotify_( card, csdefine.ADD_ITEM_LOGINBCGAME )
			return
			
		if player.iskitbagsLocked():	# ����������by����
			player.endGossip( talkEntity )
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return

		if player.getNormalKitbagFreeOrderCount() < len( self._reqireItems ):
			# �����ռ䲻�����ܱ���
			player.setGossipText( cschannel_msgs.BIAN_SHEN_VOICE_3 % len( self._reqireItems ) )
			player.sendGossipComplete( talkEntity.id )
			return

		for i in self._reqireItems:
			card = player.findItemFromNKCK_( int(i) )	# �ж��Ƿ��Ѿ���ֽ����
			if card == None:
				card = player.createDynamicItem( int(i) )
				player.addItemAndNotify_( card, csdefine.ADD_ITEM_LOGINBCGAME )

		talkEntity.loginBCGame( player )
		player.setGossipText( cschannel_msgs.BIAN_SHEN_VOICE_4 )
		player.sendGossipComplete( talkEntity.id )
		try:
			g_logger.actJoinLog( csdefine.ACTIVITY_BIAN_SHEN_DA_SAI, csdefine.ACTIVITY_JOIN_ROLE, player.databaseID, player.getName() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )

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

class FuncBCReward( Function ):
	"""
	��ȡ�����������
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.itemID = section.readInt( "param1" )	# ��������ƷID
		self.sunBathCount = section.readInt( "param2" )	# �������չ�ԡʱ�䣨�룩
		self._p3 = section.readString( "param3" )	# Ҫ���ż�ɾ����ֽ����Ʒ itemId1|itemId2|itemId3|itemId4|itemId5
		self.sunBathMaxCount = section.readInt( "param4" )	# ÿ��ɹ���չ�ԡ���ʱ�䣨�룩
		self._reqireItems = self._p3.split( '|' )	# ��Ҫ����ƷID���� type:str
		if len( self._reqireItems ) == 0:
			ERROR_MSG( "��ȡ�������Ի��������ô���" )

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if talkEntity == None:
			ERROR_MSG( "δ֪�����Ҳ������������NPC��" )
			return

		if talkEntity.canLogin() or talkEntity.hasMembers():
			# �����ڱ�������ȡ����
			player.setGossipText( cschannel_msgs.BIAN_SHEN_VOICE_5 )
			player.sendGossipComplete( talkEntity.id )
			return

		for i in self._reqireItems:
			card = player.findItemFromNKCK_( int(i) )	# �ж��Ƿ��Ѿ���ֽ����
			if card != None:
				player.removeItem_( card.order, reason = csdefine.DELETE_ITEM_BCREWARD )	# �Ƴ���������ϵ�ֽ��

		if not player.databaseID in talkEntity._passMembers:
			# ������ȡ����
			player.setGossipText( cschannel_msgs.BIAN_SHEN_VOICE_6 )
			player.sendGossipComplete( talkEntity.id )
			return

		if self.itemID != 0:
			item = player.createDynamicItem( self.itemID )
			kitbagState = player.checkItemsPlaceIntoNK_( [item] )
			if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
				# �����ռ䲻��
				player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
				player.setGossipText( cschannel_msgs.BIAN_SHEN_VOICE_7 )
				player.sendGossipComplete( talkEntity.id )
				return
			player.addItemAndNotify_( item, csdefine.ADD_ITEM_BCREWARD )

		#player.updateSunBathCount( 0 - self.sunBathCount )
		#leftSunBathTime = ( self.sunBathMaxCount - player.sunBathDailyRecord.sunBathCount ) / 60	# ����
		#player.setGossipText( "@S{4}��ĺϷ��չ�ԡʱ��������30���ӣ��㵱ǰ��ʣ��%s���ӵ��չ�ԡʱ�䡣" % leftSunBathTime )
		player.setGossipText( cschannel_msgs.BIAN_SHEN_VOICE_8 )
		talkEntity.clearPassMembers( player )
		player.sendGossipComplete( talkEntity.id )

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