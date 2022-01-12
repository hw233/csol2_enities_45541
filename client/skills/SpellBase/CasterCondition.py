# -*- coding: gb18030 -*-
#
# $Id: CasterCondition.py,v 1.5 2008-08-13 02:24:25 kebiao Exp $

"""
һЩ��ʩ�����Ƿ���ʩ���Ķ��񼯺ϡ�
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
	������
	"""
	def __init__( self , conditionType ):
		"""
		virtual method.
		"""
		self.ctype = conditionType		#������,��¼��ʩ����������ʲô����

	def init( self, dict ):
		"""
		virtual method.
		spell��ĳ��condition(ReceiverCondition or CasterConditionBase)�����ļ� python dict
		"""
		pass

	def valid( self, entity ):
		"""
		virtual method.
		У��Ŀ���Ƿ����ѡ��Ҫ��

		@param entity: Entity
		@type  entity: Entity
		@return:       INT��see also csdefine.SKILL_*
		@rtype:        INT
		"""
		return csstatus.SKILL_UNKNOW

	def GetConditionType( self ):		#��ȡʩ������������
		"""
		�������������
		"""
		return self.ctype


class SpellAllow( CasterConditionBase ):
	"""
	����ʩ��(���²�����ʩ����ԭ��ܶ࣬�类��Ĭ�����Ե�)
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
	����ʩչ��ͨ������
	"""
	def valid( self, entity ):
		"""
		"""
		if not entity.actionSign( csdefine.ACTION_FORBID_ATTACK ):
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_CANT_CAST

class BuffHave( CasterConditionBase ):
	"""
	���ϱ������ָ�����͵�buff��ֻ������ʩ���������жϡ�
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
	���ϲ�����ָ�����͵�buff��ֻ������ʩ���������жϡ�
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
	���봦��ս��״̬
	"""
	def valid( self, entity ):
		"""
		"""
		if entity.getState() == csdefine.ENTITY_STATE_FIGHT:
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_NOT_IN_FIGHT

class NotInFightState( CasterConditionBase ):
	"""
	���봦�ڷ�ս��״̬
	"""
	def valid( self, entity ):
		"""
		"""
		if entity.getState() != csdefine.ENTITY_STATE_FIGHT:
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_IN_FIGHT

class IsDead( CasterConditionBase ):
	"""
	���봦������״̬
	"""
	def valid( self, entity ):
		"""
		"""
		if entity.isDead():
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_IN_LIVE

class IsLive( CasterConditionBase ):
	"""
	���봦�ڷ�����״̬
	"""
	def valid( self, entity ):
		"""
		"""
		if not entity.isDead():
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_IN_DEAD

class EmptyHand( CasterConditionBase ):
	"""
	���봦�ڿ���
	"""
	def valid( self, entity ):
		"""
		"""
		if entity.isEmptyHand():
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_EMPTY_HAND_REQUIRE

class PrimaryHandEmpty( CasterConditionBase ):
	"""
	��(��������)�ֱ���Ϊ��
	"""
	def valid( self, entity ):
		"""
		"""
		if entity.primaryHandEmpty():
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_EMPTY_HAND_REQUIRE

class WeaponConfine( CasterConditionBase ):
	"""
	���ϱ���Ҫ������
	"""
	def valid( self, entity ):
		"""
		"""
		#weapon = entity.getItem_( ItemTypeEnum.CWT_RIGHTHAND )		#���ֻ���ж��Ƿ�װ���������������ж������;ö��Ƿ�Ϊ��
		if not entity.primaryHandEmpty():
			return csstatus.SKILL_GO_ON
		return csstatus.SKILL_WEAPON_EQUIP_REQUIRE

class PossessItem( CasterConditionBase ):
	"""
	���ϱ������ĳ����Ʒ
	"""
	def init( self, dict ):
		"""
		"""
		self._itemTypes = []
		for param in dict["ExtraValue"].split( ";" ):
			val = param.split("'")
			if len(val) < 2 or val[0] != "ItemType":continue
			self._itemTypes.append( ( val[1], int(val[2]) ) )#��ƷID������

	def valid( self, entity ):
		"""
		"""
		for itemID, amount in self._itemTypes:
			if not entity.checkItemFromNKCK_( itemID, amount ) :
				return csstatus.SKILL_MISSING_ITEM
		return csstatus.SKILL_GO_ON


class WeaponEquip( CasterConditionBase ):
	"""
	����װ����ĳ����
	"""
	def init( self, dict ):
		"""
		"""
		self._itemTypes = []
		for param in dict["ExtraValue"].split( ";" ):
			val = param.split("'")
			if len(val) < 1 or val[0] != "EquipWeapon":continue
			self._itemTypes.append( eval( "ItemTypeEnum." + val[1] ) )#��������
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
	����װ������
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
	��PK״̬
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
		��ָ���ĵ���ʹ��
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
					self._spaces.append( eval( "csdefine." +  param ) ) #��ͼ����

		def valid( self, entity ):
			if entity.getCurrentSpaceType() not in self._spaces:	#�����ҵ�ǰ���ĵ�ͼ���Ͳ��������������
				return	 csstatus.SKILL_CAST_IS_NOTIN_APPOINTSPACE
			return csstatus.SKILL_GO_ON

