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


class SpaceDomainTeamChallenge( SpaceDomain ):
	"""
	组队竞技space管理
	"""
	def __init__( self ):
		"""
		"""
		SpaceDomain.__init__( self )
		# 组队竞技专用SPACE DICT
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
		BigWorld.globalData[ "TeamChallengeMgr" ].onEnterSpace( self, position, direction, baseMailbox, params )
		
		
	def onEnterTeamChallenge( self, position, direction, shouldCreate, playerBase, spaceKey ):
		"""
		Define method.
		玩家登录空间
		
		@param shouldCreate : 空间不存在时是否需要创建
		@type shouldCreate : BOOL
		@param playerBase : 进入空间的角色base mailbox
		@type playerBase : MAILBOX
		@param enterKeyDict : 生成空间的参数字典
		@type spaceKey : INT16
		"""
		enterKeyDict = {"spaceKey":spaceKey}
		spaceItem = self.findSpaceItem( enterKeyDict, shouldCreate )
		pickData = self.pickToSpaceData( playerBase, {} )
		spaceItem.enter( baseMailbox, position, direction, pickData )
		
		