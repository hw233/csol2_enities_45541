# -*- coding: gb18030 -*-
#
# $Id: Pet.py,v 1.56 2008-08-29 02:38:42 huangyongwei Exp $

"""
This module implements the pet entity.

2007/07/01: writen by huangyongwei
2007/10/24 : according to new version document, it is rewriten by huangyongwei
"""

import random
import GUI
import BigWorld
import Pixie
import csdefine
import csconst
import csstatus
import csstatus_msgs as StatusMsgs
import Define
import EntityCache
import event.EventCenter as ECenter
from gbref import rds
from UnitSelect import UnitSelect
from PetFormulas import Formulas
from NPCObject import NPCObject
from Monster import Monster
from interface.CombatUnit import CombatUnit
from interface.PetAI import PetAI
from ItemsFactory import BuffItem
from VehicleHelper import isFlying
g_entityCache = EntityCache.EntityCache.instance()
import time
import Const
from config.client.labels import ChatFacade as lbs_ChatFacade
from Function import Functor
# --------------------------------------------------------------------
# implement pet class
# --------------------------------------------------------------------
class Pet( NPCObject, CombatUnit ) :
	def __init__( self ) :
		NPCObject.__init__( self )
		CombatUnit.__init__( self )

		self.am = None
		self.espialTime = 0.0
		self.starIndex = 0
		self.randomActions = []				# ��¼ Monster ������������ϣ������Ի�����ģ�͵ĸı���ı�
		
		self.visibleRules = [ csdefine.VISIBLE_RULE_BY_PLANEID,csdefine.VISIBLE_RULE_BY_TEL_AND_TEST,\
		 csdefine.VISIBLE_RULE_BY_PROWL_3,csdefine.VISIBLE_RULE_BY_SETTING_2,csdefine.VISIBLE_RULE_BY_SHOW_SELF]

		if self.isOwn() :					# ��������� BigWorld.player �ĳ���
			self.__class__ = OwnPet			# �򽫳����ཻ�� OwnPet
			OwnPet.__init__( self )			# ��������ʼ������

		# Ĭ����������Ϊ����
		self.weaponType = Define.WEAPON_TYPE_NONE
		# Ĭ�Ϸ�������Ϊ�޷���
		self.armorType = Define.ARMOR_TYPE_EMPTY
		self.isShowSelf = True      #�Ƿ���ʾ�Լ�,���ȼ���ߵ��ж� ���ڲ�������Ч��������ģ��
		# own��������Ҫ��combatunit ����
		self.strength = 0
		self.dexterity = 0
		self.intellect = 0
		self.corporeity = 0

		self.range = 0.0					# ��ͨ����������
		self.hit_speed = 0.0
		self.damage_min = 0
		self.damage_max = 0
		self.magic_damage = 0
		self.armor = 0
		self.magic_armor = 0
		self.dodge_probability = 0
		self.resist_hit_probability = 0
		self.double_hit_probability = 0
		self.magic_double_hit_probability = 0
		self.resist_giddy_probability = 0
		self.resist_fix_probability = 0
		self.resist_chenmo_probability = 0
		self.resist_sleep_probability = 0

		self.phyManaVal_value = 0
		self.phyManaVal_percent = 0
		self.magicManaVal_value = 0
		self.magicManaVal_percent = 0
		self.phySkillRangeVal_value = 0
		self.phySkillRangeVal_percent = 0
		self.magicSkillRangeVal_value = 0
		self.magicSkillRangeVal_percent = 0
		

	def filterCreator( self ):
		"""
		template method.
		����entity��filterģ��
		"""
		return BigWorld.AvatarFilter()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache�������
		"""
		if not self.inWorld:
			return
		NPCObject.onCacheCompleted( self )
		CombatUnit.onCacheCompleted( self )
		self.updateVisibility()
		BigWorld.addShadowEntity( self )

	def leaveWorld( self ) :
		NPCObject.leaveWorld( self )
		CombatUnit.leaveWorld( self )
		if self.model is not None:
			self.model.visible = False
		BigWorld.delShadowEntity( self )

	def onTargetFocus( self ):
		"""
		����Ƶ� pet ����ʱ������
		"""
		player = BigWorld.player()
		if self.model.visible:
			ECenter.fireEvent( "EVT_ON_SHOW_RESUME", self )
			NPCObject.onTargetFocus( self )
		if player.queryRelation( self.getOwner() ) == csdefine.RELATION_ANTAGONIZE :
			rds.ccursor.set( "attack" )
		else:
			rds.ccursor.set( "normal" )
		#if not player.canPk( self.getOwner() ) or not player.currAreaCanPk():
		#	rds.ccursor.set( "normal" )
		#else:
		#	rds.ccursor.set( "attack" )

	def onTargetBlur( self ) :
		"""
		������뿪 pet ����ʱ������
		"""
		rds.ccursor.set( "normal" )
		ECenter.fireEvent( "EVT_ON_HIDE_RESUME" )
		NPCObject.onTargetBlur( self )

	# -------------------------------------------------
	def getName( self ) :
		"""
		��ȡ��������
		"""
		return self.name and self.name or self.uname

	def getLevel( self ):
		"""
		����
		"""
		return self.level

	def getPType( self ) :
		"""
		��ȡ�������
		"""
		return self.species & csdefine.PET_TYPE_MASK

	def getHeadTexture( self ) :
		"""
		get pet's header
		"""
		modelNum = self.modelNumber

		# �����������
		if Formulas.getHierarchy( self.species ) == csdefine.PET_HIERARCHY_INFANCY2:
			modelNum += Const.PET_ATTACH_MODELNUM

		return rds.npcModel.getHeadTexture( modelNum )


	# ---------------------------------------
	def isOwn( self ) :
		"""
		�жϳ����Ƿ��� BigWorld.player �ĳ���
		"""
		return self.ownerID == BigWorld.player().id

	def getOwner( self ) :
		"""
		��ȡ�������������
		"""
		return BigWorld.entities.get( self.ownerID, None )

	# -------------------------------------------------		
	def onSnakeStateChange( self, state = True ):
		"""
		Define Method
		Ŀ��Ǳ�лص���ȷ��������Ч����ͻ��˱���һ��
		"""
		owner = self.getOwner()
		if owner and hasattr( owner, "isSnake" ):
			self.isSnake = owner.isSnake
		if self.effect_state & csdefine.EFFECT_STATE_PROWL == 0:
			self.isSnake = False
		if self.isSnake:
			type = Define.MODEL_VISIBLE_TYPE_FALSE
		else:
			type = Define.MODEL_VISIBLE_TYPE_SNEAK
		self.setModelVisible( type )


	def resetSnake( self ):
		"""
		�����Ǳ�гɹ�������Ҿ���
		"""
		#���û����Ǳ��״̬
		if self.effect_state & csdefine.EFFECT_STATE_PROWL == 0:
			self.isSnake = False
			return
		owner = self.getOwner()
		if owner and hasattr( owner, "isSnake" ):
			self.isSnake = owner.isSnake
			return
		self.isSnake = True

	def setModelVisible( self, visibleType ):
		"""
		����ģ����ʾ��ʽ
		�μ� Define.MODEL_VISIBLE_TYPE_*
		"""
		if not self.inWorld: return
		if self.model is None: return

		if visibleType == Define.MODEL_VISIBLE_TYPE_FALSE:
			self.setVisibility( False )
			rds.effectMgr.setModelAlpha( self.model, 0.0 )
			self.model.visibleAttachments = False
		elif visibleType == Define.MODEL_VISIBLE_TYPE_TRUE:
			self.setVisibility( True )
			rds.effectMgr.setModelAlpha( self.model, 1.0, 1.0 )
			self.model.visibleAttachments = False
		elif visibleType == Define.MODEL_VISIBLE_TYPE_FBUTBILL:
			self.setVisibility( False )
			rds.effectMgr.setModelAlpha( self.model, 0.0 )
			self.model.visibleAttachments = True
		elif visibleType == Define.MODEL_VISIBLE_TYPE_SNEAK:
			self.setVisibility( True )
			rds.effectMgr.setModelAlpha( self.model, 0.5, 1.0 )
			self.model.visibleAttachments = False

	def visibilitySettingChanged( self, key, value ) :
		"""
		�û�ͨ���������øı�ģ�Ϳɼ���
		"""
		BigWorld.player().isRolesVisible = True
		self.updateVisibility()

	def setIsShowSelf( self, isShow ):
		"""
		�Ƿ���ʾģ��
		"""
		self.isShowSelf = isShow
		self.updateVisibility()

	# ----------------------------------------------------------------
	# attributes update methods
	# ----------------------------------------------------------------
	def set_name( self, old ) :
		"""
		�������Ƹı�ʱ������
		"""
		ECenter.fireEvent( "EVT_ON_ENTITY_NAME_CHANGED", self.id, self.getName() )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onAddSkill( self, skillID ) :
		"""
		���һ������
		�÷���û�ã���Ϊ���＼�ܷŵ���������У�����д������������Ϊ skillBox ���� define
		"""
		pass

	def onRemoveSkill( self, skillID ) :
		"""
		ɾ��һ������
		�÷���û�ã���Ϊ���＼�ܷŵ���������У�����д������������Ϊ skillBox ���� define
		"""
		pass

	def onUpdateSkill( self, old, new ) :
		"""
		���¼���
		�÷���û�ã���Ϊ���＼�ܷŵ���������У�����д������������Ϊ skillBox ���� define
		"""
		pass

	def requeryPetDatas( self ):
		"""
		���������������
		"""
		distance = BigWorld.player().position.flatDistTo( self.position ) #���������Ŀ��ľ���
		if distance > 30.0: #������볬��30�� ��ʾ�����Զ ���ܲ鿴
			BigWorld.player().statusMessage( csstatus.ESPIAL_TARGET_TOOFAR )
			return
		if time.time() - self.espialTime < 5.0:
			BigWorld.player().statusMessage( csstatus.CHECK_TOO_HOURLY )
			return
		self.cell.requeryPetDatas()
		self.espialTime = time.time()

	def onRecievePetData( self, petDatas ):
		"""
		define method
		���ղ�ѯ������Ϣ
		"""
		ECenter.fireEvent( "EVT_ON_RECEIVE_TARGET_PETDATAS", petDatas, self )

	# ----------------------------------------------------------------
	# template methods
	# ----------------------------------------------------------------
	def onModelChange( self, oldModel, newModel ):
		"""
		ģ�͸���֪ͨ
		"""
		NPCObject.onModelChange( self, oldModel, newModel )
		CombatUnit.onModelChange( self, oldModel, newModel )
		if newModel is None: return

		am = self.am
		if am.owner != None: am.owner.delMotor( am )
		newModel.motors = ( am, )

		# ��̬ģ�͵ķŴ�������� action match ֮����������ᱻ��ԭ
		newModel.scale = ( self.modelScale, self.modelScale, self.modelScale )

		# ��ȡ��ģ�͵��漴����
		self.getRandomActions()

		rds.areaEffectMgr.onModelChange( self )

	def createModel( self, event = Define.MODEL_LOAD_IN_WORLD_CHANGE ):
		"""
		template method.
		����ģ��
		�̳� NPCObject.createModel
		"""
		if self.am is None:
			self.am = BigWorld.ActionMatcher( self )
			# ģ�͵�RolePitchYaw��Entity����һ��
			self.am.turnModelToEntity = True
			self.am.footTwistSpeed = 0.0

			# ģ�͵�����������
			self.am.boredNotifier = self.onBored
			self.am.patience = random.random() * 6 + 6.0
			self.am.fuse = random.random() * 6 + 6.0
			self.am.matchCaps = [Define.CAPS_DEFAULT]

		modelNum = self.modelNumber
		if Formulas.getHierarchy( self.species ) == csdefine.PET_HIERARCHY_INFANCY2:
			modelNum += Const.PET_ATTACH_MODELNUM

		rds.npcModel.createDynamicModelBG( modelNum,  Functor( self.__onModelLoad, event ) )
	
	def __onModelLoad( self, event, model ):
		if not self.inWorld : return  # ����Ѳ�����Ұ�����
		if model is None:
			model = rds.npcModel.createDynamicModel( Const.PET_DEFAULT_MODEL )	# ʹ�ó����Ĭ��ģ��
		self.setModel( model, event )
		self.flushAttachments_()	# ˢ��ͷ������

	def getRandomActions( self ):
		"""
		get the random actions.
		because the random actions have unfixed amount
		so I get the actions from random1,random2....if unsuccessful and return
		��ȡ���������������������������̶���
		��ȡ���������random1��ʼ��random2,random3....��ȡʧ���򷵻�
		"""
		#the range(1,10) is  provisional, because I can't find more than 2 randomActions for a entity
		for index in range(1,10):
			actName = "random"+str( index )
			if self.model.hasAction( actName ):
				self.randomActions.append( actName )
			else:
				return

	def onBored( self, actionName ):
		"""
		�˻ص����ڲ����������
		The method callback when the same action last patience time.
		More information see the Client API ActionMatcher.boredNotifier
		"""
		if actionName != "stand": return
		self.playRandomAction()
		# ��һ��������ʼ����ʱ fuse ������Ϊ0
		# �����ƺ���bug����ʱ��û������ fuse ������ԣ���������������
		self.am.fuse = 0
		# ÿ֪ͨһ�� onBored  ������Զ��� patience ��Ϊһ����ֵ??
		# ֻ������ patience ֵ ���������Ĳ�ͣ���� onBored ����
		self.am.patience = random.random() * 6 + 6.0

	def playRandomAction( self ):
		"""
		play random Action
		"""
		#��ȡ�������������
		randomActionCount = len( self.randomActions )
		if randomActionCount == 0:
				return
		elif randomActionCount == 1:
			self.am.matchCaps = [ Define.CAPS_RANDOM, Define.CAPS_INDEX25 ]
		else:
			index = random.randint( 0, randomActionCount - 1 )
			caps = Define.CAPS_INDEX25 + index
			self.am.matchCaps = [Define.CAPS_RANDOM, caps]

		BigWorld.callback( 0.1, self.onOneShoot )

	def onOneShoot( self ):
		"""
		<oneShot>
		Setting this to TRUE means that the Action Matcher will not continue
		playing that action past one cycle of it, if it is no longer triggered,
		but a <cancel> section was keeping it active.
		"""
		# ����Ѳ�����Ұ�����
		if not self.inWorld: return
		if Define.CAPS_RANDOM in self.am.matchCaps:
			self.am.matchCaps = [Define.CAPS_DEFAULT]

	def getWeaponType( self ):
		"""
		��ȡ��������
		"""
		return self.weaponType

	def getArmorType( self ):
		"""
		��ȡ��������
		"""
		return self.armorType

	def onReceiveDamage( self, casterID, skill, damageType, damage ):
		"""
		�˺���ʾ
		@param   casterID: ʩ����ID
		@type    casterID: OBJECT_ID
		@param    skill  : ����ʵ��
		@param damageType: �˺����ͣ�see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: UINT8
		@param     damage: �˺���ֵ
		@type      damage: INT
		"""
		CombatUnit.onReceiveDamage( self, casterID, skill, damageType, damage )
		player = BigWorld.player()
		sk = skill
		petID = -1
		pet = player.pcg_getActPet()
		if pet:
			petID = pet.id
		# �Լ��������ʩ���߲���ʾ
		if casterID != player.id and casterID != petID:
			return

		# ���ܲ����˺�ʱ��ͷ��������Ϣ�ȴ���
		if damage > 0:
			if ( damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
				# �����˺�
				ECenter.fireEvent( "EVT_ON_SHOW_DOUBLE_DAMAGE_VALUE", self.id, str( damage ) )
			else:
				# ��ͨ�˺�
				ECenter.fireEvent( "EVT_ON_SHOW_DAMAGE_VALUE", self.id, str( damage ) )
		else:
			# Miss
			ECenter.fireEvent( "EVT_ON_SHOW_MISS_ATTACK", self.id )

		# ���ܲ����˺�ʱ��ϵͳ��Ϣ�ȴ���
		if casterID == player.id:					# �Լ���ʩ����
			if damage > 0:
				if ( damageType & csdefine.DAMAGE_TYPE_RESIST_HIT ) == csdefine.DAMAGE_TYPE_RESIST_HIT:
					# %s�м������%s���ܵ�%i����˺���
					player.statusMessage( csstatus.SKILL_SPELL_RESIST_HIT_FROM_SKILL, self.getName(), sk.getName(), damage )
				elif (damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
					# ���%s������%s���%i����˺���
					player.statusMessage( csstatus.SKILL_SPELL_DOUBLEDAMAGE_TO, sk.getName(), self.getName(), damage )
				else:
					if (damageType & csdefine.DAMAGE_TYPE_REBOUND ) == csdefine.DAMAGE_TYPE_REBOUND:
						if (damageType & csdefine.DAMAGE_TYPE_MAGIC ) == csdefine.DAMAGE_TYPE_MAGIC:
							# %s�ܵ��㷴����%i�㷨���˺���
							player.statusMessage( csstatus.SKILL_BUFF_REBOUND_MAGIC_TO, self.getName(), damage )
						else:
							# %s�ܵ��㷴����%i���˺���
							player.statusMessage( csstatus.SKILL_BUFF_REBOUND_PHY_TO, self.getName(), damage )
					else:
						# ���%s��%s�����%i���˺���
						player.statusMessage( csstatus.SKILL_SPELL_DAMAGE_TO, sk.getName(), self.getName(), damage )
			else:
				if (damageType & csdefine.DAMAGE_TYPE_DODGE ) == csdefine.DAMAGE_TYPE_DODGE:
					# %s���������%s��
					player.statusMessage( csstatus.SKILL_SPELL_DODGE_FROM_SKILL, self.getName(), sk.getName() )
		elif casterID == petID: 					# ������ʩ����
			if damage > 0:
				if (damageType & csdefine.DAMAGE_TYPE_RESIST_HIT ) == csdefine.DAMAGE_TYPE_RESIST_HIT:
					# %s�м�����ĳ����%s���ܵ�%i����˺���
					player.statusMessage( csstatus.SKILL_SPELL_PET_RESIST_HIT_FROM_SKILL, self.getName(), pet.getName(), sk.getName(), damage )
				elif (damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
					# �����%s������%s���%i����˺���
					player.statusMessage( csstatus.SKILL_SPELL_PET_DOUBLEDAMAGE_TO, pet.getName(), sk.getName(), self.getName(), damage )
				else:
					# �����%s��%s�����%i���˺���
					player.statusMessage( csstatus.SKILL_SPELL_PET_DAMAGE_TO, pet.getName(), sk.getName(), self.getName(), damage )
			else:
				if (damageType & csdefine.DAMAGE_TYPE_DODGE ) == csdefine.DAMAGE_TYPE_DODGE:
					# %s�����˳����%s��
					player.statusMessage( csstatus.SKILL_SPELL_PET_DODGE_TO, self.getName(), pet.getName(), sk.getName() )

	def canSelect( self ):
		"""
		�Ƿ�����ѡ��
		"""
		owner = BigWorld.entities.get( self.ownerID, None )
		if not owner:
			return False
		if owner.state == csdefine.ENTITY_STATE_PENDING:
			return False
		if owner.state == csdefine.ENTITY_STATE_QUIZ_GAME:
			return False
		return True

	def set_state( self, oldState = csdefine.ENTITY_STATE_FREE ):
		"""
		����״̬�ı�
		"""
		self.updateVisibility()

	def showSkillName( self, skillID ):
		"""
		��ʾ��������
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_SKILL_NAME", self.id, skillID )	#��ʾ�ͷż��ܵ�����

	def onSetJoyancy( self, val ):
		"""
		define method.
		��������������
		"""
		pass

	def onSetLife( self, val ):
		"""
		define method.
		��������������
		"""
		pass

	def onSetProcreated( self, val ):
		"""
		define method.
		��������������
		"""
		pass

	def onSetCharacter( self, val ):
		"""
		define method.
		��������������
		"""
		pass

	def onSetCalcaneus( self, val ):
		"""
		define method.
		��������������
		"""
		pass

	def onSetNimbus( self, val ):
		"""
		define method.
		��������������
		"""
		pass

	def onSetAbility( self, val ):
		"""
		define method.
		��������������
		"""
		pass

	def onSetEC_free( self, val ):
		"""
		define method.
		��������������
		"""
		pass

	def onSetEC_dexterity( self, val ):
		"""
		define method.
		��������������
		"""
		pass

	def onSetEC_intellect( self, val ):
		"""
		define method.
		��������������
		"""
		pass

	def onSetEC_strength( self, val ):
		"""
		define method.
		��������������
		"""
		pass

	def onSetEC_corporeity( self, val ):
		"""
		define method.
		��������������
		"""
		pass

	def onSetE_corporeity( self, val ):
		"""
		define method.
		��������������
		"""
		self.e_corporeity = val

	def onSetE_strength( self, val ):
		"""
		define method.
		��������������
		"""
		self.e_strength = val

	def onSetE_dexterity( self, val ):
		"""
		define method.
		��������������
		"""
		self.e_dexterity = val

	def onSetE_intellect( self, val ):
		"""
		define method.
		��������������
		"""
		self.e_intellect = val

	def onSetPhyManaVal_value( self, val ):
		"""
		define method.
		��������������
		"""
		self.phyManaVal_value = val

	def onSetPhyManaVal_percent( self, val ):
		"""
		define method.
		��������������
		"""
		self.phyManaVal_percent = val

	def onSetMagicManaVal_value( self, val ):
		"""
		define method.
		��������������
		"""
		self.magicManaVal_value = val

	def onSetMagicManaVal_percent( self, val ):
		"""
		define method.
		��������������
		"""
		self.magicManaVal_percent = val

	def onSetPhySkillRangeVal_value( self, val ):
		"""
		define method.
		��������������
		"""
		self.phySkillRangeVal_value = val

	def onSetPhySkillRangeVal_percent( self, val ):
		"""
		define method.
		��������������
		"""
		self.phySkillRangeVal_percent = val

	def onSetMagicSkillRangeVal_value( self, val ):
		"""
		define method.
		��������������
		"""
		self.magicSkillRangeVal_value = val

	def onSetMagicSkillRangeVal_percent( self, val ):
		"""
		define method.
		��������������
		"""
		self.magicSkillRangeVal_percent = val

	def onSetCorporeity( self, val ):
		"""
		define method.
		��������������
		"""
		pass

	def onSetStrength( self, val ):
		"""
		define method.
		��������������
		"""
		pass

	def onSetIntellect( self, val ):
		"""
		define method.
		��������������
		"""
		pass

	def onSetDexterity( self, val ):
		"""
		define method.
		��������������
		"""
		pass

	# -------------------------------------------------
	def onSetDamageMin( self, val ):
		"""
		define method.
		��С������
		"""
		self.damage_min = val

	def onSetDamageMax( self, val ):
		"""
		define method.
		���������
		"""
		self.damage_max = val

	def onSetMagicDamage( self, val ):
		"""
		define method.
		��������
		"""
		self.magic_damage = val

	def onSetArmor( self, val ):
		"""
		define method.
		�������
		"""
		self.armor = val

	def onSetMagicArmor( self, val ):
		"""
		define method.
		��������
		"""
		self.magic_armor = val

	def onSetDoubleHitProbability( self, val ):
		"""
		define method.
		��������
		"""
		self.double_hit_probability = val

	def onSetMagicDoubleHitProbability( self, val ):
		"""
		define method.
		����������
		"""
		self.magic_double_hit_probability = val

	def onSetDodgeProbability( self, val ):
		"""
		define method.
		����
		"""
		self.dodge_probability = val

	def onSetResistHitProbability( self, val ):
		"""
		define method.
		�м�
		"""
		self.resist_hit_probability = val

	# -------------------------------------------------
	def onSetResistGiddyProbability( self, val ) :
		"""
		define method.
		"""
		self.resist_giddy_probability = val

	def onSetResistFixProbability( self, val ) :
		"""
		define method.
		"""
		self.resist_fix_probability = val

	def onSetResistChenmoProbability( self, val ) :
		"""
		define method.
		"""
		self.resist_chenmo_probability = val

	def onSetResistSleepProbability( self, val ) :
		"""
		define method.
		"""
		self.resist_sleep_probability = val

	def onSetRange( self, val ):
		"""
		define method.
		������������ͨ����������
		"""
		self.range = val

	def onSetHit_speed( self, val ):
		"""
		define method.
		���������ù����ٶ�
		"""
		self.hit_speed = val

	def onSetKeepPosition( self, position ):
		"""
		<Defined method>
		����ͣ��λ��
		"""
		pass

	def onClientControlled( self, isControlled ):
		"""
		<Defined method>
		����ͣ��λ��
		"""
		pass

	def initCacheTasks( self ):
		"""
		��ʼ������������
		"""
		NPCObject.initCacheTasks( self )
		CombatUnit.initCacheTasks( self )

	def getRelationEntity( self ):
		"""
		��ȡ��ϵ�ж�����ʵentity
		"""
		owner = BigWorld.entities.get( self.ownerID, None )
		if not owner:
			return None
		else:
			return owner			

