# -*- coding: gb18030 -*-
#
# WXMonster�� 2009-10-08 SongPeifang
#

from Monster import Monster
from bwdebug import *
import csdefine
import BigWorld
import cschannel_msgs


class WXMonster( Monster ):
	"""
	ǧ�궾��(ToxinFrog)��ţħ��(BovineDevil)��������(SnakeBoss)������ħ(JuLingMo)
	��������(HunterMonster)������ʦ(JishiMonster)�����ش�(HandiMonster)��Х���(XiaotianMonster)
	�Ļ���ű��ļ�
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		self.bornNPC = True
		self.callMonsterID		= ""
		self.callMonsterCount = 0
		self.fightingText		= ""
		self.freeText			= ""
		self.fightOption		= ""
		self.leaveOption		= ""
		self.fightSay			= ""
		self.dieSay				= ""
		self.dieNotifyText		= ""
		self.dieDelKey			= ""


	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
		# ��ʼ���������ݷ���ǰͷ
		Monster.initEntity( self, selfEntity )
		if not self.bornNPC:
			selfEntity.callMonsters( self.callMonsterID, self.callMonsterCount )


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
				playerEntity.setGossipText( self.fightingText )
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
			if selfEntity.getState() != csdefine.ENTITY_STATE_FREE:
				playerEntity.endGossip( selfEntity )
				return

			selfEntity.say( self.fightSay )
			monsLvl = playerEntity.level
			selfEntity.setTemp( 'call_monster_level', monsLvl )
			selfEntity.setAINowLevel( 1 )
			selfEntity.changeToMonster( monsLvl, playerEntity.id )
			count = 3
			if playerEntity.isInTeam():
				teamMembers = playerEntity.teamMembers
				if len( teamMembers ) >= 4:
					# �����4����4�����ϵ���һ�����ɱ�����ٻ�14��С��
					count = 14
				elif len( teamMembers ) >= 3:
					# �����3����3�����ϵ���һ�����ɱ�����ٻ�9��С��
					count = 9
				elif len( teamMembers ) >= 2:
					# �����2��һ�����ɱ�����ٻ�6��С��
					count = 6
			selfEntity.callMonsters( self.callMonsterID, count )	# �ٻ�С��
			playerEntity.endGossip( selfEntity )
		elif dlgKey == "NPCLeave.s1":
			playerEntity.endGossip( selfEntity )

	def dieNotify( self, selfEntity, killerID ):
		"""
		����֪ͨ
		"""
		Monster.dieNotify( self, selfEntity, killerID )
		if self.dieSay != "":
			selfEntity.say( self.dieSay )
		if self.dieNotifyText != "":
			bootyOwner = selfEntity.getBootyOwner()
			if BigWorld.entities.has_key( bootyOwner[0] ):
				killerID = bootyOwner[0]
			if not BigWorld.entities.has_key( killerID ):
				ERROR_MSG( "DieNotify of %s script counld not find player id: %s:" % ( selfEntity.getName(), killerID ) )
				return
			killer = BigWorld.entities[killerID]
			if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
				owner = killer.getOwner()
				if owner.etype == "MAILBOX" :
					ERROR_MSG( "%s��idΪ%s��Entityɱ����" % ( selfEntity.getName(), killerID ) )
					return
				killer = owner.entity
			killerName = killer.playerName
			if bootyOwner[1] != 0 and BigWorld.entities.has_key( killer.captainID ):
				killer = BigWorld.entities[ killer.captainID ]
				killerName = cschannel_msgs.CELL_WXMONSTER_2 % killer.playerName
			notifyStr = self.dieNotifyText % killerName
			selfEntity.sysBroadcast( notifyStr )
		if self.dieDelKey != "":
			BigWorld.globalData[ self.dieDelKey ] = False
			
	def getSpawnPos( self, selfEntity ):
		return selfEntity.spawnPos
		
	def getBootyOwner( self, selfEntity ):
		"""
		virtual method
		���ս��Ʒӵ����
		"""
		bootyOwner = selfEntity.queryTemp( "ToxinFrog_bootyOwner", () )
		if bootyOwner: return bootyOwner
		return Monster.getBootyOwner( self, selfEntity )
		