# -*- coding: gb18030 -*-
#

"""
implement Animation
"""

from guis.common.RootGUI import RootGUI
import GUI
import BigWorld

class Animation( RootGUI ):
	"""
	动画窗体
	"""
	def __init__( self, gui = None ):
		"""
		初始化
		"""
		RootGUI.__init__( self, gui )
		
		self.visible = False							# 显示
		self.playTime = 1								# 播放时间
		self.__playCBID = 0								# CBID
		self.focus = False								# 避免动画在播放时被移动
		
	def initAnimation( self, name, time = 1 ):
		"""
		设定动画
		name	添加到管理器名
		time 	播放时间
		"""
		self.addToMgr( name )							# 添加到管理器
		self.playTime = time
		self.getGui().stopAt = 0
	
	def playAnimation( self, pos = ( 0, 0 ), pyOwner = None ):
		"""
		播放动画
		pos		位置
		pyOwner	父窗体
		"""
		if self.__playCBID != 0:
			return
			
		self.left = pos[0]
		self.top = pos[1]
		self.__beginAnimation( pyOwner )
		self.__playCBID = BigWorld.callback( self.playTime, self.__endAnimation )
		
	def __beginAnimation( self, pos, pyOwner = None ):
		"""
		开始动画
		pos 		位置
		pyOwner		父窗体
		"""
		RootGUI.show( self, pyOwner )
		self.getGui().stopAt = -1
		
	def __endAnimation( self ):
		"""
		结束动画
		"""
		RootGUI.hide( self )
		self.getGui().stopAt = 0
		self.__playCBID = 0