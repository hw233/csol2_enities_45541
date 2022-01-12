# -*- coding: gb18030 -*-

import csdefine
import ECBExtend
import csconst
import Const
import csstatus
import cschannel_msgs
import time
from bwdebug import *
from SpaceCopyTeam import SpaceCopyTeam

LEAVE_GATE = 10001
CLOSE_SPACE = 10002
SPACE_LAST_TIME = 60 * 30

class SpaceCopyDestinyTrans( SpaceCopyTeam ):
	"""
	�����ֻظ���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopyTeam.__init__( self )
		self.bossID = ""

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�
		
		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		SpaceCopyTeam.onLoadEntityProperties_( self, section )
		
		if section["Space"].has_key( "bossID"):
			self.bossID = section[ "Space" ][ "bossID" ].readString( "className" )

	def packedDomainData( self, entity ):
		"""
		@param player:	������ʵ��
		"""
		data = { "dbID" 			: entity.databaseID,
				 "type" 			: entity.query( "destityTransSpaceType", None ),
				 "spaceKey"		: entity.databaseID,
				}
		if entity.teamMailbox:
			data[ "teamID" ] = entity.teamMailbox.id
			data[ "captainDBID" ] = entity.getTeamCaptainDBID()
			data[ "membersDBID" ] = entity.getTeamMemberDBIDs()
			if csdefine.DESTINY_ENTER_GATE_TEAM == entity.query( "destityTransSpaceType", None ):
				data["spaceKey"] = entity.getTeamCaptainDBID()
		return data

	def getCaptainLevel( self, baseMailbox ):
		"""
		�������MailBox��öӳ��ȼ�
		"""
		entity = BigWorld.entities.get( baseMailbox.id )
		if not entity:
			return
		level = entity.level
		if entity.teamMailbox:
			if entity.isTeamCaptain():
				level = entity.level
			else:
				captain = entity.getTeamCaptain()
				if captain:
					lelve = captain.level
		
		return level

	def packedSpaceDataOnEnter( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		"""
		packDict = SpaceCopyTeam.packedSpaceDataOnEnter( self, entity )
		
		type = entity.query( "destityTransSpaceType", None )
		if type == csdefine.DESTINY_ENTER_GATE_SINGLE:
			level = entity.level
		else:
			level = self.getCaptainLevel( entity )

		packDict[ "level" ] = entity.level
		return packDict

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.cell.onEnterDestinyTransGate()
		baseMailbox.client.closeBoardInterface( 0 )		# �ر����̽���
		if not selfEntity.queryTemp( "tempHaveCome", False ):				# ֻ����һ��
			level = params[ "level" ]
			selfEntity.base.createSpawnEntities( { "level" : level } )		# ˢ������
			selfEntity.setTemp( "tempHaveCome", True )
			selfEntity.setTemp( "copyStartTime", time.time() )				# ������ʼʱ��
			selfEntity.addTimer( SPACE_LAST_TIME, 0.0, CLOSE_SPACE )
		
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, selfEntity.queryTemp( "copyStartTime" ) )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, SPACE_LAST_TIME )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		SpaceCopyTeam.onLeaveCommon( self, selfEntity, baseMailbox, params )
		
		baseMailbox.cell.setTemp( "last_space_type",  self.getSpaceType() )
		baseMailbox.cell.onLeaveDestinyTransGate()

	def onRoleDie( self, role, killer ):
		"""
		�������
		"""
		if role.queryTemp( "livePoint", 0  ) <= 0:
			# ��������
			role.client.desTrans_msgs( csdefine.DESTINY_TRANS_FAILED_GATE )
			role.addTimer( 3.0, 0, ECBExtend.WAIT_ROLE_REVIVE_PRE_SPACE_CBID )
			return
		
		# �ȴ������ť����
		autoReviveTimer= role.addTimer( 10.0, 0, ECBExtend.ROLE_UESE_LIVE_POINT_REVIE_CBID )
		role.setTemp( "autoReviveTimer", autoReviveTimer )

	def onOneTypeMonsterDie( self, selfEntity, monsterID, monsterClassName ):
		"""
		����֪ͨ�����ڸ����Լ����ˣ����ݹ����className����ͬ��������
		"""	
		if monsterClassName != self.bossID:
			selfEntity.monsterCount -= 1
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, selfEntity.monsterCount  )
		else:
			selfEntity.bossCount -= 1
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, selfEntity.bossCount )
		
		if selfEntity.bossCount <= 0 and selfEntity.monsterCount <= 0 :
			self.gatePassed( selfEntity )

	def gatePassed( self, selfEntity ):
		"""
		ͨ��
		"""
		for e in selfEntity._players:
			e.cell.onPassedGate()

		selfEntity.addTimer( 3.0, 0.0, LEAVE_GATE )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		SpaceCopyTeam.onTimer( self, selfEntity, id, userArg )
		if userArg == LEAVE_GATE:
			self.roleLeaveGate( selfEntity )
		
		if userArg == CLOSE_SPACE:
			self.closeSpace( selfEntity )

	def roleLeaveGate( self, selfEntity ):
		"""
		����뿪�ؿ�
		"""
		for e in selfEntity._players:
			role = BigWorld.entities.get( e.id )
			if role:
				role.gotoForetime()
			else:
				e.cell.gotoForetime()

	def closeSpace( self, selfEntity ):
		"""
		�رո���
		"""
		for e in selfEntity._players:
			if not ( selfEntity.bossCount <= 0 and selfEntity.monsterCount <= 0 ):
				e.cell.onFailedGate()
			
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].gotoForetime()
			else:
				e.cell.gotoForetime()