# -*- coding: gb18030 -*-
#
# $Id: AddRelationBox.py Exp $

"""
implement friendnode item class
"""
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.TextBox import TextBox
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
import GUIFacade

class AddRelationBox( Window ):
	__instance=None
	def __init__( self ) :
		assert AddRelationBox.__instance is  None , "AddRelationBox instance has been created"
		AddRelationBox.__instance=self
		wnd = GUI.load( "guis/general/relationwindow/relationship/box.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.addToMgr( "relationShipAddRelationBox" )

		self.__pyTextBox = TextBox( wnd.textBox.box, self )			# text for input value
		self.__pyTextBox.inputMode = InputMode.COMMON
#		self.__pyTextBox.onKeyDown.bind( self.__onTextEnter )

		self.__pyBtnOK = HButtonEx( wnd.btnOk, self )
		self.__pyBtnOK.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOK.onLClick.bind( self.__onOk )

		self.__pyBtnCancel = HButtonEx( wnd.btnCancel,self)
		self.__pyBtnCancel.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancel.onLClick.bind( self.__onCancel )

		self.__callback = None
		self.__visibleDetectCBID = 0		# 侦测窗口的父窗口是否可见的 callback ID，原来用 timer，现改为直接用 callback( hyw -- 2008.06.24 )

		self.posZSegment 	 = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True

		labelGather.setPyBgLabel( self.__pyBtnOK, "RelationShip:RelationPanel", "btnOk" )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "RelationShip:RelationPanel", "btnCancel" )

	@staticmethod
	def instance():
		"""
		得到AddRelationBox的唯一实例
		"""
		if AddRelationBox.__instance is None:
			AddRelationBox.__instance=AddRelationBox()
		return AddRelationBox.__instance

	def __del__(self):

		Window.__del__( self )
		if Debug.output_del_AddRelationBox :
			INFO_MSG( str( self ) )




	#---------------------------------------------
	# private
	#---------------------------------------------
	def __notify( self ) :
		text = self.__pyTextBox.text.strip()
		text = text.replace( ' ', '' )
		try :
			self.__callback( text )
		except :
			EXCEHOOK_MSG()
		return True
	#------------------------------------------------------
	def __detect( self ) :
		if self.pyOwner is None :
			return
		if not self.pyOwner.rvisible :
			self.hide()
		else :
			self.__visibleDetectCBID = BigWorld.callback( 2.0, self.__detect )

	def __onOk( self ) :
		if self.__notify() :
			self.dispose()
			self.removeFromMgr()
			AddRelationBox.__instance=None

	def __onCancel( self ) :
		self.dispose()
		self.removeFromMgr()
		AddRelationBox.__instance=None

	def onKeyDown_( self, key, mods ) :
		if key == KEY_RETURN and mods == 0 :
			self.__onOk()
		return True

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, callback, pyOwner ) :
		self.__callback = callback
		self.__detect()
		Window.show( self, pyOwner )
		self.__pyTextBox.text = ''

	def hide( self ) :
		self.dispose()
		AddRelationBox.__instance=None
		BigWorld.cancelCallback( self.__visibleDetectCBID )
		Window.hide( self )

	def onActivated( self ) :
		"""
		当窗口激活时被调用
		"""
		Window.onActivated( self )
		self.__pyTextBox.tabStop = True


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getTitle( self ):
		return self.pyLbTitle_.text

	def _setTitle( self, title ):
		self.pyLbTitle_.text = labelGather.getText( "RelationShip:RelationPanel", "lbTitle" )%title

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	title = property( _getTitle, _setTitle )
