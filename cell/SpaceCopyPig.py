# -*- coding: gb18030 -*-

from bwdebug import *
from SpaceCopy import SpaceCopy
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface

class SpaceCopyPig( SpaceCopy, SpaceCopyYeWaiInterface ):
	
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopy.__init__( self )
		SpaceCopyYeWaiInterface.__init__( self )

	def shownDetails( self ):
		"""
		shownDetails ����������ʾ����
		[ 
			0: ʣ��ʱ��
			1: ʣ��С��
			3: ʣ��BOSS
		]
		"""
		return [ 0, 1, 3 ]

	def checkSpaceIsFull( self ):
		"""
		���ռ��Ƿ���Ա
		"""
		return SpaceCopyYeWaiInterface.checkSpaceIsFull( self )