# -*- coding: gb18030 -*-

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ButtonEx import HButtonEx
from config.client.CopyYiJieZhanChang import Datas as introdutionDatas
from guis.common.PyGUI import PyGUI	

class YiJieSignUp( Window ):
	def __init__( self ):
		wnd = GUI.load( "guis/general/spacecopyabout/spaceCopyYiJieZhanChang/sign.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )		
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ = True			
		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()
				
	def __initialize( self, wnd ):
		labelGather.setLabel( wnd.lbTitle, "SpaceCopyJiJieZhanChang:yiJieSignUp", "lbTitle" )
		
		self.__pyContentPanel = subPanel( wnd.introductionPanel )
		self.__pyContentPanel.title = introdutionDatas["stTitle1"]
		self.__pyContentPanel.content = introdutionDatas["introduction"]
		
		self.__pyConditionPanel = subPanel( wnd.conditionPanel )
		self.__pyConditionPanel.title = introdutionDatas["stTitle2"]
		self.__pyConditionPanel.content = introdutionDatas["conditions"]
		
		self.__pyTipsPanel = subPanel( wnd.tipsPanel )
		self.__pyTipsPanel.title = introdutionDatas["stTitle3"]
		self.__pyTipsPanel.content = introdutionDatas["tips"]
		
		self.__pyBtnOk = HButtonEx( wnd.btnOk )
		self.__pyBtnOk.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnOk.onLClick.bind( self.__onJoinIn )
		labelGather.setPyBgLabel( self.__pyBtnOk, "SpaceCopyJiJieZhanChang:yiJieSignUp", "btnOk")
		
		self.__pyBtnCancel = HButtonEx( wnd.btnCancel )
		self.__pyBtnCancel.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnCancel.onLClick.bind( self.__onCancel )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "SpaceCopyJiJieZhanChang:yiJieSignUp", "btnCancel" )
		
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_SHOW_JIJIE_SIGNUP_WINDOW"] = self.__onShow
		self.__triggers["EVT_ON_CANCEL_JIJIE_SIGNUP_WINDOW"] = self.__onCancel
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )
	
	def __onJoinIn( self ):
		BigWorld.player().requestEnterYiJie()
	
	def __onShow( self ):
		Window.show( self )
		
	def __onCancel( self ):
		self.hide()	
		
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )			
		
	def onLeaveWorld( self ) :
		self.hide()
			
class subPanel( PyGUI ):
	def __init__( self, panel ):
		PyGUI.__init__( self, panel )
		
		self.__pyRtContent = CSRichText( panel.rtContent )
		self.__pyRtContent.text = ""
		
		self.__pyStTitle = StaticText( panel.stTitle.stTitle )
		self.__pyStTitle.text = ""		
	
	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------	
	def _getTitle( self ):
		return self.__pyStTitle.text
		
	def _setTitle( self, title ):
		self.__pyStTitle.text = title
		
	def _getContent( self ):
		return self.__pyRtContent.text
		
	def _setContent( self, content ):
		self.__pyRtContent.text = content
		
	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	title 	= property( _getTitle, _setTitle )		#标题			
	content = property( _getContent, _setContent )	#内容
				