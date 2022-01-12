# -*- coding: gb18030 -*-
"""
�ɼ����ǵĶԻ� 2009-01-14 SongPeifang
"""

import csstatus
import cschannel_msgs
import ShareTexts as ST
import BigWorld
import csdefine
import items
import random
import sys
from Function import Function
from bwdebug import *
g_items = items.instance()

ENTERN_SHITU_MENBER_DISTANCE = 20.0

def getItemName( key ):
	"""
	��ȡ��Ʒ������
	"""
	itemNames = { 50101064:cschannel_msgs.SHI_TU_GIFT_VOICE_0, 50101065:cschannel_msgs.SHI_TU_GIFT_VOICE_1, 50101066:cschannel_msgs.SHI_TU_GIFT_VOICE_2, 50101067:cschannel_msgs.SHI_TU_GIFT_VOICE_3 }
	try:
		return itemNames[ int( key ) ]
	except KeyError:
		ERROR_MSG( "ʦͽ�ػ���Ʒ����û��IDΪ'%s'����Ʒ��" % key )
		return cschannel_msgs.SHI_TU_GIFT_VOICE_4


class FuncShiTuReward( Function ):
	"""
	ʦͽ�ػ���ȡ����
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._p1 = section.readString( "param1" )		# ��Ҫ����Ʒ itemId1|itemId2|itemId3 ������
		self._skillID = section.readInt( "param2" )		# �����ļ���ID(��Ϊ��������һ��buff)
		self._describe = section.readString( "param3" )	# ��ȡ�������
		self._reqireItems = self._p1.split( '|' )		# ��Ҫ����ƷID���� type:str
		if len( self._reqireItems ) == 0:
			ERROR_MSG( "û��������ȡ����ʱ��Ҫ����Ʒ��" )
		if self._describe == "":
			self._describe = cschannel_msgs.SHI_TU_GIFT_VOICE_5

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if not player.hasShiTuRelation():
			# ���û��ʦͽ��ϵ,��ʾ����������ʦͽ��ϵ���޷���ȡ������
			player.setGossipText( cschannel_msgs.SHI_TU_GIFT_VOICE_19 )
			player.sendGossipComplete( talkEntity.id )
			return

		items = []
		for itemID in self._reqireItems:
			item = player.findItemFromNKCK_( int( itemID ) )
			if not item:
				player.setGossipText( cschannel_msgs.SHI_TU_GIFT_VOICE_7 % getItemName( itemID ) )
				player.sendGossipComplete( talkEntity.id )
				return
			items.append( item )
		for item in items:
			player.removeItem_( item.order, 1, csdefine.DELETE_ITEM_SHITUREWARD )	# �Ƴ����������Ʒ
		player.spellTarget( self._skillID, player.id )
		player.setGossipText( self._describe )
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



class FuncShiTuChouJiang( Function ):
	"""
	ʦͽ�ػ��齱
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._rewards = {}								# ��������Ʒ�ֵ�
		self._p1 = section.readString( "param1" )		# ��Ҫ����Ʒ itemId1|itemId2|itemId3 ������
		self._p2 = section.readInt( "param2" )			# ÿ����Գ齱�Ĵ���
		self._p3 = section.readString( "param3" )		# ��������NPC�ĶԻ�
		self._describe = section.readString( "param4" )	# ����֮��Ķ԰�
		rewardStr = section.readString( "param5" )		# ��������Ʒ��(��ʽΪ��ID1:����1:����1|ID2:����2:����2)
		tempList = rewardStr.split('|')
		tempRate = 0
		for i in tempList:
			tempData = i.split(":")
			itemID = int( tempData[0] )
			itemAmount = int( tempData[1] )
			tempRate += int( float( tempData[2] ) * 100000 )
			self._rewards[tempRate] = ( itemID, itemAmount )
		if self._describe == "":
			self._describe = cschannel_msgs.SHI_TU_GIFT_VOICE_8
		self._reqireItems = self._p1.split( '|' )		# ��Ҫ����ƷID���� type:str
		if len( self._reqireItems ) == 0:
			ERROR_MSG( "û��������ȡ����ʱ��Ҫ����Ʒ��" )

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if not player.shiTuChouJiangDailyRecord.checklastTime():			# �ж��Ƿ�ͬһ��
			player.shiTuChouJiangDailyRecord.reset()
		if player.shiTuChouJiangDailyRecord.getDegree() >= self._p2:		# �жϴ���
			player.setGossipText( self._p3 )
			player.sendGossipComplete( talkEntity.id )
			return

		items = []
		for itemID in self._reqireItems:
			item = player.findItemFromNKCK_( int( itemID ) )
			if not item:
				player.setGossipText( cschannel_msgs.SHI_TU_GIFT_VOICE_9 % getItemName( itemID ) )
				player.sendGossipComplete( talkEntity.id )
				return
			items.append( item )
		for item in items:
			player.removeItem_( item.order, 1, csdefine.DELETE_ITEM_SHITUCHOUJIANG )	# �Ƴ����������Ʒ

		self.rewardPlayer( player )
		player.shiTuChouJiangDailyRecord.incrDegree()
		player.setGossipText( self._describe )
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

	def rewardPlayer( self, player ):
		"""
		�������
		"""
		itemID = 0
		itemAmount = 0
		b = random.random()# ����һ��0.0��1.0�������
		l = self._rewards.keys()
		l.sort()
		for key in l:
			if b <= ( key / 100000.0 ):
				itemData = self._rewards[key]
				itemID = itemData[0]
				itemAmount = itemData[1]
				break
		item = g_items.createDynamicItem( itemID, itemAmount )
		if item is None:
			ERROR_MSG( "��Ʒ[%i]������" % itemID )
			return
		kitbagState = player.checkItemsPlaceIntoNK_( [ item ] )
		if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
			# �����ռ䲻��װ
			player.statusMessage( csstatus.CIB_MSG_ITEMBAG_SPACE_NOT_ENOUGH )
		else:
			player.addItem( item, csdefine.ADD_ITEM_SHITUCHOUJIANG )


