# -*- coding: gb18030 -*-
#
# $Id: MsgBox.py,v 1.9 2008-08-26 02:22:08 huangyongwei Exp $

"""
implement messagebox class
-- 2006/05/10: writen by huangyongwei
"""

import weakref
import MessageBox
from guis import *
from guis.common.FlexExWindow import HVFlexExWindow
from guis.common.FrameEx import HVFrameEx
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from AbstractTemplates import Singleton
from LabelGather import labelGather
import event.EventCenter as ECenter
from guis.OpIndicatorObj import OpIndicatorObj
import Font

class MsgBox( HVFlexExWindow ) :
	__cg_boxes		   = []									# 保存所有的消息框
	__cg_preshow_boxes = {}									# 保存在某种状态下将要显示的窗口
	__cg_tmphide_boxes = []									# 跳转时，临时保存当前处于显示状态下的消息提示框

	__cc_text_spacing		= 4

	def __init__( self, box ) :
		HVFlexExWindow.__init__( self, box )
		self.__initialize( box )							# 初始化
		self.posZSegment = ZSegs.L2							# 设置默认为第二级
		self.escHide_ = True								# 可以按 esc 键关闭
		self.activable_ = True								# 可以被激活
		self.addToMgr( "messageBox" )						# 添加到管理器
		self.h_dockStyle = "CENTER"							# 水平居中显示
		self.v_dockStyle = "MIDDLE"							# 垂直居中显示
		self.minHeight_ = 151.0								# 设置最小高度

		self.__pyBinder = None
		self.__callback = None								# 回调
		self.defRes_ = MessageBox.RS_OK						# 默认返回结果

		MsgBox.__cg_boxes.append( self )					# 添加到全局列表

	def dispose( self ) :
		"""
		release resource
		"""
		self.__pyBinder = None
		self.__callback = None										# 删除对 callback 的引用
		if self in MsgBox.__cg_boxes :
			MsgBox.__cg_boxes.remove( self )						# 从全局列表清除
		for state, pyBoxes in MsgBox.__cg_preshow_boxes.items() :	# 从预显示列表中删除
			pyBoxes = MsgBox.__cg_preshow_boxes[state]
			if self in pyBoxes :
				pyBoxes.remove( self )
			if len( pyBoxes ) == 0 :
				MsgBox.__cg_preshow_boxes.pop( state )
		if self in MsgBox.__cg_tmphide_boxes :
			MsgBox.__cg_tmphide_boxes.remove( self )
		HVFlexExWindow.dispose( self )


	def __del__( self ) :
		HVFlexExWindow.__del__( self )
		if Debug.output_del_MessageBox :
			INFO_MSG( str( self ) )

	# -------------------------------------------------
	def __initialize( self, box ) :
		if box is None : return
		self.__pyLbMsg = StaticText( box.lbMsg )						# 短消息文本
		self.__pyLbMsg.text = ""
		maxWidth = box.msgPanel.width
		self.pyMsgPanel_ = CSRichText( box.msgPanel )					# 长消息文本板面
		self.pyMsgPanel_.opGBLink = True
		self.pyMsgPanel_.maxWidth = maxWidth
		self.pyMsgPanel_.font = "MSYHBD.TTF"
		self.pyMsgPanel_.fontSize = 14.0
		self.pyMsgPanel_.foreColor = ( 51, 76, 97, 255 )
		self.pyMsgPanel_.limning = Font.LIMN_NONE
		self.pyMsgPanel_.opGBLink = True
		self.pyBgPanel_ = None
		if hasattr( box, "panel" ):
			self.pyBgPanel_ = HVFrameEx( box.panel )
			self.pyBgPanel_.center = self.width/2.0

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def notifyCallback_( self, resultID ) :
		"""
		回调 callback
		"""
		if self.__callback is not None :
			try :
				self.__callback( resultID )
			except :
				EXCEHOOK_MSG()

	def reposition_( self ) :
		"""
		重新设置窗口位置
		"""
		self.r_center = 0
		self.r_middle = 0


	# ----------------------------------------------------------------
	# callbacks
	# ---------------------------------------------------------------
	def onLeaveWorld( self ) :
		"""
		当角色离开世界时被调用
		注：这里重写 onLeaveWorld 方法在设计上是不对的，因为 MessageBox 与是否在世界中，无关。
		    这里这么写是为了角色退出游戏时，方便隐藏弹出窗口
		"""
		if self.pyOwner is None :						# 如果有父窗口的话，leave world 时，它会被父窗口 dispose，因此这里不需要再调用一次
			self.notifyCallback_( self.defRes_ )		# 用默认点击结果通知
			self.dispose()

	def afterStatusChanged( self, oldStatus, newStatus ) :
		"""
		当游戏状态改变时被调用
		@param					onStatus  : 改变前的状态（在 Define.py 中定义）
		@param					newStatus : 改变后的状态（在 Define.py 中定义）
		"""
		if oldStatus == newStatus : return
		if newStatus == Define.GST_SPACE_LOADING :
			for pyBox in MsgBox.__cg_boxes :
				if pyBox.gui.visible :
					pyBox.gui.visible = False
					self.__cg_tmphide_boxes.append( pyBox )
		elif newStatus == Define.GST_BACKTO_ROLESELECT_LOADING:
			for pyBox in MsgBox.__cg_boxes :
				if pyBox.gui.visible :
					pyBox.gui.visible = False
		else :
			for pyBox in MsgBox.__cg_tmphide_boxes :
				pyBox.gui.visible = True

		pyBoxes = MsgBox.__cg_preshow_boxes.get( newStatus, None )
		if pyBoxes is not None :
			for pyBox in pyBoxes :
				HVFlexExWindow.show( pyBox )
			MsgBox.__cg_preshow_boxes.pop( newStatus )


	# ----------------------------------------------------------------
	# public
	# ---------------------------------------------------------------
	def show( self, msg, title, callback, pyOwner, gstStatus = None ) :
		"""
		显示消息框
		"""
		if pyOwner :												# 控制只显示一个提示框
			for pyBox in self.__cg_boxes :
				if pyBox == self :
					continue
				if pyBox.__class__ != self.__class__ :
					continue
				if pyBox.pyBinder is None :
					continue
				if pyBox.pyBinder == pyOwner :
					pyBox.hide()
		self.title = title
		self.setMessage( msg )
		self.__callback = callback
		self.reposition_()
		if pyOwner :
			self.__pyBinder = weakref.ref( pyOwner )

		currStatus = rds.statusMgr.currStatus()
		if gstStatus is None or currStatus == gstStatus :
			HVFlexExWindow.show( self, pyOwner )
		elif gstStatus in MsgBox.__cg_preshow_boxes :
			MsgBox.__cg_preshow_boxes[gstStatus].append( self )
		else :
			MsgBox.__cg_preshow_boxes[gstStatus] = [self]

	def hide( self ) :
		"""
		隐藏窗口
		"""
		self.notifyCallback_( self.defRes_ )			# 用默认点击结果通知
		self.setOkButton( None ) #add by wuxo 2012-5-17
		self.setCancelButton( None ) #add by wuxo 2012-5-17
		self.dispose()

	def setMessage( self, msg ) :
		"""
		设置消息文本
		"""
		self.pyMsgPanel_.text = msg
		lineCount = self.pyMsgPanel_.lineCount
		if lineCount == 1 :
			self.pyMsgPanel_.align = "C"
			self.pyMsgPanel_.bottom = self.height/2.0
			if self.pyBgPanel_:
				self.pyMsgPanel_.middle = self.pyBgPanel_.middle
		else:
			self.pyMsgPanel_.align = "L"
			if lineCount >= 4:
				self.pyMsgPanel_.top = 45.0
			else:
				self.pyMsgPanel_.top = 55.0
			if self.pyBgPanel_:
				disHeight = self.pyMsgPanel_.height + ( self.pyMsgPanel_.top - self.pyBgPanel_.top )*2
				if disHeight > self.pyBgPanel_.height:
					self.pyBgPanel_.height =  disHeight
				self.height =  self.pyBgPanel_.bottom + 30.0# 消息过长时自动拉长，最短已经用了minHeight_做限制了

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getBinder( self ) :
		if self.__pyBinder is None :
			return None
		return self.__pyBinder()

	def _setVisible( self, visible ) :
		if visible :
			HVFlexExWindow._setVisible( self, visible )
		else :
			self.hide()


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyBinder = property( _getBinder )
	visible = property( HVFlexExWindow._getVisible, _setVisible )


