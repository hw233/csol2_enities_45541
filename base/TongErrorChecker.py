# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
NPC����
"""

import BigWorld
from bwdebug import *
import csdefine

class TongErrorChecker:
	"""
	��������
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		for info in self.tongInfos:
			oldTid = info["tid"]
			if oldTid <= 0:
				newTid = self.getNewTongID()
				info["tid"] = newTid
				ERROR_MSG( 'TongDebug:������[%s, %i], tid=%i��Ч�� ���°���һ��tid=%i' % ( info["tongName"], info["dbID"], oldTid, newTid ) )
