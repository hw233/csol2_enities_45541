# -*- coding: gb18030 -*-

# $Id: PresentChargeUnite.py  hd
# �����ȡ��Ӫ������ͳ�ֵԪ����ģ��

from bwdebug import *
import items
import csstatus
import csdefine
import sys

g_items = items.instance()

class PresentChargeUnite:
	"""
	�����ȡ��Ӫ������ͳ�ֵԪ����ģ��
	"""
	def __init__( self ):
		pass

	def pcu_takeThings( self, dataType, item_id ):
		"""
		��ʼ��ȡ��Ʒ���߳�ֵ,�ýӿ������ӿڣ����ú���ܻ�ȡ��ȡ����Ʒ
		@type  dataType	: UINT8
		@param dataType	: ��ȡ������
		@type  item_id	: ITEM_ID
		@param item_id	: ��ȡ����Ʒ��ID
		"""
		self.base.pcu_takeThings(dataType, item_id)

	def pcu_getPresentTypes( self ):
		"""
		�������������ȡ���ӵ�еĽ�������
		"""
		self.base.pcu_getPresentTypes()

	def pcu_onGetPresentTypes(self, types):
		"""
		@define method
		pcu_getPresentTypes�ӿڻ�ȡ�������ͺ󣬸ýӿڽ��յ����ս�����ý�������������ȡ����
		"""
		pass

	def takePresent( self, presentIDs ):
		"""
		@define method
		��ȡ��Ʒ��
		"""
		itemInstances = []
		for id in presentIDs:
			item = g_items.createDynamicItem( int( id ))
			itemInstances.append( item )
		# ���ж��ܷ���뱳��
		checkReult = self.checkItemsPlaceIntoNK_( itemInstances )
		if checkReult != csdefine.KITBAG_CAN_HOLD :
			self.base.takeOverFailed()
			self.statusMessage( csstatus.PCU_NOT_ENOUGH_GRID )
			return
		for item in itemInstances:
			self.addItem( item, csdefine.ADD_ITEM_TAKEPRESENT )

		self.base.takeOverSuccess()					#֪ͨbase��������
