# -*- coding: gb18030 -*-
import csconst
from SpaceCopyYXLMPVP import SpaceCopyYXLMPVP

class SpaceCopyCampYingXiong( SpaceCopyYXLMPVP ):
	#��ӪӢ�������ű�
	def __init__( self ):
		SpaceCopyYXLMPVP.__init__( self )
	
	def packedDomainData( self, entity ):
		"""
		"""
		
		d = { "dbID" : entity.databaseID, "spaceKey":entity.databaseID}

		if entity.teamMailbox:
			# �Ѽ�����飬ȡ��������
			d["teamID"] = entity.teamMailbox.id
			d["captainDBID"] = entity.getTeamCaptainDBID()
			d["membersDBID"] = entity.getTeamMemberDBIDs()
			# ȡ�����ж�Աbasemailboxs
			teamMemberMailboxsList = entity.getTeamMemberMailboxs()
			if entity.getTeamCaptainMailBox() in teamMemberMailboxsList:
				teamMemberMailboxsList.remove( entity.getTeamCaptainMailBox() )
				
			if entity.isTeamCaptain():
				d["teamLevel"] = entity.level
				d["teamMaxLevel"] = min( entity.level + 3, csconst.ROLE_LEVEL_UPPER_LIMIT )
				d[ "membersMailboxs" ] = teamMemberMailboxsList
			
			d[ "teamInfos" ] = entity.popTemp( "CYX_teamInofs", [] )
			d["spaceKey"] = entity.teamMailbox.id	
			entity.baoZangPVPInfosReset()
		return d
	
	def getEnterInf( self, playerEntity ):
		# ��ȡ����������
		return self.spaceBirthInf[ playerEntity.yingXiongCampTeamIndex() ]