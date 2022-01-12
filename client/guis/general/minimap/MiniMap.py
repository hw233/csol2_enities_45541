# -*- coding: gb18030 -*-
#
# $Id: MiniMap.py,v 1.14 2008-08-26 02:16:03 huangyongwei Exp $

"""
implement minimap class

2006.12.07 : writen by huangyongwei
2007.12.21 : rewriten by huangyongwei( split a big map in to lots of small maps )
2008.04.04 : rewriten by huangyongwei( new version )
2013-6-11  : add new function __onMailClick( )
"""

import csdefine
import csstatus
import event.EventCenter as ECenter
import gbref
import Timer
import csconst
from guis import *
import Language
import reimpl_miniMap
import Time
from guis.common.RootGUI import RootGUI
from guis.common.PyGUI import PyGUI
from guis.controls.StaticLabel import StaticLabel
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.controls.ODComboBox import ODComboBox
from guis.controls.ComboBox import ComboBox
from guis.controls.ComboBox import ComboItem
from guis.general.navigatewnd.NavigateWindow import NavigateWindow
from guis.general.damagestatic.StatisWindow import StatisWindow
from NavigationButton import NavigationButton
from ConsignmentSale import ConsignmentSaleMenu
from PixieCote import PixieMenu, PixieBubble
from GlitteryGUI import GlitteryGUI
from AreaName import AreaName
from MapPanel import MapPanel
from Function import Functor
from cscustom import Polygon
from LabelGather import labelGather
from config.client.help.KeyHelperContent import ShowLevelDatas
from config.client.msgboxtexts import Datas as mbmsgs
from bwdebug import *
from ChatFacade import chatFacade
import Define

# ----------------------------------------------------------------
# 调整属性字体尺寸修饰器
# ----------------------------------------------------------------
from AbstractTemplates import MultiLngFuncDecorator

class deco_MiniMapResizePyItems( MultiLngFuncDecorator ) :

	@staticmethod
	def locale_big5( SELF ) :
		"""
		繁体版下重新调整部分属性字体的尺寸
		"""
		pyBtn = SELF._MiniMap__pyLVBtn
		pyBtn.pyText_.fontSize = 11
		pyBtn.pyText_.charSpace = -3
		pyBtn._Button__textPos = pyBtn.pyText_.pos


