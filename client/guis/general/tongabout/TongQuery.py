# -*- coding: gb18030 -*-
#
# $Id: TongQuery.py, fangpengjun Exp $

"""
implement tongquery window class
"""
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.common.PyGUI import PyGUI
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from WarIntergral import TaxisButton
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ListPanel import ListPanel
from guis.tooluis.CSTextPanel import CSTextPanel
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from guis.tooluis.inputbox.MoneyInputBox import MoneyInputBox
from config.client.msgboxtexts import Datas as mbmsgs
import GUIFacade
import csdefine
import csconst
import csstatus

EACH_PAGE_VIEW_ROWS = 20 #每页显示的帮会信息数

BUILDING_NAMES_MAP = { csdefine.TONG_BUILDING_TYPE_YSDT: labelGather.getText( "RelationShip:TongPanel", "build_type_ysdt" ),
			csdefine.TONG_BUILDING_TYPE_JK: labelGather.getText( "RelationShip:TongPanel", "build_type_jk" ),
			csdefine.TONG_BUILDING_TYPE_SSD: labelGather.getText( "RelationShip:TongPanel", "build_type_ssd" ),
			csdefine.TONG_BUILDING_TYPE_CK: labelGather.getText( "RelationShip:TongPanel", "build_type_ck" ),
			csdefine.TONG_BUILDING_TYPE_TJP: labelGather.getText( "RelationShip:TongPanel", "build_type_tjp" ),
			csdefine.TONG_BUILDING_TYPE_SD: labelGather.getText( "RelationShip:TongPanel", "build_type_sd" ),
			csdefine.TONG_BUILDING_TYPE_YJY: labelGather.getText( "RelationShip:TongPanel", "build_type_yjy" )
			}

text_color = ( 221, 208, 97, 255 )
val_color = ( 255, 252, 208, 255 )
affice_color = ( 26, 182, 152, 255 )

class TongQuery( Window ):
	def __init__( self ):
		wnd = GUI.load( "guis/general/tongabout/tongquery/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4			# in uidefine.py
		self.activable_ = True				# if a root gui can be ancriated, when it becomes the top gui, it will rob other gui's input focus
		self.escHide_ 		 = True
		self.__triggers = {}
		self.__registerTriggers()
		self.__trapID = 0
		self.__trapNPCID = -1
#		self.sortByIDFlag = False 		#按帮会ID排序
		self.sortByNameFlag = False		#按帮会名称
		self.sortByLevelFlag = False	#按帮会等级
		self.sortByPresFlag = False		#按帮会声望
		self.__tongInfos = []			#保存排序后的所有列表
		self.__initialize( wnd )

	def __initialize( self, wnd ):
		self.__pyTongsList = ListPanel( wnd.listPanel.clipPanel, wnd.listPanel.sbar )	#帮会信息列表
		self.__pyTongsList.autoSelect = False
		self.__pyTongsList.onItemLClick.bind( self.__onItemLClicked )

		self.__pyTongInfos = CSTextPanel( wnd.infoPanel.clipPanel, wnd.infoPanel.sbar )
		self.__pyTongInfos.text = ""

		self.__pyStTotalNum = StaticText( wnd.stTotalNum )
		self.__pyStTotalNum.text = ""

		self.__pyStIndex = StaticText( wnd.indexCtr.stPgIndex )
		self.__pyStIndex.text = "1"
		
		self.__pyStWarn = StaticText( wnd.stWarn )
		self.__pyStWarn.text = ""

		self.__pyBtnFront = Button( wnd.indexCtr.btnDec )
		self.__pyBtnFront.onLClick.bind( self.__onTurnFront )
		self.__pyBtnFront.setStatesMapping( UIState.MODE_R2C2 )

		self.__pyBtnNext = Button( wnd.indexCtr.btnInc )
		self.__pyBtnNext.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnNext.onLClick.bind( self.__onTurnNext )

		self.__pyBtnAplly = HButtonEx( wnd.btnApply )
		self.__pyBtnAplly.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnAplly.onLClick.bind( self.__onApply )
		labelGather.setPyBgLabel( self.__pyBtnAplly, "TongAbout:TongQuery", "btnApply" )

		self.__pyBtnEnter = HButtonEx( wnd.btnEnter )
		self.__pyBtnEnter.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnEnter.onLClick.bind( self.__onEnterTerritory )
		labelGather.setPyBgLabel( self.__pyBtnEnter, "TongAbout:TongQuery", "btnEnter" )

		self.__pyBtnCancel = HButtonEx( wnd.btnCancel )
		self.__pyBtnCancel.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancel.onLClick.bind( self.__onCancel )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "TongAbout:TongQuery", "btnCancel" )

