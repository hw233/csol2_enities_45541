# -*- coding: gb18030 -*-
#
# $Id: RadioButton.py,v 1.7 2008-06-21 01:46:45 huangyongwei Exp $

"""
implement checkbox class

2007/6/24: writen by huangyongwei
"""
"""
composing :
	GUI.Window
		-- checker ( GUI.Simple )
"""

from guis import *
from guis.controls.Control import Control
from guis.controls.StaticText import StaticText

class RadioButton( Control ) :
	def __init__( self, btn, pyBinder = None ) :
		Control.__init__( self, btn, pyBinder )
		self.__initialize( btn )

	def subclass( self, btn, pyBinder = None ) :
		Control.subclass( self, btn, pyBinder )
		self.__initialize( btn )

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_RadioButton :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, btn ) :
		if btn is None : return
		self.focus = True
		self.checker_ = btn.checker
		self.checker_.visible = False


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		Control.generateEvents_( self )
		self.__onCheckChanged = self.createEvent_( "onCheckChanged" )

	@property
	def onCheckChanged( self ) :
		return self.__onCheckChanged


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLClick_( self, mods ) :
		Control.onLClick_( self, mods )
		if self.checked : return True
		self.checked = True
		return True

	# -------------------------------------------------
	def onEnable_( self ) :
		Control.onEnable_( self )
		self.checker_.materialFX = "BLEND"

	def onDisable_( self ) :
		Control.onDisable_( self )
		self.checker_.materialFX = "COLOUR_EFF"


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getChecked( self ) :
		return self.checker_.visible

	def _setChecked( self, checked ) :
		if self.checked == checked : return
		self.checker_.visible = checked
		self.onCheckChanged( self.checked )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	checked = property( _getChecked, _setChecked )						# 获取/设置是否有效


# --------------------------------------------------------------------
# implement checkbox class
# --------------------------------------------------------------------
"""
composing :
	GUI.TextureFrame:
		elements :
			btn: GUI.Texture
			selector: GUI.Texture
		children :
			stext: GUI.Text ( 可选 )
"""
class RadioButtonEx( Control ) :
	"""
	不带文本的复选框
	"""
	def __init__( self, rb = None, pyBinder = None ) :
		Control.__init__( self, rb, pyBinder )
		self.focus = True
		selector = rb.elements["selector"]
		selector.visible = False
		self.pyText_ = None
		if hasattr( rb, "stext" ) :
			self.pyText_ = StaticText( rb.stext )
		if self.pyText_:
			if selector.position.x < self.pyText_.left :
				self.__isRightBtn = False				# 文本在选框的右边
			else :
				self.__isRightBtn = True				# 文本在选框的左边
		self.__clickCheck = True					# 是否在鼠标点击的时候自动选中


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		Control.generateEvents_( self )
		self.__onCheckChanged = self.createEvent_( "onCheckChanged" )		# 当选中状态改变时被触发

	@property
	def onCheckChanged( self ) :
		"""
		当选中状态改变时被触发
		"""
		return self.__onCheckChanged

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLClick_( self, mods ) :
		Control.onLClick_( self, mods )
		if self.__clickCheck :
			self.checked = True
		return True

	def onCheckChanged_( self, checked ) :
		"""
		选中改变时被调用
		"""
		self.onCheckChanged( checked )


	# -------------------------------------------------
	def onEnable_( self ) :
		Control.onEnable_( self )
		self.pyText_.materialFX = "BLEND"

	def onDisable_( self ) :
		Control.onDisable_( self )
		self.pyText_.materialFX = "COLOUR_EFF"


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setFont( self, font ) :
		self.pyText_._setFont( font )

	def _setForeColor( self, color ) :
		self.pyText_.color = color

	# -------------------------------------------------
	def _setCharSpace( self, space ) :
		self.pyText_._setCharSpace( space )

	def _setLimning( self, style ) :
		self.pyText_._setLimning( style )

	def _setLimnColor( self, color ) :
		self.pyText_._setLimnColor( color )

	# -------------------------------------------------
	def _getChecked( self ) :
		return self.txelems["selector"].visible

	def _setChecked( self, checked ) :
		if self.checked == checked :
			return
		self.txelems["selector"].visible = checked
		self.onCheckChanged_( checked )

	def _getText( self ) :
		return getattr( self.pyText_, "text", "" )

	def _setText( self, text ) :
		if self.pyText_ is None :
			return
		if not self.__isRightBtn : 					# 选框在左边
			self.pyText_.text = text
			right = self.pyText_.right
			if right > self.width :
				self.width = right
		else :										# 选框在右边
			ck = self.gui.elements["selector"]
			btn = self.gui.elements["btn"]
			txtRight = self.pyText_.right
			ckSpace = ck.position.x - txtRight
			boxSpace = btn.position.x - txtRight
			self.pyText_.text = text
			self.pyText_.right = ck.position.x - ckSpace
			if self.pyText_.left < 0 :
				self.pyText_.left = 0
				txtRight = self.pyText_.right
				ck.position.x = txtRight + ckSpace
				btn.position.x = txtRight + boxSpace
				right = self.right
				self.width = max( s_util.getFElemRight( btn ), s_util.getFElemRight( ck ) ) + 1
				self.right = right

	# -------------------------------------------------
	def _getClickCheck( self ) :
		return self.__clickCheck

	def _setClickCheck( self, clickCheck ) :
		self.__clickCheck = clickCheck


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	font = property( lambda self : self.pyText_.font, _setFont )
	foreColor = property( lambda self : self.pyText_.color, _setForeColor )
	charSpace = property( lambda self : self.pyText_.charSpace, _setCharSpace )		# 获取/设置字间距
	limning = property( lambda self : self.pyText_.limning, _setLimning )			# 获取/设置描边样式
	limnColor = property( lambda self : self.pyText_.limnColor, _setLimnColor )		# 获取/设置描边颜色
	checked = property( _getChecked, _setChecked)
	text = property( _getText, _setText )
	isRightBtn = property( lambda self : self.__isRightBtn )
	clickCheck = property( _getClickCheck, _setClickCheck )
