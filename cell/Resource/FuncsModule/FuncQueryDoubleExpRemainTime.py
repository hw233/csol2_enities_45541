# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
"""
from Function import Function
import cschannel_msgs
import ShareTexts as ST
import csdefine
import BigWorld
import csstatus
import csconst
import time

datamap = {
	100 : cschannel_msgs.ON_LINE_GIFT_INFO_4,
	200 : cschannel_msgs.KE_JU_SHUANG,
	300 : cschannel_msgs.KE_JU_SAN,
	400 : cschannel_msgs.KE_JU_SI,
	500 : cschannel_msgs.KE_JU_WU,
	600 : cschannel_msgs.KE_JU_LIU,
	700 : cschannel_msgs.KE_JU_QI,
	800 : cschannel_msgs.KE_JU_BA,
	900 : cschannel_msgs.KE_JU_JIU,
	1000 : cschannel_msgs.KE_JU_SHI,
}

class FuncQueryDoubleExpRemainTime( Function ):
	"""
	查询双倍奖励剩余时间
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		week = player.takeExpRecord[ "week" ]
		lastTime = player.takeExpRecord[ "lastTime" ]
		remainTime = player.takeExpRecord[ "remainTime" ]
		t = time.localtime()
		week1 = t[6]
		"""
		计算方式， 得出上一次记录的时间是 礼拜几然后得出距离礼拜天的时间，
		然后用今天的时间减去上次记录的时间 得出的时间如果大于距离礼拜天的时间则表明
		一个星期已经过去 wrriten by kebiao.
		"""
		# 得到上一次记录时间到晚上24点之间的间隔
		lastClock = time.ctime( lastTime ).split()[3].split(":")
		lastDayRemainTime = 24 * 60 * 60 - int( lastClock[0] ) * 60 * 60 - int( lastClock[1] ) * 60 - int( lastClock[2] )

		# 得出上一次时间距离星期天的天数时间
		remainWeekTime = ( 6 - week ) * 60 * 60 * 24
		# 今天的时间-上次领取时间的差值 < 上一次领取距离那次星期天的时间+上一次领取距离晚上24点的时间 则一个星期没有过去
		if ( time.time() - lastTime ) >= remainWeekTime + lastDayRemainTime:
			# 一个星期过了 更新时间
			player.takeExpRecord[ "remainTime" ] = 7
		if player.takeExpRecord[ "remainTime" ] > 0:
			s = datamap[ player.takeExpRecord[ "remainTime" ] * 100 ]
			if player.takeExpRecord[ "remainTime" ] == 2:
				s = cschannel_msgs.KE_JU_ER
			player.statusMessage( csstatus.TAKE_EXP_REMAIN_QUERY,  s )
		else:
			if player.takeExpRecord[ "lastTime" ] > 0:
				player.statusMessage( csstatus.TAKE_EXP_REMAIN_OVER )
			else:
				player.statusMessage( csstatus.TAKE_EXP_REMAIN_QUERY,  cschannel_msgs.KE_JU_QI )
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

