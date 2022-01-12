# -*- coding: gb18030 -*-
#
# $Id: SpecialItem.py,fangpengjun Exp $

"""
implement SpecialItem
"""
from guis import *
from LabelGather import labelGather
from guis.controls.Control import Control
from guis.common.PyGUI import PyGUI
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
import event.EventCenter as ECenter
from guis.controls.Icon import Icon
from guis.controls.ProgressBar import HProgressBar
import GUIFacade
import csdefine

class RobotItem( Control ):
	
	def __init__( self, item, pyBinder = None, index = 0 ):
		Control.__init__( self, item, pyBinder )
		self.focus = False
		self.index = index
		
		self.__pyRobotInfo = RobotInfo( item.robotBox )
		
		self.__pyBtnModify = HButtonEx( item.btnModify )
		self.__pyBtnModify.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnModify.onLClick.bind( self.__onModify )
		labelGather.setPyBgLabel( self.__pyBtnModify, "LolPVP:main", "btnModify" )
		self.__pyBtnModify.visible = False
		
		self.__pyBtnDelete = HButtonEx( item.btnDelete )
		self.__pyBtnDelete.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnDelete.onLClick.bind( self.__onDelete )
		labelGather.setPyBgLabel( self.__pyBtnDelete, "LolPVP:main", "btnDelete" )
		self.__pyBtnDelete.visible = False
		self.robotInfo =None
	
	def __onModify( self, pyBtn ):
		"""
		修改机器人
		"""
		if pyBtn is None:return
		pyBinder = self.pyBinder
		robotPro = rds.ruisMgr.robotProperty
		robots = pyBinder.getRobots()
		if self.robotInfo in robots:
			index = robots.index( self.robotInfo )
			robotPro.show( pyBinder.teamNumber, index, pyBinder.pyTopParent )
	
	def __onDelete( self, pyBtn ):
		"""
		删除机器人
		"""
		robots = self.pyBinder.getRobots()
		if self.robotInfo in robots:
			index = robots.index( self.robotInfo )
			ECenter.fireEvent( "EVT_ON_REMOVE_PVE_ROBOT", self.pyBinder.teamNumber, index )
	
	def updateInfo( self, robotInfo ):
		"""
		更新机器人信息
		"""
		self.robotInfo = robotInfo
		isRobot = robotInfo.isRobot
		pyParent = self.pyBinder
		self.__pyRobotInfo.updateInfo( robotInfo )
		isCaptain = BigWorld.player().isCaptain()
		isVisible = isRobot and pyParent.teamNumber == 0 and isCaptain
		self.__pyBtnModify.visible = isVisible
		self.__pyBtnDelete.visible = isVisible

	def __select( self ):
		self.panelState = ( 2, 1 )
		if self.__pyCover:
			self.__pyCover.visible = True

	def __deselect( self ):
		self.panelState = ( 1, 1 )
		if self.__pyCover:
			self.__pyCover.visible = False

	def _getSelected( self ):
		return self.__selected

	def _setSelected( self, selected ):
		if selected:
			self.__select()
		else:
			self.__deselect()
		self.__selected = selected

class RobotInfo( PyGUI ):
	
	__cc_pro_states = {}									# 不同职业的状态标记 mapping 位
	__cc_pro_states[csdefine.CLASS_FIGHTER]	 = ( 1, 1 )		# 战士
	__cc_pro_states[csdefine.CLASS_SWORDMAN] = ( 1, 2 )		# 剑客
	__cc_pro_states[csdefine.CLASS_ARCHER]	 = ( 2, 1 )		# 射手
	__cc_pro_states[csdefine.CLASS_MAGE]	 = ( 2, 2 )		# 法师
	
	def __init__( self, item ):
		PyGUI.__init__( self, item )
		self.__pyHeader = PyGUI( item.header )
		
#		self.__pyBorder = PyGUI( item.border )
#		self.__pyBg = PyGUI( item.bg )

		self.__pyCaptainMark = PyGUI( item.captainMark )
		self.__pyCaptainMark.visible = False

		self.__pyLbName = StaticText( item.lbName )
		self.__pyLbName.text = ""

		self.__pyLbLevel = StaticText( item.lbLevel )
		self.__pyLbLevel.fontSize = 12
		self.__pyLbLevel.text = ""
		self.__pyLbLevel.h_anchor = 'CENTER'

		self.__pyHPBar = HProgressBar( item.hpBar,self )

		self.__pyHPBar.value = 0
		self.__pyHPBar.crossFocus = True
		self.__pyLbHP = StaticText( item.lbHP )
		self.__pyLbHP.fontSize = 12
		self.__pyLbHP.text = ""
		self.__pyLbHP.h_anchor = 'CENTER'
		self.__pyLbHP.visible = True
		
		self.__pyMPBar = None
		if hasattr( item, "mpBar" ):
			self.__pyMPBar = HProgressBar( item.mpBar,self )
			self.__pyMPBar.crossFocus = True
			self.__pyMPBar.value = 0
		
		self.__pyLbMP = None
		if hasattr( item, "lbMP" ):
			self.__pyLbMP = StaticText( item.lbMP )
			self.__pyLbMP.fontSize = 12
			self.__pyLbMP.text = ""
			self.__pyLbMP.h_anchor = 'CENTER'
			self.__pyLbMP.visible = True
		
		self.__pyClassMark = Icon( item.classMark )
		self.__pyClassMark.crossFocus = True
	
	def updateInfo( self, robotInfo ):
		self.__pyLbName.text = robotInfo.name
		self.__pyLbLevel.text = str( robotInfo.level )
		hp = robotInfo.hp
		hpMax = robotInfo.hpMax
		mp = robotInfo.mp
		mpMax = robotInfo.mpMax
		if hpMax <= 0.0:
			hpMax = 1.0
		if mpMax <= 0.0:
			mpMax = 1.0
		phRato = float( hp/hpMax )
		mprato = float( mp/mpMax )
		self.__pyHPBar.value = min( phRato, 1.0 )
		if self.__pyMPBar:
			self.__pyMPBar.value = min( mprato, 1.0 )
		util.setGuiState( self.__pyClassMark.getGui(), ( 2, 2 ), self.__cc_pro_states[robotInfo.raceclass] )
		self.__pyHeader.texture = robotInfo.header
		self.__pyLbHP.text = "%d/%d"%( hp, hpMax )
		if self.__pyLbMP:
			self.__pyLbMP.text = "%d/%d"%( mp, mpMax )
