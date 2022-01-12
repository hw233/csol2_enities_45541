# -*- coding: gb18030 -*-
#
# $Id: PBItem.py,v 1.7 2008-07-21 02:57:41 huangyongwei Exp $

"""
implement quick item class
2006/07/15: writen by huangyongwei
"""

import csdefine
from guis import *
from guis.controls.Item import Item
from guis.controls.StaticText import StaticText
from guis.controls.CircleCDCover import CircleCDCover as CDCover
from guis.otheruis.AnimatedGUI import AnimatedGUI
from Helper import courseHelper
from LabelGather import labelGather
from SKItemDetector import SKIDetector
import csconst
import csstatus

class PBItem( Item ):
	__cc_colors = {}
	__cc_colors[ "default" ] = ( 255, 255, 255, 255 )
	__cc_colors[ "unableUse" ] = ( 150, 70, 70, 255 )

	def __init__( self, item, index ):
		Item.__init__( self, item )
		self.dragMark = DragMark.PET_QUICK_BAR
		self.__initialize( item )
		self.__index = index

		self.__triggers = {}
		self.__registerTriggers()

		rds.shortcutMgr.setHandler( "PET_QB_GRID_%i" % ( index + 1 ), self.spellItem )

	def __initialize( self, item ) :
		self.focus = True
		self.crossFocus = True
		self.dragFocus = True
		self.dropFocus = True

		self.__pyLbAmount = StaticText( item.lbAmount )
		self.__pyLbAmount.font = "system_small.font"
		self.__pyLbAmount.color = 255, 228, 193, 255
		self.__pyLbAmount.text = ""
		self.autoUseSign = False

		self.__pyCDCover = CDCover( item.circleCover, self )
		self.__pyCDCover.crossFocus = False

		self.__pyOverCover = AnimatedGUI( item.overCover )
		self.__pyOverCover.initAnimation( 1, 8, ( 2, 4 ) )					# 动画播放一次，共8帧
		self.__pyOverCover.cycle = 0.4										# 循环播放一次的持续时间，单位：秒
		self.__pyCDCover.onUnfreezed.bind( self.__pyOverCover.playAnimation )

		self.clear()

	def dispose( self ) :
		Item.dispose( self )
		self.__pyCDCover.dispose()
		self.__deregisterTriggers()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_PET_BEGIN_COOLDOWN"] = self.__beginCooldown
		self.__triggers["EVT_ON_PET_MP_CHANGE"]  	 = self.__onMPChanded
		for trigger in self.__triggers.iterkeys() :
			ECenter.registerEvent( trigger, self )

	def __deregisterTriggers( self ) :
		for trigger in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( self, trigger )
		self.__triggers = {}

	# -------------------------------------------------
	def __cancelCooldown( self ) :
		if self.itemInfo is not None :
			self.itemInfo.unlock()
		self.__pyCDCover.reset( 0 )

	def __beginCooldown( self, cooldownType, lastTime ) :
		if self.itemInfo is None : return
		if self.itemInfo.isCooldownType( cooldownType ) :
			cdInfo = self.itemInfo.getCooldownInfo()
			self.__pyCDCover.unfreeze( *cdInfo )

	def __onMPChanded( self, mp, mpMax ) :
		"""
		宠物MP 改变会通知此处
		"""
		self.updateIconState()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def checkForDetection_( self, newItemInfo ) :
		"""
		检查是否需要从探测器中更新
		"""
		SKIDetector.unbindPyItem( self )						# 格子清空则从探测器中清除

		if newItemInfo is None : return

		spell = newItemInfo.getSpell()
		if spell is None : return

		rangeMax = csconst.PET_FORCE_FOLLOW_RANGE
		SKIDetector.bindPyItem( self, ( "PET", rangeMax ) )		# 添加到探测器

	# -------------------------------------------------
	def onDragStart_( self, pyDragged ) :
		if pyDragged.itemInfo is None: 
			toolbox.itemCover.normalizeItem()
			return False
		Item.onDragStart_( self, pyDragged )
		return True

	def onDrop_( self, pyTarget, pyDropped ):
		Item.onDrop_( self, pyTarget, pyDropped )
		if pyDropped.itemInfo is None : return True
		player = BigWorld.player()
		if pyDropped.dragMark == DragMark.PETSKILL_BAR: 					# 从宠物技能面板
			player.pcg_updatePetQBItem( self.index, pyDropped.itemInfo.baseItem )
		elif pyDropped.dragMark == DragMark.PET_QUICK_BAR:					# 宠物快捷栏之间拖放
			player.pcg_exchangePetQBItem( pyDropped.index, self.index )
		return True

	def onDragStop_( self, pyDragged ):
		Item.onDragStop_( self, pyDragged )
		if ruisMgr.isMouseHitScreen():
			BigWorld.player().pcg_updatePetQBItem( self.index, None )

	def onLClick_( self, mods ) :
		Item.onLClick_( self, mods )
		self.spellItem()
		return

	def onRClick_( self, mods ) :
		Item.onRClick_( self, mods )
		BigWorld.player().pcg_toggleAutoUsePetQBItem( self.index )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		"""
		triggered by base
		"""
		self.__triggers[macroName]( *args )

	# -------------------------------------------------
	def update( self, itemInfo ) :
		self.checkForDetection_( itemInfo )
		Item.update( self, itemInfo )
		if itemInfo is not None :
			self.__pyLbAmount.text = ""
			if itemInfo.countable and itemInfo.amount > 1 :
				self.__pyLbAmount.text = str( itemInfo.amount )
			cdInfo = itemInfo.getCooldownInfo()
			self.__pyCDCover.unfreeze( *cdInfo )
			self.updateIconState()
		else :
			# 如果没有物品了当然就是正常显示
			self.__pyCDCover.reset( 0 )
			self.color = PBItem.__cc_colors[ "default" ]

	# -------------------------------------------------
	def spellItem( self ):
		if self.itemInfo is not None :
			self.itemInfo.spell()
		return True

	def clear( self ) :
		"""
		clean the item
		"""
		Item.clear( self )
		self.__pyLbAmount.text = ""
		self.__cancelCooldown()
		self.autoUseSign = False
		SKIDetector.unbindPyItem( self )						# 从探测器移除

	def updateIconState( self ):
		"""
		更新快捷栏图标的状态  红色，绿色
		"""
		player = BigWorld.player()
		itemInfo = self.itemInfo

		if itemInfo is not None :
			#显示/取消自动释放的标志
			if itemInfo.autoUse:
				# 自动攻击状态
				self.autoUseSign = True
			else:
				self.autoUseSign = False
			#设置图标的颜色
			state = itemInfo.validTarget()
			if state in [ csstatus.SKILL_INTONATING, csstatus.SKILL_NOT_READY, csstatus.SKILL_GO_ON ]:
				self.color = PBItem.__cc_colors[ "default" ]
				return
			elif state == csstatus.SKILL_TOO_FAR :
				# 距离远要单列出来
				if player.pcg_getActPet() and player.position.distTo( player.pcg_getActPet().position ) > csconst.PET_FORCE_FOLLOW_RANGE:
					# 距离太远红色
					self.color = PBItem.__cc_colors[ "unableUse" ]
					return
			else:
				# 不能使用，显示红色
				self.color = PBItem.__cc_colors[ "unableUse" ]
				return

		# 正常显示
		self.color = PBItem.__cc_colors[ "default" ]

	def onDetectorTrigger( self ) :
		"""目标距离侦测回调"""
		self.updateIconState()

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onDescriptionShow_( self ) :
		if self.itemInfo is None :
			self.description = labelGather.getText( "quickbar:pbItem", "tipsSkillItem" )
		Item.onDescriptionShow_( self )

	def onDescriptionHide_( self ) :
		"""
		当鼠标离开时被调用，这里因此描述
		"""
		Item.onDescriptionHide_( self )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getIndex( self ) :
		return self.__index

	def _setAutoUseSign( self , show ):
		"""
		设置自动释放的标志（边框出现旋转的线条）
		"""
		self.gui.y_light.visible = show

	def _getAutoUseSign( self ):
		"""
		查看是否显示自动释放的标志
		"""
		return self.gui.y_light.visible

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	index = property( _getIndex )
	autoUseSign = property( _getAutoUseSign, _setAutoUseSign)			#　获取和设置自动使用标志的显示