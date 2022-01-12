# -*- coding: gb18030 -*-

# implement the StatusItem class
# written by ganjinxing 2010-01-20

from guis import *
from guis.common.FrameEx import HFrameEx
from guis.controls.Control import Control
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem


class StatusItem( Control, HFrameEx ) :

	def __init__( self, item, pyBinder = None ) :
		Control.__init__( self, item, pyBinder )
		HFrameEx.__init__( self, item )
		self.focus = True

		self.__dspBg = item.elements["dspBg"]
		self.__dspbgWidthSpace = item.width - s_util.getFElemWidth( self.__dspBg )

		self.__initialize( item )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, item ) :
		self.pyItem_ = BOItem( item.icon )
		self.pyItem_.focus = False

		self.statusMap_ = {}													# ��ʼ������״̬�µ���ɫ
		self.statusMap_[UIState.COMMON]		= ( 60, 57, 48, 180 )
		self.statusMap_[UIState.HIGHLIGHT] 	= ( 60, 57, 48, 180 )
		self.statusMap_[UIState.SELECTED] 	= ( 88, 56, 16, 255 )
		self.statusMap_[UIState.DISABLE] 	= ( 80, 77, 74, 200 )

		self.state = UIState.COMMON												# Ĭ��״̬Ϊ��ͨ״̬


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def setDisableView_( self ) :
		pass

	def setStateView_( self, state ) :
		if state == UIState.DISABLE :
			self.setDisableView_()
		else :
			for child in util.preFindGui( self.gui ) :
				child.materialFX = "BLEND"
		self.__dspBg.colour = self.statusMap_[ state ]

	def onMouseEnter_( self ) :
		Control.onMouseEnter_( self )
		self.state = UIState.HIGHLIGHT
		return True

	def onMouseLeave_( self ) :
		Control.onMouseLeave_( self )
		self.state = UIState.COMMON
		return True

	def onLMouseDown_( self, mods ) :
		Control.onLMouseDown_( self, mods )
		self.selected = True
		return True


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _setWidth( self, width ) :
		HFrameEx._setWidth( self, width )
		newWidth = self.width - self.__dspbgWidthSpace
		s_util.setFElemWidth( self.__dspBg, newWidth )

	def _getPyItem( self ) :
		return self.pyItem_

	def _getSelected( self ) :
		return self.__state == UIState.SELECTED

	def _setSelected( self, selected ) :
		if not self.enable : return
		if selected :
			self.state = UIState.SELECTED
		else :
			self.state = UIState.COMMON

	def _getState( self ) :
		return self.__state

	def _setState( self, state ) :
		self.__state = state
		self.setStateView_( state )

	def _getCommonColor( self ) :
		return self.statusMap_[UIState.COMMON]

	def _setCommonColor( self, color ) :
		if isDebuged :
			assert len( tuple( color ) ) == 4, \
			"colour must be type of Vector4 or tuple, list with 4 elements."
		self.statusMap_[UIState.COMMON] = tuple( color )

	def _getHighlightColor( self ) :
		return self.statusMap_[UIState.HIGHLIGHT]

	def _setHighlightColor( self, color ) :
		if isDebuged :
			assert len( tuple( color ) ) == 4, \
			"colour must be type of Vector4 or tuple, list with 4 elements."
		self.statusMap_[UIState.HIGHLIGHT] = tuple( color )

	def _getSelectedColor( self ) :
		return self.statusMap_[UIState.SELECTED]

	def _setSelectedColor( self, color ) :
		if isDebuged :
			assert len( tuple( color ) ) == 4, \
			"colour must be type of Vector4 or tuple, list with 4 elements."
		self.statusMap_[UIState.SELECTED] = tuple( color )

	def _getDisableColor( self ) :
		return self.statusMap_[UIState.DISABLE]

	def _setDisableColor( self, color ) :
		if isDebuged :
			assert len( tuple( color ) ) == 4, \
			"colour must be type of Vector4 or tuple, list with 4 elements."
		self.statusMap_[UIState.DISABLE] = tuple( color )


	pyItem = property( _getPyItem )											# ��ȡ��ʾͼƬ�Ľű�UI
	width = property( HFrameEx._getWidth, _setWidth )						# ��ȡ/���ÿ��
	selected = property( _getSelected, _setSelected )						# ��ȡ/����ѡ��״̬
	state = property( _getState, _setState )								# ��ȡ/���õ�ǰ��״̬
	commonColor = property( _getCommonColor, _setCommonColor )				# ��ȡ/��������״̬�µ���ɫ
	highlightColor = property( _getHighlightColor, _setHighlightColor )		# ��ȡ/���ø���״̬�µ���ɫ
	selectedColor = property( _getSelectedColor, _setSelectedColor )		# ��ȡ/����ѡ��״̬�µ���ɫ
	disableColor = property( _getDisableColor, _setDisableColor )			# ��ȡ/������Ч״̬�µ���ɫ
