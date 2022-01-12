# -*- coding: gb18030 -*-
#
# $Id: __init__.py,v 1.5 2008-08-11 07:21:29 huangyongwei Exp $

"""
implement show message functions
"""

from MsgBox import *

def showOk( msg, title, callback, pyOwner, gstStatus ) :
	"""
	show messasge box
	msg		 : message text
	title	 : title text showing at the top of the window
	callback : callback function
	"""
	pyOkBox = OkBox()
	pyOkBox.show( msg, title, callback, pyOwner, gstStatus )
	return pyOkBox

def showCancel( msg, title, callback, pyOwner, gstStatus ) :
	"""
	show messasge box
	msg		 : message text
	title	 : title text showing at the top of the window
	callback : callback function
	"""
	pyCancelBox = CancelBox()
	pyCancelBox.show( msg, title, callback, pyOwner, gstStatus )
	return pyCancelBox

def showSpecialCancel( msg, title, callback, pyOwner, gstStatus ) :
	"""
	show messasge box
	msg		 : message text
	title	 : title text showing at the top of the window
	callback : callback function
	"""
	pyCancelBox = SpecialCancelBox()
	pyCancelBox.show( msg, title, callback, pyOwner, gstStatus )
	return pyCancelBox

def showOkCancel( msg, title, callback, pyOwner, gstStatus ) :
	pyOkCancelBox = OkCancelBox()
	pyOkCancelBox.show( msg, title, callback, pyOwner, gstStatus )
	return pyOkCancelBox

def showYesNo( msg, title, callback, pyOwner, gstStatus ) :
	pyYesBox = YesNoBox()
	pyYesBox.show( msg, title, callback, pyOwner, gstStatus )
	return pyYesBox

def showYesNoCancel( msg, title, callback, pyOwner, gstStatus ) :
	pyYesNoCancelBox = YesNoCancelBox()
	pyYesNoCancelBox.show( msg, title, callback, pyOwner, gstStatus )
	return pyYesNoCancelBox

def showSpecialOkCancel( msg, title, callback, pyOwner, gstStatus ) :
	pySpecialOkCancelBox = SpecialOkCancelBox()
	pySpecialOkCancelBox.show( msg, title, callback, pyOwner, gstStatus )
	return pySpecialOkCancelBox
