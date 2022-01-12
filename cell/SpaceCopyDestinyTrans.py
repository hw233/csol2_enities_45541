# -*- coding: gb18030 -*-

import Const
from bwdebug import *
from SpaceCopy import SpaceCopy
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface

DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME = 3.0

class SpaceCopyDestinyTrans( SpaceCopy, SpaceCopyYeWaiInterface ):
	"""
	�����ֻظ���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopy.__init__( self )
		SpaceCopyYeWaiInterface.__init__( self )

	def onEnterCommon( self, baseMailbox, params ):
		"""
		define method
		"""
		SpaceCopy.onEnterCommon( self, baseMailbox, params )

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

	def shownDetails( self ):
		"""
		shownDetails ����������ʾ����
		[ 
			0: ʣ��ʱ��
			1: ʣ��С��
			2: ʣ��С������
			3: ʣ��BOSS
			4: ��������
			5: ʣ��ħ�ƻ�����
			6: ʣ�����Ӱʨ����
		]
		"""
		return [ 0, 1, 3 ]

	def checkSpaceIsFull( self ):
		"""
		����SpaceCopyYeWaiInterface�ĸ÷���
		"""
		return False