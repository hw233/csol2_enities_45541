# -*- coding: gb18030 -*-

# 2008-11-26 gjx&lq

import BigWorld
from bwdebug import *
from interface.GameObject import GameObject

class SkillTrap( BigWorld.Base, GameObject ):
	"""
	作用：当玩家进入或者离开该区域时，通过对玩家进行一些动作去限制玩家的一些行为，如摆摊区域限制
	"""
	def __init__( self ):
		super( SkillTrap, self ).__init__()

		try:
			cell = self.createOnCell
			del self.createOnCell
		except AttributeError, e:
			cell = None

		if cell is not None:
			self.createCellEntity( cell )

	def onLoseCell( self ):
		self.destroy()
