# -*- coding: gb18030 -*-
#
# $Id: self.py, fangpengjun Exp $

"""
implement self window class
"""
from guis import *
from LabelGather import labelGather
from guis.controls.Control import Control
from guis.controls.ProgressBar import HProgressBar as ProgressBar
from guis.controls.TabCtrl import TabPanel
from guis.controls.StaticText import StaticText
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.SkillItem import SkillItem as SKItem
from ItemsFactory import SkillItem as SkItemInfo
from AttrRebuild import AttrRebuild
from TalismanModelRender import TalismanModelRender
import ItemTypeEnum
import BigWorld

class TalisPanel( TabPanel ):
	"""
	法宝界面
	"""
	__grade__text = { ItemTypeEnum.TALISMAN_COMMON :  labelGather.getText( "PlayerProperty:TalisPanel", "talisman_common" ),\
						ItemTypeEnum.TALISMAN_DEITY : labelGather.getText( "PlayerProperty:TalisPanel", "talisman_deity" ),\
						ItemTypeEnum.TALISMAN_IMMORTAL : labelGather.getText( "PlayerProperty:TalisPanel", "talisman_immortal" ) }

	def __init__( self, tabPanel ):
		TabPanel.__init__( self, tabPanel )
		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( tabPanel )

	def __initialize( self, tabPanel ):
		self.__taNameText = StaticText( tabPanel.taName )
		self.__taNameText.text = ""											# 名字

		self.__taGradeText = StaticText( tabPanel.taGrade )
		self.__taGradeText.text = ""										# 品质

		self.__taLevelText = StaticText( tabPanel.taLevel )
		self.__taLevelText.text = ""										# 级别

		self.__roleExpText = StaticText( tabPanel.roleExp )
		self.__roleExpText.text = ""										# 经验

		self.__taSkillLevelText = StaticText( tabPanel.taSkillLevel )
		self.__taSkillLevelText.text = ""										# 技能等级

		self.__roleSkillExpText = StaticText( tabPanel.roleSkillExp )
		self.__roleSkillExpText.text = ""									# 潜能

		self.__taExpItem = ExpItem( tabPanel.expItem )
		self.__taSkillExpItem = ExpItem( tabPanel.expSkillItem )					# 两个经验条

		self.__pyBtnUpQuality = Button( tabPanel.btnUpQuality ) #提升品质
		self.__pyBtnUpQuality.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnUpQuality.onLClick.bind( self.__onUpQuality )
		labelGather.setPyBgLabel( self.__pyBtnUpQuality, "PlayerProperty:TalisPanel", "btnUpQuality" )

		self.__pyBtnExtrExp = HButtonEx( tabPanel.btnExtrExp ) #吸经验
		self.__pyBtnExtrExp.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnExtrExp.onLClick.bind( self.__onExtrExp )
		labelGather.setPyBgLabel( self.__pyBtnExtrExp, "PlayerProperty:TalisPanel", "btnExtrExp" )

		self.__pyBtnWashAttr = HButtonEx( tabPanel.btnWashAttr ) #洗属性
		self.__pyBtnWashAttr.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnWashAttr.onLClick.bind( self.__onWashAttr )
		labelGather.setPyBgLabel( self.__pyBtnWashAttr, "PlayerProperty:TalisPanel", "btnWashAttr" )

