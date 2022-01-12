# -*- coding: gb18030 -*-
#
# implement navigation window
# 自动寻路NPC坐标查询窗口
# written by gjx 2009-05-07
#

import GUIFacade
import csdefine
import csstatus
import sys
from guis import *
from guis.common.GUIBaseObject import GUIBaseObject
from guis.controls.StaticLabel import StaticLabel
from guis.controls.Control import Control
from guis.controls.ODListPanel import ODListPanel
from guis.controls.ButtonEx import HButtonEx
from guis.common.Window import Window
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPanel
from guis.controls.TabCtrl import TabPage
from guis.controls.TextBox import TextBox
from guis.tooluis.fulltext.FullText import FullText
from config.client.msgboxtexts import Datas as BoxMsgDatas
from SpaceDoorMgr import SpaceDoorMgr
from LabelGather import labelGather
sdMgr = SpaceDoorMgr.instance()


class NavigateWindow( Window ) :

	__instance=None

	def __init__( self ) :
		assert NavigateWindow.__instance is  None
		wnd = GUI.load( "guis/general/navigatewnd/navigatewnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.addToMgr( "navigateWindow" )
		self.__preSpaceLabel = ""										# 所在地图
		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()


	@staticmethod
	def instance():
		"""
		to get the exclusive instance of NavigateWindow
		"""
		if NavigateWindow.__instance is None:
			NavigateWindow.__instance=NavigateWindow()
		return NavigateWindow.__instance


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		self.__pyFlyBtn = HButtonEx( wnd.flyBtn )							# 使用引路蜂传送按钮
		self.__pyFlyBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyFlyBtn.onLClick.bind( self.__flyToNPC )

		self.__pyNavigateBtn = HButtonEx( wnd.runBtn )						# 自动寻路至NPC按钮
		self.__pyNavigateBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyNavigateBtn.onLClick.bind( self.__runToNPC )

		self.__pyNameBtn = HButtonEx( wnd.tc.header.header_0 )
		self.__pyNameBtn.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyNameBtn.onLClick.bind( self.__onSortByName )			# 按名称排序

		self.__pyNicknameBtn = HButtonEx( wnd.tc.header.header_1 )
		self.__pyNicknameBtn.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyNicknameBtn.onLClick.bind( self.__onSortByNickname )	# 按名称排序

		self.__pySearchText = TextBox( wnd.boxSearch.box )					# 搜索输入框
		self.__pySearchBtn = HButtonEx( wnd.searchBtn )					# 搜索按钮
		self.__pySearchBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pySearchBtn.onLClick.bind( self.__onSearch )
		self.setOkButton( self.__pySearchBtn )

		self.__infoPanel = InfoPanel( wnd.tc, self )				# 信息面板

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setPyBgLabel( self.__pySearchBtn, "NavigateWindow:main", "searchBtn" )
		labelGather.setPyBgLabel( self.__pyNicknameBtn, "NavigateWindow:main", "nicknameBtn" )
		labelGather.setPyBgLabel( self.__pyNavigateBtn, "NavigateWindow:main", "runBtn" )
		labelGather.setPyBgLabel( self.__pyFlyBtn, "NavigateWindow:main", "flyBtn" )
		labelGather.setPyBgLabel( self.__pyNameBtn, "NavigateWindow:main", "nameBtn" )
		labelGather.setLabel( wnd.lbTitle, "NavigateWindow:main", "lbTitle" )
		labelGather.setLabel( wnd.stKeyword, "NavigateWindow:main", "stKeyword" )

	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_HIDE_NAVIGATE_WINDOW"] = self.hide
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )


	def __del__(self):
		"""
		just for testing memory leak
		"""
		Window.__del__( self )
		if Debug.output_del_NavigateWindow :
			INFO_MSG( str( self ) )

	# -------------------------------------------------
	def __loadNPCsInfo( self ) :
		"""
		导入NPC信息
		"""
		player = BigWorld.player()
		spaceLabel = player.getSpaceLabel()								# 检查是否已转移到另一地图，
		self.__preSpaceLabel = spaceLabel								# 重设当前所在地图
		self.__infoPanel.reset()										# 清空旧信息
		spaceNPCs = rds.npcDatasMgr.getNPCs( spaceLabel )				# 获取当前地图的所有NPC
		for npc in spaceNPCs.itervalues() :								# 将所在地图的NPC添加到界面
			npcID = npc.id
			infoItem = ( npc.name, npc.nickname, ( npc.getPosition( spaceLabel ), 8 ), npcID )
			if str( npcID )[0] in [ "1" ] :								# 功能NPC
				self.__infoPanel.addNPCItem( infoItem )
			elif str( npcID )[0] in [ "2" ] :							# 非功能NPC
				self.__infoPanel.addMonsterItem( infoItem )
		spaceDoors = sdMgr.getSpaceDoorInf( spaceLabel )				# 添加传送门信息
		for sdData in spaceDoors :
			sdName = sdData.get( "uname", "" )
			if sdName.strip() == "" : continue
			sdNickname = sdData.get( "nickname", "" )
			sdPosition = sdData.get( "position", (0,0,0) )
			sdClassName = sdData.get( "className", "" )
			infoItem = ( sdName, sdNickname, ( sdPosition, 0 ), sdClassName )
			self.__infoPanel.addNPCItem( infoItem )
		self.__infoPanel.reSort()										# 重新排列顺序

	def __onSearch( self ) :
		"""
		按输入的关键字搜索
		"""
		text = self.__pySearchText.text									# 搜索关键字去掉前后空格
		self.__infoPanel.onSearch( text )

	def __onSortByName( self ) :
		"""
		按NPC的名称排序
		"""
		self.__infoPanel.sortByName()

	def __onSortByNickname( self ) :
		"""
		按NPC的简称排序
		"""
		self.__infoPanel.sortByNickname()

	def __runToNPC( self ) :
		"""
		自动寻路
		"""
		self.__infoPanel.onRunToNPC()


	def hide(self):
		"""
		隐藏窗口
		"""
		Window.hide(self)


	def __flyToNPC( self ) :
		"""
		使用引路蜂
		"""
		self.__infoPanel.onFlyToNPC()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onLeaveWorld( self ) :
		self.hide()

	def onEvent( self, macroName, *args ) :
		self.__triggers[ macroName ]( *args )

	def show( self ) :
		if self.__preSpaceLabel!=BigWorld.player().getSpaceLabel():
			self.__loadNPCsInfo()
			self.__infoPanel.resetState()
		Window.show( self )


