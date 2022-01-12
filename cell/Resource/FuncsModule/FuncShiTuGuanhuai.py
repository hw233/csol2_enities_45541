# -*- coding: gb18030 -*-
"""
采集贝壳的对话 2009-01-14 SongPeifang
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
	获取物品的名称
	"""
	itemNames = { 50101064:cschannel_msgs.SHI_TU_GIFT_VOICE_0, 50101065:cschannel_msgs.SHI_TU_GIFT_VOICE_1, 50101066:cschannel_msgs.SHI_TU_GIFT_VOICE_2, 50101067:cschannel_msgs.SHI_TU_GIFT_VOICE_3 }
	try:
		return itemNames[ int( key ) ]
	except KeyError:
		ERROR_MSG( "师徒关怀物品出错，没有ID为'%s'的物品。" % key )
		return cschannel_msgs.SHI_TU_GIFT_VOICE_4


class FuncShiTuReward( Function ):
	"""
	师徒关怀换取奖励
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._p1 = section.readString( "param1" )		# 需要的物品 itemId1|itemId2|itemId3 。。。
		self._skillID = section.readInt( "param2" )		# 产生的技能ID(因为奖励的是一个buff)
		self._describe = section.readString( "param3" )	# 领取后的描述
		self._reqireItems = self._p1.split( '|' )		# 需要的物品ID数组 type:str
		if len( self._reqireItems ) == 0:
			ERROR_MSG( "没有配置领取奖励时需要的物品。" )
		if self._describe == "":
			self._describe = cschannel_msgs.SHI_TU_GIFT_VOICE_5

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if not player.hasShiTuRelation():
			# 如果没有师徒关系,提示“您不具有师徒关系，无法领取奖励”
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
			player.removeItem_( item.order, 1, csdefine.DELETE_ITEM_SHITUREWARD )	# 移除掉所需的物品
		player.spellTarget( self._skillID, player.id )
		player.setGossipText( self._describe )
		player.sendGossipComplete( talkEntity.id )
		Function.do( self, player, talkEntity )

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True



class FuncShiTuChouJiang( Function ):
	"""
	师徒关怀抽奖
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._rewards = {}								# 奖励的物品字典
		self._p1 = section.readString( "param1" )		# 需要的物品 itemId1|itemId2|itemId3 。。。
		self._p2 = section.readInt( "param2" )			# 每天可以抽奖的次数
		self._p3 = section.readString( "param3" )		# 超过次数NPC的对话
		self._describe = section.readString( "param4" )	# 奖励之后的对白
		rewardStr = section.readString( "param5" )		# 奖励的物品表(格式为：ID1:概率1:数量1|ID2:概率2:数量2)
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
		self._reqireItems = self._p1.split( '|' )		# 需要的物品ID数组 type:str
		if len( self._reqireItems ) == 0:
			ERROR_MSG( "没有配置领取奖励时需要的物品。" )

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if not player.shiTuChouJiangDailyRecord.checklastTime():			# 判断是否同一天
			player.shiTuChouJiangDailyRecord.reset()
		if player.shiTuChouJiangDailyRecord.getDegree() >= self._p2:		# 判断次数
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
			player.removeItem_( item.order, 1, csdefine.DELETE_ITEM_SHITUCHOUJIANG )	# 移除掉所需的物品

		self.rewardPlayer( player )
		player.shiTuChouJiangDailyRecord.incrDegree()
		player.setGossipText( self._describe )
		player.sendGossipComplete( talkEntity.id )
		Function.do( self, player, talkEntity )

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True

	def rewardPlayer( self, player ):
		"""
		奖励玩家
		"""
		itemID = 0
		itemAmount = 0
		b = random.random()# 产生一个0.0—1.0的随机数
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
			ERROR_MSG( "物品[%i]不存在" % itemID )
			return
		kitbagState = player.checkItemsPlaceIntoNK_( [ item ] )
		if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
			# 背包空间不够装
			player.statusMessage( csstatus.CIB_MSG_ITEMBAG_SPACE_NOT_ENOUGH )
		else:
			player.addItem( item, csdefine.ADD_ITEM_SHITUCHOUJIANG )


class FuncChuShiReward( Function ):
	"""
	师徒关怀30和45级出师奖励(必须由徒弟来领取)
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._p1 = section.readInt( "param1" )		# 出师级别
		self._p2 = section.readInt( "param2" )		# 师傅获得的物品的ID
		self._p3 = section.readInt( "param3" )		# 徒弟获得的物品1的ID
		self._p4 = section.readInt( "param4" )		# 徒弟获得的物品2的ID(徒弟有可能获得不同的物品)
		self._p5 = section.readInt( "param5" )		# 师傅获得的经验值

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if not player.hasShiTuRelation():
			# 如果没有师徒关系,提示“您不具有师徒关系，无法领取奖励”
			player.setGossipText( cschannel_msgs.SHI_TU_GIFT_VOICE_19 )
			player.sendGossipComplete( talkEntity.id )
			return

		teamMembers = player.getTeamMemberIDs()[:]
		if len( teamMembers ) != 2:
			# 必须只有师徒二人组队，否则提示不能领取
			player.setGossipText( cschannel_msgs.SHI_TU_GIFT_VOICE_11 )
			player.sendGossipComplete( talkEntity.id )
			return

		if not player.iAmMaster():
			# 如果不是师傅
			player.setGossipText( cschannel_msgs.SHI_TU_GIFT_VOICE_12 )
			player.sendGossipComplete( talkEntity.id )
			return

		teamMembers.remove( player.id )
		prentice = BigWorld.entities.get( teamMembers[0] )
		if prentice is None or not player.isPrentice( prentice.databaseID ) \
			or prentice.spaceID != player.spaceID \
			or player.distanceBB( prentice ) > ENTERN_SHITU_MENBER_DISTANCE:
			# 如果不是徒弟或者徒弟不在身边20米内
			player.setGossipText( cschannel_msgs.SHI_TU_GIFT_VOICE_13 )
			player.sendGossipComplete( talkEntity.id )
			return

		if prentice.level < self._p1:
			# 徒弟级别不够领取
			player.setGossipText( cschannel_msgs.SHI_TU_GIFT_VOICE_14 % self._p1 )
			player.sendGossipComplete( talkEntity.id )
			return

		if prentice.chuShiRewardRecord >= self._p1:
			# 如果已经领取过出师奖励了
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
			ERROR_MSG( "物品[%i]或[%i]不存在" % ( self._p2, self._p3 ) )
			return

		kitbagState1 = player.checkItemsPlaceIntoNK_( [ shifuItem ] )
		kitbagState2 = prentice.checkItemsPlaceIntoNK_( [ duDiItem ] )
		if  kitbagState1 == csdefine.KITBAG_NO_MORE_SPACE:
			# 背包空间不够装
			player.setGossipText( cschannel_msgs.SHI_TU_GIFT_VOICE_16 )
			player.sendGossipComplete( talkEntity.id )
			return
		if  kitbagState2 == csdefine.KITBAG_NO_MORE_SPACE:
			# 背包空间不够装
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
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True