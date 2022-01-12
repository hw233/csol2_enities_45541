# -*- coding: gb18030 -*-

import BigWorld
import csstatus
import csdefine
from guis import *
import event.EventCenter as ECenter
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.controls.Button import Button
from QBItem import QBItem
import skills as Skill
from ItemsFactory import SkillItem
from guis.otheruis.AnimatedGUI import AnimatedGUI
from guis.controls.CircleCDCover import CircleCDCover as CDCover


class PostureSKItem( QBItem ):
	def __init__( self, item, pyBinder = None ):
		QBItem.__init__( self, item, pyBinder = None )
		self.mouseHighlight = False

	def onLClick_( self, mods ):
		QBItem.onLClick_( self, mods )
		toolbox.itemCover.hideItemCover( self )
		ECenter.fireEvent( "EVT_ON_HIDE_POSTURE_MENU", self.itemInfo.id )

	def update( self, itemInfo, isNotInit = True ):
		QBItem.update( self, itemInfo, isNotInit )
		self.focus = True	# 使得黑白色也能点击

	def onDragStart_( self, pyDragged ):
		pass

	def onRClick_( self, mods ):
		pass

	def startFlash( self ):
		pass

	def stopFlash( self ):
		pass

	def onMouseEnter_( self ):
		QBItem.onMouseEnter_( self )
		# 高亮显示
		toolbox.itemCover.showItemCover( self )

	def onMouseLeave_( self ):
		QBItem.onMouseLeave_( self )
		toolbox.itemCover.hideItemCover( self )

