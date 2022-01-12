# -*- coding: gb18030 -*-
#
# $Id: DutySetting.py $

"""
implement GradeSetting class
"""
from guis import *
import BigWorld
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.CheckBox import CheckBoxEx
from guis.controls.ComboBox import ComboItem
from guis.controls.ComboBox import ComboBox
from guis.controls.ButtonEx import HButtonEx
import GUIFacade
import csdefine
import Const
import math

class GradeSetting( Window ):
	def __init__( self ):
		panel = GUI.load( "guis/general/relationwindow/tongpanel/gradeset.gui" )
		uiFixer.firstLoadFix( panel )
		Window.__init__( self, panel )
		self.addToMgr( "gradeSetting" )
		self.__triggers = {}
		self.__registerTriggers()
		self.__initpanel( panel )

	def __initpanel( self, panel ):
		labelGather.setLabel( panel.lbTitle, "RelationShip:TongPanel", "gradeSetTitle" )
		self.__pyDutiesCB = ComboBox( panel.dutyCB ) # 帮会，家族等选项
		self.__pyDutiesCB.text = labelGather.getText( "RelationShip:TongPanel", "options" )
		self.__pyDutiesCB.autoSelect = False
#		self.__pyDutiesCB.width = 145.0
		self.__pyDutiesCB.onItemSelectChanged.bind( self.__onDutyChange )

		self.__pyDuties = {}
		keyList = Const.TONG_GRADE_MAPPING.items()
		keyList.sort()
		keyList.reverse()
		for key, duty in keyList: #初始化职务下拉列表
			if key == 0:continue #过滤帮主和没帮会时的默认值
			pyDuty = ComboItem( duty )
			pyDuty.h_anchor = "CENTER"
			pyDuty.duty = key
			self.__pyDuties[key] = pyDuty
			self.__pyDutiesCB.addItem( pyDuty )

		self.__checks = []
		for name, item in panel.children: #初始化权限列表
			if "checkbox_" in name:
				index = int( name.split( "_" )[1] )
				gradeKey = index + 1
				pyCheck = CheckBoxEx( item )
				pyCheck.gradeKey = gradeKey
				pyCheck.checked = False
				pyCheck.enable = False
				labelGather.setPyLabel( pyCheck, "RelationShip:TongPanel", name )
				self.__checks.append( pyCheck )

	# ----------------------------------------------------------
	# private
	# ----------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_TONG_INIT_DUTY_NAME"] = self.__onInitDutyName #初始化所有职务名称
		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_DUTY_NAME"] = self.__onUpdateDutyName #更新某个职务名称

		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.unregisterEvent( key, self )

	#-------------------------------------------------------------

	def __onDutyChange( self, pyDuty ):
		if pyDuty is None:return
		duty = pyDuty.duty
		self.__resetChecks()
		for checker in self.__checks:
			gradeKey = checker.gradeKey
			checker.checked = gradeKey in csdefine.TONG_DUTY_CLIENT_RIGHTS_MAPPING.get( duty ) 

	def __resetChecks( self ):
		for checker in self.__checks:
			checker.checked = False

	def __onInitDutyName( self, dutyKey, name ):
		if self.__pyDuties.has_key( dutyKey ):
			pyDuty = self.__pyDuties[dutyKey]
			if pyDuty.text != name:
				pyDuty.text = name

	def __onUpdateDutyName( self, dutyKey, name ):
		if self.__pyDuties.has_key( dutyKey ):
			self.__pyDuties[dutyKey].text = name


	# -----------------------------------------------------------------
	# public
	# -----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def show( self, pyOwner = None ):
		Window.show( self, pyOwner )

	def hide( self ):			
		Window.hide( self )

	def reset( self ):
		for checker in self.__checks:
			checker.checked = False