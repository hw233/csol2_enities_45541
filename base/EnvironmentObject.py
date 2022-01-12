# -*- coding: gb18030 -*-

# $Id: SpawnPoint.py,v 1.3 2008-07-18 01:02:37 phw Exp $
"""
"""

import BigWorld
from bwdebug import *
from interface.GameObject import GameObject
import random

CREATE_CELL_ENTITY = 100
DESTROY_CELL_ENTITY = 101

class EnvironmentObject( BigWorld.Base, GameObject ):
	"""
	"""
	def __init__( self ):
		BigWorld.Base.__init__( self )
		GameObject.__init__( self )
		self.hasCell = False
		self.cellCreating = False
		
		if self.cellData["festival_key"] == "":
			try:
				cell = self.createOnCell
				del self.createOnCell
			except AttributeError, e:
				cell = None
			if cell is not None:
				self.cellCreating = True
				self.createCellEntity( cell )
		else:
			BigWorld.globalData["EnvironmentMgr"].addToMgr( self, self.cellData["festival_key"] )
		return


	def createCellEnviObject( self ):
		"""
		define method
		"""
		self.addTimer( random.random() * 10, 0, CREATE_CELL_ENTITY )


	def destroyCellEnviObject( self ):
		"""
		define method
		"""
		self.addTimer( random.random() * 10, 0, DESTROY_CELL_ENTITY )


	def onTimer( self, id, userArg ):
		"""
		"""
		if userArg == CREATE_CELL_ENTITY:
			if self.hasCell or self.cellCreating:
				return
			try:
				cell = self.createOnCell
			except AttributeError, e:
				cell = None
			if cell is not None:
				self.cellCreating = True
				self.createCellEntity( cell )

		elif userArg == DESTROY_CELL_ENTITY:
			if self.hasCell:
				self.destroyCellEntity()
				self.hasCell = False


	def onLoseCell( self ):
		"""
		when the cell is lose, it will be called
		"""
		pass

	def onGetCell( self ):
		"""
		when the cell is created, it will be called
		"""
		self.hasCell = True
		self.cellCreating = False