#		self.__pyWasSkillBtn = Button( tabPanel.washSkillBtn ) #洗技能
#		self.__pyWasSkillBtn.setStatesMapping( UIState.MODE_R4C1 )
#		self.__pyWasSkillBtn.onLClick.bind( self.__onWashSkill )

		self.__pyBtnUpgradeSk = Button( tabPanel.btnUpgradeSk ) #升级技能
		self.__pyBtnUpgradeSk.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnUpgradeSk.onLClick.bind( self.__onUpgradeSkill )
		labelGather.setPyBgLabel( self.__pyBtnUpgradeSk, "PlayerProperty:TalisPanel", "btnUpgradeSk" )

		self.__pyBtnLeft = Button( tabPanel.btnLeft )
		self.__pyBtnLeft.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnLeft.onLMouseDown.bind( self.__turnLeft )

		self.__pyBtnRight = Button( tabPanel.btnRight )
		self.__pyBtnRight.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnRight.onLMouseDown.bind( self.__turnRight )

		self.__modelRender = TalismanModelRender( tabPanel.model )						# 模型
		self.__skItem = SkillItem( tabPanel.taItem.item )								# 技能
		self.__itemInfo = None												# 当前itemInfo

		self.__pyAttrRebuild = AttrRebuild( self ) #法宝属性改造
		labelGather.setLabel( tabPanel.taExpText, "PlayerProperty:TalisPanel", "taExpText" )
		labelGather.setLabel( tabPanel.roleExpText, "PlayerProperty:TalisPanel", "roleExpText" )
		labelGather.setLabel( tabPanel.skLevelText, "PlayerProperty:TalisPanel", "skLevelText" )
		labelGather.setLabel( tabPanel.skExpText, "PlayerProperty:TalisPanel", "skExpText" )
		labelGather.setLabel( tabPanel.rolePotenText, "PlayerProperty:TalisPanel", "rolePotenText" )
		labelGather.setLabel( tabPanel.infoFrm.bgTitle.stTitle, "PlayerProperty:TalisPanel","taliInfo" )
		labelGather.setLabel( tabPanel.skillFrm.bgTitle.stTitle, "PlayerProperty:TalisPanel","skillInfo" )


		self.__turnModelCBID = 0											# 让模型不停旋转的callback ID
 	# ----------------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_ROLE_EXP_CHANGED"] = self.__onRoleExpChange
		self.__triggers["EVT_ON_ROLE_POTENTIAL_CHANGED"] = self.__onRolePotentialChange
		self.__triggers["EVT_ON_TALISMAN_LV_UP"] = self.__onLevelChange
		self.__triggers["EVT_ON_TALISMAN_SK_UP"] = self.__onSkillChange
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __unregisterTriggers( self ):
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )

	def __onRoleExpChange( self, inreasedExp, reason ):
		"""
		玩家经验改变时调用
		"""
		value = BigWorld.player().getEXP()
		self.__roleExpText.text = "%d" % value
		self.__reBtnState()													# 刷新按钮状态

	def __onRolePotentialChange( self, oldValue, newValue ):
		"""
		玩家潜能改变时调用
		"""
		self.__roleSkillExpText.text = labelGather.getText( "PlayerProperty:TalisPanel", "proPoint" ) % newValue						# 潜能
		self.__reBtnState() 												# 刷新按钮状态

	def __onTalBaseChange( self ):
		"""
		法宝基础信息改变时调用
		"""
		self.__taNameText.text = self.__itemInfo.name()						# 名字
		grade = self.__itemInfo.baseItem.getGrade()							# 品质

		if grade in self.__grade__text:
			self.__taGradeText.text = self.__grade__text[ grade ]
		else:
			pass

	def __onSkillChange( self ):
		"""
		法宝技能改变时调用
		"""
		sk = self.__itemInfo.baseItem.getSpell()
		if sk:
			skItem = SkItemInfo( sk )
			self.__skItem.update( skItem )
			self.__taSkillLevelText.text = labelGather.getText( "PlayerProperty:TalisPanel", "levelText" ) % sk.getLevel()
			self.__taSkillExpItem.update( ( self.__itemInfo.baseItem.getPotential(), self.__itemInfo.baseItem.getMaxPotential() ) )
		else:
			self.__skItem.update( None )
			self.__taSkillLevelText.text = ""
			self.__taSkillExpItem.update( ( 0, 0 ) )						# 技能条

		self.__reBtnState()

	def __onLevelChange( self ):
		"""
		法宝级别改变时调用
		"""
		self.__taLevelText.text = labelGather.getText( "PlayerProperty:TalisPanel", "levelText" ) % self.__itemInfo.baseItem.getLevel()
		self.__taExpItem.update( ( self.__itemInfo.baseItem.getExp(), self.__itemInfo.baseItem.getMaxExp() ) )
		self.__reBtnState()

	def __onUpQuality( self ): #
		"""
		提升法宝品质
		"""
		player = BigWorld.player()
		if player is None: return
		player.updateTalismanGrade()

	def __onExtrExp( self ):
		"""
		吸取经验
		"""
		player = BigWorld.player()
		if player is None: return
		player.addTalismanExp()

	def __onWashAttr( self ): #
		"""
		洗法宝属性
		"""
		self.__pyAttrRebuild.show( self )

#	def __onWashSkill( self ): #
#		"""
#		洗法宝技能
#		"""
#		pass

	def __onUpgradeSkill( self ):
		"""
		技能升级
		"""
		player = BigWorld.player()
		if player is None: return
		player.addTalismanPotential()

	def __reBtnState( self ):
		"""
		刷新按钮状态
		"""
		player = BigWorld.player()
		if self.__itemInfo is None:return
		if( None == self.__itemInfo.baseItem.getSpell() or 0 == player.potential or 0 == self.__itemInfo.baseItem.getMaxPotential()):
			self.__pyBtnUpgradeSk.enable = False
		else:
			self.__pyBtnUpgradeSk.enable = True
		if (0 == player.EXP or 0 == self.__itemInfo.baseItem.getMaxExp()):
			self.__pyBtnExtrExp.enable = False
		else:
			self.__pyBtnExtrExp.enable = True

	def __onModelChange( self ):
		"""
		模型
		"""
		modelNum = self.__itemInfo.baseItem.model()
		self.__modelRender.resetModel( modelNum )

