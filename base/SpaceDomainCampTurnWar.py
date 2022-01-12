# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *

import csdefine
import csconst
import csstatus

from SpaceDomain import SpaceDomain

class SpaceDomainCampTurnWar( SpaceDomain ):
	"""
	帮会车轮战space管理
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
		BigWorld.globalData[ "CampMgr" ].turnWar_onEnterCampTurnWarSpace( self, position, direction, baseMailbox, params )
		
	def onEnterCampTurnWarSpace( self, playerBaseMailBox, direction, enterKeyDict ):
		"""
		Define method.
		玩家登录空间
		"""
		teamID = enterKeyDict[ "teamID" ]
		isRight = teamID == enterKeyDict[ "team_right" ][ "teamID" ]
		if enterKeyDict["isFirstOrder"]:
			if isRight:
				position = self.getScript().right_fightPoint
			else:
				position = self.getScript().left_fightPoint
		else:
			if isRight:
				position = self.getScript().right_watchPoint
			else:
				position = self.getScript().left_watchPoint
		spaceItem = self.findSpaceItem( enterKeyDict, True )
		pickData = self.pickToSpaceData( playerBaseMailBox, params )
		spaceItem.enter( playerBaseMailBox, position, direction, pickData )
		
	def onLoginTurnWarSpace( self, playerBase, enterKeyDict, shouldCreate ):
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
			playerBase.cell.setTemp( "isLogin", True )
			return
			
		playerBase.logonSpaceInSpaceCopy()
	
	def getSpaceItemByTeamID( self, teamID ):
		number = self.keyTo.get( teamID )
		if number is not None:
			return self.getSpaceItem( number )
		else:
			return None

	def createSpaceItem( self, params ):
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
		teamID1 = params["team_left"]["teamID"]
		teamID2 = params["team_right"]["teamID"]
		spaceItem = SpaceDomain.createSpaceItem( self, params )
		self.keyToSpaceNumber[ teamID1 ] = spaceItem.spaceNumber
		self.keyToSpaceNumber[ teamID2 ] = spaceItem.spaceNumber
		return spaceItem
		
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		副本是由一定规则开放的， 因此不允许登陆后能够呆在一个
		不是自己开启的副本中， 遇到此情况应该返回到上一次登陆的地方
		"""
		params["login"] = True
		if params[ "teamID" ]:
			BigWorld.globalData[ "CampMgr" ].turnWar_onEnterCampTurnWarSpace( self, ( 0, 0, 0 ), ( 0, 0, 0 ), baseMailbox, params )
		else:
			baseMailbox.logonSpaceInSpaceCopy()
	