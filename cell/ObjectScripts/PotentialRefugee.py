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
	Ǳ������NPC
	"""

	def __init__( self ):
		NPC.NPC.__init__( self )

	def gossipWith( self, selfEntity, playerEntity, dlgKey ):
		"""
		����ҶԻ���δ����(��������)�ķ�����������ش˷������ϲ������Ҫ�����Լ���˽���������Լ��ж�self.isReal()��

		@param   selfEntity: ���Լ���Ӧ��Entityʵ���������������Ϊ�˷����Ժ������
		@type    selfEntity: Entity
		@param playerEntity: ˵�������
		@type  playerEntity: Entity
		@param       dlgKey: �Ի��ؼ���
		@type        dlgKey: str
		@return: ��
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
			Ӫ�Ƚ�������Ǳ�ܣ�����ֵ���ݲ�������ʱ�ĵȼ���������ʽΪ��
			����ֵ = �����ȼ� * 20 ��������ø�����BOSS�����൱��
			ÿ����Ա����õ�ֵ�ɸ�ֵͨ����Ӿ�����乫ʽ������
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