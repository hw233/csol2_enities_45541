# -*- coding: gb18030 -*-
#
# $Id: SpaceDoor.py,v 1.18 2008-04-01 05:39:06 zhangyuxing Exp $

import BigWorld
import csdefine
from utils import *
from bwdebug import *
from SpaceDoor import SpaceDoor
from gbref import rds
import event.EventCenter as ECenter
import time

class SpaceDoorLiuWangMu( SpaceDoor ):
	def __init__( self ):
		SpaceDoor.__init__(self)