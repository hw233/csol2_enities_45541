# -*- coding: gb18030 -*-



from CItemBase import CItemBase
import ItemAttrClass
from guis.tooluis.richtext_plugins.PL_Font import PL_Font

class CSilverYuanBaoPiao( CItemBase ):
	"""
	��Ԫ��Ʊ
	"""
	def __init__( self, srcData ):
		CItemBase.__init__( self, srcData )

	def getProDescription( self, reference ):
		"""
		virtual method
		��ȡ��Ʒר��������Ϣ
		"""
		attrMap = ItemAttrClass.m_itemAttrMap
		golddes = attrMap["silverYuanbao"].description( self, reference )
		self.desFrame.SetDescription("silverYuanbao", PL_Font.getSource( golddes ,fc = "c24" ))