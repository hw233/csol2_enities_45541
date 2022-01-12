# -*- coding: gb18030 -*-

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.common.GUIBaseObject import GUIBaseObject
from guis.controls.StaticText import StaticText
from guis.controls.ButtonEx import HButtonEx
from guis.controls.Control import Control
from guis.controls.TextBox import TextBox
from guis.controls.ODListPanel import ODListPanel
import csdefine
import csstatus
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Space import PL_Space

class TongsAlliance( Window ):
	def __init__( self ):
		wnd = GUI.load( "guis/general/spacecopyabout/tongsAlliance/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		
		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()
		
	def __initialize( self, wnd ):
		labelGather.setLabel( wnd.lbTitle, "TongsAlliance:main", "lbTitle")
		labelGather.setLabel( wnd.inputTips, "TongsAlliance:main", "searchTips")
		self.__pyTiAttack = PriTongItem( wnd.attackItem )
		self.__pyTiDefence = PriTongItem( wnd.defenceItem )
		
		self.__pyTextBox = TextBox( wnd.textBox.box )
		
		self.__pyBtnSearch = HButtonEx( wnd.btnSearch )
		self.__pyBtnSearch.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnSearch.onLClick.bind( self.__onSearch )
		labelGather.setPyBgLabel( self.__pyBtnSearch, "TongsAlliance:main", "btnSearch" )
		
		self.__pyListPanel = ODListPanel( wnd.tongPanel.clipPanel, wnd.tongPanel.sbar )
		self.__pyListPanel.onViewItemInitialized.bind( self.__initListItem )
		self.__pyListPanel.onDrawItem.bind( self.__drawListItem )
		self.__pyListPanel.ownerDraw = True
		self.__pyListPanel.itemHeight = 39
		self.__pyListPanel.autoSelect = False
		
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_TONG_ALLIANCE_WINDOW_SHOW"] = self.__onShow
		self.__triggers["EVT_ON_TONG_ALLIANCE_CHANGED"] = self.__onAllianceChange
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )
			
	def __initListItem( self, pyViewItem ):
		pyTongItem = TongItem()
		pyViewItem.addPyChild( pyTongItem )
		pyViewItem.pyItem = pyTongItem
		pyTongItem.left = 0
		pyTongItem.top = 0
	
	def __drawListItem( self, pyViewItem ):
		pyTongItem = pyViewItem.pyItem
		pyTongItem.updateTongInfo( pyViewItem.listItem )	
		if pyViewItem.selected :							# 选中状态
			pyTongItem.setHighLight()
			pyTongItem.resetColor( ( 60, 255, 0, 255 ) )
		elif pyViewItem.highlight :							# 高亮状态（鼠标在其上）
			pyTongItem.setHighLight()
		else :
			pyTongItem.setCommonLight()
			pyTongItem.resetColor( ( 255, 255, 255, 255 ) )
		
	def __onSearch( self ):
		"""
		查找帮会
		"""
		player = BigWorld.player()
		camp = player.getCamp()
		self.__pyListPanel.clearItems()
		tongKey = self.__pyTextBox.text.strip()
		chiefTong = player.tong_quarterFinalRecord.keys()
		tongsInfo = player.tong_battleLeagues.values()
		newTongsInfo = [ tongInfo for tongInfo in tongsInfo if tongInfo["camp"] == camp]
		tongItems = []				
		if tongKey != "":			 
			for  tongInfo in newTongsInfo:
				if tongInfo["tongDBID"] in chiefTong:continue
				tongName = tongInfo["tongName"]
				if tongKey in tongName:
					tongItems.append( tongInfo )
		else:
			for  tongInfo in newTongsInfo:
				if tongInfo["tongDBID"] in chiefTong:continue
				tongItems.append( tongInfo )
					
		self.__pyListPanel.addItems( tongItems )
		self.__pyListPanel.sort( key = lambda item: item["tongName"], reverse = False)
		
	def __checkAllianceByDBID( self, tongDBID ):
		"""
		查询一个帮会是否已经结盟
		"""
		player = BigWorld.player()
		tongInfo = player.tong_battleLeagues.get( tongDBID )
		leagues = tongInfo["battleLeagues"]
		return len(leagues) != 0	

	def __updateChiefTong( self ):
		tong_quarterFinalRecord = BigWorld.player().tong_quarterFinalRecord
		for tongDBID, order in tong_quarterFinalRecord.iteritems():
			if order == 1:		#第一名是守城帮会
				self.__pyTiDefence.updateTongInfo( tongDBID, order )
			elif order == 2:	#第二名是攻城帮会
				self.__pyTiAttack.updateTongInfo( tongDBID, order)			
		
	def __onShow( self ):
		"""
		打开界面
		"""
		self.__updateChiefTong()
		self.__onSearch()				
		Window.show( self )
		
	def __onAllianceChange( self, tongDBID ):
		for pyViewItem in self.__pyListPanel.pyViewItem:
			pyItem = pyViewItem.pyItem
			if pyItem["tongDBID"] == tongDBID:
				isAlliance = self.__checkAllianceByDBID( tongDBID )
				pyItem.updAlliance( isAlliance )
		self.__updateChiefTong()
		
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )
		
	def onLeaveWorld( self ):
		self.hide()
		
	
