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
	# ��ս���������л�
	def __init__(self):
		"""
		���캯����
		"""
		SpaceDoor.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_SPACE_CHALLENGE_DOOR )
	
	def onEnterDoor( self, role ):
		"""
		��ҽ��봫���Ŵ���
		"""
		role.challengeSpacePassDoor()
	
