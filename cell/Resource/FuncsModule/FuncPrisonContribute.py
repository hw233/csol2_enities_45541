# -*- coding: gb18030 -*-
#
# $Id:  $

"""
"""
from Function import Function
import cschannel_msgs
import ShareTexts as ST
import BigWorld
import csconst
import csdefine
import csstatus


def switchMoney( money ):
	"""
	转换货币显示形式 由于该函数适用范围比较广 根据柯大侠的建议 在这里增加公共接口 by姜毅
	"""
	if money <= 0: return "0"
	gold = int( money / 10000 )
	silver = int( ( money % 10000 ) / 100 )
	coin = int( ( money % 10000 ) % 100 )
	moneyText = ""
	if gold > 0: moneyText += cschannel_msgs.ON_LINE_GIFT_INFO_1 % gold
	if silver > 0: moneyText += cschannel_msgs.ON_LINE_GIFT_INFO_2 % silver
	if coin > 0: moneyText += cschannel_msgs.ON_LINE_GIFT_INFO_3 % coin
	return moneyText

class FuncPrisonContribute( Function ):
	"""
	监狱捐献
	"""
	def __init__( self, section ):
		"""
		param1: CLASS_*

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
		player.endGossip( talkEntity )
		if player.iskitbagsLocked():	# 背包上锁，by姜毅
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return

		money = 0
		lv = player.level

		for item in csconst.PRISON_CONTRIBUTE_DATAS:
			if lv <= item[ 1 ]:
				money = item[ 2 ]
				break

		if player.money < money:
			player.statusMessage( csstatus.PRISON_CONTRIBUTE_VALID, switchMoney( money ) )
			return

		player.client.onPrisonContributeSure( money )

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
		return player.pkValue > 0
