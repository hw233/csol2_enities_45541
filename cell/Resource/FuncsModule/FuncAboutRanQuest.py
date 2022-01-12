# -*- coding: gb18030 -*-
#
# $Id: FuncAboutRanQuest.py,v 1.8 2008-08-15 09:16:45 zhangyuxing Exp $

"""
"""
from Function import Function
import cschannel_msgs
import ShareTexts as ST
import csdefine
import csstatus
from bwdebug import *
import time

class FuncRecordRanQuest( Function ):
	"""
	记录随机任务
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.param1 = section['param1'].asInt
		self.param2 = section['param2'].asInt
		self.param3 = section['param3'].asInt

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		npc = talkEntity.getScript()

		if player.recordQuestsRandomLog.has_randomQuestGroup( self.param1 ):
			player.setGossipText( cschannel_msgs.LOOP_QUEST_VOICE_1 )
			player.sendGossipComplete( talkEntity.id )
			return

		quest = player.getQuest(self.param1)
		if quest.query( player ) not in [csdefine.QUEST_STATE_NOT_FINISH, csdefine.QUEST_STATE_FINISH]:
			player.endGossip( talkEntity )
			player.statusMessage( csstatus.ROLE_NO_RANDOM_QUEST_NOT_SAVE )
			return


		if quest.isTimeOut( player, self.param1 ):
			player.endGossip( talkEntity )
			player.statusMessage( csstatus.ROLE_RANDOM_QUEST_TIME_OUT_NOT_SAVE )
			return

		items = player.findItemsByIDFromNKCK( self.param2 )
		if items == []:
			player.endGossip( talkEntity )
			player.statusMessage( csstatus.ROLE_QUEST_NO_RANDOM_SAVE_ITEM )
			return
		player.removeItem_( items[0].order, self.param3, csdefine.DELETE_ITEM_RECORDRANQUEST )
		player.recordRandomQuest( self.param1 )
		player.setGossipText( cschannel_msgs.LOOP_QUEST_VOICE_2 )
		player.sendGossipComplete( talkEntity.id )
		player.abandonQuest( player.id, self.param1 )
		#player.endGossip( talkEntity )


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
		quest = player.getQuest(self.param1)
		return quest.query( player ) in [csdefine.QUEST_STATE_NOT_FINISH, csdefine.QUEST_STATE_FINISH]


class FuncCancelRanQuest( Function ):
	"""
	放弃随机任务
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		npc = talkEntity.getScript()
		questID = 0
		for id in npc._questStartList:
			questID = id
		if not player.has_quest( questID ): return
		player.questRemove( questID, 1 )

		player.getQuest( questID ).abandoned( player, csdefine.QUEST_REMOVE_FLAG_NPC_CHOOSE )
		player.questRemove( questID, True )
		player.onQuestBoxStateUpdate( )

		player.endGossip( talkEntity )

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

class FuncReadRanQuest( Function ):
	"""
	读取随机任务记录
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.param1 = section['param1'].asInt		#任务ID


	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		npc = talkEntity.getScript()

		quest = player.getQuest( self.param1 )
		if quest.query( player ) in [csdefine.QUEST_STATE_NOT_FINISH, csdefine.QUEST_STATE_FINISH]:
			player.statusMessage( csstatus.ROLE_HAS_RANDOM_QUEST_CANT_READ )
			return

		player.client.readRandomQuestRecord( self.param1 )
		#player.readRandomQuestRecord( self.param1 )
		#player.delRandomQuestRecord( self.param1 )


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
		return player.recordQuestsRandomLog.has_randomQuestGroup( self.param1 )




class FuncReAcceptLoopQuest( Function ):
	"""
	重新接取环任务的对话
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._minLevel = section.readInt( "param1" )	# 接任务的最低级别
		self._maxLevel = section.readInt( "param2" )	# 接任务的最高级别
		self._questID = section.readInt( "param3" )		# 环任务的任务ID

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		所需要经验的计算公式:等级*300*环数^1.2

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if player.iskitbagsLocked():	# 背包上锁，by姜毅
			player.endGossip( talkEntity )
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		quest = player.getQuest( self._questID )
		if quest == None:
			ERROR_MSG( "No such quest, config error! questID is: %s" % self._questID )
			return
		if quest.query( player ) in [csdefine.QUEST_STATE_NOT_FINISH, csdefine.QUEST_STATE_FINISH]:
			player.endGossip( talkEntity )
			player.statusMessage( csstatus.ROLE_HAS_RANDOM_QUEST_CANT_ACCEPT )
			return

		money = int( ( player.level * 300 * ( player.getGroupQuestCount( self._questID ) + 1 ) ) ** 1.2 )

		if player.money < money:
			player.endGossip( talkEntity )
			player.statusMessage( csstatus.ROLE_HAS_NOT_ENOUGH_MONEY_ACCEPT, money/10000, money%10000/100 )
			return

		moneyStr = self.convertPrice( money )
		msgStr = cschannel_msgs.LOOP_QUEST_VOICE_3 % moneyStr
		player.client.acceptQuestConfirm( self._questID, msgStr )
		#player.payMoney( money, csdefine.CHANGE_MONEY_REACCEPTLOOPQUEST )
		#quest.accept( player )
		player.endGossip( talkEntity )

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
		levelValid = ( player.level >= self._minLevel and player.level <= self._maxLevel )
		alreadyHasQuest = self._questID in player.questsTable.keys()
		reAcceptValid = False
		for i in player.failedGroupQuestList:
			if str( self._questID ) == i.split(':')[1] and i.split(':')[0] == str( time.localtime()[2] ):
				reAcceptValid = True
		alreadyStored = player.recordQuestsRandomLog.has_randomQuestGroup( self._questID )

		return levelValid and reAcceptValid and not alreadyHasQuest and not alreadyStored

	def convertPrice( self, price ):
		"""
		转换价格，把诸如“10102”形式的价格转换成“1金1银2铜”
		"""
		gold = price / 10000
		silver = price / 100 - gold * 100
		coin = price - gold * 10000 - silver * 100
		goldStr = ""
		silverStr = ""
		coinStr	= ""
		if gold != 0:
			goldStr = str( gold ) + cschannel_msgs.LOOP_QUEST_INFO_1
		if silver != 0:
			silverStr = str( silver ) + cschannel_msgs.LOOP_QUEST_INFO_2
		if coin != 0:
			coinStr = str( coin ) + cschannel_msgs.LOOP_QUEST_INFO_3

		return goldStr + silverStr + coinStr