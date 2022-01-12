# -*- coding: gb18030 -*-
#
# $Id: SpaceDoor.py,v 1.2 2008-03-14 05:49:58 phw Exp $

"""
"""

import BigWorld
from bwdebug import *
from interface.GameObject import GameObject

class SpaceDoor( BigWorld.Base, GameObject ):
	"""
	传送门。
	"""
	def __init__(self):
		"""
		构造函数。
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
		
	def onLoseCell( self ):
		self.destroy()

	def onGetCell( self ):
		pass

# SpaceDoor.py
