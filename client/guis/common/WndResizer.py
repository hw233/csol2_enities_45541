# -*- coding: gb18030 -*-
#
# $Id: ChatWindow.py,v 1.60 2008-09-04 01:00:31 huangyongwei Exp $

"""
imlement resize bord for window

2009/04/20: writen by huangyongwei
"""
"""
�̶�����:
	lt			t			  rt
	����������������������������
	��                        ��
	��                        ��
   l��                        ��r
	��                        ��
	��                        ��
	����������������������������
	lb			b			  rb
"""


import weakref
from guis import *
from guis.controls.Control import Control

INC_DIRECT_L		= 1									# ��������
INC_DIRECT_R		= 2									# ��������
INC_DIRECT_T		= 4									# ��������
INC_DIRECT_B		= 8									# ��������
INC_DIRECT_LT		= INC_DIRECT_L | INC_DIRECT_T		# �����Ͻ�����
INC_DIRECT_RT		= INC_DIRECT_R | INC_DIRECT_T		# �����Ͻ�����
INC_DIRECT_LB		= INC_DIRECT_L | INC_DIRECT_B		# �����½�����
INC_DIRECT_RB		= INC_DIRECT_R | INC_DIRECT_B		# �����½�����

class WndResizer( object ) :
	__cc_boards = {							# �������������Ĺ�ϵ
		'l'  : INC_DIRECT_L,
		'r'  : INC_DIRECT_R,
		't'  : INC_DIRECT_T,
		'b'  : INC_DIRECT_B,
		'lt' : INC_DIRECT_LT,
		'rt' : INC_DIRECT_RT,
		'lb' : INC_DIRECT_LB,
		'rb' : INC_DIRECT_RB,
		}

	__cc_resizers = {						# ��С������
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
		@param			pyWnd  : Ҫ����Ĵ���
		@type			boards : dict
		@param			boards : ���ߣ���ѡ����
								 'l'  : GUI.Simple ���
								 'r'  : GUI.Simple �ұ�
								 't'  : GUI.Simple ����
								 'b'  : GUI.Simple �ױ�
								 'lt' : GUI.Simple ���Ͻ�
								 'rt' : GUI.Simple ���Ͻ�
								 'lb' : GUI.Simple ���½�
								 'rb' : GUI.Simple ���½�
		"""
		self.pyBoards_ = {}
		for key, board in boards.iteritems() :
			direct = WndResizer.__cc_boards[key]
			pyBoard = Board( direct, board, self )
			self.pyBoards_[direct] = pyBoard
		self.__events = []									# �¼��б�
		self.generateEvents_()

		self.__pyWnd = weakref.ref( pyWnd )					# �󶨵Ĵ���
		self.__autoReisize = True							# �Ƿ��Զ��ı��С
		self.__wndRB = pyWnd.right, pyWnd.bottom			# ��¼���ڵ����½�λ��
		self.__size = pyWnd.size							# ��ʼ�ı��Сʱ����¼�´��ڴ�С
		self.__tmpDirect = 0								# ��ʼ�ı��Сʱ����¼�¸ı�ķ���

		self.__minWidth = pyWnd.width						# ���ڵ���С���
		self.__maxWidth = pyWnd.width						# ���ڵ������
		self.__minHeight = pyWnd.height						# ���ڵ���С�߶�
		self.__maxHeight = pyWnd.height						# ���ڵ����߶�


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
		self.__onShowResizer = self.createEvent_( "onShowResizer" )		# ��ʾ�ı��ȱ�
		self.__onHideResizer = self.createEvent_( "onHideResizer" )		# ���ظı��ȱ�
		self.__onBeginResized = self.createEvent_( "onBeginResized" )	# ��ʼ�ı���
		self.__onEndResized = self.createEvent_( "onEndResized" )		# �����ı���
		self.__onResizing = self.createEvent_( "onResizing" )			# ���ڸı���

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
		������ߵ���չ��
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
		�����ұߵ���չ��
		"""
		pyWnd = self.pyWnd
		width = self.__size[0] + dx
		width = max( self.__minWidth, width )
		if self.__maxWidth > 0 :
			width = min( self.__maxWidth, width )
		pyWnd.width = width

	def t_resize_( self, dx, dy ) :
		"""
		�����ϱߵ���չ��
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
		�����ױߵ���չ��
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
		�������Ͻǵ���չ��
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
		�������Ͻ���չ��
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
		�������½���չ��
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
		�������½���չ��
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
		��ʾ����
		"""
		self.onShowResizer( pyBoard )

	def onHideResizer_( self, pyBoard ) :
		"""
		�ر�������ʾ
		"""
		self.onHideResizer( pyBoard )

	def onBeginResized_( self, pyBoard ) :
		"""
		��ʼ����
		"""
		pyWnd = self.pyWnd
		self.__wndRB = ( pyWnd.right, pyWnd.bottom )
		self.__size = pyWnd.size
		self.__tmpDirect = pyBoard.direct
		self.onBeginResized( pyBoard )

	def onEndResized_( self, pyBoard ) :
		"""
		��������
		"""
		if self.__tmpDirect & INC_DIRECT_L :
			self.pyWnd.right = self.__wndRB[0]
		if self.__tmpDirect & INC_DIRECT_T :
			self.pyWnd.bottom = self.__wndRB[1]
		self.__tmpDirect = 0
		self.onEndResized( pyBoard )

	def onResizing_( self, pyBoard, dx, dy ) :
		"""
		��������
		"""
		fnName = self.__cc_resizers[pyBoard.direct]
		getattr( self, fnName )( dx, dy )
		self.onResizing( pyBoard, dx, dy )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setWidthRange( self, rng ) :
		"""
		���ÿ�ȷ�Χ( ��������Ϊ���������ʾû�������)
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
		���ø߶ȷ�Χ( ������߶�Ϊ���������ʾû�����߶�)
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
	pyWnd = property( lambda self : self.__pyWnd() )					# �󶨵���ش���
	pyBoards = property( lambda self : self.pyBoards_.values() )		# �����ϱ�
	autoReisize = property( _getAutoResize, _setAutoResize )			# �Ƿ��Զ��ı��С
	isResizing = property( lambda self : self.__tmpDirect > 0 )			# �Ƿ��ڸı��С��

	minWidth = property( lambda self : self.__minWidth )				# ���ڵ���С��ȣ����� 0��
	maxWidth = property( lambda self : self.__maxWidth )				# ���ڵ�����ȣ����Ϊ���������ʾû������ȣ�
	minHeight = property( lambda self : self.__minHeight )				# ���ڵ���С�߶ȣ����� 0��
	maxHeight = property( lambda self : self.__maxHeight )				# ���ڵ����߶ȣ����Ϊ���������ʾû�����߶ȣ�



# --------------------------------------------------------------------
# implement board class
# --------------------------------------------------------------------
class Board( Control ) :
	__cc_cursors = {								# ���ָ��
		INC_DIRECT_L  : "sizeWE",
		INC_DIRECT_R  : "sizeWE",
		INC_DIRECT_T  : "sizeNS",
		INC_DIRECT_B  : "sizeNS",
		INC_DIRECT_LT : "sizeNWSE",
		INC_DIRECT_RT : "sizeNESW",
		INC_DIRECT_LB : "sizeNESW",
		INC_DIRECT_RB : "sizeNWSE",
		}

	__cc_dock_styles = {							# ͣ����ʽ
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
