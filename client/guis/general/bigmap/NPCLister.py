# -*- coding: gb18030 -*-
#
# $Id: NPCLister.py,v 1.15 2008-06-27 03:16:49 huangyongwei Exp $

"""
implement full map class

2008.01.09 : wirten by huangyongwei
"""

from AbstractTemplates import Singleton
from guis import *
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.controls.ODListPanel import ODListPanel
from guis.controls.ListItem import ODTextColumn
from guis.controls.StaticText import StaticText
from guis.controls.TextBox import TextBox
from config.client.msgboxtexts import Datas as mbmsgs
from LabelGather import labelGather

class NPCLister( Singleton, Window ) :
	__cc_col_lefts = ( 2, 68, 133, 217 )
	__cc_col_widths = ( 66, 62, 80, 93 )

	def __init__( self ) :
		Singleton.__init__( self )
		wnd = GUI.load( "guis/general/bigmap/npclister/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.__initialize( wnd )
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "TOP"
		self.addToMgr( "bigMapNPCLister" )

	def __del__( self ) :
		Window.__del__( self )
		if Debug.output_del_BigMapNPCLister :
			INFO_MSG( str( self ) )

	def __initialize( self, wnd ) :
		self.__pyLPNPCs = ODListPanel(wnd.lvNPCs.clipPanel,wnd.lvNPCs.sbar)		#NPC列表版面
		self.__pyLPNPCs.onViewItemInitialized.bind(self.__onLPNPCsInit)
		self.__pyLPNPCs.onDrawItem.bind(self.__onDrawNPCItem)
		self.__pyLPNPCs.ownerDraw = True
		self.__pyLPNPCs.itemHeight = 23
#		self.__pyLPNPCs.orderable = True
#		self.__pyLPNPCs.autoSearchHeaders()
#		self.__pyLPNPCs.ownerDraw = True
#		self.__pyLPNPCs.onViewItemInitialized.bind( self.__onLPNPCsInit )
#		self.__pyLPNPCs.onDrawItem.bind( self.__onDrawNPCItem )
		self.__pysSTKeyWord = StaticText(wnd.stKey)
		
		self.__pyTBSearch = TextBox( wnd.tbSearch.box )								# NPC 名字输入框

		self.__pyBtnSearch = HButtonEx( wnd.btnSearch )							# 搜索按钮
		self.__pyBtnSearch.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnSearch.onLClick.bind( self.__onBtnSearchClick )
		self.setOkButton( self.__pyBtnSearch )									# 按回车键时，等于点击这个按钮
		self.__pyBtnShow = HButtonEx( wnd.btnShow )								# 显示按钮
		self.__pyBtnShow.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnShow.onLClick.bind( self.__onBtnShowClick )
		self.__pyBtnClose = HButtonEx( wnd.btnClose )								# 关闭按钮
		self.__pyBtnClose.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnClose.onLClick.bind( self.hide )
		
		self.__pyHeaders = []
		for name, item in wnd.lvNPCs.children:
			if name.startswith( "head_"):
				index = int( name.split( "_" )[1] )
				pyHeader = HButtonEx( item )
				pyHeader.index = index
				self.__pyHeaders.append( pyHeader )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyBtnSearch, "BigMap:NPCLister", "btnSearch" )
		labelGather.setPyBgLabel( self.__pyBtnShow, "BigMap:NPCLister", "btnShow" )
		labelGather.setPyBgLabel( self.__pyBtnClose, "BigMap:NPCLister", "btnClose" )
		labelGather.setLabel( self.gui.lbTitle, "BigMap:NPCLister", "lbTitle" )
		labelGather.setPyLabel( self.__pysSTKeyWord, "BigMap:NPCLister", "stKey" )
		
		for idx, pyHeader in enumerate( self.__pyHeaders ) :
			labelGather.setPyBgLabel( pyHeader, "BigMap:NPCLister", "lvNPCs_head_%i" % pyHeader.index )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onLPNPCsInit( self, pyViewItem ) :
		"""
		初始化 NPC 选项
		
		"""
		for idx, pyHeader in enumerate( self.__pyHeaders ) :
			pyCol = ODTextColumn( pyViewItem )
			pyViewItem.addPyChild( pyCol )
			pyCol.left = pyHeader.left + 2
			pyCol.maxWidth = pyHeader.width - 4
			pyCol.middle = pyViewItem.height * 0.5
			setattr( pyViewItem, "pyCol%i" % idx, pyCol )