class MiniMap( RootGUI ) :
	__cc_keyhelp_trigger		= "config/client/help/KeyHelper.xml"	# 活动帮助触发

	cc_minScale = 0.5
	cc_maxScale = 3.5

	__cc_btnMSize_common = "guis/general/minimap/btn_m.dds"
	__cc_btnMSize_animate = "guis/general/minimap/flashbtn_M.texanim"

	def __init__( self ) :
		wnd = GUI.load( "guis/general/minimap/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "TOP"
		self.moveFocus = False
		self.posZSegment = ZSegs.L4
		self.activable_ = False
		self.escHide_ = False

		self.__pyMsgBox = None
		self.__pyControls = []
		self.__mapFolder = ""						# 地图数据文件夹名称
		self.__updateTimerID = 0					# 更新地图的 Timer ID
		self.triggerLevels = []
		self.__loadHelpTriggers()
		self.__initialize( wnd )

		self.__triggers = {}
		self.__registerTriggers()
		self.__resizePyItems()

		chatFacade.bindStatus( csstatus.ROLE_ENTER_PK_FORBIDEN_AREA, self.__onStatusMsg )
		chatFacade.bindStatus( csstatus.ROLE_LEAVE_PK_FORBIDEN_AREA, self.__onStatusMsg )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		self.__pyTitle = Title( wnd.title )
		
		self.__pyTxtArea = StaticText( wnd.title.tbArea.lbText )
		self.__pyTxtArea.fontSize = 12
		self.__pyTxtPos = StaticText( wnd.title.tbPos.lbText )
		self.__pyTxtPos.fontSize = 12
		self.__pyTxtPos.color = 170,240,248,255
		
		self.__pyRing = PyGUI( wnd.ring )
		
		self.__pyBtnShow = Button( wnd.btnShow )
		self.__pyBtnShow.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnShow.visible = False
		self.__pyBtnShow.onLClick.bind( self.__onShowRing )
		
		self.__pyBtnHide = Button( wnd.btnHide )
		self.__pyBtnHide.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnHide.onLClick.bind( self.__onHideRing )

		self.__ringFader = wnd.ring.fader
		self.__ringFader.speed = 0.5
		self.__ringFader.value = 1.0
		self.__fadeCBID = 0

		self.__pyBigMapBtn = Button( wnd.ring.fullBtn )						# 显示全地图按钮
		self.__pyBigMapBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBigMapBtn.onLClick.bind( self.__onBigMapBtnClick )
		self.__pyControls.append( self.__pyBigMapBtn )

		self.__pyBigBtn = Button( wnd.ring.bigBtn )							# 放大按钮
		self.__pyBigBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBigBtn.onLClick.bind( self.__onBigBtnClick )
		self.__pySmallBtn = Button( wnd.ring.smallBtn )						# 缩小按钮
		self.__pySmallBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pySmallBtn.onLClick.bind( self.__onSmallBtnClick )

		self.__pyHelpBtn = Button( wnd.ring.helpBtn )						# 显示系统帮助
		self.__pyHelpBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyHelpBtn.highlightForeColor = ( 255.0, 240.0, 107.0 )
		self.__pyHelpBtn.onLClick.bind( self.__onHelpBtnClick )
		self.__pyHelpBtn.onMouseEnter.bind( self.__onUIMouseEnter )
		self.__pyHelpBtn.onMouseLeave.bind( self.__onUIMouseLeave )
		self.__pyControls.append( self.__pyHelpBtn )

		self.__pyTradeBtn = Button( wnd.ring.tradeBtn )						# 显示商城按钮
		self.__pyTradeBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyTradeBtn.highlightForeColor = ( 0.0, 228.0, 255.0 )
		self.__pyTradeBtn.pressedForeColor = ( 0.0, 228.0, 255.0)
		self.__pyTradeBtn.onLClick.bind( self.__onTradeBtnClick )
		self.__pyTradeBtn.onMouseEnter.bind( self.__onUIMouseEnter )
		self.__pyTradeBtn.onMouseLeave.bind( self.__onUIMouseLeave )
		self.__pyControls.append( self.__pyTradeBtn )

		self.__pySaleBtn = Button( wnd.ring.saleBtn )						# 寄售按钮
		self.__pySaleBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pySaleBtn.onLClick.bind( self.__onPopupSaleMenu )
		self.__pySaleBtn.onMouseEnter.bind( self.__onUIMouseEnter )
		self.__pySaleBtn.onMouseLeave.bind( self.__onUIMouseLeave )
		self.__pyControls.append( self.__pySaleBtn )

		self.__pyChallengeBtn = Button( wnd.ring.challengeBtn ) 				# 家族NPC争夺战
		self.__pyChallengeBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyChallengeBtn.highlightForeColor = ( 255.0, 240.0, 107.0 )
		self.__pyChallengeBtn.visible = False
		self.__pyChallengeBtn.onLClick.bind( self.__onShowReport )
		self.__pyControls.append( self.__pyChallengeBtn )

		self.__pyCityWarBtn = Button( wnd.ring.cityWarBtn )					# 帮会夺城战
		self.__pyCityWarBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyCityWarBtn.highlightForeColor = ( 255.0, 240.0, 107.0 )
		self.__pyCityWarBtn.visible = False
		self.__pyCityWarBtn.onLClick.bind( self.__onShowCityWar )
		self.__pyControls.append( self.__pyCityWarBtn )

		self.__pyActivityBtn = Button( wnd.ring.activeBtn )					# 活动提示按钮
		self.__pyActivityBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyActivityBtn.highlightForeColor = ( 255.0, 240.0, 107.0 )
		self.__pyActivityBtn.enable = False
		self.__pyActivityBtn.onLClick.bind( self.__showActiveCalendar )
		self.__pyActivityBtn.onMouseEnter.bind( self.__onUIMouseEnter )
		self.__pyActivityBtn.onMouseLeave.bind( self.__onUIMouseLeave )
		self.__pyControls.append( self.__pyActivityBtn )

		self.__pyPixieBtn = Button( wnd.ring.btn_pixie )						# 小精灵功能按钮
		self.__pyPixieBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyPixieBtn.highlightForeColor = ( 255.0, 240.0, 107.0 )
		self.__pyPixieBtn.onLClick.bind( self.__onPixieBtnClick)
		self.__pyPixieBtn.onMouseEnter.bind( self.__onUIMouseEnter )
		self.__pyPixieBtn.onMouseLeave.bind( self.__onUIMouseLeave )
		self.__pyControls.append( self.__pyPixieBtn )

		polygon = [ ( 6, 75 ), ( 27, 67 ), ( 38, 59 ), ( 49, 50 ), 		# 为自动寻路按钮定义多边形区域
					( 60, 36 ), ( 68, 31 ), ( 74, 40 ), ( 74, 48 ),
					( 69, 58 ), ( 55, 72 ), ( 36, 85 ), ( 28, 89 ),
					( 16, 90 ), ( 7, 83 ) ]
		self.__pyNavigateBtn = Button( wnd.ring.runBtn )	# 自动寻路按钮
		self.__pyNavigateBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyNavigateBtn.onLClick.bind( self.__showNavigateWnd )
#		self.__pyNavigateBtn.texture = self.__getNavigateTexture()		# 获取自动寻路按钮贴图（简体版和繁体版有区别）
		self.__pyControls.append( self.__pyNavigateBtn )

		self.__pyMailFlag = GlitteryGUI( wnd.ring.mailBtn )					# 未读邮件标记
		self.__pyMailFlag.initAnimation( -1, 4, ( 2, 2 ) )	
		self.__pyMailFlag.cycle = 1
		self.__pyMailFlag.focus = True
		self.__pyMailFlag.onMouseEnter.bind( self.__onUIMouseEnter )
		self.__pyMailFlag.onMouseLeave.bind( self.__onUIMouseLeave )
		self.__pyMailFlag.onLClick.bind( self.__onMailClick )
		#self.__pyMailFlag.visible = False
		self.__pyControls.append( self.__pyMailFlag )
		
		

		self.__pyFamilyChallengeBtn = Button( wnd.ring.fcBtn )				# 家族挑战标记
		self.__pyFamilyChallengeBtn.setStatesMapping( UIState.MODE_R1C1 )
		self.__pyFamilyChallengeBtn.onLClick.bind( self.__showFCStatus )
		self.__pyFamilyChallengeBtn.onMouseEnter.bind( self.__onUIMouseEnter )
		self.__pyFamilyChallengeBtn.onMouseLeave.bind( self.__onUIMouseLeave )
		self.__pyFamilyChallengeBtn.visible = False
		self.__pyFamilyChallengeBtn.texture = ""
		self.__pyControls.append( self.__pyFamilyChallengeBtn )

		self.__pyChangeLineCB = ODComboBox( wnd.ring.changeCB ) 				# 换线下拉列表框
		self.__pyChangeLineCB.autoSelect = True
		self.__pyChangeLineCB.ownerDraw = True
		self.__pyChangeLineCB.width = 63.0
		self.__pyChangeLineCB.onViewItemInitialized.bind( self.onInitialized_ )
		self.__pyChangeLineCB.onDrawItem.bind( self.onDrawItem_ )
		self.__pyChangeLineCB.onItemSelectChanged.bind( self.__onLineChange )

		self.__pyDamageBtn = Button( wnd.ring.damageBtn )					#伤害统计
		self.__pyDamageBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyDamageBtn.highlightForeColor = ( 255.0, 240.0, 107.0 )
		self.__pyDamageBtn.onLClick.bind( self.__onShowDamageStatis )
		self.__pyDamageBtn.onMouseEnter.bind( self.__onUIMouseEnter )
		self.__pyDamageBtn.onMouseLeave.bind( self.__onUIMouseLeave )
		self.__pyControls.append( self.__pyDamageBtn )
		
		self.__pyBtnFengQi = Button( wnd.ring.fengQiBtn )						#夜战凤栖总评
		self.__pyBtnFengQi.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnFengQi.highlightForeColor = ( 255.0, 240.0, 107.0 )
		self.__pyBtnFengQi.visible = False
		self.__pyBtnFengQi.onLClick.bind( self.__onShowFengQi )
		self.__pyControls.append( self.__pyBtnFengQi )

		self.__pyBtnFhlt = Button( wnd.ring.fhltBtn )						#烽火连天战场统计
		self.__pyBtnFhlt.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnFhlt.highlightForeColor = ( 255.0, 240.0, 107.0 )
		self.__pyBtnFhlt.visible = False
		self.__pyBtnFhlt.onLClick.bind( self.__onShowFhlt )
		self.__pyControls.append( self.__pyBtnFhlt )
		
		self.__pyBtnCFhlt = Button( wnd.ring.cfhltBtn )						#阵营烽火连天战场统计
		self.__pyBtnCFhlt.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnCFhlt.highlightForeColor = ( 255.0, 240.0, 107.0 )
		self.__pyBtnCFhlt.visible = False
		self.__pyBtnCFhlt.onLClick.bind( self.__onShowCFhlt )
		self.__pyControls.append( self.__pyBtnCFhlt )

		self.__pyMapPanel = MapPanel( wnd.ring.mapPanel )
		self.__pyPixieMenu = PixieMenu()								# 小精灵菜单
		self.__pyPixieBubble = PixieBubble()							# 小精灵闲话泡泡

		self.__rangePolygon = Polygon([
										( 52, 88 ), ( 69, 39 ), ( 119, 21 ), ( 153, 20 ),
										( 200, 38 ), ( 218, 88 ), ( 216, 118 ), ( 200, 154 ),
										( 164, 179 ), ( 138, 184 ), ( 105, 180 ), ( 67, 151 ),
										( 53, 125 ),
									  ])											# 定义多边形区域

		self.__hpCBID = 0
		self.__acCBID = 0

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyHelpBtn, "minmap:main", "btnHelp" )
#		labelGather.setPyBgLabel( self.__pyTradeBtn, "minmap:main", "btnTrade" )
		labelGather.setPyBgLabel( self.__pyCityWarBtn, "minmap:main", "btnCityWar" )
		labelGather.setPyBgLabel( self.__pyActivityBtn, "minmap:main", "btnActive" )
		labelGather.setPyBgLabel( self.__pyFamilyChallengeBtn, "minmap:main", "btnFC")
		labelGather.setPyBgLabel( self.__pyDamageBtn, "minmap:main", "btnDamage")
		labelGather.setPyBgLabel( self.__pyChallengeBtn, "minmap:main", "btnChallenge" )
		labelGather.setPyBgLabel( self.__pyPixieBtn, "minmap:main", "btn_pixie" )
		labelGather.setLabel( wnd.ring.stEast, "minmap:main", "stEast" )
		labelGather.setLabel( wnd.ring.stWest, "minmap:main", "stWest" )
		labelGather.setLabel( wnd.ring.stSouth, "minmap:main", "stSouth" )
		labelGather.setLabel( wnd.ring.stNorth, "minmap:main", "stNorth" )

	@deco_MiniMapResizePyItems
	def __resizePyItems( self ) :
		"""
		重新调整部分控件标签的尺寸
		默认版本下不进行任何操作
		"""
		pass

	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_MINMAP"] = self.__toggleVisible
		self.__triggers["EVT_ON_ROLE_ENTER_AREA"] = self.onEnterArea
		self.__triggers["EVT_ON_ROLE_ENTER_NPC_CHALLENGE"] = self.__onNPCChallengeStateChange
		self.__triggers["EVT_ON_FAMILY_CHALLENGE_STATE_CHANGE"] = self.__onFamilyChallengeStateChange
		self.__triggers["EVT_ON_TOGGLE_FAMILY_LEAVE_WAR"] = self.__onRoleLeaveWorld
		self.__triggers["EVT_ON_ROLE_LEVEL_CHANGED"] = self.__onLevelChange
		self.__triggers["EVT_ON_ACTIVITY_SOON_START"] = self.__onAcivityStart
		self.__triggers["EVT_ON_ACTIVITY_SOON_END"] = self.__onAcivityEnd
		self.__triggers["EVT_ON_NOTIFY_NEW_MAIL"] = self.__notifyNewMail
		self.__triggers["EVT_ON_CANCEL_MAIL_NOTIFY"] = self.__cancelMailNotify
		self.__triggers["EVT_ON_CANCEL_MAIL_HINT_NOTIFY"] = self.__cancelMailHintNotify
		self.__triggers["EVT_ON_ROLE_CONTROLL_STATE_CHANGE"] = self.__onRoleControlChange
		self.__triggers["EVT_ON_ROLE_STATE_CHANGED"] = self.__onRoleStateChange
		self.__triggers["EVT_ON_ENABLE_ACTIVITY_BUTTON"] = self.__onEnableActivityBtn
		self.__triggers["EVT_ON_ENTER_CITYWAR_SPACE"] = self.__onEnterCityWar
		self.__triggers["EVT_ON_ROLE_LEAVE_CITYWAR_SPACE"] = self.__onLeaveCityWar
		self.__triggers["EVT_ON_STOP_LEVEL_HELP_NOTIFIER"] = self.__unflashHelpBtn
		self.__triggers["EVT_ON_ROLE_FLAGS_CHANGED"] = self.__onPlayerFlagsChanged
		self.__triggers["EVT_ON_SHOW_PIXIE_GOSSIP"] = self.__onShowPixieGossip
		self.__triggers["EVT_ON_SHOW_YXLMCOPY_MINIMAP"] = self.__onHideMiniMap
		self.__triggers["EVT_ON_HIDE_YXLMCOPY_MINIMAP"] = self.__onShowMiniMap
		self.__triggers["EVT_ON_FENGQI_ON_ENTER"] = self.__onEnterFengQi
		self.__triggers["EVT_ON_FENGQI_ON_EXIT"] = self.__onExitFengQi
		self.__triggers["EVT_ON_ENTER_FHLT_SPACE"] = self.__onEnterFhlt
		self.__triggers["EVT_ON_LEAVE_FHLT_SPACE"] = self.__onExitFhlt
		self.__triggers["EVT_ON_ENTER_CAMP_FHLT_SPACE"] = self.__onEnterCFhlt
		self.__triggers["EVT_ON_LEAVE_FHLT_SPACE"] = self.__onExitCFhlt
		for trigger in self.__triggers :
			ECenter.registerEvent( trigger, self )

	# -------------------------------------------------
	def onInitialized_( self, pyViewItem ):
		pyLabel = StaticLabel()
		pyLabel.crossFocus = True
		pyLabel.h_anchor = "CENTER"
		pyViewItem.addPyChild( pyLabel )
		pyViewItem.pyLabel = pyLabel

	def onDrawItem_( self, pyViewItem ):
		pyPanel = pyViewItem.pyPanel
		if pyViewItem.selected :
			pyViewItem.pyLabel.foreColor = pyPanel.itemSelectedForeColor			# 选中状态下的前景色
			pyViewItem.color = pyPanel.itemSelectedBackColor				# 选中状态下的背景色
		elif pyViewItem.highlight :
			pyViewItem.pyLabel.foreColor = pyPanel.itemHighlightForeColor		# 高亮状态下的前景色
			pyViewItem.color = pyPanel.itemHighlightBackColor				# 高亮状态下的背景色
		else :
			pyViewItem.pyLabel.foreColor = pyPanel.itemCommonForeColor
			pyViewItem.color = pyPanel.itemCommonBackColor
		lineStr = pyViewItem.listItem
		pyLabel = pyViewItem.pyLabel
		pyLabel.width = pyViewItem.width
		pyLabel.foreColor = 236, 218, 157
		pyLabel.left = 1.0
		pyLabel.top = 1.0
		pyLabel.text = labelGather.getText( "minmap:main", "lineNo" )%int( lineStr )

	@reimpl_miniMap.deco_guiMinMapNavigateTexture
	def __getNavigateTexture( self ):
		"""
		获取“自动寻路”图片
		"""
		return "guis/general/minimap/autorunbtn.dds"

	def __loadHelpTriggers( self ):
		"""
		加载活动触发
		"""
		sect = Language.openConfigSection( self.__cc_keyhelp_trigger )
		if sect is None :
			ERROR_MSG( "load config '%s' fail!" % self.__cc_keyhelp_trigger )
			return
		for tag, subSect in sect.items() :
			id = subSect.readString( "id" )
			self.triggerLevels.append( int( id ))

	def __toggleVisible( self ) :
		"""
		显示/隐藏小地图
		"""
		if self.__pyRing.visible:
			self.__onHideRing( self.__pyBtnHide )
		else:
			self.__onShowRing( self.__pyBtnShow )

	def __onNPCChallengeStateChange( self, remainTime ):
		"""
		在家族NPC赛状态下有效
		"""
		self.__pyChallengeBtn.visible = remainTime > 0

	def __onFamilyChallengeStateChange ( self, relatedFamily ) :
		"""
		家族挑战状态改变（开始/结束）
		"""
		player = BigWorld.player()
		if player.isFamilyChallenging() :
			self.__pyFamilyChallengeBtn.visible = True
			self.__pyFamilyChallengeBtn.texture = self.__cc_btnMSize_animate
		else :
			self.__pyFamilyChallengeBtn.visible = False
			self.__pyFamilyChallengeBtn.texture = ""

	def __onRoleLeaveWorld( self ):
		self.__pyChallengeBtn.visible = False

	def __onLevelChange( self, oldLevel, level ):
		"""
		当玩家升级时，让等级按钮闪烁
		"""
		if not rds.statusMgr.isInWorld():
			return
		self.__flashHelpBtn()
		BigWorld.cancelCallback( self.__hpCBID )
		self.__hpCBID = BigWorld.callback( 300, self.__unflashHelpBtn )

	def __onAcivityStart( self ):
		"""
		当活动快开始时，让提示按钮闪烁
		"""
		if not rds.statusMgr.isInWorld():
			return
		self.__flashActiveBtn()
		BigWorld.cancelCallback( self.__acCBID )
		self.__acCBID = BigWorld.callback( 300, self.__unflashActiveBtn )

	def __onAcivityEnd( self ):
		pass

	def __onRoleControlChange( self, isControlled ):
		"""
		是否在角色控制状态下
		"""
		self.__pyChangeLineCB.enable = isControlled
		if not isControlled:
			self.__pyChangeLineCB.collapse()

	def __onRoleStateChange( self, state ):
		"""
		是否在战斗状态下
		"""
		self.__pyChangeLineCB.enable = state != csdefine.ENTITY_STATE_FIGHT
		if state == csdefine.ENTITY_STATE_FIGHT:
			self.__pyChangeLineCB.collapse()

	def __onEnableActivityBtn( self ):
		"""
		等日程活动数据都初始化好之后，再激活活动提示按钮
		"""
		self.__pyActivityBtn.enable = True

	def __onEnterCityWar( self, warRemainTime, tongInfos ):
		"""
		进入帮会城战副本
		"""
		self.__pyCityWarBtn.visible = warRemainTime > 0

	def __onLeaveCityWar( self, role ):
		"""
		离开帮会城战副本
		"""
		self.__pyCityWarBtn.visible = False

	# -------------------------------------------------
	def __updatePosition( self, player ) :
		"""
		定时更新玩家位置
		"""
		pos = player.position
		self.__pyTxtPos.text = "%d:%d 高度:%d" % ( pos.x, pos.z, pos.y )

	def __update( self ) :
		"""
		定时更新地图内容
		"""
		if rds.statusMgr.isInWorld() :
			player = BigWorld.player()
			self.__updatePosition( player )
			self.__pyMapPanel.update( self.__mapFolder, player )

	# -------------------------------------------------
	def __flashHelpBtn( self ) :
		"""
		闪烁帮助按钮
		"""
		self.__pyHelpBtn.texture = self.__cc_btnMSize_animate
		self.__pyHelpBtn.setStatesMapping( UIState.MODE_R1C1 )

	def __unflashHelpBtn( self ) :
		"""
		取消帮助按钮的闪烁
		"""
		self.__pyHelpBtn.texture = self.__cc_btnMSize_common
		self.__pyHelpBtn.setStatesMapping( UIState.MODE_R2C2 )
		BigWorld.cancelCallback( self.__hpCBID )
		

	def __flashActiveBtn( self ):
		"""
		闪烁活动提示按钮
		"""
		self.__pyActivityBtn.texture = self.__cc_btnMSize_animate
		self.__pyActivityBtn.setStatesMapping( UIState.MODE_R1C1 )

	def __unflashActiveBtn( self ):
		self.__pyActivityBtn.texture = self.__cc_btnMSize_common
		self.__pyActivityBtn.setStatesMapping( UIState.MODE_R2C2 )

