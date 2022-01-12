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

def calculateOnSave( self, timeVal ):
	"""
	在保存人物数据的时候重新计算延迟值。
	1.获取剩余时间(需要考虑下线后是否计时)
	2.返回剩余时间

	@type  timeVal: INT32
	@return: 返回最新的cooldown时间；我们假设所有传过来的值都是从cellData里获得的，因此该值是一个使用BigWorld.time()的整型数。
	@rtype:  INT32
	"""
	if timeVal == 0: return timeVal		# 无持续时间，不处理
	# 取得剩余时间，必须先除于修正值获取真正的剩余时间
	return int( timeVal - time.time() )

class FuncCloseDoubleExpRemainTime( Function ):
	"""
	冻结双倍奖励时间
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
		player.saveDoubleExpBuff()
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

