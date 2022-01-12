# -*- coding: gb18030 -*-
# $Id: Bulletin.py $

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.tooluis.CSRichText import CSRichText
from guis.controls.StaticText import StaticText
from guis.controls.ODPagesPanel import ODPagesPanel
from guis.controls.SelectableButton import SelectableButton
from guis.controls.SelectorGroup import SelectorGroup
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.general.tongabout.WarIntergral import TaxisButton
from TbVoteWnd import TbVoteWnd
from MsgBoard import MsgBoard
from TbExplainWnd import TbExplainWnd
import GUIFacade
import csconst

class BulletinBoard( Window ):
	
	_cc_items_rows = ( 20, 1 )
	_cc_defIndex = 1
	
	_cc_contents = {0:( labelGather.getText( "Tanabata:Bulletin", "title_4" ), labelGather.getText( "Tanabata:Bulletin", "explain" ) ),
					1:( labelGather.getText( "Tanabata:Bulletin", "title_5" ), labelGather.getText( "Tanabata:Bulletin", "rule" ) ),
					2:( labelGather.getText( "Tanabata:Bulletin", "title_result" ),  "" ),
			}
	
	def __init__( self ):
		wnd = GUI.load( "guis/general/tanabata/bulletinwnd.gui")
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 	= True
		self.sortByName = False
		self.sortByMsg = False
		self.sortByTime = False
		self.sortByVotes = False
		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()
		self.__trapID = 0
	
	def __initialize( self, wnd ):
		labelGather.setPyLabel( self.pyLbTitle_, "Tanabata:Bulletin", "lbTitle" )
		self.__pyRtTips = CSRichText( wnd.rtTips )
		self.__pyRtTips.text = ""
		
		self.__pyBtnMyCon = Button( wnd.btnConfess )			#我要告白
		self.__pyBtnMyCon.setStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyBtnMyCon, "Tanabata:Bulletin", "btnConfess" )
		self.__pyBtnMyCon.onLClick.bind( self.__onSendMsg )
		self.pyTaxiBtns = {}
		self.__pyBtnCons = SelectorGroup()
		for name, item in wnd.children:
			if name.startswith( "btnCon_" ):
				index = int( name.split( "_" )[1] )
				pyBtnCon = SelectableButton( item )
				pyBtnCon.index = index
				pyBtnCon.setStatesMapping( UIState.MODE_R4C1 )
				labelGather.setPyLabel( pyBtnCon, "Tanabata:Bulletin", name )
				self.__pyBtnCons.addSelector( pyBtnCon )
			if name.startswith( "btnTaxis_" ):
				index = int( name.split("_")[1] )
				pyBtnTaxis = TaxisButton( item )
				pyBtnTaxis.taxisIndex = index
				pyBtnTaxis.isSort = True
				pyBtnTaxis.setStatesMapping( UIState.MODE_R4C1 )
				labelGather.setPyBgLabel( pyBtnTaxis, "Tanabata:Bulletin", name )
				pyBtnTaxis.onLClick.bind( self.__onSortByTaxi )
				self.pyTaxiBtns[index] = pyBtnTaxis
		self.__pyBtnCons.onSelectChanged.bind( self.__onSelConfChange )
		
		self.__pyBtnDetail = Button( wnd.btnDetail ) 			#查看详细
		self.__pyBtnDetail.setStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyBtnDetail, "Tanabata:Bulletin", "btnDetail" )
		self.__pyBtnDetail.onLClick.bind( self.__showDetail )
		
		self.__pyBtnExplain = Button( wnd.btnExplain )			#活动说明
		self.__pyBtnExplain.setStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyBtnExplain, "Tanabata:Bulletin", "btnExplain" )
		self.__pyBtnExplain.onLClick.bind( self.__showExplain )
	
		self.__pyBtnRule = Button( wnd.btnRule )				#活动规则
		self.__pyBtnRule.setStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyBtnRule, "Tanabata:Bulletin", "btnRule" )
		self.__pyBtnRule.onLClick.bind( self.__showRule )
	
		self.__pyBtnQuery = Button( wnd.btnQuery )				#获奖查询
		self.__pyBtnQuery.setStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyBtnQuery, "Tanabata:Bulletin", "btnQuery" )
		self.__pyBtnQuery.onLClick.bind( self.__queryAwards )

		self.__pyStPages = StaticText( wnd.stPages )
		self.__pyStPages.text = ""
		
		self.__pyMsgsPage = ODPagesPanel( wnd.msgsPanel, wnd.pgIdxBar )
		self.__pyMsgsPage.onViewItemInitialized.bind( self.__initListItem )
		self.__pyMsgsPage.onDrawItem.bind( self.__drawListItem )
		self.__pyMsgsPage.selectable = True
		self.__pyMsgsPage.viewSize = self._cc_items_rows
		self.__pyMsgsPage.onItemSelectChanged.bind( self.__onItemSelectedChange )
		self.__pyMsgsPage.onItemLDBClick.bind( self.__onItemLDBClick )
		self.__pyMsgsPage.pyBtnDec.onLClick.bind( self.__onQueryFrontPage )
		self.__pyMsgsPage.pyBtnInc.onLClick.bind( self.__onQueryNextPage )
	
		self.__pyBtnClose = Button( wnd.btnClose )
		self.__pyBtnClose.setStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyBtnClose, "Tanabata:Bulletin", "btnClose" )
		self.__pyBtnClose.onLClick.bind( self.__onClose )
		
	# ---------------------------------------------------------------------
	# pravite
	# ---------------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_TOGGLE_BULLETIN_SHOW"] = self.__onShowBulletin
		self.__triggers["EVT_ON_RECIEVE_LOVE_MSG"] = self.__onAddMsg
		self.__triggers["EVT_ON_RECIEVE_REWARDS_RESULTS"] = self.__onRewardsResult
		self.__triggers["EVT_ON_VOTE_LOVEMSG_SUCC"]	= self.__onVoteSucc
		self.__triggers["EVT_ON_SEND_LOVEMSG_SUCC"] = self.__onSendSucc
		for trigger in self.__triggers :
			ECenter.registerEvent( trigger, self )

	def __desregisterTriggers( self ) :
		for trigger in self.__triggers :
			ECenter.unregisterEvent( trigger, self )
	# -----------------------------------------------------------
	def __initListItem( self, pyViewItem ):
		pyMsgItem = MsgItem()
		pyViewItem.pyMsgItem = pyMsgItem
		pyViewItem.addPyChild( pyMsgItem )
		pyViewItem.dragFocus = False
		pyMsgItem.left = 0
		pyMsgItem.top = 0
	
	def __drawListItem( self, pyViewItem ):
		msgInfo = pyViewItem.pageItem
		pyMsgItem = getattr( pyViewItem, "pyMsgItem", None )
		if pyMsgItem is not None :
			pyMsgItem.selected = pyViewItem.selected
			pyMsgItem.setMsgInfo( msgInfo )
		pyViewItem.visible = msgInfo is not None
		pyViewItem.crossFocus = msgInfo is not None
		pyViewItem.focus = msgInfo is not None
		totalPageIndex = self.__pyMsgsPage.maxPageIndex
		self.__pyStPages.text = labelGather.getText( "Tanabata:Bulletin", "stPages" )%( totalPageIndex + 1 )
	
	def __onItemSelectedChange( self, index ):
		"""
		选取某个信息
		"""
		self.__pyBtnDetail.enable = index != -1
	
	def __onItemLDBClick( self, pyViewItem ):
		"""
		左键双击触发
		"""
		if pyViewItem is None:return
		msgInfo = pyViewItem.pageItem
		if msgInfo is None:return
		TbVoteWnd.inst.readConfession( msgInfo, self )

	def __onQueryFrontPage( self ):
		"""
		查询上一页留言
		"""
		pySelector = self.__pyBtnCons.pyCurrSelector
		if pySelector is None:return
		if pySelector.index != 2: return
		pageIndex = self.__pyMsgsPage.pageIndex
		BigWorld.player().base.queryLoveMsgsByRange( pageIndex )
	
	def __onQueryNextPage( self ):
		"""
		查询下一页留言
		"""
		pySelector = self.__pyBtnCons.pyCurrSelector
		if pySelector is None:return
		if pySelector.index != 2: return
		pageIndex = self.__pyMsgsPage.pageIndex
		BigWorld.player().base.queryLoveMsgsByRange( pageIndex )
	
	def __onShowBulletin( self ):
		"""
		显示公告栏
		"""
		player = BigWorld.player()
		distance = csconst.COMMUNICATE_DISTANCE
		target=GUIFacade.getGossipTarget()
		if hasattr( target, "getRoleAndNpcSpeakDistance" ):
			distance = target.getRoleAndNpcSpeakDistance()
		self.__trapID = BigWorld.addPot(target.matrix,distance, self.__onEntitiesTrapThrough )#打开窗口后为玩家添加对话陷阱
		self.show()

	def __delTrap( self ) :
		if self.__trapID is not None:
			BigWorld.delPot( self.__trapID )									#删除玩家的对话陷阱
			self.__trapID = 0

	def __onEntitiesTrapThrough( self,isEnter, handle ):
		if not isEnter:
			self.hide()														#隐藏当前交易窗口
	# ----------------------------------------------------------
	def __onAddMsg( self, msgInfo ):
		indexs = [msg.index for msg in self.__pyMsgsPage.items]
		if not msgInfo.index in indexs:
			self.__pyMsgsPage.addItem( msgInfo )
	
	def __onRewardsResult( self, result ):
		"""
		查询结果回调
		"""
		title = self._cc_contents[2][0]
		rewardsText = ""
		for index, text in result.items():
			rewardsText += text + PL_NewLine.getSource( 2 )
		rewardsText = PL_Font.getSource( rewardsText, fc = (255, 248, 158))
		TbExplainWnd.inst.showText( title, rewardsText, self )
	
	def __onVoteSucc( self, msgInst ):
		"""
		投票成功回调
		"""
		for pyViewItem in self.__pyMsgsPage.pyViewItems:
			msgInfo = pyViewItem.pageItem
			if msgInfo is None:continue
			pyMsgItem = pyViewItem.pyMsgItem
			if msgInfo.index == msgInst.index:
				pyMsgItem.setMsgInfo( msgInst )
		if TbVoteWnd.inst.visible:
			TbVoteWnd.inst.onVoteSucc( msgInst )
		showAutoHideMessage( 3.0, 0x0e67,"", MB_OK )
	
	def __onSendSucc( self ):
		"""
		留言发送成功的回调
		"""
		msgBoard = MsgBoard.instance()
		if msgBoard and msgBoard.visible:
			msgBoard.hide()
	
	def __onSendMsg( self ):
		"""
		发送告白
		"""
		MsgBoard.instance().show( self )
	
	def __onSelConfChange( self, pyBtnConf ):
		"""
		刷新表白列表
		"""
		if pyBtnConf is None:return
		index = pyBtnConf.index
		player = BigWorld.player()
		self.__pyMsgsPage.clearItems()
		if index == 0: #自己发出的表白
			player.base.queryLoveMsgsBySenderName( player.playerName )
		elif index == 1: #自己收到的
			player.base.queryLoveMsgsByReceiverName( player.playerName )
		else: #先请求第一页留言
			startIndex = 0
			player.base.queryLoveMsgsByRange( startIndex )
