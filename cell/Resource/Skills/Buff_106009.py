# -*- coding: gb18030 -*-
#
# 移动速度降低%
#

import BigWorld
import csconst
import time
from bwdebug import *
from Buff_106001 import Buff_106001

class Buff_106009( Buff_106001 ):
	"""
	example:移动速度降低%
	"""
	def calculateTime( self, caster ):
		"""
		virtual method.
		取得持续时间
		"""
		tpEndTime = caster.queryTemp( 'trap_entity_last_time',0 )
		if tpEndTime != 0:
			leaveTime = tpEndTime - time.time()
			if leaveTime < 0:
				leaveTime = 1
			return int( time.time() + leaveTime )
		return Buff_106001.calculateTime( self, caster )

