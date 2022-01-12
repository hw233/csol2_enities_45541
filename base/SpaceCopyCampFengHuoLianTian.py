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
	阵营烽火连天活动副本
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
		self.isClose = False
		
	def closeCampFengHuoRoom( self ):
		# define method.
		# 提前结束掉某场战争 由tongmanager 关闭所有房间
		if self.isClose:
			return
		
		self.isClose = True
		self.cell.closeCampFengHuoRoom()
		
