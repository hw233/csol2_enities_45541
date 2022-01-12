# -*- coding: gb18030 -*-
"""
帮会会标NPC对话 14:11 2010-1-14 by 姜毅
"""

from Function import Function
from bwdebug import *
import csstatus
import csdefine
import csconst
import BigWorld
import sys

class FuncTongSign( Function ):
	"""
	帮会会标NPC对话
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._talkType = int( section.readString( "param1" ) )	# 需要上传(1)还是更换(2)还是取消(3)图标
		
	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if player.iskitbagsLocked():	# 背包上锁，by姜毅
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			player.endGossip( talkEntity )
			return
		if self._talkType == 1:
			self.submitTongSign( player )
		elif self._talkType == 2:
			self.changeTongSign( player )
		elif self._talkType == 3:
			self.cancleTongSign( player )
		elif self._talkType == 4:
			self.useSubmitTongSign( player )
		else:
			ERROR_MSG( "self._talkType error, no this talk type %i"%( self._talkType ) )
		player.sendGossipComplete( talkEntity.id )
		Function.do( self, player, talkEntity )
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
		
	def submitTongSign( self, player ):
		"""
		上传帮会图标
		"""
		if not player.checkDutyRights( csdefine.TONG_RIGHT_SIGN ):	# 权限检测
			player.statusMessage( csstatus.TONG_ME_NOT_IS_CHIEF )
			return
		if player.tong_level < csconst.USER_TONG_SIGN_REQ_TONG_LEVEL:
			player.statusMessage( csstatus.TONG_SIGN_NOT_THAT_LEVEL )
			return
		player.client.tongSignTalkResult( 1 )
		
	def changeTongSign( self, player ):
		"""
		更换帮会会标
		"""
		if not player.checkDutyRights( csdefine.TONG_RIGHT_SIGN ):	# 权限检测
			player.statusMessage( csstatus.TONG_ME_NOT_IS_CHIEF )
			return
		player.client.tongSignTalkResult( 2 )
		
	def cancleTongSign( self, player ):
		"""
		取消帮会会标
		"""
		if not player.checkDutyRights( csdefine.TONG_RIGHT_SIGN ):	# 权限检测
			player.statusMessage( csstatus.TONG_ME_NOT_IS_CHIEF )
			return
		player.client.tongSignTalkResult( 3 )
		
	def useSubmitTongSign( self, player ):
		"""
		使用上传会标
		"""
		if not player.checkDutyRights( csdefine.TONG_RIGHT_SIGN ):	# 权限检测
			player.statusMessage( csstatus.TONG_ME_NOT_IS_CHIEF )
			return
		player.tong_getSelfTongEntity().changeTongSing( False, 0, "sub", player )