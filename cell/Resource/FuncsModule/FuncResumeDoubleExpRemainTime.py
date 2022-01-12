# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
"""
from Function import Function
import csdefine
import BigWorld
import csstatus
import csconst
import time

def calculateOnLoad( timeVal ):
	"""
	在加载人物数据的时候重新计算延迟值。
	1.获取剩余时间(需要考虑下线后是否计时)
	2.加上现在的服务器运行时间

	@type  timeVal: INT32
	@return: 返回最新的cooldown时间
	@rtype:  INT32
	"""
	if timeVal == 0: return timeVal		# 无持续时间，不处理
	return int( timeVal + time.time() )		# int( (剩余时间 + 当前运行时间) * 修正值 )

class FuncResumeDoubleExpRemainTime( Function ):
	"""
	恢复双倍奖励时间
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
		player.endGossip( talkEntity )
		buff = player.takeExpRecord[ "freezeBuff" ]
		if player.takeExpRecord[ "freezeTime" ] > 0:
			# 记录最后冻结的时间
			t = time.time() - player.takeExpRecord[ "freezeTime" ]
			lostTime = 0
			if t > 24 * 60 * 60:
				lostTime = t - 24 * 60 * 60
			
			# BUFF是否超时
			if buff[ "persistent" ] <= lostTime:
				player.endGossip( talkEntity )
				player.takeExpRecord[ "freezeBuff" ] = { "skill" : None , "persistent" : 0, "currTick" : 0, "caster" : 0, "state" : 0, "index" : 0 ,"sourceType" : 0, "isNotIcon": 0 }
				player.takeExpRecord[ "freezeTime" ] = 0
				return
			
			# 计算BUFF的剩余时间
			buff[ "persistent" ] -= lostTime
			buff[ "persistent" ] = calculateOnLoad( buff[ "persistent" ] )
			player.takeExpRecord[ "freezeBuff" ] = { "skill" :  None , "persistent" : 0, "currTick" : 0, "caster" : 0, "state" : 0, "index" : 0 ,"sourceType" : 0, "isNotIcon": 0 }
			player.takeExpRecord[ "freezeTime" ] = 0


			buffs = player.findBuffsByBuffID( 22117 )

			if len( buffs ) > 0:
				buff1 = player.getBuff( buffs[0] )
				if ( buff1[ "persistent" ] + buff[ "persistent" ] ) > 5 * 60 * 60:
					player.statusMessage( csstatus.TAKE_EXP_HOUR_HUIFU_FAIL )
					player.endGossip( talkEntity )
					return
					
			player.addSavedBuff( buff )
			
			player.statusMessage( csstatus.TAKE_EXP_HOUR_HUIFU, "%i%%" % buff["skill"].getPercent() )

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

