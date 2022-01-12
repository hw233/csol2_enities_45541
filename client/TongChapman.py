# -*- coding: gb18030 -*-
#
# $Id: Chapman.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
Chapman����
"""

import BigWorld
from bwdebug import *
import csdefine
import csstatus
import GUIFacade
from Chapman import Chapman

class TongChapman( Chapman ):
	"""
	����������NPC����
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		Chapman.__init__( self )

	def onReceiveMakeItemData( self, buildingLevel, currHouqinVal, currMakeItemData, canMakeItemIDs ):
		"""
		define method.
		�յ������İ���������Ʒ�б�
		@param buildingLevel		:�����ļ��� �̵�
		@param currentMakeHouqinVal	:��ǰ�о���Ʒ���о��ĺ��ڶ�
		@param currentMakeItem		:��ǰ������������Ʒ
		@param canMakeItemIDs		:����������Ʒ�б�
		"""
		GUIFacade.tong_onShowTongMakeItemWindow( self, buildingLevel, currHouqinVal, currMakeItemData, canMakeItemIDs )

	def makeItems( self, makeItemID ):
		"""
		��������������������Ʒ
		@param makeItemID	:��ƷID
		"""
		return

	def onChangeMakeItem( self, makeItemID, makeAmount ):
		"""
		��ǰ�з���Ʒ���ı�
		@param makeItemID	:��ƷID
		@param makeAmount	:Ҫ����������
		"""
		GUIFacade.tong_onChangeMakeItem( makeItemID, makeAmount )

	def onReceiveGoodsAmountChange( self, uid, currAmount ):
		"""
		���ܵ���������Ʒ�����ı�֪ͨ

		@param	uid:		��ƷID
		@type	uid:		UINT16
		@param	currAmount:	��Ʒʣ������
		@param	currAmount:	UINT16
		"""
		GUIFacade.updateInvoiceAmount( uid, currAmount )

# Chapman.py
