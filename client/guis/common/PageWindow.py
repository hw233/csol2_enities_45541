# -*- coding: gb18030 -*-
#
# $Id: Window.py,v 1.17 2008-08-26 02:12:34 huangyongwei Exp $

"""
implement standard window
2009/11/23 : writen by huangyongwei
"""


from guis import *
from Window import Window
from guis.controls.Button import Button

"""
composing :
	GUI.TextureFrame
		elements :
						frm_decoder
			frm_lt		frm_t			frm_rt
			frm_l		frm_bg			frm_r
			frm_lb		frm_b			frm_rb
		children :
			lbTitle  [optional gui]( GUI.Text )-> label for show window title
			closeBtn [optional gui]( GUI.XXX  )-> close button
"""
class PageWindow( Window ) :
	def __init__( self, wnd = None ) :
		Window.__init__( self, wnd )
		self.__initialize( wnd )
		self.__pageCount = 0				# 最大页数，如果是 -1 则标示没最大页数
		self.__pageIndex = -1				# 当前所在页码

	def subclass( self, wnd ) :
		Window.subclass( self, wnd )
		self.__initialize( wnd )

	def __del__( self ) :
		Window.__del__( self )
		if Debug.output_del_PageWindow :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		if wnd is None : return
		self.pyBtnBackward_ = Button( wnd.btnBackward )
		self.pyBtnBackward_.setStatesMapping( UIState.MODE_R2C2 )
		self.pyBtnBackward_.onLClick.bind( self.__onBackwardClick )
		self.pyBtnForward_ = Button( wnd.btnForward )
		self.pyBtnForward_.setStatesMapping( UIState.MODE_R2C2 )
		self.pyBtnForward_.onLClick.bind( self.__onForwardClick )
		self.pyBtnBackward_.enable = False
		self.pyBtnForward_.enable = False

	# -------------------------------------------------
	def __setJumpBtnState( self ) :
		self.pyBtnBackward_.enable = True
		self.pyBtnForward_.enable = True
		count = self.__pageCount
		index = self.__pageIndex
		if count < 0 :									# 有无限页
			if index == 0 :
				self.pyBtnBackward_.enable = False		# 不许上一页
		elif count  == 0 :								# 空页（没有页）
			self.pyBtnBackward_.enable = False
			self.pyBtnForward_.enable = False
		else :
			if index == 0 :
				self.pyBtnBackward_.enable = False		# 不许上一页
			if index == count - 1 :
				self.pyBtnForward_.enable = False		# 不许下一页

	# -------------------------------------------------
	def __onBackwardClick( self ) :
		self.pageIndex -= 1

	def __onForwardClick( self ) :
		self.pageIndex += 1


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onPageIndexChanged_( self, index ) :
		"""
		页面改变时被触发
		"""
		INFO_MSG( "current page index: %i" % index )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setPageCount( self, count ) :
		self.__pageCount = count
		if count == 0 :										# 空页（没有任何页）
			self.pageIndex = -1
		else :												# 有多个或无限个页时
			if self.__pageIndex < 0 :
				self.pageIndex = 0							# 设置默认页为 0
			elif self.__pageIndex >= count :				# 当前页索引超出范围的话
				self.pageIndex = count - 1					# 设置为最大页码
			else :											# 不需要设置页码时
				self.__setJumpBtnState()

	def _setPageIndex( self, index ) :
		oldIndex = self.__pageIndex
		pgCount = self.__pageCount
		if pgCount < 0 :									# 没有最大页数
			self.__pageIndex = max( 0, index )
		elif pgCount == 0 :									# 没有任何页
			self.__pageIndex = -1
		else :
			self.__pageIndex = max( min( pgCount - 1, index ), 0 )

		self.__setJumpBtnState()							# 设置翻页按钮的状态

		if oldIndex != self.__pageIndex :
			self.onPageIndexChanged_( self.__pageIndex )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pageCount = property( lambda self : self.__pageCount, _setPageCount )
	pageIndex = property( lambda self : self.__pageIndex, _setPageIndex )
