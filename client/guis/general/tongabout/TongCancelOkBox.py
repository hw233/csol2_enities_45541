# -*- coding: gb18030 -*-
#
# $Id: MsgBox.py,v 1.9 2008-08-26 02:22:08 huangyongwei Exp $

"""
implement yell verify messagebox
-- 2009/04/23: writen by huangyongwei
"""

from guis import *
from guis.tooluis.messagebox.MsgBox import OkCancelBox

class TongCancelOkBox( OkCancelBox ) :
	def __init__( self ) :
		box = GUI.load( "guis/general/tongabout/tongcancelokbox/box.gui" )
		uiFixer.firstLoadFix( box )
		OkCancelBox.__init__( self, box )
		self.activable_ = False
		self.__callback = None

	def dispose( self ) :
		global _pyBox
		_pyBox = None
		OkCancelBox.dispose( self )
		self.__callback = None

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __feedback( self, resultID ) :
		"""
		点击按钮后的返回
		"""
		self.__callback( resultID )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, msg, title, callback, pyOwner = None ) :
		self.__callback = callback
		OkCancelBox.show( self, msg, title, self.__feedback, pyOwner )

_pyBox = None

def show( msg, title, callback, pyOwner = None ) :
	global _pyBox
	if _pyBox :
		_pyBox.show( msg, title, callback, pyOwner )
	else:
		_pyBox = TongCancelOkBox().show( msg, title, callback, pyOwner )