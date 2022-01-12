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
from Frame import HVFrame

# --------------------------------------------------------------------
# window can resize on horizontal and vertical
# --------------------------------------------------------------------
class HVFlexWindow( HVFrame, Window ) :
	def __init__( self, wnd = None ) :
		HVFrame.__init__( self, wnd )
		Window.__init__( self, wnd )

	def subclass( self, wnd ) :
		HVFrame.subclass( self, wnd )
		Window.subclass( self, wnd )
		return self

	def dispose( self ) :
		HVFrame.dispose( self )
		Window.dispose( self )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setWidth( self, width ) :
		old_width = self.width
		HVFrame._setWidth( self, width )
		if self.pyMinBtn_ is not None :
			rr = old_width - self.pyMinBtn_.right
			self.pyMinBtn_.right = width - rr
		if self.pyHelpBtn_ is not None :
			rr = old_width - self.pyHelpBtn_.right
			self.pyHelpBtn_.right = width - rr
		if self.pyCloseBtn_ is not None :
			rr = old_width - self.pyCloseBtn_.right
			self.pyCloseBtn_.right = width - rr

	def _setSize( self, size ) :
		self.width = size[0]
		self.height = size[1]


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	width = property( HVFrame._getWidth, _setWidth )
	size = property( HVFrame._getSize, _setSize )


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


from Frame import VFrame

class VFlexWindow( VFrame, Window ) :
	def __init__( self, wnd = None ) :
		VFrame.__init__( self, wnd )
		Window.__init__( self, wnd )

	def subclass( self, wnd ) :
		VFrame.subclass( self, wnd )
		Window.subclass( self, wnd )
		return self

	def dispose( self ) :
		VFrame.dispose( self )
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

from Frame import HFrame

class HFlexWindow( HFrame, Window ) :
	def __init__( self, wnd = None ) :
		HFrame.__init__( self, wnd )
		Window.__init__( self, wnd )

	def subclass( self, wnd ) :
		HFrame.subclass( self, wnd )
		Window.subclass( self, wnd )
		return self

	def dispose( self ) :
		HFrame.dispose( self )
		Window.dispose( self )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setWidth( self, width ) :
		old_width = self.width
		HFrame._setWidth( self, width )
		if self.pyMinBtn_ is not None :
			rr = old_width - self.pyMinBtn_.right
			self.pyMinBtn_.right = width - rr
		if self.pyHelpBtn_ is not None :
			rr = old_width - self.pyHelpBtn_.right
			self.pyHelpBtn_.right = width - rr
		if self.pyCloseBtn_ is not None :
			rr = old_width - self.pyCloseBtn_.right
			self.pyCloseBtn_.right = width - rr


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	width = property( HFrame._getWidth, _setWidth )
