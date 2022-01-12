# -*- coding: gb18030 -*-
#
# $Id: BigMap.py,v 1.28 2008-08-27 09:04:26 huangyongwei Exp $

"""
implement full map class

2008.01.03 : wirten by huangyongwei
"""

import csstatus
from event.Timer import Timer
from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.FlexExWindow import HVFlexExWindow
from guis.common.FrameEx import HVFrameEx
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from guis.controls.ODComboBox import ODComboBox
from guis.controls.ProgressBar import HProgressBar
from MapPanel import MapPanel
from NPCLister import NPCLister
from Helper import courseHelper
from LabelGather import labelGather

from bwdebug import *


class BigMap( HVFlexExWindow ) :
	def __init__( self ) :
		wnd = GUI.load( "guis/general/bigmap/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		HVFlexExWindow.__init__( self, wnd )
		self.h_dockStyle = "HFILL"									# 水平方向上随分辨率改变而改变大小
		self.v_dockStyle = "VFILL"									# 垂直方向上随分辨率改变而改变大小
		self.foacus = False
		self.moveFocus = False										# 不允许移动
		self.posZSegment = ZSegs.L3									# always on top
		self.activable_ = True										# 可以被激活
		self.escHide_ 		 = True									# 可以按 esc 键隐藏
		self.__areaList = []											# 又有的地区 Combobx 选项
		self.__ignWhAreas = {}										# 被忽略显示的全地图区域,key:(spaceLabel,isSky)
		self.__currArea = None										# 记录当前所在地区
		self.__updateTimer = Timer( self.__update )					# 实时更新的 timer
		self.__updateTimer.interval = 0.05
		

		self.__initialize( wnd )

		self.__triggers = {}
		self.__registerTriggers()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		self.__pyHPBar = HProgressBar( wnd.hpBg.bar )							# 血条

		self.__pyTopBar = PyGUI( wnd.topBar )									# 放上部按钮的板面
		self.__pyTopBar.h_dockStyle = "RIGHT"
		self.__pyDownBar = PyGUI( wnd.downBar )									# 放下部坐标的板面
		self.__pyDownBar.h_dockStyle = "CENTER"
		self.__pyDownBar.v_dockStyle = "BOTTOM"
		
		self.__pyBgFrame = HVFrameEx( wnd.bgFrame )
		self.__pyBgFrame.h_dockStyle = "HFILL"
		self.__pyBgFrame.v_dockStyle = "VFILL"		

		self.__pyMapPanel = MapPanel( wnd.mapPanel )							# 显示地图的板面
		self.__pyMapPanel.h_dockStyle = "HFILL"
		self.__pyMapPanel.v_dockStyle = "VFILL"
		self.__pyMap = self.__pyMapPanel.pyMap
		self.__pyMap.onMouseMove.bind( self.__onMapMouseMove )
		self.__pyMap.onWorldAreaClick.bind( self.__onWorldAreaClick )
		
		self.__pySTTips = StaticText( wnd.stTips )
		self.__pySTTips.text = ''

		self.__pyCBAreas = ODComboBox( wnd.topBar.cbAreas )						# 区域列表组合框
		self.__pyCBAreas.viewCount = 16
		self.__pyCBAreas.onItemSelectChanged.bind( self.__onAreaSelected )
		self.__pyCBAreas.autoSelect = False
		self.__loadAllAreas()

		self.__pyBtnToggleNP = HButtonEx( wnd.topBar.btnToggleNPC )				# 显示/隐藏所有 NPC
		self.__pyBtnToggleNP.text = labelGather.getText( "BigMap:main", "btnHideNPC" )
		self.__pyBtnToggleNP.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnToggleNP.onLClick.bind( self.__toggleNPCs )

		self.__pySearchNPCBtn = HButtonEx( wnd.topBar.btnSearchNPC )				# 搜索 NPC
		self.__pySearchNPCBtn.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pySearchNPCBtn.onLClick.bind( self.__showNPCLister )

		self.__pyShowAllMapsBtn = HButtonEx( wnd.topBar.btnWorld )					# 显示世界地图按钮
		self.__pyShowAllMapsBtn.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyShowAllMapsBtn.onLClick.bind( self.__showWholeArea )

		self.__pySTPSeat = StaticText( wnd.downBar.stPSeat )					# 显示玩家所在地点
		self.__pySTPPos = StaticText( wnd.downBar.stPPos )						# 显示玩家当前坐标
		self.__pySTMPos = StaticText( wnd.downBar.stMPos )						# 显示鼠标当前坐标

		self.__pyScaleBtnsPanel = PyGUI( wnd.mapPanel.scaleBtnsPanel )			# 缩放按钮的板面
		self.__pyScaleBtnsPanel.h_dockStyle = "RIGHT"
		self.__pyScaleBtnsPanel.v_dockStyle = "MIDDLE"
		self.__pyPlusBtn = Button( wnd.mapPanel.scaleBtnsPanel.plusBtn )		# 放大按钮
		self.__pyPlusBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyPlusBtn.onLClick.bind( self.__pyMapPanel.orginMapSize )
		self.__pyMinusBtn = Button( wnd.mapPanel.scaleBtnsPanel.minusBtn )		# 缩小按钮
		self.__pyMinusBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyMinusBtn.onLClick.bind( self.__pyMapPanel.adaptMapSize )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pySearchNPCBtn, "BigMap:main", "btnSearchNPC" )
		labelGather.setPyBgLabel( self.__pyShowAllMapsBtn, "BigMap:main", "btnWorldMap" )
		labelGather.setPyLabel( self.__pySTTips, "BigMap:main", "stTips" )
		labelGather.setPyLabel( self.__pySTPSeat, "BigMap:main", "stPSeat" )
		labelGather.setLabel( wnd.downBar.stMSeat, "BigMap:main", "stMSeat" )
		labelGather.setLabel( wnd.topBar.lbArea, "BigMap:main", "stArea" )
	


	def __loadAllAreas( self ) :
		"""
		加载所有区域选项
		"""
		areas = rds.mapMgr.getAreas()
		for idx, area in enumerate( areas ) :
			if area.ignore:
				wholeArea = area.wholeArea
				isSkyArea = wholeArea.isSkyArea
				if wholeArea.ignore:
					spaceLabel = wholeArea.spaceLabel
					if not ( spaceLabel, isSkyArea ) in self.__ignWhAreas:
						self.__ignWhAreas[( spaceLabel, isSkyArea )] = wholeArea
				continue					# 忽略该区域
			self.__pyCBAreas.addItem( area.fullName )
			self.__areaList.append( area )

	# -------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_BIGMAP"] = self.__toggleVisible
		self.__triggers["EVT_ON_ROLE_ENTER_AREA"] = self.__onEnterArea
		self.__triggers["EVT_ON_ROLE_HP_CHANGED"] = self.__onUpdateHP
		for trigger in self.__triggers :
			ECenter.registerEvent( trigger, self )

	def __toggleVisible( self ) :
		"""
		显示/隐藏大地图
		"""
		self.visible = not self.visible
		return True

	# -------------------------------------------------
	def __resetArea( self, area ) :
		"""
		设置显示区域
		"""
		self.__pyMapPanel.setArea( area )
		player = BigWorld.player()
		currArea = player.getCurrArea()
		if currArea == area or area == currArea.wholeArea :					# 角色在设置的区域上
			point = area.worldPoint2TexturePoint( player.position )
			self.__pyMapPanel.scrollToPoint( point )
		elif area.isWholeArea() or area.hasTexture() :
			self.__pyMapPanel.scrollToPoint( ( 0, 0 ) )
		else :
			worldBound = area.worldBound
			x = worldBound.x + worldBound.width * 0.5
			y = worldBound.y + worldBound.height / 2
			point = area.wholeArea.worldPoint2TexturePoint( ( x, y ) )
			self.__pyMapPanel.scrollToPoint( point )

	def __selectCurrArea( self ) :
		"""
		打开地图或更换区域时，选中当前区域
		"""
		if self.__currArea in self.__areaList :							# 如果列表中存在当前区域
			index = self.__areaList.index( self.__currArea )
			self.__pyCBAreas.selIndex = index							# 则选中当前区域
			return
		wholeArea = self.__currArea.wholeArea							# 选中区域的父区域
		if wholeArea in self.__areaList :
			index = self.__areaList.index( wholeArea )					# 父区域索引
			if self.__currArea.hasTexture() :							# 如果当前区域有贴图
				self.__pyCBAreas.onItemSelectChanged.shield()
				self.__pyCBAreas.selIndex = index						# 选中父区域，但不触发选图
				self.__pyCBAreas.onItemSelectChanged.unshield()
				self.__resetArea( self.__currArea )						# 而是显示自己的区域地图
			elif self.__pyCBAreas.selIndex == index :					# 如果当前区域没有贴图( 并且已经选中了当前地图的所属父区域 )
				self.__resetArea( wholeArea )							# 则设置地图为父区域地图
			else :
				self.__pyCBAreas.selIndex = index						# 否则，选中父区域的贴图

	def __update( self ) :
		"""
		更新地图
		"""
		player = BigWorld.player()
		self.__pyMap.update( player )
		pos = player.position
		self.__pySTPPos.text = "%d:%d" % ( pos.x, pos.z )

	# -------------------------------------------------
	def __onEnterArea( self, newArea ) :
		"""
		当角色进入某区域时被触发（newArea 不会为 None）
		"""
		self.__setIgnoreArea( newArea )
		self.__currArea = newArea
		# "你当前的位置是：%s"
		name = labelGather.getText( "BigMap:main", "stPSeat" ) % self.__currArea.spaceName
		if self.__currArea.isSubArea() :
			name = name + ", %s" % ( self.__currArea.name )
		self.__pySTPSeat.text = name
		self.__pyMap.onEnterArea( self.__currArea )
		if self.visible :											# 如果地图可见
			self.__selectCurrArea()									# 则选中当前区域（因为打开地图时，还会触发一次）

	def __onUpdateHP( self, entityID, hp, hpMax ) :
		"""
		更新血条
		"""
		if BigWorld.player().id != entityID:
			return
		if hpMax <= 0 :
			self.__pyHPBar.value = 0
		else :
			self.__pyHPBar.value = float( hp ) / hpMax
	
	def __setIgnoreArea( self, newArea ):
		if self.__currArea:				#原来的区域是忽略的，则从下拉框中删除
			wholeArea = self.__currArea.wholeArea
			spaceLabel = wholeArea.spaceLabel
			isSkyArea = wholeArea.isSkyArea
			if ( spaceLabel, isSkyArea ) in self.__ignWhAreas:
				fullName = self.__currArea.fullName
				if fullName in self.__pyCBAreas.items:
					self.__pyCBAreas.removeItem( fullName )
					if wholeArea in self.__areaList:
						self.__areaList.remove( wholeArea )
		if newArea :					#新进入的区域是忽略的，则加进下拉列表
			wholeArea = newArea.wholeArea
			spaceLabel = wholeArea.spaceLabel
			isSkyArea = wholeArea.isSkyArea
			if ( spaceLabel, isSkyArea ) in self.__ignWhAreas:
				fullName = newArea.fullName
				if not fullName in self.__pyCBAreas.items:
					self.__pyCBAreas.addItem( fullName )
					if not wholeArea in self.__areaList:
						self.__areaList.append( wholeArea )
	# -------------------------------------------------
	def __onAreaSelected( self, index ) :
		"""
		当选择一个区域时被触发
		"""
		NPCLister.hide()
		if index >= 0 :
			area = self.__areaList[index]
			self.__resetArea( area )
		self.__pyMapPanel.adaptMapSize()

	def __toggleNPCs( self, pyBtn ) :
		"""
		显示/隐藏 NPC
		"""
		showNPCText = labelGather.getText( "BigMap:main", "btnShowNPC" )
		if pyBtn.text == showNPCText :
			pyBtn.text = labelGather.getText( "BigMap:main", "btnHideNPC" )
			self.__pyMap.showNPCs()
		else :
			pyBtn.text = showNPCText
			self.__pyMap.hideNPCs()

	def __showNPCLister( self ) :
		"""
		显示 NPC 搜索界面
		"""
		area = self.__pyMap.viewArea
		if area.isSubArea() :
			area = area.wholeArea
		NPCLister.show( self, area )

	def __showWholeArea( self ) :
		"""
		显示全地图（世界地图）
		"""
		self.__resetArea( rds.mapMgr.worldArea )
		self.__pyCBAreas.selIndex = -1
		self.__pyMapPanel.orginMapSize()

	# -------------------------------------------------
	def __onMapMouseMove( self, dx, dy ) :
		"""
		当鼠标在地图上移动时被触发
		"""
		self.__pySTMPos.text = "%d:%d" % tuple( self.__pyMap.getMouseInWorldPoint() )

	def __onWorldAreaClick( self, area ) :
		"""
		选择某个区域时被触发
		"""
		if area is None :
			# "该地图暂时没开放！"
			showMessage( 0x0201, "", MB_OK, pyOwner = self )
			return
		if area in self.__areaList :
			self.__pyCBAreas.selIndex = self.__areaList.index( area )
		else :
			self.__pyCBAreas.selIndex = -1
			self.__resetArea( area )
		self.__pyMapPanel.adaptMapSize()


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def afterStatusChanged( self, oldStatus, newStatus ) :
		"""
		当状态被改变时被调用
		"""
		if oldStatus == Define.GST_BACKTO_ROLESELECT_LOADING :
			self.hide()

	def onLeaveWorld( self ) :
		"""
		角色离开世界时被调用
		"""
		self.hide()
		self.__pyMap.onLeaveWorld()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self ) :
		"""
		显示窗口
		"""
		currArea = self.__currArea
		if currArea.texture == "" and \
			currArea.wholeArea.texture == "" :						# 如果该区域的地图不能查看，则直接返回
				# "你当前所在的区域不允许查看地图"
				showMessage( 0x0202, "", MB_OK, pyOwner = self )
				return
		self.__selectCurrArea()										# 打开地图时，显示当前区域
		player = BigWorld.player()
		self.__onUpdateHP( player.id, player.getHP(), player.getHPMax() )
		self.__updateTimer.start()
		self.__pyMapPanel.adaptMapSize()
		HVFlexExWindow.show( self )
		self.__pyMap.onWindowShowed()
		rds.worldCamHandler.disable()
		rds.helper.courseHelper.openWindow( "ditu_chuangkou" )
		showNPCText = labelGather.getText( "BigMap:main", "btnShowNPC" )	
		if self.__pyBtnToggleNP.text == showNPCText :
			self.__pyMap.hideNPCs()
		else :
			self.__pyMap.showNPCs()

	def hide( self ) :
		"""
		隐藏窗口
		"""
		HVFlexExWindow.hide( self )
		self.__pyMap.onWindowHidded()
		self.__updateTimer.stop()
		rds.worldCamHandler.enable()

	# -------------------------------------------------
	def showNPC( self, npc ) :
		"""
		将视域跳转到指定的 NPC 处
		"""
		selIndex = self.__pyCBAreas.selIndex
		if selIndex < 0 : return
		area = self.__areaList[selIndex]
		point = area.worldPoint2TexturePoint( npc.getPosition( self.__pyMap.viewArea.spaceLabel ) )
		self.__pyMapPanel.scrollToPoint( point )
		self.__pyMap.highlightNPC( npc )
