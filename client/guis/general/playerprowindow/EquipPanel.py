# -*- coding: gb18030 -*-
#
# $Id: EquipPanel.py,v 1.36 2008-08-21 08:26:09 fangpengjun Exp $

from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from guis.controls.TabCtrl import TabPanel
from guis.controls.StaticText import StaticText
from guis.controls.Button import Button
from guis.controls.ComboBox import ComboBox
from guis.controls.ComboBox import ComboItem as BaseComboItem
from guis.tooluis.CSRichText import CSRichText
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from RoleModelRender import RoleModelRender
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from EquipItem import EquipItem
from PropertyItem import PropertyItem
from ResistItem import ResistItem
import ItemTypeEnum as ItemType
import event.EventCenter as ECenter
import GUIFacade
import csdefine
import csconst
import Const
import ItemTypeEnum

ELM_MAGNIFY_TIMES = 100											# 元素抗性值显示时放大的倍数

# ----------------------------------------------------------------
# 调整属性字体尺寸修饰器
# ----------------------------------------------------------------
from AbstractTemplates import MultiLngFuncDecorator

class deco_EquipInitPropertyItems( MultiLngFuncDecorator ) :

	@staticmethod
	def locale_big5( SELF, panel ) :
		"""
		繁体版下重新调整部分属性字体的尺寸
		"""
		pyRichItems = SELF._EquipPanel__pyRichItems
		for name, item in panel.children:
			if "rich_" not in name:continue
			tag = name.split( "_" )[1]
			pyItem = PropertyItem( tag, item )
			pyItem.title = labelGather.getText( "PlayerProperty:EquipPanel", name )
			pyItem.tag = tag
			pyItem._PropertyItem__pyLbValue.charSpace = -1
			pyItem._PropertyItem__pyLbValue.fontSize = 11
			pyItem._PropertyItem__pyLbValue.left = 31
			pyRichItems[tag] = pyItem
		pyRichItems["PK"]._PropertyItem__pyStTitle.charSpace = -3
		pyRichItems["Vim"]._PropertyItem__pyLbValue.charSpace = -3


class EquipPanel( TabPanel ):
	__cc_itemMaps = {
	0 : ( ItemType.CEL_HEAD, labelGather.getText( "PlayerProperty:EquipPanel", "cel_head" ) ), 			# heah
	1 : ( ItemType.CEL_BODY, labelGather.getText( "PlayerProperty:EquipPanel", "cel_body" ) ), 			# jacket
	2 : ( ItemType.CEL_VOLA, labelGather.getText( "PlayerProperty:EquipPanel", "cel_vola" ) ), 			# glove
	3 : ( ItemType.CEL_RIGHTFINGER, labelGather.getText( "PlayerProperty:EquipPanel", "cel_rightfinger" ) ),	# right finger
	4 : ( ItemType.CEL_BREECH, labelGather.getText( "PlayerProperty:EquipPanel", "cel_breech" ) ), 		# trousers
#	5 : ( ItemType.CEL_TALISMAN, labelGather.getText( "PlayerProperty:EquipPanel", "cel_talisman" ) ),	 	# candidate
	6 : ( ItemType.CEL_RIGHTHAND, labelGather.getText( "PlayerProperty:EquipPanel", "cel_tighthand" ) ), 	# right hand
	7 : ( ItemType.CEL_NECK, labelGather.getText( "PlayerProperty:EquipPanel", "cel_neck" ) ),			# necklace
	8 : ( ItemType.CEL_HAUNCH, labelGather.getText( "PlayerProperty:EquipPanel", "cel_haunch" ) ), 		# haunch
	9 : ( ItemType.CEL_CUFF, labelGather.getText( "PlayerProperty:EquipPanel", "cel_cuff" ) ), 			# cuff;
	10 : ( ItemType.CEL_LEFTFINGER, labelGather.getText( "PlayerProperty:EquipPanel", "cel_leftfinger" ) ),	# left finger
	11 : ( ItemType.CEL_FEET, labelGather.getText( "PlayerProperty:EquipPanel", "cel_feet" ) ),			# shoes
	12 : ( ItemType.CEL_CIMELIA,labelGather.getText( "PlayerProperty:EquipPanel", "cel_cimelia" ) ),		# cimelia
	13 : ( ItemType.CEL_LEFTHAND, labelGather.getText( "PlayerProperty:EquipPanel", "cel_lefthand" ) ),		# left hand
	14: ( ItemType.CEL_POTENTIAL_BOOK, labelGather.getText( "PlayerProperty:EquipPanel", "cel_potential_book" ) ),	# fashion1
	15: ( ItemType.CEL_FASHION1, labelGather.getText( "PlayerProperty:EquipPanel", "cel_fashion1" ) )		# fashion2
	}

	def __init__( self, kitbagID = 0, panel = None, pyBinder = None ):
		TabPanel.__init__( self, panel, pyBinder )
		self.__kitbagID = kitbagID
		self.__pyItems = {}
		self.__pyRichItems = {}
		self.__pyRestItems = {}
		self.__initPanel( panel )

		self.__turnModelCBID = 0					# 旋转模型的 callback ID，原来用 Timer，现在改为直接用 callback（hyw--2008.06.24）

		self.__triggers = {}
		self.__registerTriggers()


	# --------------------------------------------------------
	# pravite
	# --------------------------------------------------------
	def __initPanel( self, panel ):
		labelGather.setLabel( panel.baseTitle.stTitle, "PlayerProperty:EquipPanel", "baseTitle" )
		labelGather.setLabel( panel.privyTitle.stTitle, "PlayerProperty:EquipPanel", "privyTitle" )
		labelGather.setLabel( panel.physTitle.stTitle, "PlayerProperty:EquipPanel", "physTitle" )
		labelGather.setLabel( panel.magicTitle.stTitle, "PlayerProperty:EquipPanel", "magicTitle" )
		self.__pyLbRoleName = StaticText( panel.lbRoleName )
		self.__pyLbRoleName.text = ""
		self.__pyLbRoleInfo = StaticText( panel.lbRoleInfo )

