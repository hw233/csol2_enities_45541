# -*- coding: gb18030 -*-
#
# $Id: T_SoundSetter.py,v 1.5 2008-08-30 09:12:53 huangyongwei Exp $
#
"""
implement cameras, it moved from love3.py
2008/05/29: created by huangyongwei
"""

import inspect
import Language
from gbref import PyConfiger
from guis import *
from guis.common.Window import Window
from guis.controls.ListPanel import ListPanel
from guis.controls.ListItem import SingleColListItem
from guis.controls.TextBox import TextBox
from guis.controls.Button import Button
from guis.controls.CheckBox import CheckBox
from guis.controls.ContextMenu import ContextMenu
from guis.controls.ContextMenu import DefMenuItem
from guis.ExtraEvents import ControlEvent
from guis.UISounder import UISounder
from guis.UISounder import uiSounder
from guis.UISounder import SoundInfo
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from config.client.msgboxtexts import Datas as mbmsgs
from tools import toolMgr
from ITool import ITool

class SoundSetter( Window, ITool ) :
	__cc_event_names = {}											# 事件名称
	__cc_event_names["onLClick"]				= "左键点击"
	__cc_event_names["onRClick"]				= "右键点击"
	__cc_event_names["onLMouseDown"]			= "左键按下"
	__cc_event_names["onLMouseUp"]				= "左键提起"
	__cc_event_names["onRMouseDown"]			= "右键按下"
	__cc_event_names["onRMouseUp"]				= "右键提起"
	__cc_event_names["onLDBClick"]				= "左键双击"
	__cc_event_names["onAfterShowed"]			= "显示/打开之后"
	__cc_event_names["onAfterClosed"]			= "隐藏/关闭之后"
	__cc_event_names["onMouseEnter"]			= "鼠标进入"
	__cc_event_names["onMouseLeave"]			= "鼠标离开"
	__cc_event_names["onCheckChanged"]			= "选择改变时"
	__cc_event_names["onItemLClick"]			= "选项被左键点击时"
	__cc_event_names["onItemRClick"]			= "选项被右键点击时"
	__cc_event_names["onItemSelectChanged"]		= "选项的选择改变时"
	__cc_event_names["onDisable"]				= "禁用"
	__cc_event_names["onEnable"]				= "启用"
	__cc_event_names["onDragEnter"]				= "拖放进入"
	__cc_event_names["onDragLeave"]				= "拖放离开"
	__cc_event_names["onDragStart"]				= "开始拖放"
	__cc_event_names["onDragStop"]				= "停止拖放"
	__cc_event_names["onDrop"]					= "拖曳放下"
	__cc_event_names["onKeyDown"]				= "键盘按键按下"
	__cc_event_names["onKeyUp"]					= "键盘按键提起"
	__cc_event_names["onMouseMove"]				= "鼠标移动"
	__cc_event_names["onSelectChanged"]			= "被选中"
	__cc_event_names["onTabIn"]					= "获得焦点"
	__cc_event_names["onTabOut"]				= "失去焦点"
	__cc_event_names["onAfterPopUp"]			= "弹出"
	__cc_event_names["onAfterClose"]			= "关闭"
	__cc_event_names["onItemClick"]				= "选项被点击(左键)"
	__cc_event_names["onItemCheckChanged"]		= "选项的选择改变"
	__cc_event_names["onDropDown"]				= "弹出(打开)"
	__cc_event_names["onCollapsed"]				= "收起(关闭)"
	__cc_event_names["onTextChanged"]			= "文本改变"
	__cc_event_names["onTreeNodeLClick"]		= "左键点击树节点"
	__cc_event_names["onTreeNodeRClick"]		= "右键点击树节点"
	__cc_event_names["onTreeNodeSelected"]		= "树节点被选中"
	__cc_event_names["onTreeNodeDeselected"]	= "树节点取消选中"
	__cc_event_names["onTreeNodeExtended"]		= "树节点展开字节点"
	__cc_event_names["onTreeNodeCollapsed"]		= "树节点收起字节点"
	__cc_event_names["onTreeNodeAdded"]			= "添加了一个树节点"
	__cc_event_names["onTreeNodeRemoved"]		= "删除了一个树节点"
	__cc_event_names["onProgressChanged"]		= "进度改变"
	__cc_event_names["onComponentLClick"]		= "左键点击某个链接标签"
	__cc_event_names["onComponentRClick"]		= "右键点击某个链接标签"
	__cc_event_names["onComponentMouseEnter"]	= "鼠标进入某个链接标签"
	__cc_event_names["onComponentMouseLeave"]	= "鼠标离开某个链接标签"
	__cc_event_names["onScroll"]				= "滚动值改变"
	__cc_event_names["onScrollChanged"]			= "滚动值改变"
	__cc_event_names["onHScrollChanged"]		= "水平滚动值改变"
	__cc_event_names["onVScrollChanged"]		= "垂直滚动值改变"
	__cc_event_names["onTabPageSelectedChanged"]= "翻页改变"
	__cc_event_names["onSlide"]					= "滑动"

	__cc_common_events = []											# 常用事件
	__cc_common_events.append( "onLClick" )
	__cc_common_events.append( "onRClick" )
	__cc_common_events.append( "onLMouseDown" )
	__cc_common_events.append( "onRMouseDown" )
	__cc_common_events.append( "onLDBClick" )
	__cc_common_events.append( "onAfterShowed" )
	__cc_common_events.append( "onAfterClosed" )
	__cc_common_events.append( "onMouseEnter" )
	__cc_common_events.append( "onMouseLeave" )
	__cc_common_events.append( "onCheckChanged" )
	__cc_common_events.append( "onItemLClick" )
	__cc_common_events.append( "onItemSelectChanged" )
	__cc_common_events.append( "onDisable" )
	__cc_common_events.append( "onEnable" )
	__cc_common_events.append( "onAfterPopUp" )
	__cc_common_events.append( "onAfterClose" )
	__cc_common_events.append( "onItemClick" )
	__cc_common_events.append( "onItemCheckChanged" )
	__cc_common_events.append( "onDropDown" )
	__cc_common_events.append( "onCollapsed" )
	__cc_common_events.append( "onTreeNodeExtended" )
	__cc_common_events.append( "onTreeNodeCollapsed" )
	__cc_common_events.append( "onComponentLClick" )
	__cc_common_events.append( "onComponentMouseEnter" )
	__cc_common_events.append( "onComponentMouseLeave" )
	__cc_common_events.append( "onTabPageSelectedChanged" )

	__cc_forbend_events = []										# 禁用事件
	__cc_forbend_events.append( "onBeforeShow" )
	__cc_forbend_events.append( "onBeforeClose" )
	__cc_forbend_events.append( "onBeforePopup" )
	__cc_forbend_events.append( "onBeforeClose" )

	def __init__( self ) :
		toolMgr.addTool( self )
		wnd = GUI.load( "guis/clienttools/soundsetter/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		ITool.__init__( self )
		self.__initialize( wnd )
		self.posZSegment_ = ZSegs.L2
		self.addToMgr()

		self.__pyCurrUI = None						# 当前要调整声音的相关 UI
		self.__flashCBID = 0						# 实现闪烁效果的 callback ID
		self.__tmpFader = GUI.AlphaShader()			# 实现闪烁效果的 shader

		config = "entities/common/tempconfigs/uisounds.py"
		if ResMgr.openSection( config ) is not None :
			uiSounder._UISounder__soundInfos = {}
			UISounder._UISounder__cc_config = "tempconfigs/uisounds.py"
			uiSounder.initialize()
			ResMgr.purge( config )

	def __initialize( self, wnd ) :
		self.__pyAllEvents = ListPanel( wnd.lpAllEvents, wnd.sbAllEvents )
		self.__pyCKAllEvents = CheckBox( wnd.cbAllEvents )
		self.__pyCKAllEvents.checked = False
		self.__pyCKAllEvents.onCheckChanged.bind( self.__onCBAllEventsCheckChanged )

		self.__pyCurrEvents = ListPanel( wnd.lpCurrEvents, wnd.sbCurrEvents )
		self.__pyCurrEvents.onItemSelectChanged.bind( self.__onEventSelected )

		self.__pyUpBtn = Button( wnd.upBtn )
		self.__pyUpBtn.onLClick.bind( self.__onUpClick )
		self.__pyUpBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyDownBtn = Button( wnd.downBtn )
		self.__pyDownBtn.onLClick.bind( self.__onDownClick )
		self.__pyDownBtn.setStatesMapping( UIState.MODE_R2C2 )

		self.__pyTBSound = TextBox( wnd.tbSound )
		self.__pyTBSound.onTextChanged.bind( self.__onTBSoundTextChanged )

		self.__pyTestBtn = Button( wnd.testBtn )
		self.__pyTestBtn.onLClick.bind( self.__onTestBtnClick )
		self.__pyTestBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pySaveBtn = Button( wnd.saveBtn )
		self.__pySaveBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pySaveBtn.onLClick.bind( self.__onSaveBtnClick )
		self.__pyCancelBtn = Button( wnd.cancelBtn )
		self.__pyCancelBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyCancelBtn.onLClick.bind( self.hide )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __setCurrEvents( self, eventInfos ) :
		"""
		设置当前被选中的事件
		"""
		self.__pyCurrEvents.clearItems()
		for eventName, sound in eventInfos :
			event = getattr( self.__pyCurrUI, eventName, None )
			if event is None :
				ERROR_MSG( "%s is not an event of %s " % ( eventName, str( self.__pyCurrUI ) ) )
				continue
			pyItem = SingleColListItem()
			pyItem.text = "%s( %s )" % ( eventName, self.__cc_event_names.get( eventName, "???" ) )
			pyItem.mapEvent = event
			pyItem.mapSound = sound
			self.__pyCurrEvents.addItem( pyItem )

	def __update( self ) :
		"""
		更新事件列表
		"""
		self.__pyAllEvents.clearItems()
		events = self.__getAllEvents( self.__pyCurrUI )
		eventInfos = uiSounder.getSoundInfos( self.__pyCurrUI )
		self.__setCurrEvents( eventInfos )
		currENames = [info[0] for info in eventInfos]
		for event in events :
			name = event.getEventName()
			if name in currENames :
				continue
			if name in self.__cc_forbend_events :
				continue
			if self.__pyCKAllEvents.checked or ( name in self.__cc_common_events ) :
				pyItem = SingleColListItem()
				pyItem.text = "%s( %s )" % ( name, self.__cc_event_names.get( name, "???" ) )
				pyItem.mapEvent = event
				pyItem.mapSound = ""
				self.__pyAllEvents.addItem( pyItem )
		self.__pyAllEvents.sort( key = lambda pyItem : pyItem.text )

	def __getAllEvents( self, pyUI ) :
		"""
		获取所有事件
		"""
		events = inspect.getmembers( pyUI, lambda v:isinstance( v, ControlEvent ) )
		return set( [ evt[1] for evt in events ] )

	# -------------------------------------------------
	def __flashUI( self, dvalue = 0.1 ) :
		"""
		让操作 UI 闪烁
		"""
		self.__tmpFader.value += dvalue
		if self.__tmpFader.value >= 1.0 :
			self.__tmpFader.value = 1.0
			dvalue = -abs( dvalue )
		if self.__tmpFader.value <= 0.2 :
			self.__tmpFader.value = 0.2
			dvalue = abs( dvalue )
		self.__flashCBID = BigWorld.callback( 0.1, Functor( self.__flashUI, dvalue ) )

	# -------------------------------------------------
	def __save( self ) :
		"""
		保存声音配置
		"""
		infos = {}
		for key, soundInfo in uiSounder._UISounder__soundInfos.iteritems() :
			infos[key] = soundInfo.sound
		if PyConfiger().write( infos, "common/tempconfigs/uisounds.py" ) :
			# "保存成功！"
			showAutoHideMessage( 3.0, 0x0bc3, "" )
		else :
			# "路径“res/entities/common/tempconfigs”不存在，保存失败"
			showMessage( 0x0bc1, "", MB_OK )

	# -------------------------------------------------
	def __onCBAllEventsCheckChanged( self, checked ) :
		"""
		显示所有事件
		"""
		if self.__pyCurrUI : self.__update()

	def __onEventSelected( self, pyItem ) :
		"""
		选中某个要配置声音的事件
		"""
		if pyItem is None :
			self.__pyTBSound.text = ""
			self.__pyTBSound.enable = False
		else :
			self.__pyTBSound.enable = True
			self.__pyTBSound.tabStop = True
			self.__pyTBSound.text = pyItem.mapSound

	def __onTBSoundTextChanged( self, pyTextBox ) :
		"""
		输入声音名称时被调用
		"""
		pyItem = self.__pyCurrEvents.pySelItem
		if pyItem is None : return
		pyItem.mapSound = pyTextBox.text

	def __onUpClick( self ) :
		pyItem = self.__pyCurrEvents.pySelItem
		if pyItem is None : return
		self.__pyCurrEvents.removeItem( pyItem )
		self.__pyAllEvents.addItem( pyItem )
		self.__pyAllEvents.sort( key = lambda pyItem : pyItem.text )

	def __onDownClick( self ) :
		"""
		下移一个事件
		"""
		pyItem = self.__pyAllEvents.pySelItem
		if pyItem is None : return
		self.__pyAllEvents.removeItem( pyItem )
		self.__pyCurrEvents.addItem( pyItem )

	def __onTestBtnClick( self ) :
		"""
		测试声音
		"""
		sound = self.__pyTBSound.text.strip()
		soundPath = "ui/%s" % sound
		if not rds.soundMgr.playUI( soundPath ) :
			# "声音 '%s' 不存在!"
			showAutoHideMessage( 3.0, mbmsgs[0x0bc4] % sound, "", pyOwner = self )

	def __onSaveBtnClick( self ) :
		"""
		保存声音
		"""
		currSoundInfos = uiSounder.getSoundInfos( self.__pyCurrUI )
		eventNames = [info[0] for info in currSoundInfos]
		uiSounder.removeUIEventSounds( self.__pyCurrUI, eventNames )
		successEvents = []
		failEvents = []
		for pyItem in self.__pyCurrEvents.pyItems :
			if uiSounder.resetSound( self.__pyCurrUI, pyItem.mapEvent, pyItem.mapSound ) :
				successEvents.append( pyItem.mapEvent.getEventName() )
			else :
				failEvents.append( pyItem.mapEvent.getEventName() )
		if len( failEvents ) :
			evtStr = ""
			for failEvent in failEvents :
				evtStr += PL_NewLine.getSource( 1 )
				evtStr += PL_Space.getSource( 4 ) + failEvent
			evtStr += PL_NewLine.getSource( 1 )
			# "保存以下事件声音失败：%s原因可能是该控件不支持设置事件声音，请与程序联系！"
			showMessage( mbmsgs[0x0bc2] % evtStr, "", MB_OK )
		else:
			self.__save()
			self.hide()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		Window.onKeyDown_( self, key, mods )
		if key == KEY_ESCAPE :
			self.hide()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getCHName( self ) :
		return "声音配置器"

	def getHitUIs( self, pyRoot, mousePos ) :
		def verifier( pyUI ) :
			if not pyUI.rvisible : return False, 0
			if not pyUI.hitTest( *mousePos ) : return False, 0
			if not pyUI.acceptEvent : return False, 1
			return True, 1
		pyUIs = util.postFindPyGui( pyRoot.getGui(), verifier, True )
		return [( pyUI.__class__.__name__, pyUI ) for pyUI in pyUIs]

	def getHitUI( self, pyRoot, mousePos ) :
		pyUIs = self.getHitUIs( pyRoot, mousePos )
		if len( pyUIs ) : return pyUIs[0][1]
		return None

	# -------------------------------------------------
	def show( self, pyUI ) :
		self.__pyCurrUI = pyUI
		pyUI.getGui().addShader( self.__tmpFader )
		self.__flashUI()
		self.__update()										# 根据指定 UI 更新其声音信息
		self.__pyCKAllEvents.checked = False				# 不显示不常用事件
		LastKeyDownEvent.lock()								# 取消 LastKeyDown 消息
		LastKeyUpEvent.lock()								# 取消 LastKeyUp 消息
		LastMouseEvent.lock()								# 取消 LastMouse 消息

		Window.show( self )
		pyUI.getGui().addShader( self.__tmpFader )
		self.__pyTBSound.tabStop = True
		rds.uiHandlerMgr.setShieldUI( self )
		if rds.statusMgr.isInWorld() :						# 锁定相机
			rds.worldCamHandler.disable()

	def hide( self ) :
		Window.hide( self )
		LastKeyDownEvent.unlock()
		LastKeyUpEvent.unlock()
		LastMouseEvent.unlock()
		rds.uiHandlerMgr.clearShieldUI( self )
		BigWorld.cancelCallback( self.__flashCBID )
		if self.__pyCurrUI :
			self.__pyCurrUI.getGui().delShader( self.__tmpFader )
		if rds.statusMgr.isInWorld() :
			rds.worldCamHandler.enable()
