# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.1 2007-09-24 07:04:33 kebiao Exp $

"""
Monster基类
"""

import BigWorld
from bwdebug import *
from NPC import NPC

class Monster( NPC ):
	"""
	Monster基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		NPC.__init__( self )

# Monster.py