# --------------------------------------------------------------------
# implement ok messagebox class
# --------------------------------------------------------------------
class OkBox( MsgBox ) :
	"""
	确定消息框
	"""
	def __init__( self, box = None ) :
		if box is None :
			box = GUI.load( "guis/tooluis/messagebox/okbox.gui" )
			uiFixer.firstLoadFix( box )
		MsgBox.__init__( self, box )
		self.__pyOkBtn = HButtonEx( box.okBtn, self )					# ok 按钮
		self.__pyOkBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyOkBtn.onLClick.bind( self.hide )
		self.__pyOkBtn.v_dockStyle = "BOTTOM"
		self.setOkButton( self.__pyOkBtn )

		self.defRes_ = MessageBox.RS_OK

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyOkBtn, "MsgBox:oBox", "btnOk" )

	def dispose( self ) :
		self.__pyOkBtn.dispose()
		MsgBox.dispose( self )
	
	def show( self, msg, title, callback, pyOwner, gstStatus = None ) :
		"""
		显示消息框
		"""
		MsgBox.show( self, msg, title, callback, pyOwner, gstStatus )
		if self.pyBgPanel_:
			self.__pyOkBtn.top = self.pyBgPanel_.bottom - 2.0

# --------------------------------------------------------------------
# implement cancel messagebox class
# --------------------------------------------------------------------
class CancelBox( MsgBox ) :
	"""
	取消消息框	20089-01-13 SongPeifang
	"""
	def __init__( self, box = None ) :
		if box is None :
			box = GUI.load( "guis/tooluis/messagebox/cancelbox.gui" )
			uiFixer.firstLoadFix( box )
		MsgBox.__init__( self, box )
		self.__pyCancelBtn = HButtonEx( box.cancelBtn, self )					# cancel 按钮
		self.__pyCancelBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyCancelBtn.onLClick.bind( self.hide )
		self.__pyCancelBtn.v_dockStyle = "BOTTOM"
		self.setCancelButton( self.__pyCancelBtn )

		self.defRes_ = MessageBox.RS_CANCEL

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyCancelBtn, "MsgBox:cBox", "btnCancel" )

	def dispose( self ) :
		self.__pyCancelBtn.dispose()
		MsgBox.dispose( self )

	def show( self, msg, title, callback, pyOwner, gstStatus = None ) :
		"""
		显示消息框
		"""
		MsgBox.show( self, msg, title, callback, pyOwner, gstStatus )
		if self.pyBgPanel_:
			self.__pyCancelBtn.top = self.pyBgPanel_.bottom

