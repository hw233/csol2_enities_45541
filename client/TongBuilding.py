# -*- coding: gb18030 -*-
#
# $Id: GameObject.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
GameObject����
"""
import BigWorld
from bwdebug import *
import csdefine
from NPC import NPC
from keys import *

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
		self.setSelectable( False )
		
# GameObject.py
