# -*- coding: gb18030 -*-
#
# $Id: RoleTradeWithNPC.py,v 1.7 2008-05-04 06:44:37 zhangyuxing Exp $

"""
"""

import BigWorld
import GUIFacade
import csdefine
import event.EventCenter as ECenter
from bwdebug import *

class RoleTradeWithNPC:
	"""
	��NPC���˽���
	"""

	def __init__( self ) :
		self.__targetID = 0					# ��ǰ���� NPC �� ID	��2008.09.16��

	def leaveTradeWithNPC( self ):
		"""
		Define Method
		�뿪����NPC����״̬
		"""
		self.__targetID = 0									# ����Ի� NPC �� ID
		GUIFacade.onTradeWithNPCOver()

	def enterTradeWithNPC( self, objectID ):
		"""
		Define Method
		������NPC����״̬
		@param   objectID: ����Ŀ��
		@type    objectID: OBJECT_ID
		@return: ��
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The trade NPC  %s has not exist " % objectID )
			self.__targetID = 0
			return

		if self.__targetID == objectID : return								# �ظ������ͬһ�� NPC ���н��ף��򷵻�
		ECenter.fireEvent("EVT_ONTRADE_STATE_LEAVE", self.tradeState )		# �����֮ǰ�Ľ��ף����������ܲ��ã�
		self.__targetID = objectID											# ��¼�µ�ǰ�Ի��� NPC ID��hyw -- 2008.09.16��
		# ȡ����Ʒ�б�
		#if not entity.isRequesting() :										# �����Ƿ�����Ʒ��������е��ж�( hyw -- 2008.09.16 )
		entity.cell.sendInvoiceListToClient()								# ���������������Ʒ�б�״̬���򲻻�������
		# ֪ͨ��ʼ������
		tradeObject = entity.__class__.__name__
		if tradeObject == "Merchant":
			entity.cell.sendPriceChangeInfo()								# �����������۸�䶯��Ϣ��ֻ��Merchant�����������
			GUIFacade.onTradeWithMerchant( entity )
		elif tradeObject == "DarkMerchant":
			entity.cell.sendPriceChangeInfo()
			GUIFacade.onTradeWithDarkMerchant( entity )
		elif tradeObject == "YXLMEquipChapman":
			GUIFacade.onTradeWithYXLMEquipChapman( entity )
		else:
			#entity.__class__.__name__ == "Chapman":
			GUIFacade.onTradeWithNPC( entity )

	def enterTradeWithDarkTrader( self, objectID ):
		"""
		Define Method
		��Ͷ�����˴�������Ʒ
		@param   objectID: ����Ŀ��
		@type    objectID: OBJECT_ID
		@return: ��
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The trade NPC  %s has not exist " % objectID )
			self.__targetID = 0
			return
		if self.__targetID == objectID:
			return										# �ظ������ͬһ�� NPC ���н��ף��򷵻�
		ECenter.fireEvent("EVT_ONTRADE_STATE_LEAVE", self.tradeState )	# �����֮ǰ�Ľ��ף����������ܲ��ã�
		self.__targetID = objectID						# ��¼�µ�ǰ�Ի��� NPC ID��hyw -- 2008.09.16��
		entity.cell.sendInvoiceListToClient()			# ȡ����Ʒ�б����������������Ʒ�б�״̬���򲻻�������
		GUIFacade.onTradeWithDarkTrader( entity )		# ֪ͨ��ʼ������

	def tradeWithItemChapman( self, objectID ):
		"""
		Define Method
		������NPC����״̬
		@param   objectID: ����Ŀ��
		@type    objectID: OBJECT_ID
		@return: ��
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The trade NPC  %s has not exist " % objectID )
			self.__targetID = 0
			return

		if self.__targetID == objectID : return								# �ظ������ͬһ�� NPC ���н��ף��򷵻�
		ECenter.fireEvent("EVT_ONTRADE_STATE_LEAVE", self.tradeState )		# �����֮ǰ�Ľ��ף����������ܲ��ã�
		self.__targetID = objectID											# ��¼�µ�ǰ�Ի��� NPC ID
		# ȡ����Ʒ�б�
		entity.cell.sendInvoiceListToClient()								# ���������������Ʒ�б�״̬���򲻻�������
		# ֪ͨ��ʼ������
		GUIFacade.onTradeWithItemChapman( entity )

	def tradeWithPointChapman( self, objectID ):
		"""
		Define Method
		������NPC����״̬
		@param   objectID: ����Ŀ��
		@type    objectID: OBJECT_ID
		@return: ��
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The trade NPC  %s has not exist " % objectID )
			self.__targetID = 0
			return
		if self.__targetID == objectID : return								# �ظ������ͬһ�� NPC ���н��ף��򷵻�
		ECenter.fireEvent("EVT_ONTRADE_STATE_LEAVE", self.tradeState )		# �����֮ǰ�Ľ��ף����������ܲ��ã�
		self.__targetID = objectID											# ��¼�µ�ǰ�Ի��� NPC ID
		# ȡ����Ʒ�б�
		entity.cell.sendInvoiceListToClient()								# ���������������Ʒ�б�״̬���򲻻�������
		# ֪ͨ��ʼ������
		GUIFacade.onTradeWithPointChapman( entity )

	def onTradeWithTongSpecialChapman( self, objectID ):
		"""
		�����������˶Ի�
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The trade NPC  %s has not exist " % objectID )
			self.__targetID = 0
			return
		if self.__targetID == objectID : return								# �ظ������ͬһ�� NPC ���н��ף��򷵻�
		ECenter.fireEvent("EVT_ONTRADE_STATE_LEAVE", self.tradeState )		# �����֮ǰ�Ľ��ף����������ܲ��ã�
		self.__targetID = objectID											# ��¼�µ�ǰ�Ի��� NPC ID
		# ȡ����Ʒ�б�
		entity.cell.sendInvoiceListToClient()								# ���������������Ʒ�б�״̬���򲻻�������
		# ֪ͨ��ʼ������
		GUIFacade.onTradeWithTongSpecialChapman( entity )

	def delRedeemItemUpdate( self, uid ):
		"""
		Define method.
		�ع�һ���������Ʒ�ɹ��ĸ��º�����ɾ��������б�Ķ�Ӧ��Ʒ

		param uid:
		type uid:
		"""
		GUIFacade.onDelRedeemItem( uid )

	def addRedeemItemUpdate( self, item ):
		"""
		Define method.
		���������Ʒ�б�������Ʒ�ĸ��º���

		param item:	�¼��������б����Ʒ
		type item:	ITEM
		"""
		GUIFacade.onAddRedeemItem( item )

	def getTradeNPCID( self ) :
		"""
		��ȡ��ǰ���ڽ��׵� NPC ID
		hyw -- 2008.09.16
		@rtype				: INT32
		@return				: ������ڽ��� NPC �򷵻� NPC ID�����򷵻� 0
		"""
		return self.__targetID

	def onAddYXLMEquip( self, equipInstance ):
		"""
		<Define method>
		���Ӣ�����˵�װ��
		@type	equipItem : ITEM
		@param	equipItem : �̳���CItemBase����Ʒʵ��
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ADD_YXLM_EQUIP", equipInstance )

	def onRemoveYXLMEquip( self, equipUid ) :
		"""
		<Define method>
		�Ƴ�Ӣ�����˵�װ��
		@type	equipUid : UID
		@param	equipUid : ��Ʒʵ����UID
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_REMOVE_YXLM_EQUIP", equipUid )
#
# $Log: not supported by cvs2svn $
# Revision 1.6  2007/11/19 08:10:11  wangshufeng
# add interface: delRedeemItemUpdate,�ع�һ���������Ʒ�ɹ��ĸ��º���;
# add interface: addRedeemItemUpdate,�������Ʒ�б����ݱ䶯�ĸ��º���;
#
# Revision 1.5  2007/08/18 08:12:31  yangkai
# NPC���״������
#     - �޸���ؽӿ�
#
# Revision 1.4  2007/06/14 10:32:35  huangyongwei
# ������ȫ�ֺ궨��
#
# Revision 1.3  2006/07/21 08:12:37  phw
# �޸��˽ӿڣ�
#     onLeaveTrade()
#     onEnterTrade()
#
# Revision 1.2  2006/05/18 03:28:26  huangyongwei
# no message
#
# Revision 1.1  2005/12/12 01:58:55  phw
# no message
#
#
