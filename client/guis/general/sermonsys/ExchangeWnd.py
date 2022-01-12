# -*- coding: gb18030 -*-
#
# $Id: ExchangeWnd.py, fangpengjun Exp $

"""
implement ExchangeWnd class
"""
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.common.Window import Window
from guis.controls.ODPagesPanel import ODPagesPanel
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.controls.Icon import Icon
from guis.controls.Control import Control
from AbstractTemplates import Singleton
from ItemsFactory import ObjectItem
from guis.MLUIDefine import ItemQAColorMode
from guis.MLUIDefine import QAColor
from ZDDataLoader import *
daofaLoader = DaofaDataLoader.instance()
daofaDatas = daofaLoader._datas
import ItemTypeEnum
import skills
import csstring

class ExchangeWnd( Singleton, Window ):
	"""
	道心积分兑换窗口
	"""
	__triggers = {}
	_cc_items_rows = ( 3, 2 )
	
	def __init__( self ):
		wnd = GUI.load( "guis/general/sermonsys/exchange.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.__initialize( wnd )
		self.addToMgr( "exchangeWnd" )
	
	def __initialize( self, wnd ):
		self.__pyPagePanel = ODPagesPanel( wnd.itemsPanel, wnd.pgIdxBar )
		self.__pyPagePanel.onViewItemInitialized.bind( self.__initListItem )
		self.__pyPagePanel.onDrawItem.bind( self.__drawListItem )
		self.__pyPagePanel.selectable = True
		self.__pyPagePanel.onItemSelectChanged.bind( self.__onItemSelectedChange )
		self.__pyPagePanel.onItemRClick.bind( self.__onClickToBuy )
		self.__pyPagePanel.viewSize = self._cc_items_rows
		
		self.__pyStInteral = StaticText( wnd.stIntegal )
		self.__pyStInteral.text = ""
		
		labelGather.setPyLabel( self.pyLbTitle_, "SermonSys:ExchangWnd", "title" )
		labelGather.setLabel( wnd.inteText, "SermonSys:SemonWnd", "integral" )
	
	def __initListItem( self, pyViewItem ):
		"""
		初始化商品列表
		"""
		pyDaofaItem = DaoFaItem( DragMark.SERMON_SHOP_WND, self )
		pyViewItem.pyDaofaItem = pyDaofaItem
		pyViewItem.addPyChild( pyDaofaItem )
		pyViewItem.focus = True
		pyDaofaItem.left = 0
		pyDaofaItem.top = 0
	
	def __drawListItem( self, pyViewItem ):
		"""
		重画商品列表项
		"""
		daofa = pyViewItem.pageItem
		pyDaofaItem = pyViewItem.pyDaofaItem
		pyDaofaItem.selected = pyViewItem.selected
		pyDaofaItem.update( daofa )
		curPageIndex = self.__pyPagePanel.pageIndex
		totalPageIndex = self.__pyPagePanel.maxPageIndex
		
	
	def __onItemSelectedChange( self, index ):
		"""
		选取某个商品
		"""
		if index < 0:return
	
	def __onClickToBuy( self ):
		"""
		右键购买
		"""
		pass
	
	def __getDFDatas( self ):
		dfDatas = []
		for dfData in self.__pyPagePanel.items:
			dfDatas.append( (dfData[0], dfData[1]) )
		return dfDatas
		
	@classmethod
	def __onAddItem( SELF, dfData ):
		"""
		增加积分商品
		"""
		self = SELF.inst
		if not (dfData[0], dfData[1]) in self.__getDFDatas():
			self.__pyPagePanel.addItem( dfData )

	@classmethod
	def __onRemoveItem( SELF, dfData ):
		"""
		移除积分商品
		"""
		self = SELF.inst
		if (dfData[0], dfData[1]) in self.__getDFDatas():
			self.__pyPagePanel.removeItem( dfData )

	@classmethod
	def __onScoreChanged( SELF, score ):
		"""
		积分改变
		"""
		self = SELF.inst
		self.__pyStInteral.text = str( score )
	
	@classmethod
	def __onWndShow( SELF ):
		"""
		显示窗口
		"""
		pass
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@classmethod
	def registerTriggers( SELF ) :
		SELF.__triggers["EVT_ON_SERMON_EXCHANGE_SHOW"] = SELF.__onWndShow
		SELF.__triggers["EVT_ON_SERMON_RECEIVE_SHOP_ITEM"] = SELF.__onAddItem
		SELF.__triggers["EVT_ON_SERMON_REMOVE_SHOP_ITEM"] = SELF.__onRemoveItem
		SELF.__triggers["EVT_ON_SERMON_SCORE_CHANGED"] = SELF.__onScoreChanged
		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )

	@classmethod
	def onEvent( SELF, macroName, *args ) :
		SELF.__triggers[macroName]( *args )

	def onLeaveWorld( self ) :
		self.hide()

	def onEnterWorld( self ) :
		Window.onEnterWorld( self )
	
	def show( self ):
		player = BigWorld.player()
		self.__pyStInteral.text = str( player.ZDScore )
		Window.show( self )
	
	def hide( self ):
		Window.hide( self )

