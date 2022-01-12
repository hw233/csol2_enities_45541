# -*- coding: gb18030 -*-
#
# SpaceDomainShenGuiMiJing.py

"""
���������ظ���domain
"""

import Language
import BigWorld
import csconst
import csstatus
from bwdebug import *
import Function
from SpaceDomainCopyTeam import SpaceDomainCopyTeam
import csdefine

# ������
class SpaceDomainWuYaoWang(SpaceDomainCopyTeam):
	"""
	���������ظ����������˽������������ӽ��ĸ�����ֻ�жӳ����ܴ�������
	"""
	def __init__( self ):
		"""
		"""
		SpaceDomainCopyTeam.__init__( self )
		
	def teleportEntity( self, position, direction, baseMailbox, params ):
		"""
		define method.
		����һ��entity��ָ����space��
		@type position : VECTOR3, 
		@type direction : VECTOR3, 
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: һЩ���ڸ�entity����space�Ķ�������� (domain����)
		@type params : PY_DICT = None
		"""
		SpaceDomainCopyTeam.teleportEntity( self, position, direction, baseMailbox, params )
		self.teleportTeamMembers( position, direction, baseMailbox, params )
	
	def teleportTeamMembers( self, position, direction, baseMailbox, params ):
		"""
		�Ѷ��Ѵ��븱��
		"""				
		isCallTeamMember = params.get( "isCallTeamMember", False )
		membersMailboxs = params.get( "membersMailboxs", [] )
		mailbox = params.get( "mailbox", 0 )
		if isCallTeamMember:	# �����Ҫ���Ͷ�Ա����
			for membersMailbox in membersMailboxs:
				if membersMailbox.id != mailbox.id:
						membersMailbox.cell.gotoSpace( spaceDomain.name, ( 131.505, 1.91, -96.102 ), ( 0, 0, 0 ) )
