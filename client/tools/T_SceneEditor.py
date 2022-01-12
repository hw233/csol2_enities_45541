# -*- coding: gb18030 -*-

import math
import time
import GUI
import ResMgr
import BigWorld
from gbref import rds
from event import EventCenter as ECenter
from Function import Functor
from MessageBox import showMessage, MB_OK, MB_OK_CANCEL, RS_OK
from AbstractTemplates import MultiLngFuncDecorator

from guis.UIFixer import uiFixer
from guis.Toolbox import toolbox
from guis.uidefine import UIState, InputMode, ZSegs
from guis.common.GUIBaseObject import GUIBaseObject
from guis.common.RootGUI import RootGUI
from guis.controls.TextBox import TextBox
from guis.controls.ODComboBox import ODComboBox
from guis.controls.Control import Control
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TabSwitcher import TabSwitcher
from guis.tooluis.CSMLRichTextBox import CSMLRichTextBox
from guis.general.ScenePlayer.ScenePlayer import Fresco, FadingObject, FadingText
from guis.general.ScenePlayer.ScenePlayer import Motor, TextureInfo
from tools import toolMgr
from ITool import ITool

_global_tips = {
	0 : "贴图定位到起始位置处",
	1 : "贴图定位到目标位置处",
	2 : "显示信息框",
	3 : "隐藏信息框",
	}

class deco_initContent( MultiLngFuncDecorator ) :
	@staticmethod
	def locale_big5( SELF, font, size ) :
		"""
		"""
		deco_initContent.originalFunc( SELF, "MSJHBD.ttf", 24 )

class SceneEditor( FadingObject, RootGUI, ITool ) :
	"""剧情编辑器"""
	__cc_orgn_size = ( 1024, 768 )								# 默认在此分辨率下配置剧情

	def __init__( self ) :
		toolMgr.addTool( self )
		gui = GUI.load( "guis/clienttools/sceneeditor/wnd.gui" )
		uiFixer.firstLoadFix( gui )
		FadingObject.__init__( self, gui )
		RootGUI.__init__( self, gui )
		ITool.__init__( self )
		self.movable_ = False
		self.escHide_ = False
		self.posZSegment = ZSegs.L3
		self.fadein()
		self.addToMgr()
		self.__opMode = "NORMAL"
		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )

		self.__pyFresco = MFresco( gui.fresco )
		self.__pyFresco.onLMouseDown.bind( self.__onFrescoLMouseDown )
		self.__pyFresco.onLMouseUp.bind( self.__onFrescoLMouseUp )
		self.__pyFresco.onMouseMove.bind( self.__onFrescoMouseMove )
		self.__pyFresco.onMouseEnter.bind( self.__onFrescoMouseEnter )
		self.__pyFresco.onMouseLeave.bind( self.__onFrescoMouseLeave )
		self.__controller = Controller( self.__pyFresco )			# 这里存在交叉引用，通过调用destroy来解除

		self.__pyDynPanel = DynamicPanel( gui.frame_instant )
		dynMonitor.bindScreen( self.__pyDynPanel )					# 这里存在交叉引用，通过调用destroy来解除
		self.__pySceneInfoPanel = SceneInfoPanel( gui.frame_info )

		self.__pyBtnRestart = HideButton( gui.btn_restart )
		self.__pyBtnRestart.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnRestart.onLClick.bind( self.__onRestart )
		self.__pyBtnRestart.onMouseEnter.bind( self.__onShowDisplayButton )
		self.__pyBtnRestart.onMouseLeave.bind( self.__onHideDisplayButton )

		self.__pyBtnPlayNode = HideButton( gui.btn_playNode )
		self.__pyBtnPlayNode.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnPlayNode.onLClick.bind( self.__onPlayNode )
		self.__pyBtnPlayNode.onMouseEnter.bind( self.__onShowDisplayButton )
		self.__pyBtnPlayNode.onMouseLeave.bind( self.__onHideDisplayButton )

		self.__pyBtnPause = HideButton( gui.btn_pause )
		self.__pyBtnPause.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnPause.onLClick.bind( self.__onPause )
		self.__pyBtnPause.onMouseEnter.bind( self.__onShowDisplayButton )
		self.__pyBtnPause.onMouseLeave.bind( self.__onHideDisplayButton )

		self.__pyBtnContinue = HideButton( gui.btn_continue )
		self.__pyBtnContinue.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnContinue.onLClick.bind( self.__onContinue )
		self.__pyBtnContinue.onMouseEnter.bind( self.__onShowDisplayButton )
		self.__pyBtnContinue.onMouseLeave.bind( self.__onHideDisplayButton )

		self.__pyBtnExit = HideButton( gui.btn_stop )
		self.__pyBtnExit.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnExit.onLClick.bind( self.__onExit )
		self.__pyBtnExit.onMouseEnter.bind( self.__onShowDisplayButton )
		self.__pyBtnExit.onMouseLeave.bind( self.__onHideDisplayButton )

		self.__pyBtnZoomIn = HideButton( gui.btn_zoomIn )
		self.__pyBtnZoomIn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnZoomIn.onLClick.bind( self.__onZoomIn )
		self.__pyBtnZoomIn.onMouseEnter.bind( self.__onShowDisplayButton )
		self.__pyBtnZoomIn.onMouseLeave.bind( self.__onHideDisplayButton )

		self.__pyBtnZoomOut = HideButton( gui.btn_zoomOut )
		self.__pyBtnZoomOut.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnZoomOut.onLClick.bind( self.__onZoomOut )
		self.__pyBtnZoomOut.onMouseEnter.bind( self.__onShowDisplayButton )
		self.__pyBtnZoomOut.onMouseLeave.bind( self.__onHideDisplayButton )

		self.__pyBtnVSFrame = HideButton( gui.btn_hideFrame )
		self.__pyBtnVSFrame.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnVSFrame.onLClick.bind( self.__onVisibleFrame )
		self.__pyBtnVSFrame.onMouseEnter.bind( self.__onShowFrameButton )
		self.__pyBtnVSFrame.onMouseLeave.bind( self.__onHideFrameButton )

		self.__pyContent = FadingText( gui.rtx_content )		# 剧情文本
		self.__pyContent.align = "C"
		self.__pyContent.h_dockStyle = "CENTER"
		self.__pyContent.v_dockStyle = "BOTTOM"
		self.__initContent( "STXINWEI.TTF", 28 )

		dynMonitor.bindObserver( self )
		self.changeOpMode( "NORMAL" )

		self.__onResolutionChanged( ( 0, 0 ) )

	@deco_initContent
	def __initContent( self, font, fontSize ) :
		""""""
		self.__pyContent.font = font
		self.__pyContent.fontSize = fontSize

	def __onRestart( self ) :
		"""重新播放"""
		self.__controller.restart()

	def __onPlayNode( self ) :
		"""播放单个节点"""
		selNodeIdx = self.__pySceneInfoPanel.getSelNodeIdx()
		self.__controller.playNode( selNodeIdx )

	def __onPause( self ) :
		"""暂停播放"""
		self.__controller.pause()

	def __onContinue( self ) :
		"""继续播放"""
		self.__controller.continueMove()

	def __onExit( self ) :
		"""退出"""
		def exit() :
			#self.release()
			self.hide()
		if configEditor.isEdited() :
			def callback( res ) :
				if res == RS_OK : exit()
			showMessage( "数据未保存，是否放弃此次修改？", \
				"", MB_OK_CANCEL, callback, pyOwner = self )
		else :
			exit()

	def __onVisibleFrame( self ) :
		"""隐藏/显示信息框"""
		if self.__pyDynPanel.visible :
			self.__pyDynPanel.visible = 0
			self.__pySceneInfoPanel.visible = 0
			self.__pyBtnVSFrame.text = _global_tips[2]
		else :
			self.__pyDynPanel.visible = 1
			self.__pySceneInfoPanel.visible = 1
			self.__pyBtnVSFrame.text = _global_tips[3]

	def __onZoomIn( self ) :
		"""放大贴图"""
		self.__pyFresco.zoomIn()

	def __onZoomOut( self ) :
		"""缩小贴图"""
		self.__pyFresco.zoomOut()


	# -------------------------------------------------
	# fresco opration
	# -------------------------------------------------
	def __onFrescoLMouseDown( self, pyCover ) :
		"""
		当鼠右键在地图上按下时被调用
		"""
		rds.uiHandlerMgr.capUI( pyCover )
		self.__mouseDownPos = pyCover.mousePos
		rds.ccursor.set( "movehand" )

	def __onFrescoLMouseUp( self ) :
		"""
		当鼠标右键在地图上提起时被调用
		"""
		rds.uiHandlerMgr.uncapUI( self.__pyFresco )
		rds.ccursor.set( "hand" )

	def __onFrescoMouseMove( self, dx, dy ) :
		"""
		当鼠标右在地图上移动时被调用
		"""
		if rds.uiHandlerMgr.getCapUI() == self.__pyFresco :
			self.__pyFresco.left -= dx
			self.__pyFresco.top -= dy

	def __onFrescoMouseEnter( self ) :
		"""鼠标进入壁画区域"""
		rds.ccursor.set( "hand" )

	def __onFrescoMouseLeave( self ) :
		"""鼠标进入壁画区域"""
		rds.ccursor.normal()

	# -------------------------------------------------
	# play buttons display
	# -------------------------------------------------
	def __onShowDisplayButton( self ) :
		self.__pyBtnRestart.appear()
		self.__pyBtnPlayNode.appear()
		self.__pyBtnPause.appear()
		self.__pyBtnContinue.appear()
		self.__pyBtnExit.appear()
		self.__pyBtnZoomIn.appear()
		self.__pyBtnZoomOut.appear()

	def __onHideDisplayButton( self ) :
		self.__pyBtnRestart.disappear()
		self.__pyBtnPlayNode.disappear()
		self.__pyBtnPause.disappear()
		self.__pyBtnContinue.disappear()
		self.__pyBtnExit.disappear()
		self.__pyBtnZoomIn.disappear()
		self.__pyBtnZoomOut.disappear()

	def __onShowFrameButton( self ) :
		self.__pyBtnVSFrame.appear()

	def __onHideFrameButton( self ) :
		if not self.__pyDynPanel.visible :
			self.__pyBtnVSFrame.disappear()

	def __onResolutionChanged( self, preRes ) :
		""""""
		self.size = BigWorld.screenSize()
		self.pos = 0, 0
		scale = max( self.width / self.__cc_orgn_size[0], self.height / self.__cc_orgn_size[1] )
		self.__pyFresco.zoom( scale )							# 按照大的比例进行缩放
		# 排列按钮和版面
		self.__pyBtnVSFrame.right = self.width - 2
		self.__pyBtnVSFrame.bottom = self.height - 2
		self.__pyBtnExit.middle = self.__pyBtnVSFrame.middle
		self.__pyBtnExit.right = self.__pyBtnVSFrame.left - 2
		self.__pyBtnPause.middle = self.__pyBtnVSFrame.middle
		self.__pyBtnPause.right = self.__pyBtnExit.left
		self.__pyBtnContinue.middle = self.__pyBtnVSFrame.middle
		self.__pyBtnContinue.right = self.__pyBtnExit.left
		self.__pyBtnPlayNode.middle = self.__pyBtnVSFrame.middle
		self.__pyBtnPlayNode.right = self.__pyBtnContinue.left
		self.__pyBtnRestart.middle = self.__pyBtnVSFrame.middle
		self.__pyBtnRestart.right = self.__pyBtnPlayNode.left
		self.__pyBtnZoomIn.middle = self.__pyBtnVSFrame.middle
		self.__pyBtnZoomIn.right = self.__pyBtnRestart.left
		self.__pyBtnZoomOut.middle = self.__pyBtnVSFrame.middle
		self.__pyBtnZoomOut.right = self.__pyBtnZoomIn.left

		self.__pySceneInfoPanel.right = self.width - 20
		self.__pySceneInfoPanel.top = self.top + 20

		self.__pyDynPanel.right = self.__pySceneInfoPanel.right
		self.__pyDynPanel.top = self.__pySceneInfoPanel.bottom + 5

		spacing = self.__pyBtnVSFrame.left
		self.__pyContent.maxWidth = spacing - 40				# 自动调整文本显示的最大宽度
		self.__pyContent.left = ( spacing - self.__pyContent.maxWidth ) * 0.5

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getCHName( self ) :
		return "剧情编辑器"

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

	def dispose( self ) :
		self.__pyFresco.draw( None )
		self.__pySceneInfoPanel.onExit()
		self.__controller.destroy()
		dynMonitor.destroy()
		configEditor.release()
		normalEditor.release()
		nodesEditor.release()
		RootGUI.dispose( self )

	def show( self, pyUI ) :
		"""
		显示工具
		"""
		RootGUI.show( self )

	def hide( self ) :
		self.__controller.releaseBgMusic()
		self.__controller.stop()
		self.changeOpMode( "NORMAL" )
		configEditor.release()
		RootGUI.hide( self )

	def drawFresco( self, sceneId ) :
		"""绘制"""
		if sceneId == normalEditor.getOriginal( "sceneId" ) :
			self.__pyFresco.draw( normalEditor.getTxInfo() )
		else :
			self.__pyFresco.draw( None )

	def onEvent( self, evtMacro, *args ) :
		if evtMacro == "EVT_ON_RESOLUTION_CHANGED" :			# 分辨率改变的事件
			self.__onResolutionChanged( *args )

	def changeOpMode( self, mode ) :
		"""改变操作模式"""
		assert mode in ( "PLAY", "PAUSE", "NORMAL" ), ""
		self.__opMode = mode
		self.__pyBtnRestart.enable = mode in ["NORMAL", "PAUSE"]
		self.__pyBtnPlayNode.enable = mode in ["NORMAL", "PAUSE"]
		self.__pyBtnExit.enable = mode in ["NORMAL", "PAUSE"]
		self.__pyBtnPause.visible = mode in ["PLAY"]
		self.__pyBtnContinue.visible = mode in ["NORMAL","PAUSE"]
		self.__pyBtnContinue.enable = mode in ["PAUSE"]
		self.__pyFresco.moveFocus = mode in ["NORMAL", "PAUSE"]

	def setFrescoPos( self, pos ) :
		self.__pyFresco.pos = pos

	def getFrescoPos( self ) :
		return self.__pyFresco.pos

	def onEnterPlaying( self ) :
		self.changeOpMode( "PLAY" )
		self.__pySceneInfoPanel.onEnterPlaying()

	def onLeavePlaying( self ) :
		self.changeOpMode( "NORMAL" )
		self.__pySceneInfoPanel.onLeavePlaying()

	def updatePlayingNode( self, index ) :
		""""""
		self.__pySceneInfoPanel.updatePlayingNode( index )

	def updateContent( self, text ) :
		""""""
		if text == "EOF" :							# 配置设置为隐藏文本
				self.__pyContent.fadeout()
		elif text :									# 如果有提示文本
			self.__pyContent.text = text
			self.__pyContent.fadein()

	def onPause( self ) :
		self.changeOpMode( "PAUSE" )

	def isPlaying( self ) :
		return self.__controller.isPlaying()

	def onSceneSelected( self, sceneId ) :
		"""选择一个剧情"""
		self.drawFresco( sceneId )
		self.changeOpMode( "NORMAL" )
		self.__pyFresco.zoom( 1.0 )


