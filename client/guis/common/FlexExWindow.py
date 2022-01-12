# -*- coding: gb18030 -*-
#
# $Id: FlexWindow.py,v 1.5 2008-06-21 01:51:28 huangyongwei Exp $

"""
window can resize
2006/06/11 : writen by huangyongwei
"""
"""
composing :
	GUI.Window
		-- lt ( GUI.Window / GUI.Simple ) -> left-top angle
		-- rt ( GUI.Window / GUI.Simple ) -> right-top angle
		-- lb ( GUI.Window / GUI.Simple ) -> left-bottom angle
		-- rb ( GUI.Window / GUI.Simple ) -> right-bottom angle
		-- l  ( GUI.Window / GUI.Simple ) -> left angle
		-- r  ( GUI.Window / GUI.Simple ) -> right angle
		-- t  ( GUI.Window / GUI.Simple ) -> top angle
		-- b  ( GUI.Window / GUI.Simple ) -> bottom angle
		-- bg ( GUI.Window / GUI.Simple ) -> back grond

		-- lbTitle  [optional gui]( GUI.Text )-> label for show window title
		-- closeBtn [optional gui]( GUI.XXX  )-> close button
		-- helpBtn  [optional gui]( GUI.XXX  )-> help button
		-- minBtn   [optional gui]( GUI.XXX  )-> minimize button
"""


from guis import *
from Window import Window
from FrameEx import HVFrameEx
from RootGUI import RootGUI
# --------------------------------------------------------------------
# window can resize on horizontal and vertical
# --------------------------------------------------------------------
class HVFlexExWindow( HVFrameEx, Window ) :
	def __init__( self, wnd = None ) :
		HVFrameEx.__init__( self, wnd )
		Window.__init__( self, wnd )
		self.elmBgTitle_ = wnd.elements.get("wnd_bgTitle")

	def subclass( self, wnd ) :
		HVFrameEx.subclass( self, wnd )
		Window.subclass( self, wnd )
		return self

	def dispose( self ) :
		HVFrameEx.dispose( self )
		Window.dispose( self )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setWidth( self, width ) :
		old_width = self.width
		HVFrameEx._setWidth( self, width )
		width = self.width
		if self.pyMinBtn_ :
			rr = old_width - self.pyMinBtn_.right
			self.pyMinBtn_.right = width - rr
		if self.pyHelpBtn_ :
			rr = old_width - self.pyHelpBtn_.right
			self.pyHelpBtn_.right = width - rr
		if self.pyCloseBtn_ :
			rr = old_width - self.pyCloseBtn_.right
			self.pyCloseBtn_.right = width - rr
		if self.elmBgTitle_ :
			scale_util.setFElemCenter(self.elmBgTitle_, width*0.5)
		self.pyLbTitle_.center = width*0.5

	def _setSize( self, size ) :
		self.width = size[0]
		self.height = size[1]

	def reShow( self, pyOwner = None, floatOwner = True ) :
		"""
		show gui
		"""
		RootGUI.show( self, pyOwner, floatOwner )
	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	width = property( HVFrameEx._getWidth, _setWidth )
	size = property( HVFrameEx._getSize, _setSize )


# ----------------------------------------------------------------
# window can resize on vertical
# ----------------------------------------------------------------
"""
composing :
	GUI.Window
		-- l [optional gui] ( GUI.Window / GUI.Simple ) -> left angle
		-- r [optional gui] ( GUI.Window / GUI.Simple ) -> right angle
		-- t  ( GUI.Window / GUI.Simple ) -> top angle
		-- b  ( GUI.Window / GUI.Simple ) -> bottom angle
		-- bg ( GUI.Window / GUI.Simple ) -> back grond

		-- lbTitle  [optional gui]( GUI.Text )-> label for show window title
		-- closeBtn [optional gui]( GUI.XXX  )-> close button
		-- helpBtn  [optional gui]( GUI.XXX  )-> help button
		-- minBtn   [optional gui]( GUI.XXX  )-> minimize button
"""


from FrameEx import VFrameEx

class VFlexExWindow( VFrameEx, Window ) :
	def __init__( self, wnd = None ) :
		VFrameEx.__init__( self, wnd )
		Window.__init__( self, wnd )

	def subclass( self, wnd ) :
		VFrameEx.subclass( self, wnd )
		Window.subclass( self, wnd )
		return self

	def dispose( self ) :
		VFrameEx.dispose( self )
		Window.dispose( self )


# ----------------------------------------------------------------
# window can resize on horizontal
# ----------------------------------------------------------------
"""
composing :
	GUI.Window
		-- l ( GUI.Window / GUI.Simple ) -> left angle
		-- r ( GUI.Window / GUI.Simple ) -> right angle
		-- t [optional gui] ( GUI.Window / GUI.Simple )-> top angle
		-- b [optional gui] ( GUI.Window / GUI.Simple )-> bottom angle
		-- bg( GUI.Window / GUI.Simple ) -> back grond

		-- lbTitle  [optional gui]( GUI.Text )-> label for show window title
		-- closeBtn [optional gui]( GUI.XXX  )-> close button
		-- helpBtn  [optional gui]( GUI.XXX  )-> help button
		-- minBtn   [optional gui]( GUI.XXX  )-> minimize button
"""

from FrameEx import HFrameEx

class HFlexExWindow( HFrameEx, Window ) :
	def __init__( self, wnd = None ) :
		HFrameEx.__init__( self, wnd )
		Window.__init__( self, wnd )
		self.elmBgTitle_ = wnd.elements.get("wnd_bgTitle")

	def subclass( self, wnd ) :
		HFrameEx.subclass( self, wnd )
		Window.subclass( self, wnd )
		return self

	def dispose( self ) :
		HFrameEx.dispose( self )
		Window.dispose( self )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setWidth( self, width ) :
		old_width = self.width
		HFrameEx._setWidth( self, width )
		if self.pyMinBtn_ :
			rr = old_width - self.pyMinBtn_.right
			self.pyMinBtn_.right = width - rr
		if self.pyHelpBtn_ :
			rr = old_width - self.pyHelpBtn_.right
			self.pyHelpBtn_.right = width - rr
		if self.pyCloseBtn_ :
			rr = old_width - self.pyCloseBtn_.right
			self.pyCloseBtn_.right = width - rr
		if self.elmBgTitle_ :
			scale_util.setFElemCenter(self.elmBgTitle_, width*0.5)
		self.pyLbTitle_.center = width*0.5


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	width = property( HFrameEx._getWidth, _setWidth )


# ----------------------------------------------------------------
# window with title
# ----------------------------------------------------------------

