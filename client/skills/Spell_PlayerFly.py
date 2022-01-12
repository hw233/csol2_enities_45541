# -*- coding: gb18030 -*-

"""
���Ǵ��͹�����ʹ�ü��ܿͻ��˽ű�
"""

import BigWorld
import csdefine
import Define
from gbref import rds
from SpellBase import *
import csconst
import random
#���贫�Ͷ���ƥ��
ACTION_MAP_NO_WEAPON = {1:"ride_stand", 2:"crossleg_stand", 3:"float_stand"}
ACTION_MAP_WEAPON = {1:{1:"ride_run_weapon", 2:"ride_run_weapon_chang", 3:"ride_run_weapon_chang_fu",4:"ride_run_weapon_dan",5:"ride_run_weapon_shuang",6:"ride_run_weapon"},
	2:{1:"crossleg_run_weapon", 2:"crossleg_run_weapon_chang", 3:"crossleg_run_weapon_chang_fu",4:"crossleg_run_weapon_dan",5:"crossleg_run_weapon_shuang",6:"crossleg_run_weapon"},
		3:{1:"float_run_weapon", 2:"float_run_weapon_chang", 3:"float_run_weapon_chang_fu",4:"float_run_weapon_dan",5:"float_run_weapon_shuang",6:"float_run_weapon"}
		}

class Spell_PlayerFly( Spell ):
	
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		
	def cast( self, caster, targetObject ):
		"""
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		caster.hasCast = True
		skillID = self.getID()

		# �Զ������ԣ���ֻ�Ქ��һ��
		self.playCastAction( caster, skillID )
		if hasattr( caster,"isLoadModel" ) and caster.isLoadModel:
			caster.delayCastEffects.append( Functor( rds.skillEffect.playCastEffects, caster, targetObject, skillID ) )
		else:
			rds.skillEffect.playCastEffects( caster, targetObject, skillID )

		# ����������ʾ
		speller = caster  #���¸�ֵ����ֹ������û���
		if hasattr( speller, 'getOwner' ):
			speller = speller.getOwner()

		player = BigWorld.player()
		if player is None: return
		if speller is None: return

		if player.position.distTo( speller.position ) > 20: return
		if hasattr( caster, "className" ):
			sk_id = str( skillID )[:-3]
			if not sk_id: return		# ���Ϊ�գ�ֱ�ӷ���
			orgSkillID = int( sk_id )	# ֧�����ñ�ɱ�ȼ�NPC������д
			skillIDs = npcSkillName.get( caster.className, [] )
			if orgSkillID in skillIDs or skillID in skillIDs:
				caster.showSkillName( skillID )
				return
		if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or caster.isEntityType( csdefine.ENTITY_TYPE_PET ):
			caster.showSkillName( skillID )	
		
	def playCastAction( self, speller, skillID ):
		"""
		@type	speller 	: entity
		@param	speller 	: ����ʩ����
		@type	skillID 	: skillID
		@param	skillID 	: ����ID
		����ʩչ����
		"""
		if speller is None: return
		if not speller.inWorld: return

		type = speller.getWeaponType()
		vehicleType = 0
		castsNames = rds.spellEffect.getCastAction( skillID, type, vehicleType )
		if len( castsNames ) == 0: return False
			
		if skillID in csconst.SKILL_ID_PHYSICS_LIST:
			if speller.nAttackOrder >= len( castsNames ):
				speller.nAttackOrder = 0
			castsName = castsNames[speller.nAttackOrder]
			speller.nAttackOrder += 1
		else:
			castsName = random.choice( castsNames )
		#�������������������Ӧ���Ѿ�Ԥ�Ȳ�����
		#�ظ�����һ������ǰһ������������ɲ�����
		if hasattr( speller, "stopMove"): speller.stopMove()
		if type == 0:
			addAction = ACTION_MAP_NO_WEAPON[ speller.vehicleType ]
		else:
			addAction = ACTION_MAP_WEAPON[ speller.vehicleType ][type]
		rds.actionMgr.playActions( speller.getModel(), [ castsName, addAction ] )
		return True	