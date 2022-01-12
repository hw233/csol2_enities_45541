# -*- coding: gb18030 -*-

from bwdebug import *
import csdefine
import csconst
import csstatus
import time
import BigWorld

class FuncRequestTongFete:
	"""
	申请帮会祭祀活动
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
		if talkEntity is None:
			player.endGossip( talkEntity )
			return
			
		if not player.checkDutyRights( csdefine.TONG_RIGHT_ACTIVITY ):
			player.statusMessage( csstatus.TONG_FETE_GRADE_INVALID )
			player.endGossip( talkEntity )
			return
		#按照CSOL-9750的需求，取消帮会祭祀的等级限制
		#elif player.tong_level < 3:
		#	player.statusMessage( csstatus.TONG_FETE_LEVEL_INVALID )
		#	player.endGossip( talkEntity )
		#	return
		
		tm = time.localtime()
		# 帮会祭祀活动改为每周日12:00-22:00之间才可以申请，by mushuang
		weekDay = tm[6] # 0 表示周一
		hour = tm[3]
		minute = tm[4]
		sec = tm[5]		
		curTimeInSec = hour * 3600 + minute * 60 + sec
		# 开始时间 12：00
		startTimeInSec = 12 * 3600 
		# 结束时间 22:00
		endTimeInSec = 22 * 3600
		
		if not ( weekDay == 6 and curTimeInSec >= startTimeInSec and curTimeInSec <= endTimeInSec ) :
			player.statusMessage( csstatus.TONG_FETE_DATE_INVALID )
			player.endGossip( talkEntity )
			return
		BigWorld.globalData[ "TongManager" ].requestFete( player.tong_dbID, player.tong_grade, player.base )
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