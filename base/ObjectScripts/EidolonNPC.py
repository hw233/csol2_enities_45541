# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $


import BigWorld
from bwdebug import *
import csdefine
import csstatus
from Chapman import Chapman

class EidolonNPC( Chapman ):
	"""
	小精灵NPC基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		Chapman.__init__( self )
		
	