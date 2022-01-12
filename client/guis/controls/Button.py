# -*- coding: gb18030 -*-
#
# $Id: Button.py,v 1.33 2008-08-01 09:47:33 huangyongwei Exp $

"""
implement button class��
-- 2005/04/18 : writen by huangyongwei
"""
"""
composing :
	GUI.XXX

or
	GUI.Window
		-- lbText��GUI.Text( ����û�� )
"""

from guis import *
from Control import Control
from StaticText import StaticText

class Button( Control ) :
	"""
	��ť
	"""
	def __init__( self, button = None, pyBinder = None ) :
		Control.__init__( self, button, pyBinder )
		self.pyText_ = None								# ��ť�ϵ��ı���ǩ����û�У�
		self.__initialize( button )						# ��ʼ��
		self.__isOffsetText = True						# bool������갴��ʱ�Ƿ��ı�����ƫ��һ������
		self.__state = UIState.COMMON					# ��ť��ǰ״̬
		self.__effDisable = True						# ��ɫ״̬ʱ���Ƿ񽫰�ť����Ⱦ��ʽ��Ϊ��COLOUR_EFF��

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

		self.mappings_ = {}										# ״̬ mapping
		self.mappings_[UIState.COMMON] = self.mapping			# ��ͨ״̬
		self.mappings_[UIState.HIGHLIGHT] = self.mapping		# ����״̬
		self.mappings_[UIState.PRESSED] = self.mapping			# ��갴��״̬
		self.mappings_[UIState.DISABLE] = self.mapping			# ��Ч״̬

		foreColor = ( 0, 0, 0, 0 )
		if hasattr( button, "lbText" ) :
			self.pyText_ = StaticText( button.lbText )
			foreColor = self.pyText_.color
			self.__textPos = self.pyText_.pos					# ��ʱ��¼�ı�������λ�ã����������ʱ�ָ��ı�λ�ã�
		self.foreColors_ = {}									# ״̬ǰ��ɫ
		self.foreColors_[UIState.COMMON] = foreColor			# ��ͨ״̬
		self.foreColors_[UIState.HIGHLIGHT] = foreColor			# ����״̬
		self.foreColors_[UIState.PRESSED] = foreColor			# ��갴��״̬
		self.foreColors_[UIState.DISABLE] = foreColor			# ��Ч״̬
		backColor = 255, 255, 255, 255
		self.backColors_ = {}									# ״̬����ɫ
		self.backColors_[UIState.COMMON] = backColor			# ��ͨ״̬
		self.backColors_[UIState.HIGHLIGHT] = backColor			# ����״̬
		self.backColors_[UIState.PRESSED] = backColor			# ��갴��״̬
		self.backColors_[UIState.DISABLE] = backColor			# ��Ч״̬


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def setDisableView_( self ) :
		"""
		������Чģʽ�µı���
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
		����ָ��״̬�µ���۱���
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
		����״̬ mapping
		@type					stMode : MACRO DEFINATION / tuple
		@param					stMode : ��ʾ���м��У�������״̬��ͼ�ŵ�ͬһ��ͼƬ�ϣ�: ( ����������)
									   : Ҳ������ guis.uidefine.py �� UIState ��ѡ��MODE_XXX
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
		���ð�ť״̬
		"""
		self.__state = state
		self.setStateView_( state )
		self.onStateChanged_( state )

	def resetSetate( self ) :
		"""
		��������ΪĬ��״̬
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
		return											# ͨ���ı� materialFX ��ʵ�ֱ��
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
		return											# ͨ���ı� materialFX ��ʵ�ֱ��
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
		return													# ͨ���ı� materialFX ��ʵ�ֱ��
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
	state = property( _getState )													# ��ȡ��ť�ĵ�ǰ״̬
	effDisable = property( _getEffDisable, _setEffDisable )							# ��ȡ/���û�ɫ״̬ʱ���Ƿ���� COLOUR_EFF ��Ⱦ
	commonMapping = property( _getCommonMapping, _setCommonMapping )				# ��ȡ/������ͨ״̬�µ���ͼ mapping
	highlightMapping = property( _getHighlightMapping, _setHighlightMapping )		# ��ȡ/���ø���״̬�µ���ͼ mapping
	pressedMapping = property( _getPressedMapping, _setPressedMapping )				# ��ȡ/���ð���״̬�µ���ͼ mapping
	disableMapping = property( _getDisableMapping, _setDisableMapping )				# ��ȡ/������Ч״̬�µ���ͼ mapping
	commonForeColor = property( _getCommonForeColor, _setCommonForeColor )			# ��ȡ/������ͨ״̬�µ�ǰ��ɫ
	highlightForeColor = property( _getHighlightForeColor, _setHighlightForeColor )	# ��ȡ/���ø���״̬�µ�ǰ��ɫ
	pressedForeColor = property( _getPressedForeColor, _setPressedForeColor )		# ��ȡ/���ð���״̬�µ�ǰ��ɫ
	disableForeColor = property( _getDisableForeColor, _setDisableForeColor )		# ��ȡ/������Ч״̬�µ�ǰ��ɫ
	commonBackColor = property( _getCommonBackColor, _setCommonBackColor )			# ��ȡ/������ͨ״̬�µı���ɫ
	highlightBackColor = property( _getHighlightBackColor, _setHighlightBackColor )	# ��ȡ/���ø���״̬�µı���ɫ
	pressedBackColor = property( _getPressedBackColor, _setPressedBackColor )		# ��ȡ/���ð���״̬�µı���ɫ
	disableBackColor = property( _getDisableBackColor, _setDisableBackColor )		# ��ȡ/������Ч״̬�µı���ɫ

	text = property( _getText, _setText )											# ��ȡ/���ð�ť�ı�������Ҫ�� lbText ����Ч��
	font = property( _getFont, _setFont )											# ��ȡ/�����ı����壨����Ҫ�� lbText ����Ч��
	fontSize = property( _getFontSize, _setFontSize ) 								# ��ȡ/�����ı����壨 ����Ҫ��lbtext ����Ч��
	foreColor = property( _getForeColor, _setForeColor )							# ��ȡ/�����ı�ǰ��ɫ������Ҫ�� lbText ����Ч��
	charSpace = property( lambda self : self.pyText_.charSpace, _setCharSpace )		# ��ȡ/�����ּ��
	limning = property( lambda self : self.pyText_.limning, _setLimning )			# ��ȡ/���������ʽ
	limnColor = property( lambda self : self.pyText_.limnColor, _setLimnColor )		# ��ȡ/���������ɫ
	isOffsetText = property( _getIsOffsetText, _setIsOffsetText ) 					# ��갴��ʱ���Ƿ��ı������½�ƫ��һ������
