# -*- coding: gb18030 -*-


import time
import BigWorld
from Function import Function
import csdefine
import csstatus

TEAM_MEMBER_NEED 	= 3																	#��Ҫ�Ķ����Ա
MAX_LEVEL 			= 110																#���ȼ�

class FuncKuafuRemain( Function ):
	"""
	����丸���
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.level = section.readInt( "param1" )										#����ȼ�
		self.recordKey = "kuafu_record"
		self.spaceName = "fu_ben_kua_fu_shen_dian"
		self.questID = section.readInt( "param2" )										#����ID


	def do( self, player, talkEntity = None ):
		"""
		����丸������
		����
			�������������Ѷ�Ա����������
				������鵱ǰû�и�����
				Ҫ��������Ƕӳ���
				�ﵽ�ȼ�Ҫ��
				������������3�ˡ�
				�����Աû�н���������ġ�
			������������ֻ���Լ�һ���˽�ȥ��
				����ӡ�
				�ж��鸱�����ڡ�

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		
		if self.level > player.level:
			#��ҵȼ�����
			player.statusMessage( csstatus.KUA_FU_REMAIN_LEVEL_NOT_ARRIVE, self.level )
			return
			
		#if not player.hasPersistentFlag( csdefine.ENTITY_FLAG_KUA_FU_QUEST ):
			#û���������
			#player.statusMessage( csstatus.KUA_FU_REMAIN_QUEST_NOT_HAS, player.playerName )
			#return

		if not player.isInTeam():
			#���û�����
			player.statusMessage( csstatus.KUA_FU_REMAIN_NEED_TEAM )
			return

		if BigWorld.globalData.has_key( 'KuafuRemain_%i'%player.getTeamMailbox().id ):
			if player.isActivityCanNotJoin( csdefine.ACTIVITY_KUA_FU )  and player.query( "lastKuafuRemainTeamID", 0 ) != player.getTeamMailbox().id:
				player.statusMessage( csstatus.KUA_FU_REMAIN_HAS_ENTERED_TODAY, player.playerName )
				return
			player.gotoSpace(self.spaceName, (60.049, 24.756, 150.834), (0,0,0))
		else:
			#����û�и��������ߴ�������
			if not player.isTeamCaptain():
				player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
				return
			pList = player.getAllMemberInRange( 30 )
			
			if not len( pList ) >= 3 :
				player.statusMessage( csstatus.KUA_FU_REMAIN_ROLE_IS_ENOUGH_MEMBER )
				return

			for i in pList:
				if i.level < self.level:
					player.statusMessage( csstatus.KUA_FU_REMAIN_MEMBER_LEVEL_NOT_ARRIVE, i.playerName )
					return
				if i.isActivityCanNotJoin( csdefine.ACTIVITY_KUA_FU ) :
					player.statusMessage( csstatus.KUA_FU_REMAIN_HAS_ENTERED_TODAY, i.playerName )
					return
				#if not i.hasPersistentFlag( csdefine.ENTITY_FLAG_KUA_FU_QUEST ):
					#û���������
					#player.statusMessage( csstatus.KUA_FU_REMAIN_QUEST_NOT_HAS, i.playerName )
					#return

			pList.remove( player )
			player.gotoSpace(self.spaceName, (60.049, 24.756, 150.834), (0,0,0))
			player.set( "lastKuafuRemainTeamID", player.getTeamMailbox().id )
			for i in pList:
				i.set( "lastKuafuRemainTeamID", player.getTeamMailbox().id )
				i.gotoSpace(self.spaceName, (60.049, 24.756, 150.834), (0,0,0))

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True




class FuncKuafuBossTalk( Function ):
	"""
	����Ի�
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		pass


	def do( self, player, talkEntity = None ):
		"""
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		
		talkEntity.setNextRunAILevel( 0 )
		talkEntity.removeFlag( csdefine.ENTITY_FLAG_SPEAKER )


	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True

