# -*- coding: gb18030 -*-
"""
�ɼ����ǵĶԻ� 2009-01-14 SongPeifang
"""

from Function import Function
import cschannel_msgs
import ShareTexts as ST
from bwdebug import *
import csstatus
import BigWorld
import time
import ItemTypeEnum
import csdefine
import items
import sys
from MsgLogger import g_logger

g_items = items.instance()

class FuncCiFu( Function ):
	"""
	������͸�
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._p1 = section.readString( "param1" )	# ��Ҫ����Ʒ itemId1|itemId2|itemId3|itemId4|itemId5
		self._p2 = section.readInt( "param2" )		# ÿ����Խ��еĴ���
		self._p3 = section.readInt( "param3" )		# ��õ���Ʒ����
		self._p4 = section.readInt( "param4" )		# ��������Ʒ�ĸ���
		self._reqireItems = self._p1.split( '|' )	# ��Ҫ����ƷID���� type:str
		if len( self._reqireItems ) == 0:
			ERROR_MSG( "������͸��Ի����ô���" )

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if not player.cifuRecord.checklastTime():
			# ����һ���������͸�������¼
			player.cifuRecord.reset()

		if player.cifuRecord._degree >= self._p2:
			# ����ÿ����������ȡ�Ĵ�����
			player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_0 % self._p2 )
			player.sendGossipComplete( talkEntity.id )
			return

		rwdItem = g_items.createDynamicItem( self._p3, self._p4 )
		kitbagState = player.checkItemsPlaceIntoNK_( [ rwdItem ] )
		if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
			# �����ռ䲻��
			player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			player.setGossipText( cschannel_msgs.BIAN_SHEN_VOICE_7 )
			player.sendGossipComplete( talkEntity.id )
			return

		items = []
		for itemID in self._reqireItems:
			item = player.findItemFromNKCK_( int( itemID ) )
			items.append( item )
			if not item:
				player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_2 )
				player.sendGossipComplete( talkEntity.id )
				return
		for item in items:
			player.removeItem_( item.order, 1, csdefine.DELETE_ITEM_CIFU )	# �Ƴ����������Ʒ

		rwdItem.setBindType( ItemTypeEnum.CBT_PICKUP, player )
		player.addItemAndNotify_( rwdItem, csdefine.ADD_ITEM_CIFU )
		player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_3 )
		player.cifuRecord.incrDegree()
		player.sendGossipComplete( talkEntity.id )
		Function.do( self, player, talkEntity )
		
		g_logger.actJoinLog( csdefine.ACTIVITY_TIAN_CI_QI_FU, csdefine.ACTIVITY_JOIN_ROLE, player.databaseID, player.getName() )

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


class FuncXianLing( Function ):
	"""
	������������
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._p1 = section.readString( "param1" )	# ��Ҫ����Ʒ itemId1|itemId2|itemId3|itemId4|itemId5
		self._p2 = section.readInt( "param2" )		# ÿ����Խ��еĴ���
		self._p3 = section.readInt( "param3" )		# ��������ƷID
		self._p4 = section.readInt( "param4" )		# ��������Ʒ����
		self._reqireItems = self._p1.split( '|' )	# ��Ҫ����ƷID���� type:str
		if len( self._reqireItems ) == 0:
			ERROR_MSG( "������������Ի����ô���" )

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if not player.xianlingRecord.checklastTime():
			# ����һ������������������¼
			player.xianlingRecord.reset()

		if player.xianlingRecord._degree >= self._p2:
			# ����ÿ����������Ĵ�����
			player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_4 % self._p2 )
			player.sendGossipComplete( talkEntity.id )
			return

		rwdItem = g_items.createDynamicItem( self._p3, self._p4 )
		kitbagState = player.checkItemsPlaceIntoNK_( [ rwdItem ] )
		if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
			# �����ռ䲻��
			player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			player.setGossipText( cschannel_msgs.BIAN_SHEN_VOICE_7 )
			player.sendGossipComplete( talkEntity.id )
			return

		items = []
		for itemID in self._reqireItems:
			item = player.findItemFromNKCK_( int( itemID ) )
			items.append( item )
			if not item:
				player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_6 )
				player.sendGossipComplete( talkEntity.id )
				return
		for item in items:
			player.removeItem_( item.order, 1, csdefine.DELETE_ITEM_XIANLING )	# �Ƴ����������Ʒ

		rwdItem.setBindType( ItemTypeEnum.CBT_PICKUP, player )
		player.addItemAndNotify_( rwdItem, csdefine.ADD_ITEM_XIANLING )
		player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_7 )
		player.xianlingRecord.incrDegree()
		player.sendGossipComplete( talkEntity.id )
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


class FuncJianZheng( Function ):
	"""
	������֤��Ե
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._p1 = section.readString( "param1" )			# ��Ҫ����Ʒ itemId1|itemId2
		self._p2 = section.readInt( "param2" )				# ������Ĵ���
		self._p3 = section.readInt( "param3" )				# ��������ҵ���ƷID
		self._p4 = section.readInt( "param4" )				# ��������Ʒ����
		self._memberDistance = section.readInt( "param5" )	# ��Ա��Ҫ�ڶ�Զ�ľ����ڲ��������
		self._reqireItems = self._p1.split( '|' )			# ��Ҫ����ƷID���� type:str
		if len( self._reqireItems ) == 0:
			ERROR_MSG( "������֤��Ե�Ի����ô���" )

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		teamMembers = player.getAllMemberInRange( self._memberDistance, talkEntity.position )
		if player.captainID != player.id or len( teamMembers ) <= 1:
			player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_8 )
			player.sendGossipComplete( talkEntity.id )
			return
		elif len( teamMembers ) > 2:
			player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_9 )
			player.sendGossipComplete( talkEntity.id )
			return

		player2 = teamMembers[0]
		if player2.id == player.id:
			player2 = teamMembers[1]

		if not player.jianZhengRecord.checklastTime():
			# ����һ�������֤��Ե������¼
			player.jianZhengRecord.reset()
		if not player2.jianZhengRecord.checklastTime():
			# ����һ�������֤��Ե������¼
			player2.jianZhengRecord.reset()

		if player.jianZhengRecord._degree >= self._p2:
			# ����ÿ����Լ�֤��Ե�Ĵ�����
			player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_10 % self._p2 )
			player.sendGossipComplete( talkEntity.id )
			return
		elif player2.jianZhengRecord._degree >= self._p2:
			# ����ÿ����Լ�֤��Ե�Ĵ�����
			player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_11 % ( self._p2, player2.getName() ) )
			player.sendGossipComplete( talkEntity.id )
			return
		reqItemsValid = False
		itemID1 = int( self._reqireItems[0] )
		itemID2 = int( self._reqireItems[1] )
		item1 = player.findItemFromNKCK_( itemID1 )
		item2 = player.findItemFromNKCK_( itemID2 )
		player1Item = None
		player2Item = None
		if item1:
			item = player2.findItemFromNKCK_( itemID2 )
			if item:
				reqItemsValid = True
				player1Item = item1
				player2Item = item
		if not reqItemsValid:
			if item2:
				item = player2.findItemFromNKCK_( itemID1 )
				if item:
					reqItemsValid = True
					player1Item = item2
					player2Item = item
		if not reqItemsValid:
			player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_12 )
			player.sendGossipComplete( talkEntity.id )
			return

		rwdItem1 = g_items.createDynamicItem( self._p3, self._p4 )
		rwdItem2 = g_items.createDynamicItem( self._p3, self._p4 )
		kitbagState1 = player.checkItemsPlaceIntoNK_( [ rwdItem1 ] )
		kitbagState2 = player2.checkItemsPlaceIntoNK_( [ rwdItem2 ] )
		if kitbagState1 == csdefine.KITBAG_NO_MORE_SPACE:
			# ���1�����ռ䲻��
			player.setGossipText( cschannel_msgs.BIAN_SHEN_VOICE_7 )
			player.sendGossipComplete( talkEntity.id )
			return
		elif kitbagState2 == csdefine.KITBAG_NO_MORE_SPACE:
			# ���2�����ռ䲻��
			player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_14 % player2.getName() )
			player.sendGossipComplete( talkEntity.id )
			return

		#player.base.chat_sysBroadcast( "%s��%s���������ָ����ǧ����ᣬף���������곤�棡" % ( player.getName(), player2.getName() )  )
		player.jianZhengRecord.incrDegree()
		player2.jianZhengRecord.incrDegree()
		player.removeItem_( player1Item.order, 1, csdefine.DELETE_ITEM_JIANZHENG )
		player2.removeItem_( player2Item.order, 1, csdefine.DELETE_ITEM_JIANZHENG )
		rwdItem1.setBindType( ItemTypeEnum.CBT_PICKUP, player )
		rwdItem2.setBindType( ItemTypeEnum.CBT_PICKUP, player2 )
		player.addItemAndNotify_( rwdItem1, csdefine.ADD_ITEM_JIANZHENG )
		player2.addItemAndNotify_( rwdItem2, csdefine.ADD_ITEM_JIANZHENG )
		player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_15 )
		player.sendGossipComplete( talkEntity.id )
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


class FuncPearlPrime( Function ):
	"""
	��ȡ���龫��
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._itemID = section.readInt( "param1" )		# ��Ҫ����ƷID
		formulaStr = section.readString( "param2" )		# ÿ�ο��Ի�õľ���Ĺ�ʽ lv+23
		self._playTimes = section.readInt( "param3" )	# ÿ�������Ĵ���
		self._hpVal = 23	#int( formulaStr[ 3:len( formulaStr ) ] )	# ���ӵľ���ֵ
		self._hpOpt = "+"	#formulaStr[ 2:3 ]							# ������

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if not player.pearlPrimeRecord.checklastTime():
			# ����һ�������ȡ���龫��������¼
			player.pearlPrimeRecord.reset()

		if player.pearlPrimeRecord._degree >= self._playTimes:
			# ����ÿ����ȡ���龫���Ĵ�����
			player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_16 % self._playTimes )
			player.sendGossipComplete( talkEntity.id )
			return

		item = player.findItemFromNKCK_( self._itemID )
		if not item:
			player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_17 )
			player.sendGossipComplete( talkEntity.id )
			return
		player.removeItem_( item.order, 1, csdefine.DELETE_ITEM_PEARLPRIME )	# �Ƴ����������Ʒ
		increaseEXP = self.getIncreaseEXP( player.level, self._hpOpt, self._hpVal )
		player.addExp( increaseEXP, csdefine.CHANGE_EXP_PEARLPRIME )
		player.pearlPrimeRecord.incrDegree()
		player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_18 )
		player.sendGossipComplete( talkEntity.id )
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

	def getIncreaseEXP( self, level, opration, value ):
		"""
		���ݹ�ʽ������ӵ�Exp
		"""
		# ��ʱ�ѹ�ʽд�� ��level + value ��*10
		return ( level + value ) * 10