# --------------------------------------------------------------------
# implement my pet class
# --------------------------------------------------------------------
class OwnPet( Pet, PetAI ) :
	def __init__( self ) :
		PetAI.__init__( self )
		self.castingSpell = 0

		self.ec_corporeity = 0
		self.ec_strength = 0
		self.ec_dexterity = 0
		self.ec_intellect = 0

		self.e_corporeity = 0
		self.e_strength = 0
		self.e_dexterity = 0
		self.e_intellect = 0

		self.ec_free = 0

		self.ability = 0
		self.nimbus = 0
		self.calcaneus = 0
		self.character = 0
		self.procreated = False
		self.life = 0
		self.joyancy = 0
		
		self.visibleRules = [ csdefine.VISIBLE_RULE_BY_PLANEID, csdefine.VISIBLE_RULE_BY_SHOW_SELF, csdefine.VISIBLE_RULE_BY_PROWL_1]

	# ----------------------------------------------------------------
	# attributes update methods
	# ----------------------------------------------------------------
	def set_name( self, old ) :
		Pet.set_name( self, old )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "name" )
		ECenter.fireEvent( "EVT_ON_PET_NAME_CHANGE", self.databaseID, self.getName() )

	def set_species( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "species" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "nimbusMax" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "strengthRadix" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "intellectRadix" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "dexterityRadix" )
		if self.name.strip() == "" :
			self.set_name( "" )

	def set_level( self, old ) :
		CombatUnit.set_level( self, old )
		epitome = BigWorld.player().pcg_getPetEpitomes()[self.databaseID]
		epitome.onUpdateAttr( "level", self.level )
		# ������Ч
		rds.effectMgr.createParticleBG( self.model, Const.UPDATE_LEVEL_HP, Const.UPDATE_LEVEL_PATH, detachTime = 3.0, type = Define.TYPE_PARTICLE_PLAYER )
		rds.helper.courseHelper.petAction( "shengji" )		# ��������������ʾ

	def set_HP( self, old ) :
		CombatUnit.set_HP( self, old )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "HP" )
		ECenter.fireEvent( "EVT_ON_PET_HP_CHANGE", self.HP, self.HP_Max )
		margin = self.HP - old
		if margin > 0:
			ECenter.fireEvent( "EVT_ON_SHOW_HEALTH_VALUE", self.id, "+" + str( margin ) )
		elif margin < 0:
			ECenter.fireEvent( "EVT_ON_SHOW_DAMAGE_VALUE", self.id, str( abs( margin ) ) )

	def set_MP( self, old ) :
		CombatUnit.set_MP( self, old )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "MP" )
		ECenter.fireEvent( "EVT_ON_PET_MP_CHANGE", self.MP, self.MP_Max )
		margin = self.MP - old
		if margin > 0:
			ECenter.fireEvent( "EVT_ON_SHOW_MP_VALUE", self.id, "+" + str( margin ) )
		elif margin < 0:
			ECenter.fireEvent( "EVT_ON_SHOW_MP_VALUE", self.id, str( margin ) )

	def set_HP_Max( self, old ) :
		CombatUnit.set_HP_Max( self, old )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "HPMax" )
		ECenter.fireEvent( "EVT_ON_PET_MAX_HP_CHANGE", self.HP, self.HP_Max )
		margin = self.HP - old
		if margin > 0:
			ECenter.fireEvent( "EVT_ON_SHOW_HEALTH_VALUE", self.id, "+" + str( margin ) )
		elif margin < 0:
			ECenter.fireEvent( "EVT_ON_SHOW_DAMAGE_VALUE", self.id, str( abs( margin ) ) )

	def set_MP_Max( self, old ) :
		CombatUnit.set_MP_Max( self, old )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "MPMax" )
		ECenter.fireEvent( "EVT_ON_PET_MAX_MP_CHANGE", self.MP, self.MP_Max )
		margin = self.MP - old
		if margin > 0:
			ECenter.fireEvent( "EVT_ON_SHOW_MP_VALUE", self.id, "+" + str( margin ) )
		elif margin < 0:
			ECenter.fireEvent( "EVT_ON_SHOW_MP_VALUE", self.id, str( margin ) )

	def set_EXP( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "EXP" )


	def onSetCorporeity( self, val ):
		"""
		define method.
		��������������
		"""
		old = self.corporeity
		self.corporeity = val
		self.set_corporeity( old )

	def set_corporeity( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "corporeity" )

	def onSetStrength( self, val ):
		"""
		define method.
		��������������
		"""
		old = self.strength
		self.strength = val
		self.set_strength( old )

	def set_strength( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "strength" )

	def onSetIntellect( self, val ):
		"""
		define method.
		��������������
		"""
		old = self.intellect
		self.intellect = val
		self.set_intellect( old )

	def set_intellect( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "intellect" )

	def onSetDexterity( self, val ):
		"""
		define method.
		��������������
		"""
		old = self.dexterity
		self.dexterity = val
		self.set_dexterity( old )

	def set_dexterity( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "dexterity" )

	def onSetE_corporeity( self, val ):
		"""
		define method.
		��������������
		"""
		old = self.e_corporeity
		self.e_corporeity = val
		self.set_corporeity( old )

	def onSetE_strength( self, val ):
		"""
		define method.
		��������������
		"""
		old = self.e_strength
		self.e_strength = val
		self.set_strength( old )

	def onSetE_dexterity( self, val ):
		"""
		define method.
		��������������
		"""
		old = self.e_dexterity
		self.e_dexterity = val
		self.set_dexterity( old )

	def onSetE_intellect( self, val ):
		"""
		define method.
		��������������
		"""
		old = self.e_intellect
		self.e_intellect = val
		self.set_intellect( old )

	def onSetEC_corporeity( self, val ):
		"""
		define method.
		��������������
		"""
		old = self.ec_corporeity
		self.ec_corporeity = val
		self.set_ec_corporeity( old )

	def set_ec_corporeity( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "ec_corporeity" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "ecrm_corporeity" )

	def onSetEC_strength( self, val ):
		"""
		define method.
		��������������
		"""
		old = self.ec_strength
		self.ec_strength = val
		self.set_ec_strength( old )

	def set_ec_strength( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "ec_strength" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "ecrm_strength" )

	def onSetEC_intellect( self, val ):
		"""
		define method.
		��������������
		"""
		old = self.ec_intellect
		self.ec_intellect = val
		self.set_ec_intellect( old )

	def set_ec_intellect( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "ec_intellect" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "ecrm_intellect" )

	def onSetEC_dexterity( self, val ):
		"""
		define method.
		��������������
		"""
		old = self.ec_dexterity
		self.ec_dexterity = val
		self.set_ec_dexterity( old )

	def set_ec_dexterity( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "ec_dexterity" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "ecrm_dexterity" )

	def onSetEC_free( self, val ):
		"""
		define method.
		��������������
		"""
		old = self.ec_free
		self.ec_free = val
		self.set_ec_free( old )

	def set_ec_free( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "ec_free" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "ecrm_free" )

	def onSetAbility( self, val ):
		"""
		define method.
		��������������
		"""
		old = self.ability
		self.ability = val
		self.set_ability( old )

	def set_ability( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "ability" )

	def onSetNimbus( self, val ):
		"""
		define method.
		��������������
		"""
		old = self.nimbus
		self.nimbus = val
		self.set_nimbus( old )

	def set_nimbus( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "nimbus" )
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "calcaneusMax" )

	def onSetCalcaneus( self, val ):
		"""
		define method.
		��������������
		"""
		old = self.calcaneus
		self.calcaneus = val
		self.set_calcaneus( old )

	def set_calcaneus( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "calcaneus" )

	def onSetCharacter( self, val ):
		"""
		define method.
		��������������
		"""
		old = self.character
		self.character = val
		self.set_character( old )

	def set_character( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "character" )

	def onSetProcreated( self, val ):
		"""
		define method.
		��������������
		"""
		old = self.procreated
		self.procreated = val
		self.set_procreated( old )

	def set_procreated( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "procreated" )

	def onSetLife( self, val ):
		"""
		define method.
		��������������
		"""
		old = self.life
		self.life = val
		self.set_life( old )

	def set_life( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "life" )

	def onSetJoyancy( self, val ):
		"""
		define method.
		��������������
		"""
		old = self.joyancy
		self.joyancy = val
		self.set_joyancy( old )

	def set_joyancy( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "joyancy" )

	def set_targetID( self, old ):
		PetAI.onTargetChanged( self, old )
		if old != self.targetID:
			ECenter.fireEvent( "EVT_ON_PET_TARGET_CHANGED", self.targetID )
			if self.targetID != 0:
				target = BigWorld.entities.get( self.targetID, None )
				if target and not target.isCacheOver:
					g_entityCache.addUrgent( target )

	# -------------------------------------------------
	def onSetDamageMin( self, val ):
		"""
		define method.
		��С������
		"""
		self.damage_min = val
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "damage" )

	def onSetDamageMax( self, val ):
		"""
		define method.
		���������
		"""
		self.damage_max = val
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "damage" )

	def onSetMagicDamage( self, val ):
		"""
		define method.
		��������
		"""
		self.magic_damage = val
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "magic_damage" )

	def onSetArmor( self, val ):
		"""
		define method.
		�������
		"""
		self.armor = val
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "armor" )

	def onSetMagicArmor( self, val ):
		"""
		define method.
		��������
		"""
		self.magic_armor = val
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "magic_armor" )

	def onSetDoubleHitProbability( self, val ):
		"""
		define method.
		��������
		"""
		self.double_hit_probability = val
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "double_hit_probability" )

	def onSetMagicDoubleHitProbability( self, val ):
		"""
		define method.
		����������
		"""
		self.magic_double_hit_probability = val
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "magic_double_hit_probability" )

	def onSetDodgeProbability( self, val ):
		"""
		define method.
		����
		"""
		self.dodge_probability = val
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "dodge_probability" )

	def onSetResistHitProbability( self, val ):
		"""
		define method.
		�м�
		"""
		self.resist_hit_probability = val
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "resist_hit_probability" )

	# -------------------------------------------------
	def onSetResistGiddyProbability( self, val ) :
		"""
		define method.
		"""
		self.resist_giddy_probability = val
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "resistGiddyProbability" )

	def onSetResistFixProbability( self, val ) :
		"""
		define method.
		"""
		self.resist_fix_probability = val
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "resistFixProbability" )

	def onSetResistChenmoProbability( self, val ) :
		"""
		define method.
		"""
		self.resist_chenmo_probability = val
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "resistChenmoProbability" )

	def onSetResistSleepProbability( self, val ) :
		"""
		define method.
		"""
		self.resist_sleep_probability = val
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "resistSleepProbability" )

	def onSetRange( self, val ):
		"""
		define method.
		������������ͨ����������
		"""
		self.range = val

	def onSetHit_speed( self, val ):
		"""
		define method.
		���������ù����ٶ�
		"""
		self.hit_speed = val

	# -------------------------------------------------
	def set_actionMode( self, old ) :
		PetAI.onSetActionMode(self, self.actionMode)
		ECenter.fireEvent( "EVT_ON_PET_ACTION_CHANGED", self.actionMode )

	def set_tussleMode( self, old ) :
		PetAI.onSetTussleMode(self, self.tussleMode)
		ECenter.fireEvent( "EVT_ON_PET_TUSSLE_CHANGED", self.tussleMode )

	def set_gender( self, old ) :
		ECenter.fireEvent( "EVT_ON_PET_ATTR_CHANGED", self.databaseID, "gender" )

	def set_actWord( self, old = 0):
		"""
		�ӷ������յ��������Ƹı�֪ͨ
		"""
		CombatUnit.set_actWord(self, old)
		PetAI.onActWordChanged(self, old)

	def onSetKeepPosition( self, position ):
		"""
		<Defined method>
		����ͣ��λ��
		"""
		PetAI.onSetKeepPosition(self, position)

	def onClientControlled( self, isControlled ):
		"""
		<Defined method>
		����ͣ��λ��
		"""
		PetAI.onClientControlled(self, isControlled)

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onReceiveDamage( self, casterID, skill, damageType, damage ):
		"""
		�˺���ʾ
		@param   casterID: ʩ����ID
		@type    casterID: OBJECT_ID
		@param    skill  : ����ʵ��
		@param damageType: �˺����ͣ�see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: UINT8
		@param     damage: �˺���ֵ
		@type      damage: INT
		"""
		self.onDamageModelColor( damageType, damage )
		player = BigWorld.player()
		sk = skill

		# ���ܲ����˺�ʱ��ϵͳ��Ϣ�ȴ���
		if damage > 0:
			if casterID > 0 and BigWorld.entities.has_key( casterID ):
				caster = BigWorld.entities[casterID]
				casterName = caster.getName()
				if player.onFengQi and caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
					casterName = lbs_ChatFacade.masked
				if (damageType & csdefine.DAMAGE_TYPE_RESIST_HIT ) == csdefine.DAMAGE_TYPE_RESIST_HIT:
					# �����м���%s��%s���ܵ�%i����˺���
					player.statusMessage( csstatus.SKILL_SPELL_PET_RESIST_HIT_TO, self.getName(), casterName, sk.getName(), damage )
				elif (damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
					# %s��%s��������ĳ������%i����˺���
					player.statusMessage( csstatus.SKILL_SPELL_PET_DOUBLEDAMAGE_FROM_SKILL, casterName, sk.getName(), self.getName(), damage )
				else:# %s��%s����ĳ��������%i���˺���
					player.statusMessage( csstatus.SKILL_SPELL_PET_DAMAGE_FROM_SKILL, casterName, sk.getName(), self.getName(), damage )
			else:
				if (damageType & csdefine.DAMAGE_TYPE_RESIST_HIT ) == csdefine.DAMAGE_TYPE_RESIST_HIT:
					# �����м���%s���ܵ�%i����˺���
					player.statusMessage( csstatus.SKILL_SPELL_PET_RESIST_HIT_FROM, self.getName(), sk.getName(), damage )
				elif (damageType & csdefine.DAMAGE_TYPE_FLAG_DOUBLE ) == csdefine.DAMAGE_TYPE_FLAG_DOUBLE:
					# %s��������ĳ������%i����˺���
					player.statusMessage( csstatus.SKILL_SPELL_PET_DOUBLEDAMAGE_FROM, sk.getName(), self.getName(), damage )
				else:
					# %s����ĳ��������%i���˺���
					player.statusMessage( csstatus.SKILL_SPELL_PET_DAMAGE_FROM, sk.getName(), self.getName(), damage )
		else:
			if casterID > 0 and BigWorld.entities.has_key( casterID ):
				caster = BigWorld.entities[casterID]
				casterName = caster.getName()
				if player.onFengQi and caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
					casterName = lbs_ChatFacade.masked
				if (damageType & csdefine.DAMAGE_TYPE_DODGE ) == csdefine.DAMAGE_TYPE_DODGE:
					# %s������%s��%s
					player.statusMessage( csstatus.SKILL_SPELL_PET_DODGE_FROM_SKILL, self.getName(), casterName, sk.getName() )
		self.getOwner().onPetReceiveDamage( casterID )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onCacheCompleted( self ):
		"""
		�������
		"""
		if not self.inWorld:
			return
		Pet.onCacheCompleted( self )
		self.cell.requestSkillBox()										# �����ͼ����б�
		self.cell.requestQBItems()										# �����ͼ��ܿ����
		self.set_actionMode( self.actionMode )							# Ĭ����Ϊģʽ
		self.set_tussleMode( self.tussleMode )							# Ĭ��ս��ģʽ
		BigWorld.player().pcg_onActPetEnterWorld( self )
		ECenter.fireEvent( "EVT_ON_PET_ENTER_WORKLD", self.databaseID )

	def leaveWorld( self ) :
		Pet.leaveWorld( self )
		PetAI.leaveWorld(self)
		if self.actionMode == csdefine.PET_ACTION_MODE_KEEPING:
			return
		ECenter.fireEvent( "EVT_ON_PET_LEAVE_WORLD", self.databaseID )

	def statusMessage( self, status, *args ) :
		"""
		���״̬��Ϣ
		"""
		BigWorld.player().statusMessage( status, *args )

	def onTeleportReady( self ) :
		"""
		������ת��Ϻ󱻵���
		"""
		self.flushAttachments_()

	# -------------------------------------------------
	def getCooldown( self, typeID ):
		"""
		��ȡ��ȴʱ��
		"""
		return BigWorld.player().pcg_getPetCooldown( typeID )

	def queryRelation( self, entity ) :
		"""
		��ȡ������ָ�� entity �Ĺ�ϵ
		"""
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		owner = self.getOwner()
		if owner is None :
			return csdefine.RELATION_NONE
		return owner.queryRelation( entity )

	# -------------------------------------------------
	def setActionMode( self, mode ) :
		"""
		������Ϊģʽ
		"""
		PetAI.setActionMode(self, mode)
		self.cell.setActionMode( mode )

	def setTussleMode( self, tussle ) :
		"""
		����ս��ģʽ
		"""
		self.cell.setTussleMode( tussle )

	# -------------------------------------------------
	def isInSpelling( self ):
		"""
		�ж��Ƿ�����ʩ��
		"""
		return self.castingSpell != 0

	def intonate( self, skillID, intonateTime, targetObject ):
		"""
		Define method.��������
		@type 				skillID : INT
		"""
		if not self.isForceChasing():					# �����������ǿ��׷�٣��Ž�����������ʩչ���ܵȶ�������PetAI
			self.castingSpell = skillID
			Pet.intonate( self, skillID, intonateTime, targetObject )

	def castSpell( self, skillID, targetObject ):
		"""
		��ʽʩ�ŷ�����������ʩ��������
		@type			skillID		 : INT
		@param			targetObject : ʩչ����
		@type			targetObject : һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		self.castingSpell = 0
		if not self.isForceChasing():					# �����������ǿ��׷�٣��Ž�����������ʩչ���ܵȶ�������PetAI
			Pet.castSpell( self, skillID, targetObject )

	def intonating( self ):
		"""
		�Ƿ�������״̬
		"""
		return False		#�㶨����fase ����������

	# -------------------------------------------------

	def enterWorld( self ) :
		"""
		it will be called, when character enter world
		"""
		#  ��ʼ��ģ�����
		PetAI.enterWorld(self)
		self.createModel( Define.MODEL_LOAD_ENTER_WORLD )
		self.setVisibility( False )
		self.initCacheTasks()
		g_entityCache.addUrgent( self )

	def initCacheTasks( self ):
		"""
		��ʼ������������
		"""
		Pet.initCacheTasks( self )
		self.addCacheTask( csdefine.ENTITY_CACHE_TASK_TYPE_PET0 )
		
	def queryCombatRelation( self, entity ):
		owner = BigWorld.entities.get( self.ownerID, None )
		if not owner:
			return csdefine.RELATION_NONE
		else:
			return owner.queryCombatRelation( entity )			
			