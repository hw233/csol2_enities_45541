# -*- coding: gb18030 -*-
#
"""
钓鱼的对话 2009-06-10 SongPeifang
"""

from bwdebug import *
import cschannel_msgs
import ShareTexts as ST
from Function import Function
from SkillTargetObjImpl import createTargetObjEntity
import csdefine
import csstatus

class FuncFishingForFree( Function ):
	"""
	免费领取钓鱼时间
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._p1 = section.readInt( "param1" )		# 每次可以领取的时间
		self._p2 = section.readInt( "param2" )		# 每天可以领取的次数
		self._p3 = section.readString( "param3" )	# 超过领取次数的对白
		self._p4 = section.readInt( "param4" )		# 领取钓鱼时间的技能ID

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		Function.do( self, player, talkEntity )

		if not player.fishingRecord.checklastTime():
			# 过了一天清除钓鱼时间领取次数记录
			player.fishingRecord.reset()

		if player.fishingRecord._degree >= self._p2:
			# 超过每天可以免费领取的次数了
			player.setGossipText( self._p3 )
			player.sendGossipComplete( talkEntity.id )
			return

		target = createTargetObjEntity( player )
		if player.intonating():
			# 玩家正在释放技能的时候不能领取
			player.setGossipText( cschannel_msgs.FISHING_VOICE_1 )
			player.sendGossipComplete( talkEntity.id )
			return

		talkEntity.spellTarget( self._p4, player.id )
		player.fishingRecord.incrDegree()
		minutes = self._p1 / 60
		player.setGossipText( cschannel_msgs.FISHING_VOICE_2 % minutes )
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


class FuncFishingInCharge( Function ):
	"""
	用渔场垂钓卡换取钓鱼时间
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._p1 = section.readInt( "param1" )		# 每次可以领取的时间
		self._p2 = section.readInt( "param2" )		# 换取时需要的物品ID
		self._p3 = section.readInt( "param3" )		# 领取钓鱼时间的技能ID

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		Function.do( self, player, talkEntity )

		item = player.findItemFromNKCK_( self._p2 )
		if not item:
			player.setGossipText( cschannel_msgs.FISHING_VOICE_3 )
			player.sendGossipComplete( talkEntity.id )
			return

		target = createTargetObjEntity( player )
		if player.intonating():
			# 玩家正在释放技能的时候不能领取
			player.setGossipText( cschannel_msgs.FISHING_VOICE_1 )
			player.sendGossipComplete( talkEntity.id )
			return

		talkEntity.spellTarget( self._p3, player.id )
		player.removeItem_( item.order, 1, csdefine.DELETE_ITEM_FISHINGINCHARGE )	# 移除掉所需的物品
		minutes = self._p1 / 60
		player.setGossipText( cschannel_msgs.FISHING_VOICE_2 % minutes )
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