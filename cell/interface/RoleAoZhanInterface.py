# -*- coding: gb18030 -*-

import BigWorld

from ObjectScripts.GameObjectFactory import g_objFactory

import csdefine
import csstatus

class RoleAoZhanInterface:
	def __init__( self ):
		pass
		
	def aoZhanSetResult( self, self.enterNumber, score, useTime ):
		"""
		���ñȽϽ��
		"""
		BigWorld.globalData[ "AoZhanQunXiongMgr" ].setResult( self.enterNumber, score, useTime, remainHP )