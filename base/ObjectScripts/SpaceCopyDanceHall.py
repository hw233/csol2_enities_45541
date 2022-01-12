# -*- coding: gb18030 -*-
#
# $Id: Space.py,v 1.8 2008-04-16 05:51:18 phw Exp $

"""
"""
import BigWorld
import random
import Language
import Love3
import csdefine
import csstatus
from bwdebug import *
from SpaceCopy import SpaceCopy

class SpaceCopyDanceHall( SpaceCopy ):
	"""
	用于控制SpaceNormal entity的脚本，所有有需要的SpaceNormal方法都会调用此脚本(或继承于此脚本的脚本)的接口
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopy.__init__( self )
