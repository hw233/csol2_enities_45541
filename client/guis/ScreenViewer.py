# -*- coding: gb18030 -*-

"""
屏幕初始化
"""

import re
import Math
import csol
import csdefine
import Const
import csconst
import utils
import StringFormat
import event.EventCenter as ECenter
from AbstractTemplates import Singleton
from Function import Functor
from cscustom import Rect
from Helper import uiopHelper, pixieHelper
from guis import *
from guis.common.RootGUI import RootGUI
from guis.tooluis.CSRichText import CSRichText
from guis.common.PyGUI import PyGUI
from Weaker import WeakList
import Define
import config.client.labels.GUIFacade as lbDatas
# --------------------------------------------------------------------
# 屏幕 UI 管理器
# --------------------------------------------------------------------
class ScreenViewer( Singleton ) :
	def __init__( self ) :
		# 打开/关闭所有界面
		self.__isEmptyScreen = False				# 是否处于清屏状态

		# 清屏时忽略的窗口
		self.__pyRootsResistHidden = WeakList()

		# 按键盘键移动角色提示
		self.__rolePos = Math.Vector3()				# 角色上一侦测的位置
		self.__pyWalkGuiders = None					# 操作指示器
		self.__roleMoveTriggers = {}

		# 如何选中目标提示
		self.__entityFocusTipID = 0x0060			# 选中 entity 的操作提示
		self.__entityFocusTriggers = {}				# 选中 entity 所需要的各种事件

		# 如何攻击目标提示
		self.__attackTipID = 0x0061					# 攻击提示 id
		self.__attackTriggers = {}					# 攻击 entity 所需的各种事件
		self.__moveAttickTipCBID = 0				# 移动攻击提示框的回调 id

		# 拾取掉落箱子提示
		self.__pickupTipID = 0x0070					# 拾取提示 id
		self.__pickupTriggers = {}					# 拾取提示相关事件
		self.__droppedBoxID = 0 					# 掉落箱子的 id
		self.__movePickupTipCBID = 0				# 移动掉落提示框的回调 id

		# 剧情提示
		self.__scenaioShowTime = 2.0				# 每一行显示的延时
		self.__scenaioHideTime = 3.0				# 显示完毕后，多少秒会消失
		self.__rtScenaio = None						# 第一个参数为，第二个参数为
		self.__rtScenaio2 = None					# 剧情提示方式2
		self.__rtScenaio3 = None					# 全屏幕字幕播放
		self.__cb	  = None					#回调

		self.__rtScenaio4 = None
		self.__cb4 = None

		self.__rtScenaio5 = []
		self.__cb5 = None

		self.__pyScreenFader = None					# 屏幕alpha衰减器
		self.__pyDangerWarning = None				# 屏幕闪烁警告
		self.__scenarioTriggers = {}				# 剧情提示相关事件
		self.__pyChangeUIEffect = None				# 屏幕换UI效果相关
		self.__registerScenarioEvents()
		self.__hideByShortCut = False  #快捷键触发 比如CTR+G
