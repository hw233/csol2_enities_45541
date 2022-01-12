# -*- coding: gb18030 -*-

import time
import csdefine
import csconst
import csstatus
from guis import *
from guis.common.Window import Window
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPage
from guis.controls.StaticText import StaticText
from TiShouSellPanel import TiShouSellPanel
from LogsPanel import LogsPanel
from LabelGather import labelGather


class TiShouSellWindow( Window ):

	def __init__( self ):
		wnd = GUI.load( "guis/general/vendwindow/sellwindow/vendsellwindow.gui")
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )

		self.__tishouNPCID = -1
		self.__trapID = None
		self.__pyMsgBox = None
		self.__lastOpenTime = 0

		self.triggers_ = {}
		self.registerTriggers_()
		self.initialize_( wnd )

		rds.mutexShowMgr.addMutexRoot( self, MutexGroup.TRADE1 )				# 添加到MutexGroup.TRADE1互斥组


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def initialize_( self, wnd ):
		self.__pyTabCtrl = TabCtrl( wnd.tc )

		pyTabBtn = TabButton( wnd.tc.btn_0 )
		self.__pySellPanel = TiShouSellPanel( wnd.tc.panel_0, self )
		self.__pyTabCtrl.addPage( TabPage( pyTabBtn, self.__pySellPanel ) )		# 出售商品查看页面

		pyTabBtn = TabButton( wnd.tc.btn_1 )
		self.__pyLogsPanel = LogsPanel( wnd.tc.panel_1, self )
		self.__pyTabCtrl.addPage( TabPage( pyTabBtn, self.__pyLogsPanel ) )		# 出售记录查看页面

		self.pyStStallName_ = StaticText( wnd.stStallName ) 					# 摊位名称
		self.pyStStallName_.text = ""

	def registerTriggers_( self ):
		self.triggers_["EVT_ON_TOGGLE_COMMISSION_SALE_WND"] = self.__onToggleVisible
		for key in self.triggers_ :
			ECenter.registerEvent( key, self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __deregisterTriggers( self ) :
		"""
		deregister all events
		"""
		for key in self.triggers_.iterkeys() :
			ECenter.unregisterEvent( key, self )

	def __onToggleVisible( self, tishouNPC, destroyTime ) :
		"""
		打开替售商品管理界面
		"""
		now = time.time()
		if self.__tishouNPCID == tishouNPC.id and \
			self.__lastOpenTime + 0.5 > now :
				return
		self.__lastOpenTime = now
		player = BigWorld.player()
		if player.state == csdefine.ENTITY_STATE_VEND :
			player.statusMessage( csstatus.YOU_ARE_VENDING )
			return
		ECenter.fireEvent( "EVT_ON_VEND_WINDOW_MUTEX" )
		self.__tishouNPCID = tishouNPC.id
		self.__addTrap()
		if not self.visible :
			self.show( destroyTime )

	def __addTrap( self ):
		self.__delTrap()
		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr( self.tishouNPC, "getRoleAndNpcSpeakDistance" ):
			distance = self.tishouNPC.getRoleAndNpcSpeakDistance() + 0.5			# +0.5 避免陷阱大小和对话距离相等而导致在陷阱边缘对话时对话框会一闪消失的问题。
		self.__trapID = BigWorld.addPot( self.tishouNPC.matrix,distance, self.__onEntitiesTrapThrough )	# 打开窗口后为玩家添加对话陷阱s

	def __delTrap( self ) :
		if self.__trapID is not None :
			BigWorld.delPot( self.__trapID )								# 删除玩家的对话陷阱
			self.__trapID = None

	def __onEntitiesTrapThrough( self, isEnter,handle ):
		if not isEnter:									# 如果NPC离开玩家对话陷阱
			self.__onHide()															# 隐藏当前与NPC对话窗口

	def __showMessage( self, msg, MARK, callback ) :
		def query( res ) :
			self.__pyMsgBox = None
			callback( res )
		if self.__pyMsgBox is not None :
			self.__pyMsgBox.hide()
		self.__pyMsgBox = showMessage( msg, "", MARK, query, None, Define.GST_IN_WORLD )

	# -------------------------------------------------
	def __checkOperation( self ) :
		if not self.tishouNPC or self.tishouNPC.tsState :
			return True
		else :
			tsNPCID = self.__tishouNPCID
			def query( result ) :
				if result == RS_YES :
					tsNPC = BigWorld.entities.get( tsNPCID )
					if tsNPC :
						tsNPC.cell.startTS()
					else :
						# "未找到替售NPC！"
						self.__showMessage( 0x0341, MB_OK, query )
			# "您还没有开始寄售物品，是否开始寄售？"
			self.__showMessage( 0x0342, MB_YES_NO, query )
			return False

	def __onHide( self ) :
		Window.hide( self )
		self.__delTrap()
		self.__tishouNPCID = -1
		self.__lastOpenTime = 0
		BigWorld.player().tradeState = csdefine.TRADE_NONE
		self.__pySellPanel.onParentHide()
		self.__pyLogsPanel.onParentHide()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.triggers_[eventMacro]( *args )

	def hide( self ) :
		"""
		关闭前检查寄售状态
		"""
		self.__checkOperation()
		self.__onHide()

	def show( self, destroyTime ) :
		Window.show( self )
		self.__pySellPanel.refreshRemainTime( destroyTime )
		self.__pySellPanel.onParentShow()
		self.__pyLogsPanel.onParentShow()
		player = BigWorld.player()
		self.pyStStallName_.text = labelGather.getText( "commissionsale:TSSellWindow", "shopName", player.getName() )

	def onLeaveWorld( self ) :
		self.__onHide()
		for pyTabPanel in self.__pyTabCtrl.pyPanels :
			pyTabPanel.reset()


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getTiShouNPC( self ) :
		return BigWorld.entities.get( self.__tishouNPCID, None )

	tishouNPC = property( _getTiShouNPC )								# 获取当前的替售NPC