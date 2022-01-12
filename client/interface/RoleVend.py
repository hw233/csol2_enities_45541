# -*- coding: gb18030 -*-
#
# $Id: RoleVend.py,v 1.3 2008-09-03 10:44:47 fangpengjun Exp $

import BigWorld

from bwdebug import *
import csdefine
import event.EventCenter as ECenter
import config.client.labels.RoleVend as lbDatas
from NPCModelLoader import NPCModelLoader as NPCModel

class RoleVend:
	"""
	��Ұ�̯ϵͳ
	"""
	def __init__( self ):
		"""
		"""
		self.sellerID = 0
		pass
		#self.vendMerchandise = {}		# test,wsf

	def vend_vend( self, kitUidList, uidList, priceList, petDatabaseIDList = [], petPriceList = [] ):
		"""
		��Ұ�̯�Ľӿڣ��ڽ������ȼ������Ƿ������̯������������ܴ򿪰�̯����
		�ڵ��ô˽ӿ�֮ǰ�ڽ�������������:
		BigWorld.player().position,����Ƿ����������̯��Χ,�����򲻵�����̯����wsf
		if BigWorld.player().actionSign( csdefine.ACTION_FORBID_VEND ):
			DEBUG_MSG( "��Ҵ��ڲ������̯״̬." )
		֪ͨ�򿪰�̯����,���հ�̯������,Ȼ����ܵ��ô˽ӿ�

		param kitUidList: ��Ұ�̯��Ʒ�İ������б�
		type kitUidList: ARRAY OF UINT8
		param uidList: ��Ұ�̯��Ʒ��uidList�б�
		type uidList: ARRAY OF INT64
		param priceList: ���̯��Ʒ��Ӧ�İ�̯��Ʒ�۸��б�
		type priceList: ARRAY OF UINT32
		"""
		# �����ҽ�����Ҫ����һ����̯��Ʒ�б�,����̯��Ʒ����,����֪ͨ���ҽ���ɾ����Ӧ������,���½���
		self.cell.vend_vend( kitUidList, uidList, priceList, petDatabaseIDList, petPriceList )

	def vend_pauseVend( self ):
		"""
		�����ͣ��̯�ӿ�
		"""
		self.cell.vend_endVend( False )

	def vend_endVend( self ):
		"""
		��ҽ�����̯�Ľӿ�
		"""
		self.cell.vend_endVend( True )

	def vend_setSignboard( self, signboard ):
		"""
		��������̯λ���ƵĽӿڣ��������ʱ�����Ҳ�����Ĭ�����ƣ���signboardĬ��ʹ�á�**�ĵ��̡�����
		�����Ҹ������������֣���Ĭ�ϲ�����Ϊ��ҺϷ����ĵ����������Ա������̯�����ǹرհ�̯ʱʹ��û����յĲ�����

		param signboard: �����õ�̯λ��
		type signboard: STRING
		"""
		self.cell.vend_setSignboard( signboard )

	def set_vendSignboard( self, oldValue ):
		"""
		���Ұ�̯�����Զ����º���
		"""
		if oldValue != self.vendSignboard:
			ECenter.fireEvent( "EVT_ON_VEND_UI_NAME_CHANGE", self.id, self.vendSignboard ) #���������������
		signboard = ""
		if self.vendSignboard == "":
			signboard = self.getName() + lbDatas.SIGNBOARD
		else:
			signboard = self.vendSignboard
		ECenter.fireEvent( "EVT_ON_VEND_SIGNBOARD_NAME_CHANGED", self.id, signboard ) #����ͷ����������

	def set_vendSignboardNumber( self, oldValue ):
		"""
		���Ұ�̯������ͼ���º���
		"""
		if oldValue != self.vendSignboardNumber:
			ECenter.fireEvent( "EVT_ON_VEND_SIGNBOARD_NUMBER_CHANGE", self.vendSignboardNumber ) #����

	def	vend_buyerQueryInfo( self, vendorID ):
		"""
		��Ҳ鿴����̯λ���ݵĽӿ�

		param vendorID:	���ҵ�entity id
		type vendorID:	OBJECT_ID
		"""
		if self.id == vendorID:
			HACK_MSG( "vendor�������Լ�." )
			return

		vendor = BigWorld.entities.get( vendorID )
		if vendor == None:
			HACK_MSG( "�Ҳ������, vendorID: %i" % ( vendorID ) )
			return

		vendor.cell.vend_buyerQueryInfo()			# �������۵���Ʒ��������Ϣ
		vendor.cell.queryOwnCollectionItem()		# ��ѯ�չ���Ʒ
		ECenter.fireEvent( "EVT_ON_CLEAR_VEND_PURCHASED_ITEM" )
		self.sellerID = vendorID

	def vend_receiveShopData( self, items ):
		"""
		Define method.
		��ҽ�������̯λ���ݵĽӿ�

		param items:��̯����Ʒ����
		type items:	ITEMS
		"""
		# ֪ͨ����wsf
		ECenter.fireEvent( "EVT_ON_VEND_STATE_CHANGE", csdefine.ENTITY_STATE_VEND )
		ECenter.fireEvent( "EVT_ON_VEND_RECEIVE_VEND_ITEMS", items )
		#for temp in items:
		#	self.vendMerchandise[temp.getuid()] = temp	# test,��Ϊһ���ֵ�,�������wsf

	def vend_receivePetData( self, epitomes ):
		"""
		��ҽ������Ұ�̯���۳������ݵĽӿ�
		"""
		ECenter.fireEvent( "EVT_ON_VEND_RECEIVE_VEND_PETEPITOMES", epitomes )

	def vend_receiveRecord( self, record ):
		"""
		Define mehthod.
		��ҽ�������������¼���ݵĺ���

		@param record : [ playerName, itemID, time, price ]
		@type record : PYTHON --> [ STRING, itemID, FLOAT, UINT32 ]
		"""
		ECenter.fireEvent( "EVT_ON_VEND_BUYER_RECEIVE_RECORD", record )

	def vend_addRecordNotify( self, record ):
		"""
		Define mehthod.
		�����Լ����¿ͻ��˼�¼
		@param record : [ playerName, itemID, time, price ]
		@type record : PYTHON --> [ STRING, itemID, FLOAT, UINT32 ]
		"""
		ECenter.fireEvent( "EVT_ON_VEND_VENDOR_ADD_RECORD", record )
		
	def vend_addRecordNotify2( self, record ):
		"""
		Define mehthod.
		�����չ���¼
		@param record : [ playerName, itemID, time, price ]
		@type record : PYTHON --> [ STRING, itemID, FLOAT, UINT32 ]
		"""
		ECenter.fireEvent( "EVT_ON_VEND_VENDOR_ADD_RECORD_BUY", record )

	def vend_buy( self, uid, vendorID ):
		"""
		�����һ����Ʒ�ӿ�

		param uid:	���������Ʒ��uid
		type uid:	INT64
		param vendorID:	���ҵ�entity id
		type vendorID:	OBJECT_ID
		"""
		if self.id == vendorID:
			HACK_MSG( "vendor�������Լ�." )
			return

		vendor = BigWorld.entities.get( vendorID )
		if vendor == None:
			HACK_MSG( "�Ҳ������, vendorID: %i" % ( vendorID ) )
			return

		vendor.cell.vend_sell( uid )

	def vend_buyPet( self, petDatabaseID, vendorID ):
		"""
		�����һ������Ľӿ�
		"""
		if self.id == vendorID:
			HACK_MSG( "vendor�������Լ�." )
			return

		vendor = BigWorld.entities.get( vendorID )
		if vendor == None:
			HACK_MSG( "�Ҳ������, vendorID: %i" % ( vendorID ) )
			return

		vendor.cell.vend_sellPet( petDatabaseID )

	def vend_removeItemNotify( self, uid ):
		"""
		Define method.
		��Ӧuid����Ʒ�����ߣ�������ҿͻ�������

		param uid: ���������Ʒ��uid
		type uid: INT64
		"""
		#try:
		#	del self.vendMerchandise[uid]
		#except KeyError:
		#	DEBUG_MSG( "uid(%i)�����ڡ�" % ( uid ) )
		ECenter.fireEvent( "EVT_ON_VEND_ITEM_SELLED", uid )
		# ֪ͨ����,wsf

	def	vend_removePetNotify( self, petDataBaseID ):
		"""
		dataBaseID�ĳ��ﱻ���ߣ�������ҿͻ�������
		"""
		ECenter.fireEvent( "EVT_ON_VEND_PET_SELLED",petDataBaseID )

	def vend_onLeaveWorld( self ):
		self.vendSignboard = ""

	def _isVend( self ):
		"""
		�ж��Լ��Ƿ��ڰ�̯״̬
		"""
		return self.getState() == csdefine.ENTITY_STATE_VEND

	def vend_onVendEnd( self ):
		"""
		������̯ʱ���á�
		ע�������������vend_endVend��
		vend_endVend�ǣ�	������������������رա�
		vend_onVendEnd�ǣ�	���������ͻ�״̬�ı�ʱ���á�
		"""
		if self.id == BigWorld.player().sellerID: #��ҹرտͻ��˹رս���
			# �ص�����
			ECenter.fireEvent( "EVT_ON_VEND_STATE_CHANGE", csdefine.ENTITY_STATE_FREE )
			BigWorld.player().sellerID = 0
		ECenter.fireEvent( "EVT_ON_VEND_RESET_SIGNBOARD", self.id )#�����Լ���������ͷ����Ϣ

#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/09/02 09:56:48  fangpengjun
# ��Ӽ�¼���º���vend_addRecordNotify���Լ�������Ϣ������Ϣ
#
# Revision 1.1  2007/12/14 07:31:20  wangshufeng
# ��Ӱ�̯ϵͳ(RoleVend)
#
#
#
#