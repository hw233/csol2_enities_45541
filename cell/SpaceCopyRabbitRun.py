# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy
import time
import BigWorld
import csconst
import Const

DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME = 10.0						#玩家全部离开副本后，隔多久副本才删除

class SpaceCopyRabbitRun( SpaceCopy ):
	
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )
	
	def onEnterCommon( self, baseMailbox, params ):
		"""
		define method
		"""
		if not self.queryTemp( "firstEnter", False ):
			self.setTemp( "firstEnter", True )
		SpaceCopy.onEnterCommon( self, baseMailbox, params )

	def shownDetails( self ):
		"""
		shownDetails 副本内容显示规则：
		[ 
			0: 剩余时间
			1: 剩余小怪
			2: 剩余小怪批次
			3: 剩余BOSS
			4: 蒙蒙数量
			5: 剩余魔纹虎数量
			6: 剩余真鬼影狮数量
			7: 下一波剩余时间(拯救猰貐)
			8: 猰貐血量百分比
		]
		"""
		# 显示剩余小怪，剩余BOSS。 
		return [ 1, 3 ]

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		退出
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		
		if len( self._players ) == 0:
			self.addTimer( DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME, 0, Const.SPACE_COPY_CLOSE_CBID )


	def onTimer( self, id, userArg ):
		"""
		覆盖底层的onTimer()处理机制
		"""
		SpaceCopy.onTimer( self, id, userArg )


