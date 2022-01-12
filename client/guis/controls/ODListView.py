# -*- coding: gb18030 -*-
#

"""
implement listview class
2009/11/26 : writen by huangyongwei
"""

import copy
from guis import *
from Control import Control
from StaticText import StaticText
from ODListPanel import ODListPanel
from ODPagesPanel import ODPagesPanel

# --------------------------------------------------------------------
# ��ͷ
# --------------------------------------------------------------------
"""
GUI.TextureFrame:
	elements:
							t: GUI.Texture
		l: GUI.Texture		orderSign:GUI.Texture		r: GUI.Texture
							b: GUI.Texture
	children:
		sText
"""
class Header( Control ) :
	def __init__( self, index, header, pyBinder ) :
		Control.__init__( self, header, pyBinder )
		self.crossFocus = True
		self.focus = True
		self.pyText_ = StaticText( header.sText )						# ͷ�ı�
		header.elements['l'].visible = False
		header.elements['r'].visible = False
		header.elements['t'].visible = False
		header.elements['b'].visible = False
		header.elements['orderSign'].visible = False

		self.__ordinal = False											# ˳���
		self.__highlightColor = tuple( header.elements['l'].colour )	# ����״̬ʱ���߿���ɫ
		self.__textTop = self.pyText_.top
		self.__orderSignTop = header.elements['orderSign'].position.y
		self.__orderSignMapping = header.elements['orderSign'].mapping

		self.__index = index											# ��ͷ����

		self.__layout()

	def __del__( self ) :
		if Debug.output_del_ODListView :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __layout( self ) :
		if self.actived :
			orderSign = self.gui.elements['orderSign']
			width = self.pyText_.width + orderSign.size.x + 2
			self.pyText_.left = ( self.width - width ) * 0.5
			self.pyText_.top = self.__textTop
			orderSign.position.x = self.pyText_.right + 2
			orderSign.position.y = self.__orderSignTop
		else :
			self.pyText_.center = self.width * 0.5
			self.pyText_.top = self.__textTop

	# -------------------------------------------------
	def __common( self ) :
		"""
		�޸�Ϊ��ͨ״̬
		"""
		header = self.gui
		header.elements['l'].visible = False
		header.elements['r'].visible = False
		header.elements['t'].visible = False
		header.elements['b'].visible = False
		self.__layout()

	def __highlight( self ) :
		"""
		������ʾ
		"""
		header = self.gui
		l = header.elements['l']
		r = header.elements['r']
		t = header.elements['t']
		b = header.elements['b']
		l.colour = self.__highlightColor
		t.colour = self.__highlightColor
		l.visible = True
		r.visible = True
		t.visible = True
		b.visible = True
		self.__layout()

	def __pressed( self ) :
		"""
		����״̬
		"""
		header = self.gui
		l = header.elements['l']
		r = header.elements['r']
		t = header.elements['t']
		b = header.elements['b']
		l.visible = True
		t.visible = True
		r.visible = False
		b.visible = False
		l.colour = ( 0, 0, 0, 255 )
		t.colour = ( 0, 0, 0, 255 )

		self.__layout()
		self.pyText_.pos += ( 1, 1 )
		self.gui.elements['orderSign'].position += ( 1, 1, 0 )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseEnter_( self ) :
		Control.onMouseEnter_( self )
		if not self.orderable : return True
		if BigWorld.isKeyDown( KEY_LEFTMOUSE ) and \
			rds.uiHandlerMgr.isCapped( self ) :
				self.__pressed()
		else :
			self.__highlight()
		return True

	def onMouseLeave_( self ) :
		Control.onMouseEnter_( self )
		if not self.orderable : return True
		self.__common()
		return True

	def onLMouseDown_( self, mods ) :
		Control.onLMouseDown_( self, mods )
		if not self.orderable : return True
		self.__pressed()
		rds.uiHandlerMgr.capUI( self )
		return True

	def onLMouseUp_( self, mods ) :
		Control.onLMouseUp_( self, mods )
		if not self.orderable : return True
		uiHandlerMgr.uncapUI( self )
		if self.isMouseHit() :
			self.__highlight()
		else :
			self.__common()
		return True

	def onLClick_( self, mods ) :
		Control.onLClick_( self, mods )
		if self.actived :
			self.sort( not self.__ordinal )
		else :
			self.sort( True )
		return True

	# -------------------------------------------------
	def cancelSort_( self ) :
		"""
		ȡ������״̬
		"""
		header = self.gui
		header.elements['orderSign'].visible = False
		header.elements['l'].visible = False
		header.elements['r'].visible = False
		header.elements['t'].visible = False
		header.elements['b'].visible = False
		self.__layout()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def sort( self, ordinal = True ) :
		"""
		����
		@type			reverse : bool
		@param			reverse : �Ƿ��ǰ�˳���
		"""
		if not self.orderable : return
		header = self.gui
		orderSign = header.elements['orderSign']
		orderSign.visible = True
		self.__ordinal = ordinal
		if ordinal :
			orderSign.mapping = self.__orderSignMapping
		else :
			orderSign.mapping = util.vflipMapping( self.__orderSignMapping )
		self.__layout()

		self.pyBinder.onHeadOrdered_( self, ordinal )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setText( self, text ) :
		self.pyText_.text = text
		self.__layout()

	def _setFont( self, font ) :
		self.pyText_.font = font
		self.__textTop = self.pyText_.top

	def _setForeColor( self, color ) :
		self.pyText_.color = color

	# ---------------------------------------
	def _getOrderable( self ) :
		if self.pyBinder is None : return False
		return self.pyBinder.orderable


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	index = property( lambda self : self.__index )									# ��ͷ����
	text = property( lambda self : self.pyText_.text, _setText )					# ��ͷ�ı�
	font = property( lambda self : self.pyText_.font, _setFont )					# ��ͷ����
	foreColor = property( lambda self : self.pyText_.color, _setForeColor )			# ��ͷ��ɫ
	orderable = property( _getOrderable )											# �Ƿ������
	actived = property( lambda self : self.gui.elements['orderSign'].visible )		# �Ƿ��ڼ���״̬


