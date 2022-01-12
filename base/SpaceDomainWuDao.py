# -*- coding: gb18030 -*-
#
#$Id:$

"""
"""


import BigWorld
from bwdebug import *

import csdefine
import csconst
import csstatus

from SpaceDomain import SpaceDomain


class SpaceDomainWuDao( SpaceDomain ):
	"""
	武道大会space管理
	"""
	def __init__( self ):
		"""
		"""
		SpaceDomain.__init__( self )
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS		
		
	def teleportEntity( self, position, direction, baseMailbox, params ):
		"""
		Define method.
		传送一个entity到指定的space中
		
		@type position : VECTOR3
		@type direction : VECTOR3
		@param baseMailbox: entity的base mailbox
		@type baseMailbox : MAILBOX
		@param params: 一些关于该entity进入space的额外参数；(domain条件)
		@type params : PY_DICT
		"""
		BigWorld.globalData[ "WuDaoMgr" ].onEnterWuDaoSpace( self, position, direction, baseMailbox, params )
		
		
	def onEnterWuDaoSpace( self, position, direction, shouldCreate, playerBase, enterKeyDict ):
		"""
		Define method.
		玩家登录空间
		
		@param shouldCreate : 空间不存在时是否需要创建
		@type shouldCreate : BOOL
		@param playerBase : 进入空间的角色base mailbox
		@type playerBase : MAILBOX
		@param enterKeyDict : 生成空间的参数字典
		@type enterKeyDict : PY_DICT
		"""
		spaceItem = self.findSpaceItem( enterKeyDict, shouldCreate )
		pickData = self.pickToSpaceData( playerBase, enterKeyDict )
		spaceItem.enter( baseMailbox, position, direction, pickData )
		