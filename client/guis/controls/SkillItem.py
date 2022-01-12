# -*- coding: gb18030 -*-
#
# $Id: SkillItem.py,v 1.6 2008-06-21 01:45:44 huangyongwei Exp $

"""
implement skillitem

2007.03.17: writen by huangyongwei
"""
"""
composing :
	GUI.Window
"""

from guis import *
from Item import Item

class SkillItem( Item ) :
	def __init__( self, item = None, pyBinder = None ) :
		Item.__init__( self, item, pyBinder )
		self.__initialize( item )
		self.focus = True
		self.dragFocus = True

	def subclass( self, item, pyBinder ) :
		Item.subclass( self, item, pyBinder )
		self.__initialize( item )

	def __del__( self ) :
		Item.__del__( self )
		if Debug.output_del_Skill :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, item ) :
		if item is None : return


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onDragStart_( self, pyDragged ) :
		"""
		it will be called before drag
		"""
		if self.itemInfo is None or self.itemInfo.isPassive :
			return False
		Item.onDragStart_( self, pyDragged )
		rds.ruisMgr.hideBar.enterShow()
		rds.ruisMgr.hideBar.hightlightLack()
		rds.ruisMgr.quickBar.hightlightLack()
		return True

	def onDragStop_( self, pyDragged ) :
		Item.onDragStop_( self, pyDragged )
		rds.ruisMgr.hideBar.leaveShow()
		rds.ruisMgr.hideBar.hidelightLack()
		rds.ruisMgr.quickBar.hidelightLack()
		return True
		
	def onMouseLeave_( self ) :
		Item.onMouseLeave_( self )
		toolbox.itemCover.hideItemCover( self )
