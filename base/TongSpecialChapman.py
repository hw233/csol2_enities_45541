# -*- coding: gb18030 -*-
#
# $Id: Chapman.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
TongSpecialChapman
"""

import BigWorld
from bwdebug import *
import csdefine
import csstatus
from NPC import NPC

class TongSpecialChapman( NPC ):
	"""
	帮会领地特殊商人NPC
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		NPC.__init__( self )
		
# Chapman.py