#		self.__pyBtnSortID = HButtonEx( wnd.btnID )
#		self.__pyBtnSortID.setExStatesMapping( UIState.MODE_R3C1 )
#		self.__pyBtnSortID.onLClick.bind( self.__onSortByID )
#		labelGather.setPyBgLabel( self.__pyBtnSortID, "TongAbout:TongQuery", "taxisBtn_0" )

		self.__pyBtnSortName = HButtonEx( wnd.btnName )
		self.__pyBtnSortName.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnSortName.onLClick.bind( self.__onSortByName )
		labelGather.setPyBgLabel( self.__pyBtnSortName, "TongAbout:TongQuery", "taxisBtn_1" )

		self.__pyBtnSortLevel = HButtonEx( wnd.btnLevel )
		self.__pyBtnSortLevel.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnSortLevel.onLClick.bind( self.__onSortByLevel )
		labelGather.setPyBgLabel( self.__pyBtnSortLevel, "TongAbout:TongQuery", "taxisBtn_2" )

		self.__pyBtnSortPresBtn = HButtonEx( wnd.btnPres )
		self.__pyBtnSortPresBtn.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnSortPresBtn.onLClick.bind( self.__onSortByPres )
		labelGather.setPyBgLabel( self.__pyBtnSortPresBtn, "TongAbout:TongQuery", "taxisBtn_3" )

		labelGather.setLabel( wnd.lbTitle, "TongAbout:TongQuery", "lbTitle" )
		labelGather.setLabel( wnd.infoPanel.bgTitle.stTitle, "TongAbout:TongQuery", "tongInfo" )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TONG_QUERY_WND_SHOW"] = self.__onQueryShow
		self.__triggers["EVT_ON_TONG_RECEIVE_TONG_DATAS"] = self.__onReceiveDatas
		self.__triggers["EVT_ON_TONG_RECEIVE_TONG_COMPLETED"] = self.__onReceiveCompleted
		self.__triggers["EVT_ON_TONG_RECEIVE_TONG_INFO"] = self.__onReceiveTongInfo
		self.__triggers["EVT_ON_TONG_RECEIVE_FAMILY_INFO"] = self.__onReciveFamilyInfo
		self.__triggers["EVT_ON_TONG_AD_EDIT_SHOW" ] = self.__onADEditShow
		self.__triggers["EVT_ON_TOGGLE_TONG_DONATE_WND_OPEN"] = self.__onDonateWndOpen
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	# ---------------------------------------------------------------
	def __addTrap( self ):
		if self.__trapID:
			self.__delTrap()
		player = BigWorld.player()
		self.__trapNPCID = GUIFacade.getGossipTargetID()
		distance = csconst.COMMUNICATE_DISTANCE
		trapNPC = self.trapNPC
		if hasattr( trapNPC, "getRoleAndNpcSpeakDistance" ):
			distance = trapNPC.getRoleAndNpcSpeakDistance()
		self.__trapID = player.addTrapExt( distance, self.__onEntitiesTrapThrough )	# 打开窗口后为玩家添加对话陷阱s

	def __onEntitiesTrapThrough( self, entitiesInTrap ):
		gossiptarget = self.trapNPC
		if gossiptarget not in entitiesInTrap :
			self.hide()
			self.__delTrap()

	def __delTrap( self ) :
		player = BigWorld.player()
		if self.__trapID :
			player.delTrap( self.__trapID )											#删除玩家的对话陷阱
			self.__trapID = 0

	# ------------------------------------------------------------------
	def __onQueryShow( self ):
		"""
		显示查询界面
		"""
		self.__addTrap()
		self.show()

	def __onReceiveDatas( self, tongDatas ):
		"""
		依次接收帮会信息
		"""
		if not tongDatas in self.__tongInfos:
			self.__tongInfos.append( tongDatas )
			self.__tongInfos.sort( key = lambda tongDatas: tongDatas["tongName"], reverse = self.sortByNameFlag ) #默认按帮会名字排序
		if self.__pyTongsList.itemCount >= EACH_PAGE_VIEW_ROWS: #显示前20个
			return
		totalIndex = self.__getTotalIndex()
		if totalIndex <= 1:
			self.__pyBtnNext.enable = False
			self.__pyBtnFront.enable = False
		else:
			self.__pyBtnNext.enable = ( self.__pyStIndex.text ) < totalIndex
			self.__pyBtnFront.enable = ( self.__pyStIndex.text ) > 1
		tongDBID = tongDatas["tongDBID"]
		if not tongDBID in [pyTong.tongDatas["tongDBID"] for pyTong in self.__pyTongsList.pyItems]:
			tongItem = GUI.load( "guis/general/tongabout/tongquery/tongitem.gui" )
			uiFixer.firstLoadFix( tongItem )
			pyTongItem = TongItem( tongItem )
			pyTongItem.setTongInfo( tongDatas )
			self.__pyTongsList.addItem( pyTongItem )
			self.__pyTongsList.sort( key = lambda pyItem: pyItem.tongDatas["tongName"], reverse = self.sortByNameFlag )

	def __onReceiveCompleted( self, tongNum ):
		"""
		接收完帮会信息
		"""
		self.__pyStTotalNum.text = labelGather.getText( "TongAbout:TongQuery", "totalNum" )%tongNum
		self.__pyStWarn.text = labelGather.getText( "TongAbout:TongQuery", "warn1" )
		BigWorld.callback(1.0, self.__hideWarn )
		tongListInfos = BigWorld.player().TongListInfos
		tongDatas = tongListInfos.values()
		tongDatas.sort( key = lambda tongDatas: tongDatas["tongName"], reverse = self.sortByNameFlag )
		self.__tongInfos = tongDatas
		totalIndex = self.__getTotalIndex()
		if totalIndex <= 1:
			self.__pyBtnNext.enable = False
			self.__pyBtnFront.enable = False
		else:
			self.__pyBtnNext.enable = ( self.__pyStIndex.text ) < totalIndex
			self.__pyBtnFront.enable = ( self.__pyStIndex.text ) > 1
		self.__showPyTongs( 1 )

	def __onReceiveTongInfo( self, tongDBID, memberCount, toBuildType, toBuildLevel, chiefName, holdCity, leagues, ad ):
		"""
		接收到所查询帮会的信息
		"""
		player = BigWorld.player()
		pyTongItem = self.__pyTongsList.pySelItem
		tongDatas = pyTongItem.tongDatas
		if tongDatas["tongDBID"] == tongDBID: #如果与当前选择的帮会一致，则显示
			tongName = tongDatas["tongName"]
			tongLevel = tongDatas["tongLevel"]
			buildName = BUILDING_NAMES_MAP.get( toBuildType, "" ) #建筑名称
			cityName = csconst.g_maps_info.get( holdCity, "" ) #占领城市名称
			if cityName == "":
				cityName = labelGather.getText( "TongAbout:TongQuery", "without" )
			leagueName = ""
			if len( leagues ) <= 0:
				leagueName = labelGather.getText( "TongAbout:TongQuery", "without" )
			else:
				for league in leagues:
					leagueName += "%s%s"%( league, PL_Space.getSource(2) )
			if ad == "":
				ad = labelGather.getText( "TongAbout:TongQuery", "without" )
			nameText = PL_Font.getSource( labelGather.getText( "TongAbout:TongQuery", "tongName" ), fc = text_color )
			nameText += PL_Font.getSource( "%s%s"%( tongName, PL_NewLine.getSource() ), fc = val_color )
			chiefText =  PL_Font.getSource( labelGather.getText( "TongAbout:TongQuery", "tongChief" ), fc = text_color ) #帮主名称
			chiefText += PL_Font.getSource( "%s%s"%( chiefName, PL_NewLine.getSource() ), fc = val_color )
			levelText = PL_Font.getSource( labelGather.getText( "TongAbout:TongQuery", "tongLevel" ), fc = text_color ) #帮会等级
			levelText += PL_Font.getSource( "%d%s"%( tongLevel, PL_NewLine.getSource() ), fc = val_color )
			countText = PL_Font.getSource( labelGather.getText( "TongAbout:TongQuery", "tongMember" ), fc = text_color ) #帮会人数
			countText += PL_Font.getSource( "%d%s"%( memberCount, PL_NewLine.getSource() ), fc = val_color )
			buildText = PL_Font.getSource( labelGather.getText( "TongAbout:TongQuery", "curBuild" ), fc = text_color ) #当前建筑
			if buildName != "":
				buildText += PL_Font.getSource( labelGather.getText( "TongAbout:TongQuery", "buildLevel" )%( buildName, toBuildLevel, PL_NewLine.getSource() ), fc = val_color )
			else:
				buildText += PL_Font.getSource( labelGather.getText( "TongAbout:TongQuery", "noBuild" )%PL_NewLine.getSource(), fc = val_color )
			cityText = PL_Font.getSource( labelGather.getText( "TongAbout:TongQuery", "occupCity" ),fc = text_color ) #占领城市
			cityText += PL_Font.getSource( "%s%s"%( cityName, PL_NewLine.getSource() ) ,fc = val_color )
			leagueText = PL_Font.getSource( labelGather.getText( "TongAbout:TongQuery", "tongLeague" ),fc = text_color ) #帮会同盟
			leagueText += PL_Font.getSource( "%s%s"%( leagueName, PL_NewLine.getSource() ), fc = val_color )
			afficheText = PL_Font.getSource( labelGather.getText( "TongAbout:TongQuery", "tongPublic" ),fc = text_color ) #帮会宣传
			afficheText += PL_Font.getSource( "%s"%ad, fc = val_color )
			self.__pyTongInfos.text = nameText + chiefText + levelText + countText + buildText + leagueText + afficheText

	def __onReciveFamilyInfo( self,familyDBID, familyName ):
		"""
		收到某个家族信息
		"""
		pass

	def __onADEditShow( self ):
		"""
		帮会宣传编辑
		"""
		TongAD.instance().show()

	def __onDonateWndOpen( self ):
		"""
		帮会捐钱
		"""
		def requestInput( res, money ) :
			if res == DialogResult.OK:
				player = BigWorld.player()
				if player.money < money:
					player.statusMessage( csstatus.DONATE_MONEY_NOT_ENOUGH )
					return
				BigWorld.player().tong_contributeToMoney( money )
		MoneyInputBox().show( requestInput, labelGather.getText( "TongAbout:TongQuery", "contriMoney" ), self )

	def __onItemLClicked( self, pyTong ):
		if pyTong is None:return
		tongDatas = pyTong.tongDatas
		tongDBID = tongDatas["tongDBID"]
		BigWorld.player().tong_queryTongInfo( tongDBID )

	def __onTurnFront( self ):
		"""
		向前翻一页
		"""
		curIndex = int( self.__pyStIndex.text )
		if curIndex <= 1:return
		pageIndex = curIndex - 1
		self.__showPyTongs( pageIndex )

	def __onTurnNext( self ):
		"""
		向后翻一页
		"""
		curIndex = int( self.__pyStIndex.text )
		if curIndex >= self.__getTotalIndex():
			return
		pageIndex = curIndex + 1
		self.__showPyTongs( pageIndex )

	def __getTotalIndex( self ):
		"""
		获取全部页数
		"""
		tongListInfos = BigWorld.player().TongListInfos
		quotient = len( tongListInfos )/EACH_PAGE_VIEW_ROWS
		residue = len( tongListInfos )%EACH_PAGE_VIEW_ROWS
		if residue > 0:
			quotient += 1
		return quotient

	def __showPyTongs( self, pageIndex ):
		"""
		显示指定页数的帮会列表
		"""
		self.__pyTongsList.clearItems()
		self.__pyStIndex.text = str( pageIndex )
		startIndex = ( pageIndex - 1 )*EACH_PAGE_VIEW_ROWS
		for index, tongDatas in enumerate( self.__tongInfos ):
			disIndex = index - startIndex
			if disIndex >= 0 and disIndex <= EACH_PAGE_VIEW_ROWS - 1:
				tongItem = GUI.load( "guis/general/tongabout/tongquery/tongitem.gui" )
				uiFixer.firstLoadFix( tongItem )
				pyTongItem = TongItem( tongItem )
				pyTongItem.setTongInfo( tongDatas )
				self.__pyTongsList.addItem( pyTongItem )
		totalIndex = self.__getTotalIndex()
		if totalIndex <= 1:
			self.__pyBtnNext.enable = False
			self.__pyBtnFront.enable = False
		else:
			if pageIndex >1 and pageIndex < totalIndex:
				self.__pyBtnNext.enable = True
				self.__pyBtnFront.enable = True
			elif pageIndex >= totalIndex:
				self.__pyBtnNext.enable = False
				self.__pyBtnFront.enable = True
			else:
				self.__pyBtnNext.enable = True
				self.__pyBtnFront.enable = False

	def __onSortByID( self ):
		"""
		按帮会ID排序
		"""
		pass