#		UIOSentinel().attach( 0x0002, self.__showWalkGuider )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerRoleMoveEvents( self ) :
		"""
		注册角色移动提示所需的各种事件
		"""
		self.__roleMoveTriggers["EVT_ON_RESOLUTION_CHANGED"] = self.__onResolutionChangedForRoleMove
		for key in self.__roleMoveTriggers :
			ECenter.registerEvent( key, self )

	def __registerEntityFocusEvents( self ) :
		"""
		注册选中 entity 所需的各种事件
		"""
		self.__entityFocusTriggers["EVT_ON_ENTITY_GOT_FOCUS"] = self.__onEntityGotFocus
		self.__entityFocusTriggers["EVT_ON_TARGET_BINDED"] = self.__onEntityBindedForFocus
		for key in self.__entityFocusTriggers :
			ECenter.registerEvent( key, self )

	def __registerAttackEvents( self ) :
		"""
		注册攻击 entity 提示所需的事件
		"""
		self.__attackTriggers["EVT_ON_TARGET_BINDED"] = self.__onEntityBinded
		self.__attackTriggers["EVT_ON_TARGET_UNBINDED"] = self.__onEntityUnbinded
		self.__attackTriggers["EVT_ON_ATTACK_STATE_CHANGTED"] = self.__onAttackStateChanged
		for key in self.__attackTriggers :
			ECenter.registerEvent( key, self )

	def __registerPickupEvents( self ) :
		"""
		注册拾取提示事件
		"""
		self.__pickupTriggers["EVT_ON_ITEM_DROPPED"] = self.__onItemDropped
		self.__pickupTriggers["EVT_ON_ITEM_PICKUP"] = self.__onItemPickup
		for key in self.__pickupTriggers :
			ECenter.registerEvent( key, self )

	def __registerScenarioEvents( self ) :
		"""
		注册剧情提示相关事件
		"""
		self.__scenarioTriggers["EVT_ON_SHOW_SCENARIO_TIPS"] = self.__onShowScenarioTips
		self.__scenarioTriggers["EVT_ON_SHOW_SCENARIO_TIPS2"] = self.__onShowScenarioTips2
		self.__scenarioTriggers["EVT_ON_INTERRUPT_SCENARIO_TIPS2"] = self.__onInterruptScenarioTips2
		self.__scenarioTriggers["EVT_ON_SHOW_SCENARIO_TIPS3"] = self.__onShowScenarioTips3	#全屏字幕事件add by wuxo 2011-9-6
		self.__scenarioTriggers["EVT_ON_SHOW_SCENARIO_TIPS4"] = self.__onShowScenarioTips4	#屏幕下方滚动字幕 add by wuxo 2012-3-19
		self.__scenarioTriggers["EVT_ON_SHOW_SCENARIO_TIPS5"] = self.__onShowScenarioTips5	#电影字幕 add by wuxo 2012-8-14
		self.__scenarioTriggers["EVT_ON_INTERRUPT_SCENARIO_TIPS4"] = self.__onInterruptScenarioTips4
		self.__scenarioTriggers["EVT_ON_INTERRUPT_SCENARIO_TIPS5"] = self.__onInterruptScenarioTips5
		self.__scenarioTriggers["EVT_ON_SCREENBLUR_END"]      = self.__onEndScreenBlur	     #结束全屏模糊
		self.__scenarioTriggers["EVT_ON_VISIBLE_ROOTUIS"] = self.__setRootsVisible
		self.__scenarioTriggers["EVT_ON_BRIGHTEN_SCREEN"] = self.__onBrightenScreen
		self.__scenarioTriggers["EVT_ON_BLACKEN_SCREEN"] = self.__onBlackenScreen     #屏幕变色事件
		self.__scenarioTriggers["EVT_ON_FLICKER_SCREEN"] = self.__onFlickerScreen     #屏幕周边闪烁警告
		self.__scenarioTriggers["EVT_ON_RESTORE_SCREEN"] = self.__onRestoreScreen     #屏幕周边闪烁恢复
		self.__scenarioTriggers["EVT_ON_START_CHANGE_UI_EFFECT"] = self.__onStartChangeUIEffect		#开始屏幕换UI效果
		self.__scenarioTriggers["EVT_ON_STOP_CHANGE_UI_EFFECT"] = self.__onStopChangeUIEffect		#结束换UI效果

		for key in self.__scenarioTriggers :
			ECenter.registerEvent( key, self )

	# ---------------------------------------
	def __deregisterEvents( self, triggers ) :
		"""
		注销选中 entity 所需的各种事件
		"""
		for key in triggers :
			ECenter.unregisterEvent( key, self )
		triggers.clear()


	# -------------------------------------------------
	# 清屏
	# -------------------------------------------------
	def __setRootsVisible( self, visible ) :
		"""
		设置所有窗口是否可见
		"""
		if BigWorld.player().__class__.__name__ != "PlayerRole":
			return 
		self.__isEmptyScreen = visible
		self.__toggleAllRoots()
		BigWorld.player().pointReviveClew()

	def __toggleAllRoots( self ) :
		"""
		显示/隐藏所有当前显示的窗口( 清屏 )
		"""
		for pyRoot in rds.ruisMgr.getVSRoots() :				# 遍历所有当前可见的窗口
			if pyRoot not in self.__pyRootsResistHidden:
				pyRoot.getGui().visible = self.__isEmptyScreen		# 设置其可见性
		self.__isEmptyScreen = not self.__isEmptyScreen
		return True

	def __toggleAllRootsByShortCut( self ):
		"""
		显示/隐藏所有当前显示的窗口( 清屏 )快捷键触发
		"""
		self.__hideByShortCut = not self.__isEmptyScreen
		for pyRoot in rds.ruisMgr.getVSRoots() :				# 遍历所有当前可见的窗口
			if pyRoot not in self.__pyRootsResistHidden:
				pyRoot.getGui().visible = self.__isEmptyScreen		# 设置其可见性
		self.__isEmptyScreen = not self.__isEmptyScreen
		BigWorld.player().pointReviveClew()
		if rds.statusMgr.isOffline():
			rds.statusMgr.changeStatus( Define.GST_OFFLINE )
		return True

	def getHideByShortCut( self ):
		return self.__hideByShortCut

	# -------------------------------------------------
	# 游戏屏幕效果控制
	# -------------------------------------------------
	def __onBrightenScreen( self ) :
		"""
		使屏幕从变色状态恢复到正常状态
		"""
		if not self.__pyScreenFader : return
		self.__pyScreenFader.fadeout()
		def callback() :
			if not self.__pyScreenFader : return
			self.__pyScreenFader.dispose()
			self.__pyScreenFader = None
		BigWorld.callback( self.__pyScreenFader.fadeSpeed, callback )

	def __onBlackenScreen( self, colour = None, time = -1 ) :
		"""
		使屏幕变色,默认为变黑
		@type 	colour: list or tuple
		@param  colour: RGB(包含alpha值即4位)
		"""
		if self.__pyScreenFader : return							# 已经处于变色状态
		self.__pyScreenFader = ScreenFader()
		if colour != None :
			self.__pyScreenFader.gui.colour.set( colour )
		self.__pyScreenFader.fadein()
		if time > 0 :
			hold_time = self.__pyScreenFader.fadeSpeed + time
			BigWorld.callback( hold_time, self.__onBrightenScreen )

	def __onFlickerScreen( self, colour = None ) :
		"""
		屏幕四周闪烁,危险警告
		"""
		if self.__pyDangerWarning : return
		self.__pyDangerWarning = DangerWarning()
		if colour != None :
			self.__pyDangerWarning.gui.colour.set( colour )
		self.__pyDangerWarning.fadein()

	def __onRestoreScreen( self ) :
		"""
		屏幕闪烁恢复
		"""
		if not self.__pyDangerWarning : return
		self.__pyDangerWarning.fadeout()
		if not self.__pyDangerWarning : return
		self.__pyDangerWarning.dispose()
		self.__pyDangerWarning = None

	def __onStartChangeUIEffect( self ):
		if self.__pyChangeUIEffect:return
		self.__isEmptyScreen = False
		self.__toggleAllRoots()

		self.__pyChangeUIEffect = ChangeUIEffect()
		self.__pyChangeUIEffect.show()

	def __onStopChangeUIEffect( self ):
		if not self.__pyChangeUIEffect:return
		self.__isEmptyScreen = True
		self.__toggleAllRoots()
		self.__pyChangeUIEffect.hide()
		self.__pyChangeUIEffect.dispose()
		self.__pyChangeUIEffect = None
	# -------------------------------------------------
	# 处理角色移动操作提示
	# -------------------------------------------------
	def __showWalkGuider( self, uioKey ) :
		"""
		显示角色移动指示
		"""
		tTips = uiopHelper.getTips( 0x0001 )		# 往前移动提示
		if tTips is None : return
		lTips = uiopHelper.getTips( 0x0002 )		# 向左移动提示
		bTips = uiopHelper.getTips( 0x0003 )		# 向右移动提示
		rTips = uiopHelper.getTips( 0x0004 )		# 往后移动提示
		pyLGuider = WalkGuider( "L", lTips.text )
		pyLGuider.left = 0
		pyLGuider.r_middle = 0
		pyRGuider = WalkGuider( "R", rTips.text )
		pyRGuider.r_right = 1
		pyRGuider.r_middle = 0
		pyTGuider = WalkGuider( "T", tTips.text )
		pyTGuider.top = 0
		pyTGuider.r_center = 0
		pyBGuider = WalkGuider( "B", bTips.text )
		pyBGuider.r_center = 0
		pyBGuider.r_bottom = -1
		self.__pyWalkGuiders = ( pyLGuider, pyRGuider, pyTGuider, pyBGuider )

		WalkGuider.flash()
		self.__detectRolePos()

	def __hideWalkGuider( self ) :
		"""
		隐藏角色移动指示
		"""
		WalkGuider.unflash()
		if not self.__pyWalkGuiders : return
		for pyGuider in self.__pyWalkGuiders :
			pyGuider.dispose()
		self.__pyWalkGuiders = None
		self.__deregisterEvents( self.__roleMoveTriggers )

	def __detectRolePos( self ) :
		"""
		侦测角色位置
		"""
		rolePos = BigWorld.player().position
		if rolePos.distTo( self.__rolePos ) > 0.5 :					# 角色离开原地 0.5 米，被认为发生了移动
			BigWorld.callback( 3.0, self.__hideWalkGuider )
		else :
			BigWorld.callback( 1.0, self.__detectRolePos )

	def __onResolutionChangedForRoleMove( self, preReso ) :
		"""
		屏幕分辨率改变时被调用
		"""
		if self.__pyWalkGuiders is None : return
		self.__pyWalkGuiders[0].r_middle = 0
		self.__pyWalkGuiders[1].r_right = 1
		self.__pyWalkGuiders[1].r_middle = 0
		self.__pyWalkGuiders[2].r_center = 0
		self.__pyWalkGuiders[2].r_top = 1
		self.__pyWalkGuiders[3].r_center = 0
		self.__pyWalkGuiders[3].r_bottom = -1

	# -------------------------------------------------
	# 处理鼠标移动到 entity 身上时的提示
	# -------------------------------------------------
	def __moveEntityGetFocusTips( self, dx, dy, dz ) :
		"""
		跟随鼠标移动实体获得焦点的提示
		"""
		mpos = Math.Vector2( csol.pcursorPosition() ) - ( 25, 25 )
