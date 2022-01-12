# -*- coding: gb18030 -*-
#
# $Id: ScrollPanel.py,v 1.20 2008-08-21 09:07:02 huangyongwei Exp $

"""
imlement scroll panel( base class )
this panel is including a clippanel and a scrollbar

2005.06.17: writen by huangyongwei
2008.11.13: modified by huangyongwei
"""

from guis import *
from ClipPanel import HVClipPanel
from ClipPanel import HClipPanel
from ClipPanel import VClipPanel
from ScrollBar import HScrollBar
from ScrollBar import VScrollBar

# --------------------------------------------------------------------
# implement horizontal & vertical scroll panel
# --------------------------------------------------------------------
"""
composing :
	GUI.Window
	hBar ( gui of csui.controls.ScrollBar.HScrollBar )
	vBar ( gui of csui.controls.ScrollBar.VScrollBar )
"""

class HVScrollPanel( HVClipPanel ) :
	"""
	双滚动条版面
	"""
	def __init__( self, panel, hBar, vBar, pyBinder = None ) :
		HVClipPanel.__init__( self, panel, pyBinder )
		self.__hSBState = ScrollBarST.AUTO								# 默认一直显示水平滚动条
		self.__vSBState = ScrollBarST.AUTO								# 默认一直显示垂直滚动条
		self.__initialize( panel, hBar, vBar )

		self.__skipScroll = True										# 是否随意跳跃式滚动
		self.__hPerScroll = 60.0										# 在水平方向上鼠标滚轮每滚动一下版面的滚动宽度
		self.__vPerScroll = 60.0										# 在水平方向上鼠标滚轮每滚动一下版面的滚动高度


	def subclass( self, panel, hBar, vBar, pyBinder = None ) :
		HVClipPanel.subclass( self, panel, pyBinder )
		self.__initialize( panel, hBar, vBar )

	def __del__( self ) :
		if Debug.output_del_ScrollPanel :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, panel, hBar, vBar ) :
		if panel is None : return
		self.mouseScrollFocus = True									# 允许鼠标滚轮事件
		self.canTabIn = True											# 设置为能获得焦点
		self.pyHSBar = HScrollBar( hBar )
		self.pyHSBar.onScroll.bind( self.onHScroll_ )
		self.pyVSBar = VScrollBar( vBar )
		self.pyVSBar.onScroll.bind( self.onVScroll_ )
		self.__updateScrollState()


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		HVClipPanel.generateEvents_( self )
		self.__onHScrollChanged = self.createEvent_( "onScrollHChanged" )
		self.__onVScrollChanged = self.createEvent_( "onScrollVChanged" )

	@property
	def onHScrollChanged( self ) :
		"""
		水平滚动条滚动时被触发
		"""
		return self.__onHScrollChanged

	@property
	def onVScrollChanged( self ) :
		"""
		垂直滚动条滚动时被触发
		"""
		return self.__onVScrollChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __updateHPerScroll( self ) :
		"""
		更新水平滚动条单位滚动值
		"""
		self.pyHSBar.scrollScale = self.h_wholeLen / self.width
		perScroll = 0
		if self.h_maxScroll > 0 :
			perScroll = self.__hPerScroll / self.h_maxScroll
		self.pyHSBar.perScroll = perScroll

	def __updateVPerScroll( self ) :
		"""
		更新垂直滚动条单位滚动值
		"""
		self.pyVSBar.scrollScale = self.v_wholeLen / self.height
		perScroll = 0
		if self.v_maxScroll > 0 :
			perScroll = self.__vPerScroll / self.v_maxScroll
		self.pyVSBar.perScroll = perScroll
		
	def __updateScrollState( self ):
		"""
		初始化滚动条可见性
		"""
		if self.__hSBState == ScrollBarST.SHOW :
			self.pyVSBar.visible = True
		elif self.__hSBState == ScrollBarST.HIDE :
			self.pyVSBar.visible = False
		elif self.__hSBState == ScrollBarST.AUTO :
			self.pyVSBar.visible = False
		if self.__vSBState == ScrollBarST.SHOW :
			self.pyVSBar.visible = True
		elif self.__vSBState == ScrollBarST.HIDE :
			self.pyVSBar.visible = False
		elif self.__vSBState == ScrollBarST.AUTO :
			self.pyVSBar.visible = False


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onHScroll_( self, value ) :
		"""
		水平滚动条滚动时被触发
		"""
		h_maxScroll = self.h_maxScroll
		scroll = value * h_maxScroll
		if self.__skipScroll :
			count = round( scroll / self.__hPerScroll )
			scroll = count * self.__hPerScroll
		oldScroll = self.scroll
		HVClipPanel._setHScroll( self, scroll )
		self.onHScrollChanged( oldScroll )

	def onVScroll_( self, value ) :
		"""
		垂直滚动条滚动时被触发
		"""
		v_maxScroll = self.v_maxScroll
		scroll = value * v_maxScroll
		if self.__skipScroll and value < 1.0 :
			count = round( scroll / self.__vPerScroll )
			scroll = count * self.__vPerScroll
		oldScroll = self.scroll
		HVClipPanel._setVScroll( self, scroll )
		self.onVScrollChanged( oldScroll )

	# -------------------------------------------------
	def onMouseScroll_( self, dz ) :
		"""
		当鼠标滚轮滚动时被调用
		"""
		if BigWorld.isKeyDown( keys.KEY_LCONTROL ) :
			if dz > 0 : self.pyHSBar.decScroll()
			else : self.pyHSBar.incScroll()
		else :
			if dz > 0 : self.pyVSBar.decScroll()
			else : self.pyVSBar.incScroll()
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def resume( self ) :
		"""
		同时恢复两个滚动条的滚动位置为 0
		"""
		self.pyHSBar.value = 0
		self.pyVSBar.value = 0
		self.maxScroll = 0


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setMaxScroll( self, scroll ) :
		self._setHMaxScroll( scroll[0] )
		self._setVMaxScroll( scroll[1] )

	def _setHMaxScroll( self, hScroll ) :
		currScroll = self.h_scroll
		hScroll = max( hScroll, 0 )
		HVClipPanel._setHMaxScroll( self, hScroll )
		self.__updateHPerScroll()
		self._setHScroll( currScroll )							# 保持原来的滚动位置
		if self.__hSBState == ScrollBarST.AUTO :
			visible = hScroll - self.__hPerScroll / 10.0 > 0
			self.pyHSBar.visible = visible

	def _setVMaxScroll( self, vScroll ) :
		currScroll = self.v_scroll
		vScroll = max( vScroll, 0 )
		HVClipPanel._setVMaxScroll( self, vScroll )
		self.__updateVPerScroll()
		self._setVScroll( currScroll )							# 保持原来的滚动位置
		if self.__vSBState == ScrollBarST.AUTO :
			visible = vScroll - self.__vPerScroll / 10.0 > 0
			self.pyVSBar.visible = visible

	# ---------------------------------------
	def _setScroll( self, scroll ) :
		self._setHScroll( scroll[0] )
		self._setVScroll( scroll[1] )

	def _setHScroll( self, hScroll ) :
		hScroll = min( self.h_maxScroll, max( hScroll, 0 ) )
		if self.h_maxScroll > 0 :
			self.pyHSBar.value = hScroll / self.h_maxScroll
		else :
			self.pyHSBar.value = 0

	def _setVScroll( self, vScroll ) :
		vScroll = min( self.v_maxScroll, max( vScroll, 0 ) )
		if self.v_maxScroll > 0 :
			self.pyVSBar.value = vScroll / self.v_maxScroll
		else :
			self.pyVSBar.value = 0

	# -------------------------------------------------
	def _getHWholeLen( self ) :
		return self.h_maxScroll + self.width

	def _setHWholeLen( self, wlen ) :
		wlen = max( 0, wlen )
		self.h_maxScroll = wlen - self.width

	def _getVWholeLen( self ) :
		return self.v_maxScroll + self.height

	def _setVWholeLen( self, wlen ) :
		wlen = max( 0, wlen )
		self.v_maxScroll = wlen - self.height

	# -------------------------------------------------
	def _getSkipScroll( self ) :
		return self.__skipScroll

	def _setSkipScroll( self, skipScroll ) :
		self.__skipScroll = skipScroll

	# -------------------------------------------------
	def _getHPerScroll( self ) :
		return self.__hPerScroll

	def _setHPerScroll( self, hScroll ) :
		width = max( 1.0, hScroll )
		self.__hPerScroll = hScroll
		self.__updateHPerScroll()

	# ---------------------------------------
	def _getVPerScroll( self ) :
		return self.__vPerScroll

	def _setVPerScroll( self, vScroll ) :
		vScroll = max( 1.0, vScroll )
		self.__vPerScroll = vScroll
		self.__updateVPerScroll()

	# -------------------------------------------------
	def _getHSBarState( self ) :
		return self.__hSBState

	def _setHSBarState( self, state ) :
		self.__hSBState = state
		if state == ScrollBarST.SHOW :
			self.pyHSBar.visible = True
		elif state == ScrollBarST.HIDE :
			self.pyHSBar.visible = False
		elif state == ScrollBarST.AUTO :
			self.pyHSBar.visible = False

	# ---------------------------------------
	def _getVSBarState( self ) :
		return self.__vSBState

	def _setVSBarState( self, state ) :
		self.__vSBState = state
		if state == ScrollBarST.SHOW :
			self.pyVSBar.visible = True
		elif state == ScrollBarST.HIDE :
			self.pyVSBar.visible = False
		elif state == ScrollBarST.AUTO :
			self.pyVSBar.visible = False


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	maxScroll = property( HVClipPanel._getMaxScroll, _setMaxScroll )			# tuple: 水平/垂直最大滚动长度
	h_maxScroll = property( HVClipPanel._getHMaxScroll, _setHMaxScroll )		# float: 水平最大滚动宽度
	v_maxScroll = property( HVClipPanel._getVMaxScroll, _setVMaxScroll )		# float: 垂直最大滚动高度
	scroll = property( HVClipPanel._getScroll, _setScroll )						# tuple: 当前水平/垂直滚动长度
	h_scroll = property( HVClipPanel._getHScroll, _setHScroll )					# float: 当前水平滚动宽度
	v_scroll = property( HVClipPanel._getVScroll, _setVScroll )					# float: 当前垂直滚动高度

	h_wholeLen = property( _getHWholeLen, _setHWholeLen )						# float: 水平方向上内容的总宽度
	v_wholeLen = property( _getVWholeLen, _setVWholeLen )						# float: 垂直方向上内容的总高度

	skipScroll = property( _getSkipScroll, _setSkipScroll )						# bool: 是否跳跃式滚动
	h_perScroll = property( _getHPerScroll, _setHPerScroll )					# flaot: 水平方向上单位滚动值
	v_perScroll = property( _getVPerScroll, _setVPerScroll )					# float: 垂直方向上单位滚动值

	h_sbBarState = property( _getHSBarState, _setHSBarState )					# defined: uidefine.ScrollBarST.SHOW, ScrollBarST.SHOW, ScrollBarST.HIDE
	v_sbarState = property( _getVSBarState, _setVSBarState )					# defined: uidefine.ScrollBarST.SHOW, ScrollBarST.SHOW, ScrollBarST.HIDE



