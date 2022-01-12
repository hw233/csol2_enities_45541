# -*- coding: gb18030 -*-
#
# $Id: PotentialObject.py,v 1.21 2008-08-13 06:38:12 kebiao Exp $

import BigWorld
import cschannel_msgs
import ShareTexts as ST
import NPC
from bwdebug import *
import csdefine
import csstatus
import random
import ECBExtend
from ObjectScripts.GameObjectFactory import g_objFactory
from Resource.QuestLoader import QuestsFlyweight
quests = QuestsFlyweight.instance()
from ObjectScripts.GameObjectFactory import GameObjectFactory
g_objects = GameObjectFactory.instance()

Team_distance = 20 # 队伍进入距离要求在100米

dlgMsg1 = [
	cschannel_msgs.POTENTIAL_VOICE2,
	cschannel_msgs.POTENTIAL_VOICE3,
	cschannel_msgs.POTENTIAL_VOICE4,
	cschannel_msgs.POTENTIAL_VOICE5,
	cschannel_msgs.POTENTIAL_VOICE6,
	cschannel_msgs.POTENTIAL_VOICE7,
	cschannel_msgs.POTENTIAL_VOICE8,
	cschannel_msgs.POTENTIAL_VOICE9,
	cschannel_msgs.POTENTIAL_VOICE10,
]

