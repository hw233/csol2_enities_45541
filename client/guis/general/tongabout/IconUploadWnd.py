# -*- coding: gb18030 -*-
# $Id: StatisWindow.py, fangpengjun Exp $

import os
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ItemsPanel import ItemsPanel
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from AbstractTemplates import Singleton
from config.client import tongIconDsp
from TongIcon import TongIcon
import Function
import ResMgr
import csconst
import GUIFacade
import Function
class IconUploadWnd( Singleton, Window ):

	__instance = None
	
	__def_nums				= 32				# 初始化图标格子
	__cc_cols				= 8				# 选项列数
	__cc_row_space			= 2					# 行距
	__cc_col_space			= 0					# 列距
	
	__icons_path			= "upload"		# 图标保存路径

	def __init__( self ):
		assert IconUploadWnd.__instance is None,"IconUploadWnd instance has been created"
		IconUploadWnd.__instance = self
		wnd = GUI.load( "guis/general/tongabout/tongicon/uploadwnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.__initialize( wnd )
		self.addToMgr( "iconUploadWnd" )
		self.selectedIcon = None

	def __del__(self):
		"""
		just for testing memory leak
		"""
		if Debug.output_del_IconUploadWnd:
			INFO_MSG( str( self ) )

	def dispose( self ) :
		Window.dispose( self )
		self.__class__.releaseInst()
			
	def __initialize( self, wnd ):
		self.__pyRtWarning = CSRichText( wnd.rtWarning )
		self.__pyRtWarning.align = "L"
#		self.__pyRtWarning.maxWidth = 240.0
		self.__pyRtWarning.text = ""

		self.__pyRtSeting = CSRichText( wnd.rtSeting )
		self.__pyRtSeting.align = "L"
		self.__pyRtSeting.text = ""
		
		self.__pyIconsPanel = ItemsPanel( wnd.iconsPanel.clipPanel, wnd.iconsPanel.sbar )
		self.__pyIconsPanel.viewCols = self.__cc_cols
		self.__pyIconsPanel.rowSpace = self.__cc_row_space
		self.__pyIconsPanel.colSpace = self.__cc_col_space
		item = GUI.load( "guis/general/tongabout/tongicon/icon.gui" )
		for index in range( self.__def_nums ):
			item = util.copyGuiTree( item )
			pyItem = TongIcon( item, 0 )
			pyItem.index = index
			pyItem.texture = ""
			self.__pyIconsPanel.addItem( pyItem )
		
		self.__pyBtnUpload = HButtonEx( wnd.btnUpload )
		self.__pyBtnUpload.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnUpload.enable = False
		self.__pyBtnUpload.onLClick.bind( self.__onUpload )
		labelGather.setPyBgLabel( self.__pyBtnUpload, "TongAbout:TongIcon", "btnUpload" )
		
		self.__pyBtnShut = HButtonEx( wnd.btnShut )
		self.__pyBtnShut.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnShut.onLClick.bind( self.__onShut )
		labelGather.setPyBgLabel( self.__pyBtnShut, "TongAbout:TongIcon", "btnShut" )
		
		labelGather.setLabel( wnd.lbTitle, "TongAbout:TongIcon", "lbTitle" )
		labelGather.setLabel( wnd.iconsPanel.bgTitle.stTitle, "TongAbout:TongIcon", "tongIcon" )
	
	# ---------------------------------------------------------------
	# private
	# ---------------------------------------------------------------
	def __initIcons( self ):
		rootPath = os.getcwd() + "\\res\\"
		fullPath = rootPath + self.__icons_path.replace( "/", "\\" )
		dirExits = os.path.exists( fullPath ) #默认图标文件夹是否存在
		files = []
		if not dirExits: #不存在，则创建
			os.mkdir( fullPath )
		else:
			ResMgr.purge( self.__icons_path )
			files = Function.searchFile( self.__icons_path, ".bmp" )
		for path in files:
			iconString = Function.getIconStringByPath( path )
			if len( iconString ) > 4500:	# 图片过大
				files.remove( path )			
		item = GUI.load( "guis/general/tongabout/tongicon/icon.gui" )
		for index, path in enumerate( files ):
			if index < self.__def_nums:
				pyItem = self.__pyIconsPanel.pyItems[index]
				pyItem.path = path
				pyItem.texture = path
			else:
				item = util.copyGuiTree( item )
				pyItem = TongIcon( item, 0 )
				pyItem.index = index
				pyItem.path = path
				pyItem.texture = path
				self.__pyIconsPanel.addItem( pyItem )
	
	def __onUpload( self ):
		if self.selectedIcon is None:return
		path = self.selectedIcon.path
		BigWorld.player().submitTongSign( path )
		
	def __getItemsCount( self ):
		itemsCount = 0
		for item in self.__pyIconsPanel.pyItems :
			if item.texture != "" :
				itemsCount += 1
		return itemsCount
	
	def __onShut( self ):
		self.hide()
	# ---------------------------------------------------------------
	# public
	# ---------------------------------------------------------------
	def onIconSelected( self, index ):
		self.__pyBtnUpload.enable = index != -1
		for pyIcon in self.__pyIconsPanel.pyItems:
			pyIcon.selected = pyIcon.index == index
			if pyIcon.index != index:continue
			self.selectedIcon = pyIcon
	
	def onTongSignChange( self, role, path, isShow ):
		self.__pyBtnUpload.enable = False

	def show( self ):
		dspDatas = tongIconDsp.Datas
		warningText = dspDatas.get( "warning", "" )
		self.__pyRtWarning.text = PL_Font.getSource( warningText, fc = ( 230, 227, 185 ) )
		setingText = dspDatas.get( "seting0", "" )
		self.__pyRtSeting.text = PL_Font.getSource( setingText, fc = ( 230, 227, 185 ) )
		self.__initIcons()
		if self.__getItemsCount() > 0 :
			addingText = dspDatas.get( "adding", "" )
			self.__pyRtSeting.text += PL_Font.getSource( addingText, fc = (230,227, 185) )
		distance = csconst.COMMUNICATE_DISTANCE
		target=GUIFacade.getGossipTarget()
		if hasattr( target, "getRoleAndNpcSpeakDistance" ):
			distance = target.getRoleAndNpcSpeakDistance()
		self.__trapID = BigWorld.addPot(target.matrix,distance, self.__onEntitiesTrapThrough )
		Window.show( self )
	
	def hide( self ):
		for pyIcon in self.__pyIconsPanel.pyItems:
			pyIcon.texture = ""
			pyIcon.selected = False
			if pyIcon.index >= self.__def_nums:
				self.__pyIconsPanel.removeItem( pyIcon )
		self.__pyBtnUpload.enable = False
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
		if IconUploadWnd.__instance is None:
			IconUploadWnd.__instance = IconUploadWnd()
		return IconUploadWnd.__instance

	@staticmethod
	def getInstance():
		"""
		"""
		return IconUploadWnd.__instance

	@classmethod
	def __onShowIconUpload( SELF ):
		SELF.inst.show()
		
	@classmethod
	def __onIconSelected( SELF, index ):
		SELF.inst.onIconSelected( index )

	@classmethod
	def __onTongSignChange( SELF, role, path, isShow ):
		SELF.inst.onTongSignChange( role, path, isShow )

	__triggers = {}
	@staticmethod
	def registerEvents() :
		SELF = IconUploadWnd
		SELF.__triggers["EVT_ON_TOGGLE_TONG_SUBMIT_TONG_SIGN"] = SELF.__onShowIconUpload
		SELF.__triggers["EVT_ON_TONGICON_SELECTED"] = SELF.__onIconSelected
		SELF.__triggers["EVT_ON_TOGGLE_HAS_TONG_SIGN"] = SELF.__onTongSignChange

		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )

	@classmethod
	def onEvent( SELF, macroName, *args ) :
		SELF.__triggers[macroName]( *args )

IconUploadWnd.registerEvents()
