# -*- coding: gb18030 -*-
#
# $Id: Pet.py,v 1.86 2008-09-04 07:44:14 kebiao Exp $

"""
This module implements the pet entity.

2007/07/16 : wirten by huangyongwei
2007/10/24 : base on new version documents, it is rewirten by huangyongwei
"""

import items
import time
import BigWorld
import csdefine
import csconst
import csstatus
import Const
import ECBExtend
import Language
import ShareTexts
from bwdebug import *
from PetFormulas import formulas
from LevelEXP import PetLevelEXP
from NPCObject import NPCObject
from interface.PetAI import PetAI
from interface.SkillBox import SkillBox
from interface.CombatUnit import CombatUnit
from interface.CombatUnit import calcProperty
from Love3 import g_skillTeachDatas
from Love3 import g_skills
from Love3 import g_equipEffect
from ObjectScripts.GameObjectFactory import g_objFactory

# --------------------------------------------------------------------
# ����������ɫ��װ
# --------------------------------------------------------------------
class _PetOwner( object ) :
	__slots__ = ( "etype", "entity" )
	def __init__( self, mbBase ) :
		entity = BigWorld.entities.get( mbBase.id )
		if entity is None :
			self.etype = "MAILBOX"
			self.entity = mbBase.cell
		elif entity.isReal() :
			self.etype = "REAL"
			self.entity = entity
		else :
			self.etype = "GHOST"
			self.entity = entity


