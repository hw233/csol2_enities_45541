# -*- coding: gb18030 -*-
#
# $Id: self.py, fangpengjun Exp $

"""
implement self window class
"""
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.controls.CheckBox import CheckBoxEx
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
import ItemTypeEnum
import GUIFacade

GRADE_ACOUNT_MAPS = {"common": ( ItemTypeEnum.TALISMAN_COMMON, 1 ), #每种品质属性对应石头数
			"immortal": ( ItemTypeEnum.TALISMAN_IMMORTAL, 5 ),
			"deity" : ( ItemTypeEnum.TALISMAN_DEITY,15 )
			}

CHECKER_TOTAL_NUMBER = 6

class AttrRebuild( Window ):
	def __init__( self, pyBinder = None ):
		wnd = GUI.load( "guis/general/playerprowindow/talisman/rebuildpanel.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.addToMgr( "attrRebuild" )
		self.__triggers = {}
		self.__registerTriggers()
		self.needStoneNum = 0 #需要石头总数
		self.checkersNum = 0

		self.__pyAttrCheckers = {} #
		for name, item in wnd.children:
			if not "_" in name:continue
			tag = name.split( "_" )[0]
			index = int( name.split( "_" )[1] )
			grade = GRADE_ACOUNT_MAPS[tag][0]
			pyAttrChecker = AttrChecker( item, self )
			pyAttrChecker.tag = tag
			pyAttrChecker.index = index
			if self.__pyAttrCheckers.has_key( grade ):
				self.__pyAttrCheckers[grade][index] = pyAttrChecker
			else:
				self.__pyAttrCheckers[grade] = {index:pyAttrChecker}
		self.__pyAllChecher = CheckBoxEx( wnd.allChecker ) #全部选择
		self.__pyAllChecher.checked = False
		self.__pyAllChecher.clickCheck = True
		self.__pyAllChecher.onCheckChanged.bind( self.__onCheckAll )
		self.__pyAllChecher.text = labelGather.getText( "PlayerProperty:AttrRebuild", "ckAll" )

		self.__pyBtnConfirm = Button( wnd.btnConfirm ) #确认按钮
		self.__pyBtnConfirm.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnConfirm.onLClick.bind( self.__onConfirm )
		labelGather.setPyBgLabel( self.__pyBtnConfirm, "PlayerProperty:AttrRebuild", "btnConfirm" )

		self.__pyStStoneNum = StaticText( wnd.stoneNum ) #需要石头数
		self.__pyStStoneNum.text = labelGather.getText("PlayerProperty:AttrRebuild","stoneNum","0") 
		
		labelGather.setLabel( wnd.lbTitle, "PlayerProperty:AttrRebuild", "lbTitle" )
		labelGather.setLabel( wnd.commonFrm.bgTitle.stTitle, "PlayerProperty:AttrRebuild", "commonTitle" )
		labelGather.setLabel( wnd.immortalFrm.bgTitle.stTitle, "PlayerProperty:AttrRebuild", "immortalTitle" )
		labelGather.setLabel( wnd.deityFrm.bgTitle.stTitle, "PlayerProperty:AttrRebuild", "deityTitle" )
		
	# ----------------------------------------------------------------
	# pribvate
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TALISMAN_ATTR_REBUILD"] = self.__onAttrRebuild
		self.__triggers["EVT_ON_TALISMAN_ATTR_ACTIVATY"] = self.__onAttrActivaty
		self.__triggers["EVT_ON_TALISMAN_ATTR_CHECK"] 	= self.onAttrCheked
		for key in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( key, self )

	def __unregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			GUIFacade.unregisterEvent( key, self )

	# ------------------------------------------------------------------
	def __onAttrRebuild( self, gradee, indexx, keyy ):
		"""
		成功改造了某属性	modified by姜毅15:41 2009-9-30
		"""
		player = BigWorld.player()
		taliStone = player.getItem_( ItemTypeEnum.CWT_TALISMAN ) #获取法宝
		if taliStone is None: return
		commonAttrs = taliStone.getCommonEffect() #凡品属性
		immortalAttrs = taliStone.getImmortalEffect() #仙品属性
		deityAttrs = taliStone.getDeityEffect() #神品属性
		for index, ( key, isActive )in enumerate( commonAttrs ):
			pyAttrChecker = self.__pyAttrCheckers[ItemTypeEnum.TALISMAN_COMMON][index]
			pyAttrChecker.setAttrValue( key, isActive )
			pyAttrChecker.setChecked( False )

		for index, ( key, isActive ) in enumerate( immortalAttrs ):
			pyAttrChecker = self.__pyAttrCheckers[ItemTypeEnum.TALISMAN_IMMORTAL][index]
			pyAttrChecker.setAttrValue( key, isActive )
			pyAttrChecker.setChecked( False )

		for index, ( key, isActive )in enumerate( deityAttrs ):
			pyAttrChecker = self.__pyAttrCheckers[ItemTypeEnum.TALISMAN_DEITY][index]
			pyAttrChecker.setAttrValue( key, isActive )
			pyAttrChecker.setChecked( False )

	def __onAttrActivaty( self, grade, index ):
		"""
		成功激活某个属性
		"""
		pyAttrChecker = self.__pyAttrCheckers[grade][index]
		if pyAttrChecker is None:return
		pyAttrChecker.setAttrValue( pyAttrChecker.key, True )

	def __onConfirm( self ):
		grades = []
		indexs = []
		for grade, subAttr in self.__pyAttrCheckers.iteritems():
			for index, pyAttrChecker in subAttr.iteritems():
				if not pyAttrChecker.isChecked():continue
				grades.append( grade )
				indexs.append( index )
		BigWorld.player().rebuildTalismanAttr( grades, indexs )

	def __onCheckAll( self, checked ):
		for pyAttrCheckers in self.__pyAttrCheckers.itervalues():
			for pyAttrChecker in pyAttrCheckers.itervalues():
				pyAttrChecker.setChecked( checked )

	# ------------------------------------------------------------
	# public
	# ------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onAttrCheked( self, tag, checked ):
		stoneAmount = GRADE_ACOUNT_MAPS[tag][1]
		if checked:
			self.needStoneNum += stoneAmount
			self.checkersNum += 1
		else:
			self.needStoneNum -= stoneAmount
			self.checkersNum -= 1
			if self.needStoneNum < 0:
				self.needStoneNum = 0
		self.__pyAllChecher.txelems["checker"].visible = self.checkersNum >= CHECKER_TOTAL_NUMBER
		self.__pyStStoneNum.text = labelGather.getText("PlayerProperty:AttrRebuild","stoneNum", str( self.needStoneNum ))

	def onEnterWorld( self ):
		pass

	def onLeaveWorld( self ):
		self.hide()
#		self.__pyAttrCheckers = {}

	def show( self, pyOwner = None ):
		player = BigWorld.player()
		taliStone = player.getItem_( ItemTypeEnum.CWT_TALISMAN ) #获取法宝
		if taliStone is None: return
		commonAttrs = taliStone.getCommonEffect() #凡品属性
		immortalAttrs = taliStone.getImmortalEffect() #仙品属性
		deityAttrs = taliStone.getDeityEffect() #神品属性
		for index, ( key, isActive )in enumerate( commonAttrs ):
			pyAttrChecker = self.__pyAttrCheckers[ItemTypeEnum.TALISMAN_COMMON][index]
			pyAttrChecker.setAttrValue( key, isActive )

		for index, ( key, isActive ) in enumerate( immortalAttrs ):
			pyAttrChecker = self.__pyAttrCheckers[ItemTypeEnum.TALISMAN_IMMORTAL][index]
			pyAttrChecker.setAttrValue( key, isActive )

		for index, ( key, isActive )in enumerate( deityAttrs ):
			pyAttrChecker = self.__pyAttrCheckers[ItemTypeEnum.TALISMAN_DEITY][index]
			pyAttrChecker.setAttrValue( key, isActive )

		Window.show( self, pyOwner )

	def hide( self ):
		for pyAttrCheckers in self.__pyAttrCheckers.itervalues():
			for pyAttrChecker in pyAttrCheckers.itervalues():
				pyAttrChecker.setChecked( False )
		self.__pyAllChecher.checked = False
		self.__pyStStoneNum.text = labelGather.getText("PlayerProperty:AttrRebuild","stoneNum","0" ) 
		Window.hide( self )

# ----------------------------------------------------------
from guis.common.PyGUI import PyGUI
from guis.tooluis.CSRichText import CSRichText
from guis.controls.CheckBox import CheckBox
from AbstractTemplates import MultiLngFuncDecorator

class deco_InitRtValue( MultiLngFuncDecorator ) :

	@staticmethod
	def locale_big5( SELF, pyRtValue ) :
		"""
		繁体版下重新调整部分属性字体的尺寸
		"""
		pyRtValue.charSpace = -1.0
		pyRtValue.fontSize = 11
		
class AttrChecker( PyGUI ):
	def __init__( self, attrChecker, pyBinder = None ):
		PyGUI.__init__( self, attrChecker )
		self.index = -1
		self.tag = ""
		self.isActive = False
		self.key = -1
		self.__pyRtDsp = CSRichText( attrChecker.rtDsp )
		self.__pyRtDsp.maxWidth = 122.0
		self.__pyRtDsp.align = "L"
		self.__pyRtDsp.text = ""

		self.__pyRtValue = CSRichText( attrChecker.rtValue )
		self.__pyRtValue.maxWidth = 40.0
		self.__pyRtValue.align = "R"
		self.__pyRtValue.text = ""
		self.__setValueSpace( self.__pyRtValue )

		self.__pyChecker = CheckBoxEx( attrChecker.checker )
		self.__pyChecker.clickCheck = True
		self.__pyChecker.checked = False
		self.__pyChecker.onCheckChanged.bind( self.__onCheckChange )

#		self.__pyCheckBg = PyGUI( attrChecker.checkBg )
		self.pyBinder = pyBinder
		
	@deco_InitRtValue
	def __setValueSpace( self, pyRtValue ):
		charSpace = 0.0
		fontSize = 13
		if pyRtValue.font == "MSYHBD.TTF":
			charSpace = -1.0
			fontSize = 12
		pyRtValue.charSpace = charSpace
		pyRtValue.fontSize = fontSize
		
	def __onCheckChange( self, checked ):
		self.pyBinder.onAttrCheked( self.tag, checked )

	def setAttrValue( self, key, isActive ):
		self.isActive = isActive
		self.key = key
		taliStone = BigWorld.player().getItem_( ItemTypeEnum.CWT_TALISMAN ) #获取法宝
		initEffectValue = rds.talismanEffects.getInitValue( key )
		param = rds.talismanEffects.getUpParam( key )
		value = initEffectValue + taliStone.getLevel() * param
		effectKey = rds.talismanEffects.getEffectID( key )
		effectClass = rds.equipEffects.getEffect( effectKey )
		if effectClass is None:return
		des = effectClass.descriptionList( value )
		attrDsp = des[0]
		attrValue = des[1]
		attrText = ""
		if isActive:
			attrDsp = PL_Font.getSource( attrDsp, fc = ( 242, 235, 201, 255 ) )
			attrValue = PL_Font.getSource( attrValue, fc = ( 7, 197, 166, 255 ) )
		else:
			attrDsp = PL_Font.getSource( attrDsp, fc = ( 127, 127, 127, 255 ))
			attrValue = PL_Font.getSource( attrValue, fc = ( 127, 127, 127, 255 ))
		self.__pyRtDsp.text = attrDsp
		self.__pyRtValue.text = attrValue

	def setActivaty( self ):
		self.isActive = True
		self.__pyRtValue.foreColor = 242, 235, 201, 255

	def setChecked( self, checked ):
		self.__pyChecker.checked = checked

	def isChecked( self ):
		return self.__pyChecker.checked
