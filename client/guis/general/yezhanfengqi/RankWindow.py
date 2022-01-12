# -*- coding: gb18030 -*-
#
# $Id: RankWindow.py, fangpengjun Exp $

"""
implement RankWindow window class

"""
from guis import *
from guis.common.RootGUI import RootGUI
from guis.common.Window import Window
from guis.controls.StaticText import StaticText
from guis.controls.ODListPanel import ODListPanel
from guis.controls.TextBox import TextBox
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ButtonEx import HButtonEx
from LabelGather import labelGather
from RankItem import RankItem
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
import Timer
from Time import Time
import GUIFacade
import csdefine
import csconst

class RankWindow( Window ):
	
	_cc_fly_times = [60, 30, 15, 5, 4, 3, 2, 1]
	
	def __init__( self ):
		wnd = GUI.load( "guis/general/yezhanfengqi/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.isSvrTrigger = False					#是手动打开还是服务器触发
		self.__usecbid = 0
		self.__precbid = 0
		self.__closecbid = 0
		self.__startcbid = 0
		self.__countcbid = 0
		self.__startTime = 0.0
		self.__closeTime = 0.0
		self.__preTime = 0.0
		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( wnd )
	
	def __initialize( self, wnd ):
		self.__pyRankPanel = ODListPanel( wnd.rankPanel.clipPanel, wnd.rankPanel.sbar )
		self.__pyRankPanel.onViewItemInitialized.bind( self.__onInitItem )
		self.__pyRankPanel.onDrawItem.bind( self.__onDrawItem )
		self.__pyRankPanel.ownerDraw = True
		self.__pyRankPanel.itemHeight = 23
		self.__pyRankPanel.onItemSelectChanged.bind( self.__onRankSelected )
		
		self.__pyRtTime = CSRichText( wnd.rtTime )					#已持续时间
		self.__pyRtTime.align = "L"
		self.__pyRtTime.text = ""
		
		self.__pyRtWarn = CSRichText( wnd.rtWarn )					#倒计时提醒
		self.__pyRtWarn.align = "L"
		self.__pyRtWarn.text = ""
		
		self.__pyRtAcount = CSRichText( wnd.rtAcount )				#战场总人数
		self.__pyRtAcount.align = "L"
		self.__pyRtAcount.text = ""
		
		self.__pyBtnQuit = HButtonEx( wnd.btnQuit )
		self.__pyBtnQuit.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnQuit.onLClick.bind( self.__onQuit )
		labelGather.setPyBgLabel( self.__pyBtnQuit, "YezhanFengQi:main", "quit")
		
		self.__pyBtnTitles = {}
		for name, child in wnd.children:
			if not name.startswith( "btn_" ):continue
			pyBtnTitle = HButtonEx( child )
			pyBtnTitle.setStatesMapping( UIState.MODE_R4C1 )
			index = int( name.split( "_" )[1] )
			pyBtnTitle.index = index
			pyBtnTitle.isSort = True
			pyBtnTitle.sortByTitle = False
			labelGather.setPyBgLabel( pyBtnTitle, "YezhanFengQi:main", name )
			pyBtnTitle.onLClick.bind( self.__onSortByTitle )
			self.__pyBtnTitles[index] = pyBtnTitle
		
		self.__pyFlyCounter = FlyCountText()
		labelGather.setPyLabel( self.pyLbTitle_,"YezhanFengQi:main", "title" )

	# -----------------------------------------------------------------------------
	# pravite
	# -----------------------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_SHOW_FENGQI_RANK_WINDOW"] = self.__onShowRankWnd
		self.__triggers["EVT_ON_FENGQI_ON_ENTER"] = self.__onEnterFengQi
		self.__triggers["EVT_ON_FENGQI_UP_REPORT"] = self.__onUpdateReport
		self.__triggers["EVT_ON_FENGQI_MEMBER_EXIT"] = self.__onMemberExit
		self.__triggers["EVT_ON_FENGQI_SET_INTERGRAL"] = self.__onSetMemIntergral
		self.__triggers["EVT_ON_FENGQI_UP_BOXNUM"] = self.__onUpdateBoxNum
		self.__triggers["EVT_ON_FENGQI_COUNT_DOWN"] = self.__onCountDown
		self.__triggers["EVT_ON_FENGQI_ON_EXIT"] = self.__onExitFengQi
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( eventMacro, self )
	# -----------------------------------------------------------
	def __onInitItem( self, pyViewItem ):
		"""
		初始化积分控件
		"""
		item = GUI.load( "guis/general/yezhanfengqi/membar.gui" )
		uiFixer.firstLoadFix( item )
		pyRank = RankItem( item, self )
		pyViewItem.addPyChild( pyRank )
		pyViewItem.crossFocus = False
		pyRank.pos = -1.0, 1
		pyViewItem.pyItem = pyRank
	
	def __onDrawItem( self, pyViewItem ):
		"""
		绘画积分控件
		"""
		pyRank = pyViewItem.pyItem
		rankInfo = pyViewItem.listItem
		pyRank.updateRank( rankInfo )
		
	def __onShowRankWnd( self, isSvrTrigger = False ):
		"""
		显示积分界面
		"""
		self.isSvrTrigger = isSvrTrigger
		if isSvrTrigger:									#服务器触发,重新刷一下
			for pyViewItem in self.__pyRankPanel.pyViewItems:
				pyRank = pyViewItem.pyItem
				rankData = pyViewItem.listItem
				pyRank.updateRank( rankData )
			self.show()
		else:
			self.visible = not self.visible
	
	def __onEnterFengQi( self, role ):
		"""
		进入回调
		"""
		player = BigWorld.player()
		self.__startcbid = BigWorld.callback( 1.0, self.__setStartTime )
	
	def __setStartTime( self ):
		if self.__startTime > 0:
			if self.__usecbid:
				Timer.cancel( self.__usecbid )
				self.__usecbid = 0
			self.__usecbid = Timer.addTimer( 0, 1, self.__useTiming )
			self.__precbid = BigWorld.callback( 0.0, self.__setPreTime )
			BigWorld.cancelCallback( self.__startcbid )
			return
		self.__startTime = float( BigWorld.getSpaceDataFirstForKey( BigWorld.player().spaceID, csconst.SPACE_SPACEDATA_START_TIME) )
		self.__startcbid = BigWorld.callback( 2.0, self.__setStartTime )
	
	def __setPreTime( self ):
		if self.__preTime > 0:
			if self.__countcbid:
				Timer.cancel( self.__countcbid )
				self.__countcbid = 0
			self.__countcbid = Timer.addTimer( 0, 1, self.__countTiming )
			BigWorld.cancelCallback( self.__precbid )
			return
		self.__preTime = float( BigWorld.getSpaceDataFirstForKey( BigWorld.player().spaceID, csconst.SPACE_SPACEDATA_PREPARE_TIME ) )
		self.__precbid = BigWorld.callback( 1.0, self.__setPreTime )
	
	def __onUpdateReport( self, mId, mName, mKill, mBeKill ):
		"""
		接收积分数据
		"""
		roleIDs = [mInfo["roleID"] for mInfo in self.__pyRankPanel.items]
		if mId in roleIDs:
			for pyViewItem in self.__pyRankPanel.pyViewItems:
				rankData = pyViewItem.listItem
				if rankData["roleID"] == mId:
					pyRank = pyViewItem.pyItem
					rankData["kill"] = mKill
					rankData["bekill"] = mBeKill
					pyRank.setKillInfos( mKill, mBeKill )
		else:
			mData = {"roleID":mId, "roleName":mName, "kill":mKill, "bekill":mBeKill, "chest":0, "intergral":0, "exp":0, "rewards":0}
			self.__pyRankPanel.addItem( mData )
			self.__updateMemCount()
	
	def __onMemberExit( self, roleID ):
		"""
		退出战场
		"""
		for mData in self.__pyRankPanel.items:
			if mData["roleID"] == roleID:
				self.__pyRankPanel.removeItem( mData )
		self.__updateMemCount()
	
	def __onSetMemIntergral( self, mId, mIntergral ):
		"""
		更新积分
		"""
		for pyViewItem in self.__pyRankPanel.pyViewItems:
			rankData = pyViewItem.listItem
			if rankData["roleID"] == mId:
				rankData["intergral"] = mIntergral
				pyRank = pyViewItem.pyItem
				pyRank.setIntergal( mIntergral )
		self.__sortByIntergral( False )
		
	def __onUpdateBoxNum( self, mId, boxNum ):
		"""
		更新宝箱数
		"""
		for pyViewItem in self.__pyRankPanel.pyViewItems:
			rankData = pyViewItem.listItem
			if rankData["roleID"] == mId:
				rankData["chest"] = boxNum
				pyRank = pyViewItem.pyItem
				pyRank.setBoxNum( boxNum )
	
	def __onCountDown( self ):
		"""
		关闭副本倒计时
		"""
		if self.__closecbid:
			Timer.cancel( self.__closecbid )
			self.__closecbid = 0
		self.__closeTime = Time.time() + 60.0
		self.__closecbid = Timer.addTimer( 0, 1, self.__counting )
	
	def __counting( self ):
		"""
		结束倒计时
		"""
		reTime = self.__closeTime - Time.time()
		if reTime > 0:
			timeText = labelGather.getText( "YezhanFengQi:main", "warning" ) % reTime
			self.__pyRtWarn.text = PL_Font.getSource( timeText , fc = ( 230, 227, 185, 255 ) )
			time = int( reTime )
			if time in self._cc_fly_times:
				self.__pyFlyCounter.showTimeCount( time )
		else:
			self.__pyRtWarn.text = ""
			Timer.cancel( self.__closecbid )
			self.__closecbid = 0
	
	def __onExitFengQi( self, role ):
		"""
		离开副本回调
		"""
		self.__pyRankPanel.clearItems()
		if self.__usecbid:
			Timer.cancel( self.__usecbid )
			self.__usecbid = 0
		if self.__closecbid:
			Timer.cancel( self.__closecbid )
			self.__closecbid = 0
		self.__startTime = 0.0
		self.__closeTime = 0.0
		self.__pyRtTime.text = ""
		self.hide()
	
	def __onRankSelected( self, index ):
		"""
		选取某个积分数据
		"""
		if index < 0:return
	
	def __onQuit( self, pyBtn ):
		"""
		离开战场
		"""
		if pyBtn is None:return
		BigWorld.player().fengQiReqExit()
		
	def __onSortByTitle( self, pyBtn ):
		"""
		按按钮标题排序
		"""
		tagMaps = {0:"roleName",
				1:"bekill",
				2:"kill",
				3:"chest",
				4:"intergral",
				5:"exp",
				6:"rewards"
			}
		if pyBtn is None:return
		tag = tagMaps.get( pyBtn.index, "" )
		if tag == "":return
		sortFlag = pyBtn.sortByTitle
		if tag == "intergral":
			self.__sortByIntergral( sortFlag )
		else:
			self.__pyRankPanel.sort( key = lambda item : item[tag], reverse = sortFlag )
		pyBtn.sortByTitle = not sortFlag
	
	def __updateMemCount( self ):
		"""
		更新战场人数
		"""
		count = self.__pyRankPanel.itemCount
		self.__pyRtAcount.text = labelGather.getText( "YezhanFengQi:main", "count" )%count
	
	def __useTiming( self ):
		"""
		更新副本持续时间
		"""
		usetime = Time.time() - self.__startTime
		if usetime >= 0.0:
			min = int( usetime )/60
			sec = int( usetime )%60
			timeText = PL_Font.getSource( "%02d:%02d"%( min, sec ) , fc = ( 230, 227, 185, 255 ) )
			timeText = labelGather.getText( "YezhanFengQi:main", "usetime" ) % timeText
			self.__pyRtTime.text = timeText
	
	def __countTiming( self ):
		"""
		准备时间倒计时
		"""
		pretime = self.__preTime - ( Time.time() - self.__startTime )
		if pretime <= 0.0:
			Timer.cancel( self.__countcbid )
			self.__countcbid = 0
			self.__pyFlyCounter.visible = False
		else:
			time = int( pretime )
			if time in self._cc_fly_times:
				self.__pyFlyCounter.showTimeCount( time )
	
	def __sortByIntergral( self, sortFlag ):
		"""
		积分排序，若积分相同，按击杀次数多优先，
		击杀次数相同，则按死亡少的优先
		"""
		def func( item1, item2 ) :
			if item1["intergral"] != item2["intergral"] :									# 先按积分排序
				return cmp( item2["intergral"], item1["intergral"] )
			elif item1["kill"] != item2["kill"] :
				return cmp( item2["kill"], item1["kill"] )					# 同积分按击杀数排序
			else:
				return cmp( item1["bekill"], item2["bekill"] )						# 同击杀数按死亡次数排序
		self.__pyRankPanel.sort( cmp = func, reverse = sortFlag )

	# -----------------------------------------------------------------------------
	# public
	# -----------------------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def show( self ):
		"""
		显示窗口
		"""
		self.__updateMemCount()
		self.__sortByIntergral( False )
		Window.show( self )

	def hide( self ):
		"""
		隐藏窗口
		"""
		Window.hide( self )

	def onLeaveWorld( self ):
		"""
		离开游戏调用
		"""
		self.__pyRankPanel.clearItems()
		for pyBtnTitle in self.__pyBtnTitles.values():
			pyBtnTitle.sortByTitle = True
		Timer.cancel( self.__closecbid )
		Timer.cancel( self.__usecbid )
		self.__usecbid = 0
		self.__closecbid = 0
		self.__startTime = 0.0
		self.__closeTime = 0.0
		self.hide()
	
	def getColCenterPos( self, index ):
		pyBtnTitle = self.__pyBtnTitles.get( index )
		if pyBtnTitle is None:return 0
		return pyBtnTitle.center - self.__pyRankPanel.left
	
	def getBtnTitles( self ):
		return self.__pyBtnTitles

# --------------------------------------------------------------------------------------------
from AbstractTemplates import Singleton
import time

class FlyCountText( RootGUI, Singleton ):

	__cg_bg = None

	def __init__( self ):
		Singleton.__init__( self )
		if FlyCountText.__cg_bg is None :
			FlyCountText.__cg_bg = GUI.load( "guis/general/yezhanfengqi/count.gui" )
		bg = util.copyGuiTree( FlyCountText.__cg_bg )
		uiFixer.firstLoadFix( bg )
		RootGUI.__init__( self, bg )
		self.h_dockStyle = "CENTER"
		
		self.posZSegment = ZSegs.LMAX
		self.moveFocus = False
		self.escHide_ = False
		self.focus = False
		self.__stCount = bg.stCount
		self.__stCount.explicitSize = True
		self.__pyStCount = StaticText( self.__stCount )
		self.__pyStCount.focus = False
		self.__pyStCount.text = ""
		try :
			self.__pyStCount.font = "combtext.font"
		except :
			self.__pyStCount.font = "system_small.font"
			self.__pyStCount.font = "system_small.font"
		self.__unitSize = ( self.__stCount.width, self.__stCount.height )
		self.__primalSize = self.__unitSize
		self.__bgShader = bg.shader
		self.__bgShader.value = 1.0
		self.__textShader = self.__stCount.shader
		self.__textShader.value = 1.0
		self.__startTime = 0.0
		self.__lastTime = 0
		self.__textCBID = 0
		self.activable_ = False  # 窗口不被激活
		self.addToMgr( "flyCountText" )

	def showTimeCount( self, count ):
		"""
		开始连击
		"""
		self.__bgShader.value = 1.0
		BigWorld.cancelCallback( self.__textCBID )
		self.__textCBID = BigWorld.callback( 0.0, Functor( self.__flashText, count ) )
		self.visible = True

	def updatePosition_( self, passTime ) :
		"""
		"""
		if passTime < 0.4 :										# 缩放时缓慢上升
			self.bottom -= 10
		else :													# 回复后快速上升
			self.bottom -= 35 * 0.45 ** self.__delta
			self.__delta += 1

	def __updateColor( self, passTime ) :
		"""
		"""
		if passTime > self.__lastTime / 2 :
			self.__textShader.value *= 0.55
			self.__bgShader.value *= 0.55

	def __updateSize( self, passTime ) :
		"""
		"""
		# 先放大后缩小，在前面0.1秒放到最大，在随后的0.15秒内恢复回原始大小
		self.__stCount.width = linearScale( self.__primalSize[0], passTime )
		self.__stCount.height = linearScale( self.__primalSize[1], passTime )

	def __onUpdate( self ) :
		passTime = time.time() - self.__startTime
		if passTime >= self.__lastTime :
			self.__pyStCount.visible = False
			BigWorld.cancelCallback( self.__textCBID )
			self.__textCBID = 0
			self.visible = False
		else :
			self.__updateColor( passTime )
			self.__updateSize( passTime )
			self.__textCBID = BigWorld.callback( 0.06, self.__onUpdate )

	def __flashText( self, count ):
		"""
		当前连击数
		"""
		self.__startTime = time.time()
		self.__lastTime = 2.0
		self.__textShader.value = 1.0
		self.__pyStCount.text = str( count )
		if count > 15:
			self.__pyStCount.font = "combtext.font"
		else:
			self.__pyStCount.font = "combtext_0.font"
		units = len( str(count) )
		self.__primalSize = ( self.__unitSize[0]*units, self.__unitSize[1] )
		self.__pyStCount.visible = True
		self.__onUpdate()

def vx( va, vb, t, tx ):
	if tx <= t:
		return va + tx * (vb - va) / t
	else:
		return vb

def linearZoomOut( base, tx, t, maxScale ):
	"""
	线性缩小
	"""
	return vx(base * maxScale, base, t, tx)

def linearZoomIn( base, tx, t, maxScale ):
	"""
	线性放大
	"""
	return vx(base, base * maxScale, t, tx)

def linearScale( base, tx, zoomIn_t=0.12, zoomOut_t=0.15, maxScale=2.65 ):
	"""
	线性缩放，先放大然后恢复
	"""
	if tx <= zoomIn_t:
		return linearZoomIn(base, tx, zoomIn_t, maxScale)
	else:
		return linearZoomOut(base, tx-zoomIn_t, zoomOut_t, maxScale)
