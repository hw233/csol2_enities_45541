# -*- coding: gb18030 -*-
#
# $Id: GameObject.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
GameObject基类
"""
import BigWorld
from bwdebug import *
import csdefine
from NPC import NPC
from keys import *

class TongBuilding( NPC ):
	"""
	帮会建筑物基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		NPC.__init__( self )
		self.utype = csdefine.ENTITY_TYPE_MISC
		self.setSelectable( False )
		
# GameObject.py
