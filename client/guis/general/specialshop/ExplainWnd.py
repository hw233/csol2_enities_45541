# -*- coding: gb18030 -*-
#
# $Id: FittingPanel.py,fangpengjun Exp $

"""
implement FittingPanel class
# -*- coding: gb18030 -*-
#
# $Id: ExplainWnd.py,fangpengjun Exp $

implement ExplainWnd class
"""

from guis import *
from guis.common.Window import Window
from guis.tooluis.CSTextPanel import CSTextPanel
from guis.controls.ButtonEx import HButtonEx
from guis.controls.Button import Button
from LabelGather import labelGather
import reimpl_specialExplain
import csdefine

class ExplainWnd( Window ):
	__instance=None
	def __init__( self ):
		assert ExplainWnd.__instance is None ,"ExplainWnd instance has been created"
		ExplainWnd.__instance=self
		wnd = GUI.load( "guis/general/specialshop/explainwnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.__initWnd( wnd )
		self.addToMgr( "explainWnd" )

	@staticmethod
	def instance():
		if ExplainWnd.__instance is None:
			ExplainWnd.__instance=ExplainWnd()
		return ExplainWnd.__instance

	@staticmethod
	def getInstance():
		"""
		"""
		return ExplainWnd.__instance

	def __del__(self):
		"""
		just for testing memory leak
		"""
		Window.__del__( self )
		if Debug.output_del_ExplainWnd :
			INFO_MSG( str( self ) )

	def __initWnd( self, wnd ):
		self.__pyTextPanel = CSTextPanel( wnd.expPanel.clipPanel, wnd.expPanel.sbar )
		self.__pyTextPanel.opGBLink = True
		self.__pyTextPanel.text = ""

		self.__pyShutBtn = HButtonEx( wnd.shutBtn )
		self.__pyShutBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyShutBtn.onLClick.bind( self.hide )

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setPyBgLabel( self.__pyShutBtn, "SpecialShop:explainwnd", "shutBtn" )
		labelGather.setLabel( wnd.lbTitle, "SpecialShop:explainwnd", "lbTitle" )
		
	@reimpl_specialExplain.deco_specialExplain
	def __setSpecialExplain( self, pyTextPanel ):
		pyTextPanel.text = labelGather.getText( "SpecialShop:explainwnd", "explain" )

	def show( self, pyOwner = None ):
		self.__setSpecialExplain( self.__pyTextPanel )
		self.top = pyOwner.top
		self.left = pyOwner.right
		Window.show( self, pyOwner )

	def hide( self ):
		self.__pyTextPanel.text = ""
		Window.hide( self )
		self.removeFromMgr()
		ExplainWnd.__instance=None

