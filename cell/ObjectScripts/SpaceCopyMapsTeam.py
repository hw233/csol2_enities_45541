# -*- coding: gb18030 -*-

import BigWorld
import csstatus
import Const
import ECBExtend
from bwdebug import *
from SpaceCopyMaps import SpaceCopyMaps

TIMER_CLOSE_ACT = 1

class SpaceCopyMapsTeam( SpaceCopyMaps ):
	"""
	���ͼ��Ӹ����ű�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopyMaps.__init__( self )
		self._isPickMembers = 0
		
	def load( self, section ):
		SpaceCopyMaps.load( self, section )
		self._isPickMembers = section[ "Space" ][ "pickMembers" ].asInt
	
	def packedDomainData( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		@param entity: ͨ��Ϊ���
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		# ����databaseID������space domain�ܹ���������ȷ�ļ�¼�����Ĵ����ߣ�
		# �Ҳ��õ�������ڶ�ʱ���ڣ��ϣ����ߺ�����ʱ�һظ��������⣻
		d = { 'dbID' : entity.databaseID }
		d[ "enterCopyKey" ] = self.className
		d[ "enterCopyNo" ] = self._spaceMapsNo
		d["teamID"] = entity.teamMailbox.id			#ȥ���Ƿ��ж�����жϣ����û�ж��飬��ֱ�������ﱨ��GRL
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
	
	def closeMapsCopy( self, playerEntity ):
		"""
		�رն��ͼ�������(��ҵ���)
		"""
		if BigWorld.cellAppData.has_key( selfEntity.getSpaceGlobalKey() ):
			del BigWorld.cellAppData[ selfEntity.getSpaceGlobalKey() ]
			
		BigWorld.globalData[ "SpaceManager" ].remoteCallDomain( self.className, "closeCopyItem", ( { "teamID": playerEntity.teamMailbox.id } ) )
	
	def onTimer( self, selfEntity, id, userArg ):
		"""
		ʱ�������
		"""
		if userArg == Const.SPACE_TIMER_ARG_LIFE:
			selfEntity.domainMB.closeCopyItem( { "teamID": selfEntity.copyKey } )
		else:
			SpaceCopyMaps.onTimer( self, selfEntity, id, userArg )
	
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