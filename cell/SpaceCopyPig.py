# -*- coding: gb18030 -*-

from bwdebug import *
from SpaceCopy import SpaceCopy
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface

class SpaceCopyPig( SpaceCopy, SpaceCopyYeWaiInterface ):
	
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )
		SpaceCopyYeWaiInterface.__init__( self )

	def shownDetails( self ):
		"""
		shownDetails 副本内容显示规则：
		[ 
			0: 剩余时间
			1: 剩余小怪
			3: 剩余BOSS
		]
		"""
		return [ 0, 1, 3 ]

	def checkSpaceIsFull( self ):
		"""
		检查空间是否满员
		"""
		return SpaceCopyYeWaiInterface.checkSpaceIsFull( self )