#			BigWorld.callback( 3.0, self.__onRequery)
			
	def __onSortByTaxi( self, pyBtnTaxis ):
		"""
		列表排序方式
		"""
		sortDict = { 0: self.__sortByAdress,
				1: self.__sortByMsg,
				2: self.__sortByTime,
				3: self.__sortByVotes
		}
		index = pyBtnTaxis.taxisIndex
		sortDict[index]()
	
	def __showDetail( self ):
		"""
		详细内容
		"""
		msgInfo = self.__pyMsgsPage.selItem
		if msgInfo is None:return
		TbVoteWnd.inst.readConfession( msgInfo, self )
	
	def __showExplain( self ):
		"""
		活动说明
		"""
		title = self._cc_contents[0][0]
		text = PL_Font.getSource( self._cc_contents[0][1], fc = (255, 248, 158))
		TbExplainWnd.inst.showText( title, text, self )
	
	def __showRule( self ):
		"""
		奖励规则
		"""
		title = self._cc_contents[1][0]
		text = PL_Font.getSource( self._cc_contents[1][1], fc = (255, 248, 158))
		TbExplainWnd.inst.showText( title, text, self )
		
	def __queryAwards( self ):
		"""
		获奖查询
		"""
		BigWorld.player().base.queryLoveMsgsResult()
	
	def __prize( self ):
		"""
		领取奖励
		"""
		BigWorld.player().base.queryFeichengwuraoReward()
	
	def __sortByAdress( self ):
		"""
		按收信人排序
		"""
		flag = self.sortByName and True or False
		self.__pyMsgsPage.sort( key = lambda item : item.receiverName, reverse = flag )
		self.sortByName = not self.sortByName
	
	def __sortByMsg( self ):
		"""
		按信息排序
		"""
		flag = self.sortByMsg and True or False
		self.__pyMsgsPage.sort( key = lambda item : item.msg, reverse = flag )
		self.sortByMsg = not self.sortByMsg
	
	def __sortByTime( self ):
		"""
		按接收时间排序
		"""
		flag = self.sortByTime and True or False
		self.__pyMsgsPage.sort( key = lambda item : item.receiveTime, reverse = flag )
		self.sortByTime = not self.sortByTime
	
	def __sortByVotes( self ):
		"""
		按选票数排序
		"""
		flag = self.sortByVotes and True or False
		self.__pyMsgsPage.sort( key = lambda item : item.getVoteCount(), reverse = flag )
		self.sortByVotes = not self.sortByVotes
		
	def __onClose( self ):
		"""
		关闭公告栏
		"""
		self.hide()

	# ----------------------------------------------------------
	#public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )

	def show( self ):
		self.__pyRtTips.text = PL_Font.getSource( labelGather.getText( "Tanabata:Bulletin", "freshTips" ), fc = ( 2, 240, 203, 255 ) )
		Window.show( self )

	def hide( self ):
		self.__pyMsgsPage.clearItems()
		pySelector = self.__pyBtnCons.pyCurrSelector
		if pySelector:
			pySelector.selected = False
		Window.hide( self )
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )

	def onLeaveWorld( self ):
		self.hide()

