# -*- coding: gb18030 -*-
import time
import BigWorld

from SpaceCopyTeam import SpaceCopyTeam
from GameObject import GameObject

import csdefine
import ECBExtend
import csconst
import Const
import cschannel_msgs
import ShareTexts as ST


CLOSE_COPY_WIN_USERARG      = 1					# �رո�����ʤtimer���
CLOSE_COPY_LOSE_USERARG		= 2					# �رո���ʧ��timer���

ENTERN_SGMJ_MENBER_DISTANCE = 5					# �������

WU_YAO_WANG						= [ "20742059", "20742060", "20742061" ]		# ��������className
QUEST_WU_YAO_WANG_BAO_ZANG_ID 	= 40301003		# ����ǰ�ڸ�������id

ALL_MONSTERS_COUNT = 50							# ˢ������
SPACE_LAST_TIME = 1800							# ��������ʱ��

class SpaceCopyWuYaoWang( SpaceCopyTeam ):
	"""
	���������ؽű�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopyTeam.__init__( self )
		self.isSpaceCalcPkValue = True
		self.recordKey = "wuyaowangbaozang_record"

	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		SpaceCopyTeam.load( self, section )

	def packedDomainData( self, entity ):
		"""
		����SpaceDomainShenGuiMiJingʱ�����ݲ���
		"""
		d = { 'dbID' : entity.databaseID, 'spaceKey' : entity.databaseID }
		if entity.teamMailbox:
			# �Ѽ�����飬ȡ��������
			d["spaceKey"] = entity.teamMailbox.id
			d["teamID"] = entity.teamMailbox.id
			d["captainDBID"] = entity.getTeamCaptainDBID()
			d["membersDBID"] = entity.getTeamMemberDBIDs()
			d["mailbox"] = entity.base
			# ȡ�����ж�Աbasemailboxs
			teamMemberMailboxsList = entity.getTeamMemberMailboxs()
			if entity.getTeamCaptainMailBox() in teamMemberMailboxsList:
				teamMemberMailboxsList.remove( entity.getTeamCaptainMailBox() )
			d["membersMailboxs"] = teamMemberMailboxsList

			# ���ö���ƽ���ȼ�����ߵȼ�
			if entity.isTeamCaptain():
				d["teamLevel"] = entity.level
				d["teamMaxLevel"] = min( entity.level + 3, csconst.ROLE_LEVEL_UPPER_LIMIT )

				if entity.queryTemp( "onEnterWuYaoWangBaoZang" ) == entity.teamMailbox.id:	# ����ӳ����������
					d["isCallTeamMember"] = False
				else:
					d["isCallTeamMember"] = True

		d[ "difficulty" ] = entity.popTemp( "WuYaoWangEnterType" )
		return d

	def packedSpaceDataOnEnter( self, entity ):
		"""
		"""
		packDict = SpaceCopyTeam.packedSpaceDataOnEnter( self, entity )
		if entity.teamMailbox:
			packDict[ "teamID" ] =  entity.teamMailbox.id

		return packDict

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		��������������
		"""
		if baseMailbox and params[ "databaseID" ] not in selfEntity._enterRecord:
			baseMailbox.cell.remoteAddActivityCount( selfEntity.id, csdefine.ACTIVITY_SHI_LUO_BAO_ZHANG, self.recordKey )
			
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		# ����֮��������Ӧ�����������teamID������Ӧ�Ķ����
		if BigWorld.entities.has_key( baseMailbox.id ):
			player = BigWorld.entities[baseMailbox.id]
			if player.isInTeam():
				player.setTemp( "onEnterWuYaoWangBaoZang", params['teamID'] )
				if player.has_quest( QUEST_WU_YAO_WANG_BAO_ZANG_ID ):
					player.setQuestVal( QUEST_WU_YAO_WANG_BAO_ZANG_ID, "teamID", player.getTeamMailbox().id )

		if not selfEntity.queryTemp( "tempHaveCome", False ):	# ֻ����һ��
			selfEntity.setTemp( "tempHaveCome", True )

		# �������û�п�ʼ��ʱ
		if not selfEntity.queryTemp( "copyStartTime", 0 ):
			selfEntity.setTemp( "copyStartTime", time.time() )
			selfEntity.addTimer( SPACE_LAST_TIME, 0, CLOSE_COPY_LOSE_USERARG )	# 30min��رո���

		#��������ʹ��
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEVEL, 		"" )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_COPY_TITLE, cschannel_msgs.ACTIVITY_WU_YAO_WANG )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, selfEntity.queryTemp( "copyStartTime" ) )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, SPACE_LAST_TIME )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, selfEntity.monsterCount )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, selfEntity.bossCount )

		baseMailbox.client.startCopyTime( SPACE_LAST_TIME - int( time.time() - selfEntity.queryTemp( "copyStartTime" ) ) )	# ֪ͨ�ͻ��˸�������ʱ

		baseMailbox.cell.checkTeamInCopySpace( selfEntity.base )	# �����븱����ʱ���Ƿ��ж��飬��ֹ������������������û�ڶ�����

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity׼���뿪spaceʱ��֪ͨ��
		"""
		SpaceCopyTeam.onLeaveCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.client.endCopyTime()

	def onOneTypeMonsterDie( self, selfEntity, monsterID, monsterClassName ):
		"""
		����֪ͨ�����ڸ����Լ����ˣ����ݹ����className����ͬ��������
		"""
		if monsterClassName in WU_YAO_WANG:			# ���ɱ����boss������֮Ӱ
			uskCount = None
			monster = BigWorld.entities.get( monsterID )
			if monster and monster.isReal():
				uskCount = monster.queryTemp( "uskCount" )		# �����������������������Ӱ�ҵ�����ÿ������ͼ�����
			if uskCount is not None and uskCount <= 0:
				selfEntity.onGodWeaponWuYao()
			self.broadcastInCopy( selfEntity, cschannel_msgs.BCT_FUBEN_WU_YAO_WANG_BAO_ZANG_OVER )
			for e in selfEntity._players:
				player = BigWorld.entities[e.id]
				if player.has_quest( QUEST_WU_YAO_WANG_BAO_ZANG_ID ):
					e.cell.questTaskIncreaseState( QUEST_WU_YAO_WANG_BAO_ZANG_ID, 1 )	# �������
					e.cell.spellTarget( 122169002, e.id )		# ������ɺ󣬼�һ��90s buff(��ֹ�½ӵ����񣬽���õĸ���)
			selfEntity.addTimer( 60.0, 0.0, CLOSE_COPY_WIN_USERARG )				# 30��󣬹رո�����ʤ
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 0 )
			selfEntity.setTemp( "bossCount", 0 )
		else:
			tempCount = selfEntity.queryTemp( "allMonsterCount" )
			tempCount -= 1
			selfEntity.setTemp( "allMonsterCount", tempCount )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, tempCount )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if userArg == CLOSE_COPY_WIN_USERARG:		# �رո�������ʤ
			self.closeCopy( selfEntity, 1 )

		elif userArg == CLOSE_COPY_LOSE_USERARG:		# �رո�����ʧ��
			self.closeCopy( selfEntity, 0 )

		else:
			SpaceCopyTeam.onTimer( self, selfEntity, id, userArg )

	def broadcastInCopy( self, selfEntity, msg ):
		"""
		�����й㲥
		"""
		for baseMailBox in selfEntity._players:
			baseMailBox.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", msg, [] )

	def closeCopy( self, selfEntity, isWin ):
		"""
		�����ر�
		"""
		if not isWin:	# ���ʧ��
			for e in selfEntity._players:
				player = BigWorld.entities[e.id]
				if player.has_quest( QUEST_WU_YAO_WANG_BAO_ZANG_ID ):
					e.cell.setQuestVal( QUEST_WU_YAO_WANG_BAO_ZANG_ID, "questHasLose", True )	# ���ô�����ʧ��
					e.cell.questTaskFailed( QUEST_WU_YAO_WANG_BAO_ZANG_ID, 1 )					# ֪ͨ����ʧ��

		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				player = BigWorld.entities[ e.id ]
				if player.isInTeam():
					player.removeTemp( "onEnterWuYaoWangBaoZang" )
				BigWorld.entities[ e.id ].gotoForetime()
			else:
				e.cell.removeTemp( "onEnterWuYaoWangBaoZang" )
				e.cell.gotoForetime()

		SpaceCopyTeam.closeCopy( self, selfEntity, isWin )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		ĳrole�ڸø���������
		"""
		pass