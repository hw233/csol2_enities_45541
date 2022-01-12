# -*- coding: gb18030 -*-
#
#$Id:$

import BigWorld
from bwdebug import *
import csdefine
import csconst
import csstatus
from SpaceCopyTeam import SpaceCopyTeam

CLOSE_COPY				= 3	  # ��ǹرո���
CLOSE_WUDAO				= 4   # �ر�������

class SpaceCopyWuDao( SpaceCopyTeam ):
	"""
	�����ḱ���ռ�
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopyTeam.__init__( self )
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = True

	def load( self, section ):
		"""
		�������м�������

		@type section : PyDataSection
		@param section : python data section load from npc's coonfig file
		"""
		SpaceCopyTeam.load( self, section )

		# ��������С��������
		self.enterLimitLevel = section[ "Space" ][ "enterLimitLevel" ].asInt


	def packedDomainData( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		@param entity: ͨ��Ϊ���
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		# ����databaseID������space domain�ܹ���������ȷ�ļ�¼�����Ĵ����ߣ�
		# �Ҳ��õ�������ڶ�ʱ���ڣ��ϣ����ߺ�����ʱ�һظ��������⣻
		return { 'roleDBID' : entity.databaseID, "level": entity.level, "playerName":entity.playerName }

	def checkDomainIntoEnable( self, entity ):
		"""
		��cell�ϼ��ÿռ���������
		"""
		if entity.level < self.enterLimitLevel:
			return csstatus.WU_DAO_NO_WAR_LEVEL

		return csstatus.SPACE_OK

	def packedSpaceDataOnEnter( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		"""
		packDict = SpaceCopyTeam.packedSpaceDataOnEnter( self, entity )
		packDict[ "playerDBID" ] = entity.databaseID
		return packDict

	def packedSpaceDataOnLeave( self, entity ):
		# �������뿪����
		packDict = SpaceCopyTeam.packedSpaceDataOnLeave( self, entity )
		packDict[ "state" ] = entity.getState()
		return packDict

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		playerDBID = params["playerDBID"]
		if playerDBID not in selfEntity.databaseIDList:
			selfEntity.databaseIDList.append( playerDBID )

		player = baseMailbox.cell
		player.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )		# ���������ᣬ��ս

		if BigWorld.entities.has_key( baseMailbox.id ):
			player = BigWorld.entities[ baseMailbox.id  ]
			player.setTemp( "wudao_sclass", selfEntity.className )	# ����������ڸ����Ľű����֣��Ա���Һ͸�������ͬһ��serverʱ�����һظ���
			player.setTemp( "lastPkMode", player.pkMode )

		baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )	#����Ϊ��ƽģʽ
		baseMailbox.cell.lockPkMode()										#����pkģʽ����������

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity׼���뿪spaceʱ��֪ͨ��
		"""
		SpaceCopyTeam.onLeaveCommon( self, selfEntity, baseMailbox, params )
		if not selfEntity.hasClearNoFight:		# ���û���������ɫ����սЧ��
			baseMailbox.cell.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )
			return

		baseMailbox.cell.setSysPKMode( 0 )
		if BigWorld.entities.has_key( baseMailbox.id ):
			player = BigWorld.entities[ baseMailbox.id  ]
			player.unLockPkMode()		# ����pkģʽ
			player.setPkMode( baseMailbox.id, player.queryTemp( "lastPkMode" ) )	# �ָ�ԭ��pkMode
		else:
			baseMailbox.cell.unLockPkMode()		# ����pkģʽ
			baseMailbox.cell.setPkMode( baseMailbox.id, csdefine.PK_CONTROL_PROTECT_RIGHTFUL )	# �ָ�������ģʽ

		if not selfEntity.queryTemp( "hasCloseWuDao" ):		# ��������ḱ��û�йرգ�������;�˳�����
			if len( selfEntity._players ) == 1: 			# ����������һ���ˣ�ֱ�ӻ�ʤ
				selfEntity._players[0].client.onStatusMessage( csstatus.WU_DAO_OUT, "" )
				selfEntity._players[0].onWuDaoOver( selfEntity._players[0], 1 ) # ֪ͨ���������������ʤ��
				self.closeWuDao( selfEntity ) # �ر�������

		if params[ "state" ] == csdefine.ENTITY_STATE_DEAD:
			baseMailbox.cell.reviveActivity() # ��Ѫ��������

	def onPlayerDied( self, selfEntity, killer, killerDBID, beKiller, beKillerDBID ):
		"""
		�������
		"""
		for e in selfEntity._players:
			e.client.onStatusMessage( csstatus.WU_DAO_LEAVA, "" )

		self.onWuDaoOver( killer.base, killerDBID, killer.level, 1 )
		self.onWuDaoOver( beKiller.base, beKillerDBID, beKiller.level, 0 )
		selfEntity.databaseIDList.remove( beKillerDBID )
		killer.clearBuff( [csdefine.BUFF_INTERRUPT_INVINCIBLE_EFFECT] )

		selfEntity.setTemp( "hasCloseWuDao", True )		# �����Ѿ��ر������ᣬ��ֹ�������������CLOSE_WUDAOǰ�˳�����
		selfEntity.addTimer( 10, 0, CLOSE_WUDAO )		# 10������claseWuDao

	def onWuDaoOver( self, playerBase, dbid, level, result = 0 ):
		"""
		������һ�����������ˣ�֪ͨ������
		"""
		BigWorld.globalData[ "WuDaoMgr" ].onWuDaoOverFromSpace( playerBase, dbid, level, result )	# ֪ͨ�������������ĳ��ս�����

	def closeWuDao( self, selfEntity ):
		"""
		���������ر�������
		"""
		selfEntity.setTemp( "hasCloseWuDao", True )		# �����Ѿ��ر�������

		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].challengeActivityTransmit( csconst.TRANSMIT_TYPE_WUDAO )
			else:
				e.cell.challengeActivityTransmit( csconst.TRANSMIT_TYPE_WUDAO )

		selfEntity.addTimer( 10.0, 0.0, CLOSE_COPY )

	def clearNoFight( self , selfEntity ):
		for e in  selfEntity._players:
			# ����PKģʽ
			e.cell.unLockPkMode()
			e.cell.setPkMode( e.id, csdefine.PK_CONTROL_PROTECT_NONE )
			e.cell.lockPkMode()
			# �����ս
			e.cell.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )
			# �㲥��ҿ���
			e.client.onStatusMessage( csstatus.WU_DAO_CLEAR_NO_FIGHT, "" )

		selfEntity.hasClearNoFight = True		# ����Ѿ��������ɫ����սЧ��

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		ĳrole�ڸø���������
		"""
		if not killer:	# û�ҵ�ɱ���ߣ�����������������ֱ�ӷ���
			DEBUG_MSG( "player( %s ) has been killed,can't find killer." % role.getName() )
			return
		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = killer.getOwner()
			if owner.etype == "MAILBOX" : return
			killer = owner.entity
		if killer.getState() == csdefine.ENTITY_STATE_DEAD:		# ���ɱ�����Ѿ��������򷵻�
			return

		role.statusMessage( csstatus.WU_DAO_LOSE )
		killer.statusMessage( csstatus.WU_DAO_WIN )

		if killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			spaceBase = role.getCurrentSpaceBase()
			spaceEntity = BigWorld.entities.get( spaceBase.id )
			if spaceEntity and spaceEntity.isReal():
				self.onPlayerDied( spaceEntity, killer, killer.databaseID, role, role.databaseID )
			else:
				spaceBase.cell.remoteScriptCall( "onPlayerDied", ( killer, killer.databaseID, role, role.databaseID ) )

		role.client.onStatusMessage( csstatus.WU_DAO_JOIN_REWARD, "" )
