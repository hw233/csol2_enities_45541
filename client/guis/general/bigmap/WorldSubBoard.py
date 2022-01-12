# -*- coding: gb18030 -*-
#
# $Id: WorldArea.py,v 1.28 2008-08-27 09:04:26 huangyongwei Exp $

"""
implement sub area of the world map

2009.09.27 : wirten by huangyongwei
"""

from cscustom import Polygon
from guis import *
from guis.common.ScriptObject import ScriptObject

class WorldSubBoard( ScriptObject ) :
	__cg_pyBoards = []							# 保存所有板块
	__cg_pySelBoard = None						# 当前鼠标选中的板块
	__cg_lastHitCount = 0						# 鼠标击中板块的数量

	def __init__( self, board ) :
		if len( WorldSubBoard.__cg_pyBoards ) == 0 :					# 保证只添加一次
			LastMouseEvent.attach( WorldSubBoard.__onLastMouseEvent )	# 添加鼠标移动事件，以侦测鼠标的位置
		WorldSubBoard.__cg_pyBoards.append( self )						# 保存倒板块列表中
		gui = GUI.Simple( "" )
		ScriptObject.__init__( self, gui )
		self.setToDefault()
		gui.size = board.size
		util.setGuiState( gui )
		self.focus = True
		self.__board = board											# MapMgr.WorldArea.SubBoard
		self.__polygon = Polygon( board.polygon.points )				# 区域顶点

	def __del__( self ) :
		ScriptObject.__del__( self )
		if Debug.output_del_BigMapWorldSubBoard :
			INFO_MSG( str( self ) )

	def dispose( self ) :
		if len( WorldSubBoard.__cg_pyBoards ) :						# 保证只删除一次
			LastMouseEvent.detach( self.__onLastMouseEvent )		# 取消鼠标移动事件
		WorldSubBoard.__cg_pyBoards = []							# 清除所有板块
		WorldSubBoard.__cg_pySelBoard = None						# 去掉选中板块的引用
		ScriptObject.dispose( self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	def __onLastMouseEvent( dx, dy, dz ) :
		"""
		鼠标在按钮上并移动时调用
		"""
		pySelBoard = WorldSubBoard.__cg_pySelBoard
		pyHitedBoards = []
		for pyBoard in WorldSubBoard.__cg_pyBoards :
			if pyBoard.isMouseHit() :
				pyHitedBoards.append( pyBoard )
		oldCount = WorldSubBoard.__cg_lastHitCount
		count = len( pyHitedBoards )							# 鼠标击中板块数量
		WorldSubBoard.__cg_lastHitCount = count
		if count == 0 :											# 鼠标没有击中任何板块
			if pySelBoard :
				pySelBoard.onMouseLeave_()
		elif count == 1 :
			pyBoard = pyHitedBoards[0]
			if pyBoard == pySelBoard :							# 鼠标只在当前选中板块中
				return
			if pySelBoard :
				pySelBoard.onMouseLeave_()
			pyBoard.onMouseEnter_()
		else :													# 鼠标击中多个板块
			if oldCount < count and \
				pySelBoard in pyHitedBoards :					# 鼠标从一个板块进入多个板块的边界
					pyHitedBoards.remove( pySelBoard )			# 则以新板块作为选中板块(防止有重叠板块时，鼠标在边界时，总是击中固定的一个板块)
			if pySelBoard in pyHitedBoards :
				return
			if pySelBoard :
				pySelBoard.onMouseLeave_()
			pyHitedBoards[0].onMouseEnter_()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseEnter_( self ) :
		ScriptObject.onMouseEnter_( self )
		self.texture = self.__board.texture
		WorldSubBoard.__cg_pySelBoard = self

	def onMouseLeave_( self ) :
		ScriptObject.onMouseLeave_( self )
		self.texture = ""
		WorldSubBoard.__cg_pySelBoard = None

	def onLClick_( self, mods ) :
		pySelBoard = WorldSubBoard.__cg_pySelBoard
		if pySelBoard :											# 理论上，总不会是 None
			ScriptObject.onLClick_( pySelBoard, mods )
		return True


	# -------------------------------------------------
	# rewrite method
	# -------------------------------------------------
	def isMouseHit( self ) :
		"""
		重写isMouseHit方法，判断鼠标是否落在多边形内
		"""
		return ScriptObject.isMouseHit( self ) and \
			self.__polygon.isPointIn( self.mousePos )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getScale( self ) :
		return self.__scale

	def _setScale( self, scale ) :
		self.__scale = scale
		self.size = scale * self.__board.size
		self.pos = scale * self.__board.pos
		points = self.__board.polygon.points
		self.__polygon.update( [p * scale for p in points] )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	scale = property( _getScale, _setScale )
	area = property( lambda self : self.__board.area )
