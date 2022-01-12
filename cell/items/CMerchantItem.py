# -*- coding: gb18030 -*-



from CItemBase import CItemBase
import cschannel_msgs
import ShareTexts as ST


class CMerchantItem( CItemBase ):
	"""
	照片物品
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )
		self.set( "merchantItem", True )



	def canGive( self ):
		"""
		判断是否能给(玩家与玩家之间的物品交换)
		当该物品为绑定状态时，该物品不能交易

		@return: bool
		@rtype:  bool
		"""
		return False

	def onDieDrop( self ):
		"""
		"""
		if cschannel_msgs.ROLE_INFO_12 in self.name():
			return
		self.set( 'name', cschannel_msgs.ROLE_INFO_12 + self.name() )