#		self.__pyCBTitle = ComboBox( panel.cbTitle )
#		self.__pyCBTitle.autoSelect = False
#		self.__pyCBTitle.width = 130.0
#		self.__pyCBTitle.onItemSelectChanged.bind( self.__onTitleChange )

#		self.__pyLbStrength = StaticText( panel.lbForce )
#		self.__pyLbDexter = StaticText( panel.lbAgility )
#		self.__pyLbCorpore = StaticText( panel.lbHabitus )
#		self.__pyLbIntellect = StaticText( panel.lbMind )

#		self.__pyLbMinDamage = StaticText( panel.lbMinDamage )
#		self.__pyLbMaxDamage = StaticText( panel.lbMaxDamage )
#
#		self.__pyLbMagicDamage = StaticText( panel.lbMagDamage )
#		self.__pyLbArmor = StaticText( panel.lbPhyRec )
#		self.__pyLbMagArmor = StaticText( panel.lbMagRec )
#		self.__pyLbSplit = StaticText( panel.splitText )

		self.__pyBtnRight = Button( panel.btnRight )
		self.__pyBtnRight.setStatesMapping( UIState.MODE_R1C4 )
		self.__pyBtnRight.onLMouseDown.bind( self.__turnRight )

		self.__pyBtnLeft = Button( panel.btnLeft )
		self.__pyBtnLeft.setStatesMapping( UIState.MODE_R1C4 )
		self.__pyBtnLeft.onLMouseDown.bind( self.__turnLeft )

		self.__pyBtnFashion = Button( panel.btnFashion )
		self.__pyBtnFashion.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnFashion.enable = False
		self.__pyBtnFashion.isOffsetText = True
		self.__pyBtnFashion.onLClick.bind( self.__onChangeFashion )
		labelGather.setPyBgLabel( self.__pyBtnFashion, "PlayerProperty:EquipPanel", "btnFashion" )

		self.__modelRender = RoleModelRender( panel.modelRender )

		self.__pyRtTong = CSRichText( panel.rtTong )
		self.__pyRtTong.maxWidth = 150.0

		self.__pyRtFamily = CSRichText( panel.rtFamily )
		self.__pyRtFamily.maxWidth = 150.0
		
		self.__pyLbDaoHeng = StaticText( panel.lbDaoHeng )
		self.__pyLbDaoHeng.color = 255, 242, 0, 255
		self.__pyLbDaoHeng.fontSize = 12.0
		self.__pyLbDaoHeng.text = ""

		self.__initItems( panel )
		self.__initRichItem( panel )
		self.__initRestItem( panel )
		self.__initElmPropertys( panel )

	def __initItems( self, panel ):
		for name, item in panel.children :
			if "eqItem_" not in name : continue
			index = int( name.split( "_" )[1] )
			mapIndex, itemName = self.__cc_itemMaps[index]
			pyItem = EquipItem( self.__kitbagID, item, itemName, self.pyBinder )
			pyItem.index = mapIndex
			self.__pyItems[mapIndex] = pyItem	# 装备物品

	@deco_EquipInitPropertyItems
	def __initRichItem( self, panel ): # 初始化玩家属性信息
		for name, item in panel.children:
			if "rich_" not in name:continue
			tag = name.split( "_" )[1]
			pyItem = PropertyItem( tag, item )
			pyItem.title = labelGather.getText( "PlayerProperty:EquipPanel", name )
			pyItem._PropertyItem__pyLbValue.font = "songti.font"
			pyItem._PropertyItem__pyLbValue.charSpace = 0
			pyItem.tag = tag
			self.__pyRichItems[tag] = pyItem

	def __initRestItem( self, panel ): # 初始化玩四抗性
		for name, item in panel.children:
			if "resist_" not in name:continue
			tag = name.split( "_" )[1]
			pyItem = ResistItem( tag, item )
			self.__pyRestItems[tag] = pyItem

	def __initElmPropertys( self, panel ) :
		"""
		初始化元素属性
		"""
		dsp = labelGather.getText( "PlayerProperty:EquipPanel", "elmFireDsp", 0, 0 )
		self.__pyElmProFire = self.__createElmProItem( panel.pro_elmFire, dsp )

		dsp = labelGather.getText( "PlayerProperty:EquipPanel", "elmDarkDsp", 0, 0 )
		self.__pyElmProDark = self.__createElmProItem( panel.pro_elmDark, dsp )

		dsp = labelGather.getText( "PlayerProperty:EquipPanel", "elmThunderDsp", 0, 0 )
		self.__pyElmProThunder = self.__createElmProItem( panel.pro_elmThunder, dsp )

		dsp = labelGather.getText( "PlayerProperty:EquipPanel", "elmIceDsp", 0, 0 )
		self.__pyElmProIce = self.__createElmProItem( panel.pro_elmIce, dsp )

	def __createElmProItem( self, elmItem, dsp ) :
		"""
		创建元素属性单元
		"""
		pyElm = Control( elmItem )
		pyElm.dsp = dsp
		pyElm.onMouseEnter.bind( self.__onElmProMouseEnter )
		pyElm.onMouseLeave.bind( self.__onElmProMouseLeave )
		pyElm.crossFocus = True
		return pyElm

	# ------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ROLE_ENTER_WORLD"] = self.__onPlayerEnterWorld 	# player enter world trigger
		self.__triggers["EVT_ON_ROLE_LEVEL_CHANGED"] = self.__onRoleLevelChanged # level
		self.__triggers["EVT_ON_ROLE_CORPS_NAME_CHANGED"] = self.__onRoleTongChange #帮会
		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_GRADE"] = self.__onTongGradeChange #帮会职务改变
		self.__triggers["EVT_ON_TOGGLE_FAMILY_NAME_CHANGE"] = self.__onRoleFamilyChanged # 家族
		self.__triggers["EVT_ON_TOGGLE_FAMILY_UPDATE_GRADE"] = self.__onFamilyGradeChange #家族职务改变

		self.__triggers["EVT_ON_EQUIPBAG_ADD_ITEM"] = self.__onAddEquipItem		#装备栏增加装备
		self.__triggers["EVT_ON_EQUIPBAG_UPDATE_ITEM"] = self.__onUpdateEquipItem	#装备栏中装备属性改变（被攻击时耐久度改变）
		self.__triggers["EVT_ON_EQUIPBAG_REMOVE_ITEM"] = self.__onRemoveEquipItem	#卸下某个装备
		self.__triggers["EVT_ON_EQUIPBAG_SWAP_ITEM"] = self.__onSwapItems		#与背包中的某个装备交换位置
		self.__triggers["EVT_ON_ROLE_CHANGE_FASHIONNUM"] = self.__onFashionNumChange

		self.__triggers["EVT_ON_HIGHLIGHT_ITEM"] = self.__highLightItem
		self.__triggers["EVT_ON_DEHIGHLIGHT_ITEM"] = self.__dehighLightItem

		self.__triggers["EVT_ON_ROLE_STRENGTH_CHANGE"] = self.__onStrengthChange
		self.__triggers["EVT_ON_ROLE_DEXTER_CHANGE"] = self.__onDexterityChange
		self.__triggers["EVT_ON_ROLE_CORPORE_CHANGE"] = self.__onCorporeityChange
		self.__triggers["EVT_ON_ROLE_INTELLECT_CHANGE"] = self.__onIntellectChange

