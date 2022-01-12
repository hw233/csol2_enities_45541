# -*- coding: gb18030 -*-

from guis import *
from guis.common.Window import Window
from guis.controls.TextBox import TextBox
from guis.controls.Button import Button

class AccountDelBox( Window ) :

	__max_input_allow = 6#�����������������

	def __init__( self ) :
		wnd = GUI.load( "guis/general/delrole/delbox.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )

		self.__pyTextBox = TextBox( wnd.textPanel, self )#������
		self.__pyTextBox.maxLength = AccountDelBox.__max_input_allow

		self.__pyOkBtn = Button( wnd.okBtn, self )#ȷ�� ��Ŧ
		self.__pyOkBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyOkBtn.onLClick.bind( self.__onButtonOkClick )

		self.__pyCancelBtn = Button( wnd.cancelBtn, self )#ȡ�� ��Ŧ
		self.__pyCancelBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyCancelBtn.onLClick.bind( self.__onButtonCancelClick )

		self.__callback = None

		self.posZSegment 	 = ZSegs.L1
		self.activable_ = False
		self.addToMgr( "amountDeleteBox" )

	def dispose( self ):#����ɾ��
		self.__pyOkBtn.dispose()
		self.__pyCancelBtn.dispose()
		self.__pyTextBox.dispose()
		Window.dispose( self )

	def onClose_( self ):#X��Ŧ
		self.__onButtonCancelClick( self.__pyCancelBtn )
		return True

	def __onButtonOkClick( self, pyBtn ):#�����ȷ����Ŧ
		text = self.__pyTextBox.text.strip()#��ȡ�����string
		try:
			self.__callback( DialogResult.OK, text )#callback
		except :
			EXCEHOOK_MSG()
		self.dispose()

	def __onButtonCancelClick( self, pyBtn ):#�����ȡ����Ŧ
		try:
			self.__callback( DialogResult.CANCEL, text = "" )#callback
		except :
			EXCEHOOK_MSG()
		self.dispose()


	def onKeyUp_( self, key, mods ):#�س���ȷ��
		if key == KEY_RETURN and mods == 0:
			self.__onOk()
		return True

	def __onOk( self ):
		self.__onButtonOkClick( self.__pyOkBtn )

	def show( self, callback ):#��ʾ��ɫɾ��ȷ�Ͻ���
		self.__callback = callback
		self.__pyTextBox.text = ''
		Window.show( self )

	def onActivated( self ) :
		"""
		�����ڼ���ʱ������
		"""
		Window.onActivated( self )
		self.__pyTextBox.tabStop = True

	def onLeaveWorld( self ) :
		self.hide()
