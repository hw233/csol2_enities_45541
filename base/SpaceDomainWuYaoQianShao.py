# -*- coding: gb18030 -*-
#
# SpaceDomainWuYaoQianShao.py

"""
����ǰ�ڸ���domain
"""

import Language
import BigWorld
import csconst
import csstatus
from bwdebug import *
import Function
from SpaceDomainCopyTeam import SpaceDomainCopyTeam

# ������
class SpaceDomainWuYaoQianShao(SpaceDomainCopyTeam):
	"""
	����ǰ�ڸ����������˽������������ӽ��ĸ�����ֻ�жӳ����ܴ�������
	"""

	def findSpaceItem( self, params, createIfNotExisted = False ):
		"""
		virtual method.
		ģ�巽����ͨ��������params������space����ͬ���͵�space�в�ͬ�Ĵ���ʽ��
		���ش˷���ʱ�����ϸ��ղ����е�˵������ʵ�֡�
		
		@param params: dict; ������space�ű��е�packedDomainData()����
		@param createIfNotExisted: bool; ���Ҳ���ʱ�Ƿ񴴽�
		@return: instance of SpaceItem or None
		"""
		dbid = params.get( "dbID" )				# dbid����������֮��ص�ObjectScripts/SpaceCopy.py����ؽӿ�
		assert dbid is not None, "the key dbID is necessary."
		
		teamID = params.get( "teamID", 0 )		# get team entity's id
		spaceItem = None
		
		if teamID:
			# ������Ӳ��ܽ��븱��
			captainDBID = params.get( "captainDBID", 0 )
			mailbox = params.get( "mailbox", 0 )
			membersMailboxs = params.get( "membersMailboxs", [] )
			isCallTeamMember = params.get( "isCallTeamMember", False )
			spaceNumber = self.getSpaceNumberByTeamID( teamID )
			if spaceNumber:
				# �ҵ�������������space
				spaceItem = self.getSpaceItem( spaceNumber )
			else:
				if dbid == captainDBID  and createIfNotExisted:		# ����ӳ����ܴ����¸���
					spaceItem = self.createSpaceItem( params )
					if isCallTeamMember:	# �����Ҫ���Ͷ�Ա����
						for membersMailbox in membersMailboxs:
							if membersMailbox.id != mailbox.id:
								membersMailbox.cell.gotoSpace( self.name, ( 131.505, 1.91, -96.102 ), ( 0, 0, 0 ) )	# �����ж�ԱҲ���͵�������
		
		return spaceItem
