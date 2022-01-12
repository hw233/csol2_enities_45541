# -*- coding: gb18030 -*-



from CItemBase import CItemBase


class CSilverYuanBaoPiao( CItemBase ):
	"""
	银元宝票
	"""
	def __init__( self, srcData ):
		CItemBase.__init__( self, srcData )
		self.set( 'silverYuanbao', int( srcData["param1"] ))
		
		
