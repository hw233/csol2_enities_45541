# -*- coding: gb18030 -*-
#
# $Id: BaseInput.py,v 1.19 2008-06-21 01:48:39 huangyongwei Exp $

"""
implement cursor class
2009/01/20 : writen by huangyongwei
"""

import weakref
from AbstractTemplates import Singleton
from guis import *
from guis.common.GUIBaseObject import GUIBaseObject

# --------------------------------------------------------------------
# implement cursor
# --------------------------------------------------------------------
class Cursor( Singleton, GUIBaseObject ) :
	def __init__( self ) :
		cursor = GUI.load( "guis/common/cursor.gui"  )
		GUIBaseObject.__init__( self, cursor )
		uiFixer.firstLoadFix( cursor )
		cursor.visible = False
		self.__flickCBID = 0

		self.__pyBinder = None


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __flick( self ) :
		"""
		闪烁光标
		"""
		self.alpha = ( self.alpha == 0 ) * 255
		if not self.rvisible or self.pyBinder is None :
			self.uncap( self.pyBinder )
		else :
			BigWorld.cancelCallback( self.__flickCBID )
			self.__flickCBID = BigWorld.callback( 0.5, self.__flick )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def cap( self, pyInput ) :
		"""
		将光标附加到输入框
		"""
		pyInput.addPyChild( self )
		self.posZ = 0.0
		self.__pyBinder = weakref.ref( pyInput )
		self.visible = True
		self.__flick()

	def uncap( self, pyInput ) :
		"""
		去除光标
		"""
		pyBinder = self.pyBinder
		if pyBinder is None or pyInput == pyBinder :
			self.visible = False
			self.alpha = 0
			BigWorld.cancelCallback( self.__flickCBID )
			if pyInput : pyInput.delPyChild( self )
			self.__pyBinder = None

	def capped( self, pyInput ) :
		"""
		判断给出的输入框是否为光标所属的输入框
		"""
		if self.rvisible :
			return self.pyBinder == pyInput
		return False


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getBinder( self ) :
		if self.__pyBinder is None :
			return None
		return self.__pyBinder()

	# -------------------------------------------------
	def _setLeft( self, left ) :
		GUIBaseObject._setLeft( self, left )
		self.alpha = 0
		self.__flick()

	def _setRight( self, right ) :
		GUIBaseObject._setRight( self, right )
		self.alpha = 0
		self.__flick()


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyBinder = property( _getBinder )
	left = property( GUIBaseObject._getLeft, _setLeft )
	right = property( GUIBaseObject._getRight, _setRight )
