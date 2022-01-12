# -*- coding: gb18030 -*-
#
# $Id: EquipItem.py,v 1.18 2008-08-29 02:39:57 huangyongwei Exp $

"""
implement equipment item class
"""

from gbref import rds
from guis import *
import BigWorld
from guis.common.PyGUI import PyGUI
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from guis.tooluis.richtext_plugins.PL_Align import PL_Align
from guis.MLUIDefine import ItemQAColorMode
import csdefine
import GUIFacade
import ItemTypeEnum
import event.EventCenter as ECenter
import ItemTypeEnum

class EquipItem( PyGUI ):

	def __init__( self, kitBag, eqItem, itemName, pyBinder ):
		PyGUI.__init__( self, eqItem )
		self.dragFocus = False
		self.dropFocus = False
		self.focus = True
		self.__pyItem = Item( kitBag, eqItem.item, itemName, pyBinder )
		self.__pyItemBg = PyGUI( eqItem.itemBg )
		self.__pyItemBg.focus = False

	def update( self, itemInfo ):
		"""
		��ʾ����ĳ������ʱUPDATA��Ʒ
		"""
		self.__pyItem.update( itemInfo )
		self.itemInfo = itemInfo
		quality = itemInfo is None and 1 or itemInfo.quality
		util.setGuiState( self.__pyItemBg.getGui(), ( 4, 2 ), ItemQAColorMode[quality] )

	def equip_update( self, itemInfo ):
		"""
		װ��ĳ����Ʒ���������
		"""
		self.__pyItem.equip_update( itemInfo )
		self.itemInfo = itemInfo
		quality = itemInfo is None and 1 or itemInfo.quality
		util.setGuiState( self.__pyItemBg.getGui(), ( 4, 2 ), ItemQAColorMode[quality] )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getKitbag( self ) :
		return self.__pyItem.kitbagID

	def _getIndex( self ):
		return self.__pyItem.index

	def _setIndex( self, index ):
		self.__pyItem.index = index

	def _getPyItem( self ) : #��ȡ�ӽ��
		return self.__pyItem

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	kitbagID = property( _getKitbag )
	index = property( _getIndex, _setIndex )
	pyItem = property( _getPyItem )

# -------------------------------------------------------------------------------------
class Item( BOItem ) :
	def __init__( self, kitBag, item, itemName, pyBinder ) :
		BOItem.__init__( self, item, pyBinder )
		self.__kitbag = kitBag
		self.__itemName = itemName
		self.dragMark = DragMark.EQUIP_WND
		self.description = itemName
		self.__success_pName = "equipSuccess"

		self.clear()

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onRClick_( self, mods ) :
		BOItem.onRClick_( self, mods )
		if self.itemInfo is None : return
		if self.itemInfo.query("type") == ItemTypeEnum.ITEM_WEAPON_TWOSWORD:
			GUIFacade.autoUseKitbagItem( self.itemInfo.baseItem )
			return True
		# ����
#		if mods == MODIFIER_SHIFT and self.itemInfo.baseItem.getType() == ItemTypeEnum.ITEM_SYSTEM_TALISMAN:
#			rds.ruisMgr.talisman.show()
#			rds.ruisMgr.talisman.upDateTalisman( self.itemInfo )
#			return True
		GUIFacade.autoUseKitbagItem( self.itemInfo.baseItem )
		return True

	def onDescriptionShow_( self ):	# ����ƶ���itemͼ���ϣ���ʾ������Ϣ
		if self.itemInfo is None:
			selfDsp = self.__itemName
		else:
			item = self.itemInfo.baseItem
			selfDsp = item.description(BigWorld.player())
			#��������ж��Ƿ�Ӧ����ʾ�����ѵ�
			mouseShape = rds.ccursor.shape
			shapeName = mouseShape
			if item.isEquip() and "repair" in shapeName:
				des = GUIFacade.calcuOneRepairPrice( item, GUIFacade.getRepairType() )
				selfDsp.append([des])
		toolbox.infoTip.showItemTips( self, selfDsp )

	def onLClick_( self, mods ) :
		if self.itemInfo is None: return
		BOItem.onLClick_( self, mods )
		mouseShape = rds.ccursor.shape
		shapeName = mouseShape[0:len( mouseShape ) -2 ]
		return True

	# ---------------------------------------
	def onDrop_( self, pyTarget, pyDroped ) :
		BOItem.onDrop_( self, pyTarget, pyDroped )
		if pyDroped.dragMark == DragMark.KITBAG_WND :
			srcBagIndex = pyDroped.kitbagID			# from items window
			GUIFacade.autoMoveKitbagItem( srcBagIndex, pyDroped.gbIndex, self.__kitbag, self.index )
		return True

	# -------------------------------------------------
	def onDragStart_( self, pyDragged ) :
		if pyDragged.itemInfo is None: 
			toolbox.itemCover.normalizeItem()
			return False
		self.successParticle()					#��ô��ʾ��˸Ч�����߻�Ҫ���϶�װ��ʱҲҪ��˸��
		BOItem.onDragStart_( self, pyDragged )
		return True

	def onDragStop_( self, pyDragged ) :
		self.hideSuParticle()					#������˸
		BOItem.onDragStop_( self, pyDragged )
		return True

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def equip_update( self, itemInfo ) :
		"""
		װ����װ�������װ�����ԣ�������ʾ��˸�ĺ�ɫ��װ���ɹ���ʾ
		"""
		BOItem.update( self, itemInfo )
		if itemInfo is None :
			self.description = self.__itemName
			self.hideSuParticle()					#���ȡ��װ�� ��ôֹͣ��ʾ��˸�������ٸ�װ��װ����ȡ�µ������
		else :
			self.briefSuccessParticle()					#����װ����װ������,�������Ѿ��ɹ���,��ʾ�ɹ����Ч��
			if itemInfo.hardinessMax <= 1.0: return #����û������;õ�װ��������������ָ
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
		update item ֱ�Ӹ�����Ʒ���Ժ�ͼ�꣬����ʾ��ɫ��˸��װ���ɹ���ʾ
		"""
		BOItem.update( self, itemInfo )
		if self.index == ItemTypeEnum.CEL_TALISMAN: #�Ƿ���װ����
			ECenter.fireEvent( "EVT_ON_ROLE_ACTIVE_TALISNAM", itemInfo )
		if itemInfo is None :
			self.description = self.__itemName
		else :
			if itemInfo.hardinessMax <= 1.0: return #����û������;õ�װ��������������ָ
			else:
				ratio = itemInfo.hardiness/( itemInfo.hardinessMax + 0.1 )
				if ratio >= GUIFacade.getAbateval() and ratio <= GUIFacade.getWarningVal():
					self.color = ( 214,191,1,255 )
				if  ratio < GUIFacade.getAbateval():
					self.color = (255,0,0,255)
				elif ratio > GUIFacade.getWarningVal():
					self.color = (255,255,255,255)
				self.description = GUIFacade.getKitbagItemDescription( self.__kitbag, self.index )

	def briefSuccessParticle( self ):
		"""
		����ͼ���ϸ���װ���ɹ����Ч��
		"""
		self.successParticle()
		BigWorld.callback( 3, self.hideSuParticle )

	def successParticle( self ):
		"""
		����ͼ���ϸ���װ���ɹ����Ч��
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

	def hideSuParticle( self ):
		"""
		���ظ���װ���ɹ�����˸Ч��
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
