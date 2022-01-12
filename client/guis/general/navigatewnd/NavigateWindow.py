# -*- coding: gb18030 -*-
#
# implement navigation window
# �Զ�Ѱ·NPC�����ѯ����
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
		self.__preSpaceLabel = ""										# ���ڵ�ͼ
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
		self.__pyFlyBtn = HButtonEx( wnd.flyBtn )							# ʹ����·�䴫�Ͱ�ť
		self.__pyFlyBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyFlyBtn.onLClick.bind( self.__flyToNPC )

		self.__pyNavigateBtn = HButtonEx( wnd.runBtn )						# �Զ�Ѱ·��NPC��ť
		self.__pyNavigateBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyNavigateBtn.onLClick.bind( self.__runToNPC )

		self.__pyNameBtn = HButtonEx( wnd.tc.header.header_0 )
		self.__pyNameBtn.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyNameBtn.onLClick.bind( self.__onSortByName )			# ����������

		self.__pyNicknameBtn = HButtonEx( wnd.tc.header.header_1 )
		self.__pyNicknameBtn.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyNicknameBtn.onLClick.bind( self.__onSortByNickname )	# ����������

		self.__pySearchText = TextBox( wnd.boxSearch.box )					# ���������
		self.__pySearchBtn = HButtonEx( wnd.searchBtn )					# ������ť
		self.__pySearchBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pySearchBtn.onLClick.bind( self.__onSearch )
		self.setOkButton( self.__pySearchBtn )

		self.__infoPanel = InfoPanel( wnd.tc, self )				# ��Ϣ���

		# ---------------------------------------------
		# ���ñ�ǩ
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
		����NPC��Ϣ
		"""
		player = BigWorld.player()
		spaceLabel = player.getSpaceLabel()								# ����Ƿ���ת�Ƶ���һ��ͼ��
		self.__preSpaceLabel = spaceLabel								# ���赱ǰ���ڵ�ͼ
		self.__infoPanel.reset()										# ��վ���Ϣ
		spaceNPCs = rds.npcDatasMgr.getNPCs( spaceLabel )				# ��ȡ��ǰ��ͼ������NPC
		for npc in spaceNPCs.itervalues() :								# �����ڵ�ͼ��NPC��ӵ�����
			npcID = npc.id
			infoItem = ( npc.name, npc.nickname, ( npc.getPosition( spaceLabel ), 8 ), npcID )
			if str( npcID )[0] in [ "1" ] :								# ����NPC
				self.__infoPanel.addNPCItem( infoItem )
			elif str( npcID )[0] in [ "2" ] :							# �ǹ���NPC
				self.__infoPanel.addMonsterItem( infoItem )
		spaceDoors = sdMgr.getSpaceDoorInf( spaceLabel )				# ��Ӵ�������Ϣ
		for sdData in spaceDoors :
			sdName = sdData.get( "uname", "" )
			if sdName.strip() == "" : continue
			sdNickname = sdData.get( "nickname", "" )
			sdPosition = sdData.get( "position", (0,0,0) )
			sdClassName = sdData.get( "className", "" )
			infoItem = ( sdName, sdNickname, ( sdPosition, 0 ), sdClassName )
			self.__infoPanel.addNPCItem( infoItem )
		self.__infoPanel.reSort()										# ��������˳��

	def __onSearch( self ) :
		"""
		������Ĺؼ�������
		"""
		text = self.__pySearchText.text									# �����ؼ���ȥ��ǰ��ո�
		self.__infoPanel.onSearch( text )

	def __onSortByName( self ) :
		"""
		��NPC����������
		"""
		self.__infoPanel.sortByName()

	def __onSortByNickname( self ) :
		"""
		��NPC�ļ������
		"""
		self.__infoPanel.sortByNickname()

	def __runToNPC( self ) :
		"""
		�Զ�Ѱ·
		"""
		self.__infoPanel.onRunToNPC()


	def hide(self):
		"""
		���ش���
		"""
		Window.hide(self)


	def __flyToNPC( self ) :
		"""
		ʹ����·��
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
# һ��NPC�б���ɶ��InfoItem��ɣ���ǰ�������������һ��NPC�б��
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
		�����б����ı�
		"""
		self.__pyName.text = info[0]
		self.__pyTitle.text = info[1]

	def resetColor( self, color ) :
		"""
		�����б���������ɫ
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
# NPC�����б����һ��NPC�б����ɶ���������
# --------------------------------------------------------------------
class InfoItem( StaticLabel, Control ) :
	"""
	������ʱ�ı���������ʾ������
	"""
	def __init__( self, item, pyBinder = None ) :
		StaticLabel.__init__( self, item, pyBinder )
		item = StaticLabel.getGui( self )
		Control.__init__( self, item, pyBinder )
		self.focus = False
		self.crossFocus = True

	def onMouseEnter_( self ) :
		"""
		������󱻵���
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
# ��ҳ��Ϣ���
# --------------------------------------------------------------------
class SubInfoPanel( TabPanel ) :

	def __init__( self, panel, pyBinder ) :
		TabPanel.__init__( self, panel, pyBinder )
		self.__initialize( panel )

		self.__nameTaxisFlag = True											# ��¼���������Ƿ�ת
		self.__nicknameTaxisFlag = True										# ��¼��������Ƿ�ת


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, panel ) :
		self.__pyInfoList = ODListPanel( panel.infoPanel, panel.scrollBar )	# NPC��Ϣ�б�
		self.__pyInfoList.onItemLDBClick.bind( self.__onItemLDBClicked )
		self.__pyInfoList.onViewItemInitialized.bind( self.__initListItem )
		self.__pyInfoList.itemHeight = 23
		self.__pyInfoList.ownerDraw = True								# �����Զ������
		self.__pyInfoList.onDrawItem.bind( self.__drawListItem )

	def dispose(self):
		self.__pyInfoList.clearItems()	# NPC��Ϣ�б�
		self.__pyInfoList=None
		TabPanel.dispose(self)


	def __initListItem( self, pyViewItem ) :
		"""
		��ʼ����ӵ�NPC�б���
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

		if pyViewItem.selected :							# ѡ��״̬
			pyNPCItem.setHighLight()
			pyNPCItem.resetColor( ( 60, 255, 0, 255 ) )
		elif pyViewItem.highlight :							# ����״̬����������ϣ�
			pyNPCItem.setHighLight()
#			pyNPCItem.resetColor( ( 60, 255, 255, 255 ) )
		else :
			pyNPCItem.setCommonLight()
			pyNPCItem.resetColor( ( 255, 255, 255, 255 ) )

	def __onItemLDBClicked( self, pyItem ) :
		"""
		���˫�����Զ�Ѱ·
		"""
		self.runToNPC()

	def __distillDigital( self, sourceText ) :
		"""
		���ڲ߻�������Ҫ�󣬴˺���������ȡ�ַ����п�ͷ������
		������һ���������ֵ��ַ�ֹͣ��ȡ
		@param	sourceText	: Ҫ��ȡ���ַ���
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
		ʹ����·��
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
			player.stopMove()											# ������ֹͣ�ƶ����Ա�֤׷��Ŀ�겻�����
			player.cell.flyToNpc( npcInfo[3], 0, items[0].order )
			player.setExpectTarget( npcInfo[3] )						# ����׷��Ŀ��NPC��ID
		else:
			player.statusMessage( csstatus.SKILL_USE_ITEM_WHILE_FIGHTING )
			return
		self.pyBinder.hide()

	def runToNPC( self ) :
		"""
		�Զ�Ѱ·
		"""
		npcInfo = self.__pyInfoList.selItem
		if npcInfo is None : return
		self.pyBinder.hide()
		player = BigWorld.player()
		player.setExpectTarget( npcInfo[3] )							# ����׷��Ŀ��NPC��ID
		player.autoRun( npcInfo[2][0], npcInfo[2][1] )

	def addItem( self, info ) :
		self.__pyInfoList.addItem( info )

	def resetState( self ) :
		self.__pyInfoList.resetState()

	def sortByName( self ) :
		"""
		����������
		"""
		def customCmp( n1, n2 ) :
			spaceDoorLabel = labelGather.getText( "NavigateWindow:main", "spaceDoor" )
			if spaceDoorLabel in n1[1] and spaceDoorLabel not in n2[1] :			# �߻�Ҫ��Ĭ�ϴ����ŷ�����ǰ
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
		���������
		"""
		self.__nicknameTaxisFlag = not self.__nicknameTaxisFlag
		self.__pyInfoList.sort( key = lambda n : self.__distillDigital( n[1] ), reverse = self.__nicknameTaxisFlag )

	def reset( self ) :
		self.__nameTaxisFlag = True										# ������������ת���
		self.__nicknameTaxisFlag = True									# ���ü������ת���
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
	selIndex 	= property( _getSelIndex, _setSelIndex )				# ��ȡ��ǰ��ѡ��������
	selItem 	= property( _getSelItem, _setSelItem )					# ��ȡ��ǰ��ѡ����
	items 		= property( _getItems )									# ��ȡ����е�������Ϣ


# --------------------------------------------------------------------
# д��������Ϊ�˸��õع�����ʾ��Ϣ
# --------------------------------------------------------------------
class InfoPanel :

	def __init__( self, tabPanel, pyBinder ) :
		self.__searchResult = {}											# ��ǰ�ؼ��������Ľ��

		self.__initialize( tabPanel, pyBinder )

	def __initialize( self, tabPanel, pyBinder ) :
		self.__pyTabCtrl = TabCtrl( tabPanel )								# ��ҳ�ؼ�

		pyTabBtn = TabButton( tabPanel.btn_0 )
		pyTabBtn.setStatesMapping( UIState.MODE_R3C1 )
		self.__pyNPCPanel = SubInfoPanel( tabPanel.panel_0, pyBinder )		# NPC��Ϣ���
		pyTabPage = TabPage( pyTabBtn, self.__pyNPCPanel )
		self.__pyTabCtrl.addPage( pyTabPage )
		labelGather.setPyBgLabel( pyTabBtn, "NavigateWindow:main", "btn_0" ) # ���ñ�ǩ

		pyTabBtn = TabButton( tabPanel.btn_1 )
		pyTabBtn.setStatesMapping( UIState.MODE_R3C1 )
		self.__pyMSTPanel = SubInfoPanel( tabPanel.panel_1, pyBinder )		# ������Ϣ���
		pyTabPage = TabPage( pyTabBtn, self.__pyMSTPanel )
		self.__pyTabCtrl.addPage( pyTabPage )
		labelGather.setPyBgLabel( pyTabBtn, "NavigateWindow:main", "btn_1" ) # ���ñ�ǩ



	def dispose(self):
		self.__pyTabCtrl.dispose()
		self.__pyTabCtrl=None
		self.__pyNPCPanel.dispose()
		self.__pyNPCPanel=None
		self.__pyMSTPanel.dispose()
		self.__pyMSTPanel=None


	# ----------------------------------------------------------------
	#��public
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
		����������
		"""
		if tabPanel is None :
			tabPanel = self.pySelPanel
		if tabPanel is None : return
		tabPanel.sortByName()

	def sortByNickname( self, tabPanel = None ) :
		"""
		���������
		"""
		if tabPanel is None :
			tabPanel = self.pySelPanel
		if tabPanel is None : return
		tabPanel.sortByNickname()

	def onSearch( self, text ) :
		text = text.strip()
		if text == "" : return											# ���������ǿո����ַ�������ִ������
		currPanel = self.pySelPanel
		if currPanel is None : return
		result = self.__searchResult.get( ( text, currPanel ), [] )
		if result != [] :												# ���ǰ����������������ͬ
			result.append( result.pop( 0 ) )							# ��ȡ��һ���������
			currPanel.selItem = result[0]
		else :															# ���ǰ�������������ݲ�ͬ
			result = []
			self.__searchResult = {}									# ����ϴ��������
			self.__searchResult[( text, currPanel )] = result			# ���汾���������
			for info in currPanel.items :
				if text in info[0] or text in info[1] :
					result.append( info )
			if result != [] :											# ������������Ϊ��
				currPanel.selItem = result[0]							# ���ȡ��һ���������
			else :
				msg = BoxMsgDatas[0x0ec9] % text
				showAutoHideMessage( 3.0, msg, "", pyOwner = currPanel.pyTopParent )	# ��ʾδ�ҵ������Ϣ

	def reset( self ) :
		"""
		������
		"""
		self.__searchResult = {}										# ����ϴ��������
		self.__pyNPCPanel.reset()										# ��վ�NPC��Ϣ
		self.__pyMSTPanel.reset()										# ��վɹ�����Ϣ

	def reSort( self ) :
		self.__pyNPCPanel.sortByName()									# NPC����������
		self.__pyMSTPanel.sortByNickname()								# ���ﰴ�������

	def resetState( self ) :
		"""
		ˢ�����״̬
		"""
		self.__pyNPCPanel.resetState()
		self.__pyMSTPanel.resetState()

	def addNPCItem( self, info ) :
		"""
		���NPC��Ϣ
		"""
		self.__pyNPCPanel.addItem( info )

	def addMonsterItem( self, info ) :
		"""
		��ӹ�����Ϣ
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
	pySelPanel = property( _getPySelPanel )								# ��ǰѡ�е����