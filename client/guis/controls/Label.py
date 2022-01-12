# -*- coding: gb18030 -*-
#
# $Id: Label.py,v 1.13 2008-06-30 01:33:23 huangyongwei Exp $

"""
implement label class��
"""

"""
2008/06/27 : writen by huangyongwei
"""

"""
composing :
	GUI.Window
		-- lbText ( GUI.Text )
"""

from guis import *
from Control import Control
from StaticLabel import StaticLabel


class Label( StaticLabel, Control ) :
	"""
	�ı���ǩ�������������¼���
	"""
	def __init__( self, bg = None, pyBinder = None ) :
		if isDebuged :
			assert type( bg ) != GUI.Text, "label's background must be a window. may be you should use StaticText"
		StaticLabel.__init__( self, bg, pyBinder )
		bg = self.getGui()
		Control.__init__( self, bg )
		self.__initialize( bg )

	def subclass( self, bg, pyBinder = None ) :
		StaticLabel.subclass( self, bg, pyBinder )
		Control.subclass( self, bg )
		self.__initialize( bg )
		return self

	def __del__( self ) :
		StaticLabel.__del__( self )
		Control.__del__( self )
		if Debug.output_del_Label :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, bg ) :
		if bg is None : return
		self.focus = True
		self.crossFocus = True
		foreColor = self.foreColor
		backColor = self.backColor
		mapping = self.mapping
		self.foreColors_ = {}
		self.foreColors_[UIState.COMMON] = foreColor
		self.foreColors_[UIState.HIGHLIGHT] = foreColor
		self.foreColors_[UIState.PRESSED] = foreColor
		self.foreColors_[UIState.DISABLE] = foreColor
		self.backColors_ = {}
		self.backColors_[UIState.COMMON] = backColor
		self.backColors_[UIState.HIGHLIGHT] = backColor
		self.backColors_[UIState.PRESSED] = backColor
		self.backColors_[UIState.DISABLE] = backColor
		self.mappings_ = {}
		self.mappings_[UIState.COMMON] = mapping
		self.mappings_[UIState.HIGHLIGHT] = mapping
		self.mappings_[UIState.PRESSED] = mapping
		self.mappings_[UIState.DISABLE] = mapping


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseDown_( self, mods ) :
		Control.onLMouseDown_( self, mods )
		self.setState( UIState.PRESSED )
		return True

	def onLMouseUp_( self, mods ) :
		Control.onLMouseUp_( self, mods )
		if self.isMouseHit() :
			self.setState( UIState.HIGHLIGHT )
		else :
			self.setState( UIState.COMMON )
		return True

	def onMouseEnter_( self ) :
		Control.onMouseEnter_( self )
		self.setState( UIState.HIGHLIGHT )
		return True

	def onMouseLeave_( self ) :
		Control.onMouseLeave_( self )
		self.setState( UIState.COMMON )
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setState( self, state ) :
		"""
		���ñ�ǩ״̬
		"""
		self.foreColor = self.foreColors_[state]
		self.backColor = self.backColors_[state]
		self.mapping = self.mappings_[state]


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getCommonForeColor( self ) :
		return self.foreColors_[UIState.COMMON]

	def _setCommonForeColor( self, color ) :
		self.foreColors_[UIState.COMMON] = color
		self.foreColor = color

	# ---------------------------------------
	def _getHighlightForeColor( self ) :
		return self.foreColors_[UIState.HIGHLIGHT]

	def _setHighlightForeColor( self, color ) :
		self.foreColors_[UIState.HIGHLIGHT] = color

	# ---------------------------------------
	def _getPressedForeColor( self ) :
		return self.foreColors_[UIState.PRESSED]

	def _setPressedForeColor( self, color ) :
		self.foreColors_[UIState.PRESSED] = color

	# ---------------------------------------
	def _getDisableForeColor( self ) :
		return self.foreColors_[UIState.DISABLE]

	def _setDisableForeColor( self, color ) :
		self.foreColors_[UIState.DISABLE] = color

	# -------------------------------------------------
	def _getCommonBackColor( self ) :
		return self.backColors_[UIState.COMMON]

	def _setCommonBackColor( self, color ) :
		self.backColors_[UIState.COMMON] = color
		self.backColor = color

	# ---------------------------------------
	def _getHighlightBackColor( self ) :
		return self.backColors_[UIState.HIGHLIGHT]

	def _setHighlightBackColor( self, color ) :
		self.backColors_[UIState.HIGHLIGHT] = color

	# ---------------------------------------
	def _getPressedBackColor( self ) :
		return self.backColors_[UIState.PRESSED]

	def _setPressedBackColor( self, color ) :
		self.backColors_[UIState.PRESSED] = color

	# ---------------------------------------
	def _getDisableBackColor( self ) :
		return self.backColors_[UIState.DISABLE]

	def _setDisableBackColor( self, color ) :
		self.backColors_[UIState.DISABLE] = color

	# -------------------------------------------------
	def _getCommonMapping( self ) :
		return self.mappings_[UIState.COMMON]

	def _setCommonMapping( self, mapping ) :
		self.mappings_[UIState.COMMON]  = mapping
		self.mapping = mapping

	# ---------------------------------------
	def _getHighlightMapping( self ) :
		return self.mappings_[UIState.HIGHLIGHT]

	def _setHighlightMapping( self, mapping ) :
		self.mappings_[UIState.HIGHLIGHT]  = mapping

	# ---------------------------------------
	def _getPressedMapping( self ) :
		return self.mappings_[UIState.PRESSED]

	def _setPressedMapping( self, mapping ) :
		self.mappings_[UIState.PRESSED]  = mapping

	# ---------------------------------------
	def _getDisableMapping( self ) :
		return self.mappings_[UIState.DISABLE]

	def _setDisableMapping( self, mapping ) :
		self.mappings_[UIState.DISABLE]  = mapping


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	commonForeColor = property( _getCommonForeColor, _setCommonForeColor )			# ��ȡ/������ͨ״̬�µ�ǰ��ɫ
	highlightForeColor = property( _getHighlightForeColor, _setHighlightForeColor )	# ��ȡ/���ø���״̬�µ�ǰ��ɫ
	pressedForeColor = property( _getPressedForeColor, _setPressedForeColor )		# ��ȡ/���ð���״̬�µ�ǰ��ɫ
	disableForeColor = property( _getDisableForeColor, _setDisableForeColor )		# ��ȡ/������Ч״̬�µ�ǰ��ɫ

	commonBackColor = property( _getCommonBackColor, _setCommonBackColor )			# ��ȡ/������ͨ״̬�µı���ɫ
	highlightBackColor = property( _getHighlightBackColor, _setHighlightBackColor )	# ��ȡ/���ø���״̬�µı���ɫ
	pressedBackColor = property( _getPressedBackColor, _setPressedBackColor )		# ��ȡ/���ð���״̬�µı���ɫ
	disableBackColor = property( _getDisableBackColor, _setDisableBackColor )		# ��ȡ/������Ч״̬�µı���ɫ

	commonMapping = property( _getCommonMapping, _setCommonMapping )				# ��ȡ/������ͨ״̬�µ� mapping
	highlightMapping = property( _getHighlightMapping, _setHighlightMapping )		# ��ȡ/���ø���״̬�µ� mapping
	pressedMapping = property( _getPressedMapping, _setPressedMapping )				# ��ȡ/���ð���״̬�µ� mapping
	disableMapping = property( _getDisableMapping, _setDisableMapping )				# ��ȡ/������Ч״̬�µ� mapping
