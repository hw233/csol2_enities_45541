#-*- coding: gb18030 -*-

import GUI
from guis.UIFixer import uiFixer
from guis.common.RootGUI import RootGUI
from guis.controls.StaticText import StaticText
from guis.controls.CircleShader import CircleShader
from AbstractTemplates import Singleton

class YaoqiGourd( RootGUI, Singleton ):
	"""
	妖气葫芦
	"""
	def __init__( self ):
		gourd = GUI.load( "guis/otheruis/gourd/wnd.gui" )
		uiFixer.firstLoadFix( gourd )
		RootGUI.__init__( self, gourd )
		self.escHide_ = False
		self.v_dockStyle = "TOP"
		self.h_anchor = "LEFT"
		self.__fires = []
		self.__initialize( gourd )
		self.__onYapqiChanged( 0.0 )
		self.addToMgr()
	
	def __initialize( self, gourd ):
		self.__pySTPerct = StaticText( gourd.stPerct )
		self.__pySTPerct.font = "blueitalic.font"
		self.__pySTPerct.charSpace = -17
		self.__pySTPerct.text = ""
		
		self.__pyYaoqiBar = CircleShader( gourd.yq_ring )
		self.__pyYaoqiBar.deasil = True						#逆时针裁剪
		
	
	def __onYapqiChanged( self, percent ):
		"""
		妖气值变化
		"""
		self.__pyYaoqiBar.value = min(0.999, percent )		# Circle有个bug，当值是1时，ui会看不到
		self.__pySTPerct.text = "%d:" %int(min(percent, 1.0)*100)
		if percent < 1.0:
			self.__pySTPerct.left = 30.0
			if percent < 0.1:
				self.__pySTPerct.left = 37.0
		else:
			self.__pySTPerct.left = 22.0
	
	def onLeaveWorld( self ):
		self.__class__.cls_trigger( False )

	@classmethod
	def cls_update( CLS, percent ):
		if CLS.insted:
			CLS.inst.__onYapqiChanged( percent )

	@classmethod
	def cls_trigger( CLS, visible ):
		if visible:
			if not CLS.inst.visible:
				CLS.inst.visible = True
		elif CLS.insted:
			CLS.inst.dispose()
			CLS.releaseInst()