class HideButton( HButtonEx ) :
	"""能隐身的按钮"""

	def disappear( self ) :
		for name, elem in self.gui.elements.iteritems() :
			elem.visible = 0
		self.pyText_.visible = 0

	def appear( self ) :
		for name, elem in self.gui.elements.iteritems() :
			elem.visible = 1
		self.pyText_.visible = 1


from bwdebug import printStackTrace
class MFresco( Control, Fresco ) :
	""""""
	def __init__( self, gui ) :
		Fresco.__init__( self, gui )
		Control.__init__( self, gui )
		self.focus = True
		self.crossFocus = True
		self.moveFocus = True
		self.fadein()
		self.__scale = 1.0

	def draw( self, txInfo ) :
		if txInfo :
			Fresco.draw( self, txInfo )
		else :
			self.texture = "/"
			self.size = 200,200
			self.zoom( self.__scale )

	def zoomIn( self ) :
		self.zoom( min( self.__scale + 0.1, 3 ) )

	def zoomOut( self ) :
		self.zoom( max( self.__scale - 0.1, 0.1 ) )

	def zoom( self, scale ) :
		Fresco.zoom( self, scale )
		self.__scale = scale

	# -------------------------------------------------
	# property
	# -------------------------------------------------
	def _setLeft( self, left ) :
		"""保持pos位于父窗口的中心点上"""
		Fresco._setLeft( self, left )
		dynMonitor.updatePosition( self.pos )

	def _setTop( self, top ) :
		"""保持pos位于父窗口的中心点上"""
		Fresco._setTop( self, top )
		dynMonitor.updatePosition( self.pos )

	left = property( Fresco._getLeft, _setLeft )
	top = property( Fresco._getTop, _setTop )
	pos = property( Fresco._getPos, Fresco._setPos )


