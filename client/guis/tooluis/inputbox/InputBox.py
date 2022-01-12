# -*- coding: gb18030 -*-
#
# $Id: InputBox.py,v 1.27 2008-08-26 02:21:47 huangyongwei Exp $

"""
implement input box panels

2007/08/05 : writen by huangyongwei
"""

from AbstractTemplates import Singleton
from LabelGather import labelGather
from guis import *
from guis.common.Window import Window
from guis.controls.TextBox import TextBox
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
import BigWorld
import csdefine
import GUIFacade

def isHExButton( gui ) :
	if not isinstance( gui, GUI.TextureFrame ) : return False
	elems = gui.elements.keys()
	for elm in ("frm_l", "frm_r", "frm_bg") :
		if elm not in elems : return False
	return True

class InputBox( Singleton, Window ) :
	def __init__( self, wnd = None ) :
		if wnd is None :
			wnd = GUI.load( "guis/tooluis/inputbox/wnd.gui" )
			uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ = True
		self.addToMgr()

		self.pySTTitle_ = None
		if hasattr( wnd, "stTitle" ) :
			self.pySTTitle_ = StaticText( wnd.stTitle )				# 标题

		self.pyTextBox_ = TextBox( wnd.tbInput, self )				# 文本输入框
		self.pyTextBox_.inputMode = InputMode.COMMON
		self.maxLength = 16											# 最大输入长度

		if isHExButton( wnd.btnOk ) :
			self.pyBtnOk_ = HButtonEx( wnd.btnOk, self )			# 确定按钮
			self.pyBtnOk_.setExStatesMapping( UIState.MODE_R4C1 )
		else :
			self.pyBtnOk_ = Button( wnd.btnOk, self )				# 确定按钮
			self.pyBtnOk_.setStatesMapping( UIState.MODE_R4C1 )
		self.pyBtnOk_.onLClick.bind( self.__onOk )
		self.setOkButton( self.pyBtnOk_ )

		if isHExButton( wnd.btnCancel ) :
			self.pyBtnCancel_ = HButtonEx( wnd.btnCancel,self)		# 取消按钮
			self.pyBtnCancel_.setExStatesMapping( UIState.MODE_R4C1 )
		else :
			self.pyBtnCancel_ = Button( wnd.btnCancel,self)			# 取消按钮
			self.pyBtnCancel_.setStatesMapping( UIState.MODE_R4C1 )
		self.pyBtnCancel_.onLClick.bind( self.__onCancel )
		self.setCancelButton( self.pyBtnCancel_ )

		self.pressedOK_ = False										# 临时变量，点击了确定按钮，它被置为 True，窗口关闭时判断该变量以致可以知道玩家是怎么关闭窗口的
		self.callback_ = None										# 回调

		# ---------------------------------------------
		# 设置多语言标签
		# ---------------------------------------------
		labelGather.setPyLabel( self.pyLbTitle_, "InputBox:main", "title" )
		if self.pySTTitle_ :
			labelGather.setPyLabel( self.pySTTitle_, "InputBox:main", "tips" )
		labelGather.setPyBgLabel( self.pyBtnOk_, "InputBox:main", "btnOk" )
		labelGather.setPyBgLabel( self.pyBtnCancel_, "InputBox:main", "btnCancel" )

	def __del__( self ) :
		Window.__del__( self )
		if Debug.output_del_InputBox :
			INFO_MSG( str( self ) )

	def dispose( self ) :
		Window.dispose( self )
		self.__class__.releaseInst()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onOk( self ) :
		"""
		确定按钮被点击
		"""
		self.pressedOK_ = True
		self.hide()

	def __onCancel( self ) :
		"""
		取消按钮被点击
		"""
		self.pressedOK_ = False
		self.hide()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def notify_( self, res ) :
		"""
		关闭窗口时被调用，在这里通过回调通知父体
		"""
		try :
			text = self.pyTextBox_.text
			self.callback_( res, text )
		except :
			EXCEHOOK_MSG()
		self.pressedOK_ = False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, title, callback, pyOwner = None ) :
		"""
		显示输入框
		@type				title	 : str
		@param				title	 : 标题
		@type				callback : functor
		@param				callback : 回调
		@type				pyOwner  : python ui
		@param				pyOwner  : 所属的父窗口，如果传入该参数，则输入框将永远处于 pyOwner 的上面
		@return						 : None
		"""
		if self.callback_ :
			self.notify_( DialogResult.CANCEL )
		self.callback_ = callback
		if self.pySTTitle_ :
			self.pySTTitle_.text = title
		self.pyTextBox_.text = ''
		Window.show( self, pyOwner )
		self.pyTextBox_.tabStop = True

	def hide( self ) :
		"""
		隐藏输入框
		"""
		Window.hide( self )
		if self.pressedOK_ :
			self.notify_( DialogResult.OK )
		else :
			self.notify_( DialogResult.CANCEL )
		self.callback_ = None
		self.dispose()

	def onActivated( self ) :
		"""
		当窗口激活时被调用
		"""
		Window.onActivated( self )
		self.pyTextBox_.tabStop = True


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getText( self ) :
		return self.pyTextBox_.text

	def _setText( self, text ) :
		self.pyTextBox_.text = text

	# -------------------------------------------------
	def _getInputMode( self ) :
		return self.pyTextBox_.inputMode

	def _setInputMode( self, mode ) :
		self.pyTextBox_.inputMode = mode

	# -------------------------------------------------
	def _getMaxLength( self ):
		return self.pyTextBox_.maxLength

	def _setMaxLength( self, length ):
		self.pyTextBox_.maxLength = length


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( _getText, _setText )											# 获得/设置输入的文字
	inputMode = property( _getInputMode, _setInputMode )							# 设置输入模式，在 uidefine 中定义：InputMode
	maxLength = property( _getMaxLength, _setMaxLength )							# 设置允许输入的最大长度（字符数）



