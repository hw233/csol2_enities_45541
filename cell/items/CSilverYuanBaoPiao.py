# -*- coding: gb18030 -*-



from CItemBase import CItemBase


class CSilverYuanBaoPiao( CItemBase ):
	"""
	��Ԫ��Ʊ
	"""
	def __init__( self, srcData ):
		CItemBase.__init__( self, srcData )
		self.set( 'silverYuanbao', int( srcData["param1"] ))
		
		
