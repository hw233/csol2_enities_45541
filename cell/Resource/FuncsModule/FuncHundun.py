# -*- coding: gb18030 -*-

"""
活动混沌入侵
"""
import time
import BigWorld
from Function import Function
import csdefine
import csstatus
import utils
from bwdebug import *

TEAM_MEMBER_NEED = 3																	#需要的队伍成员

class FuncHundun( Function ):
	"""
	进入混沌副本
	(fu_ben_hun_dun_ru_qin)
	"""
	def __init__( self, section ):
		"""
		"""
		self.__mapName 		= section["param1"].asString								#地图名
		self.__level		= section["param2"].asInt									#需要等级
		
		self.__pos = None																#进入位置
		position = section.readString( "param3" )
		pos = utils.vector3TypeConvert( position )
		if pos is None:
			ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section param3 " % ( self.__class__.__name__, position ) )
		else:
			self.__pos = pos
		
		self.__direction = None
		direction = section.readString( "param4" )										#进入朝向
		dir = utils.vector3TypeConvert( direction )
		if dir is None:
			ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section param4 " % ( self.__class__.__name__, direction ) )
		else:
			self.__direction = dir
			
		self.__distance		= section["param5"].asFloat									#成员距离

	def do( self, player, talkEntity = None ):
		"""
		进入混沌入侵副本
		规则：
			创建条件：（把队员都拉进来）
				队伍成员没有进入过副本的。（有标记记录进去过的）
				要求对话者是队长。
				达到等级要求。
				队伍人数大于3人。
			进入条件：（只有自己一个人进去）
				有组队。
				有队伍副本存在。
		"""
		player.endGossip( talkEntity )

		if talkEntity.hasFlag( csdefine.ENTITY_FLAG_COPY_STARTING ):
			player.client.onStatusMessage( csstatus.TALK_FORBID_NO_TASK, "" )
			return

		if player.level < self.__level:
			player.client.onStatusMessage( csstatus.HUNDUN_FORBID_LEVEL, str(( self.__level, )) )
			return

		if not player.isInTeam():
			player.client.onStatusMessage( csstatus.TALK_FORBID_TEAM, "" )
			return
	
		#队伍没有副本，则走创建流程
		if not player.isTeamCaptain():
			player.client.onStatusMessage( csstatus.HUNDUN_FORBID_CAPTAIN, "" )
			return

		if player.getTeamCount() < TEAM_MEMBER_NEED :
			player.client.onStatusMessage( csstatus.HUNDUN_FORBID_MEMBER_AMOUNT, str(( TEAM_MEMBER_NEED, )) )
			return

		members = player.getAllMemberInRange( self.__distance )
		
		if len( members ) < len( player.teamMembers ):
			player.client.onStatusMessage( csstatus.HUNDUN_FORBID_MEMBER_NEAR, "" )
			return
		
		for i in members:
			if i.level < self.__level:
				player.client.onStatusMessage( csstatus.HUNDUN_FORBID_MEMBER_LEVEL, str(( i.getName(), self.__level )) )
				return
		
		BigWorld.cellAppData["HD_%i"%player.teamMailbox.id] = talkEntity.id
		print "monster id:",BigWorld.cellAppData["HD_%i"%player.teamMailbox.id]
		#player.setTemp("copySpaceEnterMonsterID", talkEntity.id )		
		player.gotoSpace( self.__mapName, self.__pos, self.__direction )
		members.remove( player )
		
		for i in members:
			#i.setTemp("copySpaceEnterMonsterID", talkEntity.id )
			i.set( "lastHundunTeamID", player.getTeamMailbox().id )
			i.gotoSpace( self.__mapName, self.__pos, self.__direction )

		#talkEntity.destroy()
		talkEntity.addFlag( csdefine.ENTITY_FLAG_COPY_STARTING )

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
		return BigWorld.globalData.has_key( "AS_Hundun" )




class FuncQueryJiFen( Function ):
	"""
	查看混沌副本
	(fu_ben_hun_dun_ru_qin)
	"""
	def __init__( self, section ):
		pass
	
	
	def do( self, player, talkEntity = None ):
		"""
		"""
		player.endGossip( talkEntity )
		player.client.onStatusMessage( csstatus.HUNDUN_INTEGRAL, str(( player.query("hundun_jifen", 0), )) )


	def valid( self, player, talkEntity = None ):
		"""
		"""
		return True

class FuncChangeJifen( Function ):
	"""
	混沌副本兑换积分
	(fu_ben_hun_dun_ru_qin)
	"""
	def __init__( self, section ):
		self._new_title 		= section["param1"].asInt									#兑换称号
		self._need_title		= section["param2"].asInt									#需求称号
		self._jifen		 		= section["param3"].asInt									#需求积分
	
	
	def do( self, player, talkEntity = None ):
		"""
		"""
		player.endGossip( talkEntity )
		
		if player.hasTitle( self._new_title ):
			player.client.onStatusMessage( csstatus.TITLE_REPEAT, "" )
			return
		
		if self._need_title != 0 and not player.hasTitle( self._need_title ):
			player.client.onStatusMessage( csstatus.TITLE_CANNOT_CHANGED, "" )
			return
		
		jifen = player.query("hundun_jifen")
		if jifen < self._jifen:
			player.client.onStatusMessage( csstatus.TITLE_FORBID_INTEGRAL_NOT_ENOUGH, str(( self._jifen, )) )
			return
		
		player.set("hundun_jifen", jifen - self._jifen )
		
		player.addTitle( self._new_title )


	def valid( self, player, talkEntity = None ):
		"""
		"""
		return True