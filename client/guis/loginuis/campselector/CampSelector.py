# -*- coding: gb18030 -*-
#
# $Id: RoleCreator.py,v 1.33 2008-08-26 02:20:43 huangyongwei Exp $

"""
implement role creator class
"""

import csdefine
import event.EventCenter as ECenter
from LoginMgr import roleCreator
from guis import *
from guis.loginuis import *
from guis.common.RootGUI import RootGUI
from guis.common.PyGUI import PyGUI
from guis.common.Window import Window
from guis.controls.StaticText import StaticText
from guis.controls.SelectableButton import SelectableButton
#from guis.controls.SelectorGroup import SelectorGroup
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.CSRichText import CSRichText
from LabelGather import labelGather
from config.client.msgboxtexts import Datas as mbmsgs
import random
import Font
import MessageBox

class CampSelector( RootGUI ) :
	"""
	阵营选择界面
	"""
	_camp_videos = {csdefine.ENTITY_CAMP_TAOISM:"", csdefine.ENTITY_CAMP_DEMON:""}
	
	_unit_width = 64.0
	
	def __init__( self ):
		wnd = GUI.load( "guis/loginuis/campselector/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.h_dockStyle = "HFILL"
		self.v_dockStyle = "VFILL"
		self.focus = False
		self.moveFocus = False
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_   = False
		self.__triggers = {}
		self.__pyMsgBox = None
		self.__cbids = []
		self.__registerTriggers()
		self.__initialize( wnd )
		self.__camp = 0
	
	def __initialize( self, wnd ):
		self.__pyStTitle = StaticText( wnd.stTitle )
		self.__pyStTitle.h_dockStyle = "CENTER"
		self.__pyStTitle.v_dockStyle = "S_TOP"
		labelGather.setPyLabel( self.__pyStTitle, "LoginDialog:CampSelector", "title" )
		
		self.__pyFadeText = CSRichText( wnd.fadeText)		# 阵营渐变说明
		self.__pyFadeText.h_dockStyle = "CENTER"
		self.__pyFadeText.v_dockStyle = "S_TOP"
		self.__pyFadeText.align = "L"
		self.__initContent( "MSYHBD.TTF", 14 )
		
		self.__pyBtnQuit = HButtonEx( wnd.btnQuit )
		self.__pyBtnQuit.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnQuit.h_dockStyle = "S_RIGHT"
		self.__pyBtnQuit.v_dockStyle = "S_BOTTOM"
		labelGather.setPyBgLabel( self.__pyBtnQuit, "LoginDialog:CampSelector", "btnQuit" )
		self.__pyBtnQuit.onLClick.bind( self.__onQuit )
		
		box = wnd.okCancelBox
		self.__pyOkCancelBox = PyGUI( box )
		self.__pyOkCancelBox.h_dockStyle = "S_CENTER"
		self.__pyOkCancelBox.v_dockStyle = "BOTTOM"
		self.__pyOkCancelBox.visible = False
		
		self.__pyMsgPanel = CSRichText( box.msgPanel )
		self.__pyMsgPanel.opGBLink = True
		self.__pyMsgPanel.font = "MSYHBD.TTF"
		self.__pyMsgPanel.fontSize = 14.0
		self.__pyMsgPanel.top = 50.0
		self.__pyMsgPanel.foreColor = (255,248,158,255)
		#self.__pyMsgPanel.limning = Font.LIMN_NONE
		
		self.__pyOkBtn = HButtonEx( box.okBtn, self )					# 确定按钮
		self.__pyOkBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyOkBtn.onLClick.bind( self.__onOk )
		self.__pyOkBtn.h_dockStyle = "CENTER"
		self.__pyOkBtn.v_dockStyle = "BOTTOM"
		
		self.__pyCancelBtn = HButtonEx( box.cancelBtn, self )			# 取消按钮
		self.__pyCancelBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyCancelBtn.onLClick.bind( self.__hideMsg )
		self.__pyCancelBtn.h_dockStyle = "CENTER"
		self.__pyCancelBtn.v_dockStyle = "BOTTOM"

		labelGather.setPyBgLabel( self.__pyOkBtn, "MsgBox:ocBox", "btnOk" )
		labelGather.setPyBgLabel( self.__pyCancelBtn, "MsgBox:ocBox", "btnCancel" )
				
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_CAMP_SELECTOR_SHOW"] = self.__onShow
		self.__triggers["EVT_ON_ROLE_CREATOR_SHOW"] = self.__onHide
		self.__triggers["EVT_ON_KICKOUT_OVERTIME"]  = self.__onHide
		self.__triggers["EVT_ON_ROLECREATOR_CAMP_CHANGED"] = self.__onCampSelected	# 阵营改变触发
		self.__triggers["EVT_ON_RESOLUTION_CHANGED"] = self.__onResolutionChanged
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )
	# ------------------------------------------------------------------
	def __initContent( self, font, fontSize ) :
		""""""
		self.__pyFadeText.font = font
		self.__pyFadeText.fontSize = fontSize
	
	def __onShow( self ):
		"""
		显示
		"""
		self.__setFocus( True )
		if self.__pyBtnQuit:
			self.__pyBtnQuit.visible = True
		#for item in self.__pyCampBtns.values():
		#	item.visible = True
		if self.__pyStTitle:
			self.__pyStTitle.visible = True
		self.__pyOkCancelBox.visible = False
		self.show()
	
	def __onHide( self ):
		"""
		隐藏
		"""
		self.hide()
	
	def __onCampChanged( self, camp ):
		"""
		阵营改变，播放阵营视频
		"""
		videoName = self._camp_videos.get( camp )
		if videoName is None:return
		rds.gameMgr.playVideo( videoName )
	
	def __onResolutionChanged( self, preReso ):
		"""
		分辨率改变
		"""
		#for campBtn in self.__pyCampBtns.values():
		#	pyText = campBtn.pyText_
		#	pyText.center = campBtn.center
		#	pyText.top = campBtn.bottom
#		self.__layoutStarts()
	
	def __onMouseEnter( self, pyCamp ):
		camp = pyCamp.camp
		pyCamp.text = labelGather.getText( "LoginDialog:CampSelector", "camp_%d"%camp )
	
	def __onMouseLeave( self, pyCamp ):
		if pyCamp.selected:
			return
		pyCamp.text = ""
	
	def __onCampSelected( self, pyCamp ):
		camp = pyCamp
		self.__pyFadeText.text = roleCreator.getCampDesp( camp )
		self.__camp = camp
		self.__deleyFadeText()
		rds.soundMgr.stopVoice()
		voice = roleCreator.getCampVoice( camp )
		if len( voice ) > 0:
			rds.soundMgr.playVoice( voice )
		msg = mbmsgs[0x0e22]%labelGather.getText( "LoginDialog:CampSelector", "camp_%d"%camp )
		self.__pyOkCancelBox.visible = True
		self.__pyMsgPanel.text = msg
	
	def __onOk( self, pyBtn ):
		"""
		"""
		self.hide()
		self.__pyOkCancelBox.visible = False
		roleCreator.startEnterRoleCreator( self.__camp )
	
	def __hideMsg( self, pyBtn ):
		"""
		"""
		self.__clear()
		if self.__pyBtnQuit:
			self.__pyBtnQuit.visible = True
		self.__pyOkCancelBox.visible = False
		rds.roleCreator.cancelSelectedCamp()
	
	def __onQuit( self, pyBtn ):
		"""
		退出
		"""
		def query( id ) :
			if id == RS_OK :
				self.hide()
				if rds.roleSelector.getRoleCount() > 0:		#返回角色选择
					rds.roleCreator.cancel()
				else:
					rds.roleCreator.cancelSelectCamp()
					
		msg = mbmsgs[0x0e23]
		if self.__pyMsgBox:
			self.__pyMsgBox.visible = False
			self.__pyMsgBox = None
		self.__pyMsgBox = showMessage( msg, "", MB_OK_CANCEL, query )
	
	def __setFocus( self, focus ):
		"""
		设置focus
		"""
		#for campBtn in self.__pyCampBtns.values():
		#	campBtn.focus = focus
		#	campBtn.crossFocus = focus
		self.__pyFadeText.crossFocus = focus
		self.__pyFadeText.focus = focus
	
	def __deleyFadeText( self ):
		"""
		排序说明
		"""
		lineInfos = self.__pyFadeText.lineInfos_
		hideTime = 0
		delayTime = 0
		for idx, elemInfo in enumerate( lineInfos ) :
			fader = GUI.AlphaShader()							# 渐显 Shader
			fader.value = 0
			fader.speed = 1.5
			fader.reset()
			for pyElem in elemInfo[1]:							# 给行中的每个元素添加一个渐显 shader
				pyElem.gui.addShader( fader )
			func = Functor( self.__lineByLineShow, fader )
			cbid = BigWorld.callback( delayTime, func )			# 启用渐显 callback
			self.__cbids.append( cbid )
			delayTime += 0.0   #默认为2秒

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
		self.__pyFadeText.clear()
	
	def __layoutStarts( self ):
		"""
		分配星空
		"""
		width = BigWorld.screenWidth()
		height = BigWorld.screenHeight()
		wIdxs = int( width/self._unit_width )
		hIdxs = int( height/self._unit_width )
		for wIdx in range( wIdxs ):
			for hIdx in range( hIdxs ):
				num = random.choice( [8,9,10] )
				startPos = ( self._unit_width*wIdx, self._unit_width*hIdxs )
				endPos = ( self._unit_width*( wIdx + 1 ), self._unit_width*( hIdxs + 1 ) )
				
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )
		
	def show( self ) :
		#for pySelector in self.__pyCampGroup.pySelectors:
		#	pySelector.selected = False
		self.__pyFadeText.text = ""
		self.__layoutStarts()
		RootGUI.show( self )

	def hide( self ) :
		RootGUI.hide( self )
