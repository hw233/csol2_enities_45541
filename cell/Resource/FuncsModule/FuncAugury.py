# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
占卜
"""
import time
import random
from Function import Function
import csstatus
import csdefine

class FuncAugury( Function ):
	"""
	占卜
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )	# 一天占卜次数
		self._param2 = section.readInt( "param2" )	# 每天最多可以晒多长时间
		self._param3 = section.readInt( "param3" )	# 占卜金钱消耗
		self._param4 = section.readInt( "param4" )  # 占卜间隔时间
		self._param5 = section.readString( "param5" )	# 角色施放占卜技能
		self.allSkills = self._param5.split("|")

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

		if player.money < self._param3:
			player.statusMessage( csstatus.SUN_BATHING_AUGURY_MONEY_LOW )
			return

		# 判断是否在合法日光浴时间
		if not player.isSunBathing() and player.sunBathDailyRecord.sunBathCount < self._param2:
			player.statusMessage( csstatus.SUN_BATHING_AUGURY_FORBID_TIME )
			return

		date = time.localtime()[2]
		# 判断是否为同一天
		if player.sunBathDailyRecord.auguryDate != date:
			player.sunBathDailyRecord.auguryDate = date
			player.sunBathDailyRecord.auguryCount = 0

		# 判断是否超过占卜次数
		if not player.sunBathDailyRecord.auguryCount < self._param1:
			player.statusMessage( csstatus.SUN_BATHING_AUGURY_COUNT_LOW )
			return

		# 判断占卜是否间隔5分钟
		nowTime = int( time.time() )
		if nowTime - player.sunBathDailyRecord.auguryTime < self._param4:
			player.statusMessage( csstatus.SUN_BATHING_AUGURY_INTERVAL_TIME )
			return

		player.sunBathDailyRecord.auguryCount += 1
		player.sunBathDailyRecord.auguryTime = nowTime
		player.payMoney( self._param3, csdefine.CHANGE_MONEY_AUGURY )	# 玩家扣除金钱

		skillID = int( random.choice( self.allSkills ) )
		player.spellTarget( skillID, player.id )		# 随机选择施放一个占卜技能


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