class Controller( object ) :
	"""遥控器"""
	def __init__( self, obj ) :
		object.__init__( self )
		self.__driveObj = obj
		self.__motor = Motor( obj )
		self.__motor.onArrive.bind( self.__onNodeArrive )
		self.__pause_info = {}
		self.__dwell_cbid = 0
		self.__play_time = 0
		self.__node_start_time = 0
		self.__node_play_time = 0
		self.__node_idx = 0
		self.__isPlaying = False
		self.setPlayMode( "ALL" )									# 默认播放所有节点

	def __onNodeArrive( self, dst_pos ) :
		"""已经到达到目标节点
		@param	dst_pos : 目标点坐标"""
		self.__play_time += time.time() - self.__node_start_time
		dynMonitor.updatePlayTime( self.__play_time )				# 更新已经播放的时间
		if self.__playMode == "NODE" :
			dynMonitor.stopPlaying()
			return
		elif self.__playMode == "ALL" :
			node = nodesEditor.getNodeByPos( dst_pos )
			if node is None :
				print "Can't find next node."
				self.__motor.shut()
				dynMonitor.stopPlaying()
				self.stopBgMusic()
			else :
				self.__node_idx = nodesEditor.getNodes().index( node )
				self.__node_start_time = time.time()				# 从节点开始统计时间
				self.__node_play_time = 0
				if node.dwell_time > 0 :
					func = Functor( self.__motor.move,
									node.src_pos,
									node.dst_pos,
									node.duration )
					self.__dwell_cbid = BigWorld.callback( node.dwell_time, func )
				else :
					self.__motor.move( node.src_pos,
										node.dst_pos,
										node.duration )
				if node.speech :
					rds.soundMgr.switchVoice( node.speech )			# 切换语音
				speed = self.__calcSpeed( node.src_pos, \
										node.dst_pos, \
										node.duration )
				dynMonitor.updateContent( node.content )
				dynMonitor.updateSpeed( speed )
				dynMonitor.updateMoveTime( node.duration )
				dynMonitor.updateDewllTime( node.dwell_time )
				dynMonitor.updatePlayingNode( self.__node_idx )

	def __calcSpeed( self, src, dst, duration ) :
		"""计算移动速度"""
		xs = ( dst[0] - src[0] ) / duration
		ys = ( dst[1] - src[1] ) / duration
		return math.sqrt( xs**2 + ys**2 )

	def setPlayMode( self, mode ) :
		"""播放模式"""
		assert mode in ["ALL", "NODE"], "Supported mode : [ ALL, NODE ]"
		self.__playMode = mode

	def playNode( self, index ) :
		"""播放某个节点"""
		node = nodesEditor.getNode( index )
		if node is None : return
		dynMonitor.startPlaying()
		self.__node_start_time = time.time()
		self.__node_idx = index
		self.__play_time = 0
		self.setPlayMode( "ALL" )
		self.__driveObj.pos = node.src_pos
		self.__onNodeArrive( node.src_pos )
		self.setPlayMode( "NODE" )

	def restart( self ) :
		"""从头播放"""
		start_node = nodesEditor.getNode( 0 )
		if start_node is None : return
		dynMonitor.startPlaying()
		self.__node_start_time = time.time()
		self.__node_idx = 0
		self.__play_time = 0
		self.__isPlaying = True
		self.setPlayMode( "ALL" )
		self.__driveObj.pos = start_node.src_pos
		self.__onNodeArrive( start_node.src_pos )
		self.playBgMusic()

	def play( self ) :
		"""开始播放"""
		self.restart()

	def pause( self ) :
		"""暂停"""
		dynMonitor.stopPlaying()
		dynMonitor.enterPause()
		self.__isPlaying = False
		self.__motor.shut()
		BigWorld.cancelCallback( self.__dwell_cbid )
		node = nodesEditor.getNode( self.__node_idx )
		passTime = time.time() - self.__node_start_time
		self.__node_play_time += passTime
		leaveDwellTime = node.dwell_time - self.__node_play_time
		leaveMoveTime = node.duration
		if leaveDwellTime > 0 :
			self.__pause_info["dwell_remain"] = leaveDwellTime
		else :
			leaveMoveTime -= self.__node_play_time - node.dwell_time
		self.__pause_info["duration"] = leaveMoveTime
		self.__pause_info["pause_pos"] = self.__driveObj.pos
		self.__play_time += passTime
		self.__node_start_time = 0
		self.stopBgMusic()
		dynMonitor.updatePlayTime( self.__play_time )				# 更新已经播放的时间

	def continueMove( self ) :
		"""继续移动"""
		dynMonitor.startPlaying()
		self.__isPlaying = True
		node = nodesEditor.getNode( self.__node_idx )
		dwell_time = self.__pause_info.get( "dwell_remain", 0 )
		src_pos = self.__pause_info.get( "pause_pos" )
		self.__driveObj.pos = src_pos
		duration = self.__pause_info.get( "duration", 0 )
		self.__node_start_time = time.time()
		if dwell_time > 0 :
			func = Functor( self.__motor.move,
							src_pos,
							node.dst_pos,
							duration )
			self.__dwell_cbid = BigWorld.callback( dwell_time, func )
		else :
			self.__motor.move( src_pos,
								node.dst_pos,
								duration )
		self.__pause_info = {}
		self.playBgMusic()

	def stop( self ) :
		"""停止播放"""
		self.__motor.shut()
		self.stopBgMusic()
		BigWorld.cancelCallback( self.__dwell_cbid )

	def destroy( self ) :
		"""结束播放"""
		self.__isPlaying = False
		self.__driveObj = None
		self.__motor.destroy()
		BigWorld.cancelCallback( self.__dwell_cbid )

	def releaseBgMusic( self ) :
		rds.soundMgr.lockBgPlay( False )					# 解锁背景音乐播放
		player = BigWorld.player()
		music = ""
		if player and player.isPlayer() :
			currArea = player.getCurrArea()
			if currArea :
				music = currArea.getMusic()
		rds.soundMgr.switchMusic( music )					# 音乐重设为玩家当前所在区域的音乐

	def playBgMusic( self ) :
		rds.soundMgr.lockBgPlay( False )					# 解锁背景音乐播放（因为这个是callback，为防止意外，这里再解锁一次）
		bgMusic = normalEditor.getOriginal( "bgMusic" )
		rds.soundMgr.switchMusic( bgMusic )					# 播放背景音乐
		rds.soundMgr.lockBgPlay( True )						# 锁定背景音乐播放

	def stopBgMusic( self ) :
		rds.soundMgr.lockBgPlay( False )					# 解锁背景音乐播放（因为这个是callback，为防止意外，这里再解锁一次）
		rds.soundMgr.switchMusic( "" )						# 播放背景音乐

	def isPlaying( self ) :
		"""是否正在播放"""
		return self.__isPlaying


class DynamicPanel( GUIBaseObject ) :
	"""动态信息面板"""
	def __init__( self, pnl ) :
		GUIBaseObject.__init__( self, pnl )
		self.__pyTxbPosX = TextBox( pnl.txb_currPosX.box )						# 当前位置X坐标
		self.__pyTxbPosX.readOnly = True
		self.__pyTxbPosY = TextBox( pnl.txb_currPosY.box )						# 当前位置Y坐标
		self.__pyTxbPosY.readOnly = True
		self.__pyTxbSpeed = TextBox( pnl.txb_speed.box )						# 当前移动速度
		self.__pyTxbSpeed.readOnly = True
		self.__pyTxbDwellTime = TextBox( pnl.txb_dwellTime.box )				# 当前节点停留时间
		self.__pyTxbDwellTime.readOnly = True
		self.__pyTxbMoveTime = TextBox( pnl.txb_moveTime.box )					# 当前节点移动时间
		self.__pyTxbMoveTime.readOnly = True
		self.__pyTxbPlayTime = TextBox( pnl.txb_playTime.box )					# 剧情已播放时间
		self.__pyTxbPlayTime.readOnly = True

	def updatePosition( self, pos ) :
		"""更新当前位置"""
		self.__pyTxbPosX.text = "%i" % pos[0]
		self.__pyTxbPosY.text = "%i" % pos[1]

	def updateSpeed( self, speed ) :
		self.__pyTxbSpeed.text = "%.1f" % speed

	def updateDewllTime( self, time ) :
		self.__pyTxbDwellTime.text = "%.2f" % time

	def updateMoveTime( self, time ) :
		self.__pyTxbMoveTime.text = "%.2f" % time

	def updatePlayTime( self, time ) :
		self.__pyTxbPlayTime.text = "%.2f" % time