#		tongDatas = BigWorld.player().TongListInfos.values()
#		tongDatas.sort( key = lambda datas:datas["tongID"], reverse = self.sortByIDFlag )
#		self.__tongInfos = tongDatas
#		self.__showPyTongs( int( self.__pyStIndex.text ) )
#		self.sortByIDFlag = not self.sortByIDFlag

	def __onSortByName( self ):
		"""
		按帮会名称排序
		"""
		tongDatas = BigWorld.player().TongListInfos.values()
		tongDatas.sort( key = lambda datas:datas["tongName"], reverse = self.sortByNameFlag )
		self.__tongInfos = tongDatas
		self.__showPyTongs( int( self.__pyStIndex.text ) )
		self.sortByNameFlag = not self.sortByNameFlag

	def __onSortByLevel( self ):
		"""
		按帮会等级排序
		"""
		tongDatas = BigWorld.player().TongListInfos.values()
		tongDatas.sort( key = lambda datas:datas["tongLevel"], reverse = self.sortByLevelFlag )
		self.__tongInfos = tongDatas
		self.__showPyTongs( int( self.__pyStIndex.text ) )
		self.sortByLevelFlag = not self.sortByLevelFlag

	def __onSortByPres( self ):
		"""
		按帮会声望排序
		"""
		tongDatas = BigWorld.player().TongListInfos.values()
		tongDatas.sort( key = lambda datas:datas["tongPrestige"], reverse = self.sortByPresFlag )
		self.__tongInfos = tongDatas
		self.__showPyTongs( int( self.__pyStIndex.text ) )
		self.sortByPresFlag = not self.sortByPresFlag

	def __onApply( self ):
		"""
		申请进入某个帮会
		"""
		selPyTong = self.__pyTongsList.pySelItem
		if selPyTong is None:return
		tongDBID = selPyTong.tongDatas["tongDBID"]
		BigWorld.player().tong_requestJoinToTong( tongDBID )

	def __onEnterTerritory( self ):
		"""
		进入指定帮会领地
		"""
		selPyTong = self.__pyTongsList.pySelItem
		if selPyTong is None:return
		tongDBID = selPyTong.tongDatas["tongDBID"]
		BigWorld.player().cell.tong_tongListEnterTongTerritory( tongDBID )

	def __onCancel( self ):
		"""
		关闭界面
		"""
		self.hide()
	
	def __hideWarn( self ):
		self.__pyStWarn.text = ""
	# ----------------------------------------------------------
	#public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ):
		self.__delTrap()
		self.hide()

	def show( self ):
		self.__pyStWarn.text = labelGather.getText( "TongAbout:TongQuery", "warn0" )
