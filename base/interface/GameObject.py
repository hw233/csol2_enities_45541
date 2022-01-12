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
		@return: �����Լ���ȫ�ֹ�����
		@rtype:  instance
		"""
		if len( self.className ):
			return g_objFactory.getObject( self.className )
		return None

	def createNPCObject( self, dstCellMailbox, npcID, position, direction, state ):
		"""
		define method
		(Զ��)����һ������ҿ��ƶ��󣬱�������entity����dstCellMailbox��ͬһspace�ϡ�

		@param npcID: STRING, ����ҿ��ƶ����Ψһ��ʶ
		@param position: ������Ŀ��λ��
		@param direction: ������Ŀ�귽��
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
		(Զ��)����һ������ҿ��ƶ��󣬱�������entity����dstCellMailbox��ͬһspace�ϡ�
		@param dstCellMailbox: CellmailBox
		@param entityType: STRING, ����ҿ��ƶ����Ψһ��ʶ
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
		Զ�̷������ã��˷�������������cellapp��baseapp����δ��.def�������ķ�����
		�˷�����cellapp/baseapp����clientapp��δ�����������м�ֵ���������Լ���.def��client����������������ﵽ������������ռ���ʡ�
		client top-level property Efficient to 61 (limit is 256)
		client method Efficient to 62 (limit is 15872)
		base method Efficient to 62 (limit is 15872)
		cell method Efficient to 62 (limit is 15872)

		@param name: STRING; Ҫ���õķ�������
		@param args: PY_ARGS; �����÷����Ĳ����б�������������ɸ��������д���
		"""
		try:
			method = getattr( self, name )
		except AttributeError, errstr:
			ERROR_MSG( "%s(%i): class %s has not method %s." % (self.getName(), self.id, self.__class__.__name__, name) )
			return
		method( *args )

	def getSpaceManager( self ):
		"""
		ȡ��SpaceManager��base mailbox
		@return: SpaceManager��base mailbox
		"""
		return BigWorld.globalData["SpaceManager"]	# ����������쳣�ͱ�ʾ��BUG