# -*- coding: gb18030 -*-
#
# ToxinFrog�� 2009-05-25 SongPeifang
#

from WXMonster import WXMonster
import cschannel_msgs
import ShareTexts as ST
from bwdebug import *
import csdefine
import BigWorld
import csstatus
import Const



class ToxinFrog( WXMonster ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		WXMonster.__init__( self )
		self.bornNPC = True
		#self.callMonsterID		= "20332011"
		self.fightingText		= cschannel_msgs.QIAN_NIAN_DU_WA_VOICE_4
		self.freeText			= cschannel_msgs.QIAN_NIAN_DU_WA_VOICE_5
		self.fightOption		= cschannel_msgs.CELL_GOSSIP_OBJECTSCRIPT_TOXINFROG_0
		self.leaveOption		= cschannel_msgs.CELL_GOSSIP_OBJECTSCRIPT_TOXINFROG_1
		self.fightSay			= cschannel_msgs.CELL_GOSSIP_OBJECTSCRIPT_TOXINFROG_2

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
		if selfEntity.state == csdefine.ENTITY_STATE_FIGHT:
				playerEntity.setGossipText( cschannel_msgs.CELL_WXMONSTER_1 )
				playerEntity.sendGossipComplete( selfEntity.id )
				return
		if dlgKey == "Talk":
			if playerEntity.getState() == csdefine.ENTITY_STATE_FIGHT:
				#playerEntity.setGossipText( self.fightingText )
				playerEntity.statusMessage( csstatus.AN_YING_ZHI_MENG_PLAYER_IS_FIGHTING )
				playerEntity.sendGossipComplete( selfEntity.id )
				return
			if selfEntity.getState() != csdefine.ENTITY_STATE_FREE:
				playerEntity.endGossip( selfEntity )
				return
			playerEntity.setGossipText( self.freeText )
			playerEntity.addGossipOption(  "NPCStart.s1", self.fightOption )
			playerEntity.addGossipOption(  "NPCLeave.s1", self.leaveOption )
			playerEntity.sendGossipComplete( selfEntity.id )
		elif dlgKey == "NPCStart.s1":
			if playerEntity.getState() == csdefine.ENTITY_STATE_FIGHT:
				playerEntity.statusMessage( csstatus.AN_YING_ZHI_MENG_PLAYER_IS_FIGHTING )
				return
			if selfEntity.getState() != csdefine.ENTITY_STATE_FREE:
				playerEntity.endGossip( selfEntity )
				return
			
			if playerEntity.level < Const.AN_YING_ZHI_MENG_LEVEL:
				playerEntity.statusMessage( csstatus.AN_YING_ZHI_MENG_PLAYER_LEVEL_NOT_ENOUGH )
				return
			if not playerEntity.isInTeam():
				playerEntity.statusMessage( csstatus.AN_YING_ZHI_MENG_NOT_IN_TEAM )
				return
			if not playerEntity.isTeamCaptain():
				playerEntity.statusMessage( csstatus.AN_YING_ZHI_MENG_IS_NOT_CAPTAIN )
				return
			if not playerEntity.allMemberIsInRange( Const.AN_YING_ZHI_MENG_DISTANCE ):
				playerEntity.statusMessage( csstatus.AN_YING_ZHI_MENG_PLAYER_NOT_IN_RANGE )
				return
			allMemberInRange = playerEntity.getAllMemberInRange( Const.AN_YING_ZHI_MENG_DISTANCE )	# �õ���Χ�����ж����Ա
			for member in allMemberInRange:
				if member.level < Const.AN_YING_ZHI_MENG_LEVEL:
					playerEntity.statusMessage( csstatus.AN_YING_ZHI_MENG_MEMBER_LEVEL_NOT_ENOUGH )
					return
			BigWorld.globalData[ "ToxinFrogMgr" ].onNotifySpawnBoss( selfEntity.spawnMB, playerEntity.base, playerEntity.getLevel(), playerEntity.getCamp() )
			playerEntity.endGossip( selfEntity )
		elif dlgKey == "NPCLeave.s1":
			playerEntity.endGossip( selfEntity )