# --------------------------------------------------------------------
# implement horizontal scroll panel
# --------------------------------------------------------------------
"""
composing :
	GUI.Window
	sbar ( gui of csui.controls.ScrollBar.HScrollBar )
"""

class HScrollPanel( HClipPanel ) :
	"""
	双滚动条版面
	"""
	def __init__( self, panel, sbar, pyBinder = None ) :
		HClipPanel.__init__( self, panel, pyBinder )
		self.__sbarState = ScrollBarST.AUTO								# 默认一直显示滚动条
		self.__initialize( panel, sbar )

		self.__skipScroll = True										# 是否随意跳跃式滚动
		self.__perScroll = 1.0											# 鼠标滚轮每滚动一下版面的滚动宽度
	

	def subclass( self, panel, sbar, pyBinder = None ) :
		HClipPanel.subclass( self, panel, pyBinder )
		self.__initialize( panel, sbar )

	def __del__( self ) :
		if Debug.output_del_ScrollPanel :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, panel, sbar ) :
		if panel is None : return
		self.mouseScrollFocus = True									# 允许鼠标滚轮事件
		self.canTabIn = True											# 设置为能获得焦点
		self.pySBar = HScrollBar( sbar )
		self.pySBar.onScroll.bind( self.onScroll_ )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		HClipPanel.generateEvents_( self )
		self.__onScrollChanged = self.createEvent_( "onScrollChanged" )

	@property
	def onScrollChanged( self ) :
		"""
		滚动条滚动时被触发
		"""
		return self.__onScrollChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __updatePerScroll( self ) :
		"""
		更新滚动条单位滚动值
		"""
		self.pySBar.scrollScale = self.wholeLen / self.width
		perScroll = 0
		if self.maxScroll > 0 :
			perScroll = self.__perScroll / self.maxScroll
		self.pySBar.perScroll = perScroll
		
	def __updateScrollState( self ):
		"""
		初始化滚动条可见性
		"""
		if self.__sbarState == ScrollBarST.SHOW :
			self.pySBar.visible = True
		elif self.__sbarState == ScrollBarST.HIDE :
			self.pySBar.visible = False
		elif self.__sbarState == ScrollBarST.AUTO :
			self.pySBar.visible = False


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onScroll_( self, value ) :
		"""
		滚动条滚动时被触发
		"""
		maxScroll = self.maxScroll
		scroll = value * maxScroll
		if self.__skipScroll :
			count = round( scroll / self.__perScroll )
			scroll = count * self.__perScroll
		oldScroll = self.scroll
		HClipPanel._setScroll( self, scroll )
		self.onScrollChanged( oldScroll )

	# -------------------------------------------------
	def onMouseScroll_( self, dz ) :
		"""
		当鼠标滚轮滚动时被调用
		"""
		if dz > 0 : self.pySBar.decScroll()
		else : self.pySBar.incScroll()
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def resume( self ) :
		"""
		同时恢复两个滚动条的滚动位置为 0
		"""
		self.pySBar.value = 0
		self.pySBar.maxScroll = 0


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setMaxScroll( self, scroll ) :
		currScroll = self.scroll
		scroll = max( scroll, 0 )
		HClipPanel._setMaxScroll( self, scroll )
		self.__updatePerScroll()
		self._setScroll( currScroll )
		if self.__sbarState == ScrollBarST.AUTO :
			visible = scroll - self.__perScroll / 10.0 > 0
			self.pySBar.visible = visible

	# ---------------------------------------
	def _setScroll( self, scroll ) :
		scroll = min( self.maxScroll, max( scroll, 0 ) )
		if self.maxScroll > 0 :
			self.pySBar.value = scroll / self.maxScroll
		else :
			self.pySBar.value = 0

	# -------------------------------------------------
	def _getWholeLen( self ) :
		return self.maxScroll + self.width

	def _setWholeLen( self, wlen ) :
		wlen = max( 0, wlen )
		self.maxScroll = wlen - self.width

	# -------------------------------------------------
	def _getSkipScroll( self ) :
		return self.__skipScroll

	def _setSkipScroll( self, skipScroll ) :
		self.__skipScroll = skipScroll

	# -------------------------------------------------
	def _getPerScroll( self ) :
		return self.__perScroll

	def _setPerScroll( self, scroll ) :
		width = max( 1.0, scroll )
		self.__perScroll = scroll
		self.__updatePerScroll()

	# -------------------------------------------------
	def _getSBarState( self ) :
		return self.__sbarState

	def _setSBarState( self, state ) :
		self.__sbarState = state
		if state == ScrollBarST.SHOW :
			self.pySBar.visible = True
		elif state == ScrollBarST.HIDE :
			self.pySBar.visible = False
		elif state == ScrollBarST.AUTO :
			self.pySBar.visible = False


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	maxScroll = property( HClipPanel._getMaxScroll, _setMaxScroll )			# float: 最大滚动宽度
	scroll = property( HClipPanel._getScroll, _setScroll )					# tuple: 当前滚动长度
	wholeLen = property( _getWholeLen, _setWholeLen )						# float: 方向上内容的总宽度

	skipScroll = property( _getSkipScroll, _setSkipScroll )					# bool: 是否跳跃式滚动
	perScroll = property( _getPerScroll, _setPerScroll )					# flaot: 方向上单位滚动值

	sbarState = property( _getSBarState, _setSBarState )					# defined: uidefine.ScrollBarST.SHOW, ScrollBarST.SHOW, ScrollBarST.HIDE



