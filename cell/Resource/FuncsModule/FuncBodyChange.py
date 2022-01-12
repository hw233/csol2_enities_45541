# -*- coding: gb18030 -*-
#
"""
 变身大赛的对话 2009-01-17 SongPeifang
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
	报名参加变身大赛
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._p1 = section.readString( "param1" )	# 要发放及删除的纸牌物品 itemId1|itemId2|itemId3|itemId4|itemId5
		self._reqireItems = self._p1.split( '|' )	# 需要的物品ID数组 type:str
		if len( self._reqireItems ) == 0:
			ERROR_MSG( "变身大赛报名对话参数配置错误！" )

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if talkEntity == None:
			ERROR_MSG( "未知错误，找不到变身大赛的NPC。" )
			return

		if not talkEntity.canLogin():
			# 报名已经结束
			player.setGossipText( cschannel_msgs.BIAN_SHEN_VOICE_1 )
			player.sendGossipComplete( talkEntity.id )
			return

		if talkEntity.isPlayerLogin( player ):
			# 玩家已经报名过了
			player.setGossipText( cschannel_msgs.BIAN_SHEN_VOICE_2 )
			player.sendGossipComplete( talkEntity.id )
			for i in self._reqireItems:
				card = player.findItemFromNKCK_( int(i) )	# 判断是否已经有纸牌了
				if card == None:
					card = player.createDynamicItem( int(i) )
					player.addItemAndNotify_( card, csdefine.ADD_ITEM_LOGINBCGAME )
			return
			
		if player.iskitbagsLocked():	# 背包上锁，by姜毅
			player.endGossip( talkEntity )
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return

		if player.getNormalKitbagFreeOrderCount() < len( self._reqireItems ):
			# 背包空间不够不能报名
			player.setGossipText( cschannel_msgs.BIAN_SHEN_VOICE_3 % len( self._reqireItems ) )
			player.sendGossipComplete( talkEntity.id )
			return

		for i in self._reqireItems:
			card = player.findItemFromNKCK_( int(i) )	# 判断是否已经有纸牌了
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
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True

class FuncBCReward( Function ):
	"""
	领取变身大赛奖励
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.itemID = section.readInt( "param1" )	# 奖励的物品ID
		self.sunBathCount = section.readInt( "param2" )	# 奖励的日光浴时间（秒）
		self._p3 = section.readString( "param3" )	# 要发放及删除的纸牌物品 itemId1|itemId2|itemId3|itemId4|itemId5
		self.sunBathMaxCount = section.readInt( "param4" )	# 每天晒的日光浴最多时间（秒）
		self._reqireItems = self._p3.split( '|' )	# 需要的物品ID数组 type:str
		if len( self._reqireItems ) == 0:
			ERROR_MSG( "领取变身奖励对话参数配置错误！" )

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if talkEntity == None:
			ERROR_MSG( "未知错误，找不到变身大赛的NPC。" )
			return

		if talkEntity.canLogin() or talkEntity.hasMembers():
			# 不能在比赛中领取奖励
			player.setGossipText( cschannel_msgs.BIAN_SHEN_VOICE_5 )
			player.sendGossipComplete( talkEntity.id )
			return

		for i in self._reqireItems:
			card = player.findItemFromNKCK_( int(i) )	# 判断是否已经有纸牌了
			if card != None:
				player.removeItem_( card.order, reason = csdefine.DELETE_ITEM_BCREWARD )	# 移除掉玩家身上的纸牌

		if not player.databaseID in talkEntity._passMembers:
			# 不能领取奖励
			player.setGossipText( cschannel_msgs.BIAN_SHEN_VOICE_6 )
			player.sendGossipComplete( talkEntity.id )
			return

		if self.itemID != 0:
			item = player.createDynamicItem( self.itemID )
			kitbagState = player.checkItemsPlaceIntoNK_( [item] )
			if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
				# 背包空间不够
				player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
				player.setGossipText( cschannel_msgs.BIAN_SHEN_VOICE_7 )
				player.sendGossipComplete( talkEntity.id )
				return
			player.addItemAndNotify_( item, csdefine.ADD_ITEM_BCREWARD )

		#player.updateSunBathCount( 0 - self.sunBathCount )
		#leftSunBathTime = ( self.sunBathMaxCount - player.sunBathDailyRecord.sunBathCount ) / 60	# 分钟
		#player.setGossipText( "@S{4}你的合法日光浴时间增加了30分钟，你当前还剩下%s分钟的日光浴时间。" % leftSunBathTime )
		player.setGossipText( cschannel_msgs.BIAN_SHEN_VOICE_8 )
		talkEntity.clearPassMembers( player )
		player.sendGossipComplete( talkEntity.id )

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