#			labelGather.setPyBgLabel( pyHeader, "BigMap:NPCLister", "lvNPCs_head_%i" % pyHeader.index )

	def __onDrawNPCItem( self, pyViewItem ) :
		"""
		重画 NPC 选项
		"""
		if pyViewItem.selected :
			fcolor = self.__pyLPNPCs.itemSelectedForeColor
			bcolor = self.__pyLPNPCs.itemSelectedBackColor
		elif pyViewItem.highlight :
			fcolor = self.__pyLPNPCs.itemHighlightForeColor
			bcolor = self.__pyLPNPCs.itemHighlightBackColor
		else :
			fcolor = self.__pyLPNPCs.itemCommonForeColor
			bcolor = self.__pyLPNPCs.itemCommonBackColor
		pyViewItem.color = bcolor
		for idx, col in enumerate( pyViewItem.listItem[0] ) :
			pyCol = getattr( pyViewItem, "pyCol" + str( idx ) )
			pyCol.color = fcolor
			pyCol.text = col


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def __onBtnSearchClick( self ) :
		"""
		搜索按钮被点击时调用
		"""
		npcName = self.__pyTBSearch.text.strip()
		if npcName == "" :
			# "请输入要搜索的 NPC 名字！"
			showAutoHideMessage( 3.0, 0x0221, "", pyOwner = self )
			self.__pyTBSearch.tabStop = True
			return
		items = self.__pyLPNPCs.items
		selIndex = -1
		for index, item in enumerate( items ) :
			if item[0][0] == npcName :
				selIndex = index
				break
		if selIndex < 0 :
			# "NPC：%s 不存在！"
			showAutoHideMessage( 3.0, mbmsgs[0x0222] % npcName, "", pyOwner = self )
		else :
			self.__pyLPNPCs.selIndex = selIndex
		self.__pyTBSearch.tabStop = False

	def __onBtnShowClick( self ) :
		"""
		“显示”按钮被点击时被调用
		"""
		selItem = self.__pyLPNPCs.selItem
		if selItem is None :
			# "请选择一个 NPC！"
			showAutoHideMessage( 3.0, 0x0223, "", pyOwner = self )
		else :
			self.pyOwner.showNPC( selItem[1] )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onLeaveWorld( self ) :
		"""
		玩家离开世界时被调用
		"""
		self.hide()

	@classmethod
	def show( SELF, pyOwner, area ) :
		"""
		显示窗口
		"""
		pyWnd = SELF()
		pyWnd.__pyLPNPCs.clearItems()
		if area is None : return
		player = BigWorld.player()
		spaceLabel = area.spaceLabel
		curSpaceLabel = player.getSpaceLabel()
		posY = 0
		if curSpaceLabel == spaceLabel:
			posY = player.position[1]
		viewWholeArea = area.wholeArea
		isViewSky = viewWholeArea.isSkyArea
		npcs = rds.mapMgr.getNPCs( spaceLabel, curSpaceLabel, isViewSky, 4, posY )
		for npc in npcs.itervalues() :
			point = npc.position[0], npc.position[2]		# NPC 位置
			subArea = area.getSubArea( point )				# NPC 所在子区域
			areaName = area.name							# NPC 所在区域名称
			if subArea : areaName = subArea.name			# 如果在子区域中，则显示子区域名称
			strPos = "%d:%d" % ( point )
			item = ( npc.name, npc.title, areaName, strPos ), npc
			pyWnd.__pyLPNPCs.addItem( item )

		pyWnd.right = pyOwner.width - 82
		pyWnd.top = 50
		Window.show( pyWnd, pyOwner )

	@classmethod
	def hide( SELF ) :
		if not SELF.insted : return
		pyWnd = SELF.inst
		pyWnd.__class__.releaseInst()
		Window.hide( pyWnd )
