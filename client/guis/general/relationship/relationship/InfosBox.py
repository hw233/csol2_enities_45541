# -*- coding: gb18030 -*-
#
# $Id: AddRelationBox.py Exp $

"""
implement info box class
"""
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.common.PyGUI import PyGUI
from guis.tooluis.CSRichText import CSRichText
from guis.controls.Button import Button
import csconst
import csdefine
import Const

class InfosBox( Window ):
	__instance=None
	def __init__( self ):
		assert InfosBox.__instance is None , "InfosBox instance has been created"
		InfosBox.__instance=self
		box = GUI.load( "guis/general/relationwindow/relationship/infosbox.gui" )
		uiFixer.firstLoadFix( box )
		Window.__init__( self, box )
		self.addToMgr( "relationInfoBox" )
		self.relation = ""

		self.__pyBtnShut = Button( box.btnShut )
		self.__pyBtnShut.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnShut.onLClick.bind( self.__onShut )

		self.__pyInfos = {}
		for name, item in box.children:
			if name.startswith( "rt_" ):
				pyInfoItem = InfoItem( item )
				tag = name.split( "_" )[1]
				self.__pyInfos[tag] = pyInfoItem

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setLabel( box.rt_tongDuty.stTitle, "RelationShip:InfoBox", "rt_tongDuty" )
		labelGather.setLabel( box.rt_tong.stTitle, "RelationShip:InfoBox", "rt_tong" )
		labelGather.setLabel( box.rt_area.stTitle, "RelationShip:InfoBox", "rt_area" )
		labelGather.setLabel( box.rt_friendlyValue.stTitle, "RelationShip:InfoBox", "rt_friendlyValue" )
		labelGather.setLabel( box.rt_raceClass.stTitle, "RelationShip:InfoBox", "rt_raceClass" )
		labelGather.setLabel( box.rt_playerName.stTitle, "RelationShip:InfoBox", "rt_playerName" )
		labelGather.setLabel( box.btnShut.lbText, "RelationShip:InfoBox", "btnShut" )
		labelGather.setLabel( box.lbTitle, "RelationShip:InfoBox", "lbTitle" )

	@staticmethod
	def instance():
		"""
		return the exclusive instance of InfosBox
		"""
		if InfosBox.__instance is None:
			InfosBox.__instance=InfosBox()
		return InfosBox.__instance

	@staticmethod
	def getInstance():
		"""
		"""
		return InfosBox.__instance

	def __onShut( self ):
		self.hide()

	def show( self, pyItem ):
		Window.show( self )
		
		self.relation = pyItem.relation
		if not self.relation.online :
			self.onOffline()
			return
		
		for tag, pyInfoItem in self.__pyInfos.iteritems():
			if hasattr( self.relation, tag ):
				info = getattr( self.relation, tag )
				if tag == "raceClass":
					if self.relation.raceClass == 0 :
						info = ""
					else:
						info = csconst.g_chs_class[self.relation.raceClass & csdefine.RCMASK_CLASS]
				elif tag == "tong":
					if self.relation.tong == 0 :
						info == ""
				pyInfoItem.setInfo( info )
				
		self.__pyInfos["tongDuty"].setInfo("")
		self.__pyInfos["area"].setInfo("")		
		
	def onOffline( self ):
		for tag, pyInfoItem in self.__pyInfos.iteritems():
			if tag == "playerName" :
				pyInfoItem.setInfo( self.relation.playerName )
			else:
				pyInfoItem.setInfo("")
	
	def getTongDutyStr( self, grade ) :
		tongDuty = Const.TONG_DUTY_NAME.get( grade )
		return tongDuty
		
	def updateTongGrade( self, relationUID, grade ) :
		if not self.relation.online:
			self.__pyInfos["tongDuty"].setInfo("")
			return
		if self.relation.relationUID == relationUID :
			tongDuty = self.getTongDutyStr( grade )
			if tongDuty is not None :
				self.__pyInfos["tongDuty"].setInfo( tongDuty )
			else:
				self.__pyInfos["tongDuty"].setInfo("")
	
	def updateArea( self, relationUID, areaStr ):
		if not self.relation.online:
			self.__pyInfos["area"].setInfo("")
			return
		if self.relation.relationUID == relationUID :
			self.__pyInfos["area"].setInfo( areaStr )
		
	def hide( self ):
		for tag, pyInfoItem in self.__pyInfos.iteritems():
			pyInfoItem.setInfo( "" )
		self.relation = ""
		Window.hide( self )
		self.removeFromMgr()
		self.dispose()
		InfosBox.__instance=None

	def __del__(self):
		"""
		just for testing memory leak
		"""
		pass

from guis.tooluis.richtext_plugins.PL_Font import PL_Font
class InfoItem( PyGUI ):
	def __init__( self, item ):
		PyGUI.__init__( self, item )
		self.__pyRtInfo = CSRichText( item.rtInfo )
		self.__pyRtInfo.text = ""

	def setInfo( self, info ):
		self.__pyRtInfo.text = PL_Font.getSource( "%s"%str( info ), fc = ( 16, 205, 172, 255 ) )
