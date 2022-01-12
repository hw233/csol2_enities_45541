# -*- coding: gb18030 -*-
#
# $Id: PlusSkillSet.py,v 1.5 2008-07-24 09:40:16 wangshufeng Exp $

"""
implement autofight window
"""
from guis import *
from guis.UIFixer import hfUILoader
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.ODComboBox import ODComboBox, InputBox
from guis.controls.ListPanel import ListPanel
from guis.controls.ListItem import SingleColListItem
from guis.controls.StaticText import StaticText
from AbstractTemplates import Singleton
import skills
import csdefine

class PlusSkillSet( Singleton, Window ):

	__instance = None

	plusskill_maps = { csdefine.CLASS_FIGHTER:[322206], #职业对应增益技能类型，以后可能会补充
				csdefine.CLASS_SWORDMAN:[322208],
				csdefine.CLASS_ARCHER:[322211,322212],
				csdefine.CLASS_MAGE:[322221]
				}

	def __init__( self ):
		assert PlusSkillSet.__instance is None,"PlusSkillSet instance has been created"
		PlusSkillSet.__instance = self
		wnd = GUI.load( "guis/general/autofightwindow/plusskill.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.__initialize( wnd )
		self.addToMgr( "plusSkillSet" )

	def __del__(self):
		"""
		just for testing memory leak
		"""
		if Debug.output_del_PlusSkillSet:
			INFO_MSG( str( self ) )

	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_PLAYERROLE_REMOVE_SKILL"] = self.__removeSkillByID
		self.__triggers["EVT_ON_PLAYERROLE_UPDATE_SKILL"] = self.__onUpateSkill
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	def __initialize( self, wnd ):
		labelGather.setPyLabel( self.pyLbTitle_, "AutoFightWindow:PlusSkillSet", "lbTitle" )
		self.__pySkillsCB = ODComboBox( wnd.cbSkills, ODTextBox )
		self.__pySkillsCB.onViewItemInitialized.bind( self.__onInitCBXItem )
		self.__pySkillsCB.onDrawItem.bind( self.__onDrawCBXItem )
		self.__pySkillsCB.onItemSelectChanged.bind( self.__onSkSelected )
		self.__pySkillsCB.ownerDraw = True

		self.__pySkillsList = ListPanel( wnd.listPanel, wnd.listBar )
		self.__pySkillsList.onItemSelectChanged.bind( self.__onPlusSkSelected )

		self.__pyPlusBtn = Button( wnd.btnPlus )
		self.__pyPlusBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyPlusBtn.onLClick.bind( self.__onAddSkill )

		self.__pyMinusBtn = Button( wnd.btnMinus )
		self.__pyMinusBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyMinusBtn.onLClick.bind( self.__onRemoveSkill )

		self.__pyOkBtn = HButtonEx( wnd.btnOK )
		self.__pyOkBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyOkBtn.onLClick.bind( self.__onOK )
		labelGather.setPyBgLabel( self.__pyOkBtn, "AutoFightWindow:PlusSkillSet", "btnOK" )

		self.__pyCancelBtn = HButtonEx( wnd.btnCancel )
		self.__pyCancelBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyCancelBtn.onLClick.bind( self.__onCancel )
		labelGather.setPyBgLabel( self.__pyCancelBtn, "AutoFightWindow:PlusSkillSet", "btnCancel" )

	def __onInitCBXItem( self, pyViewItem ) :
		"""初始化Combox的列表项"""
		staticText = hfUILoader.load( "guis/controls/odlistpanel/itemtext.gui" )
		pyText = StaticText( staticText )
		pyText.text = pyViewItem.listItem[0]
		pyViewItem.addPyChild( pyText )
		pyText.r_left = uiFixer.toFixedX( pyText.r_left )
		pyText.middle = pyViewItem.height / 2
		pyViewItem.pyText = pyText

	def __onDrawCBXItem( self, pyViewItem ) :
		"""更新列表项"""
		pyPanel = pyViewItem.pyPanel
		pyViewItem.pyText.text = pyViewItem.listItem[0]
		pyViewItem.pyText.font = pyPanel.font
		if pyViewItem.selected :
			pyViewItem.pyText.color = pyPanel.itemSelectedForeColor			# 选中状态下的前景色
			pyViewItem.color = pyPanel.itemSelectedBackColor				# 选中状态下的背景色
		elif pyViewItem.highlight :
			pyViewItem.pyText.color = pyPanel.itemHighlightForeColor		# 高亮状态下的前景色
			pyViewItem.color = pyPanel.itemHighlightBackColor				# 高亮状态下的背景色
		else :
			pyViewItem.pyText.color = pyPanel.itemCommonForeColor
			pyViewItem.color = pyPanel.itemCommonBackColor

	def __onAddSkill( self ):
		"""
		添加增益技能到列表
		"""
		skillItem = self.__pySkillsCB.selItem
		if skillItem is None:return
		skillID = skillItem[1]
		if self.__isInList( skillID ):return
		pyPlusSk = SingleColListItem()
		pyPlusSk.height = 23.0
		pyPlusSk.skillID = skillID
		pyPlusSk.text = skillItem[0]
		self.__pySkillsList.addItem( pyPlusSk )

	def __onRemoveSkill( self ):
		"""
		从列表中移除增益技能
		"""
		pyPlusSk = self.__pySkillsList.pySelItem
		if pyPlusSk is None:return
		self.__pySkillsList.removeItem( pyPlusSk )

	def removeSkillByID( self, skInfo ):
		"""
		通过ID移除列表中的增益技能
		"""
		for plusSk in self.__pySkillsList.pyItems:
			if plusSk.skillID == skInfo.id:
				self.__pySkillsList.removeItem( plusSk )
				break

	def onUpateSkill( self, oldSkillID, skillInfo ):
		"""
		增益技能更新时调用
		"""
		player = BigWorld.player()
		for plusSk in self.__pySkillsList.pyItems:
			if str( plusSk.skillID )[0:6] == str( oldSkillID )[0:6]:
				plusSk.skillID = skillInfo.id
		for skillItem in self.__pySkillsCB.items:
			if str( skillItem[ 1 ] ) == str( oldSkillID )[0:6]:
				skillItem[ 1 ] = skillInfo.id
		for skillID in player.autoPlusSkillList:
			if str( skillID )[0:6] == str( oldSkillID )[0:6] and skillID != skillInfo.id:
				index = player.autoPlusSkillList.index( skillID )
				player.autoPlusSkillList[index] = skillInfo.id
				player.setAutoPlusSkillIDList( player.autoPlusSkillList )

	def __onPlusSkSelected( self, pyPlusSk ):
		self.__pyMinusBtn.enable = pyPlusSk is not None

	def __onSkSelected( self, index ):
		if index is None or index < 0 : return
		skillID = self.__pySkillsCB.items[ index ][1]
		self.__pyPlusBtn.eneble = not self.__isInList( skillID )

	def __onOK( self ):
		"""
		确定
		"""
		plusSkills = [pyPlusSk.skillID for pyPlusSk in self.__pySkillsList.pyItems]
		BigWorld.player().setAutoPlusSkillIDList( plusSkills )
		self.hide()

	def __onCancel( self ):
		"""
		取消
		"""
		self.hide()

	def __isInList( self, skillID ):
		plusSkIDs = [int(str( pyPlusSk.skillID)[0:6]) for pyPlusSk in self.__pySkillsList.pyItems]
		return int( str(skillID)[0:6]) in plusSkIDs

	@staticmethod
	def instance():
		"""
		get the exclusive instance of AutoFightWindow
		"""
		if PlusSkillSet.__instance is None:
			PlusSkillSet.__instance = PlusSkillSet()
		return PlusSkillSet.__instance

	@staticmethod
	def getInstance():
		"""
		"""
		return PlusSkillSet.__instance

	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def show( self, pyOwner = None ):
		self.__pySkillsCB.clearItems()
		self.__pySkillsList.clearItems()
		player = BigWorld.player()
		skillIDs = player.skillList_
		plusSkills = player.getAutoPlusSkillIDList()
		classRace = player.getClass()
		racePluses = self.plusskill_maps.get( classRace, [] )
		for skillID in skillIDs: #初始化技能下拉框
			skillType = int( str( skillID )[0:6] )
			if not skillType in racePluses:continue
			skill = skills.getSkill( skillID )
			self.__pySkillsCB.addItem( [ skill.getName(), skillID ] )
		for plusSkID in plusSkills:
			if self.__isInList( plusSkID ):continue
			pyPlusSk = SingleColListItem()
			pyPlusSk.height = 23.0
			pyPlusSk.skillID = plusSkID
			pyPlusSk.text = skills.getSkill( plusSkID ).getName()
			self.__pySkillsList.addItem( pyPlusSk )
		Window.show( self, pyOwner )

	def hide( self ):
		self.__deregisterTriggers()
		PlusSkillSet.__instance=None
		Window.hide( self )

	@classmethod
	def __removeSkillByID( SELF, skillInfo ):
		"""
		移除技能
		"""
		SELF.inst.removeSkillByID( skillInfo )

	@classmethod
	def __onUpateSkill( SELF, oldSkillID, skillInfo ):
		"""
		更新增益技能
		"""
		SELF.inst.onUpateSkill( oldSkillID, skillInfo )

	__triggers = {}
	@staticmethod
	def registerEvents() :
		SELF = PlusSkillSet
		SELF.__triggers["EVT_ON_PLAYERROLE_REMOVE_SKILL"] = SELF.__removeSkillByID
		SELF.__triggers["EVT_ON_PLAYERROLE_UPDATE_SKILL"] = SELF.__onUpateSkill
		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )

	@classmethod
	def onEvent( SELF, macroName, *args ) :
		SELF.__triggers[macroName]( *args )


class ODTextBox( InputBox ) :

	def onItemSelectChanged_( self, index ) :
		"""
		选项改变时被调用
		"""
		pyCombo = self.pyComboBox
		self.text = "" if index < 0 else pyCombo.items[index][0]


PlusSkillSet.registerEvents()