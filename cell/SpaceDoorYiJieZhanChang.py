# -*- coding: gb18030 -*-
#

import BigWorld
import Role
from bwdebug import *
from SpaceDoor import SpaceDoor

class SpaceDoorYiJieZhanChang(SpaceDoor):
	# 异界战场内传送门
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceDoor.__init__( self )
	
	def onEnterDoor( self, role ):
		"""
		玩家进入传送门处理
		"""
		role.yiJieRequestExit()
	