# --------------------------------------------------------------------
# 一个NPC列表项，由多个InfoItem组成（当前由两个子项组成一个NPC列表项）
# --------------------------------------------------------------------
class NPCItem( GUIBaseObject ) :

	__npc_item = None

	def __init__( self, pyBinder = None ) :
		if NPCItem.__npc_item is None :
			NPCItem.__npc_item = GUI.load( "guis/general/navigatewnd/npcinfoitem.gui" )
		gui = util.copyGuiTree( NPCItem.__npc_item )
		uiFixer.firstLoadFix( gui )
		GUIBaseObject.__init__( self, gui )
		self.__initialize( gui, pyBinder )

	def __initialize( self, gui, pyBinder ) :
		self.__pyName = InfoItem( gui.col_1, pyBinder )
		self.__pyTitle = InfoItem( gui.col_2, pyBinder )
		self.__elements =gui.elements

	def resetText( self, info ) :
		"""
		更新列表项文本
		"""
		self.__pyName.text = info[0]
		self.__pyTitle.text = info[1]

	def resetColor( self, color ) :
		"""
		更新列表项字体颜色
		"""
		self.__pyName.foreColor = color
		self.__pyTitle.foreColor = color

	def setHighLight(self):
		for elem in self.__elements:
			self.__elements[elem].visible=1

	def setCommonLight(self):
		for elem in self.__elements:
			self.__elements[elem].visible=0


