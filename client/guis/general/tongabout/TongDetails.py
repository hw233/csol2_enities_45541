# -*- coding: gb18030 -*-
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.StaticText import StaticText

class TongDetails( Window ):
	"""
	查询帮会的详细信息
	"""
	def __init__( self ):
		wnd = GUI.load( "guis/general/tongabout/tongDetails/tongDetails.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( wnd )
		self.addToMgr( "TongDetails" )
		
	def __initialize( self, wnd ):
		self.__pyStTongName = StaticText( wnd.panel.tongName )
		self.__pyStTongName.text = ""
		self.__pyStChairman = StaticText( wnd.panel.chairman )
		self.__pyStChairman.text = ""
		self.__pyStTongLevel = StaticText( wnd.panel.tongLevel )
		self.__pyStTongLevel.text = ""
		self.__pyStMember = StaticText( wnd.panel.members )
		self.__pyStMember.text = ""
		
		labelGather.setPyLabel( self.pyLbTitle_, "TongAbout:TongDetails", "lbTitle" )
		labelGather.setLabel( wnd.panel.lbTongName, "TongAbout:TongDetails", "lbTongName" )
		labelGather.setLabel( wnd.panel.lbChairman, "TongAbout:TongDetails", "lbChairman" )
		labelGather.setLabel( wnd.panel.lbTongLevel, "TongAbout:TongDetails", "lbTongLevel" )
		labelGather.setLabel( wnd.panel.lbMembers, "TongAbout:TongDetails", "lbMembers" )
		
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_SHOW_TONGDETAILS"] = self.__onShowWnd
		for trigger in self.__triggers :
			ECenter.registerEvent( trigger, self )

	def __desregisterTriggers( self ) :
		for trigger in self.__triggers :
			ECenter.unregisterEvent( trigger, self )
			
	def __onShowWnd( self,arrayList ):
		print "arrayList------------",arrayList
		self.show( arrayList )
		
	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def onEvent( self, evtMacro, *args ) :
		self.__triggers[evtMacro]( *args )
		
	def show( self, arrayList ):
		print "llllllll------",arrayList
		Window.show( self )
		self.__pyStTongName.text = arrayList[0]
		self.__pyStChairman.text = arrayList[1]
		self.__pyStTongLevel.text = arrayList[2]
		self.__pyStMember.text = arrayList[3]
		
	def hide( self ):
		Window.hide( self )
		self.__pyStTongName.text = ""
		self.__pyStChairman.text = ""
		self.__pyStTongLevel.text = ""
		self.__pyStMember.text = ""
		
	def onLeaveWorld( self ) :
		self.hide()
		