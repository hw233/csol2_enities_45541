# -*- coding: gb18030 -*-
#
# 
#

from bwdebug import *
from NPC import NPC
import csdefine
import csstatus

class ProtectTongNPC( NPC ):
	"""
	��������NPC
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		NPC.__init__( self )