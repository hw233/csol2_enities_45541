# -*- coding: gb18030 -*-
#
# $Id: CasterCondition.py,v 1.15 2008-08-13 02:24:18 kebiao Exp $

"""
一些对施法者是否能施法的对像集合。
"""

import csdefine
import cschannel_msgs
import ShareTexts as ST
import csstatus
from csdefine import *			# just for "eval" expediently
from bwdebug import *
import ItemTypeEnum
from interface.State import State
import csconst
import BigWorld

class CasterConditionBase:
	"""
	基础类
	"""
	def __init__( self ):
		"""
		virtual method.
		"""
		pass

	def init( self, dictDat ):
		"""
		virtual method.
		spell的某种condition(ReceiverCondition or CasterConditionBase)配置
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
	def init( self, dictDat ):
		"""
		"""
		self._buffID = eval( dictDat[ "BuffTypeID" ] )

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
	def init( self, dictDat ):
		"""
		"""
		self._buffID = eval( dictDat[ "BuffTypeID" ] )

	def valid( self, entity ):
		"""
		"""
		if entity.getBuffByType( self._buffID ) is None:
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_BUFF_EXIST


class NotInMoveState( CasterConditionBase ):
	"""
	必须处于非战斗状态
	"""
	def valid( self, entity ):
		"""
		"""
		if not entity.isMoving():
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_IN_MOVING

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
		if entity.state == csdefine.ENTITY_STATE_DEAD:
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_IN_LIVE

class IsLive( CasterConditionBase ):
	"""
	必须处于非死亡状态
	"""
	def valid( self, entity ):
		"""
		"""
		if not entity.state == csdefine.ENTITY_STATE_DEAD:
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
	主(拿武器的)手必须不为空
	"""
	def valid( self, entity ):
		"""
		"""
		if not entity.primaryHandEmpty():
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_WEAPON_EQUIP_REQUIRE

class PossessItem( CasterConditionBase ):
	"""
	身上必须存在某个物品
	"""
	def init( self, dictDat ):
		"""
		"""
		self._itemTypes = []
		for param in dictDat["ExtraValue"].split( ";" ):
			val = param.split("'")
			if len(val) < 2 or val[0] != "ItemType":continue
			self._itemTypes.append( ( val[1], int( val[2] ) ) )#物品ID，数量

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
	def init( self, dictDat ):
		"""
		"""
		self._itemTypes = []
		for param in dictDat["ExtraValue"].split( ";" ):
			val = param.split("'")
			if len(val) < 1 or val[0] != "EquipWeapon":continue
			self._itemTypes.append( eval( "ItemTypeEnum." + val[1] ) )#武器类型
		if len( self._itemTypes ) == 0:
			raise SystemError, "Can not get a value.[ %s ]" % dictDat["ExtraValue"]

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
	def init( self, dictDat ):
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
	def init( self, dictDat ):
		"""
		"""
		pass

	def valid( self, entity ):
		"""
		"""
		if entity.pkValue > 0:
			return csstatus.SKILL_CAST_IS_NO_PK
		return csstatus.SKILL_GO_ON

class InAppointSpace( CasterConditionBase ):
		"""
		在指定的地区使用
		"""
		spaceType = {	SPACE_TYPE_NORMAL			: cschannel_msgs.SKILL_INFO_9 ,
						SPACE_TYPE_CITY_WAR			: cschannel_msgs.SKILL_INFO_11 ,
						SPACE_TYPE_TONG_ABA			: cschannel_msgs.SKILL_INFO_12 ,
						SPACE_TYPE_TONG_TERRITORY	: cschannel_msgs.TONG_INFO_24 ,
		}

		def init( self, dictDat ):
			self._spaces = []
			for param in dictDat["ExtraValue"].split( "," ):
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
	def init( self, dictDat ):
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
		if entity.targetID in entity.enemyList:
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
		
		if isinstance( entity, State ):
			return csstatus.SKILL_GO_ON if entity.hasFlag( csdefine.ROLE_FLAG_FLY ) else csstatus.FLYING_STATUS_NEEDED
		else:
			ERROR_MSG( "Entity is not an instance of State! Wrong object may be passed in!" )
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
		if isinstance( entity, State ):
			return csstatus.SKILL_GO_ON if not entity.hasFlag( csdefine.ROLE_FLAG_FLY ) else csstatus.GROUND_STATUS_NEEDED
		else:
			ERROR_MSG( "Entity is not an instance of State! Wrong object may be passed in!" )
			return csstatus.SKILL_UNKNOW

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
		csdefine.CASTER_CONDITION_MOVE_NOT_STATE			: NotInMoveState,
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

class CasterCondition:
	"""
	判断施术者是否符合条件
	"""
	def __init__( self ):
		"""
		virtual method.
		"""
		self._conditions = []

	def init( self, dictDat ):
		"""
		virtual method.
		spell的某种condition配置
		"""
		cnd = dictDat[ "conditions" ]
		if len( cnd ) <= 0:
			return
		value = eval( cnd )
		for k, c in m_map.iteritems():
			if value & k:
				instance = c()
				instance.init( dictDat )
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

