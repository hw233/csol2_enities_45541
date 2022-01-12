# -*- coding: gb18030 -*-
#
# $Id: SpaceTransport.py,v 1.8 2007-06-14 09:55:30 huangyongwei Exp $

"""
出入口实体。
"""

import BigWorld
import Love3
from bwdebug import *
from NPCObject import NPCObject
import csdefine
import cschannel_msgs

class SpaceTransport( NPCObject ):
	"""
	出入口实体，提供玩家角色切换场景的操作。
		@ivar uid:			出入口标识
		@type uid:			string
		@ivar destspace:	目标场景标识
		@type destspace:	string
		@ivar destpos:		目标点坐标
		@type destpos:		vector3
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		NPCObject.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_SPACE_TRANSPORT )

	def isInteractionRange( self, entity ):
		"""
		判断一个entity是否在自己的交互范围内
		"""
		return self.position.flatDistTo( entity.position ) < self.range + 1 # 由于延时我们在范围这里加大1米

# SpaceTransport.py