#		self.__triggers["EVT_ON_ROLE_MINDAMAGE_CHANGED"] = self.__onMinDamageChanged
#		self.__triggers["EVT_ON_ROLE_MAXDAMAGE_CHANGED"] = self.__onMaxDamageChanged
#		self.__triggers["EVT_ON_ROLE_MAGDAMAGE_CHANGED"] = self.__onMagDamageChanged
#		self.__triggers["EVT_ON_ROLE_ARMOR_CHANGED"] = self.__onArmorChanged
#		self.__triggers["EVT_ON_ROLE_MAGARMOR_CHANGED"] = self.__onMagAromrChanged

		self.__triggers["EVT_ON_ROLE_POTENTIAL_CHANGED"] = self.__onRolePotenChanged # 潜能
#		self.__triggers["EVT_ON_ROLE_PKSTATE_CHANGED"] = self.__onRolePKChanged #PK状态
		self.__triggers["EVT_ON_ROLE_PKVALUE_CHANGED"] = self.__onRolePKValueChanged	#wsf，pk值
		self.__triggers["EVT_ON_ROLE_GOODNESS_CHANGE"] = self.__onRoleGoodnessChanged #善恶值
		self.__triggers["EVT_ON_ROLE_CREDIT_CHANGED"] = self.__onRoleCreditChanged #功勋
		self.__triggers["EVT_ON_ROLE_HONOR_CHANGED"] = self.__onRoleHonorChange #荣誉
		self.__triggers["EVT_ON_ROLE_VIM_CHANGED"] = self.__onRoleVimChange #活力

		self.__triggers["EVT_ON_ROLE_MINDAMAGE_CHANGED"] = self.__onRoleMinDamageChanged #最小物理攻击
		self.__triggers["EVT_ON_ROLE_MAXDAMAGE_CHANGED"] = self.__onRoleMaxDamageChanged #最大物理攻击
		self.__triggers["EVT_ON_ROLE_HITTED_CHANGED"] = self.__onRoleHitChanged #命中率
		self.__triggers["EVT_ON_ROLE_DOUBLE_DAM_CHANGED"] = self.__onRoleDouleDamChanged #物理致命率
		self.__triggers["EVT_ON_ROLE_ARMOR_CHANGED"] = self.__onRoleAmorChanged #物理防御
		self.__triggers["EVT_ON_ROLE_DODGE_CHANGED"] = self.__onRoleDodgeChanged #闪避
		self.__triggers["EVT_ON_ROLE_RESIST_CHANGED"] = self.__onRoleResisitChanged #招架

		self.__triggers["EVT_ON_ROLE_MAGDAMAGE_CHANGED"] = self.__onRoleMagDamChanged #法术攻击
		self.__triggers["EVT_ON_ROLE_MAG_HITTED_CHANGED"] = self.__onRoleMagHitChanged #法术命中率
		self.__triggers["EVT_ON_ROLE_MAG_DOUBLE_CHANGED"] = self.__onRoleMagDoubleChanged #法术致命率
		self.__triggers["EVT_ON_ROLE_MAGARMOR_CHANGED"] = self.__onRoleMagAmorChanged #法术防御

		self.__triggers["EVT_ON_ROLE_RES_GIDDY_CHANGED"] = self.__onRoleResGiddyChanged #抵抗眩晕率
		self.__triggers["EVT_ON_ROLE_RES_SLEEP_CHANGED"] =self.__onRoleResSleepChanged #抵抗昏睡率
		self.__triggers["EVT_ON_ROLE_RES_FIX_CHANGED"] = self.__onRoleResFixChanged #抵抗定身率
		self.__triggers["EVT_ON_ROLE_RES_HUSH_CHANGED"] = self.__onRoleResHushChanged #抵抗沉默率

		self.__triggers["EVT_ON_ROLE_ELM_FIRE_DAMAGE_CHANGED"] = self.__onRoleFireDmgChanged # 火元素属性改变
		self.__triggers["EVT_ON_ROLE_ELM_FIRE_DERATE_RATIO_CHANGED"] = self.__onRoleFireDerateRatioChanged # 火元素属性改变
		self.__triggers["EVT_ON_ROLE_ELM_XUAN_DAMAGE_CHANGED"] = self.__onRoleDarkDmgChanged # 玄元素属性改变
		self.__triggers["EVT_ON_ROLE_ELM_XUAN_DERATE_RATIO_CHANGED"] = self.__onRoleDarkDerateRatioChanged # 玄元素属性改变
		self.__triggers["EVT_ON_ROLE_ELM_THUNDER_DAMAGE_CHANGED"] = self.__onRoleThunderDmgChanged # 雷元素属性改变
		self.__triggers["EVT_ON_ROLE_ELM_THUNDER_DERATE_RATIO_CHANGED"] = self.__onRoleThunderDerateRatioChanged # 雷元素属性改变
		self.__triggers["EVT_ON_ROLE_ELM_ICE_DAMAGE_CHANGED"] = self.__onRoleIceDmgChanged # 冰元素属性改变
		self.__triggers["EVT_ON_ROLE_ELM_ICE_DERATE_RATIO_CHANGED"] = self.__onRoleIceDerateRatioChanged # 冰元素属性改变
		self.__triggers["EVT_ON_ROLE_DAOHENG_CHANGE"] = self.__onRoleDaoHengChange

		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	# -----------------------------------------------------------------
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

	def resetModelAngle( self ) :
		"""
		turning model on the mirror
		"""
		self.__modelRender.yaw = 0

	def __highLightItem( self,equipList ):
		for pyItem in self.__pyItems.itervalues() :
			cleType = pyItem.index
			if cleType in equipList :
				toolbox.itemCover.showItemCover( pyItem.pyItem ) #在这里应该用pyItem的子结点才正确，所以用pyItem.pyItem

	def __dehighLightItem( self,itemList ):
		for pyItem in self.__pyItems.itervalues() :
			cleType = pyItem.index
			if cleType in itemList :
				toolbox.itemCover.hideItemCover( pyItem.pyItem ) #在这里应该用pyItem的子结点才正确，所以用pyItem.pyItem

	def __onChangeFashion( self, pyBtn ):
		"""
		时装和装备模型切换
		"""
		BigWorld.player().changFashionNum()

	# -----------------------------------------------
	def __onPlayerEnterWorld( self, player ):
		self.__pyLbRoleName.text = player.getName()
		level = player.getLevel()
		self.pclass = csconst.g_chs_class[player.getClass()]
		roleInfo = labelGather.getText( "PlayerProperty:EspialWindow", "roleInfo" )%( level, self.pclass )
		self.__pyLbRoleInfo.text = roleInfo
