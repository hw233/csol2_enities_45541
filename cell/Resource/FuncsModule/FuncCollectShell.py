# -*- coding: gb18030 -*-
"""
采集贝壳的对话 2009-01-14 SongPeifang
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
	祈求海神赐福
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._p1 = section.readString( "param1" )	# 需要的物品 itemId1|itemId2|itemId3|itemId4|itemId5
		self._p2 = section.readInt( "param2" )		# 每天可以进行的次数
		self._p3 = section.readInt( "param3" )		# 获得的物品奖励
		self._p4 = section.readInt( "param4" )		# 奖励的物品的个数
		self._reqireItems = self._p1.split( '|' )	# 需要的物品ID数组 type:str
		if len( self._reqireItems ) == 0:
			ERROR_MSG( "祈求海神赐福对话配置错误！" )

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if not player.cifuRecord.checklastTime():
			# 过了一天清除海神赐福次数记录
			player.cifuRecord.reset()

		if player.cifuRecord._degree >= self._p2:
			# 超过每天可以免费领取的次数了
			player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_0 % self._p2 )
			player.sendGossipComplete( talkEntity.id )
			return

		rwdItem = g_items.createDynamicItem( self._p3, self._p4 )
		kitbagState = player.checkItemsPlaceIntoNK_( [ rwdItem ] )
		if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
			# 背包空间不够
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
			player.removeItem_( item.order, 1, csdefine.DELETE_ITEM_CIFU )	# 移除掉所需的物品

		rwdItem.setBindType( ItemTypeEnum.CBT_PICKUP, player )
		player.addItemAndNotify_( rwdItem, csdefine.ADD_ITEM_CIFU )
		player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_3 )
		player.cifuRecord.incrDegree()
		player.sendGossipComplete( talkEntity.id )
		Function.do( self, player, talkEntity )
		
		g_logger.actJoinLog( csdefine.ACTIVITY_TIAN_CI_QI_FU, csdefine.ACTIVITY_JOIN_ROLE, player.databaseID, player.getName() )

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


class FuncXianLing( Function ):
	"""
	祈求龙王显灵
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._p1 = section.readString( "param1" )	# 需要的物品 itemId1|itemId2|itemId3|itemId4|itemId5
		self._p2 = section.readInt( "param2" )		# 每天可以进行的次数
		self._p3 = section.readInt( "param3" )		# 奖励的物品ID
		self._p4 = section.readInt( "param4" )		# 奖励的物品个数
		self._reqireItems = self._p1.split( '|' )	# 需要的物品ID数组 type:str
		if len( self._reqireItems ) == 0:
			ERROR_MSG( "祈求龙王显灵对话配置错误！" )

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if not player.xianlingRecord.checklastTime():
			# 过了一天清除龙王显灵次数记录
			player.xianlingRecord.reset()

		if player.xianlingRecord._degree >= self._p2:
			# 超过每天龙王显灵的次数了
			player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_4 % self._p2 )
			player.sendGossipComplete( talkEntity.id )
			return

		rwdItem = g_items.createDynamicItem( self._p3, self._p4 )
		kitbagState = player.checkItemsPlaceIntoNK_( [ rwdItem ] )
		if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
			# 背包空间不够
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
			player.removeItem_( item.order, 1, csdefine.DELETE_ITEM_XIANLING )	# 移除掉所需的物品

		rwdItem.setBindType( ItemTypeEnum.CBT_PICKUP, player )
		player.addItemAndNotify_( rwdItem, csdefine.ADD_ITEM_XIANLING )
		player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_7 )
		player.xianlingRecord.incrDegree()
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


class FuncJianZheng( Function ):
	"""
	龙王见证情缘
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._p1 = section.readString( "param1" )			# 需要的物品 itemId1|itemId2
		self._p2 = section.readInt( "param2" )				# 可以玩的次数
		self._p3 = section.readInt( "param3" )				# 奖励给玩家的物品ID
		self._p4 = section.readInt( "param4" )				# 奖励的物品个数
		self._memberDistance = section.readInt( "param5" )	# 队员需要在多远的距离内才算是完成
		self._reqireItems = self._p1.split( '|' )			# 需要的物品ID数组 type:str
		if len( self._reqireItems ) == 0:
			ERROR_MSG( "龙王见证情缘对话配置错误！" )

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
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
			# 过了一天清除见证情缘次数记录
			player.jianZhengRecord.reset()
		if not player2.jianZhengRecord.checklastTime():
			# 过了一天清除见证情缘次数记录
			player2.jianZhengRecord.reset()

		if player.jianZhengRecord._degree >= self._p2:
			# 超过每天可以见证情缘的次数了
			player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_10 % self._p2 )
			player.sendGossipComplete( talkEntity.id )
			return
		elif player2.jianZhengRecord._degree >= self._p2:
			# 超过每天可以见证情缘的次数了
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
			# 玩家1背包空间不够
			player.setGossipText( cschannel_msgs.BIAN_SHEN_VOICE_7 )
			player.sendGossipComplete( talkEntity.id )
			return
		elif kitbagState2 == csdefine.KITBAG_NO_MORE_SPACE:
			# 玩家2背包空间不够
			player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_14 % player2.getName() )
			player.sendGossipComplete( talkEntity.id )
			return

		#player.base.chat_sysBroadcast( "%s和%s在龙王神的指引下千里相会，祝福他们友谊长存！" % ( player.getName(), player2.getName() )  )
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
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True


class FuncPearlPrime( Function ):
	"""
	吸取珍珠精华
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._itemID = section.readInt( "param1" )		# 需要的物品ID
		formulaStr = section.readString( "param2" )		# 每次可以获得的经验的公式 lv+23
		self._playTimes = section.readInt( "param3" )	# 每天可以玩的次数
		self._hpVal = 23	#int( formulaStr[ 3:len( formulaStr ) ] )	# 增加的经验值
		self._hpOpt = "+"	#formulaStr[ 2:3 ]							# 操作符

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if not player.pearlPrimeRecord.checklastTime():
			# 过了一天清除吸取珍珠精华次数记录
			player.pearlPrimeRecord.reset()

		if player.pearlPrimeRecord._degree >= self._playTimes:
			# 超过每天吸取珍珠精华的次数了
			player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_16 % self._playTimes )
			player.sendGossipComplete( talkEntity.id )
			return

		item = player.findItemFromNKCK_( self._itemID )
		if not item:
			player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_17 )
			player.sendGossipComplete( talkEntity.id )
			return
		player.removeItem_( item.order, 1, csdefine.DELETE_ITEM_PEARLPRIME )	# 移除掉所需的物品
		increaseEXP = self.getIncreaseEXP( player.level, self._hpOpt, self._hpVal )
		player.addExp( increaseEXP, csdefine.CHANGE_EXP_PEARLPRIME )
		player.pearlPrimeRecord.incrDegree()
		player.setGossipText( cschannel_msgs.CAI_JI_ZHEN_ZHU_VOICE_18 )
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

	def getIncreaseEXP( self, level, opration, value ):
		"""
		根据公式获得增加的Exp
		"""
		# 暂时把公式写死 （level + value ）*10
		return ( level + value ) * 10