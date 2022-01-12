# -*- coding: gb18030 -*-

# bigworld
import GUI
import BigWorld

# common
import csstatus
from bwdebug import ERROR_MSG

# client
import skills
import event.EventCenter as ECenter
from guis import *
from guis.controls.Item import Item
from guis.controls.StaticText import StaticText
from guis.controls.CircleCDCover import CircleCDCover as CDCover
from guis.common.RootGUI import RootGUI
from guis.tooluis.CSRichText import CSRichText
from guis.otheruis.AnimatedGUI import AnimatedGUI
from guis.general.quickbar.SKItemDetector import SKIDetector


class CastIndicator( RootGUI ) :

	def __init__( self ) :
		gui = GUI.load( "guis/general/helper/castindicator/castInd.gui" )
		uiFixer.firstLoadFix( gui )
		RootGUI.__init__( self, gui )
		self.focus = False
		self.movable_ = False										# 不可移动
		self.escHide_ = False										# 不可按esc键关闭
		self.__pyItems = []

		ECenter.registerEvent( "EVT_ON_ROLE_BEGIN_COOLDOWN", self )
		ECenter.registerEvent( "EVT_ON_RESOLUTION_CHANGED", self )
		ECenter.registerEvent( "EVT_ON_KITBAG_REMOVE_ITEM", self )
		ECenter.registerEvent( "EVT_ON_KITBAG_UPDATE_ITEM", self )


	# ----------------------------------------------------------------
	# friend methods
	# ----------------------------------------------------------------
	def shut__( self ) :
		"""通知关闭"""
		self.shutdown()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __beginCooldown( self, cooldownType, lastTime ) :
		"""显示冷却表现"""
		for pyItem in self.__pyItems:
			pyItem.beginCooldown( cooldownType, lastTime )	
		
	def __reSort( self ):
		"""重新排列"""
		self.__clearItems()
		itemWidht = 155	
		for index, pyItem in enumerate( self.__pyItems ):
			self.addPyChild( pyItem )
			pyItem.left = index * itemWidht
			pyItem.top = 0
		self.width = itemWidht * len( self.__pyItems )
		self.__locate()
		
	def __clearItems( self ):
		"""
		"""
		for pyItem in self.__pyItems:
			self.delPyChild( pyItem )
			
	def __locate( self ) :
		"""设置到合适位置"""
		self.center = BigWorld.screenWidth() * 0.5 + 20

	def __onKitbagRemoveItem( self, itemInfo ) :
		"""背包将物品移除"""
		for pyItem in self.__pyItems:
			if pyItem.itemInfo.id == itemInfo.id:
				self.__pyItems.remove( pyItem )
		self.__reSort()
		if len( self.__pyItems ) == 0:	
			self.shutdown()
			
	def __onKitbagUpdateItem( self, itemInfo ):
		"""背包更新物品"""
		for pyItem in self.__pyItems:
			if pyItem.itemInfo.id == itemInfo.id:
				pyItem.pyItem.update( itemInfo )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isMouseHit( self ) :
		for  pyItem in self.__pyItems:
			if pyItem.isMouseHit():
				return True
		return False
		
	def indicate( self, itemInfoList ):
		self.__clearItems()
		self.__pyItems = []
		for text, itemInfo in itemInfoList:
			if text == "" and itemInfo is None:continue
			castPanel = CastPanel( self )
			castPanel.update( text, itemInfo )
			self.__pyItems .append( castPanel)
		self.__reSort()

	def shutdown( self ) :
		"""关闭提示"""
		ECenter.unregisterEvent( "EVT_ON_ROLE_BEGIN_COOLDOWN", self )
		ECenter.unregisterEvent( "EVT_ON_RESOLUTION_CHANGED", self )
