# -*- coding: gb18030 -*-
#
# 快乐金蛋活动对话function

from Function import Function
from KuaiLeJinDan import KuaiLeJinDan
g_KuaiLeJinDan = KuaiLeJinDan.instance()

class FuncKuaiLeJinDan( Function ):
	"""
	快乐金蛋活动
	"""
	def do( self, player, talkEntity = None ):
		"""
		执行快乐金蛋活动
		"""
		g_KuaiLeJinDan.startKLJDActivity( player )
		
class FuncSuperKuaiLeJinDan( Function ):
	"""
	快乐金蛋活动--超级大奖
	"""
	def do( self, player, talkEntity = None ):
		"""
		执行快乐金蛋活动--超级大奖
		"""
		g_KuaiLeJinDan.startSuperKLJDActivity( player )
		
	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用
		"""
		return g_KuaiLeJinDan.validStartSuperKLJDActivity( player )

class FuncKuaiLeJinDanExpReward( Function ):
	"""
	快乐金蛋，获取经验奖励
	"""
	def do( self, player, talkEntity = None ):
		"""
		快乐金蛋，获取经验奖励
		"""
		g_KuaiLeJinDan.doKLJDExpReward( player )
		
	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用
		"""
		return g_KuaiLeJinDan.validDoKLJDExpReward( player )

class FuncKuaiLeJinDanZuoQi( Function ):
	"""
	快乐金蛋，获取坐骑奖励
	"""
	def do( self, player, talkEntity = None ):
		"""
		快乐金蛋，获取坐骑奖励
		"""
		g_KuaiLeJinDan.doKLJDZuoQiReward( player )

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用
		"""
		return g_KuaiLeJinDan.validDoKLJDZuoQiReward( player )
