# -*- coding: gb18030 -*-
#
# $Id: FuncLevel.py,v 1.1 2008-01-31 05:18:39 kebiao Exp $

"""
"""
from Function import Function
import BigWorld
from csdefine import *		# just for "eval" expediently
import time
import csconst
import csstatus

class FuncTakeExpBuff( Function ):
	"""
	领取经验BUFF 10111224
	"""
	def __init__( self, section ):
		"""
		param1: CLASS_*

		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.skillID = section.readInt( "param1" )  			#技能ID
		self.hour = section.readInt( "param2" )					#奖励经验小时

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if player.takeExpRecord[ "freezeTime" ] > 0:
			# 记录最后冻结的时间
			t = time.time() - player.takeExpRecord[ "freezeTime" ]
			lostTime = 0
			if t > 24 * 60 * 60:
				lostTime = t - 24 * 60 * 60

			buff = player.takeExpRecord[ "freezeBuff" ]
			# 计算BUFF的剩余时间
			buff[ "persistent" ] -= lostTime
			# BUFF是否超时
			if buff[ "persistent" ] <= 0:
				player.endGossip( talkEntity )
				player.takeExpRecord[ "freezeBuff" ] = { "skill" : None, "persistent" : 0, "currTick" : 0, "state" : 0, "caster" : 0, "index" : 0 ,"sourceType":0 }
				player.takeExpRecord[ "freezeTime" ] = 0
			else:
				player.statusMessage( csstatus.TAKE_EXP_NOT_RESUME_FAIL )
				player.endGossip( talkEntity )
				return

		week = player.takeExpRecord[ "week" ]
		lastTime = player.takeExpRecord[ "lastTime" ]
		remainTime = player.takeExpRecord[ "remainTime" ]
		t = time.localtime()
		week1 = t[6]
		m_hour = self.hour

		if lastTime <= 0: # 第一次使用
			player.takeExpRecord[ "week" ] = week1
			player.takeExpRecord[ "remainTime" ] = 7
			player.takeExpRecord[ "lastTime" ] = time.time()
			player.setTemp( "rewardExpHour", m_hour )
			talkEntity.spellTarget( self.skillID, player.id )
			player.endGossip( talkEntity )
			return;

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
		if ( time.time() - lastTime ) < remainWeekTime + lastDayRemainTime:
			# 一个星期还没过去
			if remainTime < m_hour : # 剩余时间不足
				player.statusMessage( csstatus.TAKE_EXP_HOUR_LESS )
				player.endGossip( talkEntity )
				return
		else:
			player.takeExpRecord[ "remainTime" ] = 7

		buffs = player.findBuffsByBuffID( 22117 )

		if len( buffs ) <= 0:
			player.setTemp( "rewardExpHour", m_hour )
			talkEntity.spellTarget( self.skillID, player.id )
		else:
			buff = player.getBuff( buffs[ 0 ] )
			if ( buff["persistent"] - time.time() + self.hour * 60 * 60 ) > 5 * 60 * 60: # 如果叠加到身上将会超过5小时 因此不允许
				player.statusMessage( csstatus.TAKE_EXP_HOUR_MAX )
				player.endGossip( talkEntity )
				return
			player.setTemp( "rewardExpHour", m_hour )
			talkEntity.spellTarget( self.skillID, player.id )
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



#