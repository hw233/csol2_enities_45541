# -*- coding: gb18030 -*-

from guis.uidefine import UIState
from guis.controls.Button import Button
from guis.common.UIStatesTab import HStatesTabEx

# 这类按钮拥有HFrameEx的框架
# 通过设置各个element的mapping来实现不同状态下的表现
# 结构如下：
#
#	GUI.TextureFrame :
#	children :
#		lbText
#	elements :
#		frm_l, frm_bg, fem_r
# 三个element必须具有一致的 mapping state


class HButtonEx( Button, HStatesTabEx ) :
	"""
	GUI.TextureFrame :
	children :
		lbText
	elements :
		frm_l, frm_bg, fem_r
	"""
	def __init__( self, button, pyBinder = None ) :
		Button.__init__( self, button, pyBinder )
		HStatesTabEx.__init__( self, button )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def setStateView_( self, state ) :
		"""
		设置指定状态下的外观表现
		"""
		if state == UIState.DISABLE :
			self.setDisableView_()
			return
		Button.setStateView_( self, state )
		self.exMappings = self.exMappingsMap_[state]

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setExStatesMapping( self, stMode ) :
		HStatesTabEx.setExStatesMapping( self, stMode )
		if self.enable :
			self.setState( UIState.COMMON )