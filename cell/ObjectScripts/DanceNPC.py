# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.9 2008-03-25 01:59:31 zhangyuxing Exp $

"""
NPC�Ļ���
"""
from bwdebug import *
from NPC import NPC
import csdefine

class DanceNPC( NPC ):
	"""
	NPC�Ļ���
	"""
	def __init__( self ):
		NPC.__init__(self)