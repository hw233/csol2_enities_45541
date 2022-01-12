# -*- coding: gb18030 -*-
#

"""
pick Reiki window
"""

import os
import hashlib
import Define
import event.EventCenter as ECenter
import MessageBox
from AbstractTemplates import Singleton
from gbref import rds
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.common.RootGUI import RootGUI
from guis.controls.ButtonEx import HButtonEx
from guis.controls.ListPanel import ListPanel
from guis.tooluis.CSRichText import CSRichText
from config.client.msgboxtexts import Datas as mbmsgs
from AbstractTemplates import Singleton
import random
REIKI_PICK_TOTAL_RATING_0 = 28
REIKI_PICK_TOTAL_RATING_1 = 25
REIKI_PICK_TOTAL_RATING_2 = 20
REIKI_PICK_CONTINUOUS_NUM = 15

class ReikiPick( RootGUI, Singleton ) :
	"""
	灵气拾取界面
	"""
	__instance = None
	
	def __init__( self ) :
		assert ReikiPick.__instance is None,"ReikiPick instance has been created"
		ReikiPick.__instance = self
		wnd = GUI.load( "guis/otheruis/reikipick/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.focus = False
		self.moveFocus = False
		self.escHide_ = False
		self.h_dockStyle = "HFILL"
		self.v_dockStyle = "VFILL"
		self.__pyRichTexts = {"left":{},"right":{}}
		self.__triggers = {}
		self.__initialize( wnd )
		self.addToMgr( "reikiPick" )

	def __del__(self):
		"""
		just for testing memory leak
		"""
		if Debug.output_del_DamageStatis :
			INFO_MSG( str( self ) )
			
	# --------------------------------------------------
	# pravite
	# --------------------------------------------------
	def __initialize( self, wnd ):
		self.__fader = wnd.fader
		self.__pyRtTitle = CSRichText( wnd.topTitle )
		self.__pyRtTitle.h_dockStyle = "S_CENTER"
		self.__pyRtTitle.v_dockStyle = "S_TOP"
		self.__pyRtTitle.align = "C"
		self.__pyRtTitle.font = "MSYHBD.TTF"
		self.__pyRtTitle.fontSize = 40.0
		self.__pyRtTitle.text = ""
		
		leftPanel = wnd.leftPanel
		self.__pyLeftPanel = PyGUI( leftPanel )
		self.__pyLeftPanel.h_dockStyle = "S_LEFT"
		self.__pyLeftPanel.v_dockStyle = "S_TOP"
		for name, item in leftPanel.children:
			if not name.startswith( "richText"):continue
			index = int( name.split("_")[1] )
			pyRichText = CSRichText( item )
			pyRichText.align = "L"
			pyRichText.font = "MSYHBD.TTF"
			pyRichText.fontSize = 24.0
			pyRichText.text = ""
			if not index in self.__pyRichTexts["left"]:
				self.__pyRichTexts["left"].update( {index:pyRichText} )
			else:
				self.__pyRichTexts["left"][index]= pyRichText
			
		rightPanel = wnd.rightPanel
		self.__pyRightPanel = PyGUI( rightPanel )
		self.__pyRightPanel.h_dockStyle = "S_RIGHT"
		self.__pyRightPanel.v_dockStyle = "S_TOP"
		for name, item in rightPanel.children:
			if not name.startswith( "richText"):continue
			index = int( name.split("_")[1] )
			pyRichText = CSRichText( item )
			pyRichText.align = "L"
			pyRichText.font = "MSYHBD.TTF"
			pyRichText.fontSize = 24.0
			pyRichText.text = ""
			if not index in self.__pyRichTexts["right"]:
				self.__pyRichTexts["right"].update( {index:pyRichText} )
			else:
				self.__pyRichTexts["right"][index]= pyRichText
		
		bottomPanel = wnd.bottomPanel
		self.__pyBottomPanel = PyGUI( bottomPanel )
		self.__pyBottomPanel.h_dockStyle = "S_CENTER"
		self.__pyBottomPanel.v_dockStyle = "S_BOTTOM"
		
		self.__pyRtTotal = CSRichText( bottomPanel.rtTotal )
		self.__pyRtTotal.align = "L"
		self.__pyRtTotal.font = "MSYHBD.TTF"
		self.__pyRtTotal.fontSize = 24.0
		self.__pyRtTotal.text = ""
		
		self.__pyBtnStart = HButtonEx( bottomPanel.btnStart )
		self.__pyBtnStart.onLClick.bind( self.__onStart )
		self.__pyBtnStart.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnStart.visible = False
		labelGather.setPyBgLabel( self.__pyBtnStart, "ReikiPick:main", "btnStart" )
		
		self.__pyBtnOk = HButtonEx( bottomPanel.btnOk )
		self.__pyBtnOk.onLClick.bind( self.__onOk )
		self.__pyBtnOk.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOk.visible = False
		labelGather.setPyBgLabel( self.__pyBtnOk, "ReikiPick:main", "btnOk" )
		
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onStart( self , pyBtn ):
		"""
		开始
		"""
		if pyBtn is None:return
		player = BigWorld.player()
		player.pickAnima_reqStart()
	
	def __onOk( self, pyBtn ):
		"""
		确定退出
		"""
		if pyBtn is None:return
		BigWorld.player().pickAnima_confirmQuitSpace()
		self.onReikiEnd()

	def __onLostControl( self ) :
		self.enable = False

	def __onGotControl( self ) :
		self.enable = True
		
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self ) :
		self.__fader.value = 1
		RootGUI.show( self )

	def hide( self ) :
		RootGUI.hide( self )
	
	def onLeaveWorld( self ):
		for pyRichText in self.__pyRichTexts["left"].values():
			pyRichText.text = ""
		for pyRichText in self.__pyRichTexts["right"].values():
			pyRichText.text = ""
		self.__pyRtTitle.text = ""
		self.__pyRtTotal.text = ""
		self.hide()

	def onReikiPickStart( self ):
		"""
		副本开始
		"""
		if not self.visible:
			self.visible = True
		self.__pyRtTitle.text = ""
		self.__pyLeftPanel.visible = False
		self.__pyRightPanel.visible = False
		self.__pyBottomPanel.visible = True
		self.__pyBtnStart.visible = True
		self.__pyBtnOk.visible = False
		self.__pyRtTotal.text = ""

	def onReikiPickGoing( self ):
		"""
		灵气拾取进行中
		"""
		if not self.visible:
			self.visible = True
		player = BigWorld.player()
		self.__pyRtTitle.text = ""
		self.__pyBottomPanel.visible = False
		self.__pyLeftPanel.visible = True
		self.__pyRightPanel.visible = True
		self.__pyRightPanel.top = self.__pyLeftPanel.top
		self.__pyRichTexts["left"][0].text = labelGather.getText("ReikiPick:main", "totalPick" )%0
		self.__pyRichTexts["right"][0].text = labelGather.getText("ReikiPick:main", "continuPick" )%player.pickAnima_maxContinuousPick
	
	def onReikiNumChanged( self, totalPickNum, continuousPickNum ):
		"""
		总共拾取和连续拾取数量改变
		"""
		self.__pyRichTexts["left"][0].text = labelGather.getText("ReikiPick:main", "totalPick" )%totalPickNum
		self.__pyRichTexts["right"][0].text = labelGather.getText("ReikiPick:main", "continuPick" )%continuousPickNum
	
	def onReikiOverReport( self, totalPickNum, potentialCount ):
		"""
		灵气拾取结束
		"""
		if not self.visible:
			self.visible = True
		player = BigWorld.player()
		self.__pyRtTitle.text = labelGather.getText("ReikiPick:main", "title" )
		self.__pyBottomPanel.visible = True
		self.__pyLeftPanel.visible = True
		self.__pyRightPanel.visible = True
		self.__pyBtnStart.visible = False
		self.__pyBtnOk.visible = True
		self.__pyRightPanel.top = self.__pyLeftPanel.top + 60.0
		self.__pyRichTexts["left"][0].text = labelGather.getText("ReikiPick:main", "totalPick" )%totalPickNum
		self.__pyRichTexts["left"][1].text = labelGather.getText("ReikiPick:main", "continuPick" )%player.pickAnima_maxContinuousPick
		self.__pyRichTexts["left"][2].text = labelGather.getText("ReikiPick:main", "bombNum" )%player.pickAnima_maxZhadan
		rating = -1
		range = (0,0)
		if totalPickNum >= REIKI_PICK_TOTAL_RATING_0 and \
		player.pickAnima_maxContinuousPick == totalPickNum:
			rating = 0
			range = (96,100)
		elif totalPickNum > REIKI_PICK_TOTAL_RATING_1:
			if player.pickAnima_maxZhadan <= 0:
				rating = 1
				range = (90,95)
				return
			if player.pickAnima_maxContinuousPick >= REIKI_PICK_CONTINUOUS_NUM:
				rating = 2
				range = (85,89)
				return
			range = (80,84)
			rating = 3
		elif totalPickNum > REIKI_PICK_TOTAL_RATING_2:
			range = (75,79)
			rating = 4
		else:
			range = (70,74)
			rating = 5
		ratingText = labelGather.getText("ReikiPick:main", "rating_%d"%rating )
		self.__pyRichTexts["right"][0].fontSize = 32.0
		self.__pyRichTexts["right"][0].text = labelGather.getText("ReikiPick:main", "ratingLevel" )%ratingText
		randScore = random.randint( range[0],range[1] )
		self.__pyRichTexts["right"][1].text = labelGather.getText("ReikiPick:main", "totalScore" )%randScore
		self.__pyRtTotal.text = labelGather.getText("ReikiPick:main", "totalPotent" )%potentialCount
		self.__pyRichTexts["right"][1].top = self.__pyRichTexts["right"][0].bottom + 60.0
		self.__pyRightPanel.height = self.__pyRichTexts["right"][1].bottom + 50.0
		self.texture = "guis/empty.dds"
		self.color = 20, 20, 20, 150
	
	def onReikiEnd( self ):
		"""
		退出副本
		"""
		self.texture = ""
		self.color = 255, 255, 255, 255
		self.hide()

	def dispose( self ) :
		RootGUI.dispose( self )
		self.__class__.releaseInst()

	@staticmethod
	def instance():
		"""
		get the exclusive instance of AutoFightWindow
		"""
		if ReikiPick.__instance is None:
			ReikiPick.__instance = ReikiPick()
		return ReikiPick.__instance

	@staticmethod
	def getInstance():
		"""
		"""
		return ReikiPick.__instance

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@classmethod
	def __onReikiPickStart( SELF ):
		"""
		副本开始
		"""
		SELF.inst.onReikiPickStart()
		
	@classmethod
	def __onReikiPickGoing( SELF ):
		"""
		副本过程中的数据更新
		"""
		SELF.inst.onReikiPickGoing()
		
	@classmethod
	def __onReikiNumChanged( SELF, allPickNum, continuousPickNum ):
		"""
		总共拾取和连续拾取数量改变
		"""
		SELF.inst.onReikiNumChanged( allPickNum, continuousPickNum )
		
	@classmethod
	def __onReikiOverReport( SELF, totalPickNum, potentialCount ):
		"""
		副本结束的数据更新
		"""
		SELF.inst.onReikiOverReport( totalPickNum, potentialCount )
		
	@classmethod
	def __onReikiEnd( SELF ):
		"""
		灵气拾取结束
		"""
		SELF.inst.onReikiEnd()
		
	__triggers = {}
	@staticmethod
	def registerEvents() :
		SELF = ReikiPick
		SELF.__triggers["EVT_ON_PLAYER_REIKIPICK_START"] = SELF.__onReikiPickStart
		SELF.__triggers["EVT_ON_PLAYER_REIKIPICK_ONGOING"] = SELF.__onReikiPickGoing
		SELF.__triggers["EVT_ON_PLAYER_REIKIPICK_PICKNUM_CHANGED"] = SELF.__onReikiNumChanged
		SELF.__triggers["EVT_ON_PLAYER_REIKIPICK_OVER_REPORT"] = SELF.__onReikiOverReport
		SELF.__triggers["EVT_ON_PLAYER_REIKIPICK_END"] = SELF.__onReikiEnd
		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )

	@classmethod
	def onEvent( SELF, macroName, *args ) :
		SELF.__triggers[macroName]( *args )
	
ReikiPick.registerEvents()