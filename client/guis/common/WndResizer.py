# -*- coding: gb18030 -*-
#
# $Id: ChatWindow.py,v 1.60 2008-09-04 01:00:31 huangyongwei Exp $

"""
imlement resize bord for window

2009/04/20: writen by huangyongwei
"""
"""
固定名字:
	lt			t			  rt
	┌────────────┐
	│                        │
	│                        │
   l│                        │r
	│                        │
	│                        │
	└────────────┘
	lb			b			  rb
"""


import weakref
from guis import *
from guis.controls.Control import Control

INC_DIRECT_L		= 1									# 向左拉伸
INC_DIRECT_R		= 2									# 向右拉伸
INC_DIRECT_T		= 4									# 向上拉伸
INC_DIRECT_B		= 8									# 向下拉伸
INC_DIRECT_LT		= INC_DIRECT_L | INC_DIRECT_T		# 向左上角拉伸
INC_DIRECT_RT		= INC_DIRECT_R | INC_DIRECT_T		# 向右上角拉伸
INC_DIRECT_LB		= INC_DIRECT_L | INC_DIRECT_B		# 向左下角拉伸
INC_DIRECT_RB		= INC_DIRECT_R | INC_DIRECT_B		# 向右下角拉伸

class WndResizer( object ) :
	__cc_boards = {							# 拉边与递增方向的关系
		'l'  : INC_DIRECT_L,
		'r'  : INC_DIRECT_R,
		't'  : INC_DIRECT_T,
		'b'  : INC_DIRECT_B,
		'lt' : INC_DIRECT_LT,
		'rt' : INC_DIRECT_RT,
		'lb' : INC_DIRECT_LB,
		'rb' : INC_DIRECT_RB,
		}

	__cc_resizers = {						# 大小处理方法
		INC_DIRECT_L  : "l_resize_",
		INC_DIRECT_R  : "r_resize_",
		INC_DIRECT_T  : "t_resize_",
		INC_DIRECT_B  : "b_resize_",
		INC_DIRECT_LT : "lt_resize_",
		INC_DIRECT_RT : "rt_resize_",
		INC_DIRECT_LB : "lb_resize_",
		INC_DIRECT_RB : "rb_resize_",
		}

	def __init__( self, pyWnd, boards ) :
		"""
		@type			pyWnd  : RootGUI
		@param			pyWnd  : 要拉伸的窗口
		@type			boards : dict
		@param			boards : 拉边（可选）：
								 'l'  : GUI.Simple 左边
								 'r'  : GUI.Simple 右边
								 't'  : GUI.Simple 顶边
								 'b'  : GUI.Simple 底边
								 'lt' : GUI.Simple 左上角
								 'rt' : GUI.Simple 右上角
								 'lb' : GUI.Simple 左下角
								 'rb' : GUI.Simple 右下角
		"""
		self.pyBoards_ = {}
		for key, board in boards.iteritems() :
			direct = WndResizer.__cc_boards[key]
			pyBoard = Board( direct, board, self )
			self.pyBoards_[direct] = pyBoard
		self.__events = []									# 事件列表
		self.generateEvents_()

		self.__pyWnd = weakref.ref( pyWnd )					# 绑定的窗口
		self.__autoReisize = True							# 是否自动改变大小
		self.__wndRB = pyWnd.right, pyWnd.bottom			# 纪录窗口的右下角位置
		self.__size = pyWnd.size							# 开始改变大小时，纪录下窗口大小
		self.__tmpDirect = 0								# 开始改变大小时，纪录下改变的方向

		self.__minWidth = pyWnd.width						# 窗口的最小宽度
		self.__maxWidth = pyWnd.width						# 窗口的最大宽度
		self.__minHeight = pyWnd.height						# 窗口的最小高度
		self.__maxHeight = pyWnd.height						# 窗口的最大高度


	def __del__( self ) :
		if Debug.output_del_WndResizer :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def createEvent_( self, ename ) :
		event = ControlEvent( ename, self )
		self.__events.append( event )
		return event

	def generateEvents_( self ) :
		self.__onShowResizer = self.createEvent_( "onShowResizer" )		# 显示改变宽度边
		self.__onHideResizer = self.createEvent_( "onHideResizer" )		# 隐藏改变宽度边
		self.__onBeginResized = self.createEvent_( "onBeginResized" )	# 开始改变宽度
		self.__onEndResized = self.createEvent_( "onEndResized" )		# 结束改变宽度
		self.__onResizing = self.createEvent_( "onResizing" )			# 正在改变宽度

	@property
	def onShowResizer( self ) :
		return self.__onShowResizer

	@property
	def onHideResizer( self ) :
		return self.__onHideResizer

	@property
	def onBeginResized( self ) :
		return self.__onBeginResized

	@property
	def onEndResized( self ) :
		return self.__onEndResized

	@property
	def onResizing( self ) :
		return self.__onResizing


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def l_resize_( self, dx, dy ) :
		"""
		拉动左边的扩展条
		"""
		pyWnd = self.pyWnd
		width = self.__size[0] - dx
		width = max( self.__minWidth, width )
		if self.__maxWidth > 0 :
			width = min( self.__maxWidth, width )
		pyWnd.width = width
		pyWnd.right = self.__wndRB[0]

	def r_resize_( self, dx, dy ) :
		"""
		拉动右边的扩展条
		"""
		pyWnd = self.pyWnd
		width = self.__size[0] + dx
		width = max( self.__minWidth, width )
		if self.__maxWidth > 0 :
			width = min( self.__maxWidth, width )
		pyWnd.width = width

	def t_resize_( self, dx, dy ) :
		"""
		拉动上边的扩展条
		"""
		pyWnd = self.pyWnd
		height = self.__size[1] - dy
		height = max( self.__minHeight, height )
		if self.__maxHeight > 0 :
			height = min( self.__maxHeight, height )
		pyWnd.height = height
		pyWnd.bottom = self.__wndRB[1]

	def b_resize_( self, dx, dy ) :
		"""
		拉动底边的扩展条
		"""
		pyWnd = self.pyWnd
		height = self.__size[1] + dy
		height = max( self.__minHeight, height )
		if self.__maxHeight > 0 :
			height = min( self.__maxHeight, height )
		top = pyWnd.top
		pyWnd.height = height
		pyWnd.top = top

	def lt_resize_( self, dx, dy ) :
		"""
		拉动左上角的扩展点
		"""
		pyWnd = self.pyWnd
		width = self.__size[0] - dx
		width = max( self.__minWidth, width )
		if self.__maxWidth > 0 :
			width = min( self.__maxWidth, width )
		height = self.__size[1] - dy
		height = max( self.__minHeight, height )
		if self.__maxHeight > 0 :
			height = min( self.__maxHeight, height )
		pyWnd.size = width, height
		pyWnd.right = self.__wndRB[0]
		pyWnd.bottom = self.__wndRB[1]

	def rt_resize_( self, dx, dy ) :
		"""
		拉动右上角扩展点
		"""
		pyWnd = self.pyWnd
		width = self.__size[0] + dx
		width = max( self.__minWidth, width )
		if self.__maxWidth > 0 :
			width = min( self.__maxWidth, width )
		height = self.__size[1] - dy
		height = max( self.__minHeight, height )
		if self.__maxHeight > 0 :
			height = min( self.__maxHeight, height )
		pyWnd.size = width, height
		pyWnd.bottom = self.__wndRB[1]

	def lb_resize_( self, dx, dy ) :
		"""
		拉动左下角扩展点
		"""
		pyWnd = self.pyWnd
		width = self.__size[0] - dx
		width = max( self.__minWidth, width )
		if self.__maxWidth > 0 :
			width = min( self.__maxWidth, width )
		height = self.__size[1] + dy
		height = max( self.__minHeight, height )
		if self.__maxHeight > 0 :
			height = min( self.__maxHeight, height )
		pyWnd.size = width, height
		pyWnd.right = self.__wndRB[0]

	def rb_resize_( self, dx, dy ) :
		"""
		拉动右下角扩展点
		"""
		pyWnd = self.pyWnd
		width = self.__size[0] + dx
		width = max( self.__minWidth, width )
		if self.__maxWidth > 0 :
			width = min( self.__maxWidth, width )
		height = self.__size[1] + dy
		height = max( self.__minHeight, height )
		if self.__maxHeight > 0 :
			height = min( self.__maxHeight, height )
		pos = pyWnd.pos
		pyWnd.size = width, height
		pyWnd.pos = pos

	# -------------------------------------------------
	def onShowResizer_( self, pyBoard ) :
		"""
		提示拉动
		"""
		self.onShowResizer( pyBoard )

	def onHideResizer_( self, pyBoard ) :
		"""
		关闭拉动提示
		"""
		self.onHideResizer( pyBoard )

	def onBeginResized_( self, pyBoard ) :
		"""
		开始拉动
		"""
		pyWnd = self.pyWnd
		self.__wndRB = ( pyWnd.right, pyWnd.bottom )
		self.__size = pyWnd.size
		self.__tmpDirect = pyBoard.direct
		self.onBeginResized( pyBoard )

	def onEndResized_( self, pyBoard ) :
		"""
		结束拉动
		"""
		if self.__tmpDirect & INC_DIRECT_L :
			self.pyWnd.right = self.__wndRB[0]
		if self.__tmpDirect & INC_DIRECT_T :
			self.pyWnd.bottom = self.__wndRB[1]
		self.__tmpDirect = 0
		self.onEndResized( pyBoard )

	def onResizing_( self, pyBoard, dx, dy ) :
		"""
		正在拉动
		"""
		fnName = self.__cc_resizers[pyBoard.direct]
		getattr( self, fnName )( dx, dy )
		self.onResizing( pyBoard, dx, dy )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setWidthRange( self, rng ) :
		"""
		设置宽度范围( 如果最大宽度为负数，则表示没有最大宽度)
		"""
		minWidth, maxWidth = rng
		minWidth = max( 0, minWidth )
		if minWidth > maxWidth > 0 :
			maxWidth, minWidth = rng
		self.__minWidth, self.__maxWidth = minWidth, maxWidth
		pyWnd = self.pyWnd
		if pyWnd.width < minWidth :
			pyWnd.width = minWidth
		elif pyWnd.width > maxWidth > 0 :
			pyWnd.width = maxWidth

	def setHeightRange( self, rng ) :
		"""
		设置高度范围( 如果最大高度为负数，则表示没有最大高度)
		"""
		minHeight, maxHeight = rng
		minHeight = max( 0, minHeight )
		if minHeight > maxHeight > 0 :
			maxHeight, minHeight = rng
		self.__minHeight, self.__maxHeight = minHeight, maxHeight
		pyWnd = self.pyWnd
		if pyWnd.height < minHeight :
			pyWnd.height = minHeight
		elif pyWnd.height > maxHeight > 0 :
			pyWnd.height = maxHeight

	def isMouseHit( self ) :
		for pyBoard in self.pyBoards_.itervalues() :
			if pyBoard.isMouseHit() :
				return True
		return False


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getAutoResize( self ) :
		return self.__autoReisize

	def _setAutoResize( self, autoReisize ) :
		self.__autoReisize = autoReisize


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyWnd = property( lambda self : self.__pyWnd() )					# 绑定的相关窗口
	pyBoards = property( lambda self : self.pyBoards_.values() )		# 所有拖边
	autoReisize = property( _getAutoResize, _setAutoResize )			# 是否自动改变大小
	isResizing = property( lambda self : self.__tmpDirect > 0 )			# 是否处于改变大小中

	minWidth = property( lambda self : self.__minWidth )				# 窗口的最小宽度（大于 0）
	maxWidth = property( lambda self : self.__maxWidth )				# 窗口的最大宽度（如果为负数，则表示没有最大宽度）
	minHeight = property( lambda self : self.__minHeight )				# 窗口的最小高度（大于 0）
	maxHeight = property( lambda self : self.__maxHeight )				# 窗口的最大高度（如果为负数，则表示没有最大高度）



# --------------------------------------------------------------------
# implement board class
# --------------------------------------------------------------------
class Board( Control ) :
	__cc_cursors = {								# 鼠标指针
		INC_DIRECT_L  : "sizeWE",
		INC_DIRECT_R  : "sizeWE",
		INC_DIRECT_T  : "sizeNS",
		INC_DIRECT_B  : "sizeNS",
		INC_DIRECT_LT : "sizeNWSE",
		INC_DIRECT_RT : "sizeNESW",
		INC_DIRECT_LB : "sizeNESW",
		INC_DIRECT_RB : "sizeNWSE",
		}

	__cc_dock_styles = {							# 停靠方式
		INC_DIRECT_L  : ( "LEFT", "VFILL" ),
		INC_DIRECT_R  : ( "RIGHT","VFILL" ),
		INC_DIRECT_T  : ( "HFILL","TOP" ),
		INC_DIRECT_B  : ( "HFILL", "BOTTOM" ),
		INC_DIRECT_LT : ( "LEFT", "TOP" ),
		INC_DIRECT_RT : ( "RIGHT", "TOP" ),
		INC_DIRECT_LB : ( "LEFT", "BOTTOM" ),
		INC_DIRECT_RB : ( "RIGHT", "BOTTOM" ),
		}
	def __init__( self, direct, board, pyBinder ) :
		Control.__init__( self, board, pyBinder )
		self.h_dockStyle = self.__cc_dock_styles[direct][0]
		self.v_dockStyle = self.__cc_dock_styles[direct][1]
		self.focus = True
		self.moveFocus = True
		self.crossFocus = True

		self.__direct = direct
		self.__startPos = None

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseEnter_( self ) :
		rds.ccursor.lock( self.__cc_cursors[self.__direct] )
		self.pyBinder.onShowResizer_( self )

	def onMouseLeave_( self ) :
		if self.__startPos : return
		rds.ccursor.unlock( self.__cc_cursors[self.__direct], "normal" )
		self.pyBinder.onHideResizer_( self )

	def onLMouseDown_( self, mods ) :
		rds.uiHandlerMgr.capUI( self )
		self.__startPos = csol.pcursorPosition()
		self.pyBinder.onBeginResized_( self )
		return True

	def onLMouseUp_( self, mods ) :
		rds.ccursor.unlock( self.__cc_cursors[self.__direct], "normal" )
		rds.ccursor.normal()
		self.__startPos = None
		rds.uiHandlerMgr.uncapUI( self )
		self.pyBinder.onEndResized_( self )
		return True

	def onMouseMove_( self, dx, dy ) :
		if not self.__startPos : return False
		sx, sy = self.__startPos
		cx, cy = csol.pcursorPosition()
		dx, dy = ( cx - sx, cy - sy )
		self.pyBinder.onResizing_( self, dx, dy )
		return True


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getDirect( self ) :
		return self.__direct


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	direct = property( _getDirect )