#	-----------------------------------------------------------------------------------
	def __onLastKeyUpEvent( self, key, mods ) :
		if key != KEY_LEFTMOUSE : return
		BigWorld.cancelCallback( self.__turnModelCBID )
		LastKeyUpEvent.detach( self.__onLastKeyUpEvent )

	def __turnRight( self ):
		BigWorld.cancelCallback( self.__turnModelCBID )
		self.__turnModel( True )
		LastKeyUpEvent.attach( self.__onLastKeyUpEvent )
		return True

	def __turnLeft( self ):
		BigWorld.cancelCallback( self.__turnModelCBID )
		self.__turnModel( False )
		LastKeyUpEvent.attach( self.__onLastKeyUpEvent )
		return True

	def __turnModel( self, isRTurn ) :
		"""
		turning model on the mirror
		"""
		self.__modelRender.yaw += ( isRTurn and -0.1 or 0.1 )
		if BigWorld.isKeyDown( KEY_LEFTMOUSE ) :
			self.__turnModelCBID = BigWorld.callback( 0.1, Functor( self.__turnModel, isRTurn ) )

	# ---------------------------------------------------------------------
	# protected
	# ---------------------------------------------------------------------
	def onShow( self ) :
		self.__modelRender.enableDrawModel()
		TabPanel.onShow( self )

	def onHide( self ) :
		TabPanel.onHide( self )
		BigWorld.cancelCallback( self.__turnModelCBID )
		self.__modelRender.disableDrawModel()


	# ---------------------------------------------------------------------
	# public
	# ---------------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[ macroName ]( *args )

	def upDateTalisman( self, itemInfo ):
		"""
		更新信息
		"""
		if itemInfo == None: return
		self.__itemInfo = itemInfo
		# 更新所有信息
		player = BigWorld.player()
		self.__roleExpText.text = "%d" % player.EXP							# 经验
		self.__roleSkillExpText.text = "%d" % player.potential				# 潜能
		self.__onTalBaseChange()
		self.__onSkillChange()
		self.__onLevelChange()
		self.__onModelChange()

	def reset( self ):
		self.__itemInfo = None
		self.__taNameText.text = ""
		self.__taGradeText.text = ""
		self.__taLevelText.text =""
		self.__roleExpText.text = ""
		self.__skItem.update( None )
		self.__modelRender.clearModel()

# --------------------------------------------------------
# 经验条
# --------------------------------------------------------
class ExpItem( Control ):

	def __init__( self, item = None ):
		Control.__init__( self, item )
		self.__initItem( item )

	def __initItem( self, item ):
		self.__pyBar = ProgressBar( item.bar )
		self.__pyBar.value = 0.0
		self.__pyBar.clipMode = "RIGHT"

		self.__pyTxtValue = StaticText( item.lbValue )
		self.__pyTxtValue.text = ""

	def onMouseEnter_( self ):
		"""
		鼠标进入时触发
		"""
		Control.onMouseEnter_( self )
		return True

	def update( self, tuple ):
		"""
		更新
		"""
		self.__pyTxtValue.text = "%d / %d" % ( tuple[0], tuple[1] )
		if tuple[1] == 0:
			self.__pyBar.value = 0
		else:
			self.__pyBar.value = float( tuple[0] ) / tuple[1]

# -------------------------------------------------------------------
# 技能图标
# -------------------------------------------------------------------
class SkillItem( SKItem ):

	def __init__( self, item = None, pyBinder = None ):
		SKItem.__init__( self, item, pyBinder )
		self.itemInfo = None
		self.dragMark = DragMark.SKILL_WND

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onRClick_( self, mods ) :
		"""
		右键
		"""
		if self.itemInfo is not None :
			self.itemInfo.spell()
		return True

	def onDragStop_( self, pyDrogged ) :
		"""
		拖放预留
		"""
		return True

	def onDrop_( self,  pyTarget, pyDropped ) :
		"""
		拖放预留
		"""
		return True

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		"""
		更新
		"""
		SKItem.update( self, itemInfo )
		self.itemInfo = itemInfo

	def _getItemInfo( self ):
		return self.__itemInfo

	def _setItemInfo( self, itemInfo ):
		self.__itemInfo = itemInfo

	itemInfo = property( _getItemInfo, _setItemInfo )

#-------------------------------------------------------------------------------------
