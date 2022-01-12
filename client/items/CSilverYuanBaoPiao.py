# -*- coding: gb18030 -*-



from CItemBase import CItemBase
import ItemAttrClass
from guis.tooluis.richtext_plugins.PL_Font import PL_Font

class CSilverYuanBaoPiao( CItemBase ):
	"""
	银元宝票
	"""
	def __init__( self, srcData ):
		CItemBase.__init__( self, srcData )

	def getProDescription( self, reference ):
		"""
		virtual method
		获取物品专有描述信息
		"""
		attrMap = ItemAttrClass.m_itemAttrMap
		golddes = attrMap["silverYuanbao"].description( self, reference )
		self.desFrame.SetDescription("silverYuanbao", PL_Font.getSource( golddes ,fc = "c24" ))