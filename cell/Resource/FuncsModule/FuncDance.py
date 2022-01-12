# -*- coding: gb18030 -*-
# 关于领取跳舞buff
"""
"""
from Function import Function
import cschannel_msgs
import ShareTexts as ST
import BigWorld
from csdefine import *
import time
import csconst
import csstatus
import Const

class FuncTakeDanceBuff( Function ):
	"""
	领取跳舞buff
	"""
	def __init__( self, section ):
		"""
		param1: CLASS_*

		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.skillID = section.readInt( "param1" )  			# 技能ID
		self._param2 = section.readInt( "param2" )				# 一天允许领取次数

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

		if not player.danceRecord["danceDailyRecord"].checklastTime():		# 判断是否为同一天
			player.danceRecord["danceDailyRecord"].reset()
		if player.danceRecord["danceDailyRecord"].getDegree() >= self._param2:		# 判断次数
			player.statusMessage( csstatus.JING_WU_SHI_KE_LIMIT_NUM )
			return

		player.spellTarget( self.skillID, player.id )
		player.danceRecord["danceDailyRecord"].incrDegree()	# 领取次数加1

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

class FuncFreezeDanceBuff( Function ):
	"""
	冻结跳舞buff
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""

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

		buffs = player.findBuffsByBuffID( Const.JING_WU_SHI_KE_DANCE_BUFF )
		if len( buffs ) <= 0:
			player.statusMessage( csstatus.JING_WU_SHI_KE_NO_BUFF )
			return
		player.client.saveDanceBuff()		# 通知客户端要冻结了

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

class FuncResumeDanceBuff( Function ):
	"""
	恢复跳舞时间
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""

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

		if not player.danceRecord["freezeDanceDailyRecord"].checklastTime():		# 如果没有当天冻结的dance buff
			player.statusMessage( csstatus.JING_WU_SHI_KE_NO_FREEZON_BUFF )
			return

		buff = player.danceRecord[ "freezeBuff" ]
		buff[ "persistent" ] = calculateOnLoad( buff[ "persistent" ] )
		player.danceRecord[ "freezeBuff" ] = { "skill" : None, "persistent" : 0, "currTick" : 0, "caster" : 0, "state" : 0, "index" : 0 }
		player.danceRecord[ "freezeDanceDailyRecord" ]._lastTime = 0		# 领取dance buff后，设置冻结时间为0


		player.addSavedBuff( buff )

		player.statusMessage( csstatus.JING_WU_SHI_KE_RESUME )

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

class FuncQueryDancePoint( Function ):
	"""
	查询舞蹈积分
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
		player.setGossipText( cschannel_msgs.DANCE_VOICE_1 %( player.dancePoint ) )
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
