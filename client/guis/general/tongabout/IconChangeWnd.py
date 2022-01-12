# -*- coding: gb18030 -*-
# $Id: IconChangeWnd.py, fangpengjun Exp $

from guis import *
import os
import Function
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.common.Window import Window
from guis.controls.Control import Control
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ItemsPanel import ItemsPanel
from AbstractTemplates import Singleton
from config.client import tongIconDsp
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from TongIcon import TongIcon
import csconst
import GUIFacade
import ResMgr

TONG_RECOM_ICON		= 1 #推荐图标
TONG_CLASSIC_ICON	= 2 #经典图标

class IconChangeWnd( Singleton, Window ):

	__instance = None
	
	__def_nums				= 32				# 默认图标数
	__cc_cols				= 8				# 选项列数
	__cc_row_space			= 2					# 行距
	__cc_col_space			= 0					# 列距

	__icon_paths = "maps/tong_signs/"
	
	def __init__( self ):
		assert IconChangeWnd.__instance is None,"IconChangeWnd instance has been created"
		IconChangeWnd.__instance = self
		wnd = GUI.load( "guis/general/tongabout/tongicon/changewnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.__initialize( wnd )
		self.addToMgr( "iconChangeWnd" )
		self.pyTongIcon = None
	
	def __del__( self ):
		"""
		just for testing memory leak
		"""
		if Debug.output_del_IconChoiceWnd:
			INFO_MSG( str( self ) )
	
	def dispose( self ) :
		Window.dispose( self )
		self.__class__.releaseInst()
	
	def __initialize( self, wnd ):
		self.__pyRecomIncos = ItemsPanel( wnd.recomIcons.clipPanel, wnd.recomIcons.sbar )
		self.__pyRecomIncos.viewCols = self.__cc_cols
		self.__pyRecomIncos.rowSpace = self.__cc_row_space
		self.__pyRecomIncos.colSpace = self.__cc_col_space
		item = GUI.load( "guis/general/tongabout/tongicon/icon.gui" )
		for index in range( self.__def_nums ):
			item = util.copyGuiTree( item )
			pyItem = TongIcon( item, TONG_RECOM_ICON )
			pyItem.index = index
			pyItem.texture = ""
			self.__pyRecomIncos.addItem( pyItem )
		
		self.__pyClassicIncos = ItemsPanel( wnd.classicIcons.clipPanel, wnd.classicIcons.sbar )
		self.__pyClassicIncos.viewCols = self.__cc_cols
		self.__pyClassicIncos.rowSpace = self.__cc_row_space
		self.__pyClassicIncos.colSpace = self.__cc_col_space
		for index in range( self.__def_nums ):
			item = util.copyGuiTree( item )
			pyItem = TongIcon( item, TONG_CLASSIC_ICON )
			pyItem.index = index
			pyItem.texture = ""
			pyItem.reqMoney = 50
			self.__pyClassicIncos.addItem( pyItem )
		
		self.__pyRtSeting = CSRichText( wnd.rtSeting )
		self.__pyRtSeting.align = "L"
#		self.__pyRtSeting.maxWidth = 210.0
		self.__pyRtSeting.text = ""
	
		self.__pyBtnChoice = HButtonEx( wnd.btnChoose )
		self.__pyBtnChoice.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnChoice.enable = False
		self.__pyBtnChoice.onLClick.bind( self.__onChangeIcon )
		labelGather.setPyBgLabel( self.__pyBtnChoice, "TongAbout:TongIcon", "btnChoose" )
		
		self.__pyBtnShut = HButtonEx( wnd.btnShut )
		self.__pyBtnShut.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnShut.onLClick.bind( self.__onShut )
		labelGather.setPyBgLabel( self.__pyBtnShut, "TongAbout:TongIcon", "btnShut" )
	
		labelGather.setLabel( wnd.lbTitle, "TongAbout:TongIcon", "lbTitle" )
		labelGather.setLabel( wnd.classicIcons.bgTitle.stTitle, "TongAbout:TongIcon", "classicIcon" )
		labelGather.setLabel( wnd.recomIcons.bgTitle.stTitle, "TongAbout:TongIcon", "commendIcon" )
	
	def __onChangeIcon( self ):
		if self.pyTongIcon is None:return
		type = self.pyTongIcon.type
		reqMoney = self.pyTongIcon.reqMoney
		path = self.pyTongIcon.path
		BigWorld.player().changeTongSign( True, reqMoney, path )
	
	def __onShut( self ):
		self.hide()
	
	def __initIcons( self ):
		iconPaths = {}
		iconPaths[TONG_RECOM_ICON] = Function.searchFile( self.__icon_paths, ".dds" )
		iconPaths[TONG_CLASSIC_ICON] = Function.searchFile( self.__icon_paths, ".texanim" )
		ResMgr.purge( self.__icon_paths )
		item = GUI.load( "guis/general/tongabout/tongicon/icon.gui" )
		for type, files in iconPaths.items():
			pyTongIcons = None
			reqMoney = 0
			if type == TONG_RECOM_ICON:
				pyTongIcons = self.__pyRecomIncos
			else:
				reqMoney = 500000
				pyTongIcons = self.__pyClassicIncos
			for index, path in enumerate( files ):
				if index < self.__def_nums:
					pyItem = pyTongIcons.pyItems[index]
					pyItem.path = path
					pyItem.texture = path
					pyItem.reqMoney = reqMoney
				else:
					item = util.copyGuiTree( item )
					pyItem = TongIcon( item, type )
					pyItem.index = index
					pyItem.path = path
					pyItem.texture = path
					pyItem.reqMoney = reqMoney
					pyTongIcons.addItem( pyItem )
	# ---------------------------------------------------------------
	# public
	# ---------------------------------------------------------------
	def onRecomIconSel( self, index ):
		selPyIcon = self.__pyRecomIncos.pyItems[index]
		tongSign = BigWorld.player().tong_sign_md5.split( "." )[0]
		texturePath = selPyIcon.texture.split( "." )[0]
		self.__pyBtnChoice.enable = index != -1 and tongSign != texturePath
		for pyIcon in self.__pyRecomIncos.pyItems:
			pyIcon.selected = pyIcon.index == index
			if not pyIcon.selected:continue
			self.pyTongIcon = pyIcon
		for pyIcon in self.__pyClassicIncos.pyItems:
			if pyIcon.selected:
				pyIcon.selected = False
	
	def onClasicIconSel( self, index ):
		selPyIcon = self.__pyClassicIncos.pyItems[index]
		tongSign = BigWorld.player().tong_sign_md5.split( "." )[0]
		texturePath = selPyIcon.texture.split( "." )[0]
		self.__pyBtnChoice.enable = index != -1 and tongSign != texturePath
		for pyIcon in self.__pyClassicIncos.pyItems:
			pyIcon.selected = pyIcon.index == index
			if not pyIcon.selected:continue
			self.pyTongIcon = pyIcon
		for pyIcon in self.__pyRecomIncos.pyItems:
			if pyIcon.selected:
				pyIcon.selected = False
	
	def onTongSignChange( self, role, path, isShow ):
		self.__pyBtnChoice.enable = False
		for pyIcon in self.__pyRecomIncos.pyItems:
			texturePath = pyIcon.texture.split( "." )[0]
			if texturePath != path.split( "." )[0]:continue
			pyIcon.selected = False

		for pyIcon in self.__pyClassicIncos.pyItems:
			texturePath = pyIcon.texture.split( "." )[0]
			if texturePath != path.split( "." )[0]:continue
			pyIcon.selected = False

	def show( self ):
		dspDatas = tongIconDsp.Datas
		setingText = dspDatas.get( "seting1", "" )
		self.__pyRtSeting.text = PL_Font.getSource( setingText, fc = ( 230, 227, 185 ) )
		self.__initIcons()
		distance = csconst.COMMUNICATE_DISTANCE
		target=GUIFacade.getGossipTarget()
		if hasattr( target, "getRoleAndNpcSpeakDistance" ):
			distance = target.getRoleAndNpcSpeakDistance()
		self.__trapID = BigWorld.addPot(target.matrix,distance, self.__onEntitiesTrapThrough )
		Window.show( self )
	
	def hide( self ):
		for pyIcon in self.__pyRecomIncos.pyItems:
			pyIcon.texture = ""
			pyIcon.selected = False
			if pyIcon.index >= self.__def_nums:
				self.__pyRecomIncos.removeItem( pyIcon )
		for pyIcon in self.__pyClassicIncos.pyItems:
			pyIcon.texture = ""
			pyIcon.selected = False
			if pyIcon.index >= self.__def_nums:
				self.__pyClassicIncos.removeItem( pyIcon )
		self.__pyBtnChoice.enable = False
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		Window.hide( self )
	
	def onLeaveWorld( self ):
		self.hide( )

	def __onEntitiesTrapThrough( self,isEnter, handle ):
		if  not isEnter:
			self.hide()
		
	@staticmethod
	def instance():
		"""
		get the exclusive instance of AutoFightWindow
		"""
		if IconChangeWnd.__instance is None:
			IconChangeWnd.__instance = IconChangeWnd()
		return IconChangeWnd.__instance

	@staticmethod
	def getInstance():
		"""
		"""
		return IconChangeWnd.__instance
	
	@classmethod
	def __onShowIconChoice( SELF ):
		SELF.inst.show()
		
	@classmethod
	def __onRecomIconSel( SELF, index ):
		SELF.inst.onRecomIconSel( index )

	@classmethod
	def __onClasicIconSel( SELF, index ):
		SELF.inst.onClasicIconSel( index )

	@classmethod
	def __onTongSignChange( SELF, role, path, isShow ):
		SELF.inst.onTongSignChange( role, path, isShow )
		
	__triggers = {}
	@staticmethod
	def registerEvents() :
		SELF = IconChangeWnd
		SELF.__triggers["EVT_ON_TOGGLE_TONG_CHANGE_TONG_SIGN"] = SELF.__onShowIconChoice
		SELF.__triggers["EVT_ON_RECOM_TONGICON_SELECTED"] = SELF.__onRecomIconSel
		SELF.__triggers["EVT_ON_CLASSIC_TONGICON_SELECTED"] = SELF.__onClasicIconSel
		SELF.__triggers["EVT_ON_TOGGLE_HAS_TONG_SIGN"] = SELF.__onTongSignChange

		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )

	@classmethod
	def onEvent( SELF, macroName, *args ) :
		SELF.__triggers[macroName]( *args )

IconChangeWnd.registerEvents()
