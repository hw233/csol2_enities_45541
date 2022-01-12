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
# ������������ߴ�������
# ----------------------------------------------------------------
from AbstractTemplates import MultiLngFuncDecorator

class deco_MiniMapResizePyItems( MultiLngFuncDecorator ) :

	@staticmethod
	def locale_big5( SELF ) :
		"""
		����������µ���������������ĳߴ�
		"""
		pyBtn = SELF._MiniMap__pyLVBtn
		pyBtn.pyText_.fontSize = 11
		pyBtn.pyText_.charSpace = -3
		pyBtn._Button__textPos = pyBtn.pyText_.pos


class MiniMap( RootGUI ) :
	__cc_keyhelp_trigger		= "config/client/help/KeyHelper.xml"	# ���������

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
		self.__mapFolder = ""						# ��ͼ�����ļ�������
		self.__updateTimerID = 0					# ���µ�ͼ�� Timer ID
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

		self.__pyBigMapBtn = Button( wnd.ring.fullBtn )						# ��ʾȫ��ͼ��ť
		self.__pyBigMapBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBigMapBtn.onLClick.bind( self.__onBigMapBtnClick )
		self.__pyControls.append( self.__pyBigMapBtn )

		self.__pyBigBtn = Button( wnd.ring.bigBtn )							# �Ŵ�ť
		self.__pyBigBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBigBtn.onLClick.bind( self.__onBigBtnClick )
		self.__pySmallBtn = Button( wnd.ring.smallBtn )						# ��С��ť
		self.__pySmallBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pySmallBtn.onLClick.bind( self.__onSmallBtnClick )

		self.__pyHelpBtn = Button( wnd.ring.helpBtn )						# ��ʾϵͳ����
		self.__pyHelpBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyHelpBtn.highlightForeColor = ( 255.0, 240.0, 107.0 )
		self.__pyHelpBtn.onLClick.bind( self.__onHelpBtnClick )
		self.__pyHelpBtn.onMouseEnter.bind( self.__onUIMouseEnter )
		self.__pyHelpBtn.onMouseLeave.bind( self.__onUIMouseLeave )
		self.__pyControls.append( self.__pyHelpBtn )

		self.__pyTradeBtn = Button( wnd.ring.tradeBtn )						# ��ʾ�̳ǰ�ť
		self.__pyTradeBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyTradeBtn.highlightForeColor = ( 0.0, 228.0, 255.0 )
		self.__pyTradeBtn.pressedForeColor = ( 0.0, 228.0, 255.0)
		self.__pyTradeBtn.onLClick.bind( self.__onTradeBtnClick )
		self.__pyTradeBtn.onMouseEnter.bind( self.__onUIMouseEnter )
		self.__pyTradeBtn.onMouseLeave.bind( self.__onUIMouseLeave )
		self.__pyControls.append( self.__pyTradeBtn )

		self.__pySaleBtn = Button( wnd.ring.saleBtn )						# ���۰�ť
		self.__pySaleBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pySaleBtn.onLClick.bind( self.__onPopupSaleMenu )
		self.__pySaleBtn.onMouseEnter.bind( self.__onUIMouseEnter )
		self.__pySaleBtn.onMouseLeave.bind( self.__onUIMouseLeave )
		self.__pyControls.append( self.__pySaleBtn )

		self.__pyChallengeBtn = Button( wnd.ring.challengeBtn ) 				# ����NPC����ս
		self.__pyChallengeBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyChallengeBtn.highlightForeColor = ( 255.0, 240.0, 107.0 )
		self.__pyChallengeBtn.visible = False
		self.__pyChallengeBtn.onLClick.bind( self.__onShowReport )
		self.__pyControls.append( self.__pyChallengeBtn )

		self.__pyCityWarBtn = Button( wnd.ring.cityWarBtn )					# �����ս
		self.__pyCityWarBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyCityWarBtn.highlightForeColor = ( 255.0, 240.0, 107.0 )
		self.__pyCityWarBtn.visible = False
		self.__pyCityWarBtn.onLClick.bind( self.__onShowCityWar )
		self.__pyControls.append( self.__pyCityWarBtn )

		self.__pyActivityBtn = Button( wnd.ring.activeBtn )					# ���ʾ��ť
		self.__pyActivityBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyActivityBtn.highlightForeColor = ( 255.0, 240.0, 107.0 )
		self.__pyActivityBtn.enable = False
		self.__pyActivityBtn.onLClick.bind( self.__showActiveCalendar )
		self.__pyActivityBtn.onMouseEnter.bind( self.__onUIMouseEnter )
		self.__pyActivityBtn.onMouseLeave.bind( self.__onUIMouseLeave )
		self.__pyControls.append( self.__pyActivityBtn )

		self.__pyPixieBtn = Button( wnd.ring.btn_pixie )						# С���鹦�ܰ�ť
		self.__pyPixieBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyPixieBtn.highlightForeColor = ( 255.0, 240.0, 107.0 )
		self.__pyPixieBtn.onLClick.bind( self.__onPixieBtnClick)
		self.__pyPixieBtn.onMouseEnter.bind( self.__onUIMouseEnter )
		self.__pyPixieBtn.onMouseLeave.bind( self.__onUIMouseLeave )
		self.__pyControls.append( self.__pyPixieBtn )

		polygon = [ ( 6, 75 ), ( 27, 67 ), ( 38, 59 ), ( 49, 50 ), 		# Ϊ�Զ�Ѱ·��ť������������
					( 60, 36 ), ( 68, 31 ), ( 74, 40 ), ( 74, 48 ),
					( 69, 58 ), ( 55, 72 ), ( 36, 85 ), ( 28, 89 ),
					( 16, 90 ), ( 7, 83 ) ]
		self.__pyNavigateBtn = Button( wnd.ring.runBtn )	# �Զ�Ѱ·��ť
		self.__pyNavigateBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyNavigateBtn.onLClick.bind( self.__showNavigateWnd )
