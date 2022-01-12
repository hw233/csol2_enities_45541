# -*- coding: gb18030 -*-
#
# $Id: RollBox.py Exp $

"""
implement pickup box
"""
from guis import *
from guis.common.RootGUI import RootGUI
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.tooluis.CSRichText import CSRichText
from guis.controls.StaticText import StaticText
from guis.controls.ProgressBar import HProgressBar
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from ItemsFactory import ObjectItem
from guis.MLUIDefine import ItemQAColorMode, QAColor
import GUIFacade
import BigWorld
import Timer


PICKUP_LAST_TIME = 20.0 #roll框可持续显示最长时间


class RollBox( RootGUI ):

	__cc_hold_time = 1.0 #渐隐时间

	def __init__( self, box, pyBinder = None ):
		RootGUI.__init__( self, box )
		self.posZSegment_ = ZSegs.L4
		self.activable_ = False
		self.focus = False
		self.escHide_ 	= False
		self.__index = -1
		self.__limitCBID = 0
		self.__holdCBID = 0
		self.lastTime = PICKUP_LAST_TIME
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "BOTTOM"
		self.addToMgr()
		self.dropBoxID = 0
		self.rollCBID = 0
		self.pyBinder = pyBinder
		self.__initialize( box )

	def dispose( self ) :
		BigWorld.cancelCallback( self.__holdCBID )
		self.__cancelTimer()
		self.dropBoxID = 0
		RootGUI.dispose( self )

	def __del__( self ) :
		if Debug.output_del_RollBox :
			INFO_MSG( str( self ) )

	def __initialize( self, box ):
		self.__fader = GUI.AlphaShader()
		self.__fader.speed = 0.5
		self.__fader.value = 1.0
		self.__fader.reset()
		self.getGui().addShader( self.__fader )

		self.__pyRollItem = RollItem( box.rollItem.item, self )

		self.__pyDiceBtn = Button( box.diceBtn )
		self.__pyDiceBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyDiceBtn.onLClick.bind( self.__onRoll )

		self.__pyTimeHPBar = HProgressBar( box.timePanel.bar )
		self.__pyTimeHPBar.clipMode = "RIGHT"
		self.__pyTimeHPBar.value = 1.0

		self.__pyCloseBtn = Button( box.closeBtn )
		self.__pyCloseBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyCloseBtn.onLClick.bind( self.__onHide )

		self.__pyRtName = CSRichText( box.rollItem.clipPanel )
		self.__pyRtName.text = ""

		self.__pyStPoint = StaticText( box.stPoint )
		self.__pyStPoint.text = ""

	def __onRoll( self ):
		"""
		掷骰子
		"""
		if not self.__pyRollItem.itemInfo:
			return
		BigWorld.player().cell.rollRandom( self.dropBoxID, self.index )

	def updateInfo( self, itemInfo ):
		"""
		更新roll物品信息
		"""
		self.__pyRollItem.update( itemInfo )
		if itemInfo is not None:
			quality = itemInfo.quality
			name = itemInfo.name()
			color = QAColor[ quality ]
			self.__pyRtName.text = PL_Font.getSource( "%s"%name, fc = color )
		else:
			pass

	def __updateRollBar( self ):
		"""
		更新倒计时条
		"""
		self.lastTime -= 1.0
		self.__pyTimeHPBar.value -= 1.0/PICKUP_LAST_TIME
		if self.lastTime <= 0.0: #20秒后自动关闭，默认放弃roll
			self.__holdCBID = BigWorld.callback( self.__cc_hold_time, self.__endHolding )
			self.__cancelTimer()
			BigWorld.player().cell.abandonRoll( self.dropBoxID, self.index )

	def __cancelTimer( self ):
		Timer.cancel( self.__limitCBID )
		self.__limitCBID = 0

	def __endHolding( self ) :
		self.__fader.value = 0
		BigWorld.callback( self.__fader.speed, self.dispose )

	def __onHide( self ):
		"""
		自己关闭，放弃Roll
		"""
		self.__cancelTimer()
		BigWorld.player().cell.abandonRoll( self.dropBoxID, self.index )

	def onLClick_( self, mods ) :
		"""
		SHITF+鼠标左键,粘贴到剪切板
		"""
		RootGUI.onLClick_( self, mods )
		if mods == MODIFIER_SHIFT and self.__pyRollItem.itemInfo is None:
			name = self.__pyRollItem.itemInfo.name()
			csol.setClipboard( name )
	# -------------------------------------------------------
	# public
	# -------------------------------------------------------
	def show( self ):
		RootGUI.show( self )
		self.__limitCBID = Timer.addTimer( 0, 1.0, self.__updateRollBar )

	def hide( self ):
		BigWorld.cancelCallback( self.rollCBID )
		ECenter.fireEvent( "EVT_ON_HOLD_HIDE_BOX", self.dropBoxID, self.index )
		RootGUI.hide( self )

	def holdHide( self ):
		self.__holdCBID = BigWorld.callback( self.__cc_hold_time, self.__endHolding )

	def setRollPoint( self, point ):
		self.__pyStPoint.text = str( point )
		self.__pyDiceBtn.enable = False
		self.rollCBID = BigWorld.callback( 2.0, self.hide )

	def onLeaveWorld( self ):
		BigWorld.player().cell.abandonRoll( self.dropBoxID, self.index )
		self.dispose()

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	def _getIndex( self ):
		return self.__index

	def _setIndex( self, index ):
		self.__index = index

	index = property( _getIndex, _setIndex )

	left = RootGUI.left
	r_left = RootGUI.r_left
	center = RootGUI.center
	r_center = RootGUI.r_center
	right = RootGUI.right
	r_right = RootGUI.r_right
	top = RootGUI.top
	r_top = RootGUI.r_top
	middle = RootGUI.middle
	r_middle = RootGUI.r_middle
	bottom = RootGUI.bottom
	r_bottom = RootGUI.r_bottom
	visible = property( RootGUI._getVisible, lambda self, vs : vs )		# 设置 visible 属性无效