#		toolbox.infoTip.moveOperationTips( self.__entityFocusTipID, mpos )

	def __hideEntityGetFocusTips( self ) :
		"""
		隐藏实体获得焦点提示
		"""
#		toolbox.infoTip.hideOperationTips( self.__entityFocusTipID )
		LastMouseEvent.detach( self.__moveEntityGetFocusTips )
		self.__deregisterEvents( self.__entityFocusTriggers )

	def __onEntityGotFocus( self, entID ) :
		"""
		鼠标移动到某个 entity 身上时，显示操作提示
		"""
		entity = BigWorld.entity( entID )
		if entity.getEntityType() not in csconst.ENTITIES_CAN_BE_SELECTED or \
			entity is BigWorld.player() :
				return
		mx, my = csol.pcursorPosition()
		bound = Rect( ( mx - 25, my - 25 ), ( 50, 50 ) )
#		toolbox.infoTip.showOperationTips( self.__entityFocusTipID, bound = bound )
		LastMouseEvent.attach( self.__moveEntityGetFocusTips )
		BigWorld.callback( 5.0, self.__hideEntityGetFocusTips )

	def __onEntityBindedForFocus( self, target ) :
		"""
		选中某个 entity 时被调用
		"""
		self.__hideEntityGetFocusTips()

	# -------------------------------------------------
	# 处理选中怪物时，弹出如何攻击的提示
	# -----------------------------------------------

	def __onEntityBinded( self, target ) :
		"""
		选中某个 entity 时被调用
		"""
		pass

	def __onEntityUnbinded( self, target ) :
		"""
		取消选中某个 entity 时被调用
		"""
		self.__hideAttackTips()

	def __onAttackStateChanged( self, state ) :
		"""
		角色的攻击状态改变时被调用
		"""
		if state != Const.ATTACK_STATE_NONE :
			self.__hideAttackTips()

	def __hideAttackTips( self ) :
		"""
		隐藏攻击目标操作提示
		"""
#		toolbox.infoTip.hideOperationTips( self.__attackTipID )
		BigWorld.cancelCallback( self.__moveAttickTipCBID )
		self.__deregisterEvents( self.__attackTriggers )
		self.__moveAttickTipCBID = 0

	def __onItemDropped( self, entity ) :
		"""
		entity 进入世界时被调用
		"""
		pass

	def __onItemPickup( self, entity ) :
		"""
		entity 离开世界时被调用
		"""
		if entity.id == self.__droppedBoxID :
			self.__hidePickupTips()

	def __hidePickupTips( self ) :
		"""
		隐藏拾取提示
		"""