# --------------------------------------------------------------------
# implement vertical scroll panel
# --------------------------------------------------------------------
"""
composing :
	GUI.Window
	sbar ( gui of csui.controls.ScrollBar.VScrollBar )
"""

class VScrollPanel( VClipPanel ) :
	"""
	滚动条版面
	"""
	def __init__( self, panel, sbar, pyBinder = None ) :
		VClipPanel.__init__( self, panel, pyBinder )
		self.__sbarState = ScrollBarST.AUTO								# 默认自动显示滚动条
		self.__initialize( panel, sbar )

		self.__skipScroll = True										# 是否随意跳跃式滚动
		self.__perScroll = 1.0											# 鼠标滚轮每滚动一下版面的滚动高度
		

	def subclass( self, panel, sbar, pyBinder = None ) :
		VClipPanel.subclass( self, panel, pyBinder )
		self.__initialize( panel, sbar )

	def __del__( self ) :
		if Debug.output_del_ScrollPanel :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, panel, sbar ) :
		if panel is None : return
		self.mouseScrollFocus = True									# 允许鼠标滚轮事件
		self.canTabIn = True											# 设置为能获得焦点
		self.pySBar = VScrollBar( sbar )
		self.__updateScrollState()
		self.pySBar.onScroll.bind( self.onScroll_ )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		VClipPanel.generateEvents_( self )
		self.__onScrollChanged = self.createEvent_( "onScrollChanged" )

	@property
	def onScrollChanged( self ) :
		"""
		滚动条滚动时被触发
		"""
		return self.__onScrollChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __updatePerScroll( self ) :
		"""
		更新滚动条单位滚动值
		"""
		self.pySBar.scrollScale = self.wholeLen / self.height
		perScroll = 0
		if self.maxScroll > 0 :
			perScroll = self.__perScroll / self.maxScroll
		self.pySBar.perScroll = perScroll
		
	def __updateScrollState( self ):
		"""
		初始化滚动条可见性
		"""
		if self.__sbarState == ScrollBarST.SHOW :
			self.pySBar.visible = True
		elif self.__sbarState == ScrollBarST.HIDE :
			self.pySBar.visible = False
		elif self.__sbarState == ScrollBarST.AUTO :
			self.pySBar.visible = False


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onScroll_( self, value ) :
		"""
		滚动条滚动时被触发
		"""
		maxScroll = self.maxScroll
		scroll = value * maxScroll
		if self.__skipScroll and value < 1.0 :
			count = round( scroll / self.__perScroll )
			scroll = count * self.__perScroll
		oldScroll = self.scroll
		VClipPanel._setScroll( self, scroll )
		self.onScrollChanged( oldScroll )

	# -------------------------------------------------
	def onMouseScroll_( self, dz ) :
		"""
		当鼠标滚轮滚动时被调用
		"""
		if dz > 0 : self.pySBar.decScroll()
		else : self.pySBar.incScroll()
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def resume( self ) :
		"""
		同时恢复两个滚动条的滚动位置为 0
		"""
		self.pySBar.value = 0
		self.maxScroll = 0

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setMaxScroll( self, scroll ) :
		currScroll = self.scroll
		scroll = max( scroll, 0 )
		VClipPanel._setMaxScroll( self, scroll )
		self.__updatePerScroll()
		self._setScroll( currScroll )
		if self.__sbarState == ScrollBarST.AUTO :
			visible = scroll - self.__perScroll / 10.0 > 0
			self.pySBar.visible = visible

	def _setScroll( self, scroll ) :
		scroll = min( self.maxScroll, max( scroll, 0 ) )
		if self.maxScroll > 0 :
			self.pySBar.value = scroll / self.maxScroll
		else :
			self.pySBar.value = 0

	# -------------------------------------------------
	def _getWholeLen( self ) :
		return self.maxScroll + self.height

	def _setWholeLen( self, wlen ) :
		wlen = max( 0, wlen )
		self.maxScroll = wlen - self.height

	# -------------------------------------------------
	def _getSkipScroll( self ) :
		return self.__skipScroll

	def _setSkipScroll( self, skipScroll ) :
		self.__skipScroll = skipScroll

	# -------------------------------------------------
	def _getPerScroll( self ) :
		return self.__perScroll

	def _setPerScroll( self, scroll ) :
		scroll = max( 1.0, scroll )
		self.__perScroll = scroll
		self.__updatePerScroll()

	# -------------------------------------------------
	def _getSBarState( self ) :
		return self.__sbarState

	def _setSBarState( self, state ) :
		self.__sbarState = state
		if state == ScrollBarST.SHOW :
			self.pySBar.visible = True
		elif state == ScrollBarST.HIDE :
			self.pySBar.visible = False
		elif state == ScrollBarST.AUTO :
			self.pySBar.visible = False


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	maxScroll = property( VClipPanel._getMaxScroll, _setMaxScroll )			# tuple: 最大滚动长度
	scroll = property( VClipPanel._getScroll, _setScroll )					# tuple: 当前滚动长度
	wholeLen = property( _getWholeLen, _setWholeLen )						# float: 方向上内容的总宽度

	skipScroll = property( _getSkipScroll, _setSkipScroll )					# bool: 是否跳跃式滚动
	perScroll = property( _getPerScroll, _setPerScroll )					# float: 方向上单位滚动值

	sbarState = property( _getSBarState, _setSBarState )					# defined: uidefine.ScrollBarST.SHOW, ScrollBarST.SHOW, ScrollBarST.HIDE
