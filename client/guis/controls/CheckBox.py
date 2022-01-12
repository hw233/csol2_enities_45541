# -*- coding: gb18030 -*-
#
# $Id: CheckBox.py,v 1.19 2008-06-27 03:15:11 huangyongwei Exp $

"""
implement checkbox class

2006.04.28 : writen by huangyongwei
"""


from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from guis.controls.StaticText import StaticText


# --------------------------------------------------------------------
# implement checkbox class
# --------------------------------------------------------------------
"""
composing :
	GUI.Window
		-- checker ( GUI.Simple )
"""
class CheckBox( Control ) :
	"""
	不带文本的复选框
	"""
	def __init__( self, box = None, pyBinder = None ) :
		Control.__init__( self, box, pyBinder )
		self.__initialize( box )
		self.__clickCheck = True

	def subclass( self, box, pyBinder = None ) :
		Control.subclass( self, box, pyBinder )
		self.__initialize( box )
		return self

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_CheckBox :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, box ) :
		if box is None : return
		self.focus = True
		self.checker_ = box.checker


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
			self.checked = not self.checked
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

	def _setChecked( self, value ) :
		if bool( self.checked ) != bool( value ) :
			self.checker_.visible = value
			self.onCheckChanged( value )

	# -------------------------------------------------
	def _getClickCheck( self ) :
		return self.__clickCheck

	def _setClickCheck( self, clickCheck ) :
		self.__clickCheck = clickCheck


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	checked = property( _getChecked, _setChecked )						# 获取/设置选中状态
	clickCheck = property( _getClickCheck, _setClickCheck )				# 获取/设置点击时，是否选中


# --------------------------------------------------------------------
# implement checkbox class
# --------------------------------------------------------------------
"""
composing :
	GUI.TextureFrame:
		elements :
			box: GUI.Texture
			checker: GUI.Texture
		children :
			stext: GUI.Text ( 可选 )
"""
class CheckBoxEx( Control ) :
	"""
	不带文本的复选框
	"""
	def __init__( self, box = None, pyBinder = None ) :
		Control.__init__( self, box, pyBinder )
		self.focus = True
		checker = box.elements["checker"]
		checker.visible = False
		self.pyText_ = None
		if hasattr( box, "stext" ) :
			self.pyText_ = StaticText( box.stext )
		if self.pyText_:
			if checker.position.x < self.pyText_.left :
				self.__isRightBox = False				# 文本在选框的右边
			else :
				self.__isRightBox = True				# 文本在选框的左边
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
			self.checked = not self.checked
		return True

	def onCheckChanged_( self, checked ) :
		"""
		选中改变时被调用
		"""
		self.onCheckChanged( checked )


	# -------------------------------------------------
	def onEnable_( self ) :
		Control.onEnable_( self )
		if self.pyText_:
			self.pyText_.materialFX = "BLEND"

	def onDisable_( self ) :
		Control.onDisable_( self )
		if self.pyText_:
			self.pyText_.materialFX = "COLOUR_EFF"


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setFont( self, font ) :
		self.pyText_._setFont( font )

	def _setForeColor( self, color ) :
		self.pyText_.color = color

	# -------------------------------------------------
	def _getChecked( self ) :
		return self.txelems["checker"].visible

	def _setChecked( self, checked ) :
		if self.checked == checked :
			return
		self.txelems["checker"].visible = checked
		self.onCheckChanged_( checked )

	def _getText( self ) :
		return getattr( self.pyText_, "text", "" )

	def _setText( self, text ) :
		if self.pyText_ is None :
			return
		if not self.__isRightBox : 					# 选框在左边
			self.pyText_.text = text
			right = self.pyText_.right
			if right > self.width :
				self.width = right
		else :										# 选框在右边
			ck = self.gui.elements["checker"]
			box = self.gui.elements["box"]
			txtRight = self.pyText_.right
			ckSpace = ck.position.x - txtRight
			boxSpace = box.position.x - txtRight
			self.pyText_.text = text
			self.pyText_.right = ck.position.x - ckSpace
			if self.pyText_.left < 0 :
				self.pyText_.left = 0
				txtRight = self.pyText_.right
				ck.position.x = txtRight + ckSpace
				box.position.x = txtRight + boxSpace
				right = self.right
				self.width = max( s_util.getFElemRight( box ), s_util.getFElemRight( ck ) ) + 1
				self.right = right


	# -------------------------------------------------
	def _setCharSpace( self, space ) :
		self.pyText_._setCharSpace( space )

	def _setLimning( self, style ) :
		self.pyText_._setLimning( style )

	def _setLimnColor( self, color ) :
		self.pyText_._setLimnColor( color )

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
	checked = property( _getChecked, _setChecked)
	text = property( _getText, _setText )
	charSpace = property( lambda self : self.__charSpace, _setCharSpace )			# 获取/设置字间距
	charSpace = property( lambda self : self.pyText_.charSpace, _setCharSpace )		# 获取/设置字间距
	limning = property( lambda self : self.pyText_.limning, _setLimning )			# 获取/设置描边样式
	limnColor = property( lambda self : self.pyText_.limnColor, _setLimnColor )		# 获取/设置描边颜色
	clickCheck = property( _getClickCheck, _setClickCheck )