#		toolbox.infoTip.hideOperationTips( self.__pickupTipID )
		self.__deregisterEvents( self.__pickupTriggers )
		BigWorld.cancelCallback( self.__movePickupTipCBID )
		self.__movePickupTipCBID = 0

	# -------------------------------------------------
	# 显示剧情提示
	# -------------------------------------------------
	def __onShowScenarioTips( self, tips, visible ) :
		"""
		收到剧情提示（这个剧情提示文本位于屏幕中间）
		visible ：是否隐藏玩家界面，False不隐藏，True隐藏
		"""
		if tips == "" : return
		if not rds.statusMgr.isInWorld() : return
		if not self.__rtScenaio :
			self.__rtScenaio = RTScenario()

		def callback() :
			self.__rtScenaio = None
			if self.__isEmptyScreen :
				if not visible:									# 不隐藏玩家界面
					self.__toggleAllRoots()						# 复屏

		if not self.__isEmptyScreen :							# 清屏
			self.__toggleAllRoots()

		self.__rtScenaio.show( tips, self.__scenaioShowTime, \
			self.__scenaioHideTime, callback )

	def __onShowScenarioTips2( self, tips, cb=None) :
		"""
		在屏幕下方的剧情提示，黑色背景
		"""
		if tips == "" : return
		if not rds.statusMgr.isInWorld() : return
		if not self.__rtScenaio2 :
			self.__rtScenaio2 = RTScenario2()
		self.__cb = cb

		def callback() :
			self.__rtScenaio2 = None
			if callable(cb):	#add by wuxo 2011-9-29
				cb()
			self.__cb = None
		tips = StringFormat.format( tips )
		self.__rtScenaio2.show( tips, 3, 5, callback )			# 每行间隔3秒，播放完后5秒消失

	def __onInterruptScenarioTips2(self):
		"""
		中断屏幕下方字幕播放，用于ESC
		"""
		def callback() :
			self.__rtScenaio2 = None
			self.__cb = None
		if self.__rtScenaio2:
			self.__rtScenaio2.hide(callback)


	def __onShowScenarioTips3( self, tips,showTimes,color ) :
		"""
		全屏字幕播放，黑色背景
		showTimes存放每行播放时间间隔
		"""
		if tips == "" : return
		if not rds.statusMgr.isInWorld() : return
		if not self.__rtScenaio3 :
			self.__rtScenaio3 = RTScenario3( color )

		def callback() :
			self.__rtScenaio3 = None

		tips = StringFormat.format( tips )
		self.__rtScenaio3.show( tips, showTimes, 1, callback )	# 每行间隔相应秒，播放完后1秒消失

	def __onShowScenarioTips4( self, tips, showTimes, cb=None) :
		"""
		在屏幕下方的剧情提示，黑色背景
		"""
		if tips == "" : return
		#if not rds.statusMgr.isInWorld() : return #登陆流程可能会用到 所以注释掉这个判断
		if not self.__rtScenaio4 :
			self.__rtScenaio4 = RTScenario4()
		self.__cb4 = cb
		def callback() :
			self.__rtScenaio4 = None
			if callable( cb ):
				cb()
			self.__cb4 = None
		tips = StringFormat.format( tips )
		self.__rtScenaio4.show( tips, showTimes, 0, callback )

	def __onInterruptScenarioTips4(self):
		"""
		中断屏幕下方字幕播放，用于ESC
		"""
		def callback() :
			self.__rtScenaio4 = None
			self.__cb4 = None
		if self.__rtScenaio4:
			self.__rtScenaio4.hide(callback)


	def __onShowScenarioTips5( self, tips, showTimes, cb=None) :
		"""
		上下夹屏的字幕，黑色背景
		"""
		if tips == "" : return
		if not rds.statusMgr.isInWorld() : return
		if not self.__rtScenaio5 :
			self.__rtScenaio5.append( RTScenario4() )
			self.__rtScenaio5.append( RTScenario5() )

		self.__cb5 = cb

		def callback() :
			self.__rtScenaio5 = []
			if callable(cb):
				cb()
			self.__cb5 = None
		tips = StringFormat.format( tips )
		self.__rtScenaio5[1].show()
		self.__rtScenaio5[0].show( tips, showTimes, 0, callback )

	def __onInterruptScenarioTips5(self):
		"""
		中断上下夹屏的字幕，用于ESC
		"""
		def callback() :
			self.__rtScenaio5 = []
			self.__cb5 = None
		if self.__rtScenaio5:
			self.__rtScenaio5[1].hide()
			self.__rtScenaio5[0].hide(callback)

	def __onEndScreenBlur(self):
		"""
		结束全屏模糊 add by wuxo 2011-10-17
		"""
		BigWorld.setGraphicsSetting("BLOOM_FILTER", True)
		BigWorld.switchScreenBlur(-1)


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addResistHiddenRoot(self, pyRoot):
		"""添加清屏时忽略的窗口"""
		if pyRoot not in self.__pyRootsResistHidden:
			self.__pyRootsResistHidden.append(pyRoot)

	def removeResistHiddenRoot(self, pyRoot):
		"""添加清屏时忽略的窗口"""
		if pyRoot in self.__pyRootsResistHidden:
			self.__pyRootsResistHidden.remove(pyRoot)

	def isResistHiddenRoot(self, pyRoot):
		"""是否是清屏时忽略的窗口"""
		return pyRoot in self.__pyRootsResistHidden

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEvent( self, eventName, *args ) :
		if eventName in self.__roleMoveTriggers :
			self.__roleMoveTriggers[eventName]( *args )
		if eventName in self.__entityFocusTriggers :
			self.__entityFocusTriggers[eventName]( *args )
		if eventName in self.__attackTriggers :
			self.__attackTriggers[eventName]( *args )
		if eventName in self.__pickupTriggers :
			self.__pickupTriggers[eventName]( *args )
		if eventName in self.__scenarioTriggers :
			self.__scenarioTriggers[eventName]( *args )

	# -------------------------------------------------
	def onEnterWorld( self ) :
		self.__rolePos = Math.Vector3( BigWorld.player().position )
		BigWorld.callback( 0.2, Functor( pixieHelper.triggerTopic, 101 ) )
		rds.shortcutMgr.setHandler( "UI_TOGGLE_ALL_UIS", self.__toggleAllRootsByShortCut )

#		if uiopHelper.hasTips( 0x0001 ) :						# 注册角色移动操作提示事件
#			self.__registerRoleMoveEvents()
#		if uiopHelper.hasTips( self.__entityFocusTipID ) :		# 注册选中目标操作提示事件
			#self.__registerEntityFocusEvents()					# 因为提示跟着鼠标移动，感觉别扭，策划要求取消该提示（2010.05.05）
#			pass
#		if uiopHelper.hasTips( self.__attackTipID ) :			# 注册攻击目标操作提示事件
#			self.__registerAttackEvents()
#		if uiopHelper.hasTips( self.__pickupTipID ) :			# 注册拾取操作提示事件
#			self.__registerPickupEvents()

	def onLeaveWorld( self ) :
		self.__hideWalkGuider()
		self.__hideEntityGetFocusTips()
		self.__hidePickupTips()
		self.__isEmptyScreen = False
		if self.__rtScenaio :
			self.__rtScenaio.dispose()
		if self.__rtScenaio2 :
			self.__rtScenaio2.dispose()
		if self.__rtScenaio3 :
			self.__rtScenaio3.dispose()

	def isEmptyScreen( self ):
		return self.__isEmptyScreen