class SceneInfoPanel( GUIBaseObject ) :
	"""剧情信息版面"""
	def __init__( self, pnl ) :
		GUIBaseObject.__init__( self, pnl )
		self.__sel_idx = -1
		self.__opMode = "UNLOAD"
		self.__tempOpMode = ""
		self.__pyElems = {}
		pyCfgPath = TextBox( pnl.txb_configPath.box )
		self.__pyElems["txb_configPath"] = pyCfgPath
		pyCfgPath.text = "entities/locale_default/config/client/SceneDatas.xml"

		pyBtnEdit = HButtonEx( pnl.btn_edit )
		pyBtnEdit.setExStatesMapping( UIState.MODE_R4C1 )
		pyBtnEdit.onLClick.bind( self.__onEnterEdit )
		self.__pyElems["btn_edit"] = pyBtnEdit

		pyBtnCancel = HButtonEx( pnl.btn_cancel )
		pyBtnCancel.setExStatesMapping( UIState.MODE_R4C1 )
		pyBtnCancel.onLClick.bind( self.__onAbandon )
		pyBtnCancel.visible = False
		self.__pyElems["btn_cancel"] = pyBtnCancel

		pyBtnSave = HButtonEx( pnl.btn_save )
		pyBtnSave.setExStatesMapping( UIState.MODE_R4C1 )
		pyBtnSave.onLClick.bind( self.__onSave )
		self.__pyElems["btn_save"] = pyBtnSave

		pyBtnLoad = HButtonEx( pnl.btn_load )
		pyBtnLoad.setExStatesMapping( UIState.MODE_R4C1 )
		pyBtnLoad.onLClick.bind( self.__onLoad )
		self.__pyElems["btn_load"] = pyBtnLoad

		pyBtnBuildScene = HButtonEx( pnl.btn_buildScene )
		pyBtnBuildScene.setExStatesMapping( UIState.MODE_R4C1 )
		pyBtnBuildScene.onLClick.bind( self.__onBuildScene )
		self.__pyElems["btn_buildScene"] = pyBtnBuildScene

		self.__pyCmbScenes = ODComboBox( pnl.cmb_sceneId )
		self.__pyCmbScenes.onItemLClick.bind( self.__onSceneItemClick )
		self.__pyCmbScenes.pyBox.text = ""

		self.__pyPnlNormal = NormalPanel( pnl.frame_baseInfo )
		self.__pyPnlNodes = NodesPanel( pnl.frame_sceneNode )
		self.changeOpMode( "UNLOAD" )

	def __onEnterEdit( self ) :
		self.__pyPnlNormal.changeOpMode( "EDIT" )
		self.__pyPnlNodes.changeOpMode( "EDIT" )
		self.changeOpMode( "EDIT" )

	def __onAbandon( self ) :
		def abandon() :
			self.__pyPnlNormal.abandon()
			self.__pyPnlNodes.abandon()
			self.changeOpMode( "READ" )
		if configEditor.isEdited() :
			def callback( res ) :
				if res == RS_OK : abandon()
			showMessage( "数据未保存，退出编辑将放弃此次修改，确定？", \
				"", MB_OK_CANCEL, callback, pyOwner = self )
		else :
			abandon()

	def __abandonBuild( self ) :
		"""取消创建"""
		def callback( res ) :
			if res != RS_OK : return
			configEditor.abandonBuild()
			self.__pyCmbScenes.removeItemOfIndex( self.__sel_idx )
			self.__sel_idx = -1
			self.__pyCmbScenes.selIndex = self.__sel_idx
			self.__seleceScene( self.__sel_idx )
		showMessage( "确定取消创建剧情？", "", \
			MB_OK_CANCEL, callback, pyOwner = self )

	def __onSave( self ) :
		self.__pyPnlNormal.save()
		self.__pyPnlNodes.save()
		configEditor.save()

	def __onLoad( self ) :
		cfg_path = self.__pyElems["txb_configPath"].text.strip()
		if cfg_path == "" :
			showMessage( "请输入配置路径", "", MB_OK, pyOwner = self )
			return
		if not configEditor.load( cfg_path ) :
			showMessage( "配置加载失败！", "", MB_OK, pyOwner = self )
			return
		sceneIds = [ str( id ) for id in configEditor.getAllScenes() ]
		self.__pyCmbScenes.clearItems()
		self.__pyCmbScenes.addItems( sceneIds )
		self.__pyCmbScenes.pyBox.text = "请选择"
		self.changeOpMode( "EMPTY" )

	def __onBuildScene( self ) :
		"""新建剧情"""
		def build() :
			if not configEditor.buildScene() :
				showMessage( "创建失败！", "", MB_OK, pyOwner = self )
			else :
				sceneId = normalEditor.getTemp( "sceneId" )
				self.__pyCmbScenes.addItem( str( sceneId ) )
				self.__pyCmbScenes.selItem = str( sceneId )
				self.__sel_idx = self.__pyCmbScenes.selIndex
				self.__seleceScene( self.__sel_idx )
				self.changeOpMode( "READ" )
		if configEditor.isEdited() :
			def callback( res ) :
				if res == RS_OK : build()
				else : self.__pyCmbScenes.selIndex = self.__sel_idx
			showMessage( "数据未保存，新建剧情将放弃此次修改，确定？", \
				"", MB_OK_CANCEL, callback, pyOwner = self )
		else :
			build()

	def __onSceneItemClick( self, index ) :
		"""点击某个剧情"""
		def select() :
			self.__sel_idx = index
			self.__seleceScene( index )
		if configEditor.isEdited() :
			def callback( res ) :
				if res == RS_OK : select()
				else : self.__pyCmbScenes.selIndex = self.__sel_idx
			showMessage( "数据未保存，退出编辑将放弃此次修改，确定？", \
				"", MB_OK_CANCEL, callback, pyOwner = self )
		else :
			select()

	def __seleceScene( self, index ) :
		if index == -1 :
			sceneId = None
		else :
			sceneId = int( self.__pyCmbScenes.items[ index ] )
		if configEditor.selectScene( sceneId ) :
			self.changeOpMode( "READ" )
		else :
			self.changeOpMode( "EMPTY" )
		self.__pyPnlNormal.onSceneSelected( sceneId )
		self.__pyPnlNodes.onSceneSelected( sceneId )
		self.pyTopParent.onSceneSelected( sceneId )

	def getSelNodeIdx( self ) :
		return self.__pyPnlNodes.getSelNodeIdx()

	def changeOpMode( self, mode ) :
		"""改变操作模式"""
		assert mode in ( "READ", "EDIT", "EMPTY", "PLAY", "UNLOAD" ), ""
		self.__opMode = mode
		self.__pyElems["btn_edit"].visible = mode in ( "READ", "EMPTY", "PLAY", "UNLOAD" )
		self.__pyElems["btn_cancel"].visible = mode in ( "EDIT", )
		self.__pyElems["btn_edit"].enable = mode in ( "READ", )
		self.__pyElems["btn_cancel"].enable = mode in ( "EDIT", )
		self.__pyElems["btn_save"].enable = mode in ( "EDIT", )
		self.__pyElems["btn_buildScene"].enable = mode in ( "READ", "EMPTY" )
		self.__pyElems["btn_load"].enable = mode in ( "READ", "EMPTY", "UNLOAD" )
		self.__pyCmbScenes.enable = mode in ( "READ", "EMPTY" )

	def onEnterPlaying( self ) :
		"""开始播放"""
		self.__pyPnlNormal.onEnterPlaying()
		self.__pyPnlNodes.onEnterPlaying()
		self.__tempOpMode = self.__opMode
		self.changeOpMode( "PLAY" )

	def onLeavePlaying( self ) :
		"""停止播放"""
		self.__pyPnlNormal.onLeavePlaying()
		self.__pyPnlNodes.onLeavePlaying()
		self.changeOpMode( self.__tempOpMode )

	def updatePlayingNode( self, index ) :
		"""更新播放节点信息"""
		self.__pyPnlNodes.updatePlayingNode( index )

	def onExit( self ) :
		"""退出"""
		self.changeOpMode( "EMPTY" )
		self.__pyPnlNormal.updateNormalInfo( {} )
		self.__pyPnlNodes.clearNodes()
		self.__pyPnlNormal.changeOpMode( "READ" )
		self.__pyPnlNodes.changeOpMode( "READ" )


