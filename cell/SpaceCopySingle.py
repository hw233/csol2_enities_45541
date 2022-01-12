# -*- coding: gb18030 -*-

# common
from bwdebug import *
# base
from SpaceCopy import SpaceCopy
import BigWorld
import Const

DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME = 10.0						# ���ȫ���뿪�����󣬸���ø�����ɾ��

class SpaceCopySingle( SpaceCopy ):
	"""
	���˵�ͼ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopy.__init__( self )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		define method.
		һ��entity׼���뿪spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onLeave()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		@param params: dict; �뿪��spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnLeave()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		
		if len( self._players ) == 0:
			self.addTimer( DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME, 0, Const.SPACE_COPY_CLOSE_CBID )
#