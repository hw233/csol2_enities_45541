# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.9 2008-03-25 01:59:31 zhangyuxing Exp $

"""
NPC的基类
"""
from bwdebug import *
from NPC import NPC
import csdefine

class DanceNPC( NPC ):
	"""
	NPC的基类
	"""
	def __init__( self ):
		NPC.__init__(self)