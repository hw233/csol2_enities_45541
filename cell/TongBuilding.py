# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
NPC����
"""

import BigWorld
from bwdebug import *
import csdefine
from NPC import NPC

class TongBuilding( NPC ):
	"""
	��Ὠ�������
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		NPC.__init__( self )
		self.utype = csdefine.ENTITY_TYPE_MISC

	def setModelNumber( self, modelNumber ):
		"""
		define method.
		����ģ�ͱ��
		"""
		self.modelNumber = modelNumber
	
# NPC.py
