# -*- coding: gb18030 -*-
#

"""
"""
from SpaceCopy import SpaceCopy
import csconst
import BigWorld

class SpaceCopyDanceHall( SpaceCopy ):
	"""
	���ڿ���SpaceNormal entity�Ľű�����������Ҫ��SpaceNormal����������ô˽ű�(��̳��ڴ˽ű��Ľű�)�Ľӿ�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopy.__init__( self )

	def onEnter( self, selfEntity, baseMailbox, params ):
		"""
		��������
		"""
		SpaceCopy.onEnter( self, selfEntity, baseMailbox, params )
		baseMailbox.cell.enterWuTing()
		
	def onLeave( self, selfEntity, baseMailbox, params  ):
		"""
		�߿�����
		"""
		SpaceCopy.onLeave( self, selfEntity, baseMailbox, params )
		baseMailbox.cell.leaveWuTing()
		


