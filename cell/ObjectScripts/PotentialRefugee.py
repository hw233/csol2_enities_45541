# -*- coding: gb18030 -*-
#
# $Id: PotentialIssuer.py,v 1.3 2008-06-19 08:55:14 kebiao Exp $


"""
pet's foster

2007/11/08 : writen by huangyongwei
"""

import csdefine
import BigWorld
import csstatus
import csstatus_msgs
import NPC
import ECBExtend
import random
import cschannel_msgs
from bwdebug import *

class PotentialRefugee( NPC.NPC ):
	"""
	潜能难民NPC
	"""

	def __init__( self ):
		NPC.NPC.__init__( self )

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
		if dlgKey == "Talk":
			ownerDatabaseID = playerEntity.queryTemp( "ownerDatabaseID", 0 )
			canEnter = False
			if ownerDatabaseID != playerEntity.databaseID:
				canEnter = False
				if playerEntity.isInTeam():
					for e in playerEntity.teamMembers:
						if ownerDatabaseID == e["dbID"]:
							canEnter = True
							break
			else:
				canEnter = True

			if canEnter:
				if playerEntity.queryTemp( "questLevel", 0 ) > 0:
					playerEntity.setGossipText( cschannel_msgs.CELL_POTENTIALREFUGEE_S_1[ random.randint( 0, len( cschannel_msgs.CELL_POTENTIALREFUGEE_S_1 ) - 1 ) ] )
					playerEntity.addGossipOption( "yjnm_talk", cschannel_msgs.CELL_POTENTIALREFUGEE_1, csdefine.QUEST_STATE_FINISH )
					playerEntity.sendGossipComplete( selfEntity.id )
		elif dlgKey == "yjnm_talk":
			playerEntity.endGossip( selfEntity.id )
			"""
			营救奖励仅有潜能，具体值根据产生副本时的等级决定，公式为：
			奖励值 = 副本等级 * 20 （大致与该副本的BOSS奖励相当）
			每个队员所获得的值由该值通过组队经验分配公式决定。
			"""
			questLevel = playerEntity.queryTemp( "questLevel", 0 )
			pval = questLevel * 20

			spaceBase = playerEntity.queryTemp( "space", None )
			spaceEntity = None

			try:
				spaceEntity = BigWorld.entities[ spaceBase.id ]
			except:
				DEBUG_MSG( "not find the spaceEntity!" )

			selfEntity.gainReward( playerEntity, selfEntity.exp, pval, selfEntity.accumPoint )
			statusInfo = csstatus_msgs.getStatusInfo( csstatus.POTENTIAL_QUEST_REFUGEE_COMPLETE )
			selfEntity.say( statusInfo.msg )
			playerEntity.statusMessage( csstatus.POTENTIAL_QUEST_REFUGEE_COMPLETE )
			selfEntity.addTimer( 2, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )
#
# $Log: not supported by cvs2svn $
#