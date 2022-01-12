# -*- coding: gb18030 -*-
#
# $Id: CommontalkWindow.py,v 1.20 2008-08-26 02:16:14 huangyongwei Exp $

"""
implement talking window
"""
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.common.PyGUI import PyGUI
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from ContentPanel import ContentPanel
from MarkItem import MarkItem
from gbref import rds
import GUIFacade
import csconst
import csdefine
import Language
from config.client import GossipType

class CommontalkWindow( Window ) :
	__cc_content_spacing	= 4.0		# text spacing of talking content text
	__cc_respond_view_rows	= 4			# the number of respond will be show at one time
	
	def __init__( self ) :
		wnd = GUI.load( "guis/general/npctalk/commtalk.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4			# in uidefine.py
		self.activable_ = True				# if a root gui can be ancriated, when it becomes the top gui, it will rob other gui's input focus
		self.escHide_ 		 = True
		self.gossipType = GossipType.Datas
		self.__initialize( wnd )
		self.pyOptionItems_ = []
		self.triggers_ = {}
		self.registerTriggers_()
		self.__trapID = 0

		rds.mutexShowMgr.addMutexRoot( self, MutexGroup.TRADE2 )				# 添加到MutexGroup.TRADE2互斥组

	def __initialize( self, wnd ) :
		self.pyContent_ = ContentPanel( wnd.contentPanel.clipPanel, wnd.contentPanel.sbar )
		self.pyContent_.spacing = self.__cc_content_spacing

		self.pyBigPanel_ = PyGUI( wnd.bigPanel )
		labelGather.setPyLabel( self.pyLbTitle_, "NPCTalkWnd:main", "lbTitle" ) # 注意：标题的有效UI换成了lbTitle_
		
		self.pyHeader_ = PyGUI(wnd.header )
		self.pyHeader_.texture = ""

		self.pySmallPanel_ = PyGUI( wnd.smallPanel )
		self.pySmallPanel_.visible = True

		self.pyBtnShut_ = HButtonEx( wnd.smallPanel.btnShut )
		self.pyBtnShut_.visible = True
		self.pyBtnShut_.setExStatesMapping( UIState.MODE_R4C1 )
		self.pyBtnShut_.onLClick.bind( self.__onShut )
		labelGather.setPyBgLabel( self.pyBtnShut_, "NPCTalkWnd:main", "btnShut" )

		self.pyBtnAccept_ = HButtonEx( wnd.bigPanel.btnAccept )
		self.pyBtnAccept_.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.pyBtnAccept_, "NPCTalkWnd:main", "btnAccept" )

		self.pyBtnFulfil_ = HButtonEx( wnd.bigPanel.btnFulfill )
		self.pyBtnFulfil_.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.pyBtnFulfil_, "NPCTalkWnd:main", "btnFulfill" )
		
		self.pyCloseBtn_.onLClick.bind( self.__onShut )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __reset( self ) :
		self.__trapID = 0

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for eventMacro in self.triggers_.iterkeys() :
			GUIFacade.registerEvent( eventMacro, self )

	# -------------------------------------------------
	def onEndTalking_( self ) :
		self.__delTrap()
		self.hide()

	# -------------------------------------------------
	def __onItemClick( self, pyItem ) :
		pyItem.handler( *pyItem.handleArgs )

	def __addTrap( self ):
		if self.__trapID:
			self.__delTrap()

		player = BigWorld.player()
		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr( GUIFacade.getGossipTarget(), "getRoleAndNpcSpeakDistance" ):
			distance = GUIFacade.getGossipTarget().getRoleAndNpcSpeakDistance()  + 0.5	# +0.5 避免陷阱大小和对话距离相等而导致在陷阱边缘对话时对话框会一闪消失的问题。
		self.__trapID = player.addTrapExt( distance, self.__onEntitiesTrapThrough )		#打开窗口后为玩家添加对话陷阱s

	def __delTrap( self ) :
		player = BigWorld.player()
		if self.__trapID :
			player.delTrap( self.__trapID )											#删除玩家的对话陷阱
			self.__trapID = 0

	def __onEntitiesTrapThrough( self, entitiesInTrap ):
		gossiptarget = GUIFacade.getGossipTarget()									#获取当前对话NPC
		if gossiptarget and gossiptarget not in entitiesInTrap:						#如果NPC离开玩家对话陷阱
			self.__onShut()														#隐藏当前与NPC对话窗口

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		"""
		register event triggers
		"""
		self.triggers_["EVT_OPEN_GOSSIP_WINDOW"] = self.onShowCommonTalking_	# show window for talking trigger
		self.triggers_["EVT_END_GOSSIP"] = self.onEndTalking_					# hide talking window
		self.triggers_["EVT_ON_ROLE_DEAD"] = self.hide
		for eventMacro in self.triggers_.iterkeys() :
			GUIFacade.registerEvent( eventMacro, self )

	# -------------------------------------------------------------
	def getPyOptionItem_( self, index, text, markType ) :
		"""
		get/create respond item
		"""
		existCount = len( self.pyOptionItems_ )
		pyItem = None
		if index < existCount :
			pyItem = self.pyOptionItems_[index]
		else :
			pyItem = MarkItem()
			pyItem.handler = lambda *args : False
			pyItem.handleArgs = ()
		
		pyItem.text = text
		pyItem.commonForeColor = ( 69, 141, 204, 255 )
		pyItem.selectedForeColor = pyItem.highlightForeColor
		pyItem.markType = markType
		pyItem.mark = self.gossipType[markType]
		return pyItem

	# -------------------------------------------------
	def clearContent_( self ) :
		self.pyContent_.clear()

	def addOptionItem_( self, index, text, markType, handler, handleArgs = () ) : # 将任务对话选项与操作相绑定
		"""
		add a respond items
		"""
		pyItem = self.getPyOptionItem_( index, text, markType )
		pyItem.handler = handler
		pyItem.handleArgs = handleArgs
		pyItem.onLClick.bind( self.__onItemClick )
		self.pyContent_.appendOptionItem( pyItem ) # 将该选项添加到界面上
		
	# ---------------------------------------
	def onShowCommonTalking_( self ) :
		"""
		show common talking
		"""
#		self.pyLbTitle_.text = GUIFacade.getGossipTargetName()					# 对话NPC名称wsf
		self.clearContent_()
		self.pyContent_.appendText( GUIFacade.getGossipText() )					# 普通对话内容
		self.pyHeader_.texture = GUIFacade.getGossipTargetHeader()
		self.showGossipOption()
		self.__addTrap()

	def showGossipOption( self ):	# wsf add，最后添加
		options = GUIFacade.getGossipOptions()									# 普通对话选项
		handler = GUIFacade.selectGossipOption									# 任务对话功能选项
		for index, option in enumerate( options ) :
			self.addOptionItem_( index, option[1], option[2], handler, ( index, ) )

	def __onShut( self ):
		self.hide()
		self.__delTrap()
	
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		event triggering
		"""
		self.triggers_[eventMacro]( *args )
	
	def onMove_( self, dx, dy ):
		Window.onMove_( self, dx, dy )

	def onLeaveWorld( self ) :
		self.hide()
		self.__reset()
	
	def hide( self ):
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		Window.hide( self )
