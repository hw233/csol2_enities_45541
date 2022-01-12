# -*- coding: gb18030 -*-
#


"""
"""
from Function import Function
import csdefine
import BigWorld
import time
import csstatus
import csconst
from ActivityRecordMgr import g_activityRecordMgr

ENTERN_EXP_MELEE_MENBER_DISTANCE = 30.0
HUAN_XIN_GU_WU_BUFF				 = 299006

class FuncEnterExpMelee( Function ):
	"""
	进入经验乱斗副本
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.level = section.readInt( "param1" )		#进入等级


	def do( self, player, talkEntity = None ):
		"""
		进入经验乱斗副本。
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

		if not BigWorld.globalData.has_key('AS_ExpMelee'):
			#经验乱斗活动没有开启
			player.statusMessage( csstatus.EXP_MELEE_IS_NOT_OPEN )
			return

		if self.level > player.level:
			#玩家等级不够
			player.statusMessage( csstatus.EXP_MELEE_LEVEL_NOT_ENOUGH )
			return

		if not player.isInTeam():
			#玩家没有组队
			player.statusMessage( csstatus.EXP_MELEE_NEED_TEAM )
			return

		if BigWorld.globalData.has_key( 'ExpMelee_%i'%player.getTeamMailbox().id ):
			#玩家的队伍拥有一个经验乱斗副本
			if player.isActivityCanNotJoin( csdefine.ACTIVITY_JING_YAN_LUAN_DOU ):
				player.statusMessage( csstatus.EXP_MELEE_HAS_ENTER )
				return

			player.gotoSpace('fu_ben_exp_melee', (0, 0, 0), (0, 0, 0))
			player.addActivityCount( csdefine.ACTIVITY_JING_YAN_LUAN_DOU )
			return
		else:
			#队伍没有副本，则走创建流程
			if not player.isTeamCaptain():
				player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
				return

			if not len(player.getAllMemberInRange( ENTERN_EXP_MELEE_MENBER_DISTANCE )) >= 3 :
				player.statusMessage( csstatus.EXP_MELEE_NOT_ENOUGH_MEMBER )
				return

			pList = player.getAllMemberInRange( ENTERN_EXP_MELEE_MENBER_DISTANCE )
			expMeleeEnterFlag = False
			for i in pList:
				if i.level < self.level:
					player.statusMessage( csstatus.EXP_MELEE_MEMBER_LEVEL_NOT_ENOUGH )
					return

				if i.isActivityCanNotJoin( csdefine.ACTIVITY_JING_YAN_LUAN_DOU ):
					player.statusMessage( csstatus.EXP_MELEE_MEMBER_HAS_ENTER, i.getName() )
					expMeleeEnterFlag = True

			if expMeleeEnterFlag : return

			# 参数：为了创建出副本的门
			player.setTemp( "currentSpaceName", player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
			player.setTemp( "enterPosition", player.position )
			player.setTemp( "enterDirection", player.direction )

			for i in pList:
				i.addActivityCount( csdefine.ACTIVITY_JING_YAN_LUAN_DOU )
				i.gotoSpace('fu_ben_exp_melee', (0, 0, 0), (0, 0, 0))

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