#	def __flashProduceBtn( self ):
#		"""
#		闪烁产出按钮
#		"""
#		self.__pyHelpBtn.texture = self.__cc_btnMSize_animate
#		self.__pyHelpBtn.setStatesMapping( UIState.MODE_R1C1 )
#
#	def __unflashProduceBtn( self ):
#		"""
#		停止闪烁产出按钮
#		"""
#		self.__pyHelpBtn.texture = self.__cc_btnMSize_common
#		self.__pyHelpBtn.setStatesMapping( UIState.MODE_R2C2 )

	# -------------------------------------------------
	def __onBigMapBtnClick( self ) :
		"""
		点击“全地图按钮”
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_BIGMAP" )

	def __onBigBtnClick( self ) :
		"""
		点击“放大按钮”
		"""
		scale = self.__pyMapPanel.scale
		if scale < 1.0 :
			self.__pyMapPanel.scale = 1.0
		elif scale < self.cc_maxScale :
			self.__pyMapPanel.scale += 0.5

	def __onSmallBtnClick( self ) :
		"""
		点击“缩小按钮”
		"""
		scale = self.__pyMapPanel.scale
		if scale > 1.0 :
			self.__pyMapPanel.scale = 1.0
		elif scale > self.cc_minScale :
			self.__pyMapPanel.scale -= 0.25

	def __onHelpBtnClick( self ) :
		"""
		点击“系统帮助按钮”
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_HELP_WINDOW" )