# --------------------------------------------------------------------
# implement special cancel messagebox class
# --------------------------------------------------------------------
class SpecialCancelBox( MsgBox ) :
	"""
	特殊的取消消息框	20089-01-13 SongPeifang
	加这个是因为，策划要求钓鱼的时候有一个窗口取消钓鱼
	这个几乎和上面的CancelBox功能完全一样，只是加载的gui不一样
	仅留下了取消按钮，并且策划要求这个消息框要非常小
	并且会在消息后面自动加上闪动的“...”
	"""
	def __init__( self ) :
		box = GUI.load( "guis/tooluis/messagebox/specialCancelBox.gui" )
		uiFixer.firstLoadFix( box )
		MsgBox.__init__( self, box )
		self.__pyCancelBtn = Button( box.cancelBtn, self )	# cancel 按钮
		self.__pyCancelBtn.setStatesMapping( UIState.MODE_R3C1 )
		self.__pyCancelBtn.onLClick.bind( self.hide )
		self.setCancelButton( self.__pyCancelBtn )
		self.defRes_ = MessageBox.RS_SPE_CANCEL

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyCancelBtn, "MsgBox:scBox", "btnCancel" )

	def reposition_( self ) :
		"""
		重新设置窗口位置
		设置到吟唱条下面居中
		"""
		MsgBox.reposition_( self )
		self.r_top = -0.31
		self.r_left = -0.09

	def dispose( self ) :
		self.__pyCancelBtn.dispose()
		MsgBox.dispose( self )

