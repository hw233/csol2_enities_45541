# -*- coding: gb18030 -*-
#
# $Id: GameObject.py,v 1.9 2008-09-01 03:27:27 zhangyuxing Exp $

"""
implement all game object's base class
"""
import BigWorld
from bwdebug import *
from ObjectScripts.GameObjectFactory import g_objFactory

class GameObject( object ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		super( GameObject, self ).__init__()
		if hasattr( self, "cellData" ):
			self.className = self.cellData["className"]
			self.planesID = self.cellData["planesID"]

	def onLoseCell( self ):
		"""
		when the cell is lose, it will be called
		"""
		self.destroy()

	def getName( self ):
		"""
		virtual method.
		@return: the name of entity
		@rtype:  STRING
		"""
		return ""

	def getScript( self ):
		"""
		@return: 返回自己的全局公共类
		@rtype:  instance
		"""
		if len( self.className ):
			return g_objFactory.getObject( self.className )
		return None

	def createNPCObject( self, dstCellMailbox, npcID, position, direction, state ):
		"""
		define method
		(远程)创建一个非玩家控制对象，被创建的entity将与dstCellMailbox在同一space上。

		@param npcID: STRING, 非玩家控制对象的唯一标识
		@param position: 创建的目标位置
		@param direction: 创建的目标方向
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		obj = g_objFactory.createLocalBase( npcID, state )
		obj.cellData["position"] = position
		obj.cellData["direction"] = direction
		
		try:
			obj.createCellEntity( dstCellMailbox )
		except Exception, errstr:
			EXCEHOOK_MSG( "%s, dstCellMailbox:%s, npcID:%s, position:%s, state:%s" % ( errstr, dstCellMailbox, npcID, position, state ) )
		return obj

	def createEntityByDBID( self, dstCellMailbox, entityType, dbid, state ):
		"""
		Define Method
		(远程)创建一个非玩家控制对象，被创建的entity将与dstCellMailbox在同一space上。
		@param dstCellMailbox: CellmailBox
		@param entityType: STRING, 非玩家控制对象的唯一标识
		@param dbid: INT64, DatabaseID
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		def onCreateOver( baseMailBox, dbid, wasActive ):
			if baseMailBox is None: return
			entity = BigWorld.entities[baseMailBox.id]
			if not hasattr( entity, "cell" ):
				for key, value in state.iteritems():
					entity.cellData[key] = value
				entity.createCellEntity( dstCellMailbox )

		BigWorld.createBaseLocallyFromDBID( entityType, dbid, onCreateOver )

	def remoteCall( self, name, args ):
		"""
		define method.
		远程方法调用，此方法用于让其它cellapp、baseapp调用未在.def中声明的方法；
		此方法在cellapp/baseapp调用clientapp的未声明方法最有价值，这样可以减少.def中client的声明方法，以其达到网络数据最少占用率。
		client top-level property Efficient to 61 (limit is 256)
		client method Efficient to 62 (limit is 15872)
		base method Efficient to 62 (limit is 15872)
		cell method Efficient to 62 (limit is 15872)

		@param name: STRING; 要调用的方法名称
		@param args: PY_ARGS; 被调用方法的参数列表，具体参数个数由各方法自行处理；
		"""
		try:
			method = getattr( self, name )
		except AttributeError, errstr:
			ERROR_MSG( "%s(%i): class %s has not method %s." % (self.getName(), self.id, self.__class__.__name__, name) )
			return
		method( *args )

	def getSpaceManager( self ):
		"""
		取得SpaceManager的base mailbox
		@return: SpaceManager的base mailbox
		"""
		return BigWorld.globalData["SpaceManager"]	# 如果产生了异常就表示有BUG