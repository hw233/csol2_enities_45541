# -*- coding: gb18030 -*-
# $Id: Founder.py,v 1.2 2007-10-29 04:13:54 yangkai Exp $

import BigWorld
import NPC
from bwdebug import *

class Founder( NPC.NPC ):
	"""An Founder class for cell.
	铸造师NPC
	"""

	def __init__( self ):
		"""
		"""
		NPC.NPC.__init__( self )

	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		NPC.NPC.load( self, section )

	def initEntity( self, selfEntity ):
		"""
		virtual method.
		初始化自己的entity的数据
		"""
		NPC.NPC.initEntity( self, selfEntity )


# Founder.py
