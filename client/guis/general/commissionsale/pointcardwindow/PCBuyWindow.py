# -*- coding: gb18030 -*-

# Implement point card buy window.
# By ganjinxing 2009-11-17

from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.CheckBox import CheckBoxEx
from guis.controls.CheckerGroup import CheckerGroup
from guis.controls.ODListPanel import ODListPanel
from guis.controls.ODListPanel import ViewItem
from guis.tooluis.fulltext.FullText import FullText
from guis.general.commissionsale.commissionviewer.GoodsPanel import ColItem
from guis.general.commissionsale.commissionviewer.GoodsPanel import MoneyCol
from guis.general.commissionsale.commissionviewer.TaxisButton import TaxisButton
from LabelGather import labelGather
from Time import Time
import csconst
import GUIFacade

LAST_TIME = csconst.SELL_POINT_CARD_LASTTIME	# 点卡寄售持续时间

class PCBuyWindow( Window ) :

	def __init__( self ) :
		wnd = GUI.load( "guis/general/commissionsale/pointcard/buywnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )

		self.__currPage = 0
		self.__latestQuery = 0					# 上次查询时间

		self.__pyMsgBox = None
		self.__refreshCBID = 0
		self.__trapNPCID = -1
		self.__initialize( wnd )
		self.__trapID=None						#陷阱id

		self.__triggers = {}
		self.__registerTriggers()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_SHOW_POINT_CARD_BUY_WINDOW"] = self.__onShow
		self.__triggers["EVT_ON_RECEIVE_POINT_CARD"] = self.__onAddNewCard
		self.__triggers["EVT_ON_REMOVE_POINT_CARD"] = self.__onRemoveCard

		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def show1(self):
		self.__onShow()

	def __initialize( self, wnd ) :
		class ListPanel( ODListPanel ) :
			def getViewItem_( self ) :
				return CardItem( self )

		self.__pyCardsPanel = ListPanel( wnd.itemsPanel, wnd.scrollBar )
		self.__pyCardsPanel.onItemSelectChanged.bind( self.__cardSelChanged )
		self.__pyCardsPanel.onViewItemInitialized.bind( self.__onInitItem )
		self.__pyCardsPanel.onDrawItem.bind( self.__onDrawItem )
		self.__pyCardsPanel.autoSelect = False
		self.__pyCardsPanel.itemHeight = 57
		self.__pyCardsPanel.ownerDraw = True							# 开启自定义绘制
		self.__pyCardsPanel.pySBar.onScroll.bind( self.__onScroll, True )

		self.__pyTaxisBtn2 = TaxisButton( wnd.taxisBtn_2 )
		self.__pyTaxisBtn2.taxisIndex = 1
		self.__pyTaxisBtn2.onLClick.bind( self.__onTaxis )

		self.__pyTaxisBtn3 = TaxisButton( wnd.taxisBtn_3 )
		self.__pyTaxisBtn3.taxisIndex = 2
		self.__pyTaxisBtn3.onLClick.bind( self.__onTaxis )

		self.__pyBuyBtn = Button( wnd.buyBtn )
		self.__pyBuyBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBuyBtn.onLClick.bind( self.__onBuy )
		self.__pyBuyBtn.isOffsetText = True
		self.__pyBuyBtn.enable = False

		self.__pyCancelBtn = Button( wnd.cancelBtn )
		self.__pyCancelBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyCancelBtn.onLClick.bind( self.hide )
		self.__pyCancelBtn.isOffsetText = True

		self.__pyCKGroup = CheckerGroup()
		self.__pyCKGroup.onCheckChanged.bind( self.__onCheckChanged )

		pyChecker = CheckBoxEx( wnd.cb_1000 )
		pyChecker.value = "10"
		self.__pyCKGroup.addChecker( pyChecker )

		pyChecker = CheckBoxEx( wnd.cb_3000 )
		pyChecker.value = "30"
		self.__pyCKGroup.addChecker( pyChecker )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyBuyBtn, "commissionsale:PCBuyWindow", "btnBuy" )
		labelGather.setPyBgLabel( self.__pyCancelBtn, "commissionsale:PCBuyWindow", "btnCancel" )
		labelGather.setPyBgLabel( self.__pyTaxisBtn2, "commissionsale:PCBuyWindow", "taxisBtn_2" )
		labelGather.setPyBgLabel( self.__pyTaxisBtn3, "commissionsale:PCBuyWindow", "taxisBtn_3" )
		labelGather.setLabel( wnd.taxisBtn_1.lbText, "commissionsale:PCBuyWindow", "taxisBtn_1" )
		labelGather.setLabel( wnd.st_1, "commissionsale:PCBuyWindow", "stChoose" )
		labelGather.setLabel( wnd.lbTitle, "commissionsale:PCBuyWindow", "lbTitle" )

	def __onInitItem( self, pyViewItem ) :
		pass

	def __onDrawItem( self, pyViewItem ) :
		pyViewItem.update()

	def __cardSelChanged( self, selIndex ) :
		self.__pyBuyBtn.enable = selIndex != -1

	def __onScroll( self, value ) :
		"""
		滚动到底部时向服务器申请查询下一页数据
		"""
		if value < 0.999 : return
		now = Time.time()
		if self.__latestQuery + 0.1 > now : return		# 最快0.1秒查一次
		self.__latestQuery = now
		self.__currPage += 1
		currSelPar = ""
		pyCurrChecker = self.__pyCKGroup.pyCurrChecker
		if pyCurrChecker is not None :
			currSelPar = pyCurrChecker.value
		self.__queryCards( self.__currPage, currSelPar )

	def __onTaxis( self, pyBtn ) :
		taxisIndex = pyBtn.taxisIndex
		taxisReverse = pyBtn.taxisReverse
		self.__pyCardsPanel.sort( key = lambda item : item[taxisIndex], reverse = taxisReverse )

	def __onBuy( self ) :
		selCard  = self.__pyCardsPanel.selItem
		if selCard is None : return
		if selCard[2] + LAST_TIME <= Time.time() : return
		BigWorld.player().cell.buyPointCard( selCard[3] )

	def __onCheckChanged( self, pyChecker ) :
		self.__pyCardsPanel.clearItems()
		currSelPar = ""
		self.__currPage = 0
		if pyChecker is not None :
			currSelPar = pyChecker.value
		self.__queryCards( self.__currPage, currSelPar )

	# -------------------------------------------------
	def __addTrap( self ) :
		self.__delTrap()
		player = BigWorld.player()
		self.__trapID = BigWorld.addPot( GUIFacade.getGossipTarget().matrix,csconst.COMMUNICATE_DISTANCE, self.__onEntitiesTrapThrough )	# 打开窗口后为玩家添加对话陷阱。

	def __delTrap( self ) :
		if self.__trapID  is not None :
			BigWorld.delPot( self.__trapID )						# 删除玩家的对话陷阱
			self.__trapID = None

	def __onEntitiesTrapThrough( self,isEnter, handle ):
		if not isEnter:								# 如果NPC离开玩家对话陷阱
			self.hide()														# 隐藏当前与NPC对话窗口

	# -------------------------------------------------
	def __startRefresh( self ) :
		self.__stopRefresh()
		pyViewCards = self.__pyCardsPanel.pyViewItems
		if len( pyViewCards ) == 0 : return
		currTime = Time.time()
		outCards = []
		for pyCard in pyViewCards :
			listItem = pyCard.listItem
			if listItem[2] + LAST_TIME < currTime :
				outCards.append( listItem )
			else :
				pyCard.update()
		for card in outCards :
			self.__pyCardsPanel.removeItem( card )
		self.__refreshCBID = BigWorld.callback( 1, self.__startRefresh )

	def __stopRefresh( self ) :
		if self.__refreshCBID > 0 :
			BigWorld.cancelCallback( self.__refreshCBID )
			self.__refreshCBID = 0

	def __showMessage( self, msg ) :
		def query( res ) :
			self.__pyMsgBox = None
		if self.__pyMsgBox is None :
			self.__pyMsgBox = showMessage( msg, "", MB_OK, query, self, Define.GST_IN_WORLD )
		else :
			self.__pyMsgBox.show( msg, "", query, self, Define.GST_IN_WORLD )

	def __queryCards( self, page, par ) :
		"""
		向服务器查询寄售点卡
		"""
		if par == "" :
			BigWorld.player().base.queryPointCards( page )
		else :
			BigWorld.player().base.queryPointCardsByValue( page, par )

	def __onShow( self ) :
		if not self.visible :
			self.__trapNPCID = GUIFacade.getGossipTargetID()
			self.__addTrap()
			self.show()

	def __onAddNewCard( self, card ) :
		cardItem = ( card.parValue,
					( card.price, (255,255,255,255) ),
					card.sellTime,
					card.cardNo
					)
		self.__pyCardsPanel.addItem( cardItem )
		self.__startRefresh()

	def __onRemoveCard( self, cardNO ) :
		for index, card in enumerate( self.__pyCardsPanel.items ) :
			if card[3] == cardNO :
				self.__pyCardsPanel.removeItemOfIndex( index )
				break


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self ) :
		self.__startRefresh()
		Window.show( self )
		self.__currPage = 0
		self.__queryCards( self.__currPage, "" )

	def hide( self ) :
		self.__delTrap()
		self.__stopRefresh()
		self.__pyCardsPanel.clearItems()
		Window.hide( self )

	def onLeaveWorld( self ) :
		self.hide()

	def onEvent( self, evtMacro, *args ) :
		"""
		"""
		self.__triggers[evtMacro]( *args )


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getTrapNPC( self ) :
		return BigWorld.entities.get( self.__trapNPCID, None )

	trapNPC = property( _getTrapNPC )