class NormalPanel( GUIBaseObject ) :
	"""普通信息版面"""
	def __init__( self, pnl ) :
		GUIBaseObject.__init__( self, pnl )
		self.__opMode = "READ"
		self.__pyElems = {}
		self.__pyElems["bgMusic"] = TextBox( pnl.txb_bgMusic.box )
		self.__pyElems["txPath"] = TextBox( pnl.txb_txPath.box )
		self.__pyElems["txWidth"] = TextBox( pnl.txb_txWidth.box )
		self.__pyElems["txWidth"].inputMode = InputMode.INTEGER
		self.__pyElems["txHeight"] = TextBox( pnl.txb_txHeight.box )
		self.__pyElems["txHeight"].inputMode = InputMode.INTEGER
		self.changeOpMode( "READ" )

	def updateBgMusic( self, value ) :
		"""更新界面显示"""
		self.__pyElems["bgMusic"].text = str( value )

	def updateTxPath( self, value ) :
		"""更新界面显示"""
		self.__pyElems["txPath"].text = str( value )

	def updateTxWidth( self, value ) :
		"""更新界面显示"""
		self.__pyElems["txWidth"].text = "%i" % value

	def updateTxHeight( self, value ) :
		"""更新界面显示"""
		self.__pyElems["txHeight"].text = "%i" % value

	def updateNormalInfo( self, data ) :
		"""更新界面信息"""
		self.updateBgMusic( data.get( "bgMusic", "" ) )
		self.updateTxPath( data.get( "texture_path", "" ) )
		self.updateTxWidth( data.get( "texture_size", ( 0, 0 ) )[0] )
		self.updateTxHeight( data.get( "texture_size", ( 0, 0 ) )[1] )

	def fetchData( self ) :
		"""获取界面数据"""
		data = {}
		data["bgMusic"] = self.__pyElems["bgMusic"].text.strip()
		txWidth = self.__pyElems["txWidth"].text.strip()
		txHeight = self.__pyElems["txHeight"].text.strip()
		txWidth = 0 if txWidth == "" else int( txWidth )
		txHeight = 0 if txHeight == "" else int( txHeight )
		data["texture_size"] = ( txWidth, txHeight )
		data["texture_path"] = self.__pyElems["txPath"].text.strip()
		data["sceneId"] = normalEditor.getOriginal( "sceneId" )
		return data

	def save( self ) :
		"""保存界面数据"""
		data = self.fetchData()
		normalEditor.createTemp( data )
		normalEditor.save()
		self.pyTopParent.drawFresco( data[ "sceneId" ] )

	def changeOpMode( self, mode ) :
		"""改变操作模式"""
		assert mode in ( "READ", "EDIT" ), ""
		self.__opMode = mode
		self.__pyElems["bgMusic"].readOnly = mode in ["READ"]
		self.__pyElems["txPath"].readOnly = mode in ["READ"]
		self.__pyElems["txWidth"].readOnly = mode in ["READ"]
		self.__pyElems["txHeight"].readOnly = mode in ["READ"]

	def onSceneSelected( self, sceneId ) :
		"""选择一个剧情"""
		self.updateNormalInfo( normalEditor.copyOrgn() )
		self.changeOpMode( "READ" )

	def onEnterPlaying( self ) :
		"""开始播放"""
		data = self.fetchData()
		data["op_mode"] = self.__opMode
		normalEditor.createTemp( data )
		self.changeOpMode( "READ" )
		data = normalEditor.copyOrgn()
		self.updateNormalInfo( data )

	def onLeavePlaying( self ) :
		"""停止播放，恢复播放前的状态"""
		data = normalEditor.copyTemp()
		self.changeOpMode( data["op_mode"] )
		del data["op_mode"]
		normalEditor.createTemp( data )
		self.updateNormalInfo( data )

	def abandon( self ) :
		"""放弃修改"""
		data = normalEditor.copyOrgn()
		normalEditor.createTemp( {} )
		self.updateNormalInfo( data )
		self.changeOpMode( "READ" )