# --------------------------------------------------------------------
# ����
# --------------------------------------------------------------------
class Pet( NPCObject, PetAI, SkillBox ) :
	__typesMaps = {}
	__typesMaps[ csdefine.PET_TYPE_STRENGTH ]	= ShareTexts.PET_TYPE_STRENGTH
	__typesMaps[ csdefine.PET_TYPE_SMART ]		= ShareTexts.PET_TYPE_SMART
	__typesMaps[ csdefine.PET_TYPE_INTELLECT ]	= ShareTexts.PET_TYPE_INTELLECT
	__typesMaps[ csdefine.PET_TYPE_BALANCED ]	= ShareTexts.PET_TYPE_BALANCED

	__attrNamesMaps = {}
	__attrNamesMaps[ "corporeity" ]	    = ShareTexts.PET_CORPOREITY_ENHANCE
	__attrNamesMaps[ "strength" ]		= ShareTexts.PET_STRENGTH_ENHANCE
	__attrNamesMaps[ "intellect" ] 		= ShareTexts.PET_INTELLECT_ENHANCE
	__attrNamesMaps[ "dexterity" ] 		= ShareTexts.PET_DEXTERITY_ENHANCE

	def __init__( self ) :
		NPCObject.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_PET )				# ���ó������
		PetAI.__init__( self )
		SkillBox.__init__( self )

		self.initSkills()

		self.initialize()

		self.notifyDefOwner_( "onGetPetCell", self )
		self.isUseCombatCamp = True

	# ----------------------------------------------------------------
	# initialize methods
	# ----------------------------------------------------------------
	def initialize( self ) :
		self.changeState( csdefine.ENTITY_STATE_FREE )				# ��ʼ״̬
		self.tickCount = 0											# ��������
		self.joyancyDecTime = time.time()							# ��ʼ�����ֶȵݼ�ʱ��
		self.__heartbeatTimerID = self.addTimer( 1.0, Const.PET_HEARTBEAT_INTERVAL, ECBExtend.PET_HEARTBEAT_CBID )
		self.__startRevert()										# ���� HP �� MP �ظ�
		self.__calcSndAttrsBase()
		self.setJoyancy( self.joyancy )
		if self.HP == 0 or self.isDeadWithdraw :					# �ж��ϴλ����Ƿ�����Ϊ����
			self.full()												# ������������յģ����ó�����Ѫ��ħ
			self.isDeadWithdraw = False								# ���������ձ������Ϊ False


	# ----------------------------------------------------------------
	# tussle formulas
	# ----------------------------------------------------------------
	def calcHPMax( self ):
		"""
		<virtual/>
		HP ���ֵ
		"""
		PetAI.calcHPMax( self )
		self.__startRevert()

	def calcHPMaxBase( self ):
		"""
		virtual method.
		HP ����ֵ
		"""
		self.HP_Max_base = int( formulas.getBaseHPMax( self.corporeity, self.ability, self.level ) )

	def calcMPMax( self ):
		"""
		<virtual/>
		MP ���ֵ
		"""
		PetAI.calcMPMax( self )
		self.__startRevert()

	def calcMPMaxBase( self ):
		"""
		virtual method.
		MP ����ֵ
		"""
		self.MP_Max_base = int( formulas.getBaseMPMax( self.intellect, self.ability, self.level ) )

	def calcHPCureSpeed( self ):
		"""
		<virtual/>
		���������ָ��ٶ�(ÿ3����Իָ���������ֵ��ս��ʱ��Ч����ֵ����)
		"""
		self.HP_regen_base = 3.0 * self.corporeity * 0.03 + 11
		PetAI.calcHPCureSpeed( self )

	def calcMPCureSpeed( self ):
		"""
		<virtual/>
		���㷨���ظ��ٶ�(ÿ3����Իָ��ķ�����ֵ��ս��ʱ��Ч����ֵ����)
		"""
		self.MP_regen_base = 3.0 * self.intellect * 0.03 + 15
		PetAI.calcMPCureSpeed( self )

	# ---------------------------------------
	def calcPhysicsDPSBase( self ):
		"""
		��������DPS_baseֵ
		"""
		self.physics_dps_base = int( formulas.getBasePhysicsDPS( self.species, self.ability, self.strength, self.dexterity, self.level ) * csconst.FLOAT_ZIP_PERCENT )

	# ---------------------------------------
	def calcDoubleHitProbabilityBase( self ):
		"""
		��������
		"""
		self.double_hit_probability_base = int( formulas.getDoubleHitProbability( self.species, self.level, self.dexterity, self.ability ) * csconst.FLOAT_ZIP_PERCENT )

	def calcMagicDoubleHitProbabilityBase( self ):
		"""
		����������
		"""
		self.magic_double_hit_probability_base = int( formulas.getMagicDoubleHitProbability( self.species, self.level, self.intellect, self.ability ) * csconst.FLOAT_ZIP_PERCENT )

	def calcDodgeProbabilityBase( self ):
		"""
		������ ����ֵ
		��ɫ����Է������ļ��ʡ���ͨ���������Ա����ܡ������ܹ����ͷ������ܹ������ܱ����ܡ����ܳɹ��󣬱����������ι��������κ��˺���
		"""
		self.dodge_probability_base = int( formulas.getDodgeProbability( self.species, self.level, self.dexterity, self.ability ) * csconst.FLOAT_ZIP_PERCENT )

	def calcResistHitProbabilityBase( self ):
		"""
		�м���
		�м�����ָ�мܷ����ļ��ʣ���ͨ�������������ܹ��������ܹ����мܡ����Ƿ������������ܱ��мܡ��мܳɹ��󣬽�ɫ�ܵ����˺�����50%
		"""
		self.resist_hit_probability_base = int( formulas.getResistProbability( self.species, self.level, self.strength, self.ability ) * csconst.FLOAT_ZIP_PERCENT )

	# ---------------------------------------
	def calcArmorBase( self ):
		"""
		virtual method
		�������ֵ	��ʾ����ɫ�ܵ�������ʱ���ܶԴ�������������������������
		"""
		self.armor_base = formulas.getPhysicsArmorRadies( self.species, self.level, self.ability )

	def calcMagicArmorBase( self ):
		"""
		virtual method
		��������ֵ	��ʾ����ɫ�ܵ���������ʱ���ܶԴ˷�������������������������
		"""
		self.magic_armor_base = formulas.getMagicArmorRadies( self.species, self.level, self.ability )

	# ---------------------------------------
	def calcHitSpeedBase( self ):
		"""
		�����ٶ�
		"""
		self.hit_speed_base = int( formulas.getHitSpeed( self.species ) * csconst.FLOAT_ZIP_PERCENT )

	# ---------------------------------------
	def calcDamageMinBase( self ):
		"""
		������С�������� ����ֵ
		"""
		self.damage_min_base =  formulas.getMinDamage( self.species, self.physics_dps )

	def calcDamageMaxBase( self ):
		"""
		��������������� ����ֵ
		"""
		self.damage_max_base = formulas.getMaxDamage( self.species, self.physics_dps )

	def calcMagicDamageBase( self ):
		"""
		virtual method
		����������
		"""
		self.magic_damage_base = formulas.getMagicDamage( self.ability, self.species, self.intellect, self.level )

	# ---------------------------------------
	def calcDamageMin( self ):
		"""
		������С��������
		"""
		PetAI.calcDamageMin( self )
		# �������Եĸı䣬 ����Ӧ��֪ͨ�ͻ������»�ȡ����
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetDamageMin( self.damage_min )

	def calcDamageMax( self ):
		"""
		���������������
		"""
		PetAI.calcDamageMax( self )
		# �������Եĸı䣬 ����Ӧ��֪ͨ�ͻ������»�ȡ����
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetDamageMax( self.damage_max )

	# ---------------------------------------
	def calcMagicDamage( self ):
		"""
		virtual method
		����������
		"""
		PetAI.calcMagicDamage( self )
		# �������Եĸı䣬 ����Ӧ��֪ͨ�ͻ������»�ȡ����
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetMagicDamage( self.magic_damage )

	# ---------------------------------------
	def calcArmor( self ):
		"""
		virtual method
		�������ֵ	��ʾ����ɫ�ܵ�������ʱ���ܶԴ�������������������������
		"""
		PetAI.calcArmor( self )
		# �������Եĸı䣬 ����Ӧ��֪ͨ�ͻ������»�ȡ����
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetArmor( self.armor )

	def calcMagicArmor( self ):
		"""
		virtual method
		��������ֵ	��ʾ����ɫ�ܵ���������ʱ���ܶԴ˷�������������������������
		"""
		PetAI.calcMagicArmor( self )
		# �������Եĸı䣬 ����Ӧ��֪ͨ�ͻ������»�ȡ����
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetMagicArmor( self.magic_armor )

	# ---------------------------------------
	def calcDodgeProbability( self ):
		"""
		������
		��ɫ����Է������ļ��ʡ���ͨ���������Ա����ܡ������ܹ����ͷ������ܹ������ܱ����ܡ����ܳɹ��󣬱����������ι��������κ��˺���
		"""
		PetAI.calcDodgeProbability( self )
		# �������Եĸı䣬 ����Ӧ��֪ͨ�ͻ������»�ȡ����
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetDodgeProbability( self.dodge_probability )

	# ---------------------------------------
	def calcResistHitProbability( self ):
		"""
		�м���
		�м�����ָ�мܷ����ļ��ʣ���ͨ�������������ܹ��������ܹ����мܡ����Ƿ������������ܱ��мܡ��мܳɹ��󣬽�ɫ�ܵ����˺�����50%
		"""
		PetAI.calcResistHitProbability( self )
		# �������Եĸı䣬 ����Ӧ��֪ͨ�ͻ������»�ȡ����
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetResistHitProbability( self.resist_hit_probability )

	# ---------------------------------------
	def calcDoubleHitProbability( self ):
		"""
		��������
		"""
		PetAI.calcDoubleHitProbability( self )
		# �������Եĸı䣬 ����Ӧ��֪ͨ�ͻ������»�ȡ����
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetDoubleHitProbability( self.double_hit_probability )

	def calcMagicDoubleHitProbability( self ):
		"""
		����������
		"""
		PetAI.calcMagicDoubleHitProbability( self )
		# �������Եĸı䣬 ����Ӧ��֪ͨ�ͻ������»�ȡ����
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetMagicDoubleHitProbability( self.magic_double_hit_probability )

	# ---------------------------------------
	def calcResistGiddyProbability( self ):
		"""
		����ֿ�ѣ�μ���
		"""
		PetAI.calcResistGiddyProbability( self )
		# �������Եĸı䣬 ����Ӧ��֪ͨ�ͻ������»�ȡ����
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetResistGiddyProbability( self.resist_giddy_probability )

	def calcResistFixProbability( self ):
		"""
		����ֿ�������
		"""
		PetAI.calcResistFixProbability( self )
		# �������Եĸı䣬 ����Ӧ��֪ͨ�ͻ������»�ȡ����
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetResistFixProbability( self.resist_fix_probability )

	def calcResistChenmoProbability( self ):
		"""
		����ֿ���Ĭ����
		"""
		PetAI.calcResistChenmoProbability( self )
		# �������Եĸı䣬 ����Ӧ��֪ͨ�ͻ������»�ȡ����
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetResistChenmoProbability( self.resist_chenmo_probability )

	def calcResistSleepProbability( self ):
		"""
		����ֿ�˯�߼���
		"""
		PetAI.calcResistSleepProbability( self )
		# �������Եĸı䣬 ����Ӧ��֪ͨ�ͻ������»�ȡ����
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetResistSleepProbability( self.resist_sleep_probability )

	def calcElemHuoDerateRatio( self ):
		"""
		�����Ԫ�ؿ��� ������ ����Ԫ�ؿ�����ൽ8��
		"""
		self.elem_huo_derate_ratio = max(0, min( csconst.PET_ELEMENT_DERATE_MAX, calcProperty( self.elem_huo_derate_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_huo_derate_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_huo_derate_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_huo_derate_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT ) )

	def calcElemXuanDerateRatio( self ):
		"""
		������Ԫ�ؿ��� ������ ����Ԫ�ؿ�����ൽ8��
		"""
		self.elem_xuan_derate_ratio = max(0, min( csconst.PET_ELEMENT_DERATE_MAX, calcProperty( self.elem_xuan_derate_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_xuan_derate_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_xuan_derate_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_xuan_derate_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT ) )

	def calcElemLeiDerateRatio( self ):
		"""
		������Ԫ�ؿ��� ������ ����Ԫ�ؿ�����ൽ8��
		"""
		self.elem_lei_derate_ratio = max(0, min( csconst.PET_ELEMENT_DERATE_MAX, calcProperty( self.elem_lei_derate_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_lei_derate_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_lei_derate_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_lei_derate_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT ) )

	def calcElemBingDerateRatio( self ):
		"""
		�����Ԫ�ؿ��� ������ ����Ԫ�ؿ�����ൽ8��
		"""
		self.elem_bing_derate_ratio = max(0, min( csconst.PET_ELEMENT_DERATE_MAX, calcProperty( self.elem_bing_derate_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_bing_derate_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_bing_derate_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_bing_derate_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT ) )

	def calcRange( self ):
		"""
		virtual method.

		���㹥������
		"""
		ptype = self.getPType()
		if ptype == csdefine.PET_TYPE_SMART:		# �����ͳ���
			self.range_base = Const.PET_SMART_RANGE
		elif ptype == csdefine.PET_TYPE_INTELLECT:	# �����ͳ���
			self.range_base = Const.PET_INTELLECT_RANGE

		PetAI.calcRange( self )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __calcSndAttrsBase( self ) :
		"""
		���¼�������������
		ע�⣺���������Ըı�ʱ����ս������Ҳ���Ÿı䣬������ﻹҪ���¼���ս������
		"""
		sndAttrValues = formulas.getSndProperties( self.species, self.level, self.nimbus )
		self.corporeity_base = self.e_corporeity + sndAttrValues["corporeity"]
		self.strength_base = self.e_strength + sndAttrValues["strength"]
		self.intellect_base = self.e_intellect + sndAttrValues["intellect"]
		self.dexterity_base = self.e_dexterity + sndAttrValues["dexterity"]
		self.move_speed_base = 90000					# �����ƶ��ٶ�
		self.HP_regen_base = 10							# HP �ظ��ٶ�
		self.calcDynamicProperties()

	# -------------------------------------------------
	def __lifeDetecting( self ) :
		"""
		�����ļ����
		"""
		self.addLife( -formulas.getTickLifeDecreasement( self.getHierarchy() ) )

	def __joyancyDetecting( self ) :
		"""
		���ֶȵݼ����
		"""
		self.addJoyancy( -formulas.getTickJoyancyDecreasement() )


	# -------------------------------------------------
	def __startRevert( self ):
		"""
		���� HP / MP �ָ�
		"""
		if self.__revertTimerID : return
		if self.isState( csdefine.ENTITY_STATE_FIGHT ) : return
		if self.isState( csdefine.ENTITY_STATE_DEAD ) : return
		if self.HP >= self.HP_Max and self.MP >= self.MP_Max : return
		self.__revertTimerID = self.addTimer( Const.PET_MP_REVER_INTERVAL, Const.PET_MP_REVER_INTERVAL, ECBExtend.REVERT_HPMP_TIMER_CBID )

	def __stopRevert( self ):
		"""
		���� HP/MP �ָ�
		"""
		if self.__revertTimerID:
			self.cancel( self.__revertTimerID )
			self.__revertTimerID = 0


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def hackVerify_( self, srcEntityID ) :
		"""
		��֤�Ƿ�����ƭ�Բ���
		"""
		if srcEntityID != self.ownerID :
			hacker = BigWorld.entities.get( srcEntityID, None )
			if hacker :
				hacker.statusMessage( csstatus.GB_INVALID_CALLER )
			HACK_MSG( "unright srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return False
		elif self.state == csdefine.ENTITY_STATE_DEAD :
			return False
		return True

	# -------------------------------------------------
	def notifyOwner_( self, methodName, *args ) :
		"""
		����������ҵķ� def ����
		"""
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner is None :
			self.baseOwner.remoteCall( methodName, args )
		elif owner.isReal() :
			getattr( owner, methodName )( *args )
		else :
			owner.remoteCall( methodName, args )

	def notifyDefOwner_( self, methodName, *args ) :
		"""
		����������ҵ� def ����
		"""
		owner = self.getOwner()
		getattr( owner.entity, methodName )( *args )

	def notifyClient_( self, methodName, *args ) :
		"""
		����������ɫ�Ŀͻ��˷���
		"""
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner is None :
			getattr( self.baseOwner.client, methodName )( *args )
		else :
			getattr( owner.client, methodName )( *args )

	def notifyMyClient_( self, methodName, *args ):
		"""
		�����Լ��Ŀͻ��˷���
		"""
		if self.baseOwner is None:
			return
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner is not None :
			client = owner.clientEntity( self.id )
			getattr( client, methodName )( *args )
		else :
			INFO_MSG("Pet(id %i) can't find owner(id %i) in current cellapp."%(self.id, self.baseOwner.id))

	# -------------------------------------------------
	def onAddBuff( self, buff ) :
		"""
		���һ�� buff
		"""
		self.notifyClient_( "pcg_onPetAddBuff", buff )
		PetAI.onAddBuff( self, buff )
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner:
			owner.onPetAddBuff( buff )

	def onRemoveBuff( self, buff ) :
		"""
		ɾ��һ�� buff
		"""
		self.notifyClient_( "pcg_onPetRemoveBuff", buff[ "index" ] )
		PetAI.onRemoveBuff( self, buff )
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner:
			owner.onPetRemoveBuff( buff )

	# ----------------------------------------------------------------
	# public methods called by owner
	# ----------------------------------------------------------------
	def withdraw( self, wmode ) :
		"""
		defined method.
		���ճ���
		"""
		if wmode == csdefine.PET_WITHDRAW_COMMON and \
			self.isState( csdefine.ENTITY_STATE_FIGHT ) :
			self.statusMessage( csstatus.PET_WITHDRAW_FAIL_IN_FIGHT )
		else :
			self.base.withdraw( wmode )

	def free( self ) :
		"""
		��������
		"""
		if self.isState( csdefine.ENTITY_STATE_FIGHT ) :
			self.notifyDefOwner_( "pcg_onFreeResult", csstatus.PET_FREE_FAIL_FIGHTING )
		else :
			self.base.withdraw( csdefine.PET_WITHDRAW_FREE )

	# -------------------------------------------------
	def rejuvenesce( self, evolveType ) :
		"""
		define method.
		��ͯ
		"""
		newHierarchy = formulas.getRejuvenesceHierarchy( self.getHierarchy() )
		ptype = self.getPType()
		self.species = ptype | newHierarchy
		self.name = formulas.getDisplayName( self.species, self.uname, "" )

		self.EXP = 0

		self.e_corporeity = 0
		self.e_strength = 0
		self.e_intellect = 0
		self.e_dexterity = 0

		self.ec_corporeity = 0
		self.ec_strength = 0
		self.ec_intellect = 0
		self.ec_dexterity = 0
		self.ec_free = 0

		for attrName in ["corporeity", "strength", "intellect", "dexterity", "free"]:
			self.notifyMyClient_( "onSetEC_" + attrName, getattr( self, "ec_" + attrName ) )

		self.ability = formulas.getAbility( self.takeLevel, newHierarchy, evolveType, self.stamp )
		self.setAbility( self.ability )
		self.setNimbus( 0 )
		self.setCalcaneus( 0 )

		self.character = formulas.getCharacter()
		self.setCharacter( self.character )
		self.life = csconst.PET_LIFE_UPPER_LIMIT
		self.setLife( self.life )
		self.joyancy = csconst.PET_JOYANCY_UPPER_LIMIT
		self.setJoyancy( self.joyancy )

		self.level = 1
		self.__calcSndAttrsBase()
		self.resetSkill()			# ��ͯ�����ü��ܡ�10:47 2009-2-14��wsf
		self.setHP( self.HP_Max )
		self.setMP( self.MP_Max )

		self.statusMessage( csstatus.PET_EVOLVE_SUCCESS )

	def combine( self, dbid ) :
		"""
		define method.
		�ϳɳ���
		"""
		maxNimbus = formulas.getMaxNimbus( self.level )
		if self.nimbus >= maxNimbus :
			self.notifyDefOwner_( "pcg_onCombineResult", csstatus.PET_COMBINE_FAIL_NIMBUS_FULL,"" )
		else :
			self.baseOwner.pcg_combinePets( self.level, dbid )

	def enhance( self, etype, attrName, value ) :
		"""
		define method.
		ǿ��
		"""
		if not hasattr( self, attrName ) :
			HACK_MSG( "the attribute '%s' is not exist! enhance fail" % attrName )
			self.notifyOwner_( "pcg_onEnhanceResult", csstatus.PET_ENHANCE_FAIL_HACK )
			return

		def allownCommonEnhance() :
			"""
			��ͨǿ��
			"""
			maxCcount = formulas.getFixedEnhanceCount( self.species, attrName, self.level )
			count = getattr( self, "ec_" + attrName )
			if count >= maxCcount :
				self.notifyOwner_( "pcg_onEnhanceResult", csstatus.PET_ENHANCE_FAIL_COM_FULL, self.__attrNamesMaps[attrName] )
				return False
			setattr( self, "ec_" + attrName, count + 1 )
			self.notifyMyClient_( "onSetEC_" + attrName, getattr( self, "ec_" + attrName ) )
			return True

		def allowFreeEnhance() :
			"""
			����ǿ��
			"""
			maxCcount = formulas.getFreeEnhanceCount( self.level )
			if self.ec_free >= maxCcount :
				self.notifyOwner_( "pcg_onEnhanceResult", csstatus.PET_ENHANCE_FAIL_FREE_FULL )
				return False
			self.ec_free += 1
			self.notifyMyClient_( "onSetEC_free", self.ec_free )
			return True

		verifies = {}
		verifies[csdefine.PET_ENHANCE_COMMON]	= allownCommonEnhance
		verifies[csdefine.PET_ENHANCE_FREE]		= allowFreeEnhance
		if etype in verifies :
			if verifies[etype]() :
				getattr( self, "addE" + attrName )( value )
				self.notifyOwner_( "pcg_onEnhanceResult", csstatus.PET_ENHANCE_SUCCESS )
		else :
			self.notifyOwner_( "pcg_onEnhanceResult", csstatus.PET_ENHANCE_FAIL_HACK )

	# -------------------------------------------------
	def lifeup( self, value ) :
		"""
		����
		"""
		if self.life >= csconst.PET_LIFE_UPPER_LIMIT :											# ��������
			self.notifyDefOwner_( "pcg_onAddLifeResult", csstatus.PET_ADD_LIFE_FAIL_FULL )
		else :
			self.addLife( value )
			self.notifyDefOwner_( "pcg_onAddLifeResult", csstatus.PET_ADD_LIFE_SUCCESS )

	def domesticate( self, value ) :
		"""
		ѱ��
		"""
		if self.joyancy < csconst.PET_JOYANCY_UPPER_LIMIT :										# ����ѱ��
			self.addJoyancy( value )
			self.notifyDefOwner_( "pcg_onAddJoyancyResult", csstatus.PET_ADD_JOYANCY_SUCCESS )

	# -------------------------------------------------
	def setEXP( self, value ) :
		"""
		define method
		���� EXP
		"""
		expMax = PetLevelEXP.getEXPMax( self.level )
		self.EXP = min( max( value, 0 ), expMax )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def statusMessage( self, *args ) :
		"""
		��ϵͳ��Ϣ���͵�������ҵĿͻ���
		"""
		self.notifyOwner_( "statusMessage", *args )

	# -------------------------------------------------
	def getOwner( self ) :
		"""
		��ȡ������ɫ�� cell entity �� cellmailbox
		@rtype					: _PetOwner
		@return					: ���س���������ɫ�İ�װ���벻Ҫ����˷���ʵ���Թ�����ʹ��
								: ע�⣺���᷵�� None����Ϊ�����ܻ�������
		"""
		return _PetOwner( self.baseOwner )

	def getName( self ) :
		"""
		��ȡ��������
		"""
		return formulas.getDisplayName( self.species, self.uname, "" )

	def getNameAndID( self ) :
		"""
		��ȡ��������
		"""
		return formulas.getDisplayName( self.species, self.uname, "" ) + "(%s)" % self.databaseID

	def getHierarchy( self ) :
		"""
		��ȡ���ﱲ��
		"""
		return self.species & csdefine.PET_HIERARCHY_MASK

	def getPType( self ) :
		"""
		��ȡ�������
		"""
		return self.species & csdefine.PET_TYPE_MASK

	def getClass( self ):
		"""
		��ȡ����ְҵ
		"""
		return self.getPType()

	def isRaceclass( self, rc, mask = csdefine.PET_TYPE_MASK ):
		"""
		�Ƿ�Ϊָ������ְҵ��
		"""
		return self.species & mask == rc

	def tlskillNum( self ):
		"""
		�츳���ܵĸ���
		"""
		mapMonsterScript = g_objFactory.getObject( self.getOwner().entity.pcg_petDict.get( self.databaseID ).mapMonster )
		vpet = g_objFactory.getObject( mapMonsterScript.mapPetID )
		return vpet.getInbornSkillsCount()

	def getStamp( self ):
		"""
		��ó���ӡ�ǣ���д����ϵͳ
		"""
		return self.stamp

	# ----------------------------------------------------------------
	# defined methids called by base
	# ----------------------------------------------------------------
	def rename( self, newName ) :
		"""
		defined.
		����������
		"""
		self.name = newName
		self.notifyDefOwner_( "pcg_onRenameResult", csstatus.PET_RENAME_SUCCESS )

	def queryPetNimbus( self, queryerMB, params ):
		"""
		define method
		"""
		queryerMB.client.onStatusMessage( csstatus.STRING_PET_NIMBUS, str(( self.nimbus, )) )

	def queryPetLife( self, queryerMB, params ):
		"""
		define method
		"""
		queryerMB.client.onStatusMessage( csstatus.STRING_PET_LIFE, str(( self.life, )) )

	def queryPetJoyancy( self, queryerMB, params ):
		"""
		define method
		"""
		queryerMB.client.onStatusMessage( csstatus.STRING_PET_JOYANCY, str(( self.joyancy, )) )

	def queryPetPropagate( self, queryerMB, params ):
		"""
		define method
		"""
		if self.species & csdefine.PET_HIERARCHY_MASK == csdefine.PET_HIERARCHY_GROWNUP:
			queryerMB.client.onStatusMessage( csstatus.STRING_PET_HIERARCHY_GROWNUP, "" )
		if self.species & csdefine.PET_HIERARCHY_MASK == csdefine.PET_HIERARCHY_INFANCY1:
			queryerMB.client.onStatusMessage( csstatus.STRING_PET_HIERARCHY_INFANCY1, "" )
		if self.species & csdefine.PET_HIERARCHY_MASK == csdefine.PET_HIERARCHY_INFANCY2:
			queryerMB.client.onStatusMessage( csstatus.STRING_PET_HIERARCHY_INFANCY2, "" )


	# ----------------------------------------------------------------
	# exposed methods
	# ----------------------------------------------------------------
	def requestSkillBox( self, srcEntityID ) :
		"""
		<Exposed/>
		�����������е�skillID�����������ڵ�client
		"""
		self.notifyClient_( "pcg_onInitPetSkillBox", self.getSkills() )

	def requestBuffs( self, srcEntityID ) :
		"""
		<Exposed/>
		���������� buff
		"""
		if srcEntityID == self.ownerID :					# ����������������
			for buff in self.attrBuffs :
				self.onAddBuff( buff )
		else :												# ����Ǳ���������
			try : entity = BigWorld.entities[srcEntityID]
			except KeyError : return
			client = entity.clientEntity( self.id )
			for buff in self.attrBuffs :
				#����Ƿ���Ҫ�ͻ�����ʾ����������
				if buff["sourceType"] != csdefine.BUFF_ORIGIN_SYSTEM:
					client.onReceiveBuff( buff )


	# ----------------------------------------------------------------
	# �������Է���
	# ----------------------------------------------------------------
	def setLevel( self, level ) :
		"""
		for real
		virtual method
		���õȼ�
		"""
		if level == self.level : return
		level = min( max( level, 1 ), PetLevelEXP.getMaxLevel() )
		if level > self.level :
			self.setJoyancy( csconst.PET_JOYANCY_UPPER_LIMIT )
			self.absorbableEXPLevelValue = 0
		oldLevel = self.level
		self.level = level
		self.__calcSndAttrsBase()
		self.setEXP( self.EXP )
		# ��Ѫ��ħ
		self.full()
		self.onSkillUpgrade()
		self.statusMessage( csstatus.ACCOUNT_STATE_PET_UPDATE_GRADE, level )

	def setHP( self, value ):
		"""
		for real
		virtual method
		����HP
		"""
		PetAI.setHP( self, value )
		self.__startRevert()

	def setMP( self, value ):
		"""
		for real
		virtual method
		����MP
		"""
		PetAI.setMP( self, value )
		self.__startRevert()

	def calcStrength( self ):
		"""
		���������������µ��ͻ���
		"""
		PetAI.calcStrength( self )
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner:
			owner.clientEntity( self.id ).onSetStrength( self.strength )

	def calcIntellect( self ):
		"""
		���������������µ��ͻ���
		"""
		PetAI.calcIntellect( self )
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner:
			owner.clientEntity( self.id ).onSetIntellect( self.intellect )

	def calcDexterity( self ):
		"""
		�������ݣ������µ��ͻ���
		"""
		PetAI.calcDexterity( self )
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner:
			owner.clientEntity( self.id ).onSetDexterity( self.dexterity )

	def calcCorporeity( self ):
		"""
		�������ʣ������µ��ͻ���
		"""
		PetAI.calcCorporeity( self )
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner:
			owner.clientEntity( self.id ).onSetCorporeity( self.corporeity )

	# ---------------------------------------
	def setEcorporeity( self, value ) :
		"""
		for real
		����ǿ��������ֵ
		"""
		value = max( value, 0 )
		self.e_corporeity = value
		self.__calcSndAttrsBase()

		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetE_corporeity( self.e_corporeity )

	def setEstrength( self, value ) :
		"""
		for real
		����ǿ��������ֵ
		"""
		value = max( value, 0 )
		self.e_strength = value
		self.__calcSndAttrsBase()

		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetE_strength( self.e_strength )

	def setEintellect( self, value ) :
		"""
		for real
		����ǿ��������ֵ
		"""
		value = max( value, 0 )
		self.e_intellect = value
		self.__calcSndAttrsBase()

		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetE_intellect( self.e_intellect )

	def setEdexterity( self, value ) :
		"""
		for real
		����ǿ��������ֵ
		"""
		value = max( value, 0 )
		self.e_dexterity = value
		self.__calcSndAttrsBase()

		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetE_dexterity( self.e_dexterity )

	# ---------------------------------------
	def setNimbus( self, value ) :
		"""
		for real
		��������
		"""
		maxNimbus = formulas.getMaxNimbus( self.level )
		self.nimbus = min( max( value, 0 ), maxNimbus )
		self.__calcSndAttrsBase()

		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetNimbus( self.nimbus )

	# ---------------------------------------
	def setLife( self, value ) :
		"""
		for real
		��������
		"""
		value = min( max( value, 0 ), csconst.PET_LIFE_UPPER_LIMIT )
		self.life = value
		if value == 0 :
			self.changeState( csdefine.ENTITY_STATE_DEAD )

		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetLife( self.life )

	# ---------------------------------------
	def setCharacter( self, value ) :
		"""
		for real
		�����Ը�
		"""
		if value == 0 :
			self.changeState( csdefine.PET_CHARACTER_SUREFOOTED )
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetCharacter( self.character )
	# -----------------------------------------
	def setJoyancy( self, value ) :
		"""
		for real
		���ÿ��ֶ�
		"""
		value = min( max( value, 0 ), csconst.PET_JOYANCY_UPPER_LIMIT )
		self.joyancy = value

		oldPercent = self.queryTemp( "pet_effect_by_joyancy", 0.0 )
		newPercent = formulas.getJoyancyEffect( self.joyancy )
		percent = newPercent - oldPercent
		if percent != 0:
			self.setTemp( "pet_effect_by_joyancy", newPercent )
			value = percent * csconst.FLOAT_ZIP_PERCENT
			# ������
			self.damage_min_percent += value
			self.damage_max_percent += value
			self.calcDamageMin()
			self.calcDamageMax()
			# ��������
			self.magic_damage_percent += value
			self.calcMagicDamage()
			# �������
			self.armor_percent += value
			self.calcArmor()
			# ��������
			self.magic_armor_percent += value
			self.calcMagicArmor()

		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner :
			owner.clientEntity( self.id ).onSetJoyancy( self.joyancy )

	# -------------------------------------------------
	def setCalcaneus( self, value ):
		"""
		define method
		���ó������
		"""
		self.calcaneus = value
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner:
			owner.clientEntity( self.id ).onSetCalcaneus( self.calcaneus )
	# -------------------------------------------------
	def addEXP( self, value ) :
		"""
		defined method
		���� EXP
		"""
		wowner = self.getOwner()
		earg, owner = wowner.etype, wowner.entity

		#--------- ����Ϊ������ϵͳ���ж� --------#
		if earg == "REAL" and value >=0 :
			gameYield = owner.wallow_getLucreRate()
			value = value * gameYield							# ����ֵȡ�� modify by gjx 2009-3-30
		#--------- ����Ϊ������ϵͳ���ж� --------#

		if self.level >= csconst.PET_LEVEL_UPPER_LIMIT:			# ����ȼ�������ʱ���ŵ�110����
			return
		if earg == "REAL":
			# ����ʯ����ӳ�
			gemExp = value * ( owner.gem_getComGemCount() + owner.ptn_getComGemCount() ) * csconst.GEM_PET_COMMON_EXP_PERCENT
			if gemExp > 0:
				owner.client.onStatusMessage( csstatus.PET_EXP_GET_FOR_STONE, str(( gemExp, )) )
				value += int( gemExp )

		maxExp = PetLevelEXP.getEXPMax( self.level )
		if self.EXP + value >= maxExp:
			if not getattr( owner,"level" ):
				return
			if self.level >= owner.level + Const.PET_EXP_LEVEL_LIMIT_GAP:	# �������ҵȼ�������������Ʒŵ����� by����
				self.EXP = maxExp
				return
		newLevel, newEXP = formulas.getAddedEXP( self.level, self.EXP, value )
		self.EXP = newEXP
		value = int( value )
		if value > 0 :
			self.statusMessage( csstatus.ACCOUNT_STATE_PET_GAIN_EXP, value )
		elif value < 0 :
			self.statusMessage( csstatus.ACCOUNT_STATE_PET_LOST_EXP, -value )
		self.setLevel( newLevel )

	def addQuestEXP( self, value, questLevel ):
		"""
		define method
		����������
		˥����ʽΪ��
		����ȼ�С������ȼ�5��������ȼ�-����ȼ�=5������ɸ��������þ������10%
		����ȼ�С������ȼ�6��������ȼ�-����ȼ�=6������ɸ��������þ������20%
		����ȼ�С������ȼ�7��������ȼ�-����ȼ�=7������ɸ��������þ������30%
		����ȼ�С������ȼ�8��������ȼ�-����ȼ�=8������ɸ��������þ������40%
		����ȼ�С������ȼ�9��������ȼ�-����ȼ�=9������ɸ��������þ������50%
		����ȼ�С������ȼ�10��������ȼ�-����ȼ�=10������ɸ��������þ������60%
		����ȼ�С������ȼ�11��������ȼ�-����ȼ�=11������ɸ��������þ������70%
		����ȼ�С������ȼ�12�����ϣ�����ȼ�-����ȼ����ڵ���12������ɸ�������20%���飨Ҳ���Ǽ���80%����
		"""
		levelMinus = questLevel - self.level
		if levelMinus > 12:
			newValue = value * 0.2
		elif levelMinus < 5:
			newValue = value
		else:
			newValue = value * ( 1 - ( levelMinus - 4 ) * 0.1 )

		self.addEXP( int( newValue ) )					# ����ֵȡ�� modify by gjx 2009-3-30


	def absorbEXP( self, value ):
		"""
		Define method.
		�Ӵ�����ʯ�����վ���

		@param value : ������ʯ�ľ�����ֵ,INT32
		"""
		# ������ȡ�ľ��鲻�ܳ����ȼ����辭��10% by ����
		absorbLevelMax = PetLevelEXP.getEXPMax( self.level ) / 10
		oldLevel = self.level
		if self.absorbableEXPLevelValue >= absorbLevelMax:
			self.statusMessage( csstatus.PET_ABSORT_LEVEL_EXP_FULL )
			return
		limitValue = absorbLevelMax - self.absorbableEXPLevelValue
		if value > limitValue: value = limitValue

		date = time.localtime( self.absorbDate )[ 0:3 ]	# ���������
		today = time.localtime()[ 0:3 ]					# ��ý��������
		if cmp( date, today ) != 0:						# ���컹û��ȡ�����飬��ô���ý������ȡ����
			expUpper = formulas.getAbsorbExpUpper( self.level )
			self.absorbableEXP = expUpper
			self.absorbDate = time.time()				# ������ȡ������Ч��
		else:
			expUpper = self.absorbableEXP
			if expUpper == 0:
				self.statusMessage( csstatus.PET_TRAIN_FEED_LIMIT ) #���첻������ȡ����ľ���ֵ�ˡ�
				return
		tempValue = value
		if tempValue > expUpper:
			tempValue = expUpper
#		if not self.addEXP( tempValue ):
#			tempValue = 0
		self.absorbableEXP = expUpper - tempValue

		self.absorbableEXPLevelValue += value

		owner = self.getOwner().entity
		if owner.level + Const.PET_EXP_LEVEL_LIMIT_GAP > self.level:
			newLevel, newEXP = formulas.getAddedEXP( self.level, self.EXP, tempValue )
			self.EXP = newEXP
			self.setLevel( newLevel )
		else:
			self.EXP += value

		if value > 0 :
			self.statusMessage( csstatus.ACCOUNT_STATE_PET_GAIN_EXP, tempValue )
		elif value < 0 :
			self.statusMessage( csstatus.ACCOUNT_STATE_PET_LOST_EXP, -tempValue )

		owner.ptn_onFeedEXPResult( csstatus.PET_TRAIN_FEED_SUCCESS, tempValue )

	# ---------------------------------------
	def addCalcaneus( self, value ) :
		"""
		for real
		��Ӹ���
		"""
		value += self.calcaneus
		#hierarchy = self.species & csdefine.PET_HIERARCHY_MASK
		maxNimbus = formulas.getMaxNimbus( self.level )
		newNimbus, newCalcaneus = formulas.calcaneusToNimbus( maxNimbus, self.nimbus, value )
		upFlag = newNimbus - self.nimbus
		self.setNimbus( newNimbus )
		if self.nimbus == maxNimbus:
			self.calcaneus = 0
		else:
			self.calcaneus = newCalcaneus
		if upFlag:
			self.statusMessage( csstatus.PET_COMBINE_SUCCESS_UP_1,upFlag )
		self.setCalcaneus( self.calcaneus )
	# ---------------------------------------
	def addEcorporeity( self, value ) :
		"""
		for real
		�������
		"""
		self.setEcorporeity( value + self.e_corporeity )

	def addEstrength( self, value ) :
		"""
		for real
		�������
		"""
		self.setEstrength( value + self.e_strength )

	def addEintellect( self, value ) :
		"""
		for real
		�������
		"""
		self.setEintellect( value + self.e_intellect )

	def addEdexterity( self, value ) :
		"""
		for real
		�������
		"""
		self.setEdexterity( value + self.e_dexterity )

	# ---------------------------------------
	def addNimbus( self, value ) :
		"""
		for real
		�����ֵ
		"""
		self.setNimbus( self.nimbus + value )

	# ---------------------------------------
	def addLife( self, value ) :
		"""
		for real
		�������
		"""
		self.setLife( self.life + value )

	def addJoyancy( self, value ) :
		"""
		for real
		��ӿ��ֶ�
		"""
		self.setJoyancy( self.joyancy + value )

	def setAbility( self, value ):
		"""
		define method
		���ó���ɳ���
		"""
		self.ability = value
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner:
			owner.clientEntity( self.id ).onSetAbility( self.ability )

	# -------------------------------------------------
	def addSkill( self, skillID ):
		"""
		for real
		����һ�����ܡ�
		@param skillID:	Ҫ���ӵļ��ܱ�ʶ
		@type skillID:	int
		@return:		�Ƿ�ɹ�
		@rtype:			bool
		"""
		if SkillBox.addSkill( self, skillID ):
			cskill = g_skills[skillID]
			if cskill.getType() not in csconst.BASE_SKILL_TYPE_PASSIVE_SPELL_LIST:
				self.autoAddQBItem( skillID )		# ��ѧ�����Զ��ӵ��������
			self.notifyClient_( "pcg_onPetAddSkill", skillID )
		else:
			return False
		return True

	def removeSkill( self, skillID ):
		"""
		for real
		ȥ��һ�����ܡ�
		@param skillID:	Ҫȥ���ļ��ܱ�ʶ
		@type skillID:	string
		@return:		�Ƿ�ɹ�
		@rtype:			bool
		"""
		if SkillBox.removeSkill( self, skillID ):
			PetAI.removeSkill( self, skillID )
			self.notifyClient_( "pcg_onPetRemoveSkill", skillID )
		else:
			return False
		return True

	def updateSkill( self, oldSkillID, newSkillID ):
		"""
		for real
		����һ�����ܣ���һ������ID��Ϊ��һ������ID��
		@type oldSkillID: SKILLID
		@type newSkillID: SKILLID
		"""
		if oldSkillID == newSkillID : return False
		if SkillBox.updateSkill( self, oldSkillID, newSkillID ):
			PetAI.onUpdateSkill( self, oldSkillID, newSkillID )
			self.notifyClient_( "pcg_onPetUpdateSkill", oldSkillID, newSkillID )
		else:
			return False
		return True

	def changeCooldown( self, typeID, lastTime, totalTime, endTimeVal ):
		"""
		virtual method.
		�ı�һ��cooldown������
		@type  typeID: INT16
		@type timeVal: INT32
		"""
		PetAI.changeCooldown( self, typeID, lastTime, totalTime, endTimeVal )
		self.notifyClient_( "pcg_onPetCooldownChanged", typeID, lastTime, totalTime )

	# -------------------------------------------------
	def isInTeam( self ) :
		"""
		for real
		�Ƿ��ڶ�����
		"""
		owner = self.getOwner()
		if owner.etype == "MAILBOX" :
			return False
		return owner.entity.isInTeam()

	def getTeamMailbox( self ) :
		"""
		��ȡ��������
		"""
		owner = self.getOwner()
		if owner.etype == "MAILBOX" :
			return None
		return owner.entity.getTeamMailbox()

	# -------------------------------------------------
	def queryRelation( self, entity ) :
		"""
		virtual method.
		��ȡ������ָ�� entity �Ĺ�ϵ
		"""
		#if self.isDestroyed or entity.isDestroyed:
		#	return csdefine.RELATION_NOFIGHT

		#if not isinstance( entity, CombatUnit ):
		#	return csdefine.RELATION_FRIEND
		
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND

		if entity.effect_state & csdefine.EFFECT_STATE_PROWL:	# ���entity����Ǳ��Ч��״̬
			return csdefine.RELATION_NOFIGHT

		owner = self.getOwner()
		if owner.etype == "MAILBOX" :
			return csdefine.RELATION_NONE
		else :
			return owner.entity.queryRelation( entity )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onPetHeartbeatTimer( self, timerID, cbid ) :
		"""
		�������� timer
		"""
		if not self.isReal() : return
		self.tickCount += 1
		if self.tickCount % Const.PET_LIFE_WASTAGE_INTERVAL == Const.PET_LIFE_WASTAGE_INTERVAL - 1:
			self.__lifeDetecting()
		if self.tickCount % Const.PET_JOYANCY_WASTAGE_INTERVAL == Const.PET_JOYANCY_WASTAGE_INTERVAL -1:
			self.__joyancyDetecting()
		self.actionThinking_()


	def onPetDieWithdrawTimer( self, timerID, userData ) :
		"""
		���������ʱ timer
		"""
		wmode = self.queryTemp( "pet_death_status" )
		self.removeTemp( "pet_death_status" )
		if wmode :
			self.isDeadWithdraw = True
			self.base.withdraw( wmode )
		else :
			WARNING_MSG( "delay withdrawed twice!" )

	def onRevertTimer( self, timerID, cbid ):
		"""
		ʱ�䴦���¼�
		"""
		if self.HP < self.HP_Max :
			self.addHP( self.HP_regen )
		if self.MP < self.MP_Max :
			self.addMP( self.MP_regen )
		if self.HP_Max == self.HP and self.MP_Max == self.MP:
			self.__stopRevert()

	# -------------------------------------------------
	def onBeforeTeleport( self, newSpaceID, pos ) :
		"""
		���ｫҪ��תʱ�����ã�oldSpaceID : ��ǰspaceID, newSpaceID : ��Ҫ������ spaceID, pos : ��Ҫ������λ�ã�
		"""
		#self.spellTarget( csconst.PENDING_SKILL_ID, self.id )		# ������ʩ��һ��δ��buff
		pass

	# -------------------------------------------------
	def onStateChanged( self, old, new ) :
		"""
		״̬�ı�ʱ������
		"""
		PetAI.onStateChanged( self, old, new )
		if self.isState( csdefine.ENTITY_STATE_DEAD ) and old != new :	# �����������
			wmode = csdefine.PET_WITHDRAW_HP_DEATH				# Ĭ�ϻ��շ�ʽΪ��������
			if self.life <= 0 :													# �������Ϊ 0
				wmode = csdefine.PET_WITHDRAW_LIFE_DEATH			# ����շ�ʽ��Ϊ�����ľ�����
			self.setTemp( "pet_death_status", wmode )						# ��¼������ʽ
			self.addTimer( Const.PET_DIE_WITHDRAW_DELAY, 0, \
				ECBExtend.PET_DIE_WITHDRAW_DELAY_CBID )							# ������ʱ
			self.__stopRevert()													# ��ֹͣ�ظ�
		elif self.isState( csdefine.ENTITY_STATE_FREE ) or \
			self.isState( csdefine.ENTITY_STATE_REST ) :						# ���������Ϣ������״̬
				self.__startRevert()											# �ָ�״̬�ĸı�
		elif self.isState( csdefine.ENTITY_STATE_FIGHT ) :						# �������ս��״̬
			self.__stopRevert()													# ��ֹͣ�ظ�

	def onDie( self, killerID ) :
		"""
		�̳з�����CombatUnit
		@param		killerID : ɱ���ߵ�ID
		@type		killerID : OBJECT_ID
		"""
		spaceKey = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		spaceScript = g_objFactory.getObject( spaceKey )
		if not spaceScript.isSpaceCalcPkValue :							# �����ǰ��ͼ����PK�����ͷ�
			reduceLife = int( formulas.getLostBellLifeDecreasement() * ( 1 - self.queryTemp( "pet_life_reduce_discount", 0.0 ) ) )
			self.addLife( -reduceLife )									# ���ۼ�����
			reduceJoyancy = int( formulas.getLostBellJoyancyDecreasement() * ( 1 - self.queryTemp( "pet_joyancy_reduce_discount", 0.0 ) ) )
			self.addJoyancy( -reduceJoyancy )							# �ۼ����ֶ�

	# -------------------------------------------------
	def onSkillUpgrade( self ):
		"""
		��������
		"""
		for skillID in list( self.attrSkillBox ):
			cskill = g_skills[skillID]
			if cskill.getType() == csdefine.BASE_SKILL_TYPE_PASSIVE:	# �츳����ֻ���ڰ��������
				continue
			if cskill.getLevel() < cskill.getMaxLevel():
				lv = cskill.getMaxLevel() - cskill.getLevel()
				if g_skillTeachDatas[ skillID + lv ]['ReqLevel'] <= self.level:
					self.updateSkill( skillID, skillID + lv )
				else:
					for v in xrange( lv ):
						if self.level < g_skillTeachDatas[ skillID + v + 1 ]['ReqLevel']:
							self.updateSkill( skillID, skillID + v )
							break

	def resetSkill( self ):
		"""
		��������ǰ�ļ�����������ļ�������

		wsf add,10:47 2009-2-14
		"""
		mapMonsterScript = g_objFactory.getObject( self.getOwner().entity.pcg_petDict.get( self.databaseID ).mapMonster )
		vpet = g_objFactory.getObject( mapMonsterScript.mapPetID )
		defaultSkillIDs = vpet.getDefSkillIDs( self.level )
		for skillID in list( self.attrSkillBox ):
			self.removeSkill( skillID )
			level1SkillID = skillID / 1000 * 1000 + 1
			if g_skills[level1SkillID].getType() == csdefine.BASE_SKILL_TYPE_PASSIVE:	# ������츳���ܣ����»����ͽ׵ļ���
				self.addSkill( level1SkillID )
		for defaultSkillID in defaultSkillIDs:
			self.addSkill( defaultSkillID )

	def onDestroy( self ) :
		"""
		�����ٵ�ʱ����������
		"""
		PetAI.onDestroy( self )
		SkillBox.onDestroy( self )
		self.cancel( self.__heartbeatTimerID )		# ֹͣ����
		self.cancel( self.__revertTimerID )			# ֹͣ��Ѫ/����
		self.clearBuff( [0] ) 						# ����������е�buff

		# �����ҶԳ�������� BaseApp::setClient: Could not find base ***
		if not self.baseOwner:
			return
		
		owner = BigWorld.entities.get( self.baseOwner.id, None )
		if owner:
			owner.pcg_mbBaseActPet = None
			owner.pcg_actPetDBID = 0
		else:
			INFO_MSG( " My( %s, %i) owner has been destroyed!" % ( self.getName(), self.id ) )
		
		# in 1.8.6, ������base�ˣ���������¼��owner�����ڳ���destroyed��
		# �����ڳ������Ǻ��������ˣ���ң���ͬһ��baseapp��
		# ������Ѵ�������ΪNone����base�������޷��ҵ����˵�base��ʹ������crash.
		self.baseOwner = None

	def removePetBuff( self, buffID, index ):
		"""
		defined method
		ɾ����������һ��BUFF
		"""
		buff = None
		try :
			buff = self.getBuff( index )
		except :
			ERROR_MSG( "pet %d required remove buff, but the given index %d is out of range!" % ( self.id, index ) )
			return

		if buff["skill"].getID() == buffID and g_skills[buffID].isBenign() :
			self.removeBuff( index, [csdefine.BUFF_INTERRUPT_REQUEST_CANCEL] )
		else :
			DEBUG_MSG( "pet: %d. the buff he required to remove is not mach or it is not a benign buff" % self.id )

	def requeryPetDatas( self, srcEntityID ):
		"""
		exposed method
		��ȡ��������
		"""
		petDatas = {}
		observer = BigWorld.entities.get( srcEntityID, None )
		if observer is None:
			return
		petDatas["databaseID"] = self.databaseID
		petDatas["uname"] = self.getName()
		petDatas["modelNumber"] = self.modelNumber
		petDatas["gender"] = self.gender
		petDatas["species"] = self.getHierarchy()
		petDatas["level"] = self.level
		petDatas["ptype"] = self.getPType()
		petDatas["EXP"] = self.EXP
		petDatas["HPMax"] = self.HP_Max
		petDatas["MPMax"] = self.MP_Max
		petDatas["HP"] = self.HP
		petDatas["MP"] = self.MP
		petDatas["strength"] = self.strength
		petDatas["intellect"] = self.intellect
		petDatas["dexterity"] = self.dexterity
		petDatas["corporeity"] = self.corporeity
		petDatas["ec_corporeity"] = self.ec_corporeity
		petDatas["ec_strength"] = self.ec_strength
		petDatas["ec_intellect"] = self.ec_intellect
		petDatas["ec_dexterity"] = self.ec_dexterity
		petDatas["ec_free"] = self.ec_free
		petDatas["ability"] = self.ability
		petDatas["nimbus"] = self.nimbus
		petDatas["calcaneus"] = self.calcaneus
		petDatas["character"] = self.character
		petDatas["procreated"] = self.procreated
		petDatas["life"] = self.life
		petDatas["joyancy"] = self.joyancy
		petDatas["attrSkillBox"] = self.attrSkillBox
		petDatas["takeLevel"] = self.takeLevel
		petDatas["damage_min"] = self.damage_min
		petDatas["damage_max"] = self.damage_max
		petDatas["armor"] = self.armor
		petDatas["dodge_probability"] = self.dodge_probability
		petDatas["double_hit_probability"] = self.double_hit_probability
		petDatas["resist_hit_probability"] = self.resist_hit_probability
		petDatas["magic_damage"] = self.magic_damage
		petDatas["magic_armor"] = self.magic_armor
		petDatas["dodge_probability"] = self.dodge_probability
		petDatas["magic_double_hit_probability"] = self.magic_double_hit_probability
		petDatas["resist_giddy_probability"] = self.resist_giddy_probability
		petDatas["resist_fix_probability"] = self.resist_fix_probability
		petDatas["resist_chenmo_probability"] = self.resist_chenmo_probability
		petDatas["resist_sleep_probability"] = self.resist_sleep_probability
		observer.clientEntity( self.id ).onRecievePetData( petDatas )


	# ----------------------------------------------------------------
	# ��輼�ܶԳ����Ӱ��
	# ----------------------------------------------------------------
	def onVehicleAddSkills( self, skillIDList, vehicleJoyancyEffect ):
		"""
		Define Method
		Զ�̼�����Ч
		"""
		self.setTemp( "vehicleJoyancyEffect", vehicleJoyancyEffect )
		for skillID in skillIDList:
			if not g_skills.has( skillID ):
				WARNING_MSG( "Skills(%i) does not exist!" % skillID )
				continue
			skill = g_skills[skillID]
			skill.attach( self )

		self.__calcSndAttrsBase()

	def onVehicleRemoveSkills( self, skillIDList, vehicleJoyancyEffect ):
		"""
		Define Method
		Զ�̼���ж��
		"""
		self.setTemp( "vehicleJoyancyEffect", vehicleJoyancyEffect )
		for skillID in skillIDList:
			if not g_skills.has( skillID ):
				WARNING_MSG( "Skills(%i) does not exist!" % skillID )
				continue
			skill = g_skills[skillID]
			skill.detach( self )

		self.__calcSndAttrsBase()

	# ----------------------------------------------------------------
	# ���װ���Գ����Ӱ�죨�񾭲���
	# ----------------------------------------------------------------
	def onVehicleAddEquips( self, equipIDList ):
		"""
		defined Method
		������װ��ʱ���������񾭲���
		@type			equipIDList : ARRAY of ITEM_ID
		@param			equipIDList : ��ӵ�װ�� ID �б�
		"""
		for itemID in equipIDList :
			if itemID == 0 : continue
			item = items.instance().createDynamicItem( itemID )
			if item is None : continue
			extraEffect = item.query( "eq_extraEffect", {} )
			for key, value in extraEffect.iteritems() :
				effectClass = g_equipEffect.getEffect( key )
				if effectClass is None : continue
				effectClass.attach( self, value, item )

	def onVehicleRemoveEquips( self, equipIDList ) :
		"""
		defined Method
		���ɾ��װ��ʱ���������񾭲���
		@type			equipIDList : ARRAY of ITEM_ID
		@param			equipIDList : ɾ����װ�� ID �б�
		"""
		for itemID in equipIDList :
			if itemID == 0 : continue
			item = items.instance().createDynamicItem( itemID )
			if item is None : continue
			extraEffect = item.query( "eq_extraEffect", {} )
			for key, value in extraEffect.iteritems() :
				effectClass = g_equipEffect.getEffect( key )
				if effectClass is None : continue
				effectClass.detach( self, value, item )

	def calcPropertiesByVehicle( self ) :
		"""
		defined methid
		��Ϊ���װ���ĸ��£����¼����������
		"""
		self.__calcSndAttrsBase()

	def isDead( self ):
		"""
		virtual method.

		@return: BOOL�������Լ��Ƿ��Ѿ��������ж�
		@rtype:  BOOL
		"""
		return self.state == csdefine.ENTITY_STATE_DEAD

	def getLevel( self ):
		"""
		����
		"""
		return self.level

	def beforePostureChange( self, newPosture ):
		"""
		��̬�ı�֮ǰ

		@param newPosture : �ı�����̬
		"""
		SkillBox.beforePostureChange( self, newPosture )

	def afterPostureChange( self, oldPosture ):
		"""
		��̬�ı��

		@param oldPosture : �ı�ǰ����̬
		"""
		SkillBox.afterPostureChange( self, oldPosture )
		
	def getRelationEntity( self ):
		"""
		��ȡ��ϵ�ж�����ʵentity
		"""
		owner = self.getOwner()
		if owner.etype == "MAILBOX" :
			return None
		else:
			return owner.entity
			
	def queryCombatRelation( self, entity ):
		owner = self.getOwner()
		if owner.etype == "MAILBOX" :
			return csdefine.RELATION_NONE
		else:
			return owner.entity.queryCombatRelation( entity )
		