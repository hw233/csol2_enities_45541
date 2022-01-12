# -*- coding: gb18030 -*-
#
# $Id: MSGPage.py,v 1.10 2008-08-30 09:05:30 huangyongwei Exp $

"""
implement tab button for showing chating message

2009/08/28: writen by huangyongwei
"""

import ResMgr
from guis import *
from guis.common.FrameEx import HFrameEx
from guis.controls.StaticText import StaticText
from guis.controls.TabCtrl import TabButton


class MSGTab( TabButton ) :
	__cc_max_width				= 80			# 按钮最大宽度
	__cc_com_width				= 56			# 合适宽度（放下两个字）
	__cc_text_space				= 4				# 文本标签的最小左距

	__cg_pyDropMarker = None

	def __init__( self, btn ) :
		TabButton.__init__( self, btn )
		self.moveFocus = True
		self.isOffsetText = False
		self.__text = ""

		mapping = ( ( 0, 0 ), ( 0, 1 ), ( 1, 1 ), ( 1, 0 ) )
		self.mappings_[UIState.COMMON] = mapping
		self.mappings_[UIState.HIGHLIGHT] = mapping
		self.mappings_[UIState.PRESSED] = mapping
		self.mappings_[UIState.SELECTED] = mapping
		self.mappings_[UIState.DISABLE] = mapping

		if MSGTab.__cg_pyDropMarker is None :
			mk = GUI.load( "guis/general/chatwindow/mainwnd/msgpanel/dropmarker.gui" )
			MSGTab.__cg_pyDropMarker = HFrameEx( mk )

		self.__allowDrag = False					# 是否允许拖动
		self.__dragging = False						# 是否处于拖动状态中
		self.__delayDragCBID = 0					# 延时拖放操作的 callback ID


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseDown_( self, mods ) :
		TabButton.onLMouseDown_( self, mods )
		toolbox.infoTip.hide( self )

		def delayDrag() :
			if self.isMouseHit() :
				self.__allowDrag = True							# 进入拖放状态
		BigWorld.cancelCallback( self.__delayDragCBID )
		if not self.pyTabPage.docked :
			delayDrag()
		elif not self.pyTabPage.locked :
			self.__delayDragCBID = BigWorld.callback( 0.1, delayDrag )	# 延时一会再作为拖放处理，这样的目的是防止鼠标左键按下时，不小心稍稍滑动一下鼠标就会把页面拖出去

		return True

	def onLMouseUp_( self, mods ) :
		TabButton.onLMouseUp_( self, mods )

		BigWorld.cancelCallback( self.__delayDragCBID )
		if self.__allowDrag :
			self.__allowDrag = False							# 重置拖放标记
		if self.__dragging :
			self.__dragging = False								# 取消拖放状态
			self.pyTabPage.onStopDrag_()						# 停止拖动
		return True

	def onRMouseDown_( self, mods ) :
		TabButton.onRMouseDown_( self, mods )
		toolbox.infoTip.hide( self )
		return True

	# ---------------------------------------
	def onMouseEnter_( self ) :
		TabButton.onMouseEnter_( self )
		if self.__text != self.pyText_.text :
			toolbox.infoTip.showToolTips( self, self.__text )

	def onMouseLeave_( self ) :
		TabButton.onMouseLeave_( self )
		toolbox.infoTip.hide( self )

	# ---------------------------------------
	def onMouseMove_( self, dx, dy ) :
		"""
		鼠标移动时被调用
		"""
		TabButton.onMouseMove_( self, dx, dy )
		if not self.__allowDrag : return True
		if self.__dragging :
			self.pyTabPage.onDragging_()			# 处于拖动中
		else :
			self.__dragging = True
			self.pyTabPage.onStartDrag_()			# 开始拖动


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def showDropMarker( self ) :
		"""
		显示放下高亮
		"""
		self.__cg_pyDropMarker.width = self.width - 1
		self.addPyChild( self.__cg_pyDropMarker, "m" )

	def hideDropMarker( self ) :
		"""
		隐藏放下高亮
		"""
		self.delPyChild( self.__cg_pyDropMarker )

	def isDropping( self ) :
		"""
		是否处于将要放下分页状态
		"""
		return hasattr( self.gui, "m" )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getText( self ) :
		return self.__text

	def _setSelectedBackColor( self, color ) :
		TabButton._setSelectedBackColor( self, color )
		r, g, b, a = color
		commonColor = r, g, b, max( 0, a - 60 )
		self.commonBackColor = commonColor
		self.highlightBackColor = commonColor
		self.pressedBackColor = color
		self.disableBackColor = color

	# -------------------------------------------------
	def _setText( self, text ) :
		self.__text = text
		TabButton._setText( self, text )

	def _setWidth( self, width  ) :
		space = self.__cc_text_space * 2
		width = min( width, self.__cc_max_width )
		textWidth = self.pyText_.textWidth( self.__text )
		comWidth = self.__cc_com_width
		if textWidth < comWidth - space and width > comWidth :				# 如果本宽度可以小于正常宽度，并且，预设宽度大于正常宽度
			self.pyText_.text = self.__text									# 则，预设宽度内可以容下所有文本
			TabButton._setWidth( self, comWidth )							# 因此，将宽度设置为正常宽度
			self.pyText_.center = self.width * 0.5
			return
		if comWidth - space < textWidth <= width - space :					# 如果文本宽度大于
			self.pyText_.text = self.__text
			TabButton._setWidth( self, textWidth + space )
			self.pyText_.center = self.width * 0.5
			return
		text, wtext = self.pyText_.elideText( width, "CUT", self.__text )	# 其余情况，均截取部分文本
		self.pyText_.text = text
		TabButton._setWidth( self, width )
		self.pyText_.center = self.width * 0.5

	def _getFitWidth( self ) :
		width = self.pyText_.textWidth( self.__text ) + self.__cc_text_space * 2
		return min( width, self.__cc_max_width )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( _getText, _setText )
	selectedBackColor = property( TabButton._getSelectedBackColor, _setSelectedBackColor )
	width = property( TabButton._getWidth, _setWidth )
	fitWidth = property( _getFitWidth )