# ------------------------------------------------------------------
from guis.controls.Control import Control
from guis.common.PyGUI import PyGUI
import csol

class RollItem( Control ):

	def __init__( self, item, pyBinder = None ):
		Control.__init__( self, item, pyBinder )
		self.__pyItem = BOItem( item.item )
		self.itemInfo = None

	def update( self, itemInfo ):
		self.__pyItem.update( itemInfo )
		self.itemInfo = itemInfo
		quality = itemInfo is None and 1 or itemInfo.quality
		util.setGuiState( self.getGui(), ( 4, 2 ), ItemQAColorMode[quality] )

	def onRClick_( self, mods ):
		"""
		右键拾取
		"""
		Control.onRClick_( self, mods )
		if self.__pyItem.itemInfo is None:return


# -----------------------------------------------------------------
class RollsManager:
	__cc_max_rows 	= 3 				#最多显示3个
	__cc_spacing	= 1.0				#之间间隔
	__cc_v_site		= 0.73				#垂直方向的显示位置（目前设为屏幕 7/10 位置处

	def __init__( self ):
		self.__pyRollBoxs = WeakList()
		self.__triggers = {}
		self.__registerTriggers()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_SHOW_ROLL_WINDOW"] 		= self.__onRollShow
		self.__triggers["EVT_ON_ITEM_ROLL_SUCCEED"]		= self.__onItemRollSucc
		self.__triggers["EVT_ON_ITEM_ROLL_CANCEL"]		= self.__onRollCancel
		self.__triggers["EVT_ON_RECEIVE_ROLL_POINT"]	= self.__onReceivePoint
		self.__triggers["EVT_ON_CLOSE_ROLL_BOX"]		= self.__onCloseRollBox
		self.__triggers["EVT_ON_HOLD_HIDE_BOX"]			= self.__onHoldHide
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.unregisterEvent( key, self )

	# ----------------------------------------------------------
	def __onRollShow(self, index, item, dropBoxID ):
		"""
		显示ROLL界面,并排列添加的物品
		"""
		#self.dropBoxID = dropBoxID
		player = BigWorld.player()
		if not player.rollState: #设置为不拾取，则不弹出
			return
		itemInfo = ObjectItem( item )
		if not rds.statusMgr.isInWorld() :
			return
		box = GUI.load( "guis/tooluis/pickupbox/rollbox.gui" )
		uiFixer.firstLoadFix( box )
		pyRollBox = RollBox( box )
		pyRollBox.r_top = 1.0 - 2*self.__cc_v_site
		pyRollBox.r_center = 0.0
		pyRollBox.updateInfo( itemInfo )
		pyRollBox.index = index
		pyRollBox.dropBoxID = dropBoxID
		self.__pyRollBoxs.insert( 0, pyRollBox )
		pyRollBox.show()
		self.__layout()

	def __onItemRollSucc( self, index ):
		"""
		物品被分配成功后的回调，销毁对应窗口
		"""
		for pyRollBox in self.__pyRollBoxs:
			if pyRollBox.index == index:
				self.__pyRollBoxs.remove( pyRollBox )
				pyRollBox.holdHide()
				if len( self.__pyRollBoxs ) > 0:
					self.__layout()

	def __onRollCancel( self, index ):
		"""
		某个物品取消roll的回调
		"""
		for pyRollBox in self.__pyRollBoxs:
			if pyRollBox.index == index:
				self.__pyRollBoxs.remove( pyRollBox )
				pyRollBox.dispose()
				if len( self.__pyRollBoxs ) > 0:
					self.__layout()

	def __onCloseRollBox( self, index, dropBoxID ):
		for gbIndex, pyRollBox in enumerate( self.__pyRollBoxs ):
			if pyRollBox.index == index and pyRollBox.dropBoxID == dropBoxID:
				self.__pyRollBoxs.remove( pyRollBox )
				pyRollBox.dispose()
		if len( self.__pyRollBoxs ) > 0:
			self.__reLayout()


	def __onReceivePoint( self, index, point, dropBoxID ):
		for pyRollBox in self.__pyRollBoxs:
			if pyRollBox.index == index and pyRollBox.dropBoxID == dropBoxID:
				pyRollBox.setRollPoint( point )
				break

	def __onHoldHide( self, dropBoxID, index ):
		for pyRollBox in self.__pyRollBoxs:
			if pyRollBox.index == index and pyRollBox.dropBoxID == dropBoxID:
				self.__pyRollBoxs.remove( pyRollBox )
				pyRollBox.dispose()
				break
		if len( self.__pyRollBoxs ) > 0:
			self.__reLayout()

	def __reLayout( self ):
		pyTmpBox = self.__pyRollBoxs[0]
		pyTmpBox.r_top = 1.0 - 2*self.__cc_v_site
		pyTmpBox.r_center = 0.0
		for index in xrange( 1, len( self.__pyRollBoxs ) ) :
			pyRollBox = self.__pyRollBoxs[index]
			pyRollBox.bottom = pyTmpBox.top - self.__cc_spacing
			pyTmpBox = pyRollBox

	def __layout( self ):
		"""
		重新排列所有roll的位置
		"""
		pyTmpBox = self.__pyRollBoxs[0]
		for index in xrange( 1, len( self.__pyRollBoxs ) ) :
			pyRollBox = self.__pyRollBoxs[index]
			pyRollBox.bottom = pyTmpBox.top - self.__cc_spacing
			pyTmpBox = pyRollBox

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		for pyRollBox in self.__pyRollBoxs:
			pyRollBox.onLeaveWorld()
