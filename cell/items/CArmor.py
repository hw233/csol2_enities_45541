# -*- coding: gb18030 -*-

# $Id: CArmor.py,v 1.15 2008-09-04 07:44:43 kebiao Exp $

"""

"""
from CEquip import *
from ItemSystemExp import EquipQualityExp
g_equipQuality = EquipQualityExp.instance()
from ItemSystemExp import ItemTypeAmendExp
g_armorAmend = ItemTypeAmendExp.instance()
from ItemSystemExp import EquipQualityExp
g_itemQualityExp = EquipQualityExp.instance()
import math
import csconst
import csdefine
import Const
import ItemTypeEnum
from ItemSystemExp import EquipIntensifyExp
from ItemSystemExp import EquipExp
g_equipIntensify = EquipIntensifyExp.instance()
import CombatUnitConfig

class CArmor( CEquip ):
	"""
	护甲基础类

	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )

	def getFDict( self ):
		"""
		Virtual Method
		获取防具效果类型自定义数据格式
		用于发送到客户端
		return ARMOR_EFFECT FDict, Define in alias.xml
		"""
		data = { 	"modelNum"		:	self.model(),
					"iLevel"		:	self.getIntensifyLevel(),
					}

		return data

	def addGodEffect( self, owner ):
		"""
		附加防具套装10%加成效果
		7件防具全部是 同一个10级范围内，逆天前缀名，并且属性前缀名也相同时
		会有额外的套装效果（10%HP上限，10%MP上限 by姜毅）
		"""
		# 只有装上，防具类而且是逆天装备时，才会触发效果检测
		if owner.godSuitEquipActive: return
		type = self.getType()
		if type not in ItemTypeEnum.ARMOR_SUIT: return
		preFix = self.getPrefix()
		if preFix != ItemTypeEnum.CPT_MYGOD: return
		iPrefix = self.query( "propertyPrefix", 0 )
		iLevel = self.getLevel() / 10
		ARMOR_ORDER = [	ItemTypeEnum.CEL_HEAD,
						ItemTypeEnum.CEL_BODY,
						ItemTypeEnum.CEL_BREECH,
						ItemTypeEnum.CEL_VOLA,
						ItemTypeEnum.CEL_HAUNCH,
						ItemTypeEnum.CEL_CUFF,
						ItemTypeEnum.CEL_FEET,
						]
		for index in ARMOR_ORDER:
			item = owner.getItem_( index )
			if item is None: return
			if item.getLevel()/10 != iLevel: return
			if item.getPrefix() != preFix: return
			if item.query( "propertyPrefix", 0 ) != iPrefix: return

		# 额外套装效果 生命值和法力值 基于体质 提高10%
		# 用于逆天同属性前缀套装 血 法 10% 加成效果
		owner.HP_Max_percent += Const.ALL_GOD_PROP_EFFECT
		owner.MP_Max_percent += Const.ALL_GOD_PROP_EFFECT
		# 并给自身加上属性标记
		owner.godSuitEquipActive = True

	def wield( self, owner, update = True ):
		"""
		装备道具

		@param  owner: 背包拥有者
		@type   owner: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    True 装备成功，False 装备失败
		@return:    BOOL
		"""
		if not CEquip.wield( self, owner, update ): return False

		exp = EquipExp( self, owner )

		# type( armor_base ) = INT16
		# 物理防御值
		owner.armor_base += exp.getArmorBase()

		# type( magic_armor_base ) = INT16
		# 法术防御值
		owner.magic_armor_base += exp.getMagicArmorBase()

		# 抵抗沉默
		owner.resist_chenmo_probability_value += exp.getResistMagicHushProb()

		# 抵抗眩晕
		owner.resist_giddy_probability_value += exp.getResistGiddyProb()

		# 抵抗定身
		owner.resist_fix_probability_value += exp.getResistFixProb()

		# 降低对方物理命中点数
		owner.receive_be_hit_value -= exp.getReduceTargetHit()

		# 抵抗昏睡
		owner.resist_sleep_probability_value += exp.getResistSleepProb()

		# 招架点数
		owner.resist_hit_probability_value += exp.getResistHitProb()

		# 闪避点数
		owner.dodge_probability_value += exp.getDodgeProb()
		
		# 御敌点数
		owner.reduce_role_damage_value += exp.getReduceRoleD()

		# 逆天同前缀套装属性加成 by 姜毅
		self.addGodEffect( owner )

		# 重新计算属性
		if update: owner.calcDynamicProperties()
		return True

	def unWield( self, owner, update = True ):
		"""
		卸下装备，该接口被继承后，必须最后被调用，以保证重新计算属性的时候所有的装备附加属性都是被去掉了的！

		@param  owner: 背包拥有者
		@type   owner: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    无
		"""
		# 如果没有装备效果则不用unwield
		if not self.isAlreadyWield(): return

		exp = EquipExp( self, owner )

		# 物理防御值
		owner.armor_base -= exp.getArmorBase()

		# 法术防御值
		owner.magic_armor_base -= exp.getMagicArmorBase()

		# 抵抗沉默
		owner.resist_chenmo_probability_value -= exp.getResistMagicHushProb()

		# 抵抗眩晕
		owner.resist_giddy_probability_value -= exp.getResistGiddyProb()

		# 抵抗定身
		owner.resist_fix_probability_value -= exp.getResistFixProb()

		# 降低对方物理命中点数
		owner.receive_be_hit_value += exp.getReduceTargetHit()

		# 抵抗昏睡
		owner.resist_sleep_probability_value -= exp.getResistSleepProb()

		# 招架点数
		owner.resist_hit_probability_value -= exp.getResistHitProb()

		# 闪避点数
		owner.dodge_probability_value -= exp.getDodgeProb()

		# 御敌点数
		owner.reduce_role_damage_value -= exp.getReduceRoleD()
		
		
		# 逆天同前缀套装属性加成的消除 by 姜毅
		if owner.godSuitEquipActive:
			owner.HP_Max_percent -= Const.ALL_GOD_PROP_EFFECT
			owner.MP_Max_percent -= Const.ALL_GOD_PROP_EFFECT
			owner.godSuitEquipActive = False

		# 必须放置到最后 以保证所有的装备附加的属性都去掉了！
		CEquip.unWield( self, owner, update )
		return True

	def CalculateHardiness( self, owner ):
		"""
		计算耐久度(品质改变时要重新计算耐久度)
		"""
		m_type  = self.getType()
		m_level = self.getLevel()
		m_BaseRate = self.getBaseRate()

		func = CombatUnitConfig.FUNC_CALCHARDINESS_MAPS.get( m_type, None )
		if func is None: return
		hardiness = func( m_level, m_BaseRate )

		self.updataHardiness( hardiness, owner )

	def setQuality( self, quality, owner = None ):
		"""
		设置防具品质 by姜毅
		"""
		CEquip.setQuality( self, quality, owner )


### end of class: CArmor ###


#
# $Log: not supported by cvs2svn $
# Revision 1.14  2008/07/09 03:22:28  wangshufeng
# armor_value -> armor_base
# magic_armor_value -> magic_armor_base
#
# Revision 1.13  2008/04/25 04:02:36  yangkai
# no message
#
# Revision 1.12  2008/04/25 04:01:43  yangkai
# no message
#
# Revision 1.11  2008/04/23 03:58:16  yangkai
# no message
#
# Revision 1.10  2008/04/22 10:46:13  yangkai
# no message
#
# Revision 1.9  2008/02/22 01:30:42  yangkai
# 装备上即重新刷一遍玩家所有属性
#
# Revision 1.8  2008/01/11 03:38:05  yangkai
# 修正 玩家属性magic_armor_base 和 armor_base 赋值类型错误
#
# Revision 1.7  2007/12/19 01:52:26  yangkai
# 修正读取物品属性的默认类型
#
# Revision 1.6  2007/11/24 03:06:25  yangkai
# 添加实现装备/卸下 防具代码
#
# Revision 1.5  2007/11/08 06:20:30  yangkai
# 增加接口：
# - intensify()
#
# Revision 1.4  2007/08/15 07:52:03  yangkai
# 修改:
#     - 防具属性修改
#     - 防具装备/卸下函数处理
#
# Revision 1.3  2006/08/18 07:01:05  phw
# 修改接口：
#     wield()
#     unwield()
#     删除了对武器当前装备情况的检查
#
# Revision 1.2  2006/08/11 02:57:34  phw
# 属性更名：修改所有itemInstance.keyName或itemInstance.id()为itemInstance.id
#
# Revision 1.1  2006/08/09 08:23:37  phw
# no message
#
#