class NodesPanel( GUIBaseObject ) :
	"""节点信息版面"""
	def __init__( self, pnl ) :
		GUIBaseObject.__init__( self, pnl )
		self.__sel_idx = -1
		self.__pyElems = {}
		self.__temp_buffer = {}
		self.__pyElems["src_posX"] = TextBox( pnl.txb_srcPosX.box )
		self.__pyElems["src_posX"].inputMode = InputMode.INTEGER

		self.__pyElems["src_posY"] = TextBox( pnl.txb_srcPosY.box )
		self.__pyElems["src_posY"].inputMode = InputMode.INTEGER

		self.__pyElems["dst_posX"] = TextBox( pnl.txb_dstPosX.box )
		self.__pyElems["dst_posX"].inputMode = InputMode.INTEGER

		self.__pyElems["dst_posY"] = TextBox( pnl.txb_dstPosY.box )
		self.__pyElems["dst_posY"].inputMode = InputMode.INTEGER

		self.__pyElems["duration"] = TextBox( pnl.txb_duration.box )
		self.__pyElems["duration"].inputMode = InputMode.FLOAT

		self.__pyElems["dwell_time"] = TextBox( pnl.txb_dwellTime.box )
		self.__pyElems["dwell_time"].inputMode = InputMode.FLOAT

		self.__pyElems["speech"] = TextBox( pnl.txb_speechPath.box )

		self.__pyElems["content"] = CSMLRichTextBox( pnl.frame_content.clipPanel, pnl.frame_content.sbar )

		pyBtn = HButtonEx( pnl.btn_insertNode )
		pyBtn.setExStatesMapping( UIState.MODE_R4C1 )
		pyBtn.onLClick.bind( self.__onInsertNode )
		self.__pyElems["btn_insertNode"] = pyBtn

		pyBtn = HButtonEx( pnl.btn_delNode )
		pyBtn.setExStatesMapping( UIState.MODE_R4C1 )
		pyBtn.onLClick.bind( self.__onDelNode )
		self.__pyElems["btn_delNode"] = pyBtn

		pyBtn = HButtonEx( pnl.btn_updateNode )
		pyBtn.setExStatesMapping( UIState.MODE_R4C1 )
		pyBtn.onLClick.bind( self.__onAlterNode )
		self.__pyElems["btn_updateNode"] = pyBtn

		pyBtn = HButtonEx( pnl.btn_fetchPos )
		pyBtn.setExStatesMapping( UIState.MODE_R4C1 )
		pyBtn.onLClick.bind( self.__onFetchPos )
		self.__pyElems["btn_fetchPos"] = pyBtn

		pyBtn = Button( pnl.btn_moveToSrc )
		pyBtn.setStatesMapping( UIState.MODE_R2C2 )
		pyBtn.onLClick.bind( self.__onMoveToSrc )
		pyBtn.size = ( 20, 20 )
		pyBtn.tipFlag = 0
		pyBtn.onMouseEnter.bind( self.__onMouseEnter )
		pyBtn.onMouseLeave.bind( self.__onMouseLeave )
		self.__pyElems["btn_moveToSrc"] = pyBtn

		pyBtn = Button( pnl.btn_moveToDst )
		pyBtn.setStatesMapping( UIState.MODE_R2C2 )
		pyBtn.onLClick.bind( self.__onMoveToDst )
		pyBtn.size = ( 20, 20 )
		pyBtn.tipFlag = 1
		pyBtn.onMouseEnter.bind( self.__onMouseEnter )
		pyBtn.onMouseLeave.bind( self.__onMouseLeave )
		self.__pyElems["btn_moveToDst"] = pyBtn

		pyBtn = Button( pnl.btn_preNode )
		pyBtn.setStatesMapping( UIState.MODE_R2C2 )
		pyBtn.onLClick.bind( self.__onSelectFrontNode )
		self.__pyElems["btn_preNode"] = pyBtn

		pyBtn = Button( pnl.btn_nextNode )
		pyBtn.setStatesMapping( UIState.MODE_R2C2 )
		pyBtn.onLClick.bind( self.__onSelectRearNode )
		self.__pyElems["btn_nextNode"] = pyBtn

		self.__pyCmbNodes = ODComboBox( pnl.cmb_nodes )
		self.__pyCmbNodes.onItemLClick.bind( self.__onSelectNode )

		self.changeOpMode( "READ" )						# 只读模式

	def __updateNode( self, data ) :
		"""更新节点信息"""
		self.updateSrcPos( data.get( "src_pos", ( 0, 0 ) ) )
		self.updateDstPos( data.get( "dst_pos", ( 0, 0 ) ) )
		self.updateDuration( data.get( "duration", 0 ) )
		self.updateDwellTime( data.get( "dwell_time", 0 ) )
		self.updateContent( data.get( "content", "" ) )
		self.updateSpeech( data.get( "speech", "" ) )

	def __onSelectNode( self, index ) :
		"""点击某个剧情"""
		def select() :
			self.__sel_idx = index
			node = nodesEditor.getNode( index )
			if node :
				self.__updateNode( node.copyOrgn() )
			else :
				self.__updateNode( {} )
		if nodesEditor.isEdited( self.__sel_idx ) :
			def callback( res ) :
				if res == RS_OK : select()
				else : self.__pyCmbNodes.selIndex = self.__sel_idx
			showMessage( "节点数据未保存，另选节点将放弃此次修改，确定？", \
				"", MB_OK_CANCEL, callback, pyOwner = self )
		else :
			select()

	def __onInsertNode( self ) :
		if self.__opMode == "INSERT" : return
		if self.__sel_idx < 0 and len( self.__pyCmbNodes.items ) > 0 :
			showMessage( "请先选择一个节点", "", MB_OK, pyOwner = self )
			return
		self.changeOpMode( "INSERT" )
		node = nodesEditor.getNode( self.__sel_idx )
		data = {}
		if node :
			data["src_pos"] = node.dst_pos
		self.__updateNode( data )

	def __onDelNode( self ) :
		if self.__opMode == "DELETE" : return
		if self.__sel_idx is None or self.__sel_idx < 0 : return
		self.changeOpMode( "DELETE" )
		showMessage( "被删除的数据将不可恢复，确定删除当前节点请点击[保存]按钮", \
			"", MB_OK, pyOwner = self )

	def __onAlterNode( self ) :
		if self.__opMode == "UPDATE" : return
		if self.__sel_idx is None or self.__sel_idx < 0 : return
		self.changeOpMode( "UPDATE" )

	def __onFetchPos( self ) :
		if self.__pyElems["src_posX"].tabStop or \
			self.__pyElems["src_posY"].tabStop :
				self.updateSrcPos( self.pyTopParent.getFrescoPos() )
		elif self.__pyElems["dst_posX"].tabStop or \
			self.__pyElems["dst_posY"].tabStop :
				self.updateDstPos( self.pyTopParent.getFrescoPos() )
		else :
			showMessage( "请把输入焦点定位到位置信息框", "", MB_OK, pyOwner = self )

	def __onMoveToSrc( self ) :
		"""将贴图定位到起始位置点"""
		if self.__opMode == "PLAY" : return
		x = self.__pyElems["src_posX"].text.strip()
		y = self.__pyElems["src_posY"].text.strip()
		x = 0 if x == "" else int( x )
		y = 0 if y == "" else int( y )
		self.pyTopParent.setFrescoPos( ( x, y ) )

	def __onMoveToDst( self ) :
		"""将贴图定位到目标位置点"""
		if self.__opMode == "PLAY" : return
		x = self.__pyElems["dst_posX"].text.strip()
		y = self.__pyElems["dst_posY"].text.strip()
		x = 0 if x == "" else int( x )
		y = 0 if y == "" else int( y )
		self.pyTopParent.setFrescoPos( ( x, y ) )

	def __onSelectFrontNode( self ) :
		"""选择前一个节点"""
		if self.__sel_idx <= 0 : return
		self.__onSelectNode( self.__sel_idx - 1 )
		self.__pyCmbNodes.selIndex = self.__sel_idx

	def __onSelectRearNode( self ) :
		"""选择前一个节点"""
		if self.__sel_idx >= len( self.__pyCmbNodes.items ) - 1 : return
		self.__onSelectNode( self.__sel_idx + 1 )
		self.__pyCmbNodes.selIndex = self.__sel_idx

	# --------------------------------------------------
	def __onMouseEnter( self, pyElem ) :
		"""鼠标进入弹出提示"""
		dsp = _global_tips.get( pyElem.tipFlag )
		toolbox.infoTip.showToolTips( self, dsp )
		BigWorld.callback( 5, toolbox.infoTip.hide )

	def __onMouseLeave( self, pyElem ) :
		"""鼠标离开关闭提示"""
		toolbox.infoTip.hide()

	# --------------------------------------------------
	def updateSrcPos( self, value ) :
		"""更新"""
		self.__pyElems["src_posX"].text = "%i" % value[0]
		self.__pyElems["src_posY"].text = "%i" % value[1]

	def updateDstPos( self, value ) :
		"""更新"""
		self.__pyElems["dst_posX"].text = "%i" % value[0]
		self.__pyElems["dst_posY"].text = "%i" % value[1]

	def updateDuration( self, value ) :
		self.__pyElems["duration"].text = "%.2f" % value

	def updateDwellTime( self, value ) :
		self.__pyElems["dwell_time"].text = "%.2f" % value

	def updateContent( self, value ) :
		self.__pyElems["content"].text = str( value )

	def updateSpeech( self, value ) :
		self.__pyElems["speech"].text = str( value )

	# --------------------------------------------------
	def syncToEditor( self ) :
		self.__pyCmbNodes.clearItems()
		fmt = "%i(%i - %i)"
		nodes = []
		for idx, node in enumerate( nodesEditor.getNodes() ) :
			nodes.append( fmt % ( idx, node.src_pos[0], node.src_pos[1] ) )
		self.__pyCmbNodes.addItems( nodes )

	def clearNodes( self ) :
		self.__pyCmbNodes.clearItems()
		self.__updateNode( {} )
		self.__sel_idx = self.__pyCmbNodes.selIndex

	def onSceneSelected( self, sceneId ) :
		"""选择一个剧情"""
		self.clearNodes()
		self.syncToEditor()
		self.changeOpMode( "READ" )
		self.__pyCmbNodes.pyBox.text = "共%i个节点" % len( self.__pyCmbNodes.items )

	# --------------------------------------------------
	def save( self ) :
		if self.__opMode == "UPDATE" :
			data = self.fetchData()
			nodesEditor.alterNode( self.__sel_idx, data )
			self.syncToEditor()
			self.__pyCmbNodes.selIndex = self.__sel_idx
		elif self.__opMode == "INSERT" :
			data = self.fetchData()
			nodesEditor.insertNode( self.__sel_idx, data )
			self.__sel_idx += 1
			self.syncToEditor()
			self.__pyCmbNodes.selIndex = self.__sel_idx
		elif self.__opMode == "DELETE" :
			nodesEditor.removeNode( self.__sel_idx )
			self.__sel_idx -= 1
			self.syncToEditor()
			self.__onSelectNode( self.__sel_idx )
			self.__pyCmbNodes.selIndex = self.__sel_idx
		self.changeOpMode( "EDIT" )

	def abandon( self ) :
		"""放弃修改"""
		if self.__opMode == "UPDATE" :
			node = nodesEditor.getNode( self.__sel_idx )
			self.__updateNode( node.copyOrgn() )
		elif self.__opMode == "INSERT" :
			node = nodesEditor.getNode( self.__sel_idx )
			if node : self.__updateNode( node.copyOrgn() )
			else : self.__updateNode( {} )
		self.changeOpMode( "READ" )

	def fetchData( self ) :
		data = {}
		srcX = self.__pyElems["src_posX"].text.strip()
		srcY = self.__pyElems["src_posY"].text.strip()
		srcX = 0 if srcX == "" else int( srcX )
		srcY = 0 if srcY == "" else int( srcY )
		data["src_pos"] = ( srcX, srcY )

		dstX = self.__pyElems["dst_posX"].text.strip()
		dstY = self.__pyElems["dst_posY"].text.strip()
		dstX = 0 if dstX == "" else int( dstX )
		dstY = 0 if dstY == "" else int( dstY )
		data["dst_pos"] = ( dstX, dstY )

		data["duration"] = float( self.__pyElems["duration"].text.strip() )
		data["dwell_time"] = float( self.__pyElems["dwell_time"].text.strip() )
		data["content"] = self.__pyElems["content"].text.strip()
		data["speech"] = self.__pyElems["speech"].text.strip()

		return data

	def getSelNodeIdx( self ) :
		"""返回当前选中的节点索引"""
		return self.__pyCmbNodes.selIndex

	def changeOpMode( self, mode ) :
		"""改变操作模式"""
		assert mode in ( "PLAY", "EDIT", "READ", "UPDATE", "INSERT", "DELETE" ), ""
		self.__opMode = mode
		self.__pyElems["src_posX"].readOnly = mode in [ "PLAY", "READ", "EDIT", "DELETE" ]
		self.__pyElems["src_posY"].readOnly = mode in [ "PLAY", "READ", "EDIT", "DELETE" ]
		self.__pyElems["dst_posX"].readOnly = mode in [ "PLAY", "READ", "EDIT", "DELETE" ]
		self.__pyElems["dst_posY"].readOnly = mode in [ "PLAY", "READ", "EDIT", "DELETE" ]
		self.__pyElems["duration"].readOnly = mode in [ "PLAY", "READ", "EDIT", "DELETE" ]
		self.__pyElems["dwell_time"].readOnly = mode in [ "PLAY", "READ", "EDIT", "DELETE" ]
		self.__pyElems["speech"].readOnly = mode in [ "PLAY", "READ", "EDIT", "DELETE" ]
		self.__pyElems["content"].readOnly = mode in [ "PLAY", "READ", "EDIT", "DELETE" ]
		self.__pyElems["btn_insertNode"].enable = mode in [ "INSERT", "EDIT" ]
		self.__pyElems["btn_delNode"].enable = mode in [ "EDIT", "DELETE" ]
		self.__pyElems["btn_updateNode"].enable = mode in [ "UPDATE", "EDIT" ]
		self.__pyElems["btn_fetchPos"].enable = mode in [ "UPDATE", "INSERT", "EDIT" ]
		self.__pyElems["btn_moveToSrc"].enable = mode in [ "READ", "UPDATE", "INSERT", "EDIT" ]
		self.__pyElems["btn_moveToDst"].enable = mode in [ "READ", "UPDATE", "INSERT", "EDIT" ]
		self.__pyElems["btn_preNode"].enable = mode in [ "UPDATE", "EDIT", "READ", ]
		self.__pyElems["btn_nextNode"].enable = mode in [ "UPDATE", "EDIT", "READ", ]
		self.__pyCmbNodes.enable = mode in [ "UPDATE", "EDIT", "READ", ]

	def onEnterPlaying( self ) :
		"""开始播放"""
		data = self.fetchData()
		data["op_mode"] = self.__opMode
		self.__temp_buffer = data
		self.changeOpMode( "PLAY" )

	def onLeavePlaying( self ) :
		"""停止播放，恢复播放前的状态"""
		data = self.__temp_buffer
		self.changeOpMode( data["op_mode"] )
		self.__updateNode( data )
		self.__pyCmbNodes.selIndex = self.__sel_idx
		self.__temp_buffer = {}

	def updatePlayingNode( self, index ) :
		"""播放时"""
		self.__pyCmbNodes.selIndex = index
		node = nodesEditor.getNode( index )
		self.__updateNode( node.copyOrgn() )


class DynMonitor( object ) :

	def __init__( self ) :
		object.__init__( self )
		self.__screen = None
		self.__observers = []

	def bindScreen( self, screen ) :
		self.__screen = screen

	def bindObserver( self, observer ) :
		self.__observers.append( observer )

	def updatePosition( self, pos ) :
		"""更新当前位置"""
		self.__screen.updatePosition( pos )

	def updateSpeed( self, speed ) :
		self.__screen.updateSpeed( speed )

	def updateDewllTime( self, time ) :
		self.__screen.updateDewllTime( time )

	def updateMoveTime( self, time ) :
		self.__screen.updateMoveTime( time )

	def updatePlayTime( self, time ) :
		self.__screen.updatePlayTime( time )

	def startPlaying( self ) :
		for obs in self.__observers :
			obs.onEnterPlaying()

	def stopPlaying( self ) :
		for obs in self.__observers :
			obs.onLeavePlaying()

	def enterPause( self ) :
		for obs in self.__observers :
			obs.onPause()

	def updatePlayingNode( self, index ) :
		"""通知移动到了某个节点"""
		for obs in self.__observers :
			obs.updatePlayingNode( index )

	def updateContent( self, text ) :
		for obs in self.__observers :
			obs.updateContent( text )

	def destroy( self ) :
		self.__screen = None
		self.__observers = []

class ConfigEditor( object ) :
	"""配置编辑器，保存、修改，加载配置"""
	def __init__( self ) :
		object.__init__( self )
		self.__config_path = ""
		self.__configSect = None											# 配置加载的资源
		self.__selectSect = None											# 选择的剧情资源
		self.__newSceneSect = None											# 新建的剧情资源

	def load( self, cfgPath ) :
		"""加载配置"""
		self.release()
		cfgSect = ResMgr.openSection( cfgPath )
		if cfgSect is None : return False
		self.__configSect = cfgSect
		self.__config_path = cfgPath
		return True

	def getAllScenes( self ) :
		"""返回所有剧情ID"""
		return [s.readInt( "id" ) for s in self.__configSect.values()]

	def selectScene( self, sceneId ) :
		"""选择某个剧情"""
		if self.__configSect is None : return False
		for scene in self.__configSect.values() :
			if scene.readInt( "id" ) == sceneId :
				self.__selectSect = scene
				normalEditor.init( scene )
				nodesEditor.init( scene["segments"] )
				return True
		else :
			normalEditor.init( None )
			nodesEditor.init( None )
			return False

	def buildScene( self ) :
		"""创建新剧情"""
		if self.__configSect is None : return False
		ids =  self.getAllScenes()
		if len( ids ) == 0 :
			sceneId = 0
		else :
			sceneId = max( ids ) + 1
		sect = self.__configSect.createSection( "Scene%i" % sceneId )
		sect.writeInt( "id", sceneId )
		sect.writeString( "bgMusic", "" )
		txSect = sect.createSection( "texture" )
		txSect.writeInt( "width", 0 )
		txSect.writeInt( "height", 0 )
		txSect.writeString( "path", "" )
		segSect = sect.createSection( "segments" )
		normalEditor.buildScene( sect )
		nodesEditor.buildScene( segSect )
		self.__newSceneSect = sect
		return True

	def abandonBuild( self ) :
		if self.__newSceneSect is None : return
		self.__configSect.deleteSection( self.__newSceneSect.asString )
		normalEditor.init( None )
		nodesEditor.init( None )
		self.__newSceneSect = None

	def setNormalTemp( self, attr, value ) :
		"""设置临时数据"""
		normalEditor.setTemp( attr, value )

	def setNodeTemp( self, node, attr, value ) :
		"""设置节点临时数据"""
		self.__nodesEditor.setTemp( node, attr, value )

	def isEdited( self ) :
		"""是否有未保存数据"""
		return normalEditor.isEdited() or nodesEditor.isEdited()

	def save( self ) :
		"""保存修改的数据"""
		normalEditor.save()
		nodesEditor.save()
		self.__configSect.save()

	def release( self ) :
		"""释放资源"""
		if self.__config_path :
			ResMgr.purge( self.__config_path )


class NormalEditor( object ) :
	"""普通数据编辑器，贴图的路径，尺寸，背景音乐等"""
	def __init__( self ) :
		object.__init__( self )
		self.__sect = None
		self.__temp_info = {}
		self.__orgn_info = {}

	def init( self, sect ) :
		self.__sect = sect
		self.__temp_info = {}
		self.__orgn_info = {}
		if sect is None : return
		self.__orgn_info["bgMusic"] = sect.readString( "bgMusic" )
		if sect.has_key( "texture" ) :
			self.__orgn_info["texture_size"] = ( sect["texture"]["width"].asInt,\
				sect["texture"]["height"].asInt )
			self.__orgn_info["texture_path"] = sect["texture"]["path"].asString
		self.__orgn_info["sceneId"] = sect["id"].asInt

	def createTemp( self, temp ) :
		self.__temp_info = temp

	def buildScene( self, sect ) :
		"""新建剧情"""
		self.__sect = sect
		self.__temp_info["bgMusic"] = sect.readString( "bgMusic" )
		if sect.has_key( "texture" ) :
			self.__temp_info["texture_size"] = ( sect["texture"]["width"].asInt,\
				sect["texture"]["height"].asInt )
			self.__temp_info["texture_path"] = sect["texture"]["path"].asString
		self.__temp_info["sceneId"] = sect["id"].asInt

	def save( self ) :
		"""保存修改的数据"""
		bgMusic = self.__temp_info.get( "bgMusic" )
		if bgMusic is not None :
			self.__sect.writeString( "bgMusic", bgMusic )
		texture_size = self.__temp_info.get( "texture_size" )
		if texture_size is not None :
			if not self.__sect.has_key( "texture" ) :
				self.__sect.createSection( "texture" )
			self.__sect["texture"].writeInt( "width", texture_size[0] )
			self.__sect["texture"].writeInt( "height", texture_size[1] )
		texture_path = self.__temp_info.get( "texture_path" )
		if texture_path is not None :
			if not self.__sect.has_key( "texture" ) :
				self.__sect.createSection( "texture" )
			self.__sect["texture"].writeString( "path", texture_path )
		sceneId = self.__temp_info.get( "secneId" )
		if sceneId is not None :
			self.__sect.writeInt( "id", sceneId )
		self.init( self.__sect )
		self.__temp_info = {}

	def getTemp( self, name ) :
		"""获取临时编辑的数据"""
		return self.__temp_info.get( name )

	def setTemp( self, name, value ) :
		"""设置临时编辑的数据"""
		self.__temp_info[name] = value

	def getOriginal( self, name ) :
		"""获取原始数据"""
		return self.__orgn_info.get( name )

	def getTxInfo( self ) :
		"""获取贴图信息"""
		txInfo = TextureInfo()
		txInfo.init( self.__sect["texture"] )
		return txInfo

	def copyTemp( self ) :
		return self.__temp_info.copy()

	def copyOrgn( self ) :
		return self.__orgn_info.copy()

	def isEdited( self ) :
		"""是否有修改的数据"""
		return len( self.__temp_info ) and self.__temp_info != self.__orgn_info

	def release( self ) :
		"""释放资源"""
		self.__sect = None
		self.__temp_info = {}
		self.__orgn_info = {}


class NodesEditor( object ) :
	"""节点编辑器，增加，删除，修改节点"""
	def __init__( self ) :
		object.__init__( self )
		self.__sect = None
		self.__nodes = []

	def init( self, sect ) :
		"""初始化"""
		self.__sect = sect
		self.__nodes = []
		if sect is None : return
		temp = {}
		for segment in sect.values() :
			node = MSceneNode( segment )
			temp[ node.src_pos ] = node
		vertexs = self.getVertexs( temp )
		print ">>>> All src_pos:", vertexs[0]
		print ">>>> All dst_pos:", vertexs[1]
		src_pos = vertexs[0]
		while temp.has_key( src_pos ) :
			node = temp.get( src_pos )
			self.__nodes.append( node )
			src_pos = node.dst_pos

	@staticmethod
	def getVertexs( nodes ) :
		"""检查节点数据的完整性"""
		src_poss = set( nodes.keys() )
		dst_poss = set( [n.dst_pos for n in nodes.values()] )
		start_pos = src_poss - dst_poss
		tail_pos = dst_poss - src_poss
		result = [ None, None ]
		if len( start_pos ) == 1 :
			result[0] = list( start_pos )[0]
		elif len( start_pos ) > 1 :
			result[0] = tuple( start_pos )
			print( ">>>>> More than 1 start nodes found! Please check the config." )
		elif len( start_pos ) == 0 :
			print( ">>>>> Can't find start node! Please check the config." )
		if len( tail_pos ) == 1 :
			result[1] = list( tail_pos )[0]
		elif len( tail_pos ) > 1 :
			result[1] = tuple( tail_pos )
			print( ">>>>> More than 1 tail nodes found! Please check the config." )
		elif len( tail_pos ) == 0 :
			print( ">>>>> Can't find tail node! Please check the config." )
		return result

	def buildScene( self, sect ) :
		"""新建剧情"""
		self.init( sect )

	def createNode( self, data ) :
		"""创建一个新节点，并用给定的数据进行初始化"""
		node = MSceneNode( None )
		node.createTemp( data )
		node.save()
		return node

	def appendNode( self, data ) :
		"""在末尾追加节点"""
		if len( self.__nodes ) > 0 :
			tail = self.getNode( -1, True )
			tail.setTemp( "dst_pos", data["src_pos"] )				# 前置节点直接链接到后继节点
			tail.save()
		self.__nodes.append( self.createNode( data ) )

	def removeNode( self, index ) :
		"""移除节点"""
		if index not in ( 0, -1, len( self.__nodes ) - 1, -len( self.__nodes ) ) :	# 头尾节点判断
			frontNode = self.getNode( index - 1 )
			rearNode = self.getNode( index + 1 )
			frontNode.setTemp( "dst_pos", rearNode.src_pos )				# 前置节点直接链接到后继节点
			frontNode.save()
		del self.__nodes[ index ]

	def insertNode( self, index, data ) :
		"""在index之后插入节点"""
		frontNode = self.getNode( index )
		rearNode = self.getNode( index + 1 )
		if frontNode :
			frontNode.setTemp( "dst_pos", data["src_pos"] )
			frontNode.save()
		if rearNode is not None :
			rearNode.setTemp( "src_pos", data["dst_pos"] )
			rearNode.save()
		self.__nodes.insert( index + 1, self.createNode( data ) )

	def alterNode( self, index, data ) :
		"""更改节点"""
		frontNode = self.getNode( index - 1 )
		rearNode = self.getNode( index + 1 )
		if frontNode is not None :
			frontNode.setTemp( "dst_pos", data["src_pos"] )
			frontNode.save()
		if rearNode is not None :
			rearNode.setTemp( "src_pos", data["dst_pos"] )
			rearNode.save()
		node = self.getNode( index )
		node.createTemp( data )
		node.save()

	def getNodeByPos( self, pos ) :
		"""根据起始位置获取节点"""
		for node in self.__nodes :
			if node.src_pos == pos :
				return node
		return None

	def getNode( self, index, reverse = False ) :
		"""根据索引获取节点
		@param 	 reverse : 是否允许反转查找"""
		if len( self.__nodes ) <= index : return None
		if reverse :
			if index < -len( self.__nodes ) : return None
		else :
			if index < 0 : return None
		return self.__nodes[index]

	def getNodes( self ) :
		"""获取所有节点"""
		return self.__nodes[:]

	def createTemp( self, index, temp ) :
		""""""
		node = self.getNode( index )
		if node : node.createTemp( temp )

	def getTemp( self, index, name ) :
		"""获取临时编辑的数据"""
		node = self.getNode( index )
		if node : node.getTemp( name )

	def setTemp( self, index, name, value ) :
		"""设置临时编辑的数据"""
		node = self.getNode( index )
		if node : node.setTemp( name, value )

	def saveNode( self, index ) :
		"""保存节点"""
		node = self.getNode( index )
		if node : node.save()

	def save( self ) :
		"""保存配置"""
		for name, sect in self.__sect.items() :
			self.__sect.deleteSection( name )
		for node in self.__nodes :
			node.save()
			sect = self.__sect.createSection( "node" )
			sect.writeVector2( "src_pos", node.getOriginal( "src_pos" ) )
			sect.writeVector2( "dst_pos", node.getOriginal( "dst_pos" ) )
			sect.writeFloat( "duration", node.getOriginal( "duration" ) )
			sect.writeFloat( "dwell_time", node.getOriginal( "dwell_time" ) )
			sect.writeString( "content", node.getOriginal( "content" ) )
			sect.writeString( "speech", node.getOriginal( "speech" ) )

	def isEdited( self, index = None ) :
		"""是否有被编辑过的节点"""
		if index is None :
			for node in self.__nodes :
				if node.isEdited() : return True
		else :
			node = self.getNode( index )
			if node : return node.isEdited()
		return False

	def release( self ) :
		"""释放资源"""
		self.__sect = None
		self.__nodes = []


class MSceneNode( object ) :
	"""剧情节点"""
	def __init__( self, sect ) :
		object.__init__( self )
		self.__temp_info = {}
		self.__orgn_info = {}
		self.init( sect )

	def init( self, sect ) :
		self.__orgn_info = {}
		if sect is None : return
		self.__orgn_info["src_pos"] = tuple( sect.readVector2( "src_pos" ) )
		self.__orgn_info["dst_pos"] = tuple( sect.readVector2( "dst_pos" ) )
		self.__orgn_info["duration"] = sect.readFloat( "duration" )
		self.__orgn_info["dwell_time"] = sect.readFloat( "dwell_time" )
		self.__orgn_info["content"] = sect.readString( "content" )
		self.__orgn_info["speech"] = sect.readString( "speech" )

	def createTemp( self, temp ) :
		self.__temp_info = temp

	def save( self ) :
		"""保存修改的数据"""
		tmp = self.__temp_info.get( "src_pos" )
		if tmp is not None :
			self.__orgn_info["src_pos"] = tmp
		tmp = self.__temp_info.get( "dst_pos" )
		if tmp is not None :
			self.__orgn_info["dst_pos"] = tmp
		tmp = self.__temp_info.get( "duration" )
		if tmp is not None :
			self.__orgn_info["duration"] = tmp
		tmp = self.__temp_info.get( "dwell_time" )
		if tmp is not None :
			self.__orgn_info["dwell_time"] = tmp
		tmp = self.__temp_info.get( "content" )
		if tmp is not None :
			self.__orgn_info["content"] = tmp
		tmp = self.__temp_info.get( "speech" )
		if tmp is not None :
			self.__orgn_info["speech"] = tmp
		self.__temp_info = {}

	def getTemp( self, name ) :
		"""获取临时编辑的数据"""
		return self.__temp_info.get( name )

	def setTemp( self, name, value ) :
		"""设置临时编辑的数据"""
		self.__temp_info[name] = value

	def getOriginal( self, name ) :
		"""获取原始数据"""
		return self.__orgn_info.get( name )

	def copyTemp( self ) :
		return self.__temp_info.copy()

	def copyOrgn( self ) :
		return self.__orgn_info.copy()

	def isEdited( self ) :
		"""是否有未保存的数据"""
		return len( self.__temp_info ) and self.__temp_info != self.__orgn_info

	@property
	def src_pos( self ) :
		return self.getOriginal( "src_pos" )

	@property
	def dst_pos( self ) :
		return self.getOriginal( "dst_pos" )

	@property
	def duration( self ) :
		return self.getOriginal( "duration" )

	@property
	def dwell_time( self ) :
		return self.getOriginal( "dwell_time" )

	@property
	def content( self ) :
		return self.getOriginal( "content" )

	@property
	def speech( self ) :
		return self.getOriginal( "speech" )


dynMonitor = DynMonitor()
configEditor = ConfigEditor()
nodesEditor = NodesEditor()
normalEditor = NormalEditor()


# 保存操作时数据完整性检查（未实现）