# --------------------------------------------------------------------
# ʽ�б���ͼ����
# --------------------------------------------------------------------
class View( object ) :
	def __init__( self, view ) :
		self.__background = view
		self.pyHeaders_ = []						# ���б�ͷ
		self.__pyActiveHeader = None
		self.__orderable = False					# �Ƿ������

	def __del__( self ) :
		if Debug.output_del_ODListView :
			INFO_MSG( str( self ) )

	def dispose( self ) :
		self.__background = None


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		self.__onHeadOrdered = self.createEvent_( "onHeadOrdered" )

	@property
	def onHeadOrdered( self ) :
		return self.__onHeadOrdered


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onHeadOrdered_( self, pyHeader, ordinal ) :
		"""
		��ĳ��ͷ����
		"""
		if self.__pyActiveHeader and \
			self.__pyActiveHeader != pyHeader :
				self.__pyActiveHeader.cancelSort_()
		self.__pyActiveHeader = pyHeader
		self.onHeadOrdered( pyHeader, ordinal )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def autoSearchHeaders( self ) :
		"""
		�Զ�������ͷ
		"""
		self.clearHeaders()
		for name, ch in self.__background.children :
			if "head_" not in name : continue
			index = int( name[5:] )
			self.pyHeaders_.append( Header( index, ch, self ) )

	# -------------------------------------------------
	def getHeader( self, index ) :
		"""
		��ȡָ�������ı�ͷ
		"""
		return self.pyHeaders_[index]

	# -------------------------------------------------
	def addHeader( self, pyHeader ) :
		"""
		���һ����ͷ
		"""
		if pyHeader not in self.pyHeaders_ :
			self.pyHeaders_.append( pyHeader )
			self.addPyChild( pyHeader )

	def removeHeader( self, pyHeader ) :
		"""
		ɾ��һ����ͷ
		"""
		if pyHeader in self.pyHeaders_ :
			self.pyHeader_.remove( pyHeader )
			self.delPyChild( pyHeader )

	def clearHeaders( self ) :
		"""
		������б�ͷ
		"""
		for pyHeader in self.pyHeaders_ :
			self.delPyChild( pyHeader )
		self.pyHeaders_ = []


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setOrderable( self, orderable ) :
		self.__orderable = orderable
		if not orderable and self.__pyActiveHeader :
			self.__pyActiveHeader.cancelSort_()
			self.__pyActiveHeader = None


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyHeaders = property( lambda self : self.pyHeaders_[:] )
	orderable = property( lambda self : self.__orderable, _setOrderable )			# �Ƿ������


# --------------------------------------------------------------------
# ����ʽ�б���ͼ
# --------------------------------------------------------------------
"""
GUI.TextureFrame:
	elements:
								header: GUI.Texture
		frm_lt: GUI.Texture		frm_t : GUI.Texture		frm_rt: GUI.Texture
		frm_l : GUI.Texture		frm_bg: GUI.Texture		frm_r : GUI.Texture
		frm_lb: GUI.Texture		frm_b : GUI.Texture		frm_rb: GUI.Texture
								splitter: GUI.Texture
	children:
		sbar: VScrollBar
		head_0: Header
		head_1: Header
		head_2: Header
		...
"""
class ODListView( View, ODListPanel ) :
	def __init__( self, view, pyBinder = None ) :
		View.__init__( self, view )
		ODListPanel.__init__( self, view.clipPanel, view.sbar, pyBinder )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		View.generateEvents_( self )
		ODListPanel.generateEvents_( self )


# --------------------------------------------------------------------
# ��ҳʽ�б���ͼ
# --------------------------------------------------------------------
"""
GUI.TextureFrame :
	elements:
								header: GUI.Texture
		frm_lt: GUI.Texture		frm_t : GUI.Texture		frm_rt: GUI.Texture
		frm_l : GUI.Texture		frm_bg: GUI.Texture		frm_r : GUI.Texture
		frm_lb: GUI.Texture		frm_b : GUI.Texture		frm_rb: GUI.Texture
								splitter: GUI.Texture
								bgIndex : GUI.Texture
	children:
		btnDec: GUI.Simple		stIndex: GUI.Text		btnInc: GUI.Simple
		head_0: Header
		head_1: Header
		head_2: Header
		...
"""
class ODPagesView( View, ODPagesPanel ) :
	def __init__( self, view, pyBinder = None ) :
		View.__init__( self, view )
		ODPagesPanel.__init__( self, view.clipPanel, view.ctrlBar, pyBinder )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		View.generateEvents_( self )
		ODPagesPanel.generateEvents_( self )
