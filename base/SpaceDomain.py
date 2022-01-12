# -*- coding: gb18030 -*-
#
# $Id: SpaceDomain.py,v 1.27 2008-01-28 06:01:34 kebiao Exp $

"""
Space domain class
"""

import Language
import BigWorld
import csconst
import csstatus
import csdefine
from SpaceItem import SpaceItem
from bwdebug import *
import Function
from ObjectScripts.GameObjectFactory import GameObjectFactory

from WatchDog import WatchDog
from FindSpaceItemRules import g_findSpaceItemRules
WATCH_KEY_SPACE = "CREATE SPACE: NAME %s, NUMBER %i, CREATER %s"

TELEPORT_KEY = "SPACE WATCH DOG: %s.[player id %i, space %s, space number %i, at %f]"

# 领域类
class SpaceDomain( BigWorld.Base ):
	"""
	空间领域
	"""
	def __init__( self ):
		super( SpaceDomain, self ).__init__()

		self.__currentCopyCount = 0

		self.__spaceItems = {}

		self._spaceItemBuffer = []
		self._tid_bufferSpaceItem = 0
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_BIG_MAP

		self.spaceManager = BigWorld.entities[BigWorld.globalData["SpaceManager"].id]

		self.__checkToBufferSpaceItem(False)

		self.wd = WatchDog()
		
		self.keyToSpaceNumber = {}
		self.findSpaceItemRule = 0

	def getScript( self ):
		"""
		获取与自己对应的脚本
		"""
		return GameObjectFactory.instance().getObject( self.name )
		
	def getSpaceItemByKey( self, spaceKey ):
		# 根据spaceKey查找相应的space 
		if self.keyToSpaceNumber.has_key( spaceKey ):
			number = self.keyToSpaceNumber[ spaceKey ]
			return self.getSpaceItem( number )
		else:
			return None

	def createSpaceItem( self, params ):
		"""
		virtual method.
		模板方法；使用params参数创建新的spaceItem
		@return: instance of SpaceItem，如果达到了最大数量，则返回None
		"""
		if self.maxCopy > 0 and self.__currentCopyCount >= self.maxCopy:
			ERROR_MSG("space item instance is max count. %s" % ( self.name ))
			return None

		spaceItem = self.__popBufferedSpaceItem()
		if spaceItem is None:
			spaceItem = self.__createNewSpaceItem(params)
			self.__checkToBufferSpaceItem(False)
		else:
			self.__checkToBufferSpaceItem(True)

		self.__spaceItems[spaceItem.spaceNumber] = spaceItem
		self.__currentCopyCount += 1
		INFO_MSG("create new space item: name=%s, number=%d, spaceCount=%i" % ( self.name, spaceItem.spaceNumber, self.getCurrentCopyCount() ))
		return spaceItem

	def removeSpaceItem( self, spaceNumber ):
		"""
		virtual method.
		模板方法；删除spaceItem
		"""
		INFO_MSG("space item removed: %s, %d" % ( self.name, spaceNumber ))
		for key, number in self.keyToSpaceNumber.items():	#有可能两个或者多个队伍ID对应一个spaceNumber
			if number == spaceNumber:
				del self.keyToSpaceNumber[ key ]				
	
		self.__spaceItems.pop( spaceNumber )
		self.__currentCopyCount -= 1
		

	def getSpaceItem( self, spaceNumber ):
		"""
		根据space number获取space item实例
		@return: instance of SpaceItem
		"""
		return self.__spaceItems.get( spaceNumber )
		
	def getAllSpaceItems( self ):
		"""
		"""
		return self.__spaceItems

	def getCurrentCopyCount( self ):
		return self.__currentCopyCount

	def onSpaceLoseCell( self, spaceNumber ):
		"""
		define method.
		space entity 失去了cell部份后的通告；
		主要用于未来有可能存在的可存储副本，当副本数量太大时可能会考虑在没有玩家的时候只保留base部份，这时就需要这种通告；
		@param 	spaceNumber: spaceNumber
		"""
		INFO_MSG("%s space %d lose cell."%( self.name, spaceNumber ))
		#self.__spaceItems[ spaceNumber ].onLoseCell()
		spaceItem = self.__spaceItems.get(spaceNumber)
		if spaceItem is None:
			spaceItem = self.getBufferedSpaceItem(spaceNumber)
		spaceItem.onLoseCell()

	def onSpaceGetCell( self, spaceNumber ):
		"""
		define method.
		某个space的cell部份创建完成回调，此回调来自于被创建的space在onGetCell()被触发时调用。
		我们可在此回调中执行一些事情，如把等待进入此space的玩家传送进此space等等。
		@param spaceNumber: space 的唯一号码
		@type spaceNumber : SPACE_NUMBER,
		"""
		INFO_MSG("%s space %d create cell Complete"%( self.name, spaceNumber ))
		#self.__spaceItems[ spaceNumber ].onGetCell()
		spaceItem = self.__spaceItems.get(spaceNumber)
		if spaceItem is None:
			spaceItem = self.getBufferedSpaceItem(spaceNumber)
		self.wd.release(WATCH_KEY_SPACE % (self.name, spaceItem.spaceNumber, spaceItem.params.get("dbID", None)))
		spaceItem.onGetCell()

	def onSpaceCloseNotify( self, spaceNumber ):
		"""
		define method.
		空间关闭，space entity销毁通知。
		@param 	spaceNumber		:		spaceNumber
		@type 	spaceNumber		:		int32
		"""
		INFO_MSG("%s space close : %d"%( self.name, spaceNumber ))
		self.removeSpaceItem( spaceNumber )

	def findSpaceItem( self, params, createIfNotExisted = False ):
		"""
		virtual method.
		模板方法，通过给定的params来查找space，不同类型的space有不同的处理方式。
		重载此方法时必须严格按照参数中的说明进行实现。

		@param params: dict; 来自于space脚本中的packedDomainData()函数
		@param createIfNotExisted: bool; 当找不到时是否创建
		@return: instance of SpaceItem or None
		"""
		findRule = g_findSpaceItemRules.get( self.findSpaceItemRule )
		return findRule( self, params, createIfNotExisted )

	def requestCreateSpace( self, mailbox, params ):
		"""
		define method.
		手动创建一个指定的space
		@param mailbox: MAILBOX: 如果此参数不为None，space创建完成后将调用mailbox.onRequestCell()方法以通知mailbox所指向的entity
		@type  mailbox: MAILBOX
		"""
		def _onCreateBase( spaceItem, base ):
			"""
			创建base完成回调函数
			"""
			INFO_MSG("space base created, create cell now.", self.name)
			spaceItem.createCell()

		spaceI = self.createSpaceItem( params )
		if mailbox:
			spaceI.addToCreateNewList( mailbox )
		spaceI.createBase( Function.Functor( _onCreateBase, spaceI ) )

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
			print TELEPORT_KEY % ("player reaches domain", baseMailbox.id, self.name, spaceItem.spaceNumber, BigWorld.time())
		except:
			ERROR_MSG( "%s teleportEntity is error." % self.name )
	
	def pickToSpaceData( self, playerMailBox, params ):
		"""
		打包用于传递到space的数据
		"""
		newParams = {}
		newParams[ "gotoPlane" ] = params.get( "gotoPlane", False )
		return newParams

	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method.
		在玩家重新登录的时候被调用，用于让玩家在指定的space中出现（一般情况下为玩家最后下线的地图）；
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX,
		@param params: 一些关于该entity进入space的额外参数；(domain条件)
		@type params : PY_DICT = None
		"""
		spaceItem = self.findSpaceItem( params, True )
		spaceItem.logon( baseMailbox )

	def createNPCObjectFormBase( self, npcID, position, direction, state ):
		"""
		define method
		(远程)创建一个非玩家控制对象 该对象拥有base部分

		@param npcID: STRING, 非玩家控制对象的唯一标识
		@param position: 创建的目标位置
		@param direction: 创建的目标方向
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		spaceMBID = state.get( "spaceMBID", 0 )
		if len( self.__spaceItems ) > 0:
			if spaceMBID:
				for item in self.__spaceItems.values():
					if item.baseMailbox.id == spaceMBID:		# 根据baseMailBoxID来确保将要创建的对象与主人在同一个spaceItem中
						item.baseMailbox.createNPCObjectFormBase( npcID, position, direction, state )
						return
			baseMailbox = self.__spaceItems.values()[0].baseMailbox
			baseMailbox.createNPCObjectFormBase( npcID, position, direction, state )
		else:
			ERROR_MSG("Can't create entity in space, because space(%s) has no item yet!!" % self.name)

	def createCellNPCObjectFormBase( self, npcID, position, direction, state ):
		"""
		define method
		(远程)创建一个非玩家控制对象 该对象没有base部分

		@param npcID: STRING, 非玩家控制对象的唯一标识
		@param position: 创建的目标位置
		@param direction: 创建的目标方向
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		if len( self.__spaceItems ) > 0:
			baseMailbox = self.__spaceItems.values()[0].baseMailbox
			baseMailbox.cell.createNPCObject( npcID, position, direction, state )
		else:
			ERROR_MSG("Can't create entity in space, because space(%s) has no item yet!!"%self.name)

	def getSpaceClassName( self, params ):
		"""
		获取space className
		"""
		return self.name

	# -------------------------------------------------
	# space item buffer
	# -------------------------------------------------
	def __createNewSpaceItem(self, params):
		"""
		创建一个新的空间
		"""
		number = self.spaceManager.getNewSpaceNumber()
		spaceItem = SpaceItem( self.getSpaceClassName( params ), self, number, params )
		self.wd.watch(WATCH_KEY_SPACE % (self.name, spaceItem.spaceNumber, spaceItem.params.get("dbID", None)))
		return spaceItem

	def __createBufferedSpaceItem(self):
		"""
		创建缓存空间
		"""
		def _onCreateBase( spaceItem, base ):
			"""
			创建base完成回调函数
			"""
			INFO_MSG("Buffered space base created, create cell now.", self.name)
			spaceItem.createCell()

		spaceItem = self.__createNewSpaceItem({})
		self._spaceItemBuffer.append(spaceItem)
		spaceItem.createBase( Function.Functor( _onCreateBase, spaceItem ) )

	def __checkToBufferSpaceItem(self, createNow):
		"""
		检查是否创建缓存空间
		"""
		if self.bufferedSpaceItemsCount() >= self.bufferedSpaceItemsCountMax():
			self.stopBufferingSpaceItem()
			return

		if createNow:
			self.__createBufferedSpaceItem()

		if self._tid_bufferSpaceItem == 0:
			self._tid_bufferSpaceItem = self.addTimer(2.0, 2.0, 0)

	def __popBufferedSpaceItem(self):
		"""
		抽出一个缓存空间
		"""
		if len(self._spaceItemBuffer):
			return self._spaceItemBuffer.pop(0)
		else:
			return None

	def getBufferedSpaceItem(self, spaceNumber):
		"""
		根据空间编号获取缓存空间
		"""
		for spaceItem in self._spaceItemBuffer:
			if spaceItem.spaceNumber == spaceNumber:
				return spaceItem
		return None

	def stopBufferingSpaceItem(self):
		"""
		停止补充缓存空间
		"""
		if self._tid_bufferSpaceItem:
			self.delTimer(self._tid_bufferSpaceItem)
			self._tid_bufferSpaceItem = 0

	def bufferedSpaceItemsCount(self):
		"""
		获取缓存空间数量
		"""
		return len(self._spaceItemBuffer)

	def bufferedSpaceItemsCountMax(self):
		"""
		获取最大缓存空间数量
		"""
		return self.getScript().bufferCount

	def onTimer(self, timerID, userData):
		"""
		回调到达
		"""
		if timerID == self._tid_bufferSpaceItem:
			self.__checkToBufferSpaceItem(True)

#
# $Log: not supported by cvs2svn $
# Revision 1.26  2007/12/18 04:30:11  phw
# method modified: createNPCObject(), 修正:AttributeError: SpaceItem instance has no attribute 'base'
#
# Revision 1.25  2007/10/10 00:55:50  phw
# method added: createNPCObject()
#
# Revision 1.24  2007/10/07 07:16:58  phw
# 结构调整，细化了SpaceItem的创建、删除，并允许继承类去实现它
#
# Revision 1.23  2007/10/03 07:43:13  phw
# 代码整理，去掉了普通space不需要的方法及属性
#
# Revision 1.22  2007/09/29 06:01:37  phw
# 调整了各功能函数的实现方式
#
# Revision 1.21  2007/09/24 07:09:06  phw
# import ObjectScripts.GameObjectFactory -> from ObjectScripts.GameObjectFactory import GameObjectFactory
#
# Revision 1.20  2007/09/22 09:07:10  kebiao
# 重新调整了space设计
#
#
#