#		self.__pyNavigateBtn.texture = self.__getNavigateTexture()		# ��ȡ�Զ�Ѱ·��ť��ͼ�������ͷ����������
		self.__pyControls.append( self.__pyNavigateBtn )

		self.__pyMailFlag = GlitteryGUI( wnd.ring.mailBtn )					# δ���ʼ����
		self.__pyMailFlag.initAnimation( -1, 4, ( 2, 2 ) )	
		self.__pyMailFlag.cycle = 1
		self.__pyMailFlag.focus = True
		self.__pyMailFlag.onMouseEnter.bind( self.__onUIMouseEnter )
		self.__pyMailFlag.onMouseLeave.bind( self.__onUIMouseLeave )
		self.__pyMailFlag.onLClick.bind( self.__onMailClick )
		#self.__pyMailFlag.visible = False
		self.__pyControls.append( self.__pyMailFlag )
		
		

		self.__pyFamilyChallengeBtn = Button( wnd.ring.fcBtn )				# ������ս���
		self.__pyFamilyChallengeBtn.setStatesMapping( UIState.MODE_R1C1 )
		self.__pyFamilyChallengeBtn.onLClick.bind( self.__showFCStatus )
		self.__pyFamilyChallengeBtn.onMouseEnter.bind( self.__onUIMouseEnter )
		self.__pyFamilyChallengeBtn.onMouseLeave.bind( self.__onUIMouseLeave )
		self.__pyFamilyChallengeBtn.visible = False
		self.__pyFamilyChallengeBtn.texture = ""
		self.__pyControls.append( self.__pyFamilyChallengeBtn )

		self.__pyChangeLineCB = ODComboBox( wnd.ring.changeCB ) 				# ���������б��
		self.__pyChangeLineCB.autoSelect = True
		self.__pyChangeLineCB.ownerDraw = True
		self.__pyChangeLineCB.width = 63.0
		self.__pyChangeLineCB.onViewItemInitialized.bind( self.onInitialized_ )
		self.__pyChangeLineCB.onDrawItem.bind( self.onDrawItem_ )
		self.__pyChangeLineCB.onItemSelectChanged.bind( self.__onLineChange )

		self.__pyDamageBtn = Button( wnd.ring.damageBtn )					#�˺�ͳ��
		self.__pyDamageBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyDamageBtn.highlightForeColor = ( 255.0, 240.0, 107.0 )
		self.__pyDamageBtn.onLClick.bind( self.__onShowDamageStatis )
		self.__pyDamageBtn.onMouseEnter.bind( self.__onUIMouseEnter )
		self.__pyDamageBtn.onMouseLeave.bind( self.__onUIMouseLeave )
		self.__pyControls.append( self.__pyDamageBtn )
		
		self.__pyBtnFengQi = Button( wnd.ring.fengQiBtn )						#ҹս��������
		self.__pyBtnFengQi.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnFengQi.highlightForeColor = ( 255.0, 240.0, 107.0 )
		self.__pyBtnFengQi.visible = False
		self.__pyBtnFengQi.onLClick.bind( self.__onShowFengQi )
		self.__pyControls.append( self.__pyBtnFengQi )

		self.__pyBtnFhlt = Button( wnd.ring.fhltBtn )						#�������ս��ͳ��
		self.__pyBtnFhlt.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnFhlt.highlightForeColor = ( 255.0, 240.0, 107.0 )
		self.__pyBtnFhlt.visible = False
		self.__pyBtnFhlt.onLClick.bind( self.__onShowFhlt )
		self.__pyControls.append( self.__pyBtnFhlt )
		
		self.__pyBtnCFhlt = Button( wnd.ring.cfhltBtn )						#��Ӫ�������ս��ͳ��
		self.__pyBtnCFhlt.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnCFhlt.highlightForeColor = ( 255.0, 240.0, 107.0 )
		self.__pyBtnCFhlt.visible = False
		self.__pyBtnCFhlt.onLClick.bind( self.__onShowCFhlt )
		self.__pyControls.append( self.__pyBtnCFhlt )

		self.__pyMapPanel = MapPanel( wnd.ring.mapPanel )
		self.__pyPixieMenu = PixieMenu()								# С����˵�
		self.__pyPixieBubble = PixieBubble()							# С�����л�����

		self.__rangePolygon = Polygon([
										( 52, 88 ), ( 69, 39 ), ( 119, 21 ), ( 153, 20 ),
										( 200, 38 ), ( 218, 88 ), ( 216, 118 ), ( 200, 154 ),
										( 164, 179 ), ( 138, 184 ), ( 105, 180 ), ( 67, 151 ),
										( 53, 125 ),
									  ])											# ������������

		self.__hpCBID = 0
		self.__acCBID = 0

		# -------------------------------------------------
		# ���ñ�ǩ
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
		���µ������ֿؼ���ǩ�ĳߴ�
		Ĭ�ϰ汾�²������κβ���
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
			pyViewItem.pyLabel.foreColor = pyPanel.itemSelectedForeColor			# ѡ��״̬�µ�ǰ��ɫ
			pyViewItem.color = pyPanel.itemSelectedBackColor				# ѡ��״̬�µı���ɫ
		elif pyViewItem.highlight :
			pyViewItem.pyLabel.foreColor = pyPanel.itemHighlightForeColor		# ����״̬�µ�ǰ��ɫ
			pyViewItem.color = pyPanel.itemHighlightBackColor				# ����״̬�µı���ɫ
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
		��ȡ���Զ�Ѱ·��ͼƬ
		"""
		return "guis/general/minimap/autorunbtn.dds"

	def __loadHelpTriggers( self ):
		"""
		���ػ����
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
		��ʾ/����С��ͼ
		"""
		if self.__pyRing.visible:
			self.__onHideRing( self.__pyBtnHide )
		else:
			self.__onShowRing( self.__pyBtnShow )

	def __onNPCChallengeStateChange( self, remainTime ):
		"""
		�ڼ���NPC��״̬����Ч
		"""
		self.__pyChallengeBtn.visible = remainTime > 0

	def __onFamilyChallengeStateChange ( self, relatedFamily ) :
		"""
		������ս״̬�ı䣨��ʼ/������
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
		���������ʱ���õȼ���ť��˸
		"""
		if not rds.statusMgr.isInWorld():
			return
		self.__flashHelpBtn()
		BigWorld.cancelCallback( self.__hpCBID )
		self.__hpCBID = BigWorld.callback( 300, self.__unflashHelpBtn )

	def __onAcivityStart( self ):
		"""
		����쿪ʼʱ������ʾ��ť��˸
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
		�Ƿ��ڽ�ɫ����״̬��
		"""
		self.__pyChangeLineCB.enable = isControlled
		if not isControlled:
			self.__pyChangeLineCB.collapse()

	def __onRoleStateChange( self, state ):
		"""
		�Ƿ���ս��״̬��
		"""
		self.__pyChangeLineCB.enable = state != csdefine.ENTITY_STATE_FIGHT
		if state == csdefine.ENTITY_STATE_FIGHT:
			self.__pyChangeLineCB.collapse()

	def __onEnableActivityBtn( self ):
		"""
		���ճ̻���ݶ���ʼ����֮���ټ�����ʾ��ť
		"""
		self.__pyActivityBtn.enable = True

	def __onEnterCityWar( self, warRemainTime, tongInfos ):
		"""
		�������ս����
		"""
		self.__pyCityWarBtn.visible = warRemainTime > 0

	def __onLeaveCityWar( self, role ):
		"""
		�뿪����ս����
		"""
		self.__pyCityWarBtn.visible = False

	# -------------------------------------------------
	def __updatePosition( self, player ) :
		"""
		��ʱ�������λ��
		"""
		pos = player.position
		self.__pyTxtPos.text = "%d:%d �߶�:%d" % ( pos.x, pos.z, pos.y )

	def __update( self ) :
		"""
		��ʱ���µ�ͼ����
		"""
		if rds.statusMgr.isInWorld() :
			player = BigWorld.player()
			self.__updatePosition( player )
			self.__pyMapPanel.update( self.__mapFolder, player )

	# -------------------------------------------------
	def __flashHelpBtn( self ) :
		"""
		��˸������ť
		"""
		self.__pyHelpBtn.texture = self.__cc_btnMSize_animate
		self.__pyHelpBtn.setStatesMapping( UIState.MODE_R1C1 )

	def __unflashHelpBtn( self ) :
		"""
		ȡ��������ť����˸
		"""
		self.__pyHelpBtn.texture = self.__cc_btnMSize_common
		self.__pyHelpBtn.setStatesMapping( UIState.MODE_R2C2 )
		BigWorld.cancelCallback( self.__hpCBID )
		

	def __flashActiveBtn( self ):
		"""
		��˸���ʾ��ť
		"""
		self.__pyActivityBtn.texture = self.__cc_btnMSize_animate
		self.__pyActivityBtn.setStatesMapping( UIState.MODE_R1C1 )

	def __unflashActiveBtn( self ):
		self.__pyActivityBtn.texture = self.__cc_btnMSize_common
		self.__pyActivityBtn.setStatesMapping( UIState.MODE_R2C2 )

#	def __flashProduceBtn( self ):
#		"""
#		��˸������ť
#		"""
#		self.__pyHelpBtn.texture = self.__cc_btnMSize_animate
#		self.__pyHelpBtn.setStatesMapping( UIState.MODE_R1C1 )
#
#	def __unflashProduceBtn( self ):
#		"""
#		ֹͣ��˸������ť
#		"""
#		self.__pyHelpBtn.texture = self.__cc_btnMSize_common
#		self.__pyHelpBtn.setStatesMapping( UIState.MODE_R2C2 )

	# -------------------------------------------------
	def __onBigMapBtnClick( self ) :
		"""
		�����ȫ��ͼ��ť��
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_BIGMAP" )

	def __onBigBtnClick( self ) :
		"""
		������Ŵ�ť��
		"""
		scale = self.__pyMapPanel.scale
		if scale < 1.0 :
			self.__pyMapPanel.scale = 1.0
		elif scale < self.cc_maxScale :
			self.__pyMapPanel.scale += 0.5

	def __onSmallBtnClick( self ) :
		"""
		�������С��ť��
		"""
		scale = self.__pyMapPanel.scale
		if scale > 1.0 :
			self.__pyMapPanel.scale = 1.0
		elif scale > self.cc_minScale :
			self.__pyMapPanel.scale -= 0.25

	def __onHelpBtnClick( self ) :
		"""
		�����ϵͳ������ť��
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_HELP_WINDOW" )

