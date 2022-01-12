# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.1 2007-09-24 07:04:33 phw Exp $

"""
NPC基类
"""

import BigWorld
from bwdebug import *
from NPCObject import NPCObject

class NPC( NPCObject ):
	"""
	NPC基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		NPCObject.__init__( self )

# NPC.py
