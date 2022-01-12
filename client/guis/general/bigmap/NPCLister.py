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
		self.__pyLPNPCs = ODListPanel(wnd.lvNPCs.clipPanel,wnd.lvNPCs.sbar)		#NPC�б����
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
		
		self.__pyTBSearch = TextBox( wnd.tbSearch.box )								# NPC ���������

		self.__pyBtnSearch = HButtonEx( wnd.btnSearch )							# ������ť
		self.__pyBtnSearch.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnSearch.onLClick.bind( self.__onBtnSearchClick )
		self.setOkButton( self.__pyBtnSearch )									# ���س���ʱ�����ڵ�������ť
		self.__pyBtnShow = HButtonEx( wnd.btnShow )								# ��ʾ��ť
		self.__pyBtnShow.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnShow.onLClick.bind( self.__onBtnShowClick )
		self.__pyBtnClose = HButtonEx( wnd.btnClose )								# �رհ�ť
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
		# ���ñ�ǩ
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
		��ʼ�� NPC ѡ��
		
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
		�ػ� NPC ѡ��
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
		������ť�����ʱ����
		"""
		npcName = self.__pyTBSearch.text.strip()
		if npcName == "" :
			# "������Ҫ������ NPC ���֣�"
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
			# "NPC��%s �����ڣ�"
			showAutoHideMessage( 3.0, mbmsgs[0x0222] % npcName, "", pyOwner = self )
		else :
			self.__pyLPNPCs.selIndex = selIndex
		self.__pyTBSearch.tabStop = False

	def __onBtnShowClick( self ) :
		"""
		����ʾ����ť�����ʱ������
		"""
		selItem = self.__pyLPNPCs.selItem
		if selItem is None :
			# "��ѡ��һ�� NPC��"
			showAutoHideMessage( 3.0, 0x0223, "", pyOwner = self )
		else :
			self.pyOwner.showNPC( selItem[1] )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onLeaveWorld( self ) :
		"""
		����뿪����ʱ������
		"""
		self.hide()

	@classmethod
	def show( SELF, pyOwner, area ) :
		"""
		��ʾ����
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
			point = npc.position[0], npc.position[2]		# NPC λ��
			subArea = area.getSubArea( point )				# NPC ����������
			areaName = area.name							# NPC ������������
			if subArea : areaName = subArea.name			# ������������У�����ʾ����������
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