class CardItem( ViewItem ) :

	_CARD_ITEM = None
	_STATUSBG_GRAY = None
	_STATUSBG_NORMAL = None
	_STATUSBG_HIGHLIGHT = None

	def __init__( self, pyPanel ) :
		if CardItem._CARD_ITEM is None :
			CardItem._CARD_ITEM = GUI.load( "guis/general/commissionsale/pointcard/carditem.gui" )
			uiFixer.firstLoadFix( CardItem._CARD_ITEM )
		gui = util.copyGuiTree( CardItem._CARD_ITEM )
		ViewItem.__init__(  self, pyPanel, gui )
		self.crossFocus = False

		if CardItem._STATUSBG_GRAY is None :
			CardItem._STATUSBG_GRAY = BigWorld.PyTextureProvider( "guis/general/commissionsale/shopsviewer/fbg_gray.dds" )
			CardItem._STATUSBG_NORMAL = BigWorld.PyTextureProvider( "guis/general/commissionsale/shopsviewer/fbg_normal.dds" )
			CardItem._STATUSBG_HIGHLIGHT = BigWorld.PyTextureProvider( "guis/general/commissionsale/shopsviewer/fbg_highlight.dds" )

		self.__pyColItems = []
		self.__initialize( gui )

	def __initialize( self, gui ) :
		self.__pyColItems.append( CardIcon( gui.icon ) )
		self.__pyColItems.append( MyMoneyCol( gui.col_1 ) )
		self.__pyColItems.append( TimeCol( gui.col_2 ) )
		self.__statusBg = gui.statusBg


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self ) :
		listItem = self.listItem
		if listItem is None :
			self.__statusBg.texture = CardItem._STATUSBG_GRAY
			listItem = ( "",
						( 0, (255,255,255,255) ),
						0,
						)
		elif self.selected :
			self.__statusBg.texture = CardItem._STATUSBG_HIGHLIGHT
		else :
			self.__statusBg.texture = CardItem._STATUSBG_NORMAL
		for pyCItem, info in zip( self.__pyColItems, listItem ) :
			pyCItem.update( info )



