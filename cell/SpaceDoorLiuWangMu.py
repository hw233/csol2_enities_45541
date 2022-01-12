# -*- coding: gb18030 -*-
#
# $Id: SpaceDoor.py,v 1.20 2008-08-07 08:15:50 phw Exp $

"""
�л���ʵ�塣
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
	�����ʵ�壬�ṩ��ҽ�ɫ�л������Ĳ�����
		@ivar destSpace:	Ŀ�곡����ʶ
		@type destSpace:	string
		@ivar destPosition:	Ŀ�������
		@type destPosition:	vector3
	"""
	def __init__(self):
		"""
		���캯����
		"""
		SpaceDoor.__init__(self)
	
	def onEnterDoor( self, role ):
		"""
		��ҽ��봫���Ŵ���
		"""
		if BigWorld.globalData.has_key("AS_LiuWangMu") and self.floorNum <= BigWorld.globalData["AS_LiuWangMu"]:
			role.beforeEnterSpaceDoor( self.destPosition, self.destDirection )
			role.gotoSpace( self.destSpace, self.destPosition, self.destDirection )
		else :
			role.statusMessage( csstatus.SPACEDOOR_IS_NOT_OPEN )
	