# --------------------------------------------------------------------------
from guis.controls.ListItem import MultiColListItem
from Time import Time

class MsgItem( MultiColListItem ):
	_ITEM = None
	_limit_chars = 34
	def __init__( self ):
		if MsgItem._ITEM is None :
			MsgItem._ITEM = GUI.load( "guis/general/tanabata/msgitem.gui" )
			uiFixer.firstLoadFix( MsgItem._ITEM )
		item = util.copyGuiTree( MsgItem._ITEM )
		MultiColListItem.__init__( self, item )
		self.commonBackColor = ( 255, 255, 255, 0 )
		self.selectedBackColor = ( 118, 111, 67, 255 )
		self.highlightBackColor = ( 118, 111, 67, 255 )
		self.focus = False
	
	def setMsgInfo( self, msgInfo ):
		receiverName = ""
		msg = ""
		timeText = ""
		voteCount = ""
		if msgInfo:
			receiverName = msgInfo.receiverName
			msg = msgInfo.msg
			receiveTime = Time.localtime( msgInfo.receiveTime )
			minStr = ""
			if receiveTime[4] < 10:
				minStr = "0%d"%receiveTime[4]
			else:
				minStr = "%d"%receiveTime[4]
			if receiveTime[3] < 12:
				timeText = labelGather.getText( "Tanabata:Bulletin", "timeMon" )%( receiveTime[2], receiveTime[1], receiveTime[3], minStr )
			else:
				timeText = labelGather.getText( "Tanabata:Bulletin", "timeAfter" )%( receiveTime[2], receiveTime[1], receiveTime[3], minStr )
			voteCount = str( msgInfo.getVoteCount() )
#		if len( msg ) > self._limit_chars:
#			msg = "%s..."%msg[:32]
		self.setTextes( receiverName,
						msg,
						timeText,
						voteCount,
						)
		if self.selected :
			self.setState( UIState.SELECTED )
		elif self.isMouseHit() :
			self.setState( UIState.HIGHLIGHT )
		else :
			self.setState( UIState.COMMON )
			