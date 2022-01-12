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

# ������
class SpaceDomain( BigWorld.Base ):
	"""
	�ռ�����
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
		��ȡ���Լ���Ӧ�Ľű�
		"""
		return GameObjectFactory.instance().getObject( self.name )
		
	def getSpaceItemByKey( self, spaceKey ):
		# ����spaceKey������Ӧ��space 
		if self.keyToSpaceNumber.has_key( spaceKey ):
			number = self.keyToSpaceNumber[ spaceKey ]
			return self.getSpaceItem( number )
		else:
			return None

	def createSpaceItem( self, params ):
		"""
		virtual method.
		ģ�巽����ʹ��params���������µ�spaceItem
		@return: instance of SpaceItem������ﵽ������������򷵻�None
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
		ģ�巽����ɾ��spaceItem
		"""
		INFO_MSG("space item removed: %s, %d" % ( self.name, spaceNumber ))
		for key, number in self.keyToSpaceNumber.items():	#�п����������߶������ID��Ӧһ��spaceNumber
			if number == spaceNumber:
				del self.keyToSpaceNumber[ key ]				
	
		self.__spaceItems.pop( spaceNumber )
		self.__currentCopyCount -= 1
		

	def getSpaceItem( self, spaceNumber ):
		"""
		����space number��ȡspace itemʵ��
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
		space entity ʧȥ��cell���ݺ��ͨ�棻
		��Ҫ����δ���п��ܴ��ڵĿɴ洢����������������̫��ʱ���ܻῼ����û����ҵ�ʱ��ֻ����base���ݣ���ʱ����Ҫ����ͨ�棻
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
		ĳ��space��cell���ݴ�����ɻص����˻ص������ڱ�������space��onGetCell()������ʱ���á�
		���ǿ��ڴ˻ص���ִ��һЩ���飬��ѵȴ������space����Ҵ��ͽ���space�ȵȡ�
		@param spaceNumber: space ��Ψһ����
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
		�ռ�رգ�space entity����֪ͨ��
		@param 	spaceNumber		:		spaceNumber
		@type 	spaceNumber		:		int32
		"""
		INFO_MSG("%s space close : %d"%( self.name, spaceNumber ))
		self.removeSpaceItem( spaceNumber )

	def findSpaceItem( self, params, createIfNotExisted = False ):
		"""
		virtual method.
		ģ�巽����ͨ��������params������space����ͬ���͵�space�в�ͬ�Ĵ���ʽ��
		���ش˷���ʱ�����ϸ��ղ����е�˵������ʵ�֡�

		@param params: dict; ������space�ű��е�packedDomainData()����
		@param createIfNotExisted: bool; ���Ҳ���ʱ�Ƿ񴴽�
		@return: instance of SpaceItem or None
		"""
		findRule = g_findSpaceItemRules.get( self.findSpaceItemRule )
		return findRule( self, params, createIfNotExisted )

	def requestCreateSpace( self, mailbox, params ):
		"""
		define method.
		�ֶ�����һ��ָ����space
		@param mailbox: MAILBOX: ����˲�����ΪNone��space������ɺ󽫵���mailbox.onRequestCell()������֪ͨmailbox��ָ���entity
		@type  mailbox: MAILBOX
		"""
		def _onCreateBase( spaceItem, base ):
			"""
			����base��ɻص�����
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
		����һ��entity��ָ����space��
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX,
		@param params: һЩ���ڸ�entity����space�Ķ�������� (domain����)
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
		������ڴ��ݵ�space������
		"""
		newParams = {}
		newParams[ "gotoPlane" ] = params.get( "gotoPlane", False )
		return newParams

	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method.
		��������µ�¼��ʱ�򱻵��ã������������ָ����space�г��֣�һ�������Ϊ���������ߵĵ�ͼ����
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX,
		@param params: һЩ���ڸ�entity����space�Ķ��������(domain����)
		@type params : PY_DICT = None
		"""
		spaceItem = self.findSpaceItem( params, True )
		spaceItem.logon( baseMailbox )

	def createNPCObjectFormBase( self, npcID, position, direction, state ):
		"""
		define method
		(Զ��)����һ������ҿ��ƶ��� �ö���ӵ��base����

		@param npcID: STRING, ����ҿ��ƶ����Ψһ��ʶ
		@param position: ������Ŀ��λ��
		@param direction: ������Ŀ�귽��
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		spaceMBID = state.get( "spaceMBID", 0 )
		if len( self.__spaceItems ) > 0:
			if spaceMBID:
				for item in self.__spaceItems.values():
					if item.baseMailbox.id == spaceMBID:		# ����baseMailBoxID��ȷ����Ҫ�����Ķ�����������ͬһ��spaceItem��
						item.baseMailbox.createNPCObjectFormBase( npcID, position, direction, state )
						return
			baseMailbox = self.__spaceItems.values()[0].baseMailbox
			baseMailbox.createNPCObjectFormBase( npcID, position, direction, state )
		else:
			ERROR_MSG("Can't create entity in space, because space(%s) has no item yet!!" % self.name)

	def createCellNPCObjectFormBase( self, npcID, position, direction, state ):
		"""
		define method
		(Զ��)����һ������ҿ��ƶ��� �ö���û��base����

		@param npcID: STRING, ����ҿ��ƶ����Ψһ��ʶ
		@param position: ������Ŀ��λ��
		@param direction: ������Ŀ�귽��
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
		��ȡspace className
		"""
		return self.name

	# -------------------------------------------------
	# space item buffer
	# -------------------------------------------------
	def __createNewSpaceItem(self, params):
		"""
		����һ���µĿռ�
		"""
		number = self.spaceManager.getNewSpaceNumber()
		spaceItem = SpaceItem( self.getSpaceClassName( params ), self, number, params )
		self.wd.watch(WATCH_KEY_SPACE % (self.name, spaceItem.spaceNumber, spaceItem.params.get("dbID", None)))
		return spaceItem

	def __createBufferedSpaceItem(self):
		"""
		��������ռ�
		"""
		def _onCreateBase( spaceItem, base ):
			"""
			����base��ɻص�����
			"""
			INFO_MSG("Buffered space base created, create cell now.", self.name)
			spaceItem.createCell()

		spaceItem = self.__createNewSpaceItem({})
		self._spaceItemBuffer.append(spaceItem)
		spaceItem.createBase( Function.Functor( _onCreateBase, spaceItem ) )

	def __checkToBufferSpaceItem(self, createNow):
		"""
		����Ƿ񴴽�����ռ�
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
		���һ������ռ�
		"""
		if len(self._spaceItemBuffer):
			return self._spaceItemBuffer.pop(0)
		else:
			return None

	def getBufferedSpaceItem(self, spaceNumber):
		"""
		���ݿռ��Ż�ȡ����ռ�
		"""
		for spaceItem in self._spaceItemBuffer:
			if spaceItem.spaceNumber == spaceNumber:
				return spaceItem
		return None

	def stopBufferingSpaceItem(self):
		"""
		ֹͣ���仺��ռ�
		"""
		if self._tid_bufferSpaceItem:
			self.delTimer(self._tid_bufferSpaceItem)
			self._tid_bufferSpaceItem = 0

	def bufferedSpaceItemsCount(self):
		"""
		��ȡ����ռ�����
		"""
		return len(self._spaceItemBuffer)

	def bufferedSpaceItemsCountMax(self):
		"""
		��ȡ��󻺴�ռ�����
		"""
		return self.getScript().bufferCount

	def onTimer(self, timerID, userData):
		"""
		�ص�����
		"""
		if timerID == self._tid_bufferSpaceItem:
			self.__checkToBufferSpaceItem(True)

#
# $Log: not supported by cvs2svn $
# Revision 1.26  2007/12/18 04:30:11  phw
# method modified: createNPCObject(), ����:AttributeError: SpaceItem instance has no attribute 'base'
#
# Revision 1.25  2007/10/10 00:55:50  phw
# method added: createNPCObject()
#
# Revision 1.24  2007/10/07 07:16:58  phw
# �ṹ������ϸ����SpaceItem�Ĵ�����ɾ����������̳���ȥʵ����
#
# Revision 1.23  2007/10/03 07:43:13  phw
# ��������ȥ������ͨspace����Ҫ�ķ���������
#
# Revision 1.22  2007/09/29 06:01:37  phw
# �����˸����ܺ�����ʵ�ַ�ʽ
#
# Revision 1.21  2007/09/24 07:09:06  phw
# import ObjectScripts.GameObjectFactory -> from ObjectScripts.GameObjectFactory import GameObjectFactory
#
# Revision 1.20  2007/09/22 09:07:10  kebiao
# ���µ�����space���
#
#
#