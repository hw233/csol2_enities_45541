# -*- coding: gb18030 -*-
import csstatus
import Const
import ECBExtend

from SpaceCopyTemplate import SpaceCopyTemplate

class SpaceCopyTeamTemplate( SpaceCopyTemplate ):
	def __init__( self ):
		SpaceCopyTemplate.__init__( self )
	
	
	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		SpaceCopyTemplate.onLeaveCommon( self, selfEntity, baseMailbox, params )
	
	def packedDomainData( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		@param entity: ͨ��Ϊ���
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		d = SpaceCopyTemplate.packedDomainData( self, entity )
		if entity.teamMailbox:
			# �Ѽ�����飬ȡ��������
			d["teamID"] = entity.teamMailbox.id
			d["captainDBID"] = entity.getTeamCaptainDBID()
			d["membersDBID"] = entity.getTeamMemberDBIDs()
			d["spaceKey"] = entity.teamMailbox.id
		return d
	
	def packedSpaceDataOnEnter( self, player ):
		"""
		"""
		packDict = SpaceCopyTemplate.packedSpaceDataOnEnter( self, player )
		if player.teamMailbox:
			packDict[ "teamID" ] = player.teamMailbox.id

		return packDict
	
	def checkDomainIntoEnable( self, entity ):
		"""
		��cell�ϼ��ÿռ���������
		"""
		if entity.teamMailbox:
			return csstatus.SPACE_OK
		else:
			return csstatus.SPACE_MISS_NOTTEAM
	
	def nofityTeamDestroy( self, selfEntity, teamEntityID ):
		"""
		�����ɢ
		"""
		selfEntity.addTimer( 1.0, 0.0, Const.SPACE_TIMER_ARG_KICK )
		selfEntity.addTimer( 10.0, 0.0, Const.SPACE_TIMER_ARG_CLOSE )
	
	def onLeaveTeam( self, playerEntity ):
		"""
		"""
		if playerEntity.queryTemp( 'leaveSpaceTime', 0 ) == 0:
			playerEntity.leaveTeamTimer = playerEntity.addTimer( 5, 0, ECBExtend.LEAVE_TEAM_TIMER )
		playerEntity.setTemp( "leaveSpaceTime", 5 )
		playerEntity.client.onLeaveTeamInSpecialSpace( 5 )

	def onLeaveTeamProcess( self, playerEntity ):
		"""
		��Ա�뿪���鴦��
		"""
		playerEntity.gotoForetime()