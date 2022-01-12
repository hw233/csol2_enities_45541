# -*- coding: gb18030 -*-
#
# $Id: CasterCondition.py,v 1.5 2008-08-13 02:24:25 kebiao Exp $

"""
一些对施法者是否能施法的对像集合。
"""

import csdefine
import csstatus
import ItemTypeEnum
from bwdebug import *
from csdefine import *		# for eval expediently
from items.ItemDataList import ItemDataList
from config.client.labels.skills import lbs_CasterCondition
import BigWorld
import csconst

g_items = ItemDataList.instance()

class CasterConditionBase:
	"""
	基础类
	"""
	def __init__( self , conditionType ):
		"""
		virtual method.
		"""
		self.ctype = conditionType		#加入标记,记录该施放条件属于什么类型

	def init( self, dict ):
		"""
		virtual method.
		spell的某种condition(ReceiverCondition or CasterConditionBase)配置文件 python dict
		"""
		pass

	def valid( self, entity ):
		"""
		virtual method.
		校验目标是否符合选择要求。

		@param entity: Entity
		@type  entity: Entity
		@return:       INT，see also csdefine.SKILL_*
		@rtype:        INT
		"""
		return csstatus.SKILL_UNKNOW

	def GetConditionType( self ):		#获取施放条件的类型
		"""
		返回需求的类型
		"""
		return self.ctype


class SpellAllow( CasterConditionBase ):
	"""
	允许施法(导致不可以施法的原因很多，如被沉默、昏迷等)
	"""
	def valid( self, entity ):
		"""
		"""
		if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
			if entity.actionSign( csdefine.ACTION_FORBID_SPELL_PHY ) or entity.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
				 return csstatus.SKILL_CANT_CAST
		elif self.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			if entity.actionSign( csdefine.ACTION_FORBID_SPELL_MAGIC ) or entity.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
				 return csstatus.SKILL_CANT_CAST
		return csstatus.SKILL_GO_ON

class AttackAllow( CasterConditionBase ):
	"""
	允许施展普通物理攻击
	"""
	def valid( self, entity ):
		"""
		"""
		if not entity.actionSign( csdefine.ACTION_FORBID_ATTACK ):
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_CANT_CAST

class BuffHave( CasterConditionBase ):
	"""
	身上必须存在指定类型的buff，只能用于施法者条件判断。
	"""
	def init( self, dict ):
		"""
		"""
		self._buffID = eval( dict[ "BuffTypeID" ] )

	def valid( self, entity ):
		"""
		"""
		if entity.getBuffByType( self._buffID ) is not None:
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_BUFF_NOT_EXIST


class BuffNoHave( CasterConditionBase ):
	"""
	身上不存在指定类型的buff，只能用于施法者条件判断。
	"""
	def init( self, dict ):
		"""
		"""
		self._buffID = eval( dict[ "BuffTypeID" ] )

	def valid( self, entity ):
		"""
		"""
		if entity.getBuffByType( self._buffID ) is None:
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_BUFF_EXIST

class InFightState( CasterConditionBase ):
	"""
	必须处于战斗状态
	"""
	def valid( self, entity ):
		"""
		"""
		if entity.getState() == csdefine.ENTITY_STATE_FIGHT:
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_NOT_IN_FIGHT

class NotInFightState( CasterConditionBase ):
	"""
	必须处于非战斗状态
	"""
	def valid( self, entity ):
		"""
		"""
		if entity.getState() != csdefine.ENTITY_STATE_FIGHT:
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_IN_FIGHT

class IsDead( CasterConditionBase ):
	"""
	必须处于死亡状态
	"""
	def valid( self, entity ):
		"""
		"""
		if entity.isDead():
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_IN_LIVE

class IsLive( CasterConditionBase ):
	"""
	必须处于非死亡状态
	"""
	def valid( self, entity ):
		"""
		"""
		if not entity.isDead():
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_IN_DEAD

class EmptyHand( CasterConditionBase ):
	"""
	必须处于空手
	"""
	def valid( self, entity ):
		"""
		"""
		if entity.isEmptyHand():
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_EMPTY_HAND_REQUIRE

class PrimaryHandEmpty( CasterConditionBase ):
	"""
	主(拿武器的)手必须为空
	"""
	def valid( self, entity ):
		"""
		"""
		if entity.primaryHandEmpty():
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_EMPTY_HAND_REQUIRE

class WeaponConfine( CasterConditionBase ):
	"""
	身上必须要有武器
	"""
	def valid( self, entity ):
		"""
		"""
		#weapon = entity.getItem_( ItemTypeEnum.CWT_RIGHTHAND )		#如此只能判断是否装备了武器，不能判断武器耐久度是否为零
		if not entity.primaryHandEmpty():
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_WEAPON_EQUIP_REQUIRE

