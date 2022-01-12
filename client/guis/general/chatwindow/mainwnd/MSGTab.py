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
	__cc_max_width				= 80			# ��ť�����
	__cc_com_width				= 56			# ���ʿ�ȣ����������֣�
	__cc_text_space				= 4				# �ı���ǩ����С���

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

		self.__allowDrag = False					# �Ƿ������϶�
		self.__dragging = False						# �Ƿ����϶�״̬��
		self.__delayDragCBID = 0					# ��ʱ�ϷŲ����� callback ID


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseDown_( self, mods ) :
		TabButton.onLMouseDown_( self, mods )
		toolbox.infoTip.hide( self )

		def delayDrag() :
			if self.isMouseHit() :
				self.__allowDrag = True							# �����Ϸ�״̬
		BigWorld.cancelCallback( self.__delayDragCBID )
		if not self.pyTabPage.docked :
			delayDrag()
		elif not self.pyTabPage.locked :
			self.__delayDragCBID = BigWorld.callback( 0.1, delayDrag )	# ��ʱһ������Ϊ�ϷŴ���������Ŀ���Ƿ�ֹ����������ʱ����С�����Ի���һ�����ͻ��ҳ���ϳ�ȥ

		return True

	def onLMouseUp_( self, mods ) :
		TabButton.onLMouseUp_( self, mods )

		BigWorld.cancelCallback( self.__delayDragCBID )
		if self.__allowDrag :
			self.__allowDrag = False							# �����Ϸű��
		if self.__dragging :
			self.__dragging = False								# ȡ���Ϸ�״̬
			self.pyTabPage.onStopDrag_()						# ֹͣ�϶�
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
		����ƶ�ʱ������
		"""
		TabButton.onMouseMove_( self, dx, dy )
		if not self.__allowDrag : return True
		if self.__dragging :
			self.pyTabPage.onDragging_()			# �����϶���
		else :
			self.__dragging = True
			self.pyTabPage.onStartDrag_()			# ��ʼ�϶�


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def showDropMarker( self ) :
		"""
		��ʾ���¸���
		"""
		self.__cg_pyDropMarker.width = self.width - 1
		self.addPyChild( self.__cg_pyDropMarker, "m" )

	def hideDropMarker( self ) :
		"""
		���ط��¸���
		"""
		self.delPyChild( self.__cg_pyDropMarker )

	def isDropping( self ) :
		"""
		�Ƿ��ڽ�Ҫ���·�ҳ״̬
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
		if textWidth < comWidth - space and width > comWidth :				# �������ȿ���С��������ȣ����ң�Ԥ���ȴ����������
			self.pyText_.text = self.__text									# ��Ԥ�����ڿ������������ı�
			TabButton._setWidth( self, comWidth )							# ��ˣ����������Ϊ�������
			self.pyText_.center = self.width * 0.5
			return
		if comWidth - space < textWidth <= width - space :					# ����ı���ȴ���
			self.pyText_.text = self.__text
			TabButton._setWidth( self, textWidth + space )
			self.pyText_.center = self.width * 0.5
			return
		text, wtext = self.pyText_.elideText( width, "CUT", self.__text )	# �������������ȡ�����ı�
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


