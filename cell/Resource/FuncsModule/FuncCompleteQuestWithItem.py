# -*- coding: gb18030 -*-
#created by dqh
# $Id: Exp $


from Function import Function
import BigWorld
import csdefine
import csstatus
from bwdebug import *

class FuncCompleteQuestWithItem( Function ):
	"""
	完成指定的任务目标后，再给予玩家一个物品
	"""
	def __init__( self, section ):
		"""
		@param param : 由实现类自己解释格式; param1 - param5
		@type  param : pyDataSection
		"""
		Function.__init__( self, section  )
		
		self._itemID = section.readInt( "param1")			# 物品ID
		self._questID = section.readInt( "param2" )			# 任务ID
		self._taskIndex = section.readInt( "param3" )		# 任务目标索引

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player     : 玩家
		@type  player     : Entity
		@param talkEntity : 一个扩展的参数
		@type  talkEntity : entity
		@return           : None
		"""
		player.endGossip( talkEntity )
		
		#添加物品
		item = player.createDynamicItem( self._itemID )
		if item is None:
			ERROR_MSG( "Player(%d):Item(%s) is none, quest(%s) can'be done" % ( player.id, str( self._itemID ), str( self._questID )) )
			return
		checkReult = player.checkItemsPlaceIntoNK_( [item] )
		if checkReult != csdefine.KITBAG_CAN_HOLD:
			player.statusMessage( csstatus.ROLE_QUEST_GET_FU_BI_CANNOT_GET_ITEM )
			return
		player.addItem( item, reason = csdefine.ADD_ITEM_QUEST )
		
		player.questTaskIncreaseState( self._questID, self._taskIndex )

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用
		
		@param player		: 玩家
		@type  player		: Entity
		@param talkEntity	: 一个扩展的参数
		@type  talkEntity	: entity
		@return				: True/False
		@rtype				: bool
		"""
		quest = player.getQuest( self._questID )
		return quest and quest.query( player ) == csdefine.QUEST_STATE_NOT_FINISH	#任务存在且没有完成
		
