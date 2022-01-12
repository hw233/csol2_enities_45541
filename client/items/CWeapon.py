# -*- coding: gb18030 -*-

# $Id: CWeapon.py,v 1.9 2008-05-17 11:42:42 huangyongwei Exp $


import math
import csconst
import Const
import ItemTypeEnum
import ItemAttrClass

from bwdebug import *
from CEquip import CEquip
from ItemSystemExp import EquipIntensifyExp
from ItemSystemExp import EquipQualityExp
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import g_newLine
from config.client.labels.items import lbs_CWeapon
from config.client.labels.items import lbs_CItemBase
from config.client.labels.items import lbs_CEquip
from skills import getSkill
from ItemSystemExp import EquipExp
from EquipHelper import *

g_equipIntensify = EquipIntensifyExp.instance()
g_equipQualityExp = EquipQualityExp.instance()

class CWeapon( CEquip ):
	"""
	武器类

	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )

	def wield( self, who, update = True ):
		"""
		装备道具

		@param    who: 背包拥有者
		@type     who: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    True 装备成功，False 装备失败
		@return:    BOOL
		"""
		if not CEquip.wield( self, who, update ):
			return False

		return True

	def unWield( self, who, update = True ):
		"""
		卸下装备

		@param    who: 背包拥有者
		@type     who: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    无
		"""
		if not self.isAlreadyWield(): return	# 如果没有装备效果则不用unwield

		CEquip.unWield( self, who, update )

	def getGodWeaponSkillID( self ):
		"""
		获取神器属性技能ID
		"""
		return self.query( "param1", 0 )

	def fullName( self ):
		"""
		获取物品的全名 如 雄鹰的逆天的霸王弓
		"""
		nameDes = self.name()
		proName = self.query( "propertyPrefix")
		if proName: nameDes = proName + nameDes
		prefix = self.query( "prefix" )
		excName = g_equipQualityExp.getName( prefix )
		if excName != "": nameDes = excName + nameDes
		if self.getGodWeaponSkillID() > 0:
			nameDes = lbs_CEquip[14] + nameDes
		return nameDes

	def getQualityColor( self ) :
		"""
		获取品质颜色
		"""
		if self.getGodWeaponSkillID() > 0:
			return csconst.GOD_WEAPON_NAME_COLOR
		return g_equipQualityExp.getColorByQuality( self.getQuality() )

	def getProDescription( self, reference ):
		"""
		virtual method
		获取武器专有描述信息
		"""
		CEquip.getProDescription( self, reference)

		exp =  EquipExp( self, reference )

		# 注意这里，服务器对武器的物攻加值与客户端有略微区别，所以这个公式中多出了第二个项 by mushuang
		# 武器的物理攻击力
		totalDamage = calcTotal( exp.getDPSValue ) + exp.getIntensifyDamageInc()
		# 武器的法术攻击力
		if ItemTypeEnum.ITEM_WEAPON_STAFF:
			# 杖类武器强化后法术攻击力总值
			totalMagicDamage = calcTotal( exp.getMagicDamageValue ) + exp.getIntensifyMagicDamageInc()
		else:
			totalMagicDamage = calcTotal( exp.getMagicDamageValue )

		# 强化附加描述
		intenDamageDes = ""
		intenMagicDes = ""
		intensify = self.getIntensifyLevel()
		if intensify != 0:
			# 强化附加物理攻击力
			# 注意这里，服务器对武器的物攻加值与客户端有略微区别，所以这个公式中多出了第二个项 by mushuang
			intenDamageValue = calcIntensifyInc( exp.getDPSValue ) + exp.getIntensifyDamageInc()
			intenDamageDes = "+%i" % intenDamageValue
			intenDamageDes = PL_Font.getSource( intenDamageDes, fc = Const.EQUIP_INTENSIFY_COLOR )
			# 强化附加法术攻击力
			if ItemTypeEnum.ITEM_WEAPON_STAFF:
				# 杖类武器强化后附加值
				intenMagicValue = calcIntensifyInc( exp.getMagicDamageValue ) + exp.getIntensifyMagicDamageInc()
			calcIntensifyInc( exp.getMagicDamageValue )
			intenMagicDes = "+%i" % intenMagicValue
			intenMagicDes = PL_Font.getSource( intenMagicDes, fc = Const.EQUIP_INTENSIFY_COLOR )

		# 灵魂锁链绑定附加描述
		addDamageDes = ""
		addMagicDes = ""
		if self.isObey():
			# 灵魂锁链附加物理攻击力
			addDamageValue = calcObeyInc( exp.getDPSValue )
			addDamageDes = "+%i" % addDamageValue
			addDamageDes = PL_Font.getSource( addDamageDes, fc = "c7" )
			if addDamageValue < 1.0: addDamageDes = ""
			# 灵魂锁链附加法术攻击力
			addMagicValue = calcObeyInc( exp.getMagicDamageValue )
			addMagicDes = "+%i" % addMagicValue
			addMagicDes = PL_Font.getSource( addMagicDes, fc = "c7" )
			if addMagicValue < 1.0: addMagicDes = ""

		# 物理攻击
		desDps = ""
		if totalDamage:
			desDps = lbs_CWeapon[1] % totalDamage
			if len( addDamageDes ) or len( intenDamageDes ):
				hasInf = ""
				hasObe = ""
				if len( intenDamageDes ): hasInf = lbs_CWeapon[2]
				if len( addDamageDes ): hasObe = lbs_CWeapon[3]
				des = PL_Font.getSource( desDps, fc = "c4" )
				desDps = "%s(%s%s)" % ( des, hasInf + intenDamageDes, hasObe + addDamageDes )

		# 法术攻击
		desMgicP = ""
		if totalMagicDamage:
			desMgicP = lbs_CWeapon[4] % totalMagicDamage
			if len( addMagicDes ) or len( intenMagicDes ):
				hasInf = ""
				hasObe = ""
				if len( intenMagicDes ): hasInf = lbs_CWeapon[2]
				if len( addMagicDes ): hasObe = lbs_CWeapon[3]
				des = PL_Font.getSource( desMgicP, fc = "c4" )
				desMgicP = "%s(%s%s)" % ( des, hasInf + intenMagicDes, hasObe + addMagicDes )

		# 武器的基本属性 (物理攻击 ,法术攻击 ....)
		desAttribute = []
		if desDps: desAttribute.append( desDps )
		if desMgicP: desAttribute.append( desMgicP )
		self.desFrame.SetDesSeveral("Attribute" , desAttribute )

		# 神器描述 神器技能说明
		skillID = self.getGodWeaponSkillID()
		if  skillID > 0:
			# gw = PL_Font.getSource( , fc = "c8" )
			desGW = PL_Font.getSource( lbs_CWeapon[5], fc = "c24" )
			skillInst = getSkill( skillID )
			desGWS = skillInst.getDescription()
			desGWS = PL_Font.getSource( desGWS, fc = "c24" )
			self.desFrame.SetDescription( "godweaponskill", desGW )
			self.desFrame.SetDescription( "godweaponskilldes", desGWS )