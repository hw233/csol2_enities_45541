# -*- coding: gb18030 -*-
#

import BigWorld
import Role
from bwdebug import *
from SpaceDoor import SpaceDoor

class SpaceDoorYiJieZhanChang(SpaceDoor):
	# ���ս���ڴ�����
	def __init__(self):
		"""
		���캯����
		"""
		SpaceDoor.__init__( self )
	
	def onEnterDoor( self, role ):
		"""
		��ҽ��봫���Ŵ���
		"""
		role.yiJieRequestExit()
	