# --------------------------------------------------------------------
# implement input amount box
# --------------------------------------------------------------------
class AmountInputBox( InputBox ) :
	"""
	输入数量（只能输入整数）
	"""
	def __init__( self ) :
		wnd = GUI.load( "guis/tooluis/inputbox/amount_wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		InputBox.__init__( self, wnd )
		self.pyTextBox_.onTextChanged.bind( self.__onTextChanged )
		self.pyBtnOk_.enable = False

		self.__pyBtnMax = Button( wnd.btnMax )						# 最大值按钮
		self.__pyBtnMax.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnMax.onLClick.bind( self.__onMaxBtnClick )

		self.inputMode = InputMode.INTEGER							# 设置为只允许输入数值
		self.maxLength = 10											# 默认最多输入十位数
		self.__rng = None											# 默认可以输入任意大小的数值

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setLabel( wnd.btnCancel.lbText, "InputBox:AmountInputBox", "btnCancel" )
		labelGather.setLabel( wnd.btnOk.lbText, "InputBox:AmountInputBox", "btnOk" )
		labelGather.setLabel( wnd.lbTitle, "InputBox:AmountInputBox", "lbTitle" )

	def __del__( self ) :
		Window.__del__( self )
		if Debug.output_del_InputBox :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onTextChanged( self ) :
		"""
		当输入文本改变时被调用
		"""
		if self.text.strip() == "" or int(self.text) == 0:
			self.pyBtnOk_.enable = False
		elif self.__rng is not None :
			amount = int( self.text )
		#	self.pyBtnOk_.enable = amount >= self.__rng[0] and amount <= self.__rng[1]
		#else :  根据策划需求修改 取消上限
			self.pyBtnOk_.enable = True

	def __onMaxBtnClick( self ) :
		"""
		当最大值按钮被点击时调用
		"""
		if self.__rng is None :
			if self.maxLength > 0 :
				self.text = '9' * self.maxLength
		else :
			self.text = str( int(self.text) + 20 ) #每次增加20


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def notify_( self, res ) :
		"""
		关闭窗口时被调用，在这里通过回调通知父体
		"""
		text = self.text.replace( ' ', '' )
		if not text.isdigit() : return False
		amount = int( text )
		try :
			self.callback_( res, amount )
		except :
			EXCEHOOK_MSG()
		self.pressedOK_ = False


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def show( self, callback, pyOwner = None, rng = None ) :
		"""
		显示整数输入框
		@type				callback : functor
		@param				callback : 回调
		@type				pyOwner	 : python ui
		@param				pyOwner	 : 所属的父窗口，如果传入该参数，则输入框将永远处于 pyOwner 的上面
		@type				rng		 : tuple of two element
		@param				rng		 : 允许的输入范围，缺省为可以输入任意范围( 如：( 1, 100 )，则包括 100 )
		@return						 : None
		"""
		InputBox.show( self, "", callback, pyOwner )
		self.__rng = rng
		self.pyBtnOk_.enable = rng is not None
		self.text = str( rng[0] )
		self.pyTextBox_.tabStop = True