class FuncChuShiReward( Function ):
	"""
	ʦͽ�ػ�30��45����ʦ����(������ͽ������ȡ)
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._p1 = section.readInt( "param1" )		# ��ʦ����
		self._p2 = section.readInt( "param2" )		# ʦ����õ���Ʒ��ID
		self._p3 = section.readInt( "param3" )		# ͽ�ܻ�õ���Ʒ1��ID
		self._p4 = section.readInt( "param4" )		# ͽ�ܻ�õ���Ʒ2��ID(ͽ���п��ܻ�ò�ͬ����Ʒ)
		self._p5 = section.readInt( "param5" )		# ʦ����õľ���ֵ

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if not player.hasShiTuRelation():
			# ���û��ʦͽ��ϵ,��ʾ����������ʦͽ��ϵ���޷���ȡ������
			player.setGossipText( cschannel_msgs.SHI_TU_GIFT_VOICE_19 )
			player.sendGossipComplete( talkEntity.id )
			return

		teamMembers = player.getTeamMemberIDs()[:]
		if len( teamMembers ) != 2:
			# ����ֻ��ʦͽ������ӣ�������ʾ������ȡ
			player.setGossipText( cschannel_msgs.SHI_TU_GIFT_VOICE_11 )
			player.sendGossipComplete( talkEntity.id )
			return

		if not player.iAmMaster():
			# �������ʦ��
			player.setGossipText( cschannel_msgs.SHI_TU_GIFT_VOICE_12 )
			player.sendGossipComplete( talkEntity.id )
			return

		teamMembers.remove( player.id )
		prentice = BigWorld.entities.get( teamMembers[0] )
		if prentice is None or not player.isPrentice( prentice.databaseID ) \
			or prentice.spaceID != player.spaceID \
			or player.distanceBB( prentice ) > ENTERN_SHITU_MENBER_DISTANCE:
			# �������ͽ�ܻ���ͽ�ܲ������20����
			player.setGossipText( cschannel_msgs.SHI_TU_GIFT_VOICE_13 )
			player.sendGossipComplete( talkEntity.id )
			return

		if prentice.level < self._p1:
			# ͽ�ܼ��𲻹���ȡ
			player.setGossipText( cschannel_msgs.SHI_TU_GIFT_VOICE_14 % self._p1 )
			player.sendGossipComplete( talkEntity.id )
			return

		if prentice.chuShiRewardRecord >= self._p1:
			# ����Ѿ���ȡ����ʦ������
			player.setGossipText( cschannel_msgs.SHI_TU_GIFT_VOICE_15 )
			player.sendGossipComplete( talkEntity.id )
			return

		duDiItem = None
		shifuItem = g_items.createDynamicItem( self._p2 )
		a = random.random()
		if a > 0.5:
			duDiItem = g_items.createDynamicItem( self._p3 )
		else:
			duDiItem = g_items.createDynamicItem( self._p4 )

		if shifuItem is None or duDiItem is None:
			ERROR_MSG( "��Ʒ[%i]��[%i]������" % ( self._p2, self._p3 ) )
			return

		kitbagState1 = player.checkItemsPlaceIntoNK_( [ shifuItem ] )
		kitbagState2 = prentice.checkItemsPlaceIntoNK_( [ duDiItem ] )
		if  kitbagState1 == csdefine.KITBAG_NO_MORE_SPACE:
			# �����ռ䲻��װ
			player.setGossipText( cschannel_msgs.SHI_TU_GIFT_VOICE_16 )
			player.sendGossipComplete( talkEntity.id )
			return
		if  kitbagState2 == csdefine.KITBAG_NO_MORE_SPACE:
			# �����ռ䲻��װ
			player.setGossipText( cschannel_msgs.SHI_TU_GIFT_VOICE_17 )
			player.sendGossipComplete( talkEntity.id )
			return
		else:
			player.addItem( shifuItem, csdefine.ADD_ITEM_CHUSHIREWARD  )
			prentice.addItem( duDiItem, csdefine.ADD_ITEM_CHUSHIREWARD )
			prentice.chuShiRewardRecord = self._p1
			player.addExp( self._p5, csdefine.CHANGE_EXP_CHUSHIREWARD )
			player.setGossipText( cschannel_msgs.SHI_TU_GIFT_VOICE_18 % self._p1 )
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