# -*- coding: gb18030 -*-
#
# $Id: SpaceDoor.py,v 1.20 2008-08-07 08:15:50 phw Exp $

"""
切换点实体。
"""

import BigWorld
import Role
from bwdebug import *
from SpaceDoor import SpaceDoor
import csdefine
import csconst
import math
import csstatus

class SpaceDoorLiuWangMu(SpaceDoor):
	"""
	出入口实体，提供玩家角色切换场景的操作。
		@ivar destSpace:	目标场景标识
		@type destSpace:	string
		@ivar destPosition:	目标点坐标
		@type destPosition:	vector3
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceDoor.__init__(self)
	
	def onEnterDoor( self, role ):
		"""
		玩家进入传送门处理
		"""
		if BigWorld.globalData.has_key("AS_LiuWangMu") and self.floorNum <= BigWorld.globalData["AS_LiuWangMu"]:
			role.beforeEnterSpaceDoor( self.destPosition, self.destDirection )
			role.gotoSpace( self.destSpace, self.destPosition, self.destDirection )
		else :
			role.statusMessage( csstatus.SPACEDOOR_IS_NOT_OPEN )
	
