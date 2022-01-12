# -*- coding: gb18030 -*-
import BigWorld

from SpaceCopy import SpaceCopy
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface

import Const

GOD_WEAPON_QUEST_WU_YAO		= 40202001

class SpaceCopyWuYaoWang( SpaceCopy, SpaceCopyYeWaiInterface ):
	"""
	���������ظ���
	"""
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopy.__init__( self )
		SpaceCopyYeWaiInterface.__init__( self )
		
	def onGodWeaponWuYao( self ):
		"""
		define method
		����������񣬪m؅HPʣ��90%����
		"""
		for player in self._players:
			player.cell.questTaskIncreaseState( GOD_WEAPON_QUEST_WU_YAO, 1 )