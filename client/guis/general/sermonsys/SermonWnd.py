# -*- coding: gb18030 -*-
#
# $Id: SermonWnd.py, fangpengjun Exp $

"""
implement SermonWnd class

"""
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.common.Window import Window
from guis.controls.StaticText import StaticText
from guis.controls.RichText import RichText
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ItemsPanel import ItemsPanel
from guis.controls.ButtonEx import HButtonEx
from guis.controls.Button import Button
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from config.client.msgboxtexts import Datas as mbmsgs
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from TaoHeartWnd import TaoHeartWnd
from ExchangeWnd import ExchangeWnd
from ZDDataLoader import *
guidLoader = ZDGuidDataLoader.instance()
guidDatas = guidLoader._datas
daofaLoader = DaofaDataLoader.instance()
daofaDatas = daofaLoader._datas
import GUIFacade
import csdefine
import skills
import ItemTypeEnum
from guis.MLUIDefine import ItemQAColorMode
from guis.MLUIDefine import QAColor

class SermonWnd( Window ):
	"""
	证道界面
	"""
	def __init__( self ):
		wnd = GUI.load( "guis/general/sermonsys/sermonwnd/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.__pyTutors = {}				#导师
		self.__triggers = {}
		self.__remcbids = {}			#播放移除道法callback
		self.__registerTriggers()
		self.__initialize( wnd )
	
	def __initialize( self, wnd ):
		self.__pyTFPanel = ItemsPanel( wnd.tfPanel, wnd.tfBar )			#道法物品面板
		self.__pyTFPanel.focus = False
		self.__pyTFPanel.viewCols = 10
		self.__pyTFPanel.autoSelect = False
		self.__pyTFPanel.colSpace = -8.0
		
		self.__pyBtnExchange = HButtonEx( wnd.btnExchange )						#积分兑换
		self.__pyBtnExchange.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnExchange.dsp = labelGather.getText( "SermonSys:SemonWnd", "inteDsp" )
		self.__pyBtnExchange.onLClick.bind( self.__onExchange )
		self.__pyBtnExchange.onMouseEnter.bind( self.__onMouseEnter )
		self.__pyBtnExchange.onMouseLeave.bind( self.__onMouseLeave )
		labelGather.setPyBgLabel( self.__pyBtnExchange, "SermonSys:SemonWnd", "exchange" )
		
		self.__pyBtnSermon = HButtonEx( wnd.btnSermon )							#一键证道
		self.__pyBtnSermon.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnSermon.dsp = labelGather.getText( "SermonSys:SemonWnd", "semonDsp" )
		self.__pyBtnSermon.onLClick.bind( self.__onSermon )
		self.__pyBtnSermon.onMouseEnter.bind( self.__onMouseEnter )
		self.__pyBtnSermon.onMouseLeave.bind( self.__onMouseLeave )
		labelGather.setPyBgLabel( self.__pyBtnSermon, "SermonSys:SemonWnd", "semon" )
		
		self.__pyBtnComp = HButtonEx( wnd.btnComp )						#一键合成
		self.__pyBtnComp.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnComp.dsp = labelGather.getText( "SermonSys:SemonWnd", "compDsp" )
		self.__pyBtnComp.onLClick.bind( self.__onCompose )
		self.__pyBtnComp.onMouseEnter.bind( self.__onMouseEnter )
		self.__pyBtnComp.onMouseLeave.bind( self.__onMouseLeave )
		labelGather.setPyBgLabel( self.__pyBtnComp, "SermonSys:SemonWnd", "compose" )
		
		self.__pyBtnPickup = HButtonEx( wnd.btnPickup )							#一键拾取
		self.__pyBtnPickup.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnPickup.dsp = labelGather.getText( "SermonSys:SemonWnd", "pickupDsp" )
		self.__pyBtnPickup.onMouseEnter.bind( self.__onMouseEnter )
		self.__pyBtnPickup.onMouseLeave.bind( self.__onMouseLeave )
		self.__pyBtnPickup.onLClick.bind( self.__onPickup )
		labelGather.setPyBgLabel( self.__pyBtnPickup, "SermonSys:SemonWnd", "pickup" )
		
		self.__pyBtnTHeart = Button( wnd.btnTaoHeart )							#道心
		self.__pyBtnTHeart.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnTHeart.onLClick.bind( self.__onTaoHeart )
		
		self.__pyBtnCallTutor = HButtonEx( wnd.btnCallTutor )						#召唤导师
		self.__pyBtnCallTutor.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCallTutor.onLClick.bind( self.__onCallTutor )
		labelGather.setPyBgLabel( self.__pyBtnCallTutor, "SermonSys:SemonWnd", "calltutor" )
		
		self.__pyRtFreeSem = CSRichText( wnd.rtFree )								#免费证道信息
		self.__pyRtFreeSem.maxWidth = 205.0
		self.__pyRtFreeSem.align = "L"
		self.__pyRtFreeSem.text = ""
		
		self.__pyRtLucky = CSRichText( wnd.rtLucky )								#机缘信息
		self.__pyRtLucky.maxWidth = 200.0
		self.__pyRtLucky.align = "R"
		self.__pyRtLucky.text = ""
		
		self.__pyStIntegral = StaticText( wnd.stIntegral )
		self.__pyStIntegral.text = ""
		
		for name, item in wnd.children:											#导师
			if name.startswith( "tutor_" ):
				index = int( name.split( "_" )[1] ) + 1
				pyTutor = Tutor( item, index )
				self.__pyTutors[index] = pyTutor
		labelGather.setPyLabel( self.pyLbTitle_, "SermonSys:SemonWnd", "title" )
		labelGather.setLabel( wnd.inteText, "SermonSys:SemonWnd", "integral" )
		
	# ----------------------------------------------------------------
	# pribvate
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_SHOW_SERMON_WND"] = self.__onShow
		self.__triggers["EVT_ON_SERMON_JIYUAN_CHANGED"] = self.__onJiYuanChanged
		self.__triggers["EVT_ON_SERMON_DAOFA_CHANGED"] = self.__onDaoFaChanged
		self.__triggers["EVT_ON_SERMON_ACTIVE_GUIDE_CHANGE"] = self.__onActiveGuide
		self.__triggers["EVT_ON_SERMON_SCORE_CHANGED"] = self.__onScoreChanged
		self.__triggers["EVT_ON_SERMON_RECORD_CHANGED"] = self.__onRecordChanged
		self.__triggers["EVT_ON_SERMON_ADD_DAOFA"] = self.__onAddDaoFa
		self.__triggers["EVT_ON_SERMON_REMOVE_DAOFA"] = self.__onRemoveDaoFa
		self.__triggers["EVT_ON_SERMON_AUTO_COMPOSE_CONFIRM"] = self.__onAutoCompConf
		for key in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( key, self )

	def __unregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			GUIFacade.unregisterEvent( key, self )
	# ---------------------------------------------------------------
	def __onShow( self ):
		"""
		显示界面
		"""
		self.visible = not self.visible
		
	def __onJiYuanChanged( self, jiyuan ):
		"""
		机缘值改变
		"""
		luckyText = PL_Font.getSource( "%d"%jiyuan, fc = ( 0, 255, 0, 255 ) )
		self.__pyRtLucky.text = labelGather.getText( "SermonSys:SemonWnd", "currJiYuan" )%luckyText
	
	def __onDaoFaChanged( self, daofa ):
		"""
		道法值改变
		"""
		pass
	
	def __onActiveGuide( self, activeGuide ):
		"""
		激活导师
		"""
		for index, pyTutor in self.__pyTutors.items():
			pyTutor.actived = index in activeGuide
		lastCall = 1 - BigWorld.player().ybActGuideRecord.getDegree()
		self.__pyBtnCallTutor.enable = not 4 in activeGuide and lastCall > 0
	
	def __onScoreChanged( self, score ):
		"""
		积分改变
		"""
		self.__pyStIntegral.text = str( score )
	
	def __onRecordChanged( self, record ):
		"""
		使用次数改变
		"""
		lastTime = 1 - record.getDegree()
		freeText = PL_Font.getSource( "%d"%lastTime, fc = ( 255, 0, 0, 255 ) )
		self.__pyRtFreeSem.text = labelGather.getText( "SermonSys:SemonWnd", "freeSermon" )%freeText
	
	def __onAddDaoFa( self, daoxinID, orderID, uid ):
		"""
		增加道法
		"""
		if daoxinID == csdefine.KB_ZHENG_DAO_ID:			#证道
			item = GUI.load( "guis/general/sermonsys/sermonwnd/tfitem.gui" )
			uiFixer.firstLoadFix( item )
			pyTfItem = TaoFaItem( item )
			daofa = BigWorld.player().uidToDaofa( uid )
			pyTfItem.update( daofa )
			self.__pyTFPanel.addItem( pyTfItem )

	def __onRemoveDaoFa( self, daoxinID, orderID, uid, isPickup ):
		"""
		移除道法
		"""
		if daoxinID == csdefine.KB_ZHENG_DAO_ID:
			for pyItem in self.__pyTFPanel.pyItems:
				daofa = pyItem.daofa
				if daofa is None:continue
				if daofa.uid == uid:
					if daofa.quality > ItemTypeEnum.CQT_WHITE and isPickup:			#播放动画
						pyItem.setMovingState()
						height = self.__pyBtnTHeart.bottomToScreen - pyItem.middleToScreen
						time = math.sqrt( 2*height/10.0 )						#下落时间
						distance = self.__pyBtnTHeart.centerToScreen - pyItem.centerToScreen
						speed = distance/time				#水平速度
						initPos = ( pyItem.center, pyItem.middle )
						self.__remcbids[uid] = BigWorld.callback( 0.0, Functor( self.__flyDaofa, pyItem, speed, initPos, 0.0 ) )
					else:
						self.__pyTFPanel.removeItem( pyItem )
	
	def __flyDaofa( self, pyDaofa, speed, initPos, time ):
		"""
		移动道法
		"""
		if not pyDaofa in self.__pyTFPanel.pyItems:
			return
		pyDaofa.center = initPos[0] +speed*time
		pyDaofa.middle = initPos[1] + 5.0*pow( time, 2 )
		disHeight = pyDaofa.middleToScreen - self.__pyBtnTHeart.bottomToScreen
		uid = pyDaofa.daofa.uid
		if disHeight >= 0:
			self.__pyTFPanel.removeItem( pyDaofa )
			remcbid = self.__remcbids.pop( uid )
			BigWorld.cancelCallback( remcbid )
			return
		time += 1.0
		self.__remcbids[uid] = BigWorld.callback( 0.1, Functor( self.__flyDaofa, pyDaofa, speed, initPos, time ) )
	
	def __onAutoCompConf( self, daoxinID, uid ):
		"""
		一键合成确认回调
		"""
		if daoxinID != csdefine.KB_ZHENG_DAO_ID:
			return
		if len( self.__pyTFPanel.pyItems ) <= 1:
			return
		player = BigWorld.player()
		daofa = player.uidToDaofa( uid )
		msg = ""
		if uid > 0:
			dfName = daofa.name
			msg = mbmsgs[0x10a7]%dfName
		else:
			msg = mbmsgs[0x10a8]
		def query( rs_id ):
			if rs_id == RS_OK:
				player.confirmAutoCompose( csdefine.KB_ZHENG_DAO_ID )
		showMessage( msg, "", MB_OK_CANCEL, query, self )
		return True
		
	def __onItemSelected( self, pyItem ):
		"""
		选取某个道法
		"""
		pass
	
	def __onExchange( self, pyBtn ):
		"""
		弹出积分兑换界面
		"""
		ExchangeWnd().show()
		BigWorld.player().request_scoreShopData()
	
	def __onSermon( self, pyBtn ):
		"""
		一键证道
		"""
		if pyBtn is None:return
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.player().autoZhengDao()
		showMessage( mbmsgs[0x10a6], "", MB_OK_CANCEL, query, self )
		return True
	
	def __onCompose( self, pyBtn ):
		"""
		一键合成
		"""
		if pyBtn is None:return
		BigWorld.player().autoCompose( csdefine.KB_ZHENG_DAO_ID )

	def __onPickup( self, pyBtn ):
		"""
		一键拾取
		"""
		if pyBtn is None:return
		BigWorld.player().autoPickUp()
	
	def __onTaoHeart( self, pyBtn ):
		"""
		弹出道心界面
		"""
		if pyBtn is None:return
		TaoHeartWnd().show()
	
	def __onCallTutor( self, pyBtn ):
		"""
		召唤导师
		"""
		player = BigWorld.player()
		pLevel = player.getLevel()
		level = roleLevelToDictKey( pLevel )
		guidName = guidDatas[level][4]["name"]
		def query( rs_id ):
			if rs_id == RS_OK:
				player.ybActiveGuide( 4, 1000 )
		showMessage( mbmsgs[0x10a0] %guidName , "", MB_OK_CANCEL, query )
		return True
	
	def __onMouseEnter( self, pyBtn ):
		"""
		弹出浮动框说明
		"""
		if pyBtn is None:return
		dsp = pyBtn.dsp
		toolbox.infoTip.showToolTips( self, dsp )
		
	def __onMouseLeave( sellf, pyBtn ):
		"""
		隐藏浮动框说明
		"""
		toolbox.infoTip.hide()

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		self.__pyTFPanel.clearItems()
		self.hide()

	def onEnterWorld( self ) :
		Window.onEnterWorld( self )
	
	def show( self ):
		player = BigWorld.player()
		for index, pyTutor in self.__pyTutors.items():
			pyTutor.setGuidInfo()
			pyTutor.actived = index in player.activeGuide
		lastCall = 1 - player.ybActGuideRecord.getDegree()
		self.__pyBtnCallTutor.enable = not 4 in player.activeGuide and lastCall > 0
		lastTime = 1 - player.ZDRecord.getDegree()
		freeText = PL_Font.getSource( "%d"%lastTime, fc = ( 255, 0, 0, 255 ) )
		self.__pyRtFreeSem.text = labelGather.getText( "SermonSys:SemonWnd", "freeSermon" )%freeText
		luckyText = PL_Font.getSource( "%d"%player.jiyuan, fc = ( 0, 255, 0, 255 ) )
		self.__pyRtLucky.text = labelGather.getText( "SermonSys:SemonWnd", "currJiYuan" )%luckyText
		self.__pyStIntegral.text = str( player.ZDScore )
		camp = player.getCamp()
		if camp == csdefine.ENTITY_CAMP_TAOISM:
			labelGather.setPyBgLabel( self.__pyBtnCallTutor, "SermonSys:SemonWnd", "xian" )
		elif camp == csdefine.ENTITY_CAMP_DEMON:
			labelGather.setPyBgLabel( self.__pyBtnCallTutor, "SermonSys:SemonWnd", "mo" )
		Window.show( self )
	
	def hide( self ):
		Window.hide( self )

# -----------------------------------------------------------------------------
from guis.controls.Icon import Icon

class Tutor( PyGUI ):
	"""
	导师按钮
	"""
	def __init__( self, item, index ):
		PyGUI.__init__( self, item )
		self.guideLevel = index
		self.focus = False
		self.crossFocus = False
		self.__pyTutorFrm = PyGUI( item.tutorFrm )
		self.__pyIcnTutor = Icon( item.header )
		self.__pyIcnTutor.focus = True
		self.__pyIcnTutor.crossFocus = True
		self.__pyIcnTutor.onLClick.bind( self.__onActiveTutor )
		self.__pyIcnTutor.onMouseEnter.bind( self.__onMouseEnter )
		self.__pyIcnTutor.onMouseLeave.bind( self.__onMouseLeave )
		
		self.__pyArrow = PyGUI( item.arrow )
		
		self.__actived = False
		self.__dsp = ""

	def __onActiveTutor( self, pyBtn ):
		"""
		激活下个导师
		"""
		if pyBtn is None:return
		BigWorld.player().clickGuide( self.guideLevel )
	
	def __onMouseEnter( self, pyIcon ):
		"""
		导师说明浮动框
		"""
		if not self.__actived:return
		toolbox.infoTip.showToolTips( self, self.__dsp )
	
	def __onMouseLeave( self ):
		"""
		隐藏浮动框
		"""
		toolbox.infoTip.hide()
	
	def setGuidInfo( self ):
		"""
		设置导师信息
		"""
		player = BigWorld.player()
		pLevel = player.getLevel()
		pCamp = player.getCamp()
		level = roleLevelToDictKey( pLevel )
		icon = "icons/%s.dds"%guidDatas[level][self.guideLevel]["icon"][pCamp]
		self.__pyIcnTutor.icon = ( icon, ((0.0, 0.0), (0.0, 0.5625), (0.5625, 0.5625), (0.5625, 0.0)))
		guidName = guidDatas[level][self.guideLevel]["name"]
		jiyuan = guidDatas[level][self.guideLevel]["jiyuan"]
		self.__dsp = labelGather.getText( "SermonSys:SemonWnd", "guidDsp" )%( guidName, jiyuan )
	
	def _getActived( self ):
		"""
		"""
		return self.__actived
	
	def _setActived( self, actived ):
		"""
		激活导师
		"""
		self.__actived = actived
		self.__pyIcnTutor.focus = actived
		self.__pyIcnTutor.crossFocus = actived
		if actived:					#被激活
			util.setGuiState( self.__pyTutorFrm.getGui(), ( 1, 2 ), ( 1, 2 ) )
			util.setGuiState( self.__pyArrow.getGui(), ( 2, 1 ), ( 1, 1 ) )
			self.__pyIcnTutor.materialFX = "BLEND"
		else:
			util.setGuiState( self.__pyTutorFrm.getGui(), ( 1, 2 ), ( 1, 1 ) )
			util.setGuiState( self.__pyArrow.getGui(), ( 2, 1 ), ( 2, 1 ) )
			self.__pyIcnTutor.materialFX = "COLOUR_EFF"
			toolbox.infoTip.hide()

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	actived = property( _getActived, _setActived )

# -------------------------------------------------------------------------------
from guis.controls.Label import Label
from guis.controls.Icon import Icon

class TaoFaItem( PyGUI ):
	"""
	道法物品
	"""
	def __init__( self, item ):
		PyGUI.__init__( self, item )
		self.__pyIcon = Icon( item.icon )
		self.__pyIcon.focus = True
		self.__pyIcon.crossFocus = True
		self.__pyIcon.onMouseEnter.bind( self.__onMouseEnter )
		self.__pyIcon.onMouseLeave.bind( self.__onMouseLeave )
		
		self.__pyStName = StaticText( item.stName )
		self.__pyStName.font = "songti.font"
		self.__pyStName.text = ""
		
		self.__pyLbSell = Label( item.lbSell )
		self.__pyLbSell.isUnderline = True
		self.__pyLbSell.commonForeColor = 255, 241, 0, 255
		self.__pyLbSell.highlightForeColor = 255, 153, 0, 255
		self.__pyLbSell.pressedForeColor = 255, 153, 0, 255
		self.__pyLbSell.onLClick.bind( self.__onSell )
		labelGather.setPyBgLabel( self.__pyLbSell, "SermonSys:SemonWnd", "sell" )
		self.__pyLbSell.font = "songti.font"
	
		self.__pyLbPick = Label( item.lbPick )
		self.__pyLbPick.isUnderline = True
		self.__pyLbPick.commonForeColor = 255, 241, 0, 255
		self.__pyLbPick.highlightForeColor = 255, 153, 0, 255
		self.__pyLbPick.pressedForeColor = 255, 153, 0, 255
		self.__pyLbPick.onLClick.bind( self.__onPick )
		labelGather.setPyBgLabel( self.__pyLbPick, "SermonSys:SemonWnd", "pick" )
		self.__pyLbPick.font = "songti.font"
		self.daofa = None
		
	def __onSell( self, pyLb ):
		"""
		卖出
		"""
		if self.daofa is None:return
		uid = self.daofa.uid
		BigWorld.player().sellDaofa( uid )
	
	def __onPick( self , pyLb ):
		"""
		拾取
		"""
		if self.daofa is None:return
		uid = self.daofa.uid
		BigWorld.player().pickUpDaofa( uid )
	
	def __onMouseEnter( self, pyIcon ):
		"""
		显示信息
		"""
		if self.daofa is None:return
		daofa = self.daofa
		name = daofa.name
		level = daofa.level
		jiyuan = daofa.jiyuan
		quality = daofa.quality
		type = daofa.type
		nameDsp = PL_Font.getSource( "%s Lv.%d"%( name, level ), fc = QAColor[quality] )
		describe = daofaDatas[quality][type]["describe"]
		infoDsp = PL_Font.getSource( describe, fc = ( 255, 255, 255, 255 ) )
		expDsp = ""
		if quality > ItemTypeEnum.CQT_WHITE:
			skillID = daofaDatas[quality][type]["levelData"][level]
			if skillID > 1 and len( str( skillID ) ) > 8:								#技能
				skill = skills.getSkill( skillID )
				if skill:
					skDsp = skill.getDescription()
				else:
					skDsp = "没有该技能配置实例"
			else:
				skDsp = "%s %d"%( daofaDatas[quality][type]["describe"], skillID )
			infoDsp = PL_Font.getSource( skDsp, fc = ( 204, 51, 0, 255 ) )
			exp = daofa.getLevelExp()
			expMax = daofa.getExpMax()
			expDsp = "道法经验 %d/%d"%( exp, expMax ) + PL_NewLine.getSource()
		price = PL_Font.getSource( "价格 %d"%jiyuan, fc = ( 255, 204, 0, 255 ) )
		dsp = nameDsp + PL_NewLine.getSource() + expDsp + infoDsp + PL_NewLine.getSource() + price
		toolbox.infoTip.showItemTips( self, dsp )
	
	def __onMouseLeave( self, pyIcon ):
		"""
		隐藏信息
		"""
		toolbox.infoTip.hide()
	
	def update( self, daofa ):
		"""
		更新道法信息
		"""
		self.daofa = daofa
		quality = daofa.quality
		type = daofa.type
		color = QAColor[quality]
		name = daofaDatas[quality][type]["name"]
		self.__pyStName.text = name
		if quality > ItemTypeEnum.CQT_WHITE:
			self.__pyStName.color = color
		icon = "icons/%s.dds"%daofaDatas[quality][type]["icon"]
		util.setGuiState( self.__pyIcon.gui, ( 3, 2 ), ItemQAColorMode[ quality ] )
		self.__pyLbPick.visible = quality > ItemTypeEnum.CQT_WHITE
		if quality > ItemTypeEnum.CQT_WHITE:
			self.__pyLbSell.left = 2.0
			self.__pyLbPick.right = self.width - 2.0
		else:
			self.__pyLbSell.center = self.width/2.0 + 4.0
	
	def setMovingState( self ):
		"""
		移动时掩藏信息
		"""
		self.__pyLbSell.visible = False
		self.__pyLbPick.visible = False
		self.__pyIcon.focus = False
		self.__pyIcon.crossFocus = False