# --------------------------------------------------------------------
# NPC单独列表子项，一个NPC列表项由多个子项组成
# --------------------------------------------------------------------
class InfoItem( StaticLabel, Control ) :
	"""
	鼠标进入时文本过长则显示浮动框
	"""
	def __init__( self, item, pyBinder = None ) :
		StaticLabel.__init__( self, item, pyBinder )
		item = StaticLabel.getGui( self )
		Control.__init__( self, item, pyBinder )
		self.focus = False
		self.crossFocus = True

	def onMouseEnter_( self ) :
		"""
		鼠标进入后被调用
		"""
		self.pyBinder.onMouseEnter_()
		Control.onMouseEnter_( self )
		if self.pyText_.width > self.width :
			FullText.show( self, self.pyText_ )
		return True

	# -------------------------------------------------
	def onMouseLeave_( self ) :
		"""
		after mouse left, will be called
		"""
		self.pyBinder.onMouseLeave_()
		Control.onMouseLeave_( self )
		FullText.hide()
		return True


# --------------------------------------------------------------------
# 分页信息面板
# --------------------------------------------------------------------
class SubInfoPanel( TabPanel ) :

	def __init__( self, panel, pyBinder ) :
		TabPanel.__init__( self, panel, pyBinder )
		self.__initialize( panel )

		self.__nameTaxisFlag = True											# 记录名称排序是否反转
		self.__nicknameTaxisFlag = True										# 记录简称排序是否反转


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, panel ) :
		self.__pyInfoList = ODListPanel( panel.infoPanel, panel.scrollBar )	# NPC信息列表
		self.__pyInfoList.onItemLDBClick.bind( self.__onItemLDBClicked )
		self.__pyInfoList.onViewItemInitialized.bind( self.__initListItem )
		self.__pyInfoList.itemHeight = 23
		self.__pyInfoList.ownerDraw = True								# 开启自定义绘制
		self.__pyInfoList.onDrawItem.bind( self.__drawListItem )

	def dispose(self):
		self.__pyInfoList.clearItems()	# NPC信息列表
		self.__pyInfoList=None
		TabPanel.dispose(self)


	def __initListItem( self, pyViewItem ) :
		"""
		初始化添加的NPC列表项
		"""
		pyNPCItem = NPCItem( pyViewItem )
		pyViewItem.pyNPCItem = pyNPCItem
		pyViewItem.addPyChild( pyNPCItem )
		pyNPCItem.left = 0
		pyNPCItem.top = 0

	def __drawListItem( self, pyViewItem ) :
		npcInfo = pyViewItem.listItem
		pyNPCItem = pyViewItem.pyNPCItem
		pyNPCItem.resetText( npcInfo )

		if pyViewItem.selected :							# 选中状态
			pyNPCItem.setHighLight()
			pyNPCItem.resetColor( ( 60, 255, 0, 255 ) )
		elif pyViewItem.highlight :							# 高亮状态（鼠标在其上）
			pyNPCItem.setHighLight()
