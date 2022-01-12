# -*- coding: gb18030 -*-
#
# $Id: SpaceItem.py,v 1.3 2007-09-29 06:01:51 phw Exp $

import time
import BigWorld
from bwdebug import *
import csdefine
import csstatus
import Function
from ObjectScripts.GameObjectFactory import GameObjectFactory

from WatchDog import WatchDog
WATCH_KEY_BASE = "C-BASE: %s, %i"
WATCH_KEY_CELL = "C-CELL: %s, %i, %i"

# player id, space name, space number, time
TELEPORT_KEY = "SPACE WATCH DOG: player teleports start(%s).[player id %i, space %s, space number %i, at %f]"

# SpaceItem : 负责对 space 的封装，处理space的创建、加载和玩家进入
class SpaceItem:
	def __init__( self, className, parent, number, params ):
		self.className = className
		self.parent = parent			# 记录包含自己的SpaceDomain
		self.spaceNumber = number		# 空间ID
		self.params = params			# dict, 记录了与此space相关的额外参数，如进入此space的同一条件(由SpaceItem创建时传递进来决定)
		self.baseMailbox = None			# 空间的BASE mailbox
		self.hasBase = False			# 是否存在base标志
		self.baseCreateing = False		# 当前space base是否在创建中
		self.hasCell = False			# 是否存在cell标志
		self.cellCreateing = False		# 当前space是否在创建中
		self._enters = []				# 要进入空间的玩家数据: [(),...]
		self._logons = []				# 要上线进入空间的玩家数据: [Base,...]
		self._creates = []				# 要创建空间进入空间的玩家数据: [Base,...]

		self.wd = WatchDog()
		
	def isEmpty( self ):
		return self.hasBase is False and self.baseCreateing is False

	def createBase( self, callBack = None ):
		"""
		创建domain实体
		"""
		if self.baseCreateing or self.hasBase:
			# 如果正在创建base或已经存在base，不再创建
			WARNING_MSG( "I have base or creating base.", self.className )
			return
		self.wd.watch(WATCH_KEY_BASE % (self.className, self.spaceNumber))
		self.baseCreateing = True
		dict = { "spaceNumber": self.spaceNumber, "domainMB": self.parent, "params": self.params }
		GameObjectFactory.instance().createBaseAnywhere( self.className, dict, Function.Functor( self.onCreateBaseCallback_, callBack ) )

	def onCreateBaseCallback_( self, callBack, base ):
		"""
		create domain call back
		@param 	base	:		domain entity base
		@type 	base	:		mailbox
		"""
		self.wd.release(WATCH_KEY_BASE % (self.className, self.spaceNumber))
		if not base:
			ERROR_MSG( "space entity created error!", self.className, self.spaceNumber )
			return
		self.baseMailbox = base
		self.baseCreateing = False
		self.hasBase = True
		if callBack:
			callBack( base )

	def onLoseCell( self ):
		"""
		cell关闭
		"""
		self.hasCell = False

	def onGetCell( self ):
		"""
		space获得了cell部份，执行状态改变，并把需要进入space的玩家传到space中
		"""
		self.wd.release(WATCH_KEY_CELL % (self.className, self.spaceNumber, self.baseMailbox.id))

		self.hasCell = True
		self.cellCreateing = False
		
		for playerBase, position, direction, pickData in self._enters:
			print TELEPORT_KEY % ("ENTER", playerBase.id, self.className, self.spaceNumber, BigWorld.time())
			self.baseMailbox.teleportEntity( position, direction, playerBase, pickData )

		for playerBase in self._logons:
			print TELEPORT_KEY % ("LOGON", playerBase.id, self.className, self.spaceNumber, BigWorld.time())
			self.baseMailbox.registerLogonPlayer( playerBase )

		for playerBase in self._creates:
			print TELEPORT_KEY % ("CREATE", playerBase.id, self.className, self.spaceNumber, BigWorld.time())
			self.baseMailbox.registerCreatePlayer( playerBase )
			
		self._enters = []
		self._logons = []
		self._creates = []
		
	def createCell( self ):
		"""
		创建cell
		"""
		if self.cellCreateing or self.hasCell:
			# 如果正在创建cell或已经存在cell，不再创建
			WARNING_MSG( "I have cell or creating cell.", self.className )
			return
		self.wd.watch(WATCH_KEY_CELL % (self.className, self.spaceNumber, self.baseMailbox.id))
		self.cellCreateing = True
		self.baseMailbox.createCell()
		
	def addToEnterList( self, playerBase, position, direction, pickData ):
		"""
		添加进入空间的玩家记录
		"""
		self._enters.append( ( playerBase, position, direction, pickData ) )
			
	def addToLogonList( self, playerBase ):
		"""
		添加在空间上线的玩家记录
		@param 	playerBase	:		玩家的base
		@type 	playerBase	:		mailbox
		"""
		self._logons.append( playerBase )

	def addToCreateNewList( self, playerBase ):
		"""
		"""
		self._creates.append( playerBase )
		
	def teleportEntity( self, playerBase, position, direction, pickData ):
		self.baseMailbox.teleportEntity( position, direction, playerBase, pickData )
		
	def enter( self, playerBase, position, direction, pickData ):
		"""
		玩家进入空间
		@param 	playerBase	:		玩家的base
		@type 	playerBase	:		mailbox
		@param 	position	:		玩家的位置
		@type 	position	:		vector3
		@param 	direction	:		玩家的位置
		@type 	direction	:		vector3
		@return: None
		"""
		if self.hasCell:
			self.teleportEntity( playerBase, position, direction, pickData )
		elif self.hasBase:
			self.addToEnterList( playerBase, position, direction, pickData )
			self.createCell()
		else:
			def onCreateBaseCallback( spaceBase ):
				# 创建了space的base后则创建cell部份
				self.createCell()
				
			# 自身实例还没创建出来，先创建自身实例
			self.createBase( onCreateBaseCallback )
			self.addToEnterList( playerBase, position, direction, pickData )

	def logon( self, playerBase ):
		"""
		玩家上线
		@param 	playerBase	:		玩家的base
		@type 	playerBase	:		mailbox
		"""
		if self.hasCell:
			self.baseMailbox.entityCreateCell( playerBase )
		elif self.hasBase:
			self.addToLogonList( playerBase )
			self.createCell()
		else:
			def onCreateBaseCallback( spaceBase ):
				# 创建了space的base后则创建cell部份
				self.createCell()
				
			# 自身实例还没创建出来，先创建自身实例
			self.createBase( onCreateBaseCallback )
			self.addToLogonList( playerBase )		# 加入等待列表中



#
# $Log: not supported by cvs2svn $
# Revision 1.2  2007/09/24 07:08:55  phw
# import ObjectScripts.GameObjectFactory -> from ObjectScripts.GameObjectFactory import GameObjectFactory
#
# Revision 1.1  2007/09/22 09:07:39  kebiao
# no message
#
# 
#