#		self.__initTitles( player )

	def __initTitles( self, player ):
		titleIDs = player.titles
		titleIDs.insert( 0, 0 )
		for titleID in titleIDs:
			title = player.getAddTitle( titleID )
			if title == '':
				title = labelGather.getText( "PlayerProperty:TitlePanel", "noneTitle" )
			#self.__onRoleAddTitle( titleID, title )
			pyTitle = ComboItem( title )
			pyTitle.titleID = titleID
			self.__pyCBTitle.addItem( pyTitle )
		title = player.titleName
		if title == '':
			title = labelGather.getText( "PlayerProperty:TitlePanel", "noneTitle" )
		for pyTitle in self.__pyCBTitle.pyItems:
			if pyTitle.text == title:
				self.__pyCBTitle.pySelItem = pyTitle
				break

	def __onRoleLevelChanged( self, oldLevel, level ):
		roleInfo = labelGather.getText( "PlayerProperty:EspialWindow", "roleInfo" )%( level, self.pclass )
		self.__pyLbRoleInfo.text = roleInfo
		pyRichItem = self.__pyRichItems["Vim"]
		pyRichItem.onLevelChange( oldLevel, level )

	def __onAddEquipItem( self, itemInfo ):
		index = itemInfo.orderID
		if self.__pyItems.has_key( index ):
			if itemInfo.query("type") == ItemTypeEnum.ITEM_WEAPON_TWOSWORD:
				self.__pyItems[7].equip_update( itemInfo )
				self.__pyItems[8].equip_update( itemInfo )
			elif itemInfo.query("type") == ItemTypeEnum.ITEM_FASHION1:
				self.__pyBtnFashion.enable = True
				self.__pyItems[ItemType.CEL_FASHION1].equip_update( itemInfo )
				labelGather.setPyBgLabel( self.__pyBtnFashion, "PlayerProperty:EquipPanel", "btnEquip" )
			else:
				self.__pyItems[index].equip_update( itemInfo )

	def __onUpdateEquipItem( self, itemInfo ):
		index = itemInfo.orderID
		if self.__pyItems.has_key( index ):
			if itemInfo.query("type") == ItemTypeEnum.ITEM_WEAPON_TWOSWORD:
				self.__pyItems[7].update( itemInfo )
				self.__pyItems[8].update( itemInfo )
			else:
				self.__pyItems[index].update( itemInfo )

	def __onRemoveEquipItem( self, itemInfo ):
		index = itemInfo.orderID
		if self.__pyItems.has_key( index ):
			if itemInfo.query("type") == ItemTypeEnum.ITEM_WEAPON_TWOSWORD:
				self.__pyItems[8].equip_update( None )
				self.__pyItems[7].equip_update( None )
			elif itemInfo.query("type") == ItemTypeEnum.ITEM_FASHION1:
				self.__pyBtnFashion.enable = False
				self.__pyItems[ItemType.CEL_FASHION1].equip_update( None )
				labelGather.setPyBgLabel( self.__pyBtnFashion, "PlayerProperty:EquipPanel", "btnFashion" )
			else:
				self.__pyItems[index].equip_update( None )

	def __onSwapItems( self, itemInfo ):
		index = itemInfo.orderID
		if self.__pyItems.has_key( index ):
			if itemInfo.query("type") == ItemTypeEnum.ITEM_WEAPON_TWOSWORD:
				self.__pyItems[7].equip_update( itemInfo )
				self.__pyItems[8].equip_update( itemInfo )
			elif itemInfo.query("type") == ItemTypeEnum.ITEM_WEAPON_SWORD1:
				self.__pyItems[7].equip_update( None )
				self.__pyItems[8].equip_update( itemInfo )
			else:
				self.__pyItems[index].equip_update( itemInfo )

	def __onFashionNumChange( self, fashionNum ):
		if fashionNum > 0:
			labelGather.setPyBgLabel( self.__pyBtnFashion, "PlayerProperty:EquipPanel", "btnEquip" )
		else:
			labelGather.setPyBgLabel( self.__pyBtnFashion, "PlayerProperty:EquipPanel", "btnFashion" )

	def __onRoleChangeTitle( self, entity, oldTitle, titleName, titleColor = None ):
		if entity.id != BigWorld.player().id:return

	def __onRoleTongChange( self, role, oldName, tongName ):
		"""
		帮会名称
		"""
		pass

	def __onTongGradeChange( self, memberDBID, grade ):
		"""
		帮会职务
		"""
		pass

	def __onRoleFamilyChanged( self, role, oldName, familyName ):
		"""
		家族名称
		"""
		pass


	def __onFamilyGradeChange(self, memberDBID, grade ):
		"""
		家族职务
		"""
		pass

	# --------------------------------------------
	# 基本属性
	# --------------------------------------------
	def __onStrengthChange( self, newValue ):
		"""
		力量
		"""
		pyRichItem = self.__pyRichItems["Force"]
		pyRichItem.updateValue( "Force", newValue )

	def __onIntellectChange( self, newValue ):
		"""
		智力
		"""
		pyRichItem = self.__pyRichItems["Brains"]
		pyRichItem.updateValue( "Brains", newValue )

	def __onDexterityChange( self, newValue ):
		"""
		敏捷
		"""
		pyRichItem = self.__pyRichItems["Agility"]
		pyRichItem.updateValue( "Agility", newValue )

	def __onCorporeityChange( self, newValue ):
		"""
		体质
		"""
		pyRichItem = self.__pyRichItems["Habitus"]
		pyRichItem.updateValue( "Habitus",newValue )