class CardIcon( PyGUI ) :

	_CARD_1000 = None
	_CARD_3000 = None

	def __init__( self, icon, pyBinder = None ) :
		PyGUI.__init__( self, icon )

		if CardIcon._CARD_1000 is None :
			CardIcon._CARD_1000 = BigWorld.PyTextureProvider( "guis/general/commissionsale/pointcard/1000_1.dds" )
			CardIcon._CARD_3000 = BigWorld.PyTextureProvider( "guis/general/commissionsale/pointcard/3000_1.dds" )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, value ) :
		if value == "10" :
			self.texture = CardIcon._CARD_1000
		elif value == "30" :
			self.texture = CardIcon._CARD_3000
		else :
			self.texture = ""
			if value != "" :
				ERROR_MSG( "Error par value %s found of point card" % value  )



class TimeCol( ColItem ) :

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __convertTimeStr( self, startTime ) :
		endTime = startTime + LAST_TIME
		leaveTime = int( endTime - Time.time() )
		timeText = ""
		color = 255,255,255,255										# 设置默认颜色(白色)
		if leaveTime > 0 :
			hour = leaveTime / 3600
			min = leaveTime / 60 - hour * 60
			sec = leaveTime - hour * 3600 - min * 60
			if hour == 0 and min == 0 :									# 剩余时间不大于1分钟
				timeText += labelGather.getText( "commissionsale:TimeCol", "leaveTime_second" ) % sec
			else :
				if sec : min += 1										# 把秒向分钟进位
				if min == 60 :											# 分钟向小时进位
					min = 0
					hour += 1
				if hour:												# 小时
					timeText += labelGather.getText( "commissionsale:TimeCol", "leaveTime_hour" ) % hour
				if min :												# 分钟
					timeText += labelGather.getText( "commissionsale:TimeCol", "leaveTime_minute" ) % min
		else :
			timeText += labelGather.getText( "commissionsale:TimeCol", "leaveTime_end" )
		return ( timeText, color )									# 如有需求可设置颜色


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, startTime ) :
		str, color = self.__convertTimeStr( startTime )
		self.pyText_.text = str
		self.pyText_.color = color
		if self.isMouseHit() and \
		( self.pyText_.left < 0 or self.pyText_.right > self.width ) :
			FullText.show( self, self.pyText_, False )


class MyMoneyCol( MoneyCol ) :

	def initialize_( self, colItem ) :
		MoneyCol.initialize_( self, colItem )
		self.pyText_.autoNewline = True
		self.pyText_.align = "C"