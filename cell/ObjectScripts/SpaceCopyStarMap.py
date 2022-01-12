# -*- coding: gb18030 -*-

# 星际地图
# by daiqinghui

# python
import random
# bigworld
import math
import time
import Math
import BigWorld
# common
import csconst
import csdefine
import csstatus
from bwdebug import ERROR_MSG, WARNING_MSG
# cell
from SpaceCopy import SpaceCopy
from GameObjectFactory import g_objFactory

class SpaceCopyStarMap( SpaceCopy ) :
	"""
	"""
	def __init__( self ) :
		SpaceCopy.__init__( self )
