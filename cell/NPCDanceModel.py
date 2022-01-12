# -*- coding: gb18030 -*-

"""
"""


import BigWorld
import NPC
from bwdebug import *
from utils import *
import csdefine


class NPCDanceModel( NPC.NPC ):
	def __init__( self ):
		NPC.NPC.__init__( self )	
		self.setEntityType( csdefine.ENTITY_TYPE_NPCDanceModel )