# --------------------------------------------------------------------
# 角色移动提示界面
# --------------------------------------------------------------------
class WalkGuider( RootGUI ) :
	__cc_path = "guis/screenviewer/walkguider/guider.gui"
	__cc_fader = GUI.AlphaShader()
	__cc_fader.speed = 6
	__cg_flashCBID = 0

	def __init__( self, direct, text ) :
		gui = GUI.load( self.__cc_path )
		gui.bg.addShader( self.__cc_fader )
		RootGUI.__init__( self, gui )
		self.posZSegment = ZSegs.L2
		self.movable_ = False
		self.activable_ = False
		self.hitable_ = False
		self.escHide_ = False
		self.focus = False
		self.addToMgr()

		self.__pyRich = CSRichText( gui.rtTips )
		self.__pyRich.autoNewline = False
		self.__pyRich.widthAdapt = True
		edgeSpace = 4
		if direct == "L" :
			gui.bg.mapping = util.ccwRotateMapping90( gui.bg.mapping )
			gui.size = gui.bg.size = gui.size[1], gui.size[0]
			self.__pyRich.align = "R"
			self.__pyRich.text = text
			self.__pyRich.middle = self.height * 0.5
			self.__pyRich.right = gui.width - edgeSpace
		elif direct == "R" :
			gui.bg.mapping = util.cwRotateMapping90( gui.bg.mapping )
			gui.size = gui.bg.size = gui.size[1], gui.size[0]
			self.__pyRich.align = "L"
			self.__pyRich.text = text
			self.__pyRich.middle = self.height * 0.5
			self.__pyRich.left = edgeSpace
		elif direct == "T" :
			self.__pyRich.align = "C"
			self.__pyRich.text = text
			self.__pyRich.center = self.width * 0.5
			self.__pyRich.bottom = self.height - edgeSpace
		elif direct == "B" :
			gui.bg.mapping = util.cwRotateMapping180( gui.bg.mapping )
			self.__pyRich.align = "C"
			self.__pyRich.text = text
			self.__pyRich.center = self.width * 0.5
			self.__pyRich.top = edgeSpace
		self.show()

	def __del__( self ) :
		if Debug.output_del_ScreenViewerWaklGuider :
			INFO_MSG( str( self ) )
		RootGUI.__del__( self )

	# -------------------------------------------------
	# public
	# -------------------------------------------------
	def isMouseHit( self ) :
		"""
		返回 False，使得鼠标可以透过
		"""
		return False

	# --------------------------------------
	@classmethod
	def flash( SELF ) :
		"""
		闪烁
		"""
		if SELF.__cc_fader.currentAlpha >= 1.0 :
			SELF.__cc_fader.value = 0.2
		elif SELF.__cc_fader.currentAlpha <= 0.2 :
			SELF.__cc_fader.value = 1.0
		BigWorld.cancelCallback( SELF.__cg_flashCBID )
		SELF.__cg_flashCBID = BigWorld.callback( 0.1, SELF.flash )

	@classmethod
	def unflash( SELF ) :
		BigWorld.cancelCallback( SELF.__cg_flashCBID )


class ScreenFader( RootGUI ) :
	"""屏幕alpha衰减器"""
	def __init__( self ) :
		gui = GUI.load( "guis/screenviewer/screenfader/fader.gui" )
		RootGUI.__init__( self, gui )
		self.setToDefault()
		self.movable_ = False
		self.escHide_ = False
		self.posZSegment = ZSegs.L1
		self.__fade_cbid = 0
		self.addToMgr()
		self.__layout()
		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

	def __layout( self ) :
		self.size = BigWorld.screenSize()
		self.pos = 0, 0

	def __onResolutionChanged( self, preRes ) :
		""""""
		self.__layout()

	def fadein( self ) :
		"""显现"""
		BigWorld.cancelCallback( self.__fade_cbid )
		self.show()
		self.gui.fader.value = 1

	def fadeout( self ) :
		"""渐隐"""
		self.gui.fader.value = 0
		self.__fade_cbid = BigWorld.callback( self.gui.fader.speed, self.hide )

	def onEvent( self, evtMacro, *args ) :
		"""事件触发"""
		self.__onResolutionChanged( *args )

	@property
	def fadeSpeed( self ) :
		return self.gui.fader.speed
# --------------------------------------------------------------------
# 血量少时,屏幕闪烁危险警告
# --------------------------------------------------------------------
class DangerWarning( RootGUI ):
	def __init__( self ) :
		gui = GUI.load( "guis/screenviewer/screenfader/danger.gui" )
		RootGUI.__init__( self, gui )
		self.setToDefault()
		self.movable_ = False
		self.escHide_ = False
		self.focus = False
		self.crossFocus = False
		self.moveFocus = False
		self.activable_ = False
		self.hitable_ = False
		self.posZSegment = ZSegs.L1
		self.__fade_cbid = 0

		self.addToMgr()
		self.__layout()
		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

	def __layout( self ) :
		self.size = BigWorld.screenSize()
		self.pos = 0, 0

	def __onResolutionChanged( self, preRes ) :
		""""""
		self.__layout()

	def fadein( self ) :
		"""显现"""
		BigWorld.cancelCallback( self.__fade_cbid )
		self.show()
		self.gui.fader.value = 1
		self.flicker()

	def flicker( self ) :
		"""闪烁"""
		#显示
		if self.gui.fader.alpha == 0:
			self.gui.fader.speed = 0.25
			self.gui.fader.alpha = 1
			self.temp = True
		#隐藏
		elif self.gui.fader.alpha == 1:
			self.gui.fader.speed = 1
			self.gui.fader.alpha = 0
		BigWorld.callback( 1, self.flicker )

	def fadeout( self ) :
		"""渐隐"""
		self.gui.fader.value = 0
		self.__fade_cbid = BigWorld.callback( self.gui.fader.speed, self.hide )

	def onEvent( self, evtMacro, *args ) :
		"""事件触发"""
		self.__onResolutionChanged( *args )

	@property
	def fadeSpeed( self ) :
		return self.gui.fader.speed

