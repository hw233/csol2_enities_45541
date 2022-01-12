# -*- coding: gb18030 -*-
#
# $Id: InputPanel.py,v 1.1 2008-03-06 09:25:30 fangpengjun Exp $

"""
implement inputpanel  class
# 写信窗口中的输入框
"""
from guis import *
from guis.tooluis.CSMLRichTextBox import CSMLRichTextBox
from guis.common.PyGUI import PyGUI

class InputPanel( PyGUI ):
	def __init__( self, panel = None, scrollBar = None, pyBinder = None ):
		PyGUI.__init__( self, panel )
		self.__initialize( panel, scrollBar )

	def subclass( self, panel, scrollBar, pyBinder ):
		PyGUI.subclass( self, panel, pyBinder )
		self.__initialize( panel, scrollBar )
		return self

	def __initialize( self, panel, scrollBar ):
		if panel is None :return
		self.__pyInputBox = CSMLRichTextBox( panel.textBox, scrollBar )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getText( self ) :
		return self.__pyInputBox.text

	def _setText( self, text ) :
		self.__pyInputBox.text = text

	# -------------------------------------------------
	def _getFont( self ) :
		return self.__pyInputBox.font

	def _setFont( self, font ) :
		self.__pyInputBox.font = font

	# ---------------------------------------
	def _getForeColor( self ) :
		return self.__pyInputBox.foreColor

	def _setForeColor( self, color ) :
		self.__pyInputBox.foreColor = color

	def _getTabStop( self ) :
		return self.__pyInputBox.tabStop

	def _setTabStop( self, tabStop ) :
		self.__pyInputBox.tabStop = tabStop
	
	def _getPyBox( self ):
		return self.__pyInputBox

	# -------------------------------------------------
#	def _getSpacing( self ) :
#		return self.pyRichText_.spacing

#	def _setSpacing( self, spacing ) :
#		self.pyRichText_.spacing = spacing
#		self.__resetScrollProperties()

	# -------------------------------------------------
#	def _getLineCount( self ) :
#		return self.pyRichText_.lineCount

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( _getText, _setText )						# get or set text
	font = property( _getFont, _setFont )						# get or set font
	foreColor = property( _getForeColor, _setForeColor )		# get or set color
	tabStop = property( _getTabStop, _setTabStop )				# 设置/获取焦点
	pyBox = property( _getPyBox )
#	spacing = property( _getSpacing, _setSpacing )				# get or set spacing between two lines
#	lineCount = property( _getLineCount )						# get the number of lines