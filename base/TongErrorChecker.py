# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
NPC基类
"""

import BigWorld
from bwdebug import *
import csdefine

class TongErrorChecker:
	"""
	帮会错误检查
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		for info in self.tongInfos:
			oldTid = info["tid"]
			if oldTid <= 0:
				newTid = self.getNewTongID()
				info["tid"] = newTid
				ERROR_MSG( 'TongDebug:这个帮会[%s, %i], tid=%i无效， 重新安排一个tid=%i' % ( info["tongName"], info["dbID"], oldTid, newTid ) )