class PriTongItem( GUIBaseObject ):
	def __init__( self, gui ):
		GUIBaseObject.__init__( self, gui )
		self.__tongDBID = 0
		
		self.__pyTongText = StaticText( gui.tongText )
		self.__pyTongText.text = ""
		
		self.__pyRtAlliance = CSRichText( gui.allianceText )
		self.__pyRtAlliance.onMouseEnter.bind( self.__showAllianceTong )
		self.__pyRtAlliance.onMouseLeave.bind( self.__hideAllianceTong )
		self.__pyRtAlliance.crossFocus = False
		self.__pyRtAlliance.autoNewline = False
		self.__pyRtAlliance.text = ""		
		
		self.__pyTongName = StaticText( gui.stTongName )
		self.__pyTongName.text = ""
		
		self.__pyBtnAlliance = HButtonEx( gui.btnAlliance )
		self.__pyBtnAlliance.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnAlliance.onLClick.bind( self.__requestAlliance )
		labelGather.setPyBgLabel( self.__pyBtnAlliance, "TongsAlliance:main", "btnAlliance" )
		
	def __requestAlliance( self ):
		"""
		申请结盟
		"""
		player = BigWorld.player()
		tongDBID = player.tong_dbID
		if not tongDBID or player.tong_grade != csdefine.TONG_DUTY_CHIEF:
			player.statusMessage( csstatus.TONG_BATTLE_LEAGUE_LIMIT )
			return
		if tongDBID in player.tong_quarterFinalRecord.keys():	# 不能和自己和敌对帮会结盟
			return
		if self.__checkAllianceByDBID( tongDBID ):				#	已经结盟的帮会不能和攻、守城帮会结盟
			return
		
		TongInvite.instance().show( self.__tongDBID )
		
	def __checkAllianceByDBID( self, tongDBID ):
		"""
		查询一个帮会是否已经结盟
		"""
		player = BigWorld.player()
		tongInfo = player.tong_battleLeagues.get( tongDBID )
		leagues = tongInfo["battleLeagues"]
		return len(leagues) != 0		
		
	def __showAllianceTong( self ):
		"""
		显示同盟帮会悬浮框
		"""
		player = BigWorld.player()
		infos = labelGather.getText( "TongsAlliance:main", "allianceTongs" )
		tongData = BigWorld.player().tong_battleLeagues.get( self.__tongDBID )
		battleLeagues = tongData["battleLeagues"]
		for tongDBID in battleLeagues:
			tongInfo = player.tong_battleLeagues.get( tongDBID )
			tongName = tongInfo["tongName"]
			infos += tongName
			infos += PL_Space.getSource( 1 )
		toolbox.infoTip.showToolTips( self.__pyRtAlliance, infos )
		
	def __hideAllianceTong( self ):
		"""
		隐藏悬浮信息
		"""
		toolbox.infoTip.hide()
		
	def updateTongInfo( self, tongDBID, order ):
		self.__tongDBID = tongDBID
		player = BigWorld.player()
		tongData = player.tong_battleLeagues.get( tongDBID )
		if tongData is None:return
		leagues = tongData["battleLeagues"]
		if order == 1:
			self.__pyTongText.text = labelGather.getText( "TongsAlliance:main", "attackTongText" )
		elif order == 2:
			self.__pyTongText.text = labelGather.getText( "TongsAlliance:main", "defenceTongText" )
		self.__pyTongName.text = tongData["tongName"]
		if len( leagues ) == 0:
			self.__pyRtAlliance.text = labelGather.getText( "TongsAlliance:main", "unAllianceText" )
			self.__pyRtAlliance.crossFocus = False
		else:
			self.__pyRtAlliance.text = labelGather.getText( "TongsAlliance:main", "allianceText" )
			self.__pyRtAlliance.crossFocus = True
		
		