ExchangeWnd.registerTriggers()
# ----------------------------------------------------------------------------------------
class DaoFaItem( Control ):
	"""
	积分兑换商品
	"""
	def __init__( self, dragMark = 0, pyBinder = None ):
		item = GUI.load( "guis/general/sermonsys/inteitem.gui" )
		uiFixer.firstLoadFix( item )
		Control.__init__( self, item, pyBinder )
		self.focus = False
		self.crossFocus = False
		self.dragFocus = False
		self.__pyCover = None
		self.__pyItem = Item( item.item, self.dragMark, self )
		self.__pyItemBg = PyGUI( item.itemBg )
		
		self.__pyRtName = CSRichText( item.rtName )
		self.__pyRtName.align = "L"
		self.__pyRtName.focus = True
		self.__pyRtName.crossFocus = True
		self.__pyRtName.onMouseEnter.bind( self.__showName )
		self.__pyRtName.onMouseLeave.bind( self.__onMouseLeave )
		
		self.__pyRtDsp = CSRichText( item.rtDsp )
		self.__pyRtDsp.align = "L"
		self.__pyRtDsp.focus = True
		self.__pyRtDsp.crossFocus = True
		self.__pyRtDsp.onMouseEnter.bind( self.__showDsp )
		self.__pyRtDsp.onMouseLeave.bind( self.__onMouseLeave )
		self.__pyRtDsp.maxWidth =190.0
		
		self.__pyRtMoney = CSRichText( item.rtCost )
		self.__pyRtMoney.align = "L"

		self.__pyBtnExchange = HButtonEx( item.btnExchange )
		self.__pyBtnExchange.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnExchange.onLClick.bind( self.__onExchange )
		labelGather.setPyBgLabel( self.__pyBtnExchange, "SermonSys:ExchangWnd", "exchange" )

		if hasattr( item, "cover" ) :
			self.__pyCover = PyGUI( item.cover )
		self.__panelState = ( 1, 1 )
		self.selected = False
	
	def __onExchange( self, pyBtn ):
		"""
		积分兑换商品
		"""
		if pyBtn is None:return
		if self.daofa is None:return
		quality, type = self.daofa[0], self.daofa[1]
		BigWorld.player().scoreExchangeDaofa( quality, type )
	
	def __showName( self, pyRt ):
		"""
		道法名称
		"""
		daofa = self.daofa
		if daofa is None:return
		quality, type, level = daofa[0], daofa[1], daofa[3]
		name = daofaDatas[quality][type]["name"]
		uname = csstring.toWideString( name )
		if len( uname ) > 7:
			name = "%s.Lv%d"%( name, level )
			toolbox.infoTip.showToolTips( self, name )
	
	def __showDsp( self, pyRt ):
		"""
		道法描述
		"""
		daofa = self.daofa
		if daofa is None:return
		quality, type, level = daofa[0], daofa[1], daofa[3]
		skDsp = ""
		if quality > ItemTypeEnum.CQT_WHITE:
			skillID = daofaDatas[quality][type]["levelData"][level]
			skill = skills.getSkill( skillID )
			if skill:							#可以获取技能实例
				skDsp = skill.getDescription()
				uskDsp = csstring.toWideString( skDsp )
				if len( uskDsp ) > 11:
					toolbox.infoTip.showToolTips( self, skDsp )
		
	def __onMouseLeave( self ):
		"""
		"""
		toolbox.infoTip.hide( self )

	def __select( self ):
		self.panelState = ( 3, 1 )
		if self.__pyCover:
			self.__pyCover.visible = True

	def __deselect( self ):
		self.panelState = ( 1, 1 )
		if self.__pyCover:
			self.__pyCover.visible = False
	
	def update( self, daofa ):
		"""
		更新商品信息
		"""
		name = ""
		self.__pyItem.crossFocus = daofa is not None
		self.__pyItem.dragFocus = daofa is not None
		self.__pyBtnExchange.visible = daofa is not None
		self.__pyItem.update( daofa )
		if daofa:
			quality, type, score, level = daofa[0], daofa[1], daofa[2], daofa[3]
			color = QAColor[quality]
			name = daofaDatas[quality][type]["name"]
			skDsp = ""
			if quality > ItemTypeEnum.CQT_WHITE:
				infoVal = daofaDatas[quality][type]["levelData"][level]
				if infoVal > 1 and len( str( infoVal ) ) > 8:								#技能
					skill = skills.getSkill( infoVal )
					if skill:
						skDsp = skill.getDescription()
					else:
						skDsp = "没有该技能配置实例"
				else:
					skDsp = "%s %d"%( daofaDatas[quality][type]["describe"], infoVal )
				skDsp = csstring.toWideString( skDsp )
				if len( skDsp ) > 11:
					skDsp = "%s..."%skDsp[:11]
				uname = csstring.toWideString( name )
				if len( uname ) > 7:
					uname = "%s..."%uname[:7]
				self.__pyRtName.text = PL_Font.getSource( "%s.Lv%d"%( uname, level ), fc = color )
			self.__pyRtMoney.text = PL_Font.getSource( "兑换所需: %d"%score, fc = ( 16, 197, 165, 255 ) )
			self.__pyRtDsp.text = PL_Font.getSource( skDsp, fc = ( 204, 51, 0, 255 ) )
			self.__setItemQuality( self.__pyItemBg.getGui(), quality )
			self.__pyItem.amountText = ""
		else:
			self.selected = False
			self.__pyRtName.text = ""
			self.__pyRtMoney.text = ""
			self.__pyRtDsp.text = ""
			self.__setItemQuality( self.__pyItemBg.getGui(), 0 )

	def __setItemQuality( self, itemBg, quality ):
		util.setGuiState( itemBg, ( 4, 2 ), ItemQAColorMode[quality] )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def onMouseEnter_( self ):
		Control.onMouseEnter_( self )
		if self.selected:return
		self.panelState = ( 2, 1 )

	def onMouseLeave_( self ):
		Control.onMouseLeave_( self )
		if self.selected:return
		self.panelState = ( 1, 1 )

	def _getItemInfo( self ):
		return self.__pyItem.daofa

	def _getSelected( self ):
		return self.__selected

	def _setSelected( self, selected ):
		if selected:
			self.__select()
		else:
			self.__deselect()
		self.__selected = selected

	def _getIcon( self ):
		return self.__pyItem.icon

	def _getPanelState( self ):
		return self.__panelState

	def _setPanelState( self, state ):
		self.__panelState = state
		elements = self.getGui().elements
		for ename, element in elements.items():
			if ename == "frm_bg":continue
			element.mapping = util.getStateMapping( element.size, UIState.MODE_R3C1, state )
			if ename in ["frm_rt", "frm_r", "frm_rb"]:
				element.mapping = util.hflipMapping( element.mapping )

	def _getDaofa( self ):
		return self.__pyItem.daofa

	def _getSelected( self ):
		return self.__selected

	def _setSelected( self, selected ):
		if selected:
			self.__select()
		else:
			self.__deselect()
		self.__selected = selected

	def _getIcon( self ):
		return self.__pyItem.icon
		
	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	panelState = property( _getPanelState, _setPanelState )
	daofa = property( _getDaofa )
	selected = property( _getSelected, _setSelected )
	icon = property( _getIcon )

