# -*- coding: gb18030 -*-

# $Id: CWeapon.py,v 1.22 2008-09-04 07:44:43 kebiao Exp $

"""

"""
from bwdebug import *
import csconst
import ItemTypeEnum
from ItemSystemExp import EquipIntensifyExp

from config.item.GodWeaponSkillModel import Datas as gw_SM

from CEquip import CEquip
from Love3 import g_skills
from ItemSystemExp import EquipExp

g_equipIntensify = EquipIntensifyExp.instance()

class CWeapon( CEquip ):
	"""
	武器类

	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )

	def getFDict( self ):
		"""
		Virtual Method
		获取武器效果类型自定义数据格式
		用于发送到客户端
		return WEAPON_EFFECT FDict, Define in alias.xml
		"""
		modelNum = self.model()
		gw_sk = self.getGodWeaponSkillID()
		if gw_sk in gw_SM:
			modelNum += gw_SM[gw_sk]
		data = { 	"modelNum"		:	modelNum,
					"iLevel"		:	self.getIntensifyLevel(),
					"stAmount"		:	self.getBjExtraEffectCount(),
					}

		return data

	def wield( self, owner, update = True ):
		"""
		装备道具

		@param    owner: 背包拥有者
		@type     owner: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    True 装备成功，False 装备失败
		@return:    BOOL
		"""
		if not CEquip.wield( self, owner, update ):
			return False

		exp = EquipExp( self, owner )

		intensifyLevel = self.getIntensifyLevel()
		if intensifyLevel != 0: #有强化则设置强化DPS加值
			# Note: damage_min_base 值由 dps * speed 算出来的
			# 在这里设 damage_min_base 是毫无意义的
			owner.damage_min_value += exp.getIntensifyDamageInc()
			owner.damage_max_value += exp.getIntensifyDamageInc()
			if ItemTypeEnum.ITEM_WEAPON_STAFF:
				owner.magic_damage_value += exp.getIntensifyMagicDamageInc()

		# 附加武器的dps加值
		owner.physics_dps_value += exp.getDPSValue()

		# CombatUnit的DPS波动加值 = 武器获取的DPS波动
		owner.wave_dps_base = exp.getDPSFluctuation()

		# 附加武器的魔攻加值
		owner.magic_damage_value += exp.getMagicDamageValue()

		# CombatUnit的攻击速度基础值 = 武器获取的攻击速度
		owner.hit_speed_base = exp.getHitSpeedBase()

		# CombatUnit的攻击距离基础值 = 武器获取的攻击距离
		owner.range_base = exp.getAttackRangeBase()
		
		# 破敌点数
		owner.add_role_damage_value += exp.getAddRoleD()
		
		"""# 添加神器技能 by 姜毅
		skillID = self.getGodWeaponSkillID()
		if skillID > 0:
			skill = g_skills[skillID]
			owner.appendAttackerHit( skill )
		"""

		if update: owner.calcDynamicProperties()
		return True

	def unWield( self, owner, update = True ):
		"""
		卸下装备

		@param    owner: 背包拥有者
		@type     owner: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    无
		"""
		# 如果没有装备效果则不用unwield
		if not self.isAlreadyWield(): return

		exp = EquipExp( self, owner )

		intensifyLevel = self.getIntensifyLevel()
		if intensifyLevel != 0:
			owner.damage_min_value -= exp.getIntensifyDamageInc()
			owner.damage_max_value -= exp.getIntensifyDamageInc()
			if ItemTypeEnum.ITEM_WEAPON_STAFF:
				owner.magic_damage_value -= exp.getIntensifyMagicDamageInc()
		try:
			owner.physics_dps_value -= exp.getDPSValue()
		except:
			owner.physics_dps_value = 0  #防止修改玩家属性导致数据溢出
		# 武器卸下则表示空手
		# 空手的DPS波动基础值和攻击速度和攻击距离为固定值
		owner.wave_dps_base = exp.getDefaultDPSFluctuation()
		owner.hit_speed_base = exp.getDefaultHitSpeedBase()
		owner.range_base = exp.getDefaultAttackRangeBase()

		owner.magic_damage_value -= exp.getMagicDamageValue()
		
		# 破敌点数
		owner.add_role_damage_value -= exp.getAddRoleD()

		"""# 卸除神器技能
		skillID = self.getGodWeaponSkillID()
		if skillID > 0:
			owner.removeAttackerHitByID( skillID )
		"""

		CEquip.unWield( self, owner, update )
		return True

	def CalculateHardiness( self, owner ):
		"""
		计算耐久度(品质改变时要重新计算耐久度)
		"""
		m_type  = self.getType()
		m_level = self.getLevel()
		m_BaseRate = self.getBaseRate()
		# 单手剑、法杖、单手斧、长弓
		w_types = [ItemTypeEnum.ITEM_WEAPON_SWORD1, ItemTypeEnum.ITEM_WEAPON_STAFF, ItemTypeEnum.ITEM_WEAPON_AXE1, ItemTypeEnum.ITEM_WEAPON_LONGBOW]
		if m_type in w_types:
			hardiness = int( ( pow( m_BaseRate, 1.54 ) * pow( m_level, 1.2 ) * 20 + 20000 ) * 100 )
		else:
			ERROR_MSG( "The type of weapon(%s) is wrong!" % self.id )
			return
		self.updataHardiness( hardiness, owner )

	def setGodWeapon( self, skillID, owner = None ):
		"""
		设置神器属性
		"""
		self.set( "param1", skillID, owner )

	def getGodWeaponSkillID( self ):
		"""
		获取神器属性技能ID
		"""
		return self.query( "param1", 0 )

#
#增加神器技能时，因为保存的是技能ID而非UID导致BUG，现在神器取消了，不做处理，仅去掉增加、卸除神器技能的操作——grl20140408
#
# $Log: not supported by cvs2svn $
# Revision 1.21  2008/07/17 07:50:47  yangkai
# 修正装备强化无效问题
#
# Revision 1.20  2008/07/09 03:26:37  wangshufeng
# damage_min_value -> damage_min_base
# damage_max_value -> damage_max_base
# magic_damage_value -> magic_damage_base
#
# Revision 1.19  2008/04/22 10:46:13  yangkai
# no message
#
# Revision 1.18  2008/04/12 02:14:10  yangkai
# 添加武器对强化属性的处理
#
# Revision 1.17  2008/03/29 08:36:47  yangkai
# 装备强化完善
#
# Revision 1.16  2008/03/08 06:24:23  yangkai
# no message
#
# Revision 1.15  2008/03/01 02:34:33  yangkai
# 计算用的DPS = 表格填的DPS * 基础属性比率
#
# Revision 1.14  2008/02/22 01:37:21  yangkai
# 装备上即重新刷一遍玩家所有属性
#
# Revision 1.13  2007/12/19 01:52:41  yangkai
# 修正读取物品属性的默认类型
#
# Revision 1.12  2007/12/14 08:05:41  yangkai
# 卸载装备后，hit_speed_base = 1.5
#
# Revision 1.11  2007/11/24 03:07:54  yangkai
# 添加实现装备/卸下 武器代码
#
# Revision 1.10  2007/11/08 06:21:28  yangkai
# 增加接口：
# - intensify()
#
# Revision 1.9  2007/10/26 07:00:19  kebiao
# 根据全新的策划战斗系统做调整
#
# Revision 1.8  2007/08/28 02:32:01  kebiao
# 调整战斗公式和属性
#
# Revision 1.7  2007/08/15 07:52:37  yangkai
# 修改:
#     - 武器属性修改
#     - 武器装备/卸下函数处理
#
# Revision 1.6  2007/08/01 05:43:04  phw
# removed: import AttrDefine
#
# Revision 1.5  2007/01/03 04:01:45  phw
# 恢复了使用武器的攻击延迟
# 取消了空手时设置owner.range_base值,统一由role.py里处理
#
# Revision 1.4  2006/08/31 08:38:47  phw
# modify method:
#     wield()
#     unwield()
#     实现了武器的最小、最大物理伤害。
#
# Revision 1.3  2006/08/18 06:59:21  phw
# 修改接口：
#     wield()
#     unwield()
#     删除了旧系统的伤害判断方式，根据新系统进行了简化。
#
# Revision 1.2  2006/08/11 02:57:34  phw
# 属性更名：修改所有itemInstance.keyName或itemInstance.id()为itemInstance.id
#
# Revision 1.1  2006/08/09 08:23:37  phw
# no message
#
#