class TongItem( Control ):
	
	_TONG_ITEM = None
	
	def __init__( self ):
		if TongItem._TONG_ITEM is None:
			TongItem._TONG_ITEM = GUI.load( "guis/general/spacecopyabout/tongsAlliance/tongItem.gui" )
			uiFixer.firstLoadFix( TongItem._TONG_ITEM )
		gui = util.copyGuiTree( TongItem._TONG_ITEM )
		
		Control.__init__( self, gui )
		self.crossFocus = False
		self.focu = False
		self.__tongDBID = 0
		
		self.__initialize( gui )
		
	def __initialize( self, gui ):
		self.__selPanel = gui.selPanel
		self.__selPanel.visible = False
		
		self.__pyTongName = StaticText( gui.stTongName )
		self.__pyTongName.text = ""
		
		self.__pyRtAlliance = CSRichText( gui.allianceText )
		self.__pyRtAlliance.onMouseEnter.bind( self.__showAllianceTong )
		self.__pyRtAlliance.onMouseLeave.bind( self.__hideAllianceTong )
		self.__pyRtAlliance.crossFocus = False
		self.__pyRtAlliance.autoNewline = False
		self.__pyRtAlliance.text = ""
		
		self.__pyBtnAlliance = HButtonEx( gui.btnAlliance )
		self.__pyBtnAlliance.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnAlliance.onLClick.bind( self.__requestAlliance )
		labelGather.setPyBgLabel( self.__pyBtnAlliance, "TongsAlliance:main", "btnAlliance" )
		
	def __requestAlliance( self ):
		"""
		申请结盟
		"""
		player = BigWorld.player()
		tongDBID = player.tong_dbID
		if not tongDBID or player.tong_grade != csdefine.TONG_DUTY_CHIEF:
			player.statusMessage( csstatus.TONG_BATTLE_LEAGUE_LIMIT )
			return
		if not self.__checkIsChiefTong( tongDBID ):
			player.statusMessage( csstatus.TONG_BATTLE_LEAGUE_NOT_QUALIFIED )
			return
		
		TongInvite.instance().show( self.__tongDBID )	
		
	def __checkIsChiefTong( self, tongDBID ):
		"""
		判断帮会是否是攻城或者守城帮会
		"""
		player = BigWorld.player()
		return tongDBID in player.tong_quarterFinalRecord.keys()
		
	def __showAllianceTong( self ):
		"""
		显示同盟帮会悬浮框
		"""
		player = BigWorld.player()
		infos = labelGather.getText( "TongsAlliance:main", "allianceTongs" )
		tongData = BigWorld.player().tong_battleLeagues.get( self.__tongDBID )
		battleLeagues = tongData["battleLeagues"]
		for tongDBID in battleLeagues:
			tongInfo = player.tong_battleLeagues.get( tongDBID )
			tongName = tongInfo["tongName"]
			infos += tongName
			infos += PL_Space.getSource( 1 )
		toolbox.infoTip.showToolTips( self.__pyRtAlliance, infos )
		
	def __hideAllianceTong( self ):
		"""
		隐藏悬浮信息
		"""
		toolbox.infoTip.hide()
				
		
	def updateTongInfo( self, tongInfo ):
		self.__tongDBID = tongInfo["tongDBID"]
		tongName = tongInfo["tongName"]
		isAlliance = not( len( tongInfo["battleLeagues"]) == 0 )
		self.__pyTongName.text = tongName
		if isAlliance:
			self.__pyRtAlliance.text = labelGather.getText( "TongsAlliance:main", "allianceText" )
			self.__pyBtnAlliance.enable = False
		else:
			self.__pyRtAlliance.text = labelGather.getText( "TongsAlliance:main", "unAllianceText" )
		
	def updAlliance( self, isAlliance ):
		if isAlliance:
			self.__pyRtAlliance.text = labelGather.getText( "TongsAlliance:main", "allianceText" )
			self.__pyBtnAlliance.enable = False
		else:
			self.__pyRtAlliance.text = labelGather.getText( "TongsAlliance:main", "unAllianceText" )
	
	def resetColor( self, color ) :
		"""
		更新列表项字体颜色
		"""
		self.__pyTongName.color = color
		self.__pyRtAlliance.foreColor = color
		
	def setHighLight( self ):
		self.__selPanel.visible = True
	
	def setCommonLight( self ):
		self.__selPanel.visible = False
	
