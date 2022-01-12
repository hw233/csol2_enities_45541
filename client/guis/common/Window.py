# -*- coding: gb18030 -*-
#
# $Id: Window.py,v 1.17 2008-08-26 02:12:34 huangyongwei Exp $

"""
implement standard window
2006/08/22 : writen by huangyongwei
"""
"""
composing :
	GUI.Window
		-- lbTitle  [optional gui]( GUI.Text )-> label for show window title
		-- closeBtn [optional gui]( GUI.XXX  )-> close button
		-- helpBtn  [optional gui]( GUI.XXX  )-> help button
		-- minBtn   [optional gui]( GUI.XXX  )-> minimize button
"""


from guis import *
from RootGUI import RootGUI
from guis.controls.StaticText import StaticText
from guis.controls.Button import Button
import Helper


class Window( RootGUI ) :
	def __init__( self, wnd = None ) :
		RootGUI.__init__( self, wnd )			# calling parent's constructor
		self.__initialize( wnd )
		self.helpName_ = ""						# the help file is stored in folder: "clent/help/syshelp.xml"
												# this is the tag name in the help config file
	def subclass( self, wnd ) :
		RootGUI.subclass( self, wnd )
		self.__initialize( wnd )
		return self

	def __del__( self ) :
		RootGUI.__del__( self )
		if Debug.output_del_Window :
			INFO_MSG( str( self ) )

	def __initialize( self, wnd ) :
		if wnd is None : return
		self.__wnd = wnd
		if self.__wnd is None : return
		self.__wnd.visible = False

		self.posZSegment = ZSegs.L4							# in uidefine.py
		self.activable_ = True								# indicate window can be activated
		self.escHide_ = True								# if escHide_ is True, when pressed key "ESC" the gui will hide

		# ----------------------------------------
		# potected
		# ----------------------------------------
		self.pyLbTitle_ = StaticText()
		if hasattr( wnd, "lbTitle" ) :
			self.pyLbTitle_.subclass( wnd.lbTitle )
		self.pyMinBtn_ = self.__createPyButtons( "minBtn" )
		self.pyHelpBtn_ = self.__createPyButtons( "helpBtn" )
		self.pyCloseBtn_ = self.__createPyButtons( "closeBtn" )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __createPyButtons( self, name ) :
		"""
		if the window contain many buttons, create its' python object
		"""
		if hasattr( self.__wnd, name ) :
			btn = getattr( self.__wnd, name )
			pyBtn = Button( btn )
			pyBtn.setStatesMapping( UIState.MODE_R2C2 )
			pyBtn.onLClick.bind( self.__onButtonClick )
			return pyBtn
		return None

	def __onButtonClick( self, sender ) :
		if sender == self.pyMinBtn_ :
			self.onMinimize_()
			return True
		if sender == self.pyHelpBtn_ :
			self.onShowHelp_()
			return True
		if sender == self.pyCloseBtn_ :
			self.hide()
		return False


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMinimize_( self ) :
		"""
		when the minBtn be clicked it will be called
		"""
		pass

	def onShowHelp_( self ) :
		"""
		when the helpBtn be clicked it will be called
		"""
		pass


	# ----------------------------------------------------------------
	# property method
	# ----------------------------------------------------------------
	def _getTitle( self ) :
		return self.pyLbTitle_.text

	def _setTitle( self, title ) :
		self.pyLbTitle_.text = title

	def show( self, pyOwner = None, floatOwner = True ) :
		"""
		show gui
		"""
		RootGUI.show( self, pyOwner, floatOwner )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	title = property( _getTitle, _setTitle )			# title of the window
