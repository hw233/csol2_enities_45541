# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
NPC基类
"""

import BigWorld
from bwdebug import *
import csdefine
from Monster import Monster

class TongNagual( Monster ):
	"""
	帮会守护神
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		Monster.__init__( self )

# TongNagual.py