#			pyNPCItem.resetColor( ( 60, 255, 255, 255 ) )
		else :
			pyNPCItem.setCommonLight()
			pyNPCItem.resetColor( ( 255, 255, 255, 255 ) )

	def __onItemLDBClicked( self, pyItem ) :
		"""
		鼠标双击则自动寻路
		"""
		self.runToNPC()

	def __distillDigital( self, sourceText ) :
		"""
		鉴于策划的特殊要求，此函数用来提取字符串中开头的数字
		遇到第一个不是数字的字符停止提取
		@param	sourceText	: 要提取的字符串
		@type	sourceText	: str
		@reType				: str
		"""
		dstText = ""
		for char in sourceText :
			if char.isdigit() :
				dstText += char
			else :
				break
		if dstText == "" : return sourceText
		return int( dstText )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def flyToNPC( self ) :
		"""
		使用引路蜂
		"""
		npcInfo = self.__pyInfoList.selItem
		if npcInfo is None : return
		player = BigWorld.player()
		items = player.findItemsByIDFromNKCK( 50101003 )
		if items == []:
			items = player.findItemsByIDFromNKCK( 50101002 )
		if items == []:
			player.statusMessage( csstatus.ROLE_HAS_NOT_FIY_ITEM )
			return
		if not player.getState() == csdefine.ENTITY_STATE_FIGHT:
			player.stopMove()											# 必须先停止移动，以保证追踪目标不被清空
			player.cell.flyToNpc( npcInfo[3], 0, items[0].order )
			player.setExpectTarget( npcInfo[3] )						# 设置追踪目标NPC的ID
		else:
			player.statusMessage( csstatus.SKILL_USE_ITEM_WHILE_FIGHTING )
			return
		self.pyBinder.hide()

	def runToNPC( self ) :
		"""
		自动寻路
		"""
		npcInfo = self.__pyInfoList.selItem
		if npcInfo is None : return
		self.pyBinder.hide()
		player = BigWorld.player()
		player.setExpectTarget( npcInfo[3] )							# 设置追踪目标NPC的ID
		player.autoRun( npcInfo[2][0], npcInfo[2][1] )

	def addItem( self, info ) :
		self.__pyInfoList.addItem( info )

	def resetState( self ) :
		self.__pyInfoList.resetState()

	def sortByName( self ) :
		"""
		按名称排序
		"""
		def customCmp( n1, n2 ) :
			spaceDoorLabel = labelGather.getText( "NavigateWindow:main", "spaceDoor" )
			if spaceDoorLabel in n1[1] and spaceDoorLabel not in n2[1] :			# 策划要求默认传送门放在最前
				return -1
			elif spaceDoorLabel not in n1[1] and spaceDoorLabel in n2[1] :
				return 1
			else :
				n1 = self.__distillDigital( n1[0] )
				n2 = self.__distillDigital( n2[0] )
				return cmp( n1, n2 )
		self.__nameTaxisFlag = not self.__nameTaxisFlag
		self.__pyInfoList.sort( cmp = customCmp, reverse = self.__nameTaxisFlag )

	def sortByNickname( self ) :
		"""
		按简称排序
		"""
		self.__nicknameTaxisFlag = not self.__nicknameTaxisFlag
		self.__pyInfoList.sort( key = lambda n : self.__distillDigital( n[1] ), reverse = self.__nicknameTaxisFlag )

	def reset( self ) :
		self.__nameTaxisFlag = True										# 重置名称排序反转标记
		self.__nicknameTaxisFlag = True									# 重置简称排序反转标记
		self.__pyInfoList.clearItems()


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getSelItem( self ) :
		return self.__pyInfoList.selItem

	def _setSelItem( self, item ) :
		self.__pyInfoList.selItem = item

	def _getItems( self ) :
		return self.__pyInfoList.items

	def _getSelIndex( self ) :
		return self.__pyInfoList.selIndex

	def _setSelIndex( self, index ) :
		self.__pyInfoList.selIndex = index

	# -------------------------------------------------
	selIndex 	= property( _getSelIndex, _setSelIndex )				# 获取当前的选中项索引
	selItem 	= property( _getSelItem, _setSelItem )					# 获取当前的选中项
	items 		= property( _getItems )									# 获取面板中的所有信息


