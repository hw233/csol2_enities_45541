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


class SpaceCopyTongFengHuoLianTian( SpaceCopy ):
	"""
	帮会夺城战复赛（烽火连天）
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
		self.isClose = False
		
	def closeFengHuoLianTianRoom( self ):
		# define method.
		# 提前结束掉某场战争 由tongmanager 关闭所有房间
		if self.isClose:
			return
		
		self.isClose = True
		self.cell.closeFengHuoLianTianRoom()
		
