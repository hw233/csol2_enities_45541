# -*- coding: gb18030 -*-
#
# $Id: Trainer.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
Trainer����
"""

import BigWorld
from bwdebug import *
import csdefine
import csstatus
from NPC import NPC

class TongTrainer( NPC ):
	"""
	������NPC����
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		NPC.__init__( self )
		
# Trainer.py
