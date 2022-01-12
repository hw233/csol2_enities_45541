# -*- coding: gb18030 -*-
#
# $Id: SpaceDomainCityWar.py,v 1.1 2008-08-25 09:28:44 kebiao Exp $

"""
Space domain class
"""

import time
import Language
import BigWorld
from bwdebug import *
import Function
import csstatus
from SpaceDomain import SpaceDomain
import csdefine

# ������
class SpaceDomainTongTerritory(SpaceDomain):
	"""
	����ս���������� 
	"""
	def __init__( self ):
		SpaceDomain.__init__(self)
		
		# ����ҵ�dbid��ӳ��SpaceItemʵ��������߸���ͬһ�����Ľ����ж��ٶȣ�
		# ��ҵ�dbidҲ��ʾ��֮���Ӧ��SpaceItem��ʵ��ӵ���ߣ�
		# ʹ����ҵ�dbid����ʹ��entityID��ԭ����Ϊ�˷�ֹ����£��ϣ��ߺ�����ʱ�Ҳ���ԭ��������space��
		# Ҳ��Ϊ�˷�ֹ������£��ϣ��ߵķ�ʽ�ƹ�������ʱ���ڿɽ���Ĵ���
		# �˱���self.spaceItems_��Ӧ�������self.spaceItems_ɾ��һ�ҲӦ��������ɾ����������Ȼ
		# key = player's dbid, value = spaceNumber
		self.reset()
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS
		
	def reset( self ):
		"""
		"""
		self.tempData = {}
		self.tempData[ "waitEnterPlayers" ] = {}	# ��¼�ȴ�������ص���
		self.tempData[ "waitLoginPlayers" ] = {}

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
		tongDBID = param.get( "tongDBID" )		# dbid����������֮��ص�ObjectScripts/SpaceCopy.py����ؽӿ�
		assert tongDBID is not None, "the param tongDBID is necessary."
		
		spaceItem = self.getSpaceItem( tongDBID )
		if spaceItem:
			spaceItem.params["tongDBID"] = ""
		spaceItem = SpaceDomain.createSpaceItem( self, param )
		self.keyToSpaceNumber[ tongDBID ] = spaceItem.spaceNumber
		return spaceItem

	def onSpaceCloseNotify( self, spaceNumber ):
		"""
		define method.
		�ռ�رգ�space entity����֪ͨ��
		@param 	spaceNumber		:		spaceNumber
		@type 	spaceNumber		:		int32
		"""
		SpaceDomain.onSpaceCloseNotify( self, spaceNumber )
	
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
		# ����ȡ�˸��ɣ� ����һ��������Ϊ0�ģ� ���������������� ������������DBID
		if params[ "enter_tong_territory_datas" ].has_key( "enterOtherTong" ):
			params[ "tongDBID" ] = params[ "enter_tong_territory_datas" ][ "enterOtherTong" ]
			
		spaceItem = self.findSpaceItem( params, False )
		if spaceItem:
			if position[0] == 0 and position[1] == 0  and position[2] == 0:
				position = self.getScript().enterPoint[0]
				direction = self.getScript().enterPoint[1]
			pickData = self.pickToSpaceData( baseMailbox, params )
			spaceItem.enter( baseMailbox, position, direction, pickData )
		else:
			# ����һ���ȴ����У� �����ڸ���δ����������ʱ ���кü������������
			tongDBID = params[ "tongDBID" ]
			if tongDBID in self.tempData[ "waitEnterPlayers" ]:
				self.tempData[ "waitEnterPlayers" ][ tongDBID ].append( baseMailbox )
			else:
				self.tempData[ "waitEnterPlayers" ][ tongDBID ] = [ baseMailbox ]
			BigWorld.globalData[ "TongManager" ].onRequestCreateTongTerritory( self, tongDBID )

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
			# ����һ���ȴ����У� �����ڸ���δ����������ʱ ���кü������������
			tongDBID = params[ "tongDBID" ]
			if tongDBID in self.tempData[ "waitLoginPlayers" ]:
				self.tempData[ "waitLoginPlayers" ][ tongDBID ].append( baseMailbox )
			else:
				self.tempData[ "waitLoginPlayers" ][ tongDBID ] = [ baseMailbox ]
			BigWorld.globalData[ "TongManager" ].onRequestCreateTongTerritory( self, tongDBID )
			
	def onCreateTongTerritory( self, tongDBID, ysdt_level, jk_level, ssd_level, ck_level, tjp_level, sd_level, yjy_level, shenshouType, shenshouReviveTime ):
		"""
		define method.
		����������
		"""
		# ����һ�������ز���
		params = { "tongDBID" : tongDBID, "ysdt_level": ysdt_level, "jk_level" : jk_level, "ssd_level" : ssd_level, "ck_level" : ck_level, "tjp_level" : tjp_level, \
		"sd_level" : sd_level, "yjy_level" : yjy_level, "shenshouType" : shenshouType, "shenshouReviveTime" : shenshouReviveTime,"spaceKey":tongDBID }
		
		spaceItem = self.findSpaceItem( params, True )
		if spaceItem:
			if tongDBID in self.tempData[ "waitEnterPlayers" ]:
				pickData = self.pickToSpaceData( None, params )
				for baseMailbox in self.tempData[ "waitEnterPlayers" ].pop( tongDBID ):
					spaceItem.enter( baseMailbox, self.getScript().enterPoint[0], self.getScript().enterPoint[1], pickData )
					
			if tongDBID in self.tempData[ "waitLoginPlayers" ]:		
				for baseMailbox in self.tempData[ "waitLoginPlayers" ].pop( tongDBID ):
					spaceItem.logon( baseMailbox )				
		else:
			self.onCreateTongTerritoryError( tongDBID )
			
	def onCreateTongTerritoryError( self, tongDBID ):
		"""
		define method.
		����������ʧ��
		"""
		if tongDBID in self.tempData[ "waitEnterPlayers" ]:		
			for baseMailbox in self.tempData[ "waitEnterPlayers" ].pop( tongDBID ):
				baseMailbox.client.onStatusMessage( csstatus.TONG_TARGET_INVALID, "" )
				
		if tongDBID in self.tempData[ "waitLoginPlayers" ]:			
			for baseMailbox in self.tempData[ "waitLoginPlayers" ].pop( tongDBID ):
				baseMailbox.tong_logonInTerritoryError()
			
	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""	
		pass
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/08/01 08:04:17  kebiao
# ������Ҹ�������
#
# Revision 1.1  2008/07/31 09:03:41  kebiao
# add:SpaceDomainFamilyWar
#
#