# --------------------------------------------------------------------
# 写这个面板是为了更好地管理显示信息
# --------------------------------------------------------------------
class InfoPanel :

	def __init__( self, tabPanel, pyBinder ) :
		self.__searchResult = {}											# 当前关键字搜索的结果

		self.__initialize( tabPanel, pyBinder )

	def __initialize( self, tabPanel, pyBinder ) :
		self.__pyTabCtrl = TabCtrl( tabPanel )								# 分页控件

		pyTabBtn = TabButton( tabPanel.btn_0 )
		pyTabBtn.setStatesMapping( UIState.MODE_R3C1 )
		self.__pyNPCPanel = SubInfoPanel( tabPanel.panel_0, pyBinder )		# NPC信息面板
		pyTabPage = TabPage( pyTabBtn, self.__pyNPCPanel )
		self.__pyTabCtrl.addPage( pyTabPage )
		labelGather.setPyBgLabel( pyTabBtn, "NavigateWindow:main", "btn_0" ) # 设置标签

		pyTabBtn = TabButton( tabPanel.btn_1 )
		pyTabBtn.setStatesMapping( UIState.MODE_R3C1 )
		self.__pyMSTPanel = SubInfoPanel( tabPanel.panel_1, pyBinder )		# 怪物信息面板
		pyTabPage = TabPage( pyTabBtn, self.__pyMSTPanel )
		self.__pyTabCtrl.addPage( pyTabPage )
		labelGather.setPyBgLabel( pyTabBtn, "NavigateWindow:main", "btn_1" ) # 设置标签



	def dispose(self):
		self.__pyTabCtrl.dispose()
		self.__pyTabCtrl=None
		self.__pyNPCPanel.dispose()
		self.__pyNPCPanel=None
		self.__pyMSTPanel.dispose()
		self.__pyMSTPanel=None


	# ----------------------------------------------------------------
	#　public
	# ----------------------------------------------------------------
	def onRunToNPC( self ) :
		currPanel = self.pySelPanel
		if  currPanel is None : return
		currPanel.runToNPC()

	def onFlyToNPC( self ) :
		currPanel = self.pySelPanel
		if  currPanel is None : return
		currPanel.flyToNPC()

	def sortByName( self, tabPanel = None ) :
		"""
		按名称排序
		"""
		if tabPanel is None :
			tabPanel = self.pySelPanel
		if tabPanel is None : return
		tabPanel.sortByName()

	def sortByNickname( self, tabPanel = None ) :
		"""
		按简称排序
		"""
		if tabPanel is None :
			tabPanel = self.pySelPanel
		if tabPanel is None : return
		tabPanel.sortByNickname()

	def onSearch( self, text ) :
		text = text.strip()
		if text == "" : return											# 如果输入的是空格或空字符串，则不执行搜索
		currPanel = self.pySelPanel
		if currPanel is None : return
		result = self.__searchResult.get( ( text, currPanel ), [] )
		if result != [] :												# 如果前后两次搜索内容相同
			result.append( result.pop( 0 ) )							# 获取下一个搜索结果
			currPanel.selItem = result[0]
		else :															# 如果前后两次搜索内容不同
			result = []
			self.__searchResult = {}									# 清空上次搜索结果
			self.__searchResult[( text, currPanel )] = result			# 保存本次搜索结果
			for info in currPanel.items :
				if text in info[0] or text in info[1] :
					result.append( info )
			if result != [] :											# 如果搜索结果不为空
				currPanel.selItem = result[0]							# 则获取第一个搜索结果
			else :
				msg = BoxMsgDatas[0x0ec9] % text
				showAutoHideMessage( 3.0, msg, "", pyOwner = currPanel.pyTopParent )	# 提示未找到相关信息

	def reset( self ) :
		"""
		清空面板
		"""
		self.__searchResult = {}										# 清空上次搜索结果
		self.__pyNPCPanel.reset()										# 清空旧NPC信息
		self.__pyMSTPanel.reset()										# 清空旧怪物信息

	def reSort( self ) :
		self.__pyNPCPanel.sortByName()									# NPC按名称排序
		self.__pyMSTPanel.sortByNickname()								# 怪物按简称排序

	def resetState( self ) :
		"""
		刷新面板状态
		"""
		self.__pyNPCPanel.resetState()
		self.__pyMSTPanel.resetState()

	def addNPCItem( self, info ) :
		"""
		添加NPC信息
		"""
		self.__pyNPCPanel.addItem( info )

	def addMonsterItem( self, info ) :
		"""
		添加怪物信息
		"""
		self.__pyMSTPanel.addItem( info )


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getPySelPanel( self ) :
		pySelPage = self.__pyTabCtrl.pySelPage
		if pySelPage is not None :
			return pySelPage.pyPanel
		return None

	# -------------------------------------------------
	pySelPanel = property( _getPySelPanel )								# 当前选中的面板