# --------------------------------------------------------------------
# implement ok-cancel messagebox class
# --------------------------------------------------------------------
class OkCancelBox( MsgBox, OpIndicatorObj ) :
	"""
	确定/取消消息框
	"""
	def __init__( self, box = None ) :
		if box is None :
			box = GUI.load( "guis/tooluis/messagebox/okcancelbox.gui" )
			uiFixer.firstLoadFix( box )
		MsgBox.__init__( self, box )
		OpIndicatorObj.__init__( self )
		self.__pyOkBtn = HButtonEx( box.okBtn, self )					# 确定按钮
		self.__pyOkBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyOkBtn.onLClick.bind( self.onOk_ )
		self.__pyOkBtn.v_dockStyle = "BOTTOM"

		self.__pyCancelBtn = HButtonEx( box.cancelBtn, self )			# 取消按钮
		self.__pyCancelBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyCancelBtn.onLClick.bind( self.hide )
		self.__pyCancelBtn.v_dockStyle = "BOTTOM"

		self.setOkButton( self.__pyOkBtn )							# 设置默认的回车按钮
		self.setCancelButton( self.__pyCancelBtn )					# 设置默认的 esc 按钮

		self.defRes_ = MessageBox.RS_CANCEL							# 默认结果为 cancel

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyOkBtn, "MsgBox:ocBox", "btnOk" )
		labelGather.setPyBgLabel( self.__pyCancelBtn, "MsgBox:ocBox", "btnCancel" )
		
	def _initOpIndicationHandlers( self ) :
		"""
		"""
		trigger = ( "gui_visible","okCancelBox" )
		condition = ( "quest_uncompleted","checkNotHasVehicle" )
		idtIds = rds.opIndicator.idtIdsOfCmd( condition, trigger )
		for i in idtIds :
			self._opIdtHandlers[i] = self.__showIndication
	
	def __showIndication( self, idtId ):
		pyBtn = self.__pyOkBtn
		toolbox.infoTip.showHelpTips( idtId, pyBtn )
		self.addVisibleOpIdt( idtId )

	def dispose( self ) :
		self.__pyOkBtn.dispose()
		self.__pyCancelBtn.dispose()
		if hasattr(rds.ruisMgr,"okCancelBox"):
			del rds.ruisMgr.okCancelBox
		MsgBox.dispose( self )

	def show( self, msg, title, callback, pyOwner, gstStatus = None ) :
		"""
		显示消息框
		"""
		MsgBox.show( self, msg, title, callback, pyOwner, gstStatus )
		if self.pyBgPanel_:
			self.__pyOkBtn.top = self.pyBgPanel_.bottom - 2.0
			self.__pyCancelBtn.top = self.pyBgPanel_.bottom - 2.0
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def onOk_( self ) :
		"""
		当确定按钮被点击时调用
		"""
		self.notifyCallback_( MessageBox.RS_OK )
		self.dispose()
		
	def onMove_( self, dx, dy ) :
		self.relocateIndications()

