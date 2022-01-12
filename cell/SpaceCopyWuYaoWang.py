# -*- coding: gb18030 -*-
import BigWorld

from SpaceCopy import SpaceCopy
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface

import Const

GOD_WEAPON_QUEST_WU_YAO		= 40202001

class SpaceCopyWuYaoWang( SpaceCopy, SpaceCopyYeWaiInterface ):
	"""
	巫妖王宝藏副本
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )
		SpaceCopyYeWaiInterface.__init__( self )
		
	def onGodWeaponWuYao( self ):
		"""
		define method
		完成神器任务，猰貐HP剩余90%以上
		"""
		for player in self._players:
			player.cell.questTaskIncreaseState( GOD_WEAPON_QUEST_WU_YAO, 1 )