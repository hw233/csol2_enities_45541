# -*- coding: gb18030 -*-
#
# $Id: NPCObject.py,v 1.1 2007-09-24 07:04:33 phw Exp $

"""
NPC基类
"""

import BigWorld
from bwdebug import *
from interface.GameObject import GameObject

class NPCObject( BigWorld.Base, GameObject ):
	"""
	NPC基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		BigWorld.Base.__init__( self )
		GameObject.__init__( self )

		try:
			cell = self.createOnCell
			del self.createOnCell
		except AttributeError, e:
			cell = None
		
		if cell is not None:
			self.createCellEntity( cell )

	def getName( self ):
		"""
		virtual method.
		@return: the name of character entity
		@rtype:  STRING
		"""
		return self.getScript().getName()

# NPCObject.py