#	def __onMinDamageChanged( self, value ):
#		"""
#		最小物理攻击
#		"""
#		self.__pyLbMinDamage.text = str( value )
#
#		self.__pyLbMinDamage.right = self.__pyLbSplit.left - 2
#
#	def __onMaxDamageChanged( self, value ):
#		"""
#		物理攻击
#		"""
#		self.__pyLbMaxDamage.text = str( value )
#		self.__pyLbSplit.right = self.__pyLbMaxDamage.left - 3
#
#	def __onMagDamageChanged( self, value ):
#		"""
#		法术攻击
#		"""
#		self.__pyLbMagicDamage.text = str( value )
#
#	def __onArmorChanged( self, value ):
#		"""
#		物理防御
#		"""
#		self.__pyLbArmor.text = str( value )
#
#	def __onMagAromrChanged( self, value ):
#		"""
#		法术防御
#		"""
#		self.__pyLbMagArmor.text = str( value )

	# -------------------------------------------------
	# 私人信息
	# -------------------------------------------------
	def __onRoleGoodnessChanged( self, newValue ):
		"""
		善恶
		"""
		pyRichItem = self.__pyRichItems["Ditheism"]
		pyRichItem.updateValue( "Ditheism", newValue )

	def __onRolePotenChanged( self, oldValue, newValue ):
		"""
		潜能
		"""
		pyRichItem = self.__pyRichItems["Potential"]
		pyRichItem.updateValue( "Potential", newValue )

