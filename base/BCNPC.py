# -*- coding: gb18030 -*-
#
# �������NPC 2009-01-17 SongPeifang
#

import BigWorld
from bwdebug import *
from NPC import NPC

class BCNPC( NPC ):
	"""
	�������NPC
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		NPC.__init__( self )
		BigWorld.globalData["BCGameMgr"].registerBCNPC( self.lineNumber, self )
		
	def getLoginMembers( self, memberCount ):
		"""
		Define Method.
		���ñ���������
		"""
		BigWorld.globalData["BCGameMgr"].setMemberCount( self.lineNumber, memberCount )