#	def __onLVBtnClick( self, ) :
#		"""
#		������ȼ�������ʾ��ť��
#		"""
#		self.__unflashLevelBtn()
#		ECenter.fireEvent( "EVT_ON_TOGGLE_UPGRADE_HELPER" )

	def __onTradeBtnClick( self ) :
		"""
		������̳ǰ�ť��
		"""
		if Language.LANG == Language.LANG_GBK:
			if BigWorld.player().level < 30:
#			 "������30�����޷��鿴�̳ǡ�"
				self.__showMessage( mbmsgs[0x0461] )
				return
		ECenter.fireEvent( "EVT_ON_TOGGLE_SPECIAL_SHOP" )

	def __onPopupSaleMenu( self ) :
		"""
		�������۲˵�
		"""
		ConsignmentSaleMenu.instance().show()

	def __onPixieBtnClick( self ) :
		"""���С���鰴ť"""
		self.__pyPixieMenu.popup()
		self.__pyPixieMenu.right = self.__pyPixieBtn.leftToScreen + 2.0
		self.__pyPixieMenu.top = self.__pyPixieBtn.bottomToScreen

	def __onShowPixieGossip( self, msg ) :
		"""С������������"""
		self.__pyPixieBubble.show( msg )
		self.__pyPixieBubble.right = self.__pyHelpBtn.leftToScreen + 10
		self.__pyPixieBubble.top = self.__pyHelpBtn.topToScreen
	
	def __onHideMiniMap( self, spaceLabel ):
		"""
		����lol��������С��ͼ
		"""
		self.hide()
	
	def __onShowMiniMap( self ):
		"""
		�뿪lol������ʾС��ͼ
		"""
		self.show()
	
	def __onEnterFengQi( self, role ):
		"""
		����ҹս����ս��
		"""
		self.__pyBtnFengQi.visible = True
	
	def __onExitFengQi( self, role ):
		"""
		����ҹս����ս��
		"""
		self.__pyBtnFengQi.visible = False
	
	def __onEnterFhlt( self, remainTime, tongInfos ):
		"""
		����������
		"""
		self.__pyBtnFhlt.visible = True
	
	def __onExitFhlt( self ):
		"""
		�뿪�������
		"""
		self.__pyBtnFhlt.visible = False
		
	def __onEnterCFhlt( self, entity, remainTime, tongInfos ):
		"""
		������Ӫ�������
		"""
		self.__pyBtnCFhlt.visible = True
	
	def __onExitCFhlt( self,entity ):
		"""
		�뿪��Ӫ�������
		"""
		self.__pyBtnCFhlt.visible = False

	def __onShowReport( self ):
		"""
		�ڼ���NPC��״̬����Ч
		"""
		ECenter.fireEvent( "EVT_ON_TOGGLE_STAT_WINDOW" )

	def __showActiveCalendar( self ):
		"""
		��������ʾ��ť��
		"""
		self.__unflashActiveBtn()
		BigWorld.cancelCallback( self.__acCBID )
		ECenter.fireEvent( "EVT_ON_TOGGLE_ACTIVITY_WINDOW" )

	def __showNavigateWnd( self ) :
		"""
		���Զ�Ѱ·����
		"""
		NavigateWindow.instance().show()

	def __showFCStatus( self ) :
		ECenter.fireEvent( "EVT_ON_SHOW_FAMILY_CHALLENGING_STATUS" )

	def __notifyNewMail( self ) :
		"""
		��δ���ʼ�ʱ�����ʼ���ʾ
		"""	
		self.__pyMailFlag.startFlash()
	

		
	"""
	def __onMailNotify ( self ) :
		
		��¼ʱ�ʼ�ͼ����ʾ��״̬
		
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
		û�����ʼ�ʱ�ر��ʼ���ʾ
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
			return #��ɫ��ǰ����
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
		�����밴ťʱ���ã��ɶ����ť����
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
		����뿪��ťʱ���ã��ɶ����ť����
		"""
		toolbox.infoTip.hide()
	
	def __onMailClick( self, pyMail ):
		"""
		����ʼ�ͼ��
		"""
		self.__pyMailFlag.focus = True
		player = BigWorld.player()
		msg = ""
		for id, mail in player.mails.iteritems() :
			if  not player.hasReadAllMails() :   #���ʼ�δ��
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
					if player.hasReadAllMailsHints() : #�����ʼ���ʾ֮�󣬲�ѯ�Ƿ�û���µ��ʼ���ʾ��ȷ���ʼ�ͼ���Ƿ���˸
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
		��������ս����
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_INTERGRAL_WINDOW" )

