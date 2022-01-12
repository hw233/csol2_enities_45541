# -*- coding: gb18030 -*-
#
# $Id: EidolonWindow.py,v 1.20 2009-12-29 16:16:16 pengju Exp $

import Define
import time
import random
import BigWorld
from bwdebug import *
from guis import *
from guis.common.Window import Window
from guis.common.FrameEx import HVFrameEx
from guis.controls.Control import Control
from guis.controls.Button import Button
from guis.tooluis.CSRichText import CSRichText
from config.client.help import LoadingHints
from LabelGather import labelGather

class EidolonWindow( Window ):
	"""
	创世精灵界面
	"""
	__c_msg_show_detect_dbid = 0	# 更换提示内容callback
	__c_eff_show_detect_dbid = 0	# 眨眼callback
	__cc_reset_time = 10			# 更换提示内容的时间
	def __init__( self ) :
		wnd = GUI.load( "guis/general/eidolonwindow/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L3
		self.escHide_ = False
		self.focus = False
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "BOTTOM"
		self.__msgs = []
		self.__eidolon = wnd.eidolon_eff	# 精灵眨眼动画
		self.__eidolon.stopAt = 0			# 眨眼动画停留的帧，为0则停在第一帧，为-1则开始播放所有帧
		self.__canShow = True				# 创世精灵能否显示，显示过后就不能显示了
		self.__initialize( wnd )

		self.__triggers = {}
		self.__registerTriggers()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		self.__msgPanel = HVFrameEx( wnd.msgPanel ) # 消息底框，根据消息的多少改变面板高度

		self.__pyMsg = CSRichText( wnd.msgPanel.rtMsg ) # 消息框
		self.__pyMsg.focus = True
		self.__pyMsg.onLMouseDown.bind( self.__onLMouseDownMsg )
		self.__pyMsg.maxWidth = 210.0
		self.__pyMsg.text = ""

		self.__pycloseBtn = Button( wnd.closeBtn ) # 关闭按钮
		self.__pycloseBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pycloseBtn.onLClick.bind( self.__hide )

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setPyBgLabel( self.__pycloseBtn, "EidolonWindow:main", "closeBtn" )

	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ENTITY_HP_CHANGED"] = self.__onHPChanged		# 血量改变时调用
		self.__triggers["EVT_ON_ROLE_ENTER_WORLD"] = self.__onRoleEnterWorld
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __onHPChanged( self, entity, hp, hpMax, oldValue ) :
		"""
		血量改变时调用
		"""
		if self.visible and entity == BigWorld.player() and \
			hp < hpMax / 10 and oldValue > hpMax / 10 :
			self.__showMessage( hpChange = True )

	def __showMessage( self, hpChange = False ) :
		"""
		显示内容
		"""
		if hpChange :
			self.__pyMsg.text = labelGather.getText( "EidolonWindow:main", "HPTooLess" )
		else :
			self.__pyMsg.text = self.__getMsg()
		self.__changeHeight()
		BigWorld.cancelCallback( EidolonWindow.__c_msg_show_detect_dbid )
		EidolonWindow.__c_msg_show_detect_dbid = BigWorld.callback( EidolonWindow.__cc_reset_time, self.__showMessage )

	def __getMsg( self ):
		"""
		取得消息内容
		"""
		if len(self.__msgs)==0 :
			self.__msgs = LoadingHints.Datas.values()				#存放所有的信息提示(id,item)
			random.shuffle( self.__msgs )
		return "@S{4}" + self.__msgs.pop()

	def __showEidolonEff( self ) :
		"""
		显示精灵眨眼效果
		"""
		time = random.randint( 1, 10 )
		self.__eidolon.stopAt = -1
		BigWorld.callback( 0.3, self.__stopEff )
		BigWorld.cancelCallback( EidolonWindow.__c_eff_show_detect_dbid )
		EidolonWindow.__c_eff_show_detect_dbid = BigWorld.callback( time, self.__showEidolonEff )

	def __stopEff( self ) :
		"""
		停止眨眼
		"""
		self.__eidolon.stopAt = 0

	def __changeHeight( self ) :
		"""
		根据消息的多少改变面板高度
		"""
		panelHeight = 53 			# 默认信息面板高度
		msgMoreHeight = 28			# 信息底部离面板底部的高度
		wndMoreHeight = 70			# 面板底部离窗口底部的高度
		bottom = self.bottom	# 窗口的底部不变，这里先暂存，后面再赋给窗口

		if self.__pyMsg.height + msgMoreHeight > panelHeight : # 改变高度
			self.__msgPanel.height = self.__pyMsg.height + msgMoreHeight
			self.height = self.__msgPanel.height + wndMoreHeight
			self.__pycloseBtn.bottom = self.__msgPanel.bottom - 5
			self.bottom = bottom
		else :
			self.__msgPanel.height = panelHeight
			self.height = self.__msgPanel.height + wndMoreHeight
			self.__pycloseBtn.bottom = self.__msgPanel.bottom - 5
			self.bottom = bottom
	
	def __onLMouseDownMsg( self, mods ):
		"""
		"""
		self.focus = True
		self.onLMouseDown_( mods )

	def __hide( self ) :
		"""
		隐藏并且释放
		"""
		self.hide()
		self.__pyMsg.text = ""
		BigWorld.cancelCallback( EidolonWindow.__c_msg_show_detect_dbid )
		BigWorld.cancelCallback( EidolonWindow.__c_eff_show_detect_dbid )
		self.__eidolon.stopAt = 0
		self.__canShow = False

	def __onRoleEnterWorld( self, player ) :
		self.__canShow = True

	def onLMouseDown_( self, mods ) :
		Window.onLMouseDown_( self, mods )
		self.__pyMsg.focus = False
		
	def onLMouseUp_( self, mods ) :
		Window.onLMouseUp_( self, mods )
		self.__pyMsg.focus = True
		self.focus = False

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, evtMacro, *args ) :
		self.__triggers[ evtMacro ]( *args )

	def isMouseHit( self ) :
		return self.__msgPanel.isMouseHit()

	def hide( self ) :
		"""
		只隐藏窗口
		"""
		Window.hide( self )

	def show( self ) :
		Window.show( self )
		self.__showMessage()
		self.__showEidolonEff()

	def afterStatusChanged( self, oldStatus, newStatus ) :
		if newStatus == Define.GST_IN_WORLD and self.__canShow :
			self.show()
		else :
			self.hide()

	def onLeaveWorld( self ) :
		self.__hide()
