# -*- coding: gb18030 -*-
#
# $Id: DutySetting.py $

"""
implement DutySetting class
"""
from guis import *
import BigWorld
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TextBox import TextBox
from guis.controls.SelectableButton import SelectableButton
from guis.controls.SelectorGroup import SelectorGroup
from config.client.msgboxtexts import Datas as mbmsgs
import GUIFacade
import csdefine
import Const
import math

class DutySetting( Window ):
	__instance=None
	__pyDutiestexts= {}
	def __init__( self ):
		assert DutySetting.__instance is None,"DutySetting instance has been create"
		DutySetting.__instance=self
		panel = GUI.load( "guis/general/relationwindow/tongpanel/dutyset.gui" )
		uiFixer.firstLoadFix( panel )
		Window.__init__( self, panel )
		self.addToMgr( "dutySetting" )
		self.__triggers = {}
		self.__registerTriggers()
		self.__initpanel( panel )

	@staticmethod
	def instance():
		"""
		to get the exclusive instance of DutySetting
		"""
		if DutySetting.__instance is None:
			DutySetting.__instance=DutySetting()
		return DutySetting.__instance

	@staticmethod
	def getInstance():
		"""
		return DutySetting.__instance, if DutySetting.__instance is None ,return None,
		else return the exclusive instance of DutySetting
		"""
		return DutySetting.__instance

	def __del__(self):
		"""
		just fot testing memory leak
		"""
		pass

	def __initpanel( self, panel ):
		labelGather.setLabel( panel.lbTitle, "RelationShip:TongPanel", "dutySetTitle" )
		labelGather.setLabel( panel.amendText, "RelationShip:TongPanel", "amendText" )
		self.__pyBtnOk = HButtonEx( panel.btnOk )
		self.__pyBtnOk.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOk.onLClick.bind( self.__onAmendOK )
		labelGather.setPyBgLabel( self.__pyBtnOk, "RelationShip:RelationPanel", "btnOk" )

		self.__pyBtnQuit = HButtonEx( panel.btnQuit )
		self.__pyBtnQuit.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnQuit.onLClick.bind( self.hide )
		labelGather.setPyBgLabel( self.__pyBtnQuit, "RelationShip:TongPanel", "btnQuit" )

		self.__pyAmendBox = TextBox( panel.amendBox.box )
		self.__pyAmendBox.inputMode = InputMode.COMMON
		self.__pyAmendBox.onTextChanged.bind( self.__onNameChange )
		self.__pyAmendBox.text = ""
		self.__pyDuties={}

		self.__pySelectorGroup = SelectorGroup()
		for name, item in panel.children:
			if "dutyBtn_" not in name:continue
			index = int( name.split( "_" )[1] )
			dutyKey = index + 1
			pyDutyBtn = SelectableButton( item )
			pyDutyBtn.setStatesMapping( UIState.MODE_R4C1 )
			pyDutyBtn.dutyKey = dutyKey
			self.__pyDuties[dutyKey] = pyDutyBtn
			if Const.TONG_GRADE_MAPPING.has_key( dutyKey ):
				dutyName = ""
				if DutySetting.__pyDutiestexts.has_key(dutyKey):
					dutyName=DutySetting.__pyDutiestexts[dutyKey]
				self.__pyDuties[dutyKey].text = dutyName
			pyDutyBtn.onMouseEnter.bind( self.__onShowDutyName )
			pyDutyBtn.onMouseLeave.bind( self.__onHideDuty )
			self.__pySelectorGroup.addSelector( pyDutyBtn )

		#			self.__pySelectorGroup.onSelectChanged.bind( self.__onDutyChange )
	# ----------------------------------------------------------
	# private
	# ----------------------------------------------------------
	def __registerTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.unregisterEvent( key, self )

	#-------------------------------------------------------------
	def __onNameChange( self ):
		self.__pyBtnOk.enable = self.__pyAmendBox.text != "" and \
			self.__pySelectorGroup.pyCurrSelector is not None

	def __onAmendOK( self ):
		pyDuty = self.__pySelectorGroup.pyCurrSelector
		if pyDuty is None:return
		dutyKey = pyDuty.dutyKey
		text = self.__pyAmendBox.text.strip()
		if len( text ) > 10:
			# "名称长度不能超过 10 个字节"
			showAutoHideMessage( 3.0, 0x0741, mbmsgs[0x0c22] )
			return
		elif text == "" :
			# "您输入的用户名无效，请重新输入。"
			showAutoHideMessage( 3.0, 0x0742, mbmsgs[0x0c22] )
			return
		elif not rds.wordsProfanity.isPureString( text ) :
			# "名称不合法！"
			showAutoHideMessage( 3.0, 0x0743, mbmsgs[0x0c22] )
			return
		elif rds.wordsProfanity.searchNameProfanity( text ) is not None :
			# "输入的名字有禁用词汇!"
			showAutoHideMessage( 3.0, 0x0744, mbmsgs[0x0c22] )
			return
		elif text in [pyBtn.text for pyBtn in self.__pyDuties.itervalues()]:
			# "已存在相同的职务名称!"
			showAutoHideMessage( 3.0, 0x0745, mbmsgs[0x0c22] )
			return
		BigWorld.player().tong_setDutyName( dutyKey, text )

	def __onDutyChange( self, pyDuty ):
		self.__pyAmendBox.enable = pyDuty is not None

	def __onShowDutyName( self, pyBtn ):
		if pyBtn is None:return
		dutyKey = pyBtn.dutyKey
		defName = Const.TONG_GRADE_MAPPING.get( dutyKey, "" )
		toolbox.infoTip.showToolTips( pyBtn, defName )
			
	def __onHideDuty( self ):
		toolbox.infoTip.hide()
		
	def onInitDutyName( self, dutyKey, name ): #初始化职务名称
		self.__pyDutiestexts[dutyKey] = name
		defName = Const.TONG_GRADE_MAPPING.get( dutyKey, "" )
		pyDuty = self.__pyDuties[dutyKey]
		pyDuty.text = name
		if name != defName:
			pyDuty.commonForeColor = 255, 224, 128, 255
			pyDuty.selectedForeColor = 255, 224, 128, 255

	def onUpdateDutyName( self, dutyKey, name ): #更新职务名称
		if self.__pyDutiestexts.has_key( dutyKey ):
			pyDuty = self.__pyDuties[dutyKey]
			pyDuty.text = name
			self.__pyAmendBox.text = ""
			self.__pyDutiestexts[dutyKey]=name
			defName = Const.TONG_GRADE_MAPPING.get( dutyKey, "" )
			if defName != name:
				pyDuty.commonForeColor = 255, 224, 128, 255
				pyDuty.selectedForeColor = 255, 224, 128, 255

	def onKeyDown_( self, key, mods ) :
		if key == KEY_RETURN and mods == 0 :
			self.__onAmendOK()
		return True

	def initDuties( self, tongWnd ): # 获取各职务人数数量
		pyItems = tongWnd.getMembers()
		dutyNums = {}
		for pyItem in pyItems:
			grade = pyItem.getGrade()
			if self.__pyDuties.has_key( grade ):
				if dutyNums.has_key( grade ):
					dutyNums[grade] += 1
				else:
					dutyNums[grade] = 1
			else:
				dutyNums[grade] = 0
		self.__pyAmendBox.text = ""

	# -----------------------------------------------------------
	# public
	# -----------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def reset( self ):
		self.__pyAmendBox.text = ""
		self.__pyDuties = {}

	def show( self, pyOwner = None ):
		Window.show( self, pyOwner )
		self.__pyAmendBox.tabStop = True

	def hide( self ):
		Window.hide( self )
		self.dispose()
		self.removeFromMgr()
		DutySetting.__instance=None
		self.__triggers={}