from guis.tooluis.CSMLRichTextBox import CSMLRichTextBox
from config.client.msgboxtexts import Datas as mbmsgs
class TongInvite( Window ):
	"""
	帮会结盟申请窗口
	"""
	__instance=None
	def __init__( self ):
		assert TongInvite.__instance is None,"FoundTong instance has been created"
		TongInvite.__instance = self
		panel = GUI.load( "guis/general/spacecopyabout/tongsAlliance/invite.gui" )
		uiFixer.firstLoadFix( panel )
		Window.__init__( self, panel )
		self.addToMgr( "TongInvite" )
		self.__tongDBID = 0
		
		self.__initpanel( panel )

	def __initpanel( self, panel ):
		"""
		"""
		self.__pyBtnSend = HButtonEx( panel.btnSend )
		self.__pyBtnSend.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnSend.onLClick.bind( self.__onSend)
		self.__pyBtnSend.enable = False
		labelGather.setPyBgLabel( self.__pyBtnSend, "TongsAlliance:TongInvite", "btnSend" )

		self.__pyADBox = CSMLRichTextBox( panel.editPanel, panel.editBar )
		self.__pyADBox.maxLength = 246
		self.__pyADBox.onTextChanged.bind( self.__onTextChange )
		self.__pyADBox.text = ""
		labelGather.setLabel( panel.lbTitle, "TongsAlliance:TongInvite", "lbTitle" )


	def __onSend( self ) :
		if self.notify_:	
			msg = self.__pyADBox.text				
			BigWorld.player().tong_inviteTongBattleLeagues( self.__tongDBID, msg )
			self.hide()
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def notify_( self ) :
		player = BigWorld.player()
		text = self.__pyADBox.text
		if text == "" : 
			showAutoHideMessage( 3.0, mbmsgs[0x11c1], "", pyOwner = self )
			return False
		wideText = csstring.toWideString( text )
		if len(wideText) > 246:
			# "请输入246个字符。"
			showAutoHideMessage( 3.0, mbmsgs[0x11c0], "", pyOwner = self )
			return False
		return True

	def __onTextChange( self ) :
		self.__pyBtnSend.enable = True

	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def show( self, tongDBID ) :
		Window.show( self )
		self.__pyADBox.tabStop = True
		self.__tongDBID = tongDBID

	def hide( self ):
		Window.hide( self )
		self.__pyADBox.tabStop = False
		self.__tongDBID = 0
		
	def onLeaveWorld( self ):
		self.hide()

	@staticmethod
	def instance():
		if TongInvite.__instance is None:
			TongInvite.__instance = TongInvite()
		return TongInvite.__instance