#	def __onShowProApproach( self, pyBtn ):
#		"""
#		��������;������
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
		ҹս������
		"""
		if not BigWorld.player().onFengQi:return
		ECenter.fireEvent( "EVT_ON_SHOW_FENGQI_RANK_WINDOW" )
	
	def __onShowFhlt( self, pyBtn ):
		"""
		�������
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_FHLTRANK_WND" )
		
	def __onShowCFhlt( self, pyBtn ):
		"""
		��Ӫ�������
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_CAMP_FHLTRANK_WND" )

	def __isSubItemsMouseHit( self ) :
		for pyItem in self.__pyControls :
			if pyItem.isMouseHit() :
				return True
		return False

	def __onStatusMsg( self, statusID, msg ) :
		"""
		�յ��󶨵�״̬��Ϣ
		"""
		self.__updatePkFlag()

	def __updatePkFlag( self ) :
		"""
		����С��ͼ�ϱ�ʾPK״̬�ı��
		"""
		player = BigWorld.player()
		if player.currAreaCanPk() :
			self.__pyTxtArea.color = 255,0,0,255
		else :
			self.__pyTxtArea.color = 170,240,248,255

	def __refreshSpaceLines( self, lineAmount ) :
		"""
		ˢ�µ�ǰ��ͼ������
		"""
		if self.__pyChangeLineCB.itemCount == lineAmount :
			return
		self.__pyChangeLineCB.clearItems()
		if lineAmount > 0 :
			for lineIndex in xrange( 1, lineAmount + 1 ):
				self.__pyChangeLineCB.addItem( "%d"%lineIndex )

	def __selectSpaceLine( self, lineNo ) :
		"""
		ѡ��ǰ��ͼ��ĳ����
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
		�ж�����Ƿ���ڶ����������
		"""
		return self.__rangePolygon.isPointIn( self.mousePos ) \
		or self.__isSubItemsMouseHit()

	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onEnterWorld( self ) :
		"""
		��������ʱ��Ϊ���� UI ��ʾ
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
		�뿪����ʱ����
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
		����ҽ���ĳ������ʱ��������
		"""
		#if newArea.isSubArea() :								# �߻�Ҫ��ֻ��ʾ�������ƣ�����ʾ��������
			#name = "%s:%s" % ( newArea.spaceName, name )		# �����ʱע������hyw--2009.05.05��
		# �߻�Ҫ��ֻ��С��ͼ������ʾ"����*��"
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
		���������ڵĵ�ͼ�ܷ����Լ���λ����Ϣ�Ա��������׷��
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
	__common_fc = ( 0, 255, 0, 255 )	#��ͨ����ɫ
	__hign_fc = ( 255, 0, 0, 255 )	#��������ɫ
	
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
		