class PotentialObject( NPC.NPC ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		NPC.NPC.__init__( self )
	
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		初始化自己的entity的数据
		"""
		NPC.NPC.initEntity( self, selfEntity )
		BigWorld.globalData[ "PotentialQuestMgr" ].onRegisterPotentialObject( selfEntity.queryTemp( "ownerDatabaseID", 0 ), selfEntity.base )

	def onDestroySelf( self, selfEntity ):
		"""
		副本通知 删除自身
		"""
		BigWorld.globalData[ "PotentialQuestMgr" ].onUnRegisterPotentialObject( selfEntity.queryTemp( "ownerDatabaseID", 0 ) )
		selfEntity.destroy()

	def onDestroySelfTimer( self, selfEntity ):
		"""
		生命时钟到期删除自身
		"""
		spaceBaseMailbox = selfEntity.queryTemp( "spaceBaseMailbox", None )
		if spaceBaseMailbox:
			spaceBaseMailbox.cell.remoteScriptCall( "onPotentialObjectDie", () )

	def gossipWith( self, selfEntity, playerEntity, dlgKey ):
		"""
		与玩家对话；未声明(不能声明)的方法，因此重载此方法的上层如果需要访问自己的私有属性请自己判断self.isReal()。

		@param   selfEntity: 与自己对应的Entity实例，传这个参数是为了方便以后的扩充
		@type    selfEntity: Entity
		@param playerEntity: 说话的玩家
		@type  playerEntity: Entity
		@param       dlgKey: 对话关键字
		@type        dlgKey: str
		@return: 无
		"""
		playerEntity = BigWorld.entities.get( playerEntity.id )
		if not playerEntity:
			return

		if dlgKey == "Talk":
			qids = playerEntity.findQuestByType( csdefine.QUEST_TYPE_POTENTIAL )
			if selfEntity.isReal():
				self.gossip_Talk( selfEntity, playerEntity, qids )
			else:
				selfEntity.remoteScriptCall( "gossip_Talk", ( playerEntity.base, qids ) )
		elif dlgKey == "gossip.0":
			playerEntity.endGossip( selfEntity.id )
			qids = playerEntity.findQuestByType( csdefine.QUEST_TYPE_POTENTIAL )
			if len( qids ) <= 0 :
				return

			qid = qids[ 0 ]
			quest = playerEntity.getQuestTasks( qid )
			maps = quests[ qid ].questSpaceName
			map = None
			done = False
			r = random.random()
			map = maps[0]
			for m in maps:
				if r <= m[2]:
					map = m
					done = True
					break
			gm_mapName = playerEntity.queryTemp( "gmSetPotentialMap", "" )
			if gm_mapName != "":
				for m in maps:
					if m[0] == gm_mapName:
						map = m
						playerEntity.removeTemp( "gmSetPotentialMap" )
						break;

			#selfEntity.setTemp( "potential_createSpaceName", map[0] )
			playerEntity.setTemp( "potential_creating", (selfEntity.id,map[0]) )
			selfEntity.setTemp( "questLevel", quest.query( "qLevel" ) )
			monClassType = quest.query( "monClassType" )
			quest.set( "potential_createSpaceName", map[0] )
			entitys = [ playerEntity ]

			if playerEntity.isInTeam():
				# 将所有符合任务条件的队员传入副本
				teamMembers = playerEntity.getAllMemberInRange( Team_distance )
				for entity in teamMembers:
					if entity.id != playerEntity.id:
						if quests[ qid ].validQuestCondition( entity ):
							entitys.append( entity )

			entityCount = len( entitys )
			for entity in entitys:
				# 给予创建副本的参数
				entity.setTemp( "monClassType", monClassType )
				entity.setTemp( "enterSpaceID", playerEntity.databaseID )
				entity.setTemp( "questID", qid )
				entity.setTemp( "potentialIssuer", playerEntity.databaseID )
				entity.setTemp( "NPCObjMailbox", selfEntity.base )
				entity.setTemp( "NPCClassName", selfEntity.className )
				entity.setTemp( "bossModelNumber", selfEntity.modelNumber )
				entity.setTemp( "bossName", selfEntity.getName() )
				entity.setTemp( "playerAmount", entityCount )
				entity.setTemp( "questLevel", quest.query( "qLevel" ) )
				entity.setTemp( "castNPCMapName", quest.query( "dest_space_id", "" ) )
				entity.setTemp( "leavePoint", ( tuple( selfEntity.position ), tuple( selfEntity.direction ) ) )
				entity.gotoSpace( map[0], ( 0, 0, 0 ), ( 0, 0, 0 ) )
			
		elif dlgKey == "gossip.2":
			if playerEntity.isReal():
				playerEntity.endGossip( selfEntity.id )

			if not selfEntity.isReal():
				selfEntity.remoteScriptCall( "gossipWith", ( playerEntity, dlgKey ) )
				return
			playerEntity.gotoSpace( selfEntity.queryTemp( "potential_createSpaceName", "" ), ( 0, 0, 0 ), ( 0, 0, 0 ) )

	def isSameTeam( self, playerEntity, ownerDatabaseID ):
		"""
		是否是同一个队伍成员
		"""
		if playerEntity.isInTeam():
			for e in playerEntity.teamMembers:
				if ownerDatabaseID == e["dbID"]:
					return True
		return False

	def gossip_Talk( self, selfEntity, playerEntity, qids ):
		"""
		第一阶段对话： 在这里selfEntity一定为real
		"""
		playerEntity = BigWorld.entities.get( playerEntity.id )
		if not playerEntity:
			return

		ownerDatabaseID = selfEntity.queryTemp( "ownerDatabaseID", 0 )
		if ownerDatabaseID != playerEntity.databaseID:
			canEnter = self.isSameTeam( playerEntity, ownerDatabaseID )
			qid = selfEntity.queryTemp( "questID", 0 )
			if not canEnter or selfEntity.queryTemp( "potential_createSpaceName", "" ) == "" or not quests[ qid ].validQuestCondition( playerEntity ):
				playerEntity.setGossipText( cschannel_msgs.POTENTIAL_VOICE11 )
				playerEntity.sendGossipComplete( selfEntity.id )
			else:
				playerEntity.setTemp( "enterSpaceID", ownerDatabaseID )
				playerEntity.setGossipText( cschannel_msgs.POTENTIAL_VOICE12 )
				playerEntity.addGossipOption( "gossip.2", cschannel_msgs.GOSSIP_8 )
				playerEntity.sendGossipComplete( selfEntity.id )

				# 这里已经确定任务主人在一个队伍中了  我们更新副本的队伍ID
				spaceBaseMailbox = selfEntity.queryTemp( "spaceBaseMailbox", None )
				if spaceBaseMailbox:
					spaceBaseMailbox.cell.setTemp( "teamID", playerEntity.teamMailbox.id )
		else:
			# 有可能他放弃了任务后来与NPC对话
			if len( qids ) <= 0:
				playerEntity.setGossipText( cschannel_msgs.POTENTIAL_VOICE11 )
				playerEntity.sendGossipComplete( selfEntity.id )
				return

			playerEntity.setTemp( "enterSpaceID", ownerDatabaseID )
			#只有接任务者唯一一个人能够经过这里
			if selfEntity.queryTemp( "potential_createSpaceName", "" ) == "":
				playerEntity.setGossipText( dlgMsg1[ random.randint( 0, len( dlgMsg1 ) - 1) ] )
				playerEntity.addGossipOption( "gossip.0", cschannel_msgs.GOSSIP_9 )
				playerEntity.sendGossipComplete( selfEntity.id )
			else:
				playerEntity.setGossipText( cschannel_msgs.POTENTIAL_VOICE13 )
				playerEntity.addGossipOption( "gossip.2", cschannel_msgs.GOSSIP_10 )
				playerEntity.sendGossipComplete( selfEntity.id )

#
# $Log: not supported by cvs2svn $
# Revision 1.20  2008/06/19 08:55:14  kebiao
# 按照新的策划按进行修改了
#
# Revision 1.19  2008/04/30 01:45:41  kebiao
# 修改副本base的存储问题
#
# Revision 1.18  2008/04/28 06:50:54  kebiao
# 去掉onDestroySelf重载
#
# Revision 1.17  2008/03/28 06:50:00  kebiao
# 调整任务NPC对话
#
# Revision 1.16  2008/03/12 08:06:32  kebiao
# 调整任务对话
#
# Revision 1.15  2008/03/12 05:38:51  kebiao
# 修改addGossipOption相关接口
#
# Revision 1.14  2008/02/23 08:39:33  kebiao
# 调整潜能任务
#
# Revision 1.13  2008/02/18 08:52:47  kebiao
# 潜能任务调整
#
# Revision 1.12  2008/02/14 02:25:08  kebiao
# no message
#
# Revision 1.11  2008/02/03 08:18:32  kebiao
# 修改获取队伍ID的一个BUG
#
# Revision 1.10  2008/02/03 04:18:51  kebiao
# 潜能任务调整
#
# Revision 1.9  2008/02/03 00:52:04  kebiao
# 潜能任务调整
#
# Revision 1.8  2008/01/28 06:10:06  kebiao
# 重写该模块
#
#
#