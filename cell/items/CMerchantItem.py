# -*- coding: gb18030 -*-



from CItemBase import CItemBase
import cschannel_msgs
import ShareTexts as ST


class CMerchantItem( CItemBase ):
	"""
	��Ƭ��Ʒ
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )
		self.set( "merchantItem", True )



	def canGive( self ):
		"""
		�ж��Ƿ��ܸ�(��������֮�����Ʒ����)
		������ƷΪ��״̬ʱ������Ʒ���ܽ���

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