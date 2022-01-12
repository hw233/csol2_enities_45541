# -*- coding: gb18030 -*-
#
# $Id: FuncConstCityWar.py,v 1.1 2008-08-20 00:52:43 kebiao Exp $

"""
"""
from Function import Function
import cschannel_msgs
import ShareTexts as ST
from bwdebug import *
import csdefine
import csstatus
import csconst
import BigWorld

class FuncCommitCityWarQuest( Function ):
	"""
	提交城市战场任务
	"""
	def __init__( self, section ):
		"""
		param1: amount

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
		if player.checkItemFromNKCK_( 50201256, 1 ):
			if player.removeItemTotal( 50201256, 1, csdefine.DELETE_ITEM_COMMITCITYWAR ):
				BigWorld.globalData[ "TongManager" ].commitCityWarQuest( player.tong_dbID, player.playerName )
				player.tong_removeFungusFlag()
			player.endGossip( talkEntity )
		else:
			player.endGossip( talkEntity )
			player.setGossipText( cschannel_msgs.BIAN_SHEN_VOICE_9 )
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
		return player.tong_dbID in BigWorld.globalData[ "CityWarRightTongDBID" ]


#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/08/02 09:25:48  kebiao
# no message
#
# Revision 1.1  2008/07/25 03:17:49  kebiao
# no message
#
#