# --------------------------------------------------------------------
# implement yes-no messagebox class
# --------------------------------------------------------------------
class YesNoBox( MsgBox ) :
	"""
	是/否消息框
	"""
	def __init__( self, box = None ) :
		if box is None :
			box = GUI.load( "guis/tooluis/messagebox/yesnobox.gui" )
			uiFixer.firstLoadFix( box )
		MsgBox.__init__( self, box )
		self.__pyYesBtn = HButtonEx( box.yesBtn, self )					# 是 按钮
		self.__pyYesBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyYesBtn.onLClick.bind( self.onYes_ )
		self.__pyYesBtn.v_dockStyle = "BOTTOM"
		self.setOkButton( self.__pyYesBtn )

		self.__pyNoBtn = HButtonEx( box.noBtn, self )						# 否 按钮
		self.__pyNoBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyNoBtn.onLClick.bind( self.hide )
		self.__pyNoBtn.v_dockStyle = "BOTTOM"

		self.setOkButton( self.__pyYesBtn )								# 设置默认的回车按钮
		self.setCancelButton( self.__pyNoBtn )							# 设置默认的 esc 按钮

		self.defRes_ = MessageBox.RS_NO									# 默认返回结果为否

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyYesBtn, "MsgBox:ynBox", "btnYes" )
		labelGather.setPyBgLabel( self.__pyNoBtn, "MsgBox:ynBox", "btnNo" )

	def dispose( self ) :
		self.__pyYesBtn.dispose()
		self.__pyNoBtn.dispose()
		MsgBox.dispose( self )

	def show( self, msg, title, callback, pyOwner, gstStatus = None ) :
		"""
		显示消息框
		"""
		MsgBox.show( self, msg, title, callback, pyOwner, gstStatus )
		if self.pyBgPanel_:
			self.__pyYesBtn.top = self.pyBgPanel_.bottom - 2.0
			self.__pyNoBtn.top = self.pyBgPanel_.bottom - 2.0

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def onYes_( self ) :
		"""
		是按钮被点击时调用
		"""
		self.notifyCallback_( MessageBox.RS_YES )
		self.dispose()


# --------------------------------------------------------------------
# implement yes-no messagebox class
# --------------------------------------------------------------------
class YesNoCancelBox( MsgBox ) :
	"""
	是/否取消消息框
	"""
	def __init__( self, box = None ) :
		if box is None :
			box = GUI.load( "guis/tooluis/messagebox/yesnocancelbox.gui" )
			uiFixer.firstLoadFix( box )
		MsgBox.__init__( self, box )
		self.__pyYesBtn = HButtonEx( box.yesBtn, self )					# 是 按钮
		self.__pyYesBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyYesBtn.onLClick.bind( self.onYes_ )
		self.__pyYesBtn.v_dockStyle = "BOTTOM"
		self.setOkButton( self.__pyYesBtn )

		self.__pyNoBtn = HButtonEx( box.noBtn, self )						# 否 按钮
		self.__pyNoBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyNoBtn.onLClick.bind( self.onNo_ )
		self.__pyNoBtn.v_dockStyle = "BOTTOM"

		self.__pyCancelBtn = HButtonEx( box.cancelBtn, self )				# 否 按钮
		self.__pyCancelBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyCancelBtn.onLClick.bind( self.hide )
		self.__pyCancelBtn.v_dockStyle = "BOTTOM"

		self.setOkButton( self.__pyYesBtn )								# 设置默认的回车按钮
		self.setCancelButton( self.__pyNoBtn )							# 设置默认的 esc 按钮

		self.defRes_ = MessageBox.RS_CANCEL								# 默认结果为取消

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyYesBtn, "MsgBox:yncBox", "btnYes" )
		labelGather.setPyBgLabel( self.__pyNoBtn, "MsgBox:yncBox", "btnNo" )
		labelGather.setPyBgLabel( self.__pyCancelBtn, "MsgBox:yncBox", "btnCancel" )

	def dispose( self ) :
		self.__pyYesBtn.dispose()
		self.__pyNoBtn.dispose()
		self.__pyCancelBtn.dispose()
		MsgBox.dispose( self )


	def show( self, msg, title, callback, pyOwner, gstStatus = None ) :
		"""
		显示消息框
		"""
		MsgBox.show( self, msg, title, callback, pyOwner, gstStatus )
		if self.pyBgPanel_:
			self.__pyYesBtn.top = self.pyBgPanel_.bottom - 2.0
			self.__pyNoBtn.top = self.pyBgPanel_.bottom - 2.0
			self.__pyCancelBtn.top = self.pyBgPanel_.bottom - 2.0
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def onYes_( self ) :
		"""
		是按钮被点击时调用
		"""
		self.notifyCallback_( MessageBox.RS_YES )
		self.dispose()

	def onNo_( self ) :
		"""
		否按钮被点击时调用
		"""
		self.notifyCallback_( MessageBox.RS_NO )
		self.dispose()

