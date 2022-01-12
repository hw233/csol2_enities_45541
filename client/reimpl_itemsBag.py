# -*- coding: gb18030 -*-

"""
2010.05.15: writen by pengju
"""

from AbstractTemplates import MultiLngFuncDecorator
import csdefine

class deco_itemsBagUseKitBagItem( MultiLngFuncDecorator ) :
	@staticmethod
	def locale_big5( SELF, uid ) :
		"""
		使用背包物品
		@param uid 			: 物品的唯一ID
		@type uid			: INT64
		"""
		item = SELF.getItemByUid_( uid )
		kitOrder = item.getKitID()
		orderID = item.getOrder()%csdefine.KB_MAX_SPACE
		for i in xrange( csdefine.KB_EXCONE_ID , csdefine.KB_EXCSIX_ID + 1 ):
			if i not in SELF.kitbags:
				SELF.moveKbItemToKitTote( kitOrder, orderID, i )
				break
