# -*- coding: gb18030 -*-
#
# $Id: PetInfo.py,v 1.11 2008-08-26 02:17:25 huangyongwei Exp $

"""
implement target info window
"""

from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.RootGUI import RootGUI
from guis.controls.StaticText import StaticText
from guis.controls.Button import Button
from guis.controls.ProgressBar import HProgressBar as ProgressBar
from BuffItem import BuffItem
from cscustom import Polygon
from PetFormulas import formulas
import csdefine

# ----------------------------------------------------------------
# 调整属性字体尺寸修饰器
# ----------------------------------------------------------------
from AbstractTemplates import MultiLngFuncDecorator

class deco_PetInfoResetPyItems( MultiLngFuncDecorator ) :

	@staticmethod
	def locale_big5( SELF ) :
		"""
		繁体版下重新调整部分属性字体的尺寸
		"""
		SELF._PetInfo__pyLbHP.fontSize = 11
		SELF._PetInfo__pyLbHP.charSpace = -1

		SELF._PetInfo__pyLbMP.fontSize = 11
		SELF._PetInfo__pyLbMP.charSpace = -1

		SELF._PetInfo__pyLbLevel.fontSize = 11
		SELF._PetInfo__pyLbLevel.charSpace = -1


class PetInfo( RootGUI ):
	__cc_item_top = 2.0, 15.0
	def __init__( self ):
		wnd = GUI.load( "guis/general/petswindow/petinfo/window.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.h_dockStyle = "LEFT"
		self.v_dockStyle = "TOP"

		self.posZSegment = ZSegs.L5
		self.activable_ = False
		self.escHide_ 		 = False
		self.moveFocus		 = False

		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( wnd )
		self.__resetPyItems()

	def __initialize( self, wnd ):
		self.__pyBg = PyGUI( wnd.bg )
		self.__pyHead = PyGUI( wnd.head )
		self.__pyBuffPanel = PyGUI( wnd.buffPanel )

		self.__pyLbName = StaticText( wnd.lbName )
		self.__pyLbName.text = ""
		self.__pyLbName.h_anchor = 'CENTER'

		self.__pyLbLevel = StaticText( wnd.lbLevel )
		self.__pyLbLevel.text = ""
		self.__pyLbLevel.fontSize = 11
		self.__pyLbLevel.h_anchor = 'CENTER'

		self.__pyLbHP = StaticText( wnd.lbHP )
		self.__pyLbHP.fontSize = 12
		self.__pyLbHP.text = ""

		self.__pyLbMP = StaticText( wnd.lbMP )
		self.__pyLbMP.fontSize = 12
		self.__pyLbMP.text = ""

		self.__pyHPBar = ProgressBar( wnd.hpBar )
		self.__pyHPBar.clipMode = "RIGHT"

		self.__pyMPBar = ProgressBar( wnd.mpBar )
		self.__pyMPBar.clipMode = "RIGHT"

		self.__pyBuffItems = []			# 良性buff格子
		self.__pyDBuffItems = []		# 恶性buff格子
		self.__initBDItems( self.__pyBuffItems, self.__cc_item_top[0] )
		self.__initBDItems( self.__pyDBuffItems, self.__cc_item_top[1] )

		self.__rangePolygon = Polygon([
										( 2, 17 ), ( 14, 2 ), ( 30, 0 ), ( 185, 4 ),
										( 185, 52 ), ( 17, 52 ), ( 2, 36 ),
									])												# 定义多边形区域

	def dispose( self ) :
		RootGUI.dispose( self )


	def __initBDItems( self, pyItems, top ) :
		"""
		initialize all buff/duff items
		"""
		for index in xrange( 12 ) :
			pyItem = BuffItem( )
			self.__pyBuffPanel.addPyChild( pyItem )
			pyItem.top = top
			pyItem.left = index * (pyItem.width + 2.0)
			pyItems.append( pyItem )

	@deco_PetInfoResetPyItems
	def __resetPyItems( self ) :
		"""
		重设部分UI元素的位置、大小、字体等属性
		"""
		pass											# 简体版本不作修改


	# --------------------------------------------
	# private
	# --------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_PET_ENTER_WORKLD"]   = self.__onPetEnterWorld
		self.__triggers["EVT_ON_PET_HP_CHANGE"]  	 = self.__onPetHPChange
		self.__triggers["EVT_ON_PET_MAX_HP_CHANGE"]  = self.__onPetHPChange
		self.__triggers["EVT_ON_PET_MP_CHANGE"]  	 = self.__onPetMPChange
		self.__triggers["EVT_ON_PET_MAX_MP_CHANGE"]	 = self.__onPetMPChange
		self.__triggers["EVT_ON_PET_NAME_CHANGE"] 	 = self.__onPetNameChange
		self.__triggers["EVT_ON_PET_LEVEL_CHANGE"] 	 = self.__onPetLevelChange
		self.__triggers["EVT_ON_PET_LEAVE_WORLD"] 	 = self.__onPetLeaveWorld
		self.__triggers["EVT_ON_PET_ADD_BUFF"] 	 	 = self.__onAddBuff
		self.__triggers["EVT_ON_PET_REMOVE_BUFF"] 	 = self.__onRemoveBuff
		self.__triggers["EVT_ON_PET_UPDATE_BUFF"] 	 = self.__onUpdateBuff
		self.__triggers["EVT_ON_PET_WITHDRAWED"]	 = self.__onPetWithdrawed
		for trigger in self.__triggers :
			ECenter.registerEvent( trigger, self )

	# -------------------------------------------
	def __onPetEnterWorld( self, dbid ):
		player = BigWorld.player()
		outPet = player.pcg_getActPet()
		if outPet is None:return
		if outPet.databaseID != dbid:return
		self.petID = outPet.id
		self.__pyHead.texture = outPet.getHeadTexture()
		self.__onPetHPChange( outPet.getHP(), outPet.getHPMax() )
		self.__onPetMPChange( outPet.getMP(), outPet.getMPMax() )
		self.__onPetNameChange( outPet.databaseID, outPet.getName() )
		self.__onPetLevelChange( outPet.databaseID, outPet.level )
		self.__clearBuffs()
		self.__showSelfBuff()
		self.__setNameColor( outPet )
		self.show()
	
	def __setNameColor( self, outPet ):
		"""
		设置名称颜色
		"""
		color = 255, 255, 255, 255
		if formulas.isHierarchy( outPet.species, csdefine.PET_HIERARCHY_GROWNUP ) :
			color = 255, 255, 255, 255
		elif formulas.isHierarchy( outPet.species, csdefine.PET_HIERARCHY_INFANCY1 ) :
			color = 0, 128, 255, 255
		else :
			color = 254, 163, 8, 255
		self.__pyLbName.color = color

	def __onPetHPChange( self, hp, hpMax ):
		"""
		update pet's hp
		"""
		if hpMax <= 0:
			self.__pyHPBar.value = 0
			return
		if hp >= hpMax:
			hp = hpMax
		self.__pyHPBar.value = float( hp )/hpMax
		self.__pyLbHP.text = "%d/%d" % ( hp, hpMax )

	def __onPetMPChange( self, mp, mpMax ):
		"""
		update pet's mp
		"""
		if mpMax <= 0:
			self.__pyMPBar.value = 0
		else:
			self.__pyMPBar.value = float( mp )/mpMax
		self.__pyLbMP.text = "%d/%d" % ( mp, mpMax )

	def __onPetNameChange( self, dbid, name ):
		player = BigWorld.player()
		outPet = player.pcg_getActPet()
		if outPet is None:return
		if outPet.databaseID != dbid:return
		self.__pyLbName.text = name

	def __onPetLevelChange( self, dbid, level ):
		player = BigWorld.player()
		outPet = player.pcg_getActPet()
		if outPet is None:return
		if outPet.databaseID != dbid:return
		self.__pyLbLevel.text = str( level )

	def __onPetLeaveWorld( self, dbid ):
		self.visible = False

	# -------------------------------------------------
	def __showSelfBuff( self ):
		"""
		initialize pet's buffs
		"""
		buffs = BigWorld.player().pcg_getActPetBuffList()
		for buff in buffs:
			self.__onAddBuff(buff)

	def __clearBuffs( self ):

		for pyItem in self.__pyDBuffItems + self.__pyBuffItems:
			pyItem.update( None )

	def __onAddBuff( self, itemInfo ) :
		"""
		当添加了一个 buff 时被触发
		"""
		baseItem = itemInfo.baseItem
		skillID = baseItem.getSourceSkillID()
		pyItems = []
		if baseItem.isMalignant(): #恶性buff
			pyItems = self.__pyDBuffItems
		else:
			pyItems = self.__pyBuffItems

		pyItem = self.__getEmptyItem( pyItems )
		pyItem.update( itemInfo )

	def __onRemoveBuff( self, buffInfo ) :
		"""
		当删除了一个 buff 时被触发
		"""
		pyItems = []
		top = 0
		if buffInfo.baseItem.isMalignant():
			pyItems = self.__pyDBuffItems
			top = self.__cc_item_top[1]
		else:
			pyItems = self.__pyBuffItems
			top = self.__cc_item_top[0]
		pyItem = self.__findItem( pyItems, buffInfo.buffIndex )
		if pyItem is None :
			return
		pyItem.update( None )
		pyItems.remove( pyItem )
		pyItems.append( pyItem )
		self.__layoutItems( pyItems, top )

	def __onUpdateBuff( self, itemInfo ) :
		"""
		当有一个 buff 更新时被触发
		"""
		pyItems = []
		baseItem = itemInfo.baseItem
		if baseItem.isMalignant():
			pyItems = self.__pyDBuffItems
		else:
			pyItems = self.__pyBuffItems
		for pyItem in pyItems :
			if pyItem.itemInfo is None: break
			if pyItem.itemInfo.baseItem.getSourceSkillID() == baseItem.getSourceSkillID() :
				pyItem.update( itemInfo )

	def __getEmptyItem( self, pyItems ) :
		"""
		find out an item with no buff/duff information
		"""
		for pyItem in pyItems :
			if pyItem.itemInfo is None :
				return pyItem
		pyItems.append( pyItems.pop( 0 ) )
		self.__layoutItems( pyItems, pyItems[0].top )
		return pyItems[-1]

	def __layoutItems( self, pyItems, top ) :
		"""
		relayout all buff/duff items
		"""
		for index, pyItem in enumerate( pyItems ) :
			pyItem.top = top
			pyItem.index = index
			pyItem.left = index * (pyItem.width + 2.0)

	def __findItem( self, pyItems, buffIndex ) :
		"""
		find item which it's buff/duff information is argument info
		"""
		for pyItem in pyItems :
			info = pyItem.itemInfo
			if info and info.buffIndex == buffIndex:
				return pyItem
		return None

	def __onPetWithdrawed( self, dbid ) :
		"""
		当宠物回收时被调用
		"""
		for pyItem in self.__pyBuffItems+self.__pyDBuffItems :
			pyItem.update( None )
		self.visible = False

	def __isSubItemsMouseHit( self ) :
		for pyBuffItem in self.__pyBuffItems + self.__pyDBuffItems :
			if pyBuffItem.isMouseHit() :
				return True
		return False


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseDown_( self, mods ) :
		RootGUI.onLMouseDown_( self, mods )
		return self.isMouseHit()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isMouseHit( self ) :
		"""
		判断鼠标是否点在多边形区域上
		"""
		return self.__rangePolygon.isPointIn( self.mousePos ) \
		or self.__isSubItemsMouseHit()

	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onLeaveWorld( self ):
		for pyItem in self.__pyBuffItems+self.__pyDBuffItems :
			pyItem.update( None )
		self.hide()

	def onLClick_( self,mods ):
		if not self.isMouseHit() : return False
		RootGUI.onLClick_( self,mods )
		try:
			entity = BigWorld.entities[self.petID]
		except:
			return
		rds.targetMgr.bindTarget( entity )
