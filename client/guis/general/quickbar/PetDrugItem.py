# -*- coding: gb18030 -*-

import Define
from guis.ItemsBrush import itemsBrush
from AutoFightItem import AutoFightItem

class PetDrugItem( AutoFightItem ) :
	"""
	�����Զ�ս�������ҩ��Item
	"""
	def update( self, itemInfo, isNotInit = True ) :
		AutoFightItem.update( self, itemInfo )
		if itemInfo is not None :
			itemsBrush.attach( self )							# ���Խ����߸��Ӱ󶨵���Ʒˢ
			self.updateUseStatus( itemInfo.checkUseStatus() )	# ������Ʒ�Ŀ�ʹ��״̬
		else:
			itemsBrush.detach( self )							# �����߸��Ӵ���Ʒˢ���
			self.updateUseStatus( Define.ITEM_STATUS_NATURAL )
	
	def updateUseStatus( self, itemStatus ) :
		"""
		������Ʒ��ʹ��״̬�ı���
		"""
		self.color = Define.ITEM_STATUS_TO_COLOR[ itemStatus ]