class PossessItem( CasterConditionBase ):
	"""
	身上必须存在某个物品
	"""
	def init( self, dict ):
		"""
		"""
		self._itemTypes = []
		for param in dict["ExtraValue"].split( ";" ):
			val = param.split("'")
			if len(val) < 2 or val[0] != "ItemType":continue
			self._itemTypes.append( ( val[1], int(val[2]) ) )#物品ID，数量

	def valid( self, entity ):
		"""
		"""
		for itemID, amount in self._itemTypes:
			if not entity.checkItemFromNKCK_( itemID, amount ) :
				return csstatus.SKILL_MISSING_ITEM
		return csstatus.SKILL_GO_ON


class WeaponEquip( CasterConditionBase ):
	"""
	必须装备了某武器
	"""
	def init( self, dict ):
		"""
		"""
		self._itemTypes = []
		for param in dict["ExtraValue"].split( ";" ):
			val = param.split("'")
			if len(val) < 1 or val[0] != "EquipWeapon":continue
			self._itemTypes.append( eval( "ItemTypeEnum." + val[1] ) )#武器类型
		if len( self._itemTypes ) == 0:
			raise SystemError, "Can not get a value.[ %s ]" % dict["ExtraValue"]

	def valid( self, entity ):
		"""
		"""
		weapon = entity.getItem_( ItemTypeEnum.CWT_RIGHTHAND )
		if weapon is None:
			return csstatus.SKILL_WEAPON_EQUIP_REQUIRE
		if weapon.query( "type" ) in self._itemTypes:
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_WEAPON_EQUIP_REQUIRE

class ShieldEquip( CasterConditionBase ):
	"""
	必须装备盾牌
	"""
	def init( self, dict ):
		"""
		"""
		pass

	def valid( self, entity ):
		"""
		"""
		weapon = entity.getItem_( ItemTypeEnum.CWT_LEFTHAND )
		if weapon is None:
			return csstatus.SKILL_WEAPON_EQUIP_SHIELD
		return csstatus.SKILL_GO_ON

class NoPKState( CasterConditionBase ):
	"""
	非PK状态
	"""
	def init( self, dict ):
		"""
		"""
		pass

	def valid( self, entity ):
		"""
		"""
		if entity.pkValue != 0:
			return csstatus.SKILL_CAST_IS_NO_PK
		return csstatus.SKILL_GO_ON

class InAppointSpace( CasterConditionBase ):
		"""
		在指定的地区使用
		"""
		spaceType = {	SPACE_TYPE_NORMAL			: lbs_CasterCondition[1],
						SPACE_TYPE_CITY_WAR			: lbs_CasterCondition[3],
						SPACE_TYPE_TONG_ABA		: lbs_CasterCondition[4],
						SPACE_TYPE_TONG_TERRITORY	: lbs_CasterCondition[5],
		}

		def init( self, dict ):
			self._spaces = []
			for param in dict["ExtraValue"].split( "," ):
				if len( param ) > 0:
					self._spaces.append( eval( "csdefine." +  param ) ) #地图类型

		def valid( self, entity ):
			if entity.getCurrentSpaceType() not in self._spaces:	#如果玩家当前处的地图类型不在需求的类型中
				return	 csstatus.SKILL_CAST_IS_NOTIN_APPOINTSPACE
			return csstatus.SKILL_GO_ON

class InAppointSpaceNotUse( InAppointSpace ):
		"""
		指定地图不能使用
		"""
		def valid( self, entity ):
			if InAppointSpace.valid( self, entity ) == csstatus.SKILL_GO_ON:
				return csstatus.SKILL_CAST_IS_NOTIN_APPOINTSPACE
			return csstatus.SKILL_GO_ON

class IsWieldTalish( CasterConditionBase ):
	"""
	是否装备法宝
	"""
	def init( self, dict ):
		"""
		"""
		pass

	def valid( self, entity ):
		"""
		"""
		talish = entity.getItem_( ItemTypeEnum.CWT_TALISMAN )
		if talish is None:
			return csstatus.SKILL_NOT_WIELD_TALISH
		return csstatus.SKILL_GO_ON

class IsNotEnemyState( CasterConditionBase ):
	"""
	是否不为敌对状态
	"""
	def init( self, dictDat ):
		"""
		"""
		pass

	def valid( self, entity ):
		"""
		"""
		target = BigWorld.entities.get( entity.targetID )
		if target is None: return csstatus.SKILL_CAN_NOT_CAST_TO_ENEMY
		if not target.inWorld: return csstatus.SKILL_CAN_NOT_CAST_TO_ENEMY

		if entity.queryRelation( target ) != csdefine.RELATION_ANTAGONIZE:
			return csstatus.SKILL_CAN_NOT_CAST_TO_ENEMY

		return csstatus.SKILL_GO_ON

class IsPosture( CasterConditionBase ):
	"""
	在某种姿态
	"""

	def init( self, dictDat ):
		"""
		"""
		self.posture = 0
		for extraValue in dictDat["ExtraValue"].split( ";" ):
			valueList = extraValue.split( "'" )
			if len( valueList ) < 1 or valueList[0] != "Posture":
				continue
			self.posture = int( valueList[1] )

	def valid( self, entity ):
		"""
		"""
		if entity.isPosture( self.posture ):
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_NOT_IN_POSTURE

class IsSpaceSupportFly( CasterConditionBase ):
	"""
	空间是否支持飞行 by mushuang
	"""
	def init( self, dictDat ):
		"""
		"""
		pass
			
	def valid( self, entity ):
		"""
		"""
		
		canFly = csstatus.SKILL_UNKNOW
		str = BigWorld.getSpaceDataFirstForKey( entity.spaceID, csconst.SPACE_SPACEDATA_CAN_FLY )
		try:
			canFly = csstatus.SKILL_GO_ON if eval( str ) else csstatus.FLYING_NOT_ALLOWED
		except:
			ERROR_MSG( "Incorrect space data, please check space data for key: csconst.SPACE_SPACEDATA_CAN_FLY!" )
			return csstatus.SKILL_UNKNOW
		
		return canFly
		
class IsFlyingState( CasterConditionBase ):
	"""
	是否处于飞行状态 by mushuang
	"""
	def init( self, dictDat ):
		"""
		"""
		pass
			
	def valid( self, entity ):
		"""
		"""
		
		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			return csstatus.SKILL_GO_ON if entity.hasFlag( csdefine.ROLE_FLAG_FLY ) else csstatus.FLYING_STATUS_NEEDED
		else:
			ERROR_MSG( "Entity does not have attribute state! Wrong object may be passed in!" )
			return csstatus.SKILL_UNKNOW
			
class IsGroundState( CasterConditionBase ):
	"""
	是否处于地面状态 by mushuang
	"""
	def init( self, dictDat ):
		"""
		"""
		pass
			
	def valid( self, entity ):
		"""
		"""
		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			return csstatus.SKILL_GO_ON if not entity.hasFlag( csdefine.ROLE_FLAG_FLY ) else csstatus.GROUND_STATUS_NEEDED
		else:
			ERROR_MSG( "Entity does not have attribute state! Wrong object may be passed in!" )
			return csstatus.SKILL_UNKNOW


