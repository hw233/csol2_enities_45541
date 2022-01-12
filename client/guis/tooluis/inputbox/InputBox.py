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
			self.pySTTitle_ = StaticText( wnd.stTitle )				# ����

		self.pyTextBox_ = TextBox( wnd.tbInput, self )				# �ı������
		self.pyTextBox_.inputMode = InputMode.COMMON
		self.maxLength = 16											# ������볤��

		if isHExButton( wnd.btnOk ) :
			self.pyBtnOk_ = HButtonEx( wnd.btnOk, self )			# ȷ����ť
			self.pyBtnOk_.setExStatesMapping( UIState.MODE_R4C1 )
		else :
			self.pyBtnOk_ = Button( wnd.btnOk, self )				# ȷ����ť
			self.pyBtnOk_.setStatesMapping( UIState.MODE_R4C1 )
		self.pyBtnOk_.onLClick.bind( self.__onOk )
		self.setOkButton( self.pyBtnOk_ )

		if isHExButton( wnd.btnCancel ) :
			self.pyBtnCancel_ = HButtonEx( wnd.btnCancel,self)		# ȡ����ť
			self.pyBtnCancel_.setExStatesMapping( UIState.MODE_R4C1 )
		else :
			self.pyBtnCancel_ = Button( wnd.btnCancel,self)			# ȡ����ť
			self.pyBtnCancel_.setStatesMapping( UIState.MODE_R4C1 )
		self.pyBtnCancel_.onLClick.bind( self.__onCancel )
		self.setCancelButton( self.pyBtnCancel_ )

		self.pressedOK_ = False										# ��ʱ�����������ȷ����ť��������Ϊ True�����ڹر�ʱ�жϸñ������¿���֪���������ô�رմ��ڵ�
		self.callback_ = None										# �ص�

		# ---------------------------------------------
		# ���ö����Ա�ǩ
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
		ȷ����ť�����
		"""
		self.pressedOK_ = True
		self.hide()

	def __onCancel( self ) :
		"""
		ȡ����ť�����
		"""
		self.pressedOK_ = False
		self.hide()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def notify_( self, res ) :
		"""
		�رմ���ʱ�����ã�������ͨ���ص�֪ͨ����
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
		��ʾ�����
		@type				title	 : str
		@param				title	 : ����
		@type				callback : functor
		@param				callback : �ص�
		@type				pyOwner  : python ui
		@param				pyOwner  : �����ĸ����ڣ��������ò��������������Զ���� pyOwner ������
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
		���������
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
		�����ڼ���ʱ������
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
	text = property( _getText, _setText )											# ���/�������������
	inputMode = property( _getInputMode, _setInputMode )							# ��������ģʽ���� uidefine �ж��壺InputMode
	maxLength = property( _getMaxLength, _setMaxLength )							# ���������������󳤶ȣ��ַ�����



# --------------------------------------------------------------------
# implement input amount box
# --------------------------------------------------------------------
class AmountInputBox( InputBox ) :
	"""
	����������ֻ������������
	"""
	def __init__( self ) :
		wnd = GUI.load( "guis/tooluis/inputbox/amount_wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		InputBox.__init__( self, wnd )
		self.pyTextBox_.onTextChanged.bind( self.__onTextChanged )
		self.pyBtnOk_.enable = False

		self.__pyBtnMax = Button( wnd.btnMax )						# ���ֵ��ť
		self.__pyBtnMax.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnMax.onLClick.bind( self.__onMaxBtnClick )

		self.inputMode = InputMode.INTEGER							# ����Ϊֻ����������ֵ
		self.maxLength = 10											# Ĭ���������ʮλ��
		self.__rng = None											# Ĭ�Ͽ������������С����ֵ

		# ---------------------------------------------
		# ���ñ�ǩ
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
		�������ı��ı�ʱ������
		"""
		if self.text.strip() == "" or int(self.text) == 0:
			self.pyBtnOk_.enable = False
		elif self.__rng is not None :
			amount = int( self.text )
		#	self.pyBtnOk_.enable = amount >= self.__rng[0] and amount <= self.__rng[1]
		#else :  ���ݲ߻������޸� ȡ������
			self.pyBtnOk_.enable = True

	def __onMaxBtnClick( self ) :
		"""
		�����ֵ��ť�����ʱ����
		"""
		if self.__rng is None :
			if self.maxLength > 0 :
				self.text = '9' * self.maxLength
		else :
			self.text = str( int(self.text) + 20 ) #ÿ������20


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def notify_( self, res ) :
		"""
		�رմ���ʱ�����ã�������ͨ���ص�֪ͨ����
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
		��ʾ���������
		@type				callback : functor
		@param				callback : �ص�
		@type				pyOwner	 : python ui
		@param				pyOwner	 : �����ĸ����ڣ��������ò��������������Զ���� pyOwner ������
		@type				rng		 : tuple of two element
		@param				rng		 : ��������뷶Χ��ȱʡΪ�����������ⷶΧ( �磺( 1, 100 )������� 100 )
		@return						 : None
		"""
		InputBox.show( self, "", callback, pyOwner )
		self.__rng = rng
		self.pyBtnOk_.enable = rng is not None
		self.text = str( rng[0] )
		self.pyTextBox_.tabStop = True