# -------------------------------------------------------------------------------
from guis import *
import BigWorld
import event.EventCenter as ECenter
import csdefine
class Item( Icon ):
	def __init__( self, item = None, dragMark = 0, pyBinder = None ):
		Icon.__init__( self, item, pyBinder )
		self.focus = True
		self.crossFocus = True
		self.dragFocus = False
		self.dragMark = dragMark
		self.daofa = None
		self.dsp = ""
		self.__initialize( item )

	def __initialize( self, item ) :
		if item is None : return

	def dispose( self ) :
		Icon.dispose( self )

	def onMouseEnter_( self ):
		toolbox.itemCover.highlightItem( self ) #这个放到self.onDescriptionShow_()后面会导致第一次高亮图标失败，原因未明！
		if self.isMouseHit():
			self.onDescriptionShow_()
		if self.dragMark != DragMark.SERMON_SHOP_WND or \
			self.daofa is None: return
		if self.pyBinder.selected:return
		self.pyBinder.panelState = ( 2, 1 )
		
	def onMouseLeave_( self ):
		Icon.onMouseLeave_( self )
		self.pyBinder.panelState = ( 1, 1 )
		self.onDescriptionHide_()
		return True

	def onDescriptionShow_( self ):
		if self.dsp == "" : return
		toolbox.infoTip.showItemTips( self, self.dsp )

	def onDescriptionHide_( self ):
		toolbox.infoTip.hide()

	# -------------------------------------------------
	def onDragStart_( self, pyDragged ) :
		Icon.onDragStart_( self, pyDragged )
		if BigWorld.isKeyDown( KEY_LCONTROL ) :
			rds.ruisMgr.dragObj.attach = KEY_LCONTROL
		return True
	# -----------------------------------------------
	# public
	# -----------------------------------------------
	def update( self, daofa ) :
		"""
		update item
		"""
		self.daofa = daofa
		if daofa is None:
			self.texture = ""
			self.dsp = ""
		else:
			quality, type, score, level = daofa[0], daofa[1], daofa[2], daofa[3]
			row = ItemQAColorMode[quality][0]
			col = ItemQAColorMode[quality][1]
			mapping = util.getIconMapping( (53.0, 53.0), ( 3, 2 ), row, col )
			self.icon = ( "guis/general/sermonsys/sermonwnd/icons.dds", mapping )
			color = QAColor[quality]
			nameDsp = PL_Font.getSource( "%s %s"%( daofaDatas[quality][type]["name"], "Lv.%d"%level ), fc = color )
			skDsp = ""
			infoVal = daofaDatas[quality][type]["levelData"][level]
			if infoVal > 1 and len( str( infoVal ) ) > 8:								#技能
				skill = skills.getSkill( infoVal )
				if skill:
					skDsp = skill.getDescription()
				else:
					skDsp = "没有该技能配置实例"
			else:
				skDsp = "%s %d"%( daofaDatas[quality][type]["describe"], infoVal )
			infoDsp = PL_Font.getSource( skDsp, fc = ( 204, 51, 0, 255 ) )
			exchange = PL_Font.getSource( "兑换所需: %d积分"%score, fc = ( 16, 197, 165, 255 ) )
			self.dsp = nameDsp + PL_NewLine.getSource() + infoDsp + PL_NewLine.getSource() + exchange