# -*- coding: gb18030 -*-


import time
import Math
from SpaceCopy import SpaceCopy
from bwdebug import *
import cschannel_msgs
import Love3
import csdefine
import csconst
import BigWorld


class SpaceCopyCampFengHuoLianTian( SpaceCopy ):
	"""
	��Ӫ�����������
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
		self.isClose = False
		
	def closeCampFengHuoRoom( self ):
		# define method.
		# ��ǰ������ĳ��ս�� ��tongmanager �ر����з���
		if self.isClose:
			return
		
		self.isClose = True
		self.cell.closeCampFengHuoRoom()
		
