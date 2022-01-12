# -*- coding: gb18030 -*-
#
# $Id: SpaceDomainPotential.py,v 1.3 2008-04-25 08:34:45 kebiao Exp $

"""
Space domain class
"""

import time
import Language
import BigWorld
from bwdebug import *
import Function
from SpaceDomain import SpaceDomain
import csdefine

# 领域类
class SpaceDomainPotential(SpaceDomain):
	"""
	潜能副本领域 单人副本，队伍特性；
	"""
	def __init__( self ):
		SpaceDomain.__init__(self)
		
		# 以玩家的dbid来映射SpaceItem实例，以提高副本同一条件的进入判断速度，
		# 玩家的dbid也标示与之相对应的SpaceItem例实的拥有者，
		# 使用玩家的dbid而不使用entityID的原因是为了防止玩家下（断）线后重上时找不到原来的所属space，
		# 也是为了防止玩家以下（断）线的方式绕过副本短时间内可进入的次数
		# 此表与self.spaceItems_对应，如果在self.spaceItems_删除一项，也应该在这里删除，创建亦然
		# key = player's dbid, value = spaceNumber
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS		
		if not BigWorld.globalData.has_key( "SpaceDomainPotential" ):
			BigWorld.globalData["SpaceDomainPotential"] = { self.name : self }
		else:
			BigWorld.globalData["SpaceDomainPotential"][ self.name ] = self
		BigWorld.globalData["SpaceDomainPotential"] = BigWorld.globalData["SpaceDomainPotential"]
		
				
	def createSpaceItem( self, param ):
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
		if not param.get("playerAmount"):
			printStackTrace()
			ERROR_MSG( "SpaceDomainPotential:playerAmount is None." )
		DEBUG_MSG("playerAmount is %s,dbid = %i"%( param.get("playerAmount"), param.get( "dbID" )))
		dbid = param.get( "dbID" )		# dbid参数来自与之相关的ObjectScripts/SpaceCopy.py的相关接口
		assert dbid is not None, "the param dbID is necessary."
		
		spaceItem = self.getSpaceItem( dbid )
		if spaceItem:
			spaceItem.params["dbID"] = 0
		
		spaceItem = SpaceDomain.createSpaceItem( self, param )
#		self.keyToSpaceNumber[ dbid ] = spaceItem.spaceNumber
		return spaceItem

	def teleportEntity( self, position, direction, baseMailbox, params ):
		"""
		define method.
		传送一个entity到指定的space中
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX,
		@param params: 一些关于该entity进入space的额外参数； (domain条件)
		@type params : PY_DICT = None
		"""
		spaceItem = self.findSpaceItem( params, True )
		try:
			pickData = self.pickToSpaceData( baseMailbox, params )
			spaceItem.enter( baseMailbox, position, direction, pickData )
			baseMailbox.cell.onCreatePotential() #通知cell 潜能副本已创建
			print TELEPORT_KEY % ("player reaches domain", baseMailbox.id, self.name, spaceItem.spaceNumber, BigWorld.time())
		except:
			ERROR_MSG( "%s teleportEntity is error." % self.name )

	def onSpaceCloseNotify( self, spaceNumber ):
		"""
		define method.
		空间关闭，space entity销毁通知。
		@param 	spaceNumber		:		spaceNumber
		@type 	spaceNumber		:		int32
		"""
		if spaceNumber in self._SpaceDomain__spaceItems:
			SpaceDomain.onSpaceCloseNotify( self, spaceNumber )	
			
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method.
		在玩家重新登录的时候被调用，用于让玩家在指定的space中出现（一般情况下为玩家最后下线的地图）；
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: 一些关于该entity进入space的额外参数；(domain条件)
		@type params : PY_DICT = None
		"""
		spaceItem = self.findSpaceItem( params, False )
		if spaceItem:
			spaceItem.logon( baseMailbox )
		else:
			baseMailbox.logonSpaceInSpaceCopy()

	def onDisableQuest( self, dbid ):
		"""
		define method.
		某个任务完成了 或者 失效了(主动取消了)
		"""
		DEBUG_MSG( "[%s]quest disable. dbid=%i" % ( self.name, dbid ) )
		spaceItem = self.findSpaceItem( { "dbID" : dbid }, False )
		if spaceItem:
			spaceItem.baseMailbox.cell.onDisableQuest()
			self.removeSpaceItem( spaceItem.spaceNumber )
			DEBUG_MSG( "found spaceItem:%i, copyCount=%i, spaceItems=%s" % ( dbid, self.getCurrentCopyCount(), self._SpaceDomain__spaceItems ) )

	def onSpaceLoseCell( self, spaceNumber ):
		"""
		define method.
		space entity 失去了cell部份后的通告；
		主要用于未来有可能存在的可存储副本，当副本数量太大时可能会考虑在没有玩家的时候只保留base部份，这时就需要这种通告；
		@param 	spaceNumber: spaceNumber
		"""
		if spaceNumber not in self._SpaceDomain__spaceItems:
			return
		SpaceDomain.onSpaceLoseCell( self, spaceNumber )
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/04/10 02:36:36  kebiao
# 修正可能循环登陆的BUG
#
# Revision 1.1  2008/02/14 02:23:59  kebiao
# no message
#
#
#