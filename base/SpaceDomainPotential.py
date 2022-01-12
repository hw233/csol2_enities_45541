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

# ������
class SpaceDomainPotential(SpaceDomain):
	"""
	Ǳ�ܸ������� ���˸������������ԣ�
	"""
	def __init__( self ):
		SpaceDomain.__init__(self)
		
		# ����ҵ�dbid��ӳ��SpaceItemʵ��������߸���ͬһ�����Ľ����ж��ٶȣ�
		# ��ҵ�dbidҲ��ʾ��֮���Ӧ��SpaceItem��ʵ��ӵ���ߣ�
		# ʹ����ҵ�dbid����ʹ��entityID��ԭ����Ϊ�˷�ֹ����£��ϣ��ߺ�����ʱ�Ҳ���ԭ��������space��
		# Ҳ��Ϊ�˷�ֹ������£��ϣ��ߵķ�ʽ�ƹ�������ʱ���ڿɽ���Ĵ���
		# �˱���self.spaceItems_��Ӧ�������self.spaceItems_ɾ��һ�ҲӦ��������ɾ����������Ȼ
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
		ģ�巽����ʹ��param���������µ�spaceItem
		"""
		# ���ڵ�ǰ�Ĺ����Ǵ����߲��ᣨҲ�����ܣ����Ŷӳ��ĸı���ı䣬
		# �����ǰ�����Ĵ������뿪�˶��飬Ȼ���Լ����ⴴ������ʱ��
		# �µĸ����ͻḲ�Ǿɵĸ��������ھɵĸ�������Ĵ����߻������ڵ���ң�
		# ���ɵĸ����ȸ�����´����ĸ����ȹر�ʱ����Ȼ�ᵼ���µĸ���ӳ�䱻ɾ����
		# ��ˣ�Ϊ�˱�������bug���ڴ����µĸ���ʱ�����Ǳ����Ȳ��ҵ�ǰ����Ƿ��Ѵ����˸�����
		# ���������Ҫ�ȰѾɸ����Ĵ�������0����û�д����߻򴴽��߶�ʧ�����ſ��Դ����µĸ�����
		if not param.get("playerAmount"):
			printStackTrace()
			ERROR_MSG( "SpaceDomainPotential:playerAmount is None." )
		DEBUG_MSG("playerAmount is %s,dbid = %i"%( param.get("playerAmount"), param.get( "dbID" )))
		dbid = param.get( "dbID" )		# dbid����������֮��ص�ObjectScripts/SpaceCopy.py����ؽӿ�
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
			baseMailbox.cell.onCreatePotential() #֪ͨcell Ǳ�ܸ����Ѵ���
			print TELEPORT_KEY % ("player reaches domain", baseMailbox.id, self.name, spaceItem.spaceNumber, BigWorld.time())
		except:
			ERROR_MSG( "%s teleportEntity is error." % self.name )

	def onSpaceCloseNotify( self, spaceNumber ):
		"""
		define method.
		�ռ�رգ�space entity����֪ͨ��
		@param 	spaceNumber		:		spaceNumber
		@type 	spaceNumber		:		int32
		"""
		if spaceNumber in self._SpaceDomain__spaceItems:
			SpaceDomain.onSpaceCloseNotify( self, spaceNumber )	
			
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method.
		��������µ�¼��ʱ�򱻵��ã������������ָ����space�г��֣�һ�������Ϊ���������ߵĵ�ͼ����
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: һЩ���ڸ�entity����space�Ķ��������(domain����)
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
		ĳ����������� ���� ʧЧ��(����ȡ����)
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
		space entity ʧȥ��cell���ݺ��ͨ�棻
		��Ҫ����δ���п��ܴ��ڵĿɴ洢����������������̫��ʱ���ܻῼ����û����ҵ�ʱ��ֻ����base���ݣ���ʱ����Ҫ����ͨ�棻
		@param 	spaceNumber: spaceNumber
		"""
		if spaceNumber not in self._SpaceDomain__spaceItems:
			return
		SpaceDomain.onSpaceLoseCell( self, spaceNumber )
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/04/10 02:36:36  kebiao
# ��������ѭ����½��BUG
#
# Revision 1.1  2008/02/14 02:23:59  kebiao
# no message
#
#
#