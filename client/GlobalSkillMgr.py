# -*- coding: gb18030 -*-

import BigWorld
from ShortcutMgr import shortcutMgr
import Const


class GlobalSkillMgr( object ):
	"""
	闪躲技能相关
	"""
	def __init__( self ):
		object.__init__( self )
		self.__initCtrl()
		
	def __initCtrl( self ):
		shortcutMgr.setHandler( "OTHER_TOGGLE_SKILL_AVOIDANCE", self.__handleShortcut )
		
	def __handleShortcut( self ):
		try:
			player = BigWorld.player()
			skillList = player.getSkillList()
			for id in skillList:
				if id/1000 in Const.AVOIDANCE_SKILL_ID_LIST:
					player.useSkill( id )
			return True
		except:
			return False
		return False