class ChangeUIEffect( RootGUI ):
	def __init__( self ):
		gui = GUI.load( "guis/screenviewer/screenfader/changeUIEffect.gui" )
		RootGUI.__init__( self, gui )
		self.setToDefault()
		self.movable_ = False
		self.escHide_ = False
		self.focus = False
		self.crossFocus = False
		self.moveFocus = False
		self.activable_ = False
		self.hitable_ = False
		self.posZSegment = ZSegs.L1

		self.addToMgr()
		self.__layout()
		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

	def __layout( self ) :
		self.size = BigWorld.screenSize()
		self.pos = 0, 0

	def __onResolutionChanged( self, preRes ) :
		""""""
		self.__layout()

	def onEvent( self, evtMacro, *args ) :
		"""事件触发"""
		self.__onResolutionChanged( *args )


# --------------------------------------------------------------------
# 剧情提示的 RichText
# --------------------------------------------------------------------
class RTScenario( RootGUI, CSRichText ) :
	def __init__( self ) :
		CSRichText.__init__( self )
		gui = CSRichText.getGui( self )
		RootGUI.__init__( self, gui )
		self.posZSegment = ZSegs.L4
		self.movable_ = False
		self.activable_ = False
		self.hitable_ = False
		self.escHide_ = False
		self.focus = False
		self.addToMgr()

		self.autoNewline = False
		self.widthAdapt = True
		self.align = "C"

		self.__cbids = []

		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

		# 添加清屏例外窗口
		ScreenViewer().addResistHiddenRoot(self)

	def dispose( self ) :
		self.__clear()
		ECenter.unregisterEvent( "EVT_ON_RESOLUTION_CHANGED", self )
		RootGUI.dispose( self )
		CSRichText.dispose( self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __lineByLineShow( self, fader ) :
		"""
		渐显文本行
		"""
		fader.value = 1

	def __clear( self ) :
		"""
		清除当前所有提示文本
		"""
		for cbid in self.__cbids :
			BigWorld.cancelCallback( cbid )
		self.clear()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		RootGUI.generateEvents_( self )
		CSRichText.generateEvents_( self )

	def locate_( self ) :
		"""
		摆放显示位置
		"""
		self.r_center = 0
		self.r_middle = 0.3
		if self.top < 0 :
			self.r_top = 0.8


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, preReso ) :
		"""
		屏幕分辨率改变时被调用
		"""
		self.locate_()

	# -------------------------------------------------
	def show( self, text, showTime, hideTime, callback ) :
		self.__clear()
		self.text = text
		self.locate_()

		delayTime = 0
		for idx, elemInfo in enumerate( self.lineInfos_ ) :
			fader = GUI.AlphaShader()							# 渐显 Shader
			fader.value = 0
			fader.speed = 1.5
			fader.reset()
			for pyElem in elemInfo[1] :							# 给行中的每个元素添加一个渐显 shader
				pyElem.gui.addShader( fader )
			func = Functor( self.__lineByLineShow, fader )
			cbid = BigWorld.callback( delayTime, func )			# 启用渐显 callback
			self.__cbids.append( cbid )
			delayTime += showTime
		hideTime += delayTime
		func = Functor( self.hide, callback )
		cbid = BigWorld.callback( hideTime, func )				# 延时隐藏
		self.__cbids.append( cbid )
		RootGUI.show( self )

	def hide( self, callback ) :
		RootGUI.hide( self )
		self.dispose()
		callback()


class RTScenario2( RTScenario ) :


	def __init__( self ) :
		RTScenario.__init__( self )
		self.texture = "guis/empty.dds"
		self.color = ( 20, 20, 20, 250 )
		self.align = "L"


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def locate_( self ) :
		screenSIze = BigWorld.screenSize()
		self.gui.height = 75
		self.gui.width = screenSIze[0]
		self.bottom = screenSIze[1]
		self.left = 0


class RTScenario3( RootGUI, CSRichText ) :
	"""
	字幕播放text
	add by wuxo 2011-9-6
	"""
	def __init__( self,color = (20,20,20,255) ) :
		CSRichText.__init__( self )
		gui = CSRichText.getGui( self )
		RootGUI.__init__( self, gui )
		self.posZSegment = ZSegs.L4

		win = GUI.Window("guis/empty.dds")
		self.parentUI = PyGUI(win)
		self.parentUI.setToDefault()
		self.parentUI.color = color

		self.movable_ = False
		self.activable_ = False
		self.hitable_ = False
		self.escHide_ = False
		self.focus = False
		self.addToMgr()

		self.autoNewline = False
		self.widthAdapt = True
		self.align = "C"

		self.__cbids = []

		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

		# 添加清屏例外窗口
		ScreenViewer().addResistHiddenRoot(self)

	def dispose( self ) :
		self.__clear()
		ECenter.unregisterEvent( "EVT_ON_RESOLUTION_CHANGED", self )
		RootGUI.dispose( self )
		CSRichText.dispose( self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __lineByLineShow( self, fader ) :
		"""
		渐显文本行
		"""
		fader.value = 1

	def __clear( self ) :
		"""
		清除当前所有提示文本
		"""
		for cbid in self.__cbids :
			BigWorld.cancelCallback( cbid )
		self.clear()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		RootGUI.generateEvents_( self )
		CSRichText.generateEvents_( self )

	def locate_( self ) :
		"""
		摆放显示位置
		"""
		self.parentUI.size = BigWorld.screenSize()
		self.parentUI.gui.position = (-1,1,0.5)
		self.posZ = 1

		self.r_center = 0
		self.r_middle = 0.3
		if self.top < 0 :
			self.r_top = 0.8


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, preReso ) :
		"""
		屏幕分辨率改变时被调用
		"""
		self.locate_()

	# -------------------------------------------------
	def show( self, text, showTimes, hideTime, callback) :
		"""
		字幕播放,每行播放时间由配置表决定
		"""
		GUI.addRoot(self.parentUI.gui)

		self.__clear()
		self.text = text
		self.locate_()

		delayTime = 0
		count = 0
		for idx, elemInfo in enumerate( self.lineInfos_ ) :
			fader = GUI.AlphaShader()							# 渐显 Shader
			fader.value = 0
			fader.speed = 1.5
			fader.reset()
			for pyElem in elemInfo[1] :							# 给行中的每个元素添加一个渐显 shader
				pyElem.gui.addShader( fader )
			func = Functor( self.__lineByLineShow, fader )
			cbid = BigWorld.callback( delayTime, func )			# 启用渐显 callback
			self.__cbids.append( cbid )
			if len(showTimes) > count:		#根据配置表计算每行显示时间
				delayTime += showTimes[count]
			else:
				delayTime += 3   #默认为3秒
			count += 1
		hideTime += delayTime
		func = Functor( self.hide, callback )
		cbid = BigWorld.callback( hideTime, func )				# 延时隐藏
		self.__cbids.append( cbid )
		RootGUI.show( self )

	def hide( self, callback ) :
		GUI.delRoot( self.parentUI.gui )
		RootGUI.hide( self )
		self.dispose()
		self.parentUI.dispose()
		del self.parentUI
		callback()


class RTScenario4( RootGUI, CSRichText ):
	def __init__( self ) :
		CSRichText.__init__( self )
		gui = CSRichText.getGui( self )
		RootGUI.__init__( self, gui )
		self.posZSegment = ZSegs.L4
		self.movable_ = False
		self.activable_ = False
		self.hitable_ = False
		self.escHide_ = False
		self.focus = False
		self.addToMgr()

		self.autoNewline = True
		self.maxWidth = BigWorld.screenWidth()
		self.widthAdapt = False
		self.align = "L"
		self.__cbids = []

		win = GUI.Window("guis/empty.dds")
		self.parentUI = PyGUI(win)
		self.parentUI.setToDefault()
		#self.parentUI.align = "L"
		self.parentUI.color = ( 20, 20, 20, 255 )
		self.realheight = 0.0
		self.alreadyAdd = False

		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

		# 添加清屏例外窗口
		ScreenViewer().addResistHiddenRoot(self)

	def dispose( self ) :
		self.__clear()
		ECenter.unregisterEvent( "EVT_ON_RESOLUTION_CHANGED", self )
		RootGUI.dispose( self )
		CSRichText.dispose( self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __lineByLineShow( self, fader, num ) :
		"""
		渐显文本行
		"""
		if self.alreadyAdd and num ==1:
			self.bottom += self.realheight/2
			self.alreadyAdd = False
		if not self.alreadyAdd and num == 2:
			self.bottom -= self.realheight/2
			self.alreadyAdd = True
		fader.value = 1

	def __clear( self ) :
		"""
		清除当前所有提示文本
		"""
		for cbid in self.__cbids :
			BigWorld.cancelCallback( cbid )
		self.clear()

	def __locate( self ):
		screenSIze = BigWorld.screenSize()
		self.parentUI.size = screenSIze
		self.parentUI.gui.position = ( -1, -1 + 2*100/screenSIze[1], 0.5 )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		RootGUI.generateEvents_( self )
		CSRichText.generateEvents_( self )

	def onEvent( self, macroName, preReso ) :
		"""
		屏幕分辨率改变时被调用
		"""
		if "@B" in self.text:
			self.__locate()
		else:
			self.maxWidth = BigWorld.screenWidth()
			self.locate_()

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def locate_( self ) :
		screenSIze = BigWorld.screenSize()
		self.gui.height = 800
		self.gui.width = screenSIze[0]
		self.bottom = screenSIze[1] + 800 - 60
		if len( self.lineInfos_ ) > 1 and not "@B" in self.text:
			self.bottom -= self.realheight/2
		self.left = 0

		self.parentUI.size = screenSIze
		self.parentUI.gui.position = (-1,-1 + 2*100/screenSIze[1] ,0.5)
		self.posZ = 1

	def show( self, text, showTimes, hideTime, callback) :
		"""
		字幕播放,每行播放时间由配置表决定
		当一行字很多时,大分辨率下可以显示完整，但是小分辨率显示不完整时
		小分辨率屏幕使用2行来显示完整
		RichText控件在初始化时，不会设置字体大小、行高、行宽等信息
		一行结束符号用E表示
		"""
		GUI.addRoot(self.parentUI.gui)
		self.__clear()
		text = text.replace("@B","E@B")
		self.text = text
		self.locate_()

		displayTime =0				# 行显示时间
		delayTime = 0				# 行渐隐时间
		count = 0
		splitFalg = False			# 已经被拆分标记
		preCount = 0
		for idx, elemInfo in enumerate( self.lineInfos_ ) :
			fader = GUI.AlphaShader()							# 渐显 Shader
			fader.value = 0
			fader.speed = 1.5
			fader.reset()
			num = 1
			for pyElem in elemInfo[1] :							# 给行中的每个元素添加一个渐显 shader
				pyElem.gui.addShader( fader )
				self.realheight = pyElem.height
				if not pyElem.text.endswith("E"):		# 被拆分的一行的前半段，用E做结束判断
					num = 2
					splitFalg = True
				else:
					pyElem.text = pyElem.text.rstrip("E")
					if splitFalg:							# 被拆分的一行的后半段
						num = 0
					splitFalg = 0
			func = Functor( self.__lineByLineShow, fader, num )
			cbid = BigWorld.callback( displayTime, func )			# 启用渐显 callback
			self.__cbids.append( cbid )
			if len(showTimes) > preCount:		#根据配置表计算每行显示时间
				delayTime = displayTime + showTimes[preCount]
			else:
				delayTime =  displayTime + 3    #默认为3秒
			if num >1:
				x=0
			else:
				x=1
				displayTime = delayTime
			fun = Functor( self.scroll, count, num )
			cbid = BigWorld.callback( delayTime, fun )
			self.__cbids.append( cbid )
			count += 1
			preCount += x
		hideTime += delayTime
		func = Functor( self.hide, callback )
		cbid = BigWorld.callback( hideTime, func )				# 延时隐藏
		self.__cbids.append( cbid )
		RootGUI.show( self )

	def scroll( self, count, num = 1 ):
		pyElems = []
		if len( self.lineInfos_ ) > count:
			text, pyElems = self.lineInfos_[count]
		for i in pyElems:
			i.visible = False
		self.bottom -= num * ( self.realheight + self.spacing )

	def hide( self, callback ) :
		callback()
		GUI.delRoot( self.parentUI.gui )
		RootGUI.hide( self )
		self.dispose()
		self.parentUI.dispose()
		del self.parentUI

class RTScenario5( RootGUI, CSRichText ):
	"""
	用于和RTScenario4构成电影夹屏
	"""
	def __init__( self ) :
		CSRichText.__init__( self )
		gui = CSRichText.getGui( self )
		RootGUI.__init__( self, gui )
		self.posZSegment = ZSegs.L4
		self.movable_ = False
		self.activable_ = False
		self.hitable_ = False
		self.escHide_ = False
		self.focus = False
		self.addToMgr()

		self.autoNewline = False
		self.widthAdapt = True
		self.align = "L"
		self.__cbids = []

		win = GUI.Window("guis/empty.dds")
		self.parentUI = PyGUI(win)
		self.parentUI.setToDefault()
		#self.parentUI.align = "L"
		self.parentUI.color = ( 20, 20, 20, 255 )

		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

		# 添加清屏例外窗口
		ScreenViewer().addResistHiddenRoot(self)

	def dispose( self ) :
		self.__clear()
		ECenter.unregisterEvent( "EVT_ON_RESOLUTION_CHANGED", self )
		RootGUI.dispose( self )
		CSRichText.dispose( self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __lineByLineShow( self, fader ) :
		"""
		渐显文本行
		"""
		fader.value = 1

	def __clear( self ) :
		"""
		清除当前所有提示文本
		"""
		for cbid in self.__cbids :
			BigWorld.cancelCallback( cbid )
		self.clear()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		RootGUI.generateEvents_( self )
		CSRichText.generateEvents_( self )

	def onEvent( self, macroName, preReso ) :
		"""
		屏幕分辨率改变时被调用
		"""
		self.locate_()
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def locate_( self ) :
		screenSIze = BigWorld.screenSize()
		self.gui.height = 75
		self.gui.width = screenSIze[0]
		self.bottom = 75
		self.left = 0

		self.parentUI.size = screenSIze
		self.parentUI.gui.position = (-1,  3 - 2*100 / screenSIze[1]  ,0.5)
		self.posZ = 1

	def __lineByLineShow( self, fader ) :
		"""
		渐显文本行
		"""
		fader.value = 1

	def show( self ) :
		"""
		字幕播放,每行播放时间由配置表决定
		"""
		GUI.addRoot(self.parentUI.gui)
		self.__clear()
		self.locate_()
		RootGUI.show( self )


	def hide( self ) :
		GUI.delRoot( self.parentUI.gui )
		RootGUI.hide( self )
		self.dispose()
		self.parentUI.dispose()
		del self.parentUI

class RTScenario6( RootGUI, CSRichText ):
	"""
	用于ESC按键提示
	"""
	def __init__( self ) :
		CSRichText.__init__( self )
		gui = CSRichText.getGui( self )
		RootGUI.__init__( self, gui )
		self.posZSegment = ZSegs.L1
		self.movable_ = False
		self.activable_ = False
		self.hitable_ = False
		self.escHide_ = False
		self.focus = False
		self.fontSize = 18
		self.addToMgr()

		self.autoNewline = False
		self.widthAdapt = True
		self.align = "L"

		#win = GUI.Window("guis/empty.dds")
		#self.parentUI = PyGUI(win)
		#self.parentUI.setToDefault()
		#self.parentUI.color = ( 0, 0, 0, 0 )
		self.__clear()
		self.text = lbDatas.CAMERA_ESC
		self.locate_()
		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

		# 添加清屏例外窗口
		ScreenViewer().addResistHiddenRoot(self)

	def dispose( self ) :
		self.__clear()
		ECenter.unregisterEvent( "EVT_ON_RESOLUTION_CHANGED", self )
		RootGUI.dispose( self )
		CSRichText.dispose( self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __lineByLineShow( self, fader ) :
		"""
		渐显文本行
		"""
		fader.value = 1

	def __clear( self ) :
		"""
		清除当前所有提示文本
		"""
		self.clear()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		RootGUI.generateEvents_( self )
		CSRichText.generateEvents_( self )

	def onEvent( self, macroName, preReso ) :
		"""
		屏幕分辨率改变时被调用
		"""
		self.locate_()
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def locate_( self ) :
		screenSIze = BigWorld.screenSize()
		self.gui.height = 40.0
		self.gui.width = 200.0
		self.bottom = 40.0
		self.left = screenSIze[0]/2.0 - 200/2.0

		#self.parentUI.size = ( 40.0, 200.0 )
		#self.parentUI.gui.position = (-200.0/screenSIze[0],  -40.0 / screenSIze[1]  , 1 )
		#self.posZ = 1

	def show( self ) :
		"""
		显示
		"""
		#GUI.addRoot(self.parentUI.gui)
		RootGUI.show( self )


	def hide( self ) :
		#GUI.delRoot( self.parentUI.gui )
		RootGUI.hide( self )
		#self.dispose()
		#self.parentUI.dispose()
		#del self.parentUI




class UIOSentinel( Singleton ) :
	"""
	用户界面提示中转机制
	"""
	def __init__( self ) :
		self.__consigner = {}
		ECenter.registerEvent( "EVT_ON_IMPLEMENT_UI_OPERATION", self )

	def attach( self, uioKey, handler ) :
		"""
		"""
		handlers = self.__consigner.get( uioKey )
		if handlers is not None :
			handlers.append( handler )
		else :
			self.__consigner[uioKey] = [ handler ]

	def detach( self, uioKey, handler ) :
		"""
		"""
		handlers = self.__consigner.get( uioKey )
		if handlers is None : return
		if handler in handlers :
			handlers.remove( handler )
		if len( handlers ) == 0 :
			del self.__consigner[ uioKey ]

	def implement( self, uioKey ) :
		"""
		"""
		handlers = self.__consigner.get( uioKey )
		if handlers is None : return
		for handler in handlers :
			handler( uioKey )
		print "UI operations( ids: %s ) commits!" % str( uioKey )

	def onEvent( self, evtMacro, *args ) :
		"""
		"""
		if evtMacro == "EVT_ON_IMPLEMENT_UI_OPERATION" :
			self.implement( *args )