class PostureBar( PyGUI ):
	"""
	心法切换快捷栏
	"""
	CLASS_MAP = {
			csdefine.CLASS_FIGHTER: ( 322458005, 322459005 ),
			csdefine.CLASS_SWORDMAN: ( 322460005, 322461005 ),
			csdefine.CLASS_ARCHER: ( 322462005, 322463005 ),
			csdefine.CLASS_MAGE: ( 322464005, 322465005 ),
			}

	POSTURE_MAP = {
			csdefine.ENTITY_POSTURE_NONE: ( labelGather.getText( "quickbar:postureBar", "tipsNone" ), "" ),
			csdefine.ENTITY_POSTURE_VIOLENT: ( labelGather.getText( "quickbar:postureBar", "tipsViolent" ),
												"guis/general/quickbar/posturebar/skill_defend_031.dds" ),
			csdefine.ENTITY_POSTURE_DEFENCE: ( labelGather.getText( "quickbar:postureBar", "tipsDefence" ),
												"guis/general/quickbar/posturebar/skill_defend_032.dds" ),
			csdefine.ENTITY_POSTURE_DEVIL_SWORD: ( labelGather.getText( "quickbar:postureBar", "tipsDevil" ),
												"guis/general/quickbar/posturebar/skill_defend_033.dds" ),
			csdefine.ENTITY_POSTURE_SAGE_SWORD: ( labelGather.getText( "quickbar:postureBar", "tipsSage" ),
												"guis/general/quickbar/posturebar/skill_defend_034.dds" ),
			csdefine.ENTITY_POSTURE_SHOT: ( labelGather.getText( "quickbar:postureBar", "tipsShot" ),
												"guis/general/quickbar/posturebar/skill_defend_035.dds" ),
			csdefine.ENTITY_POSTURE_PALADIN: ( labelGather.getText( "quickbar:postureBar", "tipsPaladin" ),
												"guis/general/quickbar/posturebar/skill_defend_036.dds" ),
			csdefine.ENTITY_POSTURE_MAGIC: ( labelGather.getText( "quickbar:postureBar", "tipsMagic" ),
												"guis/general/quickbar/posturebar/skill_defend_037.dds" ),
			csdefine.ENTITY_POSTURE_CURE: ( labelGather.getText( "quickbar:postureBar", "tipsCure" ),
												"guis/general/quickbar/posturebar/skill_defend_038.dds" ),
			}

	def __init__( self, bar ) :
		PyGUI.__init__( self, bar )

		self.__initialize( bar )
		self.__triggers = {}
		self.__registerTriggers()

	def __initialize( self, bar ):
		self.__pyPostureItem1 = PostureSKItem( bar.posture_1 )	# 心法1
		self.__pyPostureItem2 = PostureSKItem( bar.posture_2 )	# 心法2
		self.__pyBtnPosture = Button( bar.btnPosture )			# 主按钮
		self.__pyBtnPosture.onLClick.bind( self.__showPostureMenu )
		self.__pyBtnPosture.onMouseEnter.bind( self.__showTip )
		self.__pyBtnPosture.onMouseLeave.bind( self.__hideTip )

		self.__pyCDCover = CDCover( bar.btnPosture.circleCover, self.__pyBtnPosture )
		self.__pyCDCover.crossFocus = False

		self.__pyOverCover = AnimatedGUI( bar.btnPosture.overCover )
		self.__pyOverCover.initAnimation( 1, 8, ( 2, 4 ) )				# 动画播放一次，共8帧
		self.__pyOverCover.cycle = 0.4									# 循环播放一次的持续时间，单位：秒
		self.__pyCDCover.onUnfreezed.bind( self.__pyOverCover.playAnimation )

		self.__itemFrame1 = PyGUI( bar.itemFrame1 )
		self.__itemFrame2 = PyGUI( bar.itemFrame2 )

		self.__hidePostureItems()	# 先隐藏心法菜单

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_HIDE_POSTURE_MENU"]			= self.__onHideMenu			# 隐藏心法菜单
		self.__triggers["EVT_ON_PLAYER_POSTURE_CHANGED"]	= self.__onPostureChange	# 姿态改变
		self.__triggers["EVT_ON_PLAYERROLE_ADD_SKILL"] 		= self.__onAddSkill			# 添加技能
		self.__triggers["EVT_ON_PLAYERROLE_UPDATE_SKILL"]	= self.__onSkillUpdate		# 更新技能
		self.__triggers["EVT_ON_PLAYERROLE_REMOVE_SKILL"]	= self.__onSkillRemove		# 移除技能
		self.__triggers["EVT_ON_ROLE_BEGIN_COOLDOWN"] 		= self.__beginCooldown		# 技能CD特效
		for key in self.__triggers.iterkeys():
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ):
		for key in self.__triggers.iterkeys():
			ECenter.unregisterEvent( key, self )

	def __initPostureSkItems( self ):
		player = BigWorld.player()
		pclass = player.getClass()
		itemInfo_1, isHas_1 = self.__getItemInfo( self.CLASS_MAP[pclass][0] )
		itemInfo_2, isHas_2 = self.__getItemInfo( self.CLASS_MAP[pclass][1] )
		self.__pyPostureItem1.update( itemInfo_1, isHas_1 )
		self.__pyPostureItem2.update( itemInfo_2, isHas_2 )

	def __showPostureMenu( self ):
		"""
		显示心法菜单
		"""
		if self.pyTopParent.isLocked():
			BigWorld.player().statusMessage( csstatus.QB_HAS_LOCKED )
			return 
		if self.__pyPostureItem1.visible and self.__pyPostureItem2.visible:
			self.__hidePostureItems()
			return
		self.__initPostureSkItems()
		self.__pyPostureItem1.visible = True
		self.__pyPostureItem2.visible = True
		self.__itemFrame1.visible = True
		self.__itemFrame2.visible = True

	def __hidePostureItems( self ):
		self.__pyPostureItem1.visible = False
		self.__pyPostureItem2.visible = False
		self.__itemFrame1.visible = False
		self.__itemFrame2.visible = False

	def __getItemInfo( self, initSkillID ):
		mapSkid, isHas = self.__getMapSkillID( initSkillID )
		skill = Skill.getSkill( mapSkid )
		itemInfo = SkillItem( skill )
		return itemInfo, isHas

	def __getMapSkillID( self, initSkillID ):
		player = BigWorld.player()
		for skillID in player.skillList_:
			if skillID/1000 == initSkillID/1000:
				return skillID, True
		return initSkillID, False

	def __onAddSkill( self, skillInfo ):
		"""
		添加技能触发
		"""
		if skillInfo is None:return
		self.__initPostureSkItems()

	def __onSkillUpdate( self, oldSkillID, skillInfo ):
		"""
		更新技能触发
		"""
		if skillInfo is None: return
		self.__initPostureSkItems()

	def __onSkillRemove( self, skillInfo ):
		"""
		移除技能触发
		"""
		if skillInfo is None: return
		self.__initPostureSkItems()

	def __onHideMenu( self, skillID ):
		"""
		隐藏心法菜单
		"""
		player = BigWorld.player()
		if not skillID in player.skillList_:
			player.statusMessage( csstatus.SKILL_NOT_LEARN_POSTURE )
		self.__hidePostureItems()

	def __onPostureChange( self, posture, oldPosture ):
		"""
		姿态改变
		"""
		self.__setPosture( posture )

	def __setPosture( self, posture ):
		self.__pyBtnPosture.dsp = self.POSTURE_MAP[posture][0]
		self.__pyBtnPosture.texture = self.POSTURE_MAP[posture][1]

	def __showTip( self, pyBtn ):
		"""
		显示提示消息
		"""
		toolbox.infoTip.showToolTips( pyBtn, pyBtn.dsp )
		toolbox.itemCover.showItemCover( self.__pyBtnPosture )

	def __hideTip( self ) :
		"""
		隐藏提示消息
		"""
		toolbox.infoTip.hide()
		toolbox.itemCover.hideItemCover( self.__pyBtnPosture )

	def __beginCooldown( self, cooldownType, lastTime ) :
		itemInfo = self.__pyPostureItem1.itemInfo	# 任取一个心法技能
		if itemInfo is None: return
		if itemInfo.isCooldownType( cooldownType ):
			self.__pyCDCover.visible = True
			cdInfo = itemInfo.getCooldownInfo()
			self.__pyCDCover.unfreeze( *cdInfo )

	def __isSubItemsMouseHit( self ):
		if self.__pyPostureItem1.isMouseHit():
			return True
		if self.__pyPostureItem2.isMouseHit():
			return True
		if self.__pyBtnPosture.isMouseHit():
			return True
		return False

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.__triggers[eventMacro]( *args )

	def onEnterWorld( self ):
		"""
		角色进入世界时被调用
		"""
		player = BigWorld.player()
		self.__initPostureSkItems()
		self.__setPosture( player.posture )
		self.visible = True

	def onLeaveWorld( self ) :
		"""
		角色离开世界时被调用
		"""
		self.visible = False

	def isMouseHit( self ):
		return self.__isSubItemsMouseHit()
