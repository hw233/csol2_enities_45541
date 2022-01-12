# -*- coding: gb18030 -*-
# $Id: Smith.py,v 1.3 2007-10-29 04:15:22 yangkai Exp $

import BigWorld
import NPC
from bwdebug import *

class Smith( NPC.NPC ):
	"""
	Smith
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


# Smith.py
