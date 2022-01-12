# -*- coding: gb18030 -*-
import BigWorld
from bwdebug import *
from interface.GameObject import GameObject

class NPCCityMaster( BigWorld.Base, GameObject  ):
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