# --------------------------------------------------------------------
# implement special ok-cancel messagebox class
# --------------------------------------------------------------------
class SpecialOkCancelBox( MsgBox ) :
	"""
	特殊确定/取消消息框（主要用于延迟传送）
	"""
	def __init__( self, box = None ) :
		if box is None :
			box = GUI.load( "guis/tooluis/messagebox/specialokcancelbox.gui" )
			uiFixer.firstLoadFix( box )
		MsgBox.__init__( self, box )
		self.__pyOkBtn = HButtonEx( box.okBtn, self )					# 立刻传送按钮
		self.__pyOkBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyOkBtn.onLClick.bind( self.onOk_ )
		self.__pyOkBtn.v_dockStyle = "BOTTOM"

		self.__pyCancelBtn = HButtonEx( box.cancelBtn, self )			# 取消传送按钮
		self.__pyCancelBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyCancelBtn.onLClick.bind( self.hide )
		self.__pyCancelBtn.v_dockStyle = "BOTTOM"

		self.setOkButton( self.__pyOkBtn )							# 设置默认的回车按钮
		self.setCancelButton( self.__pyCancelBtn )					# 设置默认的 esc 按钮

		self.defRes_ = MessageBox.RS_SPE_CAN						# 默认结果为 cancel
		player = BigWorld.player()
		self.delayTime = player.delayTeleportTime

		self.__triggers = {}
		self.__registerTriggers()

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyOkBtn, "MsgBox:speOCBox", "btnOk", self.delayTime )
		labelGather.setPyBgLabel( self.__pyCancelBtn, "MsgBox:speOCBox", "btnCancel" )

	def dispose( self ) :
		self.delayTime = 0
		self.__pyOkBtn.dispose()
		self.__pyCancelBtn.dispose()
		MsgBox.dispose( self )

	def show( self, msg, title, callback, pyOwner, gstStatus = None ) :
		"""
		显示消息框
		"""
		MsgBox.show( self, msg, title, callback, pyOwner, gstStatus )
		if self.pyBgPanel_:
			self.__pyOkBtn.top = self.pyBgPanel_.bottom + 2.0
			self.__pyCancelBtn.top = self.pyBgPanel_.bottom + 2.0

		BigWorld.callback( 1.0, self.delayTimeChanged_ )

	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def setMessage( self, msg ) :
		"""
		设置消息文本
		"""
		self.pyMsgPanel_.text = msg
		lineCount = self.pyMsgPanel_.lineCount
		if lineCount == 1 :
			self.pyMsgPanel_.align = "C"
			self.pyMsgPanel_.bottom = self.height/2.0
			if self.pyBgPanel_:
				self.pyMsgPanel_.middle = self.pyBgPanel_.middle
		else:
			self.pyMsgPanel_.align = "L"
			if lineCount >= 4:
				self.pyMsgPanel_.top = 55.0
			else:
				self.pyMsgPanel_.top = 65.0
			if self.pyBgPanel_:
				disHeight = self.pyMsgPanel_.height + ( self.pyMsgPanel_.top - self.pyBgPanel_.top )*2
				if disHeight > self.pyBgPanel_.height:
					self.pyBgPanel_.height =  disHeight
				self.pyBgPanel_.gui.elements["light_effect"].size.y = self.pyBgPanel_.height - 2.0
				self.height =  self.pyBgPanel_.bottom +50.0# 消息过长时自动拉长，最短已经用了minHeight_做限制了

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		"""
		注册事件
		"""
		self.__triggers["EVT_ON_HIDE_SPE_OCBOX"]	 =  self.__onHide	 # 隐藏界面
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def onOk_( self ) :
		"""
		当确定按钮被点击时调用
		"""
		self.notifyCallback_( MessageBox.RS_SPE_OK )
		self.dispose()

	# ----------------------------------------------------------------
	def delayTimeChanged_( self ):
		"""
		延迟时间改变
		"""
		if self.delayTime < 0: return
#		if not self.visible: return
		self.delayTime -= 1
		labelGather.setPyBgLabel( self.__pyOkBtn, "MsgBox:speOCBox", "btnOk", self.delayTime )
		BigWorld.callback( 1.0, self.delayTimeChanged_ )

	def __onHide( self ):
		"""
		隐藏界面，中断传送
		"""
		if self.delayTime < 0: return
		self.hide()