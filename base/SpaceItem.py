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

# SpaceItem : ����� space �ķ�װ������space�Ĵ��������غ���ҽ���
class SpaceItem:
	def __init__( self, className, parent, number, params ):
		self.className = className
		self.parent = parent			# ��¼�����Լ���SpaceDomain
		self.spaceNumber = number		# �ռ�ID
		self.params = params			# dict, ��¼�����space��صĶ��������������space��ͬһ����(��SpaceItem����ʱ���ݽ�������)
		self.baseMailbox = None			# �ռ��BASE mailbox
		self.hasBase = False			# �Ƿ����base��־
		self.baseCreateing = False		# ��ǰspace base�Ƿ��ڴ�����
		self.hasCell = False			# �Ƿ����cell��־
		self.cellCreateing = False		# ��ǰspace�Ƿ��ڴ�����
		self._enters = []				# Ҫ����ռ���������: [(),...]
		self._logons = []				# Ҫ���߽���ռ���������: [Base,...]
		self._creates = []				# Ҫ�����ռ����ռ���������: [Base,...]

		self.wd = WatchDog()
		
	def isEmpty( self ):
		return self.hasBase is False and self.baseCreateing is False

	def createBase( self, callBack = None ):
		"""
		����domainʵ��
		"""
		if self.baseCreateing or self.hasBase:
			# ������ڴ���base���Ѿ�����base�����ٴ���
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
		cell�ر�
		"""
		self.hasCell = False

	def onGetCell( self ):
		"""
		space�����cell���ݣ�ִ��״̬�ı䣬������Ҫ����space����Ҵ���space��
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
		����cell
		"""
		if self.cellCreateing or self.hasCell:
			# ������ڴ���cell���Ѿ�����cell�����ٴ���
			WARNING_MSG( "I have cell or creating cell.", self.className )
			return
		self.wd.watch(WATCH_KEY_CELL % (self.className, self.spaceNumber, self.baseMailbox.id))
		self.cellCreateing = True
		self.baseMailbox.createCell()
		
	def addToEnterList( self, playerBase, position, direction, pickData ):
		"""
		��ӽ���ռ����Ҽ�¼
		"""
		self._enters.append( ( playerBase, position, direction, pickData ) )
			
	def addToLogonList( self, playerBase ):
		"""
		����ڿռ����ߵ���Ҽ�¼
		@param 	playerBase	:		��ҵ�base
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
		��ҽ���ռ�
		@param 	playerBase	:		��ҵ�base
		@type 	playerBase	:		mailbox
		@param 	position	:		��ҵ�λ��
		@type 	position	:		vector3
		@param 	direction	:		��ҵ�λ��
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
				# ������space��base���򴴽�cell����
				self.createCell()
				
			# ����ʵ����û�����������ȴ�������ʵ��
			self.createBase( onCreateBaseCallback )
			self.addToEnterList( playerBase, position, direction, pickData )

	def logon( self, playerBase ):
		"""
		�������
		@param 	playerBase	:		��ҵ�base
		@type 	playerBase	:		mailbox
		"""
		if self.hasCell:
			self.baseMailbox.entityCreateCell( playerBase )
		elif self.hasBase:
			self.addToLogonList( playerBase )
			self.createCell()
		else:
			def onCreateBaseCallback( spaceBase ):
				# ������space��base���򴴽�cell����
				self.createCell()
				
			# ����ʵ����û�����������ȴ�������ʵ��
			self.createBase( onCreateBaseCallback )
			self.addToLogonList( playerBase )		# ����ȴ��б���



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