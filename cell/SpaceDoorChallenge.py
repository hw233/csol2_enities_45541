# -*- coding: gb18030 -*-
#

import BigWorld
import Role
from bwdebug import *
from SpaceDoor import SpaceDoor
import csdefine
import csconst
import csstatus

class SpaceDoorChallenge(SpaceDoor):
	# 挑战副本场景切换
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceDoor.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_SPACE_CHALLENGE_DOOR )
	
	def onEnterDoor( self, role ):
		"""
		玩家进入传送门处理
		"""
		role.challengeSpacePassDoor()
	
