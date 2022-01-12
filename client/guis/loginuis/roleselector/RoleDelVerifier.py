# -*- coding: gb18030 -*-
#
# $Id: InputBox.py,v 1.27 2008-08-26 02:21:47 huangyongwei Exp $

"""
implement delete role verifier box

2009/05/09 : writen by huangyongwei
"""

from guis import *
from guis.tooluis.inputbox.InputBox import InputBox
from guis.controls.StaticText import StaticText
from LabelGather import labelGather

class RoleDelVerifier( InputBox ) :
	def __init__( self ) :
		wnd = GUI.load( "guis/loginuis/roleselector/verfywnd.gui" )
		uiFixer.firstLoadFix( wnd )
		InputBox.__init__( self, wnd )
		self.__pySTTip = StaticText( wnd.stTip )
		labelGather.setLabel( wnd.lbTitle, "RoleSelector:main", "delPlayer" )
		labelGather.setLabel( wnd.stTips, "RoleSelector:main", "stTips" )
		labelGather.setLabel( wnd.stDelTip, "RoleSelector:main", "stDelTip" )

	def show( self, tip, callback, pyOwner = None ) :
		self.__pySTTip.text = tip
		InputBox.show( self, "", callback, pyOwner )
		

