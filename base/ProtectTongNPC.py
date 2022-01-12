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
	保护帮派NPC
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		NPC.__init__( self )