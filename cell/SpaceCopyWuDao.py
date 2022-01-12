# -*- coding: gb18030 -*-
#


from SpaceCopy import SpaceCopy
import BigWorld
import csconst
import csstatus

IS_ENTER_TIME			= 1   # 标记进行判断是否存在对手
CLOSE_WUDAO_TIME		= 2   # 标记关闭武道大会
CLOSE_COPY				= 3	  # 标记关闭副本
CLOSE_WUDAO				= 4   # 关闭武道大会

class SpaceCopyWuDao( SpaceCopy ):
	"""
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )
		
		self.hasClearNoFight = False		# 标记是否已经清楚过角色的免战效果
		self.addTimer( csconst.WUDAO_TIME_PREPARE * 60, 0, IS_ENTER_TIME )
		self.addTimer( csconst.WUDAO_TIME_SPACE_LIVING * 60, 0, CLOSE_WUDAO_TIME )
		
	def onTimer( self, id, userArg ):
		"""
		"""
		if userArg == IS_ENTER_TIME: # 准备时间过后，查看是否有对手	
			if len( self.databaseIDList ) == 1 and len( self._players ) == 1: # 如果没有对手并且在副本中，直接获胜
				self._players[0].client.onStatusMessage( csstatus.WU_DAO_ENEMY_NOT_ENTER, "" )
				self._players[0].onWuDaoOver( self._players[0], 1 ) # 通知武道大会管理器，获胜方
				self.getScript().closeWuDao( self ) # 关闭武道大会
				return
				
			self.getScript().clearNoFight( self )

		elif userArg == CLOSE_WUDAO_TIME: # 关闭武道大会
			if len(self._players) == 1:
				self._players[0].client.onStatusMessage( csstatus.WU_DAO_WIN, "" )
				self._players[0].onWuDaoOver( self._players[0], 1 ) # 通知武道大会管理器，获胜方
			else:
				for e in self._players:
					e.client.onStatusMessage( csstatus.WU_DAO_DRAW, "" )
					e.onWuDaoOver( e, 0 ) # 通知武道大会管理器，失败方
			self.getScript().closeWuDao( self )
			return

		elif userArg == CLOSE_COPY:
			self.base.closeSpace( True )

		elif userArg == CLOSE_WUDAO:
			self.getScript().closeWuDao( self )