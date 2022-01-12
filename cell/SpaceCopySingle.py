# -*- coding: gb18030 -*-

# common
from bwdebug import *
# base
from SpaceCopy import SpaceCopy
import BigWorld
import Const

DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME = 10.0						# 玩家全部离开副本后，隔多久副本才删除

class SpaceCopySingle( SpaceCopy ):
	"""
	单人地图
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopy.__init__( self )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		define method.
		一个entity准备离开space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onLeave()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 要离开此space的entity mailbox
		@param params: dict; 离开此space时需要的附加数据。此数据由当前脚本的packedDataOnLeave()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		
		if len( self._players ) == 0:
			self.addTimer( DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME, 0, Const.SPACE_COPY_CLOSE_CBID )
#