#	def __onLVBtnClick( self, ) :
#		"""
#		点击“等级帮助提示按钮”
#		"""
#		self.__unflashLevelBtn()
#		ECenter.fireEvent( "EVT_ON_TOGGLE_UPGRADE_HELPER" )

	def __onTradeBtnClick( self ) :
		"""
		点击“商城按钮”
		"""
		if Language.LANG == Language.LANG_GBK:
			if BigWorld.player().level < 30:
#			 "您低于30级，无法查看商城。"
				self.__showMessage( mbmsgs[0x0461] )
				return
		ECenter.fireEvent( "EVT_ON_TOGGLE_SPECIAL_SHOP" )

	def __onPopupSaleMenu( self ) :
		"""
		弹出寄售菜单
		"""
		ConsignmentSaleMenu.instance().show()

	def __onPixieBtnClick( self ) :
		"""点击小精灵按钮"""
		self.__pyPixieMenu.popup()
		self.__pyPixieMenu.right = self.__pyPixieBtn.leftToScreen + 2.0
		self.__pyPixieMenu.top = self.__pyPixieBtn.bottomToScreen

	def __onShowPixieGossip( self, msg ) :
		"""小精灵闲聊泡泡"""
		self.__pyPixieBubble.show( msg )
		self.__pyPixieBubble.right = self.__pyHelpBtn.leftToScreen + 10
		self.__pyPixieBubble.top = self.__pyHelpBtn.topToScreen
	
	def __onHideMiniMap( self, spaceLabel ):
		"""
		进入lol副本隐藏小地图
		"""
		self.hide()
	
	def __onShowMiniMap( self ):
		"""
		离开lol副本显示小地图
		"""
		self.show()
	
	def __onEnterFengQi( self, role ):
		"""
		进入夜战凤栖战场
		"""
		self.__pyBtnFengQi.visible = True
	
	def __onExitFengQi( self, role ):
		"""
		进入夜战凤栖战场
		"""
		self.__pyBtnFengQi.visible = False
	
	def __onEnterFhlt( self, remainTime, tongInfos ):
		"""
		进入烽火连天
		"""
		self.__pyBtnFhlt.visible = True
	
	def __onExitFhlt( self ):
		"""
		离开烽火连天
		"""
		self.__pyBtnFhlt.visible = False
		
	def __onEnterCFhlt( self, entity, remainTime, tongInfos ):
		"""
		进入阵营烽火连天
		"""
		self.__pyBtnCFhlt.visible = True
	
	def __onExitCFhlt( self,entity ):
		"""
		离开阵营烽火连天
		"""
		self.__pyBtnCFhlt.visible = False

	def __onShowReport( self ):
		"""
		在家族NPC赛状态下有效
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_STAT_WINDOW" )

	def __showActiveCalendar( self ):
		"""
		点击“活动提示按钮”
		"""
		self.__unflashActiveBtn()
		BigWorld.cancelCallback( self.__acCBID )
		ECenter.fireEvent( "EVT_ON_TOGGLE_ACTIVITY_WINDOW" )

	def __showNavigateWnd( self ) :
		"""
		打开自动寻路界面
		"""
		NavigateWindow.instance().show()

	def __showFCStatus( self ) :
		ECenter.fireEvent( "EVT_ON_SHOW_FAMILY_CHALLENGING_STATUS" )

	def __notifyNewMail( self ) :
		"""
		有未读邮件时开启邮件提示
		"""	
		self.__pyMailFlag.startFlash()
	

		
	"""
	def __onMailNotify ( self ) :
		
		登录时邮件图标显示的状态
		
		player = BigWorld.player()
		if not player.hasReadAllMails() :
			if not player.hasReadAllMailsHints() :
				self.__pyMailFlag.initAnimation( -1, 4, ( 2, 2 ) )
			else :
				self.__cancelMailHintNotify() 
		else :
			self.__pyMailFlag.hide()
	"""
	
	def __cancelMailNotify( self ) :
		"""
		没有新邮件时关闭邮件提示
		"""
		self.__pyMailFlag.hide()
		
	def __cancelMailHintNotify( self ) :
		self.__pyMailFlag.stopPlay_()
		util.setGuiState( self.__pyMailFlag.getGui(), ( 2, 2 ), ( 1,1 ) )
		

	def __onLineChange( self, selIndex ):
		player = BigWorld.player()
		selItem = self.__pyChangeLineCB.selItem
		if selItem is None:return
		try:
			spaceNum = BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_LINE_NUMBER )
		except:
			pass
#		spaceNumber = int( spaceNum )
		lineIndex = int( selItem )
		if spaceNum == selItem:
			return #角色当前分线
		elif player.getState() == csdefine.ENTITY_STATE_FIGHT:
			player.statusMessage( csstatus.ACCOUNT_SWITCH_LINE_FAILED1 )
#			self.__pyChangeLineCB.selIndex = curIndex
			return
		elif player.hasControlForbid( Define.CONTROL_FORBID_ROLE_MOVE ):
			player.statusMessage( csstatus.ACCOUNT_SWITCH_LINE_FAILED2 )
#			self.__pyChangeLineCB.selIndex = curIndex
			return
		self.__pyChangeLineCB.pyBox_.text = labelGather.getText( "minmap:main", "lineNo" )%lineIndex
		player.cell.switchSpaceLineNumber( lineIndex )

	def __onUIMouseEnter( self, pyGui ) :
		"""
		鼠标进入按钮时调用，可多个按钮共用
		"""
		msg = ""
		if pyGui == self.__pyTradeBtn :
			if BigWorld.player().level < 30 and \
			Language.LANG == Language.LANG_GBK:
				msg = labelGather.getText( "minmap:main", "tipsShopInvalid" )
		elif pyGui == self.__pyFamilyChallengeBtn :
			msg = labelGather.getText( "minmap:main", "tipsFChallenging" )
		elif pyGui == self.__pyMailFlag :
			msg = labelGather.getText( "minmap:main", "tipsMail" )
		elif pyGui == self.__pyPixieBtn :
			msg = labelGather.getText( "minmap:main", "btn_pixie_tips" )
		elif pyGui == self.__pyDamageBtn :
			msg = labelGather.getText( "minmap:main", "btnDamage_tips" )
		elif pyGui == self.__pyHelpBtn :
			msg = labelGather.getText( "minmap:main", "btnHelp_tips" )
		elif pyGui == self.__pyActivityBtn :
			msg = labelGather.getText( "minmap:main", "btnActive_tips" )
		elif pyGui == self.__pySaleBtn :
			msg = labelGather.getText( "minmap:main", "btnSale_tips" )
		if msg != "" :
			toolbox.infoTip.showESignTips( self, msg )

	def __onUIMouseLeave( self, pyBtn ) :
		"""
		鼠标离开按钮时调用，可多个按钮共用
		"""
		toolbox.infoTip.hide()
	
	def __onMailClick( self, pyMail ):
		"""
		点击邮件图标
		"""
		self.__pyMailFlag.focus = True
		player = BigWorld.player()
		msg = ""
		for id, mail in player.mails.iteritems() :
			if  not player.hasReadAllMails() :   #有邮件未读
				if player.hasReadAllMailsHints() : 	
					msg = mbmsgs[0x0445]			
					self.__cancelMailHintNotify()	
					break
				if mail["readedHintTime"]  == 0 :
					mail["readedHintTime"] = Time.Time.time()
					if ( mail["senderType"] == csdefine.MAIL_SENDER_TYPE_PLAYER or mail["senderType"] == csdefine.MAIL_SENDER_TYPE_RETURN ) :
						msg = mbmsgs[0x0444]%( mail["senderNamer"], mail["title"] )
					else :
						msg = mbmsgs[0x0446]%( mail["title"] )
					player.base.mailHint_readedNotify( id )
					if player.hasReadAllMailsHints() : #看完邮件提示之后，查询是否没有新的邮件提示，确定邮件图标是否闪烁
						self.__cancelMailHintNotify()
					break	
			else :	
				self.__pyMailFlag.hide()
		
		self.__showMessage( msg )

		#self.__pyMailFlag.focus = False


	def __showMessage( self, msg ) :
		def query( res ) :
			self.__pyMsgBox = None
		if self.__pyMsgBox is None :
			self.__pyMsgBox = showMessage( msg, "", MB_OK, query )
		else :
			self.__pyMsgBox.show( msg, "", query, None )

	def __onShowCityWar( self, pyBtn ):
		"""
		触发帮会城战积分
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_INTERGRAL_WINDOW" )

