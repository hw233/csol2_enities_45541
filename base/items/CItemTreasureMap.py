# -*- coding: gb18030 -*-
"""
�ر�ͼ��Ʒ�ࡣ
"""
import ItemAttrClass
import Love3
from CItemBase import CItemBase

class CItemTreasureMap( CItemBase ):
	"""
	�Զ������͵���ʵ������Ҫ���ڱ���ʹ���һЩ���ߵ��ױ�����
	"""
	def __init__( self, srcData ):
		"""
		@param srcData: ��Ʒ��ԭʼ����
		"""
		CItemBase.__init__( self, srcData )