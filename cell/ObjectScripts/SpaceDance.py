# -*- coding: gb18030 -*-
#

"""
"""
from Space import Space
import csconst

class SpaceDance( Space ):
	"""
	���ڿ���SpaceNormal entity�Ľű�����������Ҫ��SpaceNormal����������ô˽ű�(��̳��ڴ˽ű��Ľű�)�Ľӿ�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		Space.__init__( self )

	def onEnter( self, selfEntity, baseMailbox, params ):
		"""
		��������
		"""
		Space.onEnter( self, selfEntity, baseMailbox, params )
		baseMailbox.cell.addWuTingBuff()
		baseMailbox.cell.enterWuTing()
		
	def onLeave( self, selfEntity, baseMailbox, params  ):
		"""
		�߿�����
		"""
		Space.onLeave( self, selfEntity, baseMailbox, params )
		baseMailbox.cell.leaveWuTing()


