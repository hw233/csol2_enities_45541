# -*- coding: gb18030 -*-
#
# $Id: IME.py,v 1.2 2008-02-13 10:08:45 huangyongwei Exp $

"""
implement textbox class
2008/01/26 : writen by huangyongwei
"""

import csol
import Font
from gbref import rds


def __imeInput( text ) :
	pyACon = rds.uiHandlerMgr.getTabInUI()
	if pyACon is None :
		inactive()
		return
	if not hasattr( pyACon, "notifyInput" ) :
		return
	if Font.isWideFont( pyACon.font ) :
		pyACon.notifyInput( text )

def initialize() :
	csol.setImeEventFunc( 0, __imeInput )

def active() :
	imeHandler = csol.ImeHandle()
	if imeHandler :
		imeHandler.canInput( True )

def inactive() :
	imeHandler = csol.ImeHandle()
	if imeHandler :
		imeHandler.canInput( False )

def isActivated() :
	imeHandler = csol.ImeHandle()
	if imeHandler :
		return imeHandler.getImeName() != ""
	return False

def is9FangInputActivated() :
	return csol.findWindow( "", "q9appwin" ) and not csol.getKeyState( "NUMLOCK" )
