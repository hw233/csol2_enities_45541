# -*- coding: gb18030 -*-
#
# $Id: OperationBar.py,v 1.15 2008-08-26 02:17:14 huangyongwei Exp $

"""
implement listitem class
2007/12/04: writen by huangyongwei
"""

import csdefine
import csconst
from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.RootGUI import RootGUI
from guis.controls.Button import Button
from guis.controls.Control import Control
from guis.controls.SelectorGroup import SelectorGroup
from guis.controls.SelectableButton import SelectableButton
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from PBItem import PBItem
from AutoFightItem import AutoFightItem
from PetDrugItem import PetDrugItem
from PetTussleMenu import PetTussleMenu
from cscollections import MapList
from LabelGather import labelGather

ITEM_DSPS = { 0: labelGather.getText( "quickbar:petBar", "tipsSkillItem" ),				# 技能栏描述
		10: labelGather.getText( "quickbar:petBar", "tipsHPItem" ),			# 生命药栏描述
		11: labelGather.getText( "quickbar:petBar", "tipsMPItem" ),			# 法力药栏描述
		}


class PetBar( PyGUI ) :

	def __init__( self, bar ) :
		PyGUI.__init__( self, bar )
		self.__initialize( bar )

		self.__triggers = {}
		self.__registerTriggers()
		self.__temperText = "" 													# 记录宠物的当前心情描述

		self.__cancelCoverCBID = 0
		self.__invalidItems = []												# 不可用技能

		rds.shortcutMgr.setHandler( "PET_ASSIST", self.__attackTarget )			# 命令宠物协助攻击
		rds.shortcutMgr.setHandler( "PET_TO_FOLLOW", self.__setToFollow )		# 命令宠物停留/跟随
		rds.shortcutMgr.setHandler( "PET_TO_KEEPING", self.__setToKeeping )		# 命令宠物停留/跟随
		rds.shortcutMgr.setHandler( "PET_DOMESTICATE", self.__domesticate )		# 驯养


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, bar ) :
		self.__pyAttackBtn = Button( bar.attackBtn )							# 命令发起攻击按钮
		self.__pyAttackBtn.setStatesMapping( UIState.MODE_R1C3 )
		self.__pyAttackBtn.onLMouseDown.bind( self.__attackTarget )
		self.__pyAttackBtn.description = labelGather.getText( "quickbar:petBar", "dspAttack" )
		self.__pyAttackBtn.scTag = "PET_ASSIST"
		self.__pyAttackBtn.onMouseEnter.bind( self.__showTip )
		self.__pyAttackBtn.onMouseLeave.bind( self.__hideTip )
		self.__pyAttackBtn.onLMouseDown.bind( self.__hideTip, True )

		self.__pyTemperBtn = Button( bar.temperBtn )							# 宠物情绪表现兼驯养按钮
		self.__pyTemperBtn.setStatesMapping( UIState.MODE_R1C3 )
		self.__pyTemperBtn.onLMouseDown.bind( self.__domesticate )
		self.__pyTemperBtn.description = labelGather.getText( "quickbar:petBar", "dspDomesticate" )
		self.__pyTemperBtn.scTag = "PET_DOMESTICATE"
		self.__pyTemperBtn.onMouseEnter.bind( self.__showTip )
		self.__pyTemperBtn.onMouseLeave.bind( self.__hideTip )

		self.__temperStates = MapList()
		self.__temperStates[81] = ( labelGather.getText( "quickbar:petBar", "tipsHappy" ),
									"guis/general/quickbar/petbar/happybtn.tga" )
		self.__temperStates[50] = ( labelGather.getText( "quickbar:petBar", "tipsMorose" ),
									"guis/general/quickbar/petbar/gloomybtn.tga" )
		self.__temperStates[0] = ( labelGather.getText( "quickbar:petBar", "tipsAngry" ),
									"guis/general/quickbar/petbar/angrybtn.tga" )

		pyFollowBtn = SelectableButton( bar.followBtn )							# 命令跟随按钮
		pyFollowBtn.setStatesMapping( UIState.MODE_R1C3 )
		pyFollowBtn.autoSelect = False
		pyFollowBtn.description = labelGather.getText( "quickbar:petBar", "dspFollow" )
		pyFollowBtn.scTag = "PET_TO_FOLLOW"
		pyFollowBtn.actMode = csdefine.PET_ACTION_MODE_FOLLOW
		pyFollowBtn.onLMouseDown.bind( self.__setToFollow )
		pyFollowBtn.onLMouseDown.bind( self.__hideTip, True )
		pyFollowBtn.onMouseEnter.bind( self.__showTip )
		pyFollowBtn.onMouseLeave.bind( self.__hideTip )

		pyKeepBtn = SelectableButton( bar.stopBtn )								# 命令停留按钮
		pyKeepBtn.setStatesMapping( UIState.MODE_R1C3 )
		pyKeepBtn.autoSelect = False
		pyKeepBtn.description = labelGather.getText( "quickbar:petBar", "dspStay" )
		pyKeepBtn.scTag = "PET_TO_KEEPING"
		pyKeepBtn.actMode = csdefine.PET_ACTION_MODE_KEEPING
		pyKeepBtn.onLMouseDown.bind( self.__setToKeeping )
		pyKeepBtn.onLMouseDown.bind( self.__hideTip, True )
		pyKeepBtn.onMouseEnter.bind( self.__showTip )
		pyKeepBtn.onMouseLeave.bind( self.__hideTip )

		self.__pyActionBtnArray = SelectorGroup( pyFollowBtn, pyKeepBtn )

		self.__pyTussleMenu = PetTussleMenu( bar.tussleBtn_0.icon )

		self.__initPetQBItems( bar )


	def __initPetQBItems( self, bar ):
		self.__pyItems = [None] * csconst.QB_PET_ITEM_COUNT						# 首先分配快捷格总数（modified by hyw -- 2008.07.17）
		self.__pyAutoItems = {}
		for name, item in bar.children :
			if "item_" in name :
				index = int( name.split( "_" )[1] )								# item 的名称必须为 item_XX
				pyItem = PBItem( item.icon, index )
				pyItem.description = ITEM_DSPS[0]
				self.__pyItems[index] = pyItem
			elif "autoItem_" in name :
				index = int( name.split( "_" )[1] )
				pyItem= PetDrugItem( item.icon, self )
				pyItem.gbIndex = csdefine.QB_AUTO_SPELL_INDEX + index
				pyItem.description = ITEM_DSPS[index]
				pyItem.gbCopy = True
				self.__pyAutoItems[pyItem.gbIndex] = pyItem
			else :
				continue
			pyItem.onLMouseDown.bind( self.__onBarMouseDown )
			pyItem.onMouseEnter.bind( self.__onBarMouseEnter )
			pyItem.onMouseLeave.bind( self.__onBarMouseLeave )
		assert None not in self.__pyItems											# UI 格子数量必须与指定个数匹配

	# -------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_PET_ACTION_CHANGED"] = self.__onActionChnaged		# 行为模式改变时被调用
		self.__triggers["EVT_ON_PET_TUSSLE_CHANGED"] = self.__onTussleChanged		# 战斗模式改变时被调用
		self.__triggers["EVT_ON_PET_UPDATE_QUICKITEM"] = self.__onUpdateQBItem		# 技能图标改变时被调用
		self.__triggers["EVT_ON_PET_ATTR_CHANGED"] = self.__onPetJoyancyChanged		# 宠物属性改变时被调用
		self.__triggers["EVT_ON_PET_REMOVE_SKILL"] = self.__onPetRemoveSkill		# 当移除宠物某个技能时
		self.__triggers["EVT_ON_PET_CLEAR_SKILLS"] = self.__clearPetBarSkills		# 清空宠物快捷栏技能
		self.__triggers["EVT_ON_SHOW_PET_INVALID_COVER"] = self.__coverInvalidItem	# 点击不可用技能时显示红色边框
		self.__triggers["EVT_ON_QUICKBAR_UPDATE_ITEM"] = self.__onUpdateItem		# 更新自动回血、回蓝栏		
		for trigger in self.__triggers :
			ECenter.registerEvent( trigger, self )

	def __unregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	# -----------------------------------------------
	def __showTip( self, pyBtn ):
		"""
		显示按钮功能提示
		"""
		dsp = pyBtn.description
		if hasattr( pyBtn, "scTag" ) and rds.shortcutMgr.getShortcutInfo( pyBtn.scTag ).shortcutString != "" :
			if pyBtn.scTag == "PET_DOMESTICATE" :
				dsp = dsp + labelGather.getText( "quickbar:petBar", "tipsKeyClew" ) % rds.shortcutMgr.getShortcutInfo( pyBtn.scTag ).shortcutString + \
				labelGather.getText( "quickbar:petBar", "tipsKeyDom" ) + self.__temperText
			else:
				dsp = dsp + labelGather.getText( "quickbar:petBar", "tipsKeyClew" ) % rds.shortcutMgr.getShortcutInfo( pyBtn.scTag ).shortcutString
		toolbox.infoTip.showToolTips( self, dsp )

	def __hideTip( self ):
		"""
		隐藏按钮功能提示
		"""
		toolbox.infoTip.hide()

	def __onBarMouseDown( self ) :
		"""
		鼠标点击则浮动框消失
		"""
		toolbox.infoTip.hide()

	def __onBarMouseEnter( self, pyItem ) :
		"""
		鼠标进入则浮动框出现
		"""
		toolbox.infoTip.showItemTips( self, pyItem.description )

	def __onBarMouseLeave( self ) :
		"""
		鼠标离开则浮动框消失
		"""
		toolbox.infoTip.hide()

	# -------------------------------------------------
	def __attackTarget( self ) :
		"""
		攻击目标
		"""
		BigWorld.player().pcg_attackTarget()
		return True

	def __setToFollow( self ) :
		"""
		设置为跟随
		"""
		BigWorld.player().pcg_setActionMode( csdefine.PET_ACTION_MODE_FOLLOW )
		return True

	def __setToKeeping( self ) :
		"""
		设置为跟随/停留模式
		"""
		BigWorld.player().pcg_setActionMode( csdefine.PET_ACTION_MODE_KEEPING )
		return True

	def __domesticate( self ) :
		"""
		驯养
		"""
		actEpitome = BigWorld.player().pcg_getActPetEpitome()
		if actEpitome is None : return
		actEpitome.addJoyancy()
		return True

	def __onShowTussleDsp( self, pyTussleBtn ):
		statusVal = pyTussleBtn.statusVal
		tussleDsp = STATUS_INFOS.get( statusVal, "" )[0]
		toolbox.infoTip.showToolTips( self, tussleDsp )

	def __setTussleStatus( self, pyTussleBtn ):
		"""
		设置战斗状态
		"""
		if pyTussleBtn is None:return
		statusVal = pyTussleBtn.statusVal
		BigWorld.player().pcg_setTussleMode( statusVal )
		return True

	# -------------------------------------------------
	def __onActionChnaged( self, mode ) :
		"""
		当行为模式改变时被调用
		"""
		for pyActBtn in self.__pyActionBtnArray.pySelectors :
			if pyActBtn.actMode == mode :
				self.__pyActionBtnArray.pyCurrSelector = pyActBtn

	def __onTussleChanged( self, mode ) :
		"""
		战斗模式改变成功,则更改固定状态按钮
		"""
		self.__pyTussleMenu.setTussleMode( mode )

	def __onUpdateQBItem( self, index, qbItem ) :
		"""
		当技能快捷栏改变时被调用
		"""
		self.__pyItems[index].update( qbItem )

	def __onPetJoyancyChanged( self, dbid, attr ):
		"""
		快乐度改变时被调用
		"""
		if attr != "joyancy" : return
		self.__updateTemperBtn()

	def __onPetRemoveSkill( self, skillID ):
		for pyItem in self.__pyItems:
			itemInfo = pyItem.itemInfo
			if itemInfo and itemInfo.id == skillID:
				pyItem.update( None )
				break

	def __clearPetBarSkills( self ):
		"""
		"""
		for pyItem in self.__pyItems:
			pyItem.update( None )

	# -------------------------------------------------
	def __updateTemperBtn( self ) :
		"""
		根据出征宠物快乐度，以不同状态显示宠物情绪表现图标
		"""
		pet = BigWorld.player().pcg_getActPet()
		if pet is None : return
		for segValue, ( label, texture ) in self.__temperStates.items() :
			if pet.joyancy < segValue : continue
			self.__temperText = labelGather.getText( "quickbar:petBar", "tipsMood" )%( PL_NewLine.getSource(), label )
			self.__pyTemperBtn.texture = texture
			if self.__pyTemperBtn.isMouseHit() :
				self.__showTip( self.__pyTemperBtn )
			break

	def __coverInvalidItem( self, skillID ) :
		"""
		点击不可用技能时显示红色边框
		"""
		BigWorld.cancelCallback( self.__cancelCoverCBID )
		self.__hideInvalidCovers()
		for pyItem in self.__pyItems :
			if pyItem.itemInfo is None : continue
			if pyItem in self.__invalidItems : continue
			if pyItem.itemInfo.id == skillID :
				self.__invalidItems.append( pyItem )
				toolbox.itemCover.showInvalidItemCover( pyItem )
		self.__cancelCoverCBID = BigWorld.callback( 1, self.__hideInvalidCovers )		# 标记在1秒后自动隐藏

	def __onUpdateItem( self, gbIndex, itemInfo ):
		player = BigWorld.player()
		pyAutoItem = self.__pyAutoItems.get( gbIndex, None )
		if pyAutoItem is None:return
		pyAutoItem.update( itemInfo )
		if itemInfo is None:
			pyAutoItem.description = ITEM_DSPS[gbIndex - csdefine.QB_AUTO_SPELL_INDEX]
		if gbIndex == csdefine.QB_AUTO_SPELL_INDEX + 10:
			player.qb_setPetRecordRedMedication( itemInfo )
		elif gbIndex == csdefine.QB_AUTO_SPELL_INDEX + 11:
			player.qb_setPetRecordBlueMedication( itemInfo )

	def __hideInvalidCovers( self ) :
		"""
		隐藏不可用技能的红色边框
		"""
		for pyItem in self.__invalidItems :
			toolbox.itemCover.hideItemCover( pyItem )
		self.__invalidItems = []

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		for pyItem in self.__pyItems:
			pyItem.update( None )
		for pyAutoItem in self.__pyAutoItems.itervalues():
			pyAutoItem.update( None )
		self.visible = False
		toolbox.infoTip.hideOperationTips( 0x0049 )

	def onPetEnterWorld( self ) :
		outPet = BigWorld.player().pcg_getActPet()
		self.__updateTemperBtn()
#		toolbox.infoTip.showOperationTips( 0x0049, self.__pyTussleMenu.pySTBtn )
