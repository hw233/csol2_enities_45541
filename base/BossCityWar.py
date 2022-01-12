# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.1 2007-09-24 07:04:33 kebiao Exp $

"""
NPC基类
"""

import BigWorld
from bwdebug import *
from Monster import Monster

class BossCityWar( Monster ):
	"""
	Monster基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		Monster.__init__( self )

# NPC.py
