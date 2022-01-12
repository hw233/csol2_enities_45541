# -*- coding: gb18030 -*-
#

#
import BigWorld
from bwdebug import *
import random
import csdefine
import csconst
import csstatus
import cschannel_msgs
from NPC import NPC

class DanceSeat(NPC):
	def __init__(self):
		NPC.__init__(self)
		self.setEntityType( csdefine.ENTITY_TYPE_DANCESEAT )
		
	