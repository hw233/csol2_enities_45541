# -*- coding: gb18030 -*-
#
# $Id: PropertyPanel.py,v 1.12 2008-06-27 03:18:55 huangyongwei Exp $

from guis import *
from guis.controls.TabCtrl import TabPanel
from guis.controls.Button import Button
import event.EventCenter as ECenter
from PropertyItem import PropertyItem
from ResistItem import ResistItem
import GUIFacade

class PropertyPanel( TabPanel ):
	def __init__( self, panel = None, pyBinder = None ):
		TabPanel.__init__( self, panel, pyBinder )

		self.__triggers = {}
		self.__registerTriggers()
		self.__pyRichItems = {}
		self.__pyRestItems = {}
		self.__initPanel( panel )

	def __initPanel( self, panel ):
		self.__pyCloseBtn = Button( panel.closeBtn )
		self.__pyCloseBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyCloseBtn.onLClick.bind( self.__onClose )


		self.__initRichItem( panel )
		self.__initRestItem( panel )


	def __initRichItem( self, panel ): # 初始化属性浮动按钮等
		for name, item in panel.children:
			if "rich_" not in name:continue
			tag = name.split( "_" )[1]
			pyItem = PropertyItem( tag, item )
			pyItem.tag = tag
			self.__pyRichItems[tag] = pyItem

	def __initRestItem( self, panel ):
		for name, item in panel.children:
			if "resist_" not in name:continue
			tag = name.split( "_" )[1]
			pyItem = ResistItem( tag, item )
			self.__pyRestItems[tag] = pyItem

	# -------------------------------------------------------
	# private
	# -------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ROLE_POTENTIAL_CHANGED"] = self.__onRolePotenChanged # 潜能
#		self.__triggers["EVT_ON_ROLE_PKSTATE_CHANGED"] = self.__onRolePKChanged #PK状态
		self.__triggers["EVT_ON_ROLE_PKVALUE_CHANGED"] = self.__onRolePKValueChanged	# wsf，pk值
#		self.__triggers["EVT_ON_ROLE_CREDIT_CHANGED"] = self.__onRoleCreditChanged # 声望
#		self.__triggers["EVT_ON_ROLE_FAMILY_CHANGED"] = self.__onRoleFamilyChanged # 家族
#		self.__triggers["EVT_ON_ROLE_TONG_CHANGED"] = self.__onRoleTongChanged # 帮派

		self.__triggers["EVT_ON_ROLE_MINDAMAGE_CHANGED"] = self.__onRoleMinDamageChanged # 最小物理攻击
		self.__triggers["EVT_ON_ROLE_MAXDAMAGE_CHANGED"] = self.__onRoleMaxDamageChanged # 最大物理攻击
		self.__triggers["EVT_ON_ROLE_HITTED_CHANGED"] = self.__onRoleHitChanged # 命中率
		self.__triggers["EVT_ON_ROLE_DOUBLE_DAM_CHANGED"] = self.__onRoleDouleDamChanged # 物理暴击率
		self.__triggers["EVT_ON_ROLE_ARMOR_CHANGED"] = self.__onRoleAmorChanged # 物理防御
		self.__triggers["EVT_ON_ROLE_DODGE_CHANGED"] = self.__onRoleDodgeChanged # 闪避
		self.__triggers["EVT_ON_ROLE_RESIST_CHANGED"] = self.__onRoleResisitChanged # 招架

		self.__triggers["EVT_ON_ROLE_MAGDAMAGE_CHANGED"] = self.__onRoleMagDamChanged # 法术攻击
		self.__triggers["EVT_ON_ROLE_MAG_HITTED_CHANGED"] = self.__onRoleMagHitChanged # 法术命中率
		self.__triggers["EVT_ON_ROLE_MAG_DOUBLE_CHANGED"] = self.__onRoleMagDoubleChanged # 法术暴击率
		self.__triggers["EVT_ON_ROLE_MAGARMOR_CHANGED"] = self.__onRoleMagAmorChanged # 法术防御

		self.__triggers["EVT_ON_ROLE_RES_GIDDY_CHANGED"] = self.__onRoleResGiddyChanged # 抵抗眩晕率
		self.__triggers["EVT_ON_ROLE_RES_SLEEP_CHANGED"] =self.__onRoleResSleepChanged # 抵抗昏睡率
		self.__triggers["EVT_ON_ROLE_RES_FIX_CHANGED"] = self.__onRoleResFixChanged # 抵抗定身率
		self.__triggers["EVT_ON_ROLE_RES_HUSH_CHANGED"] = self.__onRoleResHushChanged # 抵抗沉默率

		for key in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( key, self )

	def __unregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			GUIFacade.unregisterEvent( key, self )

	# ----------------------------------------------------------------------
	def __onClose( self ):
		shortcutMgr.trigger( "TOGGLE_PROPWINDOW" )

	def __onRolePotenChanged( self, oldValue, newValue ):
		pyRichItem = self.__pyRichItems["Poten"]
		pyRichItem.updateValue( "Poten", newValue )

#	def __onRolePKChanged( self, value ):
#		pyRichItem = self.__pyRichItems["PK"]
#		pyRichItem.updateValue( "PK", value )

	def __onRolePKValueChanged( self, newValue ):
		pyRichItem = self.__pyRichItems["PK"]
		pyRichItem.updateValue( "PK", newValue )

	def __onRoleCreditChanged( self, value ):
		"""
		声望
		"""
		pyRichItem = self.__pyRichItems["Credit"]
		pyRichItem.updateValue( "Credit", value )

	def __onRoleFamilyChanged( self, family, official ):
		"""
		家族
		"""
		pyRichItem = self.__pyRichItems["Family"]
		pyRichItem.updateInfo( "Family", family, official )

	def __onRoleTongChanged( self, tong, official ):
		"""
		帮派
		"""
		pyRichItem = self.__pyRichItems["Tong"]
		pyRichItem.updateInfo( "Tong", tong, official )

	# -------------------------------------------------------------
	def __onRoleMinDamageChanged( self, value ):
		"""
		最小物理攻击
		"""
		pyRichItem = self.__pyRichItems["Damage"]
		pyRichItem.updateMin( value )

	def __onRoleMaxDamageChanged( self, value ): #
		"""
		最大物理攻击
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
		物理暴击率
		"""
		pyRichItem = self.__pyRichItems["Double"]
		pyRichItem.updateValue( "Double", value )

	def __onRoleAmorChanged( self, value ):
		"""
		物理防御率
		"""
		pyRichItem = self.__pyRichItems["Amor"]
		pyRichItem.updateValue( "Amor", value )

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
		pyRichItem = self.__pyRichItems["MagDouble"]
		pyRichItem.updateValue( "MagDouble", value )

	def __onRoleMagAmorChanged( self, value ):
		"""
		法术防御
		"""
		pyRichItem = self.__pyRichItems["MagAmor"]
		pyRichItem.updateValue( "MagAmor", value )

	# --------------------------------------------------------------
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

	# ---------------------------------------------------------------------
	# public
	# ---------------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )