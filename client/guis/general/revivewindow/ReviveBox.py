# -*- coding: gb18030 -*-

# 复活地点选择窗口
# written by gjx 2009-4-21
# implement the ReviveBox class
#

import csdefine
import csstatus
import csconst
import love3
from bwdebug import INFO_MSG
from guis import *
from Time import Time
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from AbstractTemplates import Singleton
from LabelGather import labelGather
import Timer

class ReviveBox( Singleton, Window ) :

	__triggers = {}

	def __init__( self ) :
		wnd = GUI.load( "guis/general/revivewindow/revivewnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.escHide_ = False
		self.h_dockStyle = "CENTER"							# 水平居中显示
		self.v_dockStyle = "MIDDLE"							# 垂直居中显示
		self.__cdTimer = 0
		self.__revEndTime = 0
		self.__initialize( wnd )
		self.addToMgr( "reviveBox" )

	def __del__( self ) :
		Window.__del__( self )
		if Debug.output_del_ReviveBox :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		self.__pyCityReviveBtn = HButtonEx( wnd.cityBtn )		# 回城复活按钮
		self.__pyCityReviveBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyCityReviveBtn.isOffsetText = True

		self.__pyCurrPointReviveBtn = HButtonEx( wnd.currBtn )	# 原地复活按钮
		self.__pyCurrPointReviveBtn.onLClick.bind( self.__reviveAtCurrPoint )
		self.__pyCurrPointReviveBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyCurrPointReviveBtn.isOffsetText = True

		self.__pySText = StaticText( wnd.st_city )

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setLabel( wnd.lbTitle, "ReviveBox:main", "lbTitle" )
		labelGather.setLabel( wnd.st_city, "ReviveBox:main", "stCity" )
		labelGather.setLabel( wnd.st_currPoint, "ReviveBox:main", "stCurrPoint" )
		labelGather.setPyBgLabel( self.__pyCityReviveBtn, "ReviveBox:main", "cityBtn" )
		labelGather.setPyBgLabel( self.__pyCurrPointReviveBtn, "ReviveBox:main", "currBtn" )


	# -------------------------------------------------
	# about revive
	# -------------------------------------------------
	def __canReviveAtCurrPoint( self ) :
		"""
		查找玩家身上的归命符，判断是否能原地复活
		"""
		player = BigWorld.player()
		if not player.checkItemFromNKCK_( 110103001, 1 ) :
			player.statusMessage( csstatus.ROLE_CONDITION_OF_REVIVE_ORIGINAL )
			return False
		if player.iskitbagsLocked() : 					# 如果背包已上锁，则返回
			player.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return False
		return True

	def __reviveInCity( self ) :
		"""
		回到绑定复活点复活
		"""
		player = BigWorld.player()
		spaceLabel = player.getSpaceLabel()
		spaceType = player.getCurrentSpaceType()
		if spaceType == csdefine.SPACE_TYPE_CITY_WAR:
			player.tong_onCityWarRelive( 1 )
		else:
			player.cell.revive( csdefine.REVIVE_ON_CITY )
		self.hide()

	def __reviveInTemple( self ) :
		"""
		在当前副本的复活点复活
		"""
		player = BigWorld.player()
		player.cell.revive( csdefine.REVIVE_ON_SPACECOPY )
		self.hide()

	def __revivePreSpace( self ) :
		"""
		在当前进入NPC处复活
		"""
		player = BigWorld.player()
		player.cell.revive( csdefine.REVIVE_PRE_SPACE )
		self.hide()

	def __reviveAtCurrPoint( self ) :
		"""
		使用归命符原地复活
		"""
		player = BigWorld.player()
		if not self.__canReviveAtCurrPoint() :
			return
		player.cell.useItemRevive()
		self.hide()

	def __reviveDestCopy( self ):
		"""
		天命轮回复活
		"""
		player = BigWorld.player()
		player.cell.roleReviveCostLivePoint()
		self.hide()

	def __reviveCityWarFianlCopy( self ):
		"""
		帮会夺城战决赛
		"""
		player = BigWorld.player()
		player.cell.roleReviveCostLivePoint()
		self.hide()

	def __formatToNoCurrPoint( self ) :
		"""
		不显示原地复活按钮，并重新对齐其他按钮
		"""
		self.gui.st_currPoint.visible = False
		self.__pyCurrPointReviveBtn.visible = False
		self.__pyCityReviveBtn.onLClick.bind( self.__reviveInCity )
		self.__pyCityReviveBtn.top = 76
		self.__pySText.top = 105

	def __revCountdown( self ):
		"""
		帮会战场倒计时复活
		"""
		if not self.visible:
			self.__cancelRevTimer()
			return
		remTime = self.__revEndTime - Time.time()
		self.pyLbTitle_.text = labelGather.getText( "ReviveBox:main", "revTime" )%remTime
		if remTime <= 0:
			BigWorld.player().tong_onCityWarRelive( 1 )
			self.__cancelRevTimer()
			self.hide()

	def __revCountDownFengQi( self ):
		if not self.visible:
			self.__cancelRevTimer()
			return

		remTime = self.__revEndTime - Time.time()
		self.pyLbTitle_.text = labelGather.getText( "ReviveBox:main", "revTime" )%remTime
		if remTime <= 0:
			self.__reviveInTemple()
			self.__cancelRevTimer()
			self.hide()

	def __revCountDownYiJie( self ):
		if not self.visible:
			self.__cancelRevTimer()
			return
		remTime = self.__revEndTime - Time.time()
		showTime = int( remTime + 0.5 )
		self.pyLbTitle_.text = labelGather.getText( "ReviveBox:main", "revTime" )%showTime
		if remTime <= 0:
			self.__cancelRevTimer()
			self.__pyCityReviveBtn.enable = True

	def __revCountDownDestCopy( self ):
		if not self.visible:
			self.__cancelRevTimer()
			return
		remTime = self.__revEndTime - Time.time()
		self.pyLbTitle_.text = labelGather.getText( "ReviveBox:main", "revTime" )%remTime
		if remTime <= 0:
			self.__reviveDestCopy()
			self.__cancelRevTimer()
			self.hide()

	def __revCountDownMercuryCore( self ):
		if not self.visible:
			self.__cancelRevTimer()
			return

		remTime = self.__revEndTime - Time.time()
		self.pyLbTitle_.text = labelGather.getText( "ReviveBox:main", "revTime" )%remTime
		if remTime <= 0:
			self.__reviveInTemple()
			self.__cancelRevTimer()
			self.hide()

	def __reviveOnPlaneEntry(self):
		BigWorld.player().cell.revive(csdefine.REVIVE_ON_SPACECOPY)
		self.hide()

	def __cancelRevTimer( self ):
		"""
		停止倒计时
		"""
		Timer.cancel( self.__cdTimer )
		self.__cdTimer = 0

	# -------------------------------------------------
	@classmethod
	def __onShow( SELF ) :
		SELF.inst.show()

	@classmethod
	def __onHide( SELF ) :
		if SELF.insted :
			SELF.inst.hide()

	@classmethod
	def __deadInFalling( SELF ) :
		self = SELF.inst
		self.__formatToNoCurrPoint()
		Window.show( self )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@classmethod
	def registerTriggers( SELF ) :
		SELF.__triggers["EVT_ON_SHOW_REVIVE_BOX"] = SELF.__onShow
		SELF.__triggers["EVT_ON_HIDE_REVIVE_BOX"] = SELF.__onHide
		SELF.__triggers["EVT_ON_SHOW_REVIVE_BOX_ON_FALLING_DOWN"] = SELF.__deadInFalling
		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )

	def show( self ) :
		"""
		打开窗口
		"""
		player = BigWorld.player()
		currSpaceLabel = player.getSpaceLabel()
		spaceType = player.getCurrentSpaceType()
		if currSpaceLabel in csconst.COPY_REVIVE_PREVIOUS :			#NPC复活
			self.__pyCityReviveBtn.onLClick.bind( self.__revivePreSpace )
			self.__pyCityReviveBtn.text = labelGather.getText( "ReviveBox:main", "revivePreBtn" )
			self.__pySText.text = labelGather.getText( "ReviveBox:main", "stPreBtn" )
			self.gui.st_currPoint.visible = False
			self.__pyCurrPointReviveBtn.visible = False
			self.__pyCityReviveBtn.top = 76
			self.__pySText.top = 105
		elif love3.g_SpaceCopyReviveCfg.reviveIsCfg( currSpaceLabel ) :
			self.__pyCityReviveBtn.onLClick.bind( self.__reviveInTemple )
			self.__pyCityReviveBtn.text = labelGather.getText( "ReviveBox:main", "ReviveBtn" )
			self.__pySText.text = labelGather.getText( "ReviveBox:main", "stRevive" )
			if spaceType in [ csdefine.SPACE_TYPE_YXLM, csdefine.SPACE_TYPE_FENG_HUO_LIAN_TIAN, csdefine.SPACE_TYPE_CAMP_FENG_HUO_LIAN_TIAN ]:
				self.gui.st_currPoint.visible = False
				self.__pyCurrPointReviveBtn.visible = False
				self.__pyCityReviveBtn.top = 76
				self.__pySText.top = 105
			elif spaceType == csdefine.SPACE_TYPE_MERCURY_CORE_MAP:
				self.__pyCityReviveBtn.text = labelGather.getText( "ReviveBox:main", "currBtn" )
				self.gui.st_currPoint.visible = False
				self.__pyCurrPointReviveBtn.visible = False
				self.__pyCityReviveBtn.top = 76
				self.__pySText.visible = False
				if self.__cdTimer > 0:
					self.__cancelRevTimer()
				self.__revEndTime = Time.time() + 5.0
				self.__cdTimer = Timer.addTimer( 0, 1, self.__revCountDownMercuryCore )
			elif spaceType == csdefine.SPACE_TYPE_YE_ZHAN_FENG_QI:
				self.__pyCityReviveBtn.text = labelGather.getText( "ReviveBox:main", "ReviveBtn" )
				self.__pySText.text = labelGather.getText( "ReviveBox:main", "stRandomBtn" )
				if self.__cdTimer > 0:
					self.__cancelRevTimer()
				self.__revEndTime = Time.time() + player.fengQiReviveTime
				self.__cdTimer = Timer.addTimer( 0, 1, self.__revCountDownFengQi )
		elif spaceType == csdefine.SPACE_TYPE_DESTINY_TRANS:
			self.__pyCityReviveBtn.onLClick.bind( self.__reviveDestCopy )
			self.__pyCityReviveBtn.text = labelGather.getText( "ReviveBox:main", "stDestRevive" )
			self.__pySText.text = labelGather.getText( "ReviveBox:main", "livePoint" )%player.livePoint
			self.gui.st_currPoint.visible = False
			self.__pyCurrPointReviveBtn.visible = False
			self.__pyCityReviveBtn.top = 76
			self.__pySText.top = 105
			if self.__cdTimer > 0:
				self.__cancelRevTimer()
			self.__revEndTime = Time.time() + 10.0
			self.__cdTimer = Timer.addTimer( 0, 1, self.__revCountDownDestCopy )
		elif spaceType == csdefine.SPACE_TYPE_YI_JIE_ZHAN_CHANG:
				self.__formatToNoCurrPoint()
				self.__pyCityReviveBtn.onLClick.bind( self.__reviveInTemple )
				self.__pyCityReviveBtn.text = labelGather.getText( "ReviveBox:main", "ReviveBtn" )
				self.__pySText.text = labelGather.getText( "ReviveBox:main", "killerName" )%player.yiJieKiller
				self.__pyCityReviveBtn.enable = False
				if self.__cdTimer > 0:
					self.__cancelRevTimer()
				self.__revEndTime = Time.time() + player.yiJieReviveTime
				self.__cdTimer = Timer.addTimer( 0, 1, self.__revCountDownYiJie )
		elif spaceType == csdefine.SPACE_TYPE_CITY_WAR_FINAL:
			self.__pyCityReviveBtn.onLClick.bind( self. __reviveCityWarFianlCopy )
			self.__pyCityReviveBtn.text = labelGather.getText( "ReviveBox:main", "ReviveBtn" )
			self.__pySText.text = labelGather.getText( "ReviveBox:main", "stRevPoint" )
			if self.__cdTimer > 0:
				self.__cancelRevTimer()
			self.__revEndTime = Time.time() + 5.0
			self.__cdTimer = Timer.addTimer( 0, 1, self.__revCountdown )
		elif spaceType == csdefine.SPACE_TYPE_WM:
			self.__pyCityReviveBtn.onLClick.bind( self.__reviveOnPlaneEntry )
			self.__pyCityReviveBtn.text = labelGather.getText( "ReviveBox:main", "revive_entry" )
			self.__pySText.text = labelGather.getText( "ReviveBox:main", "revive_entry_dsp" )
		else :
			self.__pyCityReviveBtn.onLClick.bind( self.__reviveInCity )
			self.__pyCityReviveBtn.text = labelGather.getText( "ReviveBox:main", "cityBtn" )
			self.__pySText.text = labelGather.getText( "ReviveBox:main", "stCity" )
			if spaceType == csdefine.SPACE_TYPE_CITY_WAR:
				self.__pyCityReviveBtn.text = labelGather.getText( "ReviveBox:main", "ReviveBtn" )
				self.__pySText.text = labelGather.getText( "ReviveBox:main", "stRevPoint" )
				if self.__cdTimer > 0:
					self.__cancelRevTimer()
				self.__revEndTime = Time.time() + 10.0
				self.__cdTimer = Timer.addTimer( 0, 1, self.__revCountdown )
		Window.show( self )

	def hide( self ) :
		Window.hide( self )
		self.removeFromMgr()
		player = BigWorld.player()
		spaceType = player.getCurrentSpaceType()
		if spaceType == csdefine.SPACE_TYPE_CITY_WAR and \
		self.__cdTimer > 0:
			self.__cancelRevTimer()
		self.dispose()

	def onLeaveWorld( self ) :
		self.hide()

	def dispose( self ) :
		Window.dispose( self )
		self.__class__.releaseInst()

	@classmethod
	def onEvent( SELF, macroName, *args ) :
		SELF.__triggers[macroName]( *args )

ReviveBox.registerTriggers()