class CasterCondition:
	"""
	判断施术者是否符合条件
	"""
	m_map = {
			csdefine.CASTER_CONDITION_ATTACK_ALLOW				: AttackAllow,
			csdefine.CASTER_CONDITION_SPELL_ALLOW				: SpellAllow,
			csdefine.CASTER_CONDITION_BUFF_NO_HAVE				: BuffNoHave,
			csdefine.CASTER_CONDITION_BUFF_HAVE					: BuffHave,
			csdefine.CASTER_CONDITION_FIGHT_STATE				: InFightState,
			csdefine.CASTER_CONDITION_FIGHT_NOT_STATE			: NotInFightState,
			csdefine.CASTER_CONDITION_STATE_DEAD				: IsDead,
			csdefine.CASTER_CONDITION_STATE_LIVE				: IsLive,
			csdefine.CASTER_CONDITION_EMPTY_HAND				: EmptyHand,
			csdefine.CASTER_CONDITION_EMPTY_PRIMARY_HAND		: PrimaryHandEmpty,
			csdefine.CASTER_CONDITION_WEAPON_CONFINE			: WeaponConfine,
			csdefine.CASTER_CONDITION_POSSESS_ITEM				: PossessItem,
			csdefine.CASTER_CONDITION_WEAPON_EQUIP				: WeaponEquip,
			csdefine.CASTER_CONDITION_SHIELD_EQUIP				: ShieldEquip,
			csdefine.CASTER_CONDITION_STATE_NO_PK				: NoPKState,
			csdefine.CASTER_CONDITION_IN_APPOINT_SPACE			: InAppointSpace,		#在指定的地图才能使用
			csdefine.CASTER_CONDITION_IN_APPOINT_SPACE_NOT_USE	: InAppointSpaceNotUse,	#在指定的地图不能使用
			csdefine.CASTER_CONDITION_WEAPON_TALISMAN			: IsWieldTalish,		# 装备法宝
			csdefine.CASTER_CONDITION_NOT_ENEMY_STATE			: IsNotEnemyState,		# 是否不为敌对状态
			csdefine.CASTER_CONDITION_POSTURE					: IsPosture,			# 正在某种姿态
			csdefine.CASTER_CONDITION_SPACE_SUPPORT_FLY			: IsSpaceSupportFly,	# 空间支持飞行
			csdefine.CASTER_CONDITION_IS_FLYING_STATUS			: IsFlyingState,		# 正处在飞行状态
			csdefine.CASTER_CONDITION_IS_GROUND_STATUS			: IsGroundState,		# 正处在地面状态
			}

	def __init__( self ):
		"""
		virtual method.
		"""
		self._conditions = []

	def __iter__( self ) :
		"""
		"""
		return self._conditions.__iter__()

	def init( self, dict ):
		"""
		virtual method.
		spell的某种condition配置文件dict
		"""
		cnd = dict[ "conditions" ]
		if len( cnd ) <= 0:
			return
		value = eval( cnd )
		for k, c in self.m_map.iteritems():
			if value & k:
				instance = c(k)
				instance.init( dict )
				self._conditions.append( instance )

	def valid( self, caster ):
		"""
		判断目标是否有效

		@return: INT，see also csdefine.SKILL_*
		@rtype:  INT
		"""
		for cnd in self._conditions:
			state = cnd.valid( caster )
			if state != csstatus.SKILL_GO_ON:
				return state
		return csstatus.SKILL_GO_ON

	def getNeedWeaponDescription( self , entity ):
		"""
		获取施放该技能需要的武器的种类(远程或者近程或者盾或者 远程/近程武器)
		@RETURN		TUPLE: (技能对武器的需求类型,是否满足条件)
		"""
		conditions = self._conditions
		if not conditions:		#没有需求
			return None
		weapondes = ""			#需求的武器
		bequip    = 1			#是否满足需求
		weapon = entity.getItem_( ItemTypeEnum.CWT_RIGHTHAND )
		for condition in conditions:
			if condition.GetConditionType() == csdefine.CASTER_CONDITION_WEAPON_CONFINE:	#身上装备了武器 无论什么
				weapondes += lbs_CasterCondition[10]
				if not weapon:
					bequip = 0
			if condition.GetConditionType() == csdefine.CASTER_CONDITION_WEAPON_EQUIP:	#身上装备了某武器
				for weaponType in condition._itemTypes:
					weaponName = ItemTypeEnum.WEAPONNAME_DIC.get( weaponType )
					if weaponName:
						if weapondes:
							weapondes = weapondes + "," + weaponName
						else:
							weapondes += weaponName
					if not weapon or not weapon.query( "type" ) in condition._itemTypes:
						bequip = 0
			if condition.GetConditionType() == csdefine.CASTER_CONDITION_SHIELD_EQUIP:		#身上装备盾
				if weapondes:
					weapondes += ","
				weapondes += lbs_CasterCondition[11]
				shield = entity.getItem_( ItemTypeEnum.CWT_LEFTHAND )
				if shield is None:
					bequip = 0


		if weapondes =="":
			return ()
		return ( weapondes , bequip )

	def getNeedItemDescription( self , entity ):
		"""
		获取施放该技能需要哪些物品的描述
		@RETURN		LIST: [ (需求的物品名称 , 是否满足) ]
		"""
		conditions = self._conditions
		if not conditions:		#没有需求
			return []
		Itemdes = []			#需求的物品
		for condition in conditions:
			if condition.GetConditionType() == csdefine.CASTER_CONDITION_POSSESS_ITEM:	#身上需要某个物品
				for itemID, amount in condition._itemTypes:
					name = g_items.id2name( itemID )
					if amount > 1:
						name = name + ( 'x%s'% amount )
					if entity.checkItemFromNKCK_( int(itemID) , int( amount ) ):
						Itemdes.append( ( name , 1 ) )
					else:
						Itemdes.append( ( name , 0 ) )
		return Itemdes

	def getNeedSpaceDescription( self, entity ):
		"""
		获取施放该魔法需要在的地图
		@RETURN		TUPLE: ( 需要的地图 , 是否满足 )
		"""
		conditions = self._conditions
		if not conditions:		#没有需求
			return None
		spaces	= ""		#需求的地图
		bein	= 1			#是否满足
		for condition in conditions:
			if condition.GetConditionType() == csdefine.CASTER_CONDITION_IN_APPOINT_SPACE:
				for space in condition._spaces:
					spaceName = condition.spaceType.get( space )
					if spaceName:
						if spaces:
							spaces = spaces + '/' + spaceName
						else:
							spaces += spaceName
				if entity.getCurrentSpaceType() not in condition._spaces:
					bein = 0
		if spaces == "":
			return ()
		return ( spaces , bein )


#
# $Log: not supported by cvs2svn $
# Revision 1.4  2008/07/15 04:08:01  kebiao
# 将技能配置修改到datatool相关初始化需要修改
#
# Revision 1.3  2008/05/30 03:06:16  yangkai
# 装备栏调整引起的部分修改
#
# Revision 1.2  2008/05/27 09:04:29  kebiao
# 增加装备盾牌
#
# Revision 1.1  2008/01/05 03:47:16  kebiao
# 调整技能结构，目录结构
#
#