# -*- coding: gb18030 -*-
#
# $Id: EquipItem.py,v 1.18 2008-08-29 02:39:57 huangyongwei Exp $

"""
implement equipment item class
"""

from guis import *
import BigWorld
from guis.common.PyGUI import PyGUI
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
import csdefine
import GUIFacade
import ItemTypeEnum
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from guis.tooluis.richtext_plugins.PL_Align import PL_Align

class EquipItem( PyGUI ):
	_quality_maps = { 1: ( 1, 1 ),
			2: ( 1, 2 ),
			3: ( 2, 1 ),
			4: ( 2, 2 ),
			5: ( 3, 1 )
			}
	def __init__( self, eqItem, itemName, pyBinder ):
		PyGUI.__init__( self, eqItem )
		self.dragFocus = False
		self.dropFocus = False
		self.focus = True
		self.__pyItem = Item( eqItem.item, itemName, pyBinder )
		self.__pyItemBg = PyGUI( eqItem.itemBg )
		self.__pyItemBg.focus = False

	def update( self, itemInfo ):
		"""
		表示更新某个属性时UPDATA物品
		"""
		self.__pyItem.update( itemInfo )
		self.itemInfo = itemInfo
		if itemInfo is not None :
			quality = itemInfo.quality
			util.setGuiState( self.__pyItemBg.getGui(), ( 3, 2 ), self._quality_maps[quality] )
		else:
			util.setGuiState( self.__pyItemBg.getGui(), ( 3, 2 ), ( 1, 1 ) )

	def equip_update( self, itemInfo ):
		"""
		装备某个物品后更新属性
		"""
		self.__pyItem.equip_update( itemInfo )
		self.itemInfo = itemInfo
		if itemInfo is not None :
			quality = itemInfo.quality
			util.setGuiState( self.__pyItemBg.getGui(), ( 3, 2 ), self._quality_maps[quality] )
		else:
			util.setGuiState( self.__pyItemBg.getGui(), ( 3, 2 ), ( 1, 1 ) )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getKitbag( self ) :
		return self.__pyItem.kitbagID

	def _getIndex( self ):
		return self.__pyItem.index

	def _setIndex( self, index ):
		self.__pyItem.index = index

	def _getPyItem( self ) : #获取子结点
		return self.__pyItem

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	kitbagID = property( _getKitbag )
	index = property( _getIndex, _setIndex )
	pyItem = property( _getPyItem )

# -------------------------------------------------------------------------------------
class Item( BOItem ) :
	def __init__( self, item, itemName, pyBinder ) :
		BOItem.__init__( self, item, pyBinder )
		self.__itemName = itemName
		self.dragMark = DragMark.VEHICLE_SKILL_BAR
		self.description = itemName
		self.__kitbag = 0
		self.__success_pName = "equipSuccess"
		self.dragFocus = False
		self.clear()

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onRClick_( self, mods ) :
		BOItem.onRClick_( self, mods )
		if self.itemInfo is None : return True
		return True

	def onDescriptionShow_( self ):	# 鼠标移动到item图标上，显示描述信息
		if self.itemInfo is None:
			selfDsp = self.__itemName
		else:
			item = self.itemInfo.baseItem
			selfDsp = item.description(BigWorld.player())
		toolbox.infoTip.showItemTips( self, selfDsp )

	def onLClick_( self, mods ) :
		if self.itemInfo is None: return
		mouseShape = rds.ccursor.shape
		shapeName = mouseShape[0:len( mouseShape ) -2 ]
		return True

	# ---------------------------------------
	def onDrop_( self, pyTarget, pyDroped ) :
		BOItem.onDrop_( self, pyTarget, pyDroped )
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def equip_update( self, itemInfo ) :
		"""
		装备了装备后更新装备属性，并且显示闪烁的红色的装备成功提示
		"""
		BOItem.update( self, itemInfo )
		if itemInfo is None :
			self.description = self.__itemName
			self.hideSuParticle()					#如果取下装备 那么停止显示闪烁（避免再刚装上装备又取下的情况）
		else :
			self.successParticle()					#更换装备到装备栏上,到这里已经成功了,显示成功后的效果
			if itemInfo.hardinessMax <= 1.0: return #过滤没有最大耐久的装备，如项链、戒指
			else:
				ratio = itemInfo.hardiness/( itemInfo.hardinessMax + 0.1 )
				if ratio >= GUIFacade.getAbateval() and ratio <= GUIFacade.getWarningVal():
					self.color = ( 214,191,1,255 )
				if  ratio < GUIFacade.getAbateval():
					self.color = (255,0,0,255)
				elif ratio > GUIFacade.getWarningVal():
					self.color = (255,255,255,255)
				self.description = GUIFacade.getKitbagItemDescription( self.__kitbag, self.index )

	def update( self, itemInfo ) :
		"""
		update item 直接更新物品属性和图标，不显示红色闪烁的装备成功提示
		"""
		BOItem.update( self, itemInfo )
		if itemInfo is None :
			self.description = self.__itemName
		else :
			if itemInfo.hardinessMax <= 1.0: return #过滤没有最大耐久的装备，如项链、戒指
			else:
				ratio = itemInfo.hardiness/( itemInfo.hardinessMax + 0.1 )
				if ratio >= GUIFacade.getAbateval() and ratio <= GUIFacade.getWarningVal():
					self.color = ( 214,191,1,255 )
				if  ratio < GUIFacade.getAbateval():
					self.color = (255,0,0,255)
				elif ratio > GUIFacade.getWarningVal():
					self.color = (255,255,255,255)
				self.description = GUIFacade.getKitbagItemDescription( self.__kitbag, self.index )

	def successParticle( self ):
		"""
		更新图标上更换装备成功后的效果
		"""
		gui = self.getGui()
		if not hasattr( gui, self.__success_pName ):
			textureName = "maps/particle_2d/guanxiao_an_hong/guanxiao_an_hong.texanim"
			toolbox.itemParticle.addParticle( self , textureName, self.__success_pName, 0.99999 )
		else:
			for child in gui.children:
				if child[0] == self.__success_pName:
					child[1].visible = True
					break
		BigWorld.callback( 3, self.hideSuParticle )

	def hideSuParticle( self ):
		"""
		隐藏更换装备成功后闪烁效果
		"""
		gui = self.getGui()
		if not hasattr( gui, self.__success_pName ):
			return
		for child in gui.children:
			if child[0] == self.__success_pName:
				child[1].visible = False
				return

	def clear( self ) :
		BOItem.clear( self )
		self.__itemInfo = None

	def getRepairInfo( self, repairer ) :
		if self.itemInfo is None : return None
		return GUIFacade.getRepairType(), self.kitbagID, self.index

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getKitbag( self ) :
		return self.__kitbag

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	kitbagID = property( _getKitbag )