#	def __onShowProApproach( self, pyBtn ):
#		"""
#		触发产出途径界面
#		"""
#		self.__unflashProduceBtn()
#		ECenter.fireEvent( "EVT_ON_GET_ITEMS_WINDOW_SHOW" )

	def __onPlayerFlagsChanged( self, oldFlag ) :
		if ConsignmentSaleMenu.isInstantial() :
			ConsignmentSaleMenu.instance().resetMenuItem( oldFlag )

	def __onShowDamageStatis( self, pyBtn ):
		stWnd = StatisWindow.instance()
		if not stWnd.visible:
			stWnd.show()
		else:
			stWnd.hide()
	
	def __onShowFengQi( self, pyBtn ):
		"""
		夜战凤栖镇
		"""
		if not BigWorld.player().onFengQi:return
		ECenter.fireEvent( "EVT_ON_SHOW_FENGQI_RANK_WINDOW" )
	
	def __onShowFhlt( self, pyBtn ):
		"""
		烽火连天
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_FHLTRANK_WND" )
		
	def __onShowCFhlt( self, pyBtn ):
		"""
		阵营烽火连天
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_CAMP_FHLTRANK_WND" )

	def __isSubItemsMouseHit( self ) :
		for pyItem in self.__pyControls :
			if pyItem.isMouseHit() :
				return True
		return False

	def __onStatusMsg( self, statusID, msg ) :
		"""
		收到绑定的状态消息
		"""
		self.__updatePkFlag()

	def __updatePkFlag( self ) :
		"""
		更新小地图上表示PK状态的标记
		"""
		player = BigWorld.player()
		if player.currAreaCanPk() :
			self.__pyTxtArea.color = 255,0,0,255
		else :
			self.__pyTxtArea.color = 170,240,248,255

	def __refreshSpaceLines( self, lineAmount ) :
		"""
		刷新当前地图的线数
		"""
		if self.__pyChangeLineCB.itemCount == lineAmount :
			return
		self.__pyChangeLineCB.clearItems()
		if lineAmount > 0 :
			for lineIndex in xrange( 1, lineAmount + 1 ):
				self.__pyChangeLineCB.addItem( "%d"%lineIndex )

	def __selectSpaceLine( self, lineNo ) :
		"""
		选择当前地图的某条线
		"""
		if lineNo == 0:return
		self.__pyChangeLineCB.pyBox_.text = labelGather.getText( "minmap:main", "lineNo" )%lineNo
		selItem = self.__pyChangeLineCB.selItem
		if selItem is None:return
		if int( selItem ) == lineNo:
			return
		for pyViewItem in self.__pyChangeLineCB.pyViewItems :
			lineStr = pyViewItem.listItem
			if  int( lineStr ) == lineNo :
				self.__pyChangeLineCB.selItem = str( lineNo )
				break
			else :
				ERROR_MSG( "Can't find space line of no%i" % lineNo )

	def __onShowRing( self, pyBtn ):
		BigWorld.cancelCallback( self.__fadeCBID )
		self.__ringFader.value = 1.0
		self.__pyBtnShow.visible = False
		self.__pyBtnHide.visible = True
		self.__fadeCBID = BigWorld.callback( self.__ringFader.speed, self.showRing )
	
	def __onHideRing( self, pyBtn ):
		BigWorld.cancelCallback( self.__fadeCBID )
		self.__ringFader.value = 0.0
		self.__pyBtnShow.visible = True
		self.__pyBtnHide.visible = False
		self.__fadeCBID = BigWorld.callback( self.__ringFader.speed, self.hideRing )

	def hideRing( self ):
		self.__pyRing.visible = False

	def showRing( self ):
		self.__pyRing.visible = True
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseDown_( self, mods ) :
		RootGUI.onLMouseDown_( self, mods )
		return self.isMouseHit()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isMouseHit( self ) :
		"""
		判断鼠标是否点在多边形区域上
		"""
		return self.__rangePolygon.isPointIn( self.mousePos ) \
		or self.__isSubItemsMouseHit()

	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onEnterWorld( self ) :
		"""
		进入世界时作为常规 UI 显示
		"""
		self.__pyMapPanel.onEnterWorld()
		self.__updatePkFlag()
		self.__pyPixieMenu.onRoleEnterWorld()
		player = BigWorld.player()
		currArea = player.getCurrArea()
		if currArea:
			self.onEnterArea( currArea )
		if rds.ruisMgr.lolMiniMap.visible: return
		self.show()

	def onLeaveWorld( self ) :
		"""
		离开世界时隐藏
		"""
		self.__pyActivityBtn.enable = False
		self.__pyMapPanel.clearAllSigns()
		self.__pyChangeLineCB.clearItems()
		self.__pyFamilyChallengeBtn.visible = False
		self.__pyChallengeBtn.visible = False
		self.__pyCityWarBtn.visible = False
		self.__pyPixieMenu.onRoleLeaveWorld()
		self.hide()

	# ---------------------------------------
	def show( self ) :
		Timer.cancel( self.__updateTimerID )
		self.__updateTimerID = Timer.addTimer(0, 1.0, self.__update )

		spaceNum = 0
		maxLines = 0
		try:
			spaceNum = int( BigWorld.getSpaceDataFirstForKey( BigWorld.player().spaceID, csconst.SPACE_SPACEDATA_LINE_NUMBER ) )
			maxLines = int( BigWorld.getSpaceDataFirstForKey( BigWorld.player().spaceID, csconst.SPACE_SPACEDATA_MAX_LINE_NUMBER ) )
		except:
			pass
		self.__refreshSpaceLines( maxLines )
		self.__selectSpaceLine( spaceNum )
		self.__pyChangeLineCB.enable = maxLines > 0
		RootGUI.show( self )

	def hide( self ) :
		RootGUI.hide( self )
		Timer.cancel( self.__updateTimerID )
		self.__updateTimerID = 0


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEnterArea( self, newArea ) :
		"""
		当玩家进入某个区域时，被调用
		"""
		#if newArea.isSubArea() :								# 策划要求只显示区域名称，不显示场景名称
			#name = "%s:%s" % ( newArea.spaceName, name )		# 因此暂时注销掉（hyw--2009.05.05）
		# 策划要求只在小地图区域显示"副本*线"
		player = BigWorld.player()
		folder = player.getSpaceFolder()
		if folder is None :
			ERROR_MSG( "player is not in space!" )
		else :
			self.__mapFolder = folder
			self.__pyMapPanel.onEnterArea( newArea )

		spaceNum = 0
		maxLines = 0
		try :
			spaceNum = int( BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_LINE_NUMBER ) )
			maxLines = int( BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_MAX_LINE_NUMBER ) )
		except :
			pass
		self.__pyTxtArea.text = newArea.name
		self.__refreshSpaceLines( maxLines )
		self.__selectSpaceLine( spaceNum )
		self.__pyChangeLineCB.enable = maxLines > 0
		
from guis.common.ScriptObject import ScriptObject
from ChatFacade import chatFacade, chatObjTypes		
class Title( ScriptObject ):
	def __init__( self, panel ):
		ScriptObject.__init__( self, panel )
		self.itemInfo = None
		self.focus = True
		
	def checkArea( self ):
		"""
		检查玩家所在的地图能否发送自己的位置信息以被其他玩家追踪
		"""
		player = BigWorld.player()
		spaceLabel = player.getSpaceLabel()
		return spaceLabel in csconst.AREAS_CAN_BE_TRACE
		
	def onLClick_( self, mods ):
		ScriptObject.onLClick_( self, mods )
		if mods == MODIFIER_CTRL :
			if not self.checkArea():return
			self.itemInfo = LinkItem()
			chatFacade.insertChatObj( chatObjTypes.LINK, self.itemInfo )
			
class LinkItem( object ):
	__common_fc = ( 0, 255, 0, 255 )	#普通背景色
	__hign_fc = ( 255, 0, 0, 255 )	#高亮背景色
	
	def __init__( self ):
		self.id = 0
		self.name = ""
		self.linkMark = ""
		self.spaceLabel = ""
		self.cfc = self.__common_fc
		self.hfc = self.__hign_fc 
		self.__initPlayerPos()
		
	def __initPlayerPos( self ):
		player = BigWorld.player()
		wholeAreaName = player.getCurrWholeArea().name
		subAreaName = player.getCurrArea().name
		self.name = labelGather.getText( "minmap:viewName","posInfo", wholeAreaName,subAreaName )
		spaceLabel = player.getSpaceLabel()
		position = player.position
		positionList = [position[0], position[1], position[2]]
		spaceNum = int( BigWorld.getSpaceDataFirstForKey( BigWorld.player().spaceID, csconst.SPACE_SPACEDATA_LINE_NUMBER ) )
		self.linkMark = "goto:%s*%s*%s"%( positionList, spaceNum, spaceLabel )
		