#		ECenter.unregisterEvent( "EVT_ON_KITBAG_REMOVE_ITEM", self )
#		ECenter.unregisterEvent( "EVT_ON_KITBAG_UPDATE_ITEM", self )
		self.__pyItems = []
		rds.castIndicator.onShutIndication()
		self.hide()

	def onEvent( self, evtMacro, *args ) :
		"""事件触发"""
		if evtMacro == "EVT_ON_ROLE_BEGIN_COOLDOWN" :
			self.__beginCooldown( *args )
		elif evtMacro == "EVT_ON_RESOLUTION_CHANGED" :
			self.__locate()
		elif evtMacro == "EVT_ON_KITBAG_REMOVE_ITEM" :
			self.__onKitbagRemoveItem( *args )
		elif evtMacro == "EVT_ON_KITBAG_UPDATE_ITEM" :
			self.__onKitbagUpdateItem( *args )

from guis.common.PyGUI import PyGUI			
class	CastPanel( PyGUI ):
	def __init__( self, pyBinder ) :
		gui = GUI.load( "guis/general/helper/castindicator/cidt.gui" )
		uiFixer.firstLoadFix( gui )
		PyGUI.__init__( self, gui )
		self.itemInfo = None
		
		self.__pyItem = CastItem( gui.item, pyBinder )
		self.__pyItem.focus = True
		self.__pyItem.dragFocus = False
		self.__pyItem.dropFocus = False
		
		self.__pyRText = CSRichText( gui.rtInfo )
		self.__pyRText.align = "C"
		
	def beginCooldown( self, cooldownType, lastTime ) :
		"""显示冷却表现"""
		self.__pyItem.beginCooldown( cooldownType, lastTime )
		
	def update( self, text, itemInfo ):
		self.__pyItem.update( itemInfo )
		self.__pyRText.text = text
		self.itemInfo = itemInfo
		
	def _getItem( self ):
		return self.__pyItem
		
	pyItem = property( _getItem )


class CastItem( Item ) :

	def __init__( self, item, pyBinder ) :
		Item.__init__( self, item.item, pyBinder )
		self.__pyAmount = StaticText( item.item.lbAmount )
		self.__pyAmount.text = ""

		self.__pyCDCover = CDCover( item.cdCover.circleCover, self )
		self.__pyCDCover.crossFocus = False

		self.__pyOverCover = AnimatedGUI( item.cdCover.overCover )
		self.__pyOverCover.initAnimation( 1, 8, ( 2, 4 ) )			# 动画播放一次，共8帧
		self.__pyOverCover.cycle = 0.4								# 循环播放一次的持续时间，单位：秒
		self.__pyCDCover.onUnfreezed.bind( self.__pyOverCover.playAnimation )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def __useableCheck( self ) :
		"""检查道具是否可用"""
		if self.itemInfo.validTarget() != csstatus.SKILL_GO_ON :
			self.pyBinder.hide()
		else :
			self.pyBinder.show()

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onRClick_( self, mods ) :
		Item.onRClick_( self, mods )
		self.itemInfo.spell()
		return True
	
	def onLClick_( self, mods ) :
		Item.onRClick_( self, mods )
		self.itemInfo.spell()
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def beginCooldown( self, cooldownType, lastTime ) :
		"""进入冷却状态"""
		if self.itemInfo is None : return
		if self.itemInfo.isCooldownType( cooldownType ) :
			cdInfo = self.itemInfo.getCooldownInfo()
			self.__pyCDCover.unfreeze( *cdInfo )

	def update( self, itemInfo ) :
		"""更新"""
		SKIDetector.unbindPyItem( self )						# 将探测器中的旧数据清空
		Item.update( self, itemInfo )
		if itemInfo is None :
			self.__pyAmount.text = ""
		else :
			self.__useableCheck()
			if itemInfo.amount > 1 :
				self.__pyAmount.text = str( itemInfo.amount )
			else :
				self.__pyAmount.text = ""

			spell = itemInfo.getSpell()
			if spell is None : return

			player = BigWorld.player()
			rangeMax = spell.getRangeMax( player )
			rangeMin = spell.getRangeMin( player )

			if rangeMax > 0.0 :
				SKIDetector.bindPyItem( self, ( "COM", rangeMax ) )	# 添加到探测器
			if rangeMin > 0.0 :
				SKIDetector.bindPyItem( self, ( "COM", rangeMin ) )	# 添加到探测器

	def onDetectorTrigger( self ) :
		"""施放距离检测"""
		self.__useableCheck()
