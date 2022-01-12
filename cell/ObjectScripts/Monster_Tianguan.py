# -*- coding: gb18030 -*-
#
# $Id: Monster_Tianguan.py,v 1.1 2008-07-28 02:31:39 zhangyuxing Exp $

"""
怪物NPC的类
"""
import BigWorld
from Monster import Monster
from bwdebug import *
import csconst
import csdefine
import Language

class Monster_Tianguan(Monster):
	"""
	"""
	def __init__( self ):
		"""
		初始化
		"""
		Monster.__init__( self )
		self.levelPropertySection = Language.openConfigSection( "config/server/MLProperty.xml" )

	def setLevelProperty( self, selfEntity, level ):
		"""
		根据等级重新设置怪物属性
		"""
		
		selfEntity.uname = self.levelPropertySection[selfEntity.className + str(level)]['uanme']

