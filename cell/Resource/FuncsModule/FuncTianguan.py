# -*- coding: gb18030 -*-
#
# $Id: FuncTianguan.py,v 1.6 2008-09-01 03:37:25 zhangyuxing Exp $

"""
"""
from Function import Function
#import ChuangtianguanMgr
import csdefine
import csstatus
import Language
import time
import BigWorld
import utils
from bwdebug import *
import csdefine

ENTERN_TIANGUAN_MENBER_DISTANCE = 30					#天关成员距离

class FuncCreateTianguan( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		"""
		self.level 		= section.readInt( "param2" )								#天关需要等级
		self._longM 	= section.readInt( "param3" )								#天关开启时间长度

		self.position = None														#进入天关位置
		position = section.readString( "param4" )
		pos = utils.vector3TypeConvert( position )
		if pos is None:
			ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section param4 " % ( self.__class__.__name__, position ) )
		else:
			self.position = pos
		
		self.direction = None
		direction = section.readString( "param5" )									#进入天关朝向
		dir = utils.vector3TypeConvert( direction )
		if dir is None:
			ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section param5 " % ( self.__class__.__name__, direction ) )
		else:
			self.direction = dir
				
		self.recordKey = "tianguan_record"
		self.spaceName = section.readString( "param1" )

	def do( self, player, talkEntity = None ):
		"""
		进入天关副本。
		规则：
			创建条件：（把队员都拉进来）
				这个队伍当前没有副本。
				要求进入者是队长。
				达到等级要求。
				队伍人数大于3人。
				队伍成员没有进入过副本的。
			进入条件：（只有自己一个人进去）
				有组队。
				有队伍副本存在。

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		if not player.isInTeam():
			#玩家没有组队
			player.statusMessage( csstatus.TIAN_GUAN_NEED_TEAM )
			return
		if self.level > player.level:
			player.statusMessage( csstatus.ROLE_HAS_NOT_TIANGUAN_LEVEL, self.level )
			return
		if BigWorld.globalData.has_key( 'Tianguan_%i'%player.getTeamMailbox().id ):
			if player.isActivityCanNotJoin( csdefine.ACTIVITY_CHUANG_TIAN_GUAN )  and player.query( "lastTianguanTeamID", 0 ) != player.getTeamMailbox().id:
				player.client.onStatusMessage( csstatus.TIANGUAN_IN_ALREADY, "" )
				return
			player.gotoSpace( self.spaceName, self.position, self.direction )
		else:
			#队伍没有副本，则走创建流程
			if not player.isTeamCaptain():
				player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
				return
				
			pList = player.getAllMemberInRange( ENTERN_TIANGUAN_MENBER_DISTANCE )
			if not len(pList) >= 3 :
				player.statusMessage( csstatus.ROLE_IS_ENOUGH_MEMBER )
				return	

			for i in pList:
				if i.level < self.level:
					player.statusMessage( csstatus.ROLE_MEMBER_HAS_NOT_TIANGUAN_LEVEL, self.level )
					return
				if i.isActivityCanNotJoin( csdefine.ACTIVITY_CHUANG_TIAN_GUAN ) :
					player.statusMessage( csstatus.TIANGUAN_MEMBER_HAS_ENTERED_TODAY, i.getName() )
					return
			player.gotoSpace( self.spaceName, self.position, self.direction )	# 队长必须第一个进入副本
			pList.remove( player )
			for i in pList:
				if i.id == player.id: #防止用GM命令添加队友造成plist中数据异常，从而导致传送异常
					continue
				i.set( "lastTianguanTeamID", player.getTeamMailbox().id )
				i.gotoSpace( self.spaceName, self.position, self.direction )

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
		#return BigWorld.globalData.has_key( "AS_Tianguan" )


class FuncLastReward( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
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
		if talkEntity.isReal():
			talkEntity.getScript().touch( talkEntity, player )
		else:
			talkEntity.remoteScriptCall( "touch", ( player, ) )
		return False