#	def __onRolePKChanged( self, value ):
#		pyRichItem = self.__pyRichItems["PK"]
#		pyRichItem.updateValue( "PK", value )

	def __onRolePKValueChanged( self, newValue ):
		"""
		PK值
		"""
		pyRichItem = self.__pyRichItems["PK"]
		pyRichItem.updateValue( "PK", newValue )

	def __onRoleCreditChanged( self, value ):
		"""
		功勋
		"""
		pyRichItem = self.__pyRichItems["Credit"]
		pyRichItem.updateValue( "Credit", int( value ) )

	def __onRoleHonorChange( self, value ):
		"""
		荣誉
		"""
		pass
#		pyRichItem = self.__pyRichItems["Honor"]
#		pyRichItem.updateValue( "Honor", int( value ) )

	def __onRoleVimChange( self, value ):
		"""
		活力值
		"""
		pyRichItem = self.__pyRichItems["Vim"]
		pyRichItem.updateValue( "Vim", int( value ) )
	# --------------------------------------------
	# 物理属性
	# --------------------------------------------
	def __onRoleMinDamageChanged( self, value ):
		"""
		最小物理伤害
		"""
		pyRichItem = self.__pyRichItems["Damage"]
		pyRichItem.updateMin( value )

	def __onRoleMaxDamageChanged( self, value ): #
		"""
		最大物理伤害
		"""
		pyRichItem = self.__pyRichItems["Damage"]
		pyRichItem.updateMax( value )

	def __onRoleHitChanged( self, value ):
		"""
		物理命中率
		"""
		pyRichItem = self.__pyRichItems["Hit"]
		pyRichItem.updateValue( "Hit", value )

	def __onRoleDouleDamChanged( self, value ):
		"""
		物理致命一击率
		"""
		pyRichItem = self.__pyRichItems["Dead"]
		pyRichItem.updateValue( "Dead", value )

	def __onRoleDodgeChanged( self, value ):
		"""
		闪避率
		"""
		pyRichItem = self.__pyRichItems["Dodge"]
		pyRichItem.updateValue( "Dodge", value )

	def __onRoleResisitChanged( self, value ):
		"""
		招架率
		"""
		pyRichItem = self.__pyRichItems["Resisit"]
		pyRichItem.updateValue( "Resisit", value )

	def __onRoleAmorChanged( self, value ):
		"""
		物理防御率
		"""
		pyRichItem = self.__pyRichItems["Amor"]
		pyRichItem.updateValue( "Amor", value )

	# --------------------------------------------
	# 法术属性
	# --------------------------------------------
	def __onRoleMagDamChanged( self, value ):
		"""
		法术攻击
		"""
		pyRichItem = self.__pyRichItems["MagDam"]
		pyRichItem.updateValue( "MagDam", value )

	def __onRoleMagHitChanged( self, value ):
		"""
		法术命中率
		"""
		pyRichItem = self.__pyRichItems["MagHit"]
		pyRichItem.updateValue( "MagHit", value )

	def __onRoleMagDoubleChanged( self, value ):
		"""
		法术暴击率
		"""
		pyRichItem = self.__pyRichItems["MagDead"]
		pyRichItem.updateValue( "MagDead", value )

	def __onRoleMagAmorChanged( self, value ):
		"""
		法术防御
		"""
		pyRichItem = self.__pyRichItems["MagAmor"]
		pyRichItem.updateValue( "MagAmor", value )

	# ---------------------------------------------
	# 玩家四抗性
	# ---------------------------------------------
	def __onRoleResGiddyChanged( self, value ):
		"""
		眩晕抵抗
		"""
		pyRestItem = self.__pyRestItems["Giddy"]
		pyRestItem.updateValue( value )

	def __onRoleResSleepChanged( self, value ):
		"""
		昏睡抵抗
		"""
		pyRestItem = self.__pyRestItems["Sleep"]
		pyRestItem.updateValue( value )

	def __onRoleResFixChanged( self, value ):
		"""
		定身抵抗
		"""
		pyRestItem = self.__pyRestItems["Fix"]
		pyRestItem.updateValue( value )

	def __onRoleResHushChanged( self, value ):
		"""
		沉默抵抗
		"""
		pyRestItem = self.__pyRestItems["Hush"]
		pyRestItem.updateValue( value )

	def __onRoleFireDmgChanged( self, value ) :
		"""
		火伤害发生变化
		"""
		player = BigWorld.player()
		derateValue = float( player.elem_huo_derate_ratio ) / csconst.FLOAT_ZIP_PERCENT * ELM_MAGNIFY_TIMES
		dsp = labelGather.getText( "PlayerProperty:EquipPanel", "elmFireDsp", value, derateValue )
		self.__pyElmProFire.dsp = dsp

	def __onRoleFireDerateRatioChanged( self, value ) :
		"""
		火抗性发生变化
		"""
		player = BigWorld.player()
		global ELM_MAGNIFY_TIMES
		derateValue = float( value ) / csconst.FLOAT_ZIP_PERCENT * ELM_MAGNIFY_TIMES
		dsp = labelGather.getText( "PlayerProperty:EquipPanel", "elmFireDsp", player.elem_huo_damage, derateValue )
		self.__pyElmProFire.dsp = dsp

	def __onRoleDarkDmgChanged( self, value ) :
		"""
		玄伤害发生变化
		"""
		player = BigWorld.player()
		derateValue = float( player.elem_xuan_derate_ratio ) / csconst.FLOAT_ZIP_PERCENT * ELM_MAGNIFY_TIMES
		dsp = labelGather.getText( "PlayerProperty:EquipPanel", "elmDarkDsp", value, derateValue )
		self.__pyElmProDark.dsp = dsp

	def __onRoleDarkDerateRatioChanged( self, value ) :
		"""
		玄抗性发生变化
		"""
		player = BigWorld.player()
		global ELM_MAGNIFY_TIMES
		derateValue = float( value ) / csconst.FLOAT_ZIP_PERCENT * ELM_MAGNIFY_TIMES
		dsp = labelGather.getText( "PlayerProperty:EquipPanel", "elmDarkDsp", player.elem_xuan_damage, derateValue )
		self.__pyElmProDark.dsp = dsp

	def __onRoleThunderDmgChanged( self, value ) :
		"""
		雷伤害发生变化
		"""
		player = BigWorld.player()
		derateValue = float( player.elem_lei_derate_ratio ) / csconst.FLOAT_ZIP_PERCENT * ELM_MAGNIFY_TIMES
		dsp = labelGather.getText( "PlayerProperty:EquipPanel", "elmThunderDsp", value, derateValue )
		self.__pyElmProThunder.dsp = dsp

	def __onRoleThunderDerateRatioChanged( self, value ) :
		"""
		雷抗性发生变化
		"""
		player = BigWorld.player()
		global ELM_MAGNIFY_TIMES
		derateValue = float( value ) / csconst.FLOAT_ZIP_PERCENT * ELM_MAGNIFY_TIMES
		dsp = labelGather.getText( "PlayerProperty:EquipPanel", "elmThunderDsp", player.elem_lei_damage, derateValue )
		self.__pyElmProThunder.dsp = dsp

	def __onRoleIceDmgChanged( self, value ) :
		"""
		冰伤害发生变化
		"""
		player = BigWorld.player()
		derateValue = float( player.elem_bing_derate_ratio ) / csconst.FLOAT_ZIP_PERCENT * ELM_MAGNIFY_TIMES
		dsp = labelGather.getText( "PlayerProperty:EquipPanel", "elmIceDsp", value, derateValue )
		self.__pyElmProIce.dsp = dsp

	def __onRoleIceDerateRatioChanged( self, value ) :
		"""
		冰抗性发生变化
		"""
		player = BigWorld.player()
		global ELM_MAGNIFY_TIMES
		derateValue = float( value ) / csconst.FLOAT_ZIP_PERCENT * ELM_MAGNIFY_TIMES
		dsp = labelGather.getText( "PlayerProperty:EquipPanel", "elmIceDsp", player.elem_bing_damage, derateValue )
		self.__pyElmProIce.dsp = dsp
	
	def __onRoleDaoHengChange( self, oldValue ):
		"""
		道行改变
		"""
		player = BigWorld.player()
		years = player.daoheng/365
		days = player.daoheng%365
		dhText = labelGather.getText( "PlayerProperty:EquipPanel","daohengOfday" )%days
		if years > 0:
			dhText = labelGather.getText( "PlayerProperty:EquipPanel","daohengOfyear" )%( years, days )
		self.__pyLbDaoHeng.text = dhText

	def __onElmProMouseEnter( self, pyElm ) :
		"""
		鼠标进入元素属性图标
		"""
		toolbox.infoTip.showToolTips( self, pyElm.dsp )

	def __onElmProMouseLeave( self ) :
		"""
		鼠标离开元素属性图标
		"""
		toolbox.infoTip.hide()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onEnterWorld( self ) :
		self.__modelRender.onEnterWorld()
		player = BigWorld.player()
		daoheng = player.daoheng
		self.__onRoleDaoHengChange( daoheng )
		fashionNum = player.fashionNum
		fashionItem = self.__pyItems[ItemType.CEL_FASHION1]
		pyItem = fashionItem.pyItem
		if pyItem is None:return
		if pyItem.itemInfo is None:return
		self.__onFashionNumChange( fashionNum )

	def onShow( self ):
		self.__modelRender.enableDrawModel()
		TabPanel.onShow( self )
		rds.helper.courseHelper.openWindow( "renwushuxing_chuangkou" )

	def onHide( self ) :
		BigWorld.cancelCallback( self.__turnModelCBID )
		TabPanel.onHide( self )
		self.__modelRender.disableDrawModel()

	def initSociaInfo( self ):
		pass

	# -------------------------------------------------
	def reset( self ) :		# reset装备栏
		for item in self.__pyItems.itervalues():
			item.update( None )

	def getItem( self, index ) :
		if index < 0 : return None
		if index >= len( self.__pyItems ) : return None
		return self.__pyItems[index]

class ComboItem( BaseComboItem ):
	def __init__( self, text ):
		BaseComboItem.__init__( self, text )
		self.titleID = 0