class InAppointSpaceNotUse( InAppointSpace ):
		"""
		ָ����ͼ����ʹ��
		"""
		def valid( self, entity ):
			if InAppointSpace.valid( self, entity ) == csstatus.SKILL_GO_ON:
				return csstatus.SKILL_CAST_IS_NOTIN_APPOINTSPACE
			return csstatus.SKILL_GO_ON

class IsWieldTalish( CasterConditionBase ):
	"""
	�Ƿ�װ������
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
	�Ƿ�Ϊ�ж�״̬
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
	��ĳ����̬
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
	�ռ��Ƿ�֧�ַ��� by mushuang
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
	�Ƿ��ڷ���״̬ by mushuang
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
	�Ƿ��ڵ���״̬ by mushuang
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
	�ж�ʩ�����Ƿ��������
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
			csdefine.CASTER_CONDITION_IN_APPOINT_SPACE			: InAppointSpace,		#��ָ���ĵ�ͼ����ʹ��
			csdefine.CASTER_CONDITION_IN_APPOINT_SPACE_NOT_USE	: InAppointSpaceNotUse,	#��ָ���ĵ�ͼ����ʹ��
			csdefine.CASTER_CONDITION_WEAPON_TALISMAN			: IsWieldTalish,		# װ������
			csdefine.CASTER_CONDITION_NOT_ENEMY_STATE			: IsNotEnemyState,		# �Ƿ�Ϊ�ж�״̬
			csdefine.CASTER_CONDITION_POSTURE					: IsPosture,			# ����ĳ����̬
			csdefine.CASTER_CONDITION_SPACE_SUPPORT_FLY			: IsSpaceSupportFly,	# �ռ�֧�ַ���
			csdefine.CASTER_CONDITION_IS_FLYING_STATUS			: IsFlyingState,		# �����ڷ���״̬
			csdefine.CASTER_CONDITION_IS_GROUND_STATUS			: IsGroundState,		# �����ڵ���״̬
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
		spell��ĳ��condition�����ļ�dict
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
		�ж�Ŀ���Ƿ���Ч

		@return: INT��see also csdefine.SKILL_*
		@rtype:  INT
		"""
		for cnd in self._conditions:
			state = cnd.valid( caster )
			if state != csstatus.SKILL_GO_ON:
				return state
		return csstatus.SKILL_GO_ON

	def getNeedWeaponDescription( self , entity ):
		"""
		��ȡʩ�Ÿü�����Ҫ������������(Զ�̻��߽��̻��߶ܻ��� Զ��/��������)
		@RETURN		TUPLE: (���ܶ���������������,�Ƿ���������)
		"""
		conditions = self._conditions
		if not conditions:		#û������
			return None
		weapondes = ""			#���������
		bequip    = 1			#�Ƿ���������
		weapon = entity.getItem_( ItemTypeEnum.CWT_RIGHTHAND )
		for condition in conditions:
			if condition.GetConditionType() == csdefine.CASTER_CONDITION_WEAPON_CONFINE:	#����װ�������� ����ʲô
				weapondes += lbs_CasterCondition[10]
				if not weapon:
					bequip = 0
			if condition.GetConditionType() == csdefine.CASTER_CONDITION_WEAPON_EQUIP:	#����װ����ĳ����
				for weaponType in condition._itemTypes:
					weaponName = ItemTypeEnum.WEAPONNAME_DIC.get( weaponType )
					if weaponName:
						if weapondes:
							weapondes = weapondes + "," + weaponName
						else:
							weapondes += weaponName
					if not weapon or not weapon.query( "type" ) in condition._itemTypes:
						bequip = 0
			if condition.GetConditionType() == csdefine.CASTER_CONDITION_SHIELD_EQUIP:		#����װ����
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
		��ȡʩ�Ÿü�����Ҫ��Щ��Ʒ������
		@RETURN		LIST: [ (�������Ʒ���� , �Ƿ�����) ]
		"""
		conditions = self._conditions
		if not conditions:		#û������
			return []
		Itemdes = []			#�������Ʒ
		for condition in conditions:
			if condition.GetConditionType() == csdefine.CASTER_CONDITION_POSSESS_ITEM:	#������Ҫĳ����Ʒ
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
		��ȡʩ�Ÿ�ħ����Ҫ�ڵĵ�ͼ
		@RETURN		TUPLE: ( ��Ҫ�ĵ�ͼ , �Ƿ����� )
		"""
		conditions = self._conditions
		if not conditions:		#û������
			return None
		spaces	= ""		#����ĵ�ͼ
		bein	= 1			#�Ƿ�����
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
# �����������޸ĵ�datatool��س�ʼ����Ҫ�޸�
#
# Revision 1.3  2008/05/30 03:06:16  yangkai
# װ������������Ĳ����޸�
#
# Revision 1.2  2008/05/27 09:04:29  kebiao
# ����װ������
#
# Revision 1.1  2008/01/05 03:47:16  kebiao
# �������ܽṹ��Ŀ¼�ṹ
#
#