#		self.__pyBtnNext.enable = False
#		self.__pyBtnFront.enable = False
		Window.show( self )

	def hide( self ):
		self.__tongInfos = []
		self.__pyTongsList.clearItems()
		self.__pyTongInfos.text = ""
		self.__pyStIndex.text = "1"
		self.__pyStTotalNum.text = ""
		self.__pyStWarn.text = ""
#		self.sortByIDFlag = False 		#按帮会ID排序
		self.sortByNameFlag = False		#按帮会名称
		self.sortByLevelFlag = False	#按帮会等级
		self.sortByPresFlag = False		#按帮会声望
		Window.hide( self )

	def _getTrapNPC( self ) :
		return BigWorld.entities.get( self.__trapNPCID, None )

	trapNPC = property( _getTrapNPC )

# ----------------------------------------------------------------------
from guis.controls.ListItem import MultiColListItem

class TongItem( MultiColListItem ):
	def __init__( self, tongItem ):
		MultiColListItem.__init__( self, tongItem )
		self.tongDatas = None
		self.commonBackColor = ( 255, 255, 255, 255 )
		self.selectedBackColor = ( 255, 255, 255, 255 )
		self.highlightBackColor = ( 255, 255, 255, 255 )

	def onStateChanged_( self, state ):
		MultiColListItem.onStateChanged_( self, state )
		elements = self.getGui().elements
		for element in elements.values():
			element.visible = state in [UIState.HIGHLIGHT, UIState.SELECTED]

	def setTongInfo( self, tongDatas ):
		player = BigWorld.player()
		self.tongDatas = tongDatas
		tongName = tongDatas["tongName"]
		leagues = player.tong_leagues
		commonForeColor = ( 255, 252, 208, 255 )
		if tongName in leagues: #同盟帮会
			commonForeColor = ( 252, 255, 0, 255 )
		if tongDatas["isHoldCity"]:
			tongName = labelGather.getText( "TongAbout:TongQuery", "cityTag" )%tongName
		self.pyCols[1].commonForeColor = commonForeColor
		self.setTextes( tongName, tongDatas["tongLevel"], tongDatas["tongPrestige"] )

# ----------------------------------------------------------------------
from guis.controls.TextBox import TextBox
from guis.tooluis.CSMLRichTextBox import CSMLRichTextBox
import csdefine

class TongAD( Window ):
	"""
	帮会宣传窗口
	"""
	__instance=None
	def __init__( self ):
		assert TongAD.__instance is None,"FoundTong instance has been created"
		TongAD.__instance = self
		panel = GUI.load( "guis/general/tongabout/tongquery/tongad.gui" )
		uiFixer.firstLoadFix( panel )
		Window.__init__( self, panel )
		self.addToMgr( "tongAD" )
		self.pressedOK_ = False
		self.callback_ = lambda *args : False

		self.__initpanel( panel )

	def __initpanel( self, panel ):
		"""
		"""
		self.__pyBtnOK = HButtonEx( panel.btnOk )
		self.__pyBtnOK.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOK.onLClick.bind( self.__onSetAD )
		self.__pyBtnOK.enable = False
		labelGather.setPyBgLabel( self.__pyBtnOK, "TongAbout:TongAD", "okBtn" )

		self.__pyBtnCancel = HButtonEx( panel.btnCancel )
		self.__pyBtnCancel.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancel.onLClick.bind( self.__onCancel )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "TongAbout:TongAD", "cancelBtn" )

		self.__pyADBox = CSMLRichTextBox( panel.editPanel, panel.editBar )
		self.__pyADBox.maxLength = 220
		self.__pyADBox.onTextChanged.bind( self.__onTextChange )
		self.__pyADBox.text = ""
		labelGather.setLabel( panel.lbTitle, "TongAbout:TongAD", "lbTitle" )

	def __onSetAD( self ) :
		player = BigWorld.player()
		if self.notify_() :
			text = self.__pyADBox.text
			player.tong_setTongAD( text )
			self.hide()

	def __onCancel( self ) :
		self.hide()
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def notify_( self ) :
		player = BigWorld.player()
		text = self.__pyADBox.text
#		if text == "" : return False

		if player.tong_dbID <= 0:
			# "对不起，您还没有帮会。"
			showAutoHideMessage( 3.0, 0x09e1, mbmsgs[0x0c22] )
			return False
		elif len( text ) > csdefine.TONG_AD_LENGTH_MAX:
			# "帮会宣传必须在40字节内"
			showMessage( 0x09e4,"", MB_OK )
			return False
		elif rds.wordsProfanity.searchMsgProfanity( text ) is not None :
			# "帮会宣传含有禁用词汇!"
			showAutoHideMessage( 3.0, 0x09e3, mbmsgs[0x0c22] )
			return False
		try :
			self.callback_( DialogResult.OK, text )
		except :
			EXCEHOOK_MSG()
		self.pressedOK_ = True
		return True

	def __onTextChange( self ) :
		self.__pyBtnOK.enable = True

	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def show( self ) :
		player = BigWorld.player()
		Window.show( self )
		self.__pyADBox.tabStop = True

	def hide( self ):
		Window.hide( self )
		self.dispose()
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		self.removeFromMgr()
		self.__pyADBox.tabStop = False

	def onLeaveWorld( self ) :
		self.hide()

	def onActivated( self ) :
		"""
		当窗口激活时被调用
		"""
		Window.onActivated( self )
		self.__pyADBox.tabStop = True

	def dispose(self):
		TongAD.__instance=None
		Window.dispose(self)

	@staticmethod
	def instance():
		if TongAD.__instance is None:
			TongAD.__instance = TongAD()
		return TongAD.__instance

	def __del__(self):
		Window.__del__( self )
		if Debug.output_del_TongAD :
			INFO_MSG( str( self ) )
