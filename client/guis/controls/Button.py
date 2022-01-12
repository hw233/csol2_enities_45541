# -*- coding: gb18030 -*-
#
# $Id: Button.py,v 1.33 2008-08-01 09:47:33 huangyongwei Exp $

"""
implement button class。
-- 2005/04/18 : writen by huangyongwei
"""
"""
composing :
	GUI.XXX

or
	GUI.Window
		-- lbText：GUI.Text( 可以没有 )
"""

from guis import *
from Control import Control
from StaticText import StaticText

class Button( Control ) :
	"""
	按钮
	"""
	def __init__( self, button = None, pyBinder = None ) :
		Control.__init__( self, button, pyBinder )
		self.pyText_ = None								# 按钮上的文本标签（可没有）
		self.__initialize( button )						# 初始化
		self.__isOffsetText = True						# bool：当鼠标按下时是否文本向下偏移一个像素
		self.__state = UIState.COMMON					# 按钮当前状态
		self.__effDisable = True						# 灰色状态时，是否将按钮的渲染方式改为“COLOUR_EFF”

	def subclass( self, button, pyBinder = None ) :
		Control.subclass( self, button, pyBinder )
		self.__initialize( button )
		return self

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_Button :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, button ) :
		if button is None : return
		self.focus = True
		self.crossFocus = True

		self.mappings_ = {}										# 状态 mapping
		self.mappings_[UIState.COMMON] = self.mapping			# 普通状态
		self.mappings_[UIState.HIGHLIGHT] = self.mapping		# 高亮状态
		self.mappings_[UIState.PRESSED] = self.mapping			# 鼠标按下状态
		self.mappings_[UIState.DISABLE] = self.mapping			# 无效状态

		foreColor = ( 0, 0, 0, 0 )
		if hasattr( button, "lbText" ) :
			self.pyText_ = StaticText( button.lbText )
			foreColor = self.pyText_.color
			self.__textPos = self.pyText_.pos					# 临时记录文本的正常位置（给鼠标提起时恢复文本位置）
		self.foreColors_ = {}									# 状态前景色
		self.foreColors_[UIState.COMMON] = foreColor			# 普通状态
		self.foreColors_[UIState.HIGHLIGHT] = foreColor			# 高亮状态
		self.foreColors_[UIState.PRESSED] = foreColor			# 鼠标按下状态
		self.foreColors_[UIState.DISABLE] = foreColor			# 无效状态
		backColor = 255, 255, 255, 255
		self.backColors_ = {}									# 状态背景色
		self.backColors_[UIState.COMMON] = backColor			# 普通状态
		self.backColors_[UIState.HIGHLIGHT] = backColor			# 高亮状态
		self.backColors_[UIState.PRESSED] = backColor			# 鼠标按下状态
		self.backColors_[UIState.DISABLE] = backColor			# 无效状态


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def setDisableView_( self ) :
		"""
		设置无效模式下的表现
		"""
		if self.__effDisable :
			self.mapping = self.mappings_[UIState.COMMON]
			self.backColor = self.backColors_[UIState.COMMON]
			self.materialFX = "COLOUR_EFF"
			if self.pyText_ :
				self.foreColor = self.foreColors_[UIState.COMMON]
				self.pyText_.materialFX = "COLOUR_EFF"
		else :
			self.materialFX = "BLEND"
			self.mapping = self.mappings_[UIState.DISABLE]
			self.backColor = self.backColors_[UIState.DISABLE]
			if self.pyText_ :
				self.pyText_.materialFX = "BLEND"
				self.foreColor = self.foreColors_[UIState.DISABLE]

	def setStateView_( self, state ) :
		"""
		设置指定状态下的外观表现
		"""
		if state == UIState.DISABLE :
			self.setDisableView_()
			return
		self.materialFX = "BLEND"
		self.mapping = self.mappings_[state]
		self.color = self.backColors_[state]
		if not self.pyText_ : return
		self.pyText_.materialFX = "BLEND"
		self.pyText_.color = self.foreColors_[state]
		if not self.__isOffsetText : return
		if state == UIState.PRESSED :
			self.pyText_.left = self.__textPos[0] + 1
			self.pyText_.top = self.__textPos[1] + 1
		else :
			self.pyText_.pos = self.__textPos

	# -------------------------------------------------
	def onLMouseDown_( self, mods ) :
		isMouseHit = self.isMouseHit()
		if isMouseHit :
			uiHandlerMgr.capUI( self )
			self.setState( UIState.PRESSED )
		Control.onLMouseDown_( self, mods )
		return isMouseHit

	def onLMouseUp_( self, mods ) :
		uiHandlerMgr.uncapUI( self )
		isMouseHit = self.isMouseHit()
		if not self.enable :
			self.setState( UIState.DISABLE )
		elif isMouseHit :
			self.setState( UIState.HIGHLIGHT )
		else :
			self.setState( UIState.COMMON )
		Control.onLMouseUp_( self, mods )
		return isMouseHit

	# ---------------------------------------
	def onLClick_( self, mods ) :
		if self.isMouseHit() :
			Control.onLClick_( self, mods )
		return True

	# ---------------------------------------
	def onMouseEnter_( self ) :
		Control.onMouseEnter_( self )
		if uiHandlerMgr.getCapUI() == self :
			self.setState( UIState.PRESSED )
		elif self.enable :
			self.setState( UIState.HIGHLIGHT )
		return True

	def onMouseLeave_( self ) :
		Control.onMouseLeave_( self )
		if self.enable :
			self.setState( UIState.COMMON )
		return True

	# ---------------------------------------
	def onEnable_( self ) :
		Control.onEnable_( self )
		self.setState( UIState.COMMON )

	def onDisable_( self ) :
		Control.onDisable_( self )
		self.setState( UIState.DISABLE )

	# -------------------------------------------------
	def onStateChanged_( self, state ) :
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setStatesMapping( self, stMode ) :
		"""
		设置状态 mapping
		@type					stMode : MACRO DEFINATION / tuple
		@param					stMode : 标示几行几列（将各个状态贴图放到同一张图片上）: ( 行数，列数)
									   : 也可以在 guis.uidefine.py 的 UIState 中选择：MODE_XXX
		"""
		row, col = stMode
		count = row * col
		if count <= 0 : return
		comMapping = util.getStateMapping( self.size, stMode, UIState.ST_R1C1 )
		self.mappings_[UIState.COMMON] = comMapping
		self.mappings_[UIState.HIGHLIGHT] = comMapping
		self.mappings_[UIState.PRESSED] = comMapping
		self.mappings_[UIState.DISABLE] = comMapping
		if count > 1 :
			state = ( 1 / col + 1, 1 % col + 1 )
			self.mappings_[UIState.HIGHLIGHT] = util.getStateMapping( self.size, stMode, state )
		if count > 2 :
			state = ( 2 / col + 1, 2 % col + 1 )
			self.mappings_[UIState.PRESSED] = util.getStateMapping( self.size, stMode, state )
		if count > 3 :
			state = ( 3 / col + 1, 3 % col + 1 )
			self.mappings_[UIState.DISABLE] = util.getStateMapping( self.size, stMode, state )
		if self.enable :
			self.setState( UIState.COMMON )

	def setState( self, state ) :
		"""
		设置按钮状态
		"""
		self.__state = state
		self.setStateView_( state )
		self.onStateChanged_( state )

	def resetSetate( self ) :
		"""
		重新设置为默认状态
		"""
		if self.__state != UIState.DISABLE :
			self.setState( UIState.COMMON )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getState( self ) :
		return self.__state

	def _getEffDisable( self ) :
		return self.__effDisable

	def _setEffDisable( self, effDisable ) :
		self.__effDisable = effDisable
		if not self.enable :
			self.setDisableView_()

	# ---------------------------------------
	def _getCommonMapping( self ) :
		return self.mappings_[UIState.COMMON]

	def _setCommonMapping( self, mapping ) :
		self.mapping = mapping
		self.mappings_[UIState.COMMON] = mapping

	# ---------------------------------------
	def _getHighlightMapping( self ) :
		return self.mappings_[UIState.HIGHLIGHT]

	def _setHighlightMapping( self, mapping ) :
		self.mappings_[UIState.HIGHLIGHT] = mapping

	# ---------------------------------------
	def _getPressedMapping( self ) :
		return self.mappings_[UIState.PRESSED]

	def _setPressedMapping( self, mapping ) :
		self.mappings_[UIState.PRESSED] = mapping

	# ---------------------------------------
	def _getDisableMapping( self ) :
		return self.mappings_[UIState.DISABLE]

	def _setDisableMapping( self, mapping ) :
		return											# 通过改变 materialFX 来实现变灰
		self.mappings_[UIState.DISABLE] = mapping
		if not self.enable :
			self.setState( UIState.DISABLE )

	# ---------------------------------------
	def _getCommonForeColor( self ) :
		return self.foreColors_[UIState.COMMON]

	def _setCommonForeColor( self, color ) :
		self.pyText_.color = color
		self.foreColors_[UIState.COMMON] = color

	def _getHighlightForeColor( self ) :
		return self.foreColors_[UIState.HIGHLIGHT]

	def _setHighlightForeColor( self, color ) :
		self.foreColors_[UIState.HIGHLIGHT] = color

	def _getPressedForeColor( self ) :
		return self.foreColors_[UIState.PRESSED]

	def _setPressedForeColor( self, color ) :
		self.foreColors_[UIState.PRESSED] = color

	def _getDisableForeColor( self ) :
		return self.foreColors_[UIState.DISABLE]

	def _setDisableForeColor( self, color ) :
		return											# 通过改变 materialFX 来实现变灰
		self.foreColors_[UIState.DISABLE] = color
		if not self.enable :
			self.setStateView_( UIState.DISABLE )

	# ---------------------------------------
	def _getCommonBackColor( self ) :
		return self.backColors_[UIState.COMMON]

	def _setCommonBackColor( self, color ) :
		self.color = color
		self.backColors_[UIState.COMMON] = color

	def _getHighlightBackColor( self ) :
		return self.backColors_[UIState.HIGHLIGHT]

	def _setHighlightBackColor( self, color ) :
		self.backColors_[UIState.HIGHLIGHT] = color

	def _getPressedBackColor( self ) :
		return self.backColors_[UIState.PRESSED]

	def _setPressedBackColor( self, color ) :
		self.backColors_[UIState.PRESSED] = color

	def _getDisableBackColor( self ) :
		return self.backColors_[UIState.DISABLE]

	def _setDisableBackColor( self, color ) :
		return													# 通过改变 materialFX 来实现变灰
		self.backColors_[UIState.DISABLE] = color
		if not self.enable :
			self.setStateView_( UIState.DISABLE )

	# ---------------------------------------
	def _getIsOffsetText( self ) :
		return self.__isOffsetText

	def _setIsOffsetText( self, value ) :
		self.__isOffsetText = value

	# -------------------------------------------------
	def _getText( self ) :
		if self.pyText_ :
			return self.pyText_.text
		return ""

	def _setText( self, text ) :
		if isDebuged :
			assert self.pyText_ is not None, "this button doesn't contain a text label! you can't set its 'text' property!"
		self.pyText_.text = text
		x, y = self.pyText_.pos
		self.__textPos = x, y
		if self.__isOffsetText and self.__state == UIState.PRESSED :
			self.__textPos = x - 1, y - 1

	# -------------------------------------------------
	def _getFont( self ) :
		if self.pyText_ :
			return self.pyText_.font
		return ""

	def _setFont( self, font ) :
		if self.pyText_ :
			self.pyText_.font = font
		self.__textPos = self.pyText_.pos
		
	#------------------------------------------
	def _getFontSize( self ) :
		if self.pyText_ :
			return self.pyText_.fontSize
		return ""

	def _setFontSize( self, fontSize ) :
		if self.pyText_ :
			self.pyText_.fontSize = fontSize
			self.__textPos = self.pyText_.pos
			
	# ---------------------------------------
	def _getForeColor( self ) :
		if self.pyText_ :
			return self.pyText_.color
		return ( 0, 0, 0, 0 )

	def _setForeColor( self, color ) :
		if self.pyText_ :
			self.pyText_.color = color
		self.commonForeColor = color

	# -------------------------------------------------
	def _setCharSpace( self, space ) :
		self.pyText_._setCharSpace( space )
		self.__textPos = self.pyText_.pos

	def _setLimning( self, style ) :
		self.pyText_._setLimning( style )

	def _setLimnColor( self, color ) :
		self.pyText_._setLimnColor( color )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	state = property( _getState )													# 获取按钮的当前状态
	effDisable = property( _getEffDisable, _setEffDisable )							# 获取/设置灰色状态时，是否采用 COLOUR_EFF 渲染
	commonMapping = property( _getCommonMapping, _setCommonMapping )				# 获取/设置普通状态下的贴图 mapping
	highlightMapping = property( _getHighlightMapping, _setHighlightMapping )		# 获取/设置高亮状态下的贴图 mapping
	pressedMapping = property( _getPressedMapping, _setPressedMapping )				# 获取/设置按下状态下的贴图 mapping
	disableMapping = property( _getDisableMapping, _setDisableMapping )				# 获取/设置无效状态下的贴图 mapping
	commonForeColor = property( _getCommonForeColor, _setCommonForeColor )			# 获取/设置普通状态下的前景色
	highlightForeColor = property( _getHighlightForeColor, _setHighlightForeColor )	# 获取/设置高亮状态下的前景色
	pressedForeColor = property( _getPressedForeColor, _setPressedForeColor )		# 获取/设置按下状态下的前景色
	disableForeColor = property( _getDisableForeColor, _setDisableForeColor )		# 获取/设置无效状态下的前景色
	commonBackColor = property( _getCommonBackColor, _setCommonBackColor )			# 获取/设置普通状态下的背景色
	highlightBackColor = property( _getHighlightBackColor, _setHighlightBackColor )	# 获取/设置高亮状态下的背景色
	pressedBackColor = property( _getPressedBackColor, _setPressedBackColor )		# 获取/设置按下状态下的背景色
	disableBackColor = property( _getDisableBackColor, _setDisableBackColor )		# 获取/设置无效状态下的背景色

	text = property( _getText, _setText )											# 获取/设置按钮文本（必须要有 lbText 才有效）
	font = property( _getFont, _setFont )											# 获取/设置文本字体（必须要有 lbText 才有效）
	fontSize = property( _getFontSize, _setFontSize ) 								# 获取/设置文本字体（ 必须要有lbtext 才有效）
	foreColor = property( _getForeColor, _setForeColor )							# 获取/设置文本前景色（必须要有 lbText 才有效）
	charSpace = property( lambda self : self.pyText_.charSpace, _setCharSpace )		# 获取/设置字间距
	limning = property( lambda self : self.pyText_.limning, _setLimning )			# 获取/设置描边样式
	limnColor = property( lambda self : self.pyText_.limnColor, _setLimnColor )		# 获取/设置描边颜色
	isOffsetText = property( _getIsOffsetText, _setIsOffsetText ) 					# 鼠标按下时，是否将文本向右下角偏移一个像素
