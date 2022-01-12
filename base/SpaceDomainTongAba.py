# -*- coding: gb18030 -*-
#
#$Id:$

"""
2010.11
家族擂台移植为帮会擂台 by cxm
"""

import BigWorld
from bwdebug import *

import csdefine
import csconst
import csstatus

from SpaceDomain import SpaceDomain


class SpaceDomainTongAba( SpaceDomain ):
	"""
	帮会擂台赛space管理
	"""
	def __init__( self ):
		"""
		"""
		SpaceDomain.__init__( self )
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS
	
			
	def createSpaceItem( self, enterKeyDict ):
		"""
		virtual method.
		模板方法；使用param参数创建新的spaceItem
		"""
		# 由于当前的规则是创建者不会（也不可能）随着队长的改变而改变，
		# 如果当前副本的创建者离开了队伍，然后自己另外创建副本时，
		# 新的副本就会覆盖旧的副本，由于旧的副本保存的创建者还是现在的玩家，
		# 当旧的副本比该玩家新创建的副本先关闭时，必然会导致新的副本映射被删除，
		# 因此，为了避免这种bug，在创建新的副本时，我们必须先查找当前玩家是否已创建了副本，
		# 如果有则需要先把旧副本的创建者置0（即没有创建者或创建者丢失），才可以创建新的副本。
		tongDBID1 = enterKeyDict.get( "tongDBID1" )		# dbid参数来自与之相关的ObjectScripts/SpaceCopy.py的相关接口
		tongDBID2 = enterKeyDict.get( "tongDBID2" )
		spaceItem = SpaceDomain.createSpaceItem( self, enterKeyDict )
		self.keyToSpaceNumber[ tongDBID1 ] = spaceItem.spaceNumber
		self.keyToSpaceNumber[ tongDBID2 ] = spaceItem.spaceNumber
		return spaceItem
		
		
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
		BigWorld.globalData[ "TongManager" ].onEnterAbattoirSpace( self, position, direction, baseMailbox, params )
		
		
	def onEnterAbattoirSpace( self, shouldCreate, playerBase, enterKeyDict ):
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
		spaceItem = self.findSpaceItem( enterKeyDict, True )	# 帮会擂台赛，spaceItem不会为None
		if enterKeyDict[ "isRight" ]:							# 确定本帮会所在的擂台位置
			position = self.getScript().right_playerEnterPoint[ 0 ]
			direction = self.getScript().right_playerEnterPoint[ 1 ]
		else:
			position = self.getScript().left_playerEnterPoint[ 0 ]
			direction = self.getScript().right_playerEnterPoint[ 1 ]
			
		pickData = self.pickToSpaceData( playerBase, enterKeyDict )
		spaceItem.enter( playerBase, position, direction, pickData )
		
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method.
		在玩家重新登录的时候被调用，用于让玩家在指定的space中出现（一般情况下为玩家最后下线的地图）；
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: 一些关于该entity进入space的额外参数；(domain条件)
		@type params : PY_DICT = None
		"""
		params[ "login" ] = True
		BigWorld.globalData[ "TongManager" ].onEnterAbattoirSpace( self, (0,0,0), (0,0,0), baseMailbox, params )	
			
			
	def onLoginAbattoirSpace( self, shouldCreate, playerBase, enterKeyDict ):
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
		if spaceItem:
			spaceItem.logon( playerBase )
			return
			
		playerBase.logonSpaceInSpaceCopy()