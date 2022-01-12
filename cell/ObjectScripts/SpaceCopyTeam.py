# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyTeam.py,v 1.2 2008-08-01 03:31:46 kebiao Exp $

"""
"""
import BigWorld
import csstatus
import Const
import ECBExtend
from bwdebug import *
from SpaceCopy import SpaceCopy

class SpaceCopyTeam( SpaceCopy ):
	"""
	����ƥ��SpaceDomainCopyTeam�Ļ�����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopy.__init__( self )

	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		SpaceCopy.load( self, section )
		
	def checkDomainIntoEnable( self, entity ):
		"""
		��cell�ϼ��ÿռ���������
		"""
		if entity.teamMailbox:
			return csstatus.SPACE_OK
		else:
			return csstatus.SPACE_MISS_NOTTEAM
		
	def packedDomainData( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		@param entity: ͨ��Ϊ���
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		# ����databaseID������space domain�ܹ���������ȷ�ļ�¼�����Ĵ����ߣ�
		# �Ҳ��õ�������ڶ�ʱ���ڣ��ϣ����ߺ�����ʱ�һظ��������⣻
		d = SpaceCopy.packedDomainData( self, entity )
		if entity.teamMailbox:
			# �Ѽ�����飬ȡ��������
			d["teamID"] = entity.teamMailbox.id
			d["captainDBID"] = entity.getTeamCaptainDBID()
			d["membersDBID"] = entity.getTeamMemberDBIDs()
			d["spaceKey"] = entity.teamMailbox.id
		return d
	
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