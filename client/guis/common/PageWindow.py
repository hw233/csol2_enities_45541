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
		self.__pageCount = 0				# ���ҳ��������� -1 ���ʾû���ҳ��
		self.__pageIndex = -1				# ��ǰ����ҳ��

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
		if count < 0 :									# ������ҳ
			if index == 0 :
				self.pyBtnBackward_.enable = False		# ������һҳ
		elif count  == 0 :								# ��ҳ��û��ҳ��
			self.pyBtnBackward_.enable = False
			self.pyBtnForward_.enable = False
		else :
			if index == 0 :
				self.pyBtnBackward_.enable = False		# ������һҳ
			if index == count - 1 :
				self.pyBtnForward_.enable = False		# ������һҳ

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
		ҳ��ı�ʱ������
		"""
		INFO_MSG( "current page index: %i" % index )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setPageCount( self, count ) :
		self.__pageCount = count
		if count == 0 :										# ��ҳ��û���κ�ҳ��
			self.pageIndex = -1
		else :												# �ж�������޸�ҳʱ
			if self.__pageIndex < 0 :
				self.pageIndex = 0							# ����Ĭ��ҳΪ 0
			elif self.__pageIndex >= count :				# ��ǰҳ����������Χ�Ļ�
				self.pageIndex = count - 1					# ����Ϊ���ҳ��
			else :											# ����Ҫ����ҳ��ʱ
				self.__setJumpBtnState()

	def _setPageIndex( self, index ) :
		oldIndex = self.__pageIndex
		pgCount = self.__pageCount
		if pgCount < 0 :									# û�����ҳ��
			self.__pageIndex = max( 0, index )
		elif pgCount == 0 :									# û���κ�ҳ
			self.__pageIndex = -1
		else :
			self.__pageIndex = max( min( pgCount - 1, index ), 0 )

		self.__setJumpBtnState()							# ���÷�ҳ��ť��״̬

		if oldIndex != self.__pageIndex :
			self.onPageIndexChanged_( self.__pageIndex )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pageCount = property( lambda self : self.__pageCount, _setPageCount )
	pageIndex = property( lambda self : self.__pageIndex, _setPageIndex )
