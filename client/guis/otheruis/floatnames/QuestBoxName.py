# -*- coding: gb18030 -*-
#
# $Id: QuestBoxName.py,v 1.3 2008-06-27 03:20:42 huangyongwei Exp $

"""
implement float name of the character
2009.02.13：tidy up by huangyongwei
"""

import event.EventCenter as ECenter
from guis import *
from FloatName import FloatName
from EntityDecoratorMgr import EntityDecoratorMgr

g_entDecConfig = EntityDecoratorMgr.instance()
from DoubleName import DoubleName

class QuestBoxName( FloatName ) :
	def __init__( self ) :
		wnd = GUI.load( "guis/otheruis/floatnames/questboxname.gui" )
		uiFixer.firstLoadFix( wnd )
		FloatName.__init__( self, wnd )
		self.visible = False
		self.pyLbName_ = DoubleName( wnd.elemName )	
		self.pyElements_ = [self.pyLbName_]
		self.pyLbName_.toggleRightName( False )

	def dispose( self ) :
		FloatName.dispose( self )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def layout_( self ) :
		self.pyLbName_.toggleLeftName( g_entDecConfig.getQuestBoxNameShowState() )
		FloatName.layout_( self )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEnterWorld( self ) :
		FloatName.onEnterWorld( self )

	# ---------------------------------------
	def onTargetFocus( self ) :
		self.visible = True

	def onTargetBlur( self ) :
		if BigWorld.player().targetEntity != self.entity_:
			self.visible = False

	# ---------------------------------------
	def onBecomeTarget( self ) :
		self.visible = True

	def onLoseTarget( self ) :
		self.visible = False