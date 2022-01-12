# -*- coding: gb18030 -*-

from CEquip import CEquip
import ItemTypeEnum
import random

from ItemSystemExp import TalismanExp
g_talisman = TalismanExp.instance()
from TalismanEffectLoader import TalismanEffectLoader
g_tmEffect = TalismanEffectLoader.instance()
from EquipEffectLoader import EquipEffectLoader
g_equipEffect = EquipEffectLoader.instance()
from config.item.TalismanAmend import Datas as TalismanAmentData

class CTalisman( CEquip ):
	"""
	����-�̳�װ��
	"""
	def __init__( self, srcData ):
		"""
		"""
		CEquip.__init__( self, srcData )
		self.__initExtraEffect()

	def getFDict( self ):
		"""
		Virtual Method
		��ȡ����Ч�������Զ������ݸ�ʽ
		���ڷ��͵��ͻ���
		return INT32
		"""
		return self.model()

	def icon( self ):
		"""
		��ȡͼ��·��
		"""
		grade = self.getGrade()
		if grade == ItemTypeEnum.TALISMAN_COMMON:
			return CEquip.icon( self )
		else:
			try:
				return TalismanAmentData[self.id][grade][1]
			except:
				return CEquip.icon( self )

	def model( self ):
		"""
		��ȡģ��
		"""
		grade = self.getGrade()
		if grade == ItemTypeEnum.TALISMAN_COMMON:
			return CEquip.model( self )
		else:
			try:
				return TalismanAmentData[self.id][grade][0]
			except:
				return CEquip.model( self )

	def __initExtraEffect( self, owner = None ):
		"""
		���ݷ�����Ʒ����ʼ����������
		"""
		# ������ʼ�����Ի�����6�����ԡ���Ʒ2������Ʒ2������Ʒ2����
		# Ĭ������·���Ʒ�������ἤ��Ʒ����Ӧ�������е�һ�����ԡ�
		grade = self.getGrade()
		# ���ɷ�Ʒ���ԣ�Ĭ�ϵ�һ�������Ǽ����
		if len( self.getCommonEffect() ) == 0:
			isLive = grade >= ItemTypeEnum.TALISMAN_COMMON
			commonEffectID1 = g_tmEffect.getEffects( ItemTypeEnum.TALISMAN_COMMON )
			commonEffectID2 = g_tmEffect.getEffects( ItemTypeEnum.TALISMAN_COMMON )
			commonEffect = [ ( commonEffectID1, isLive ), ( commonEffectID2, False ) ]
			self.setCommonEffect( commonEffect, owner )
		# ������Ʒ���ԣ�Ĭ�ϵ�һ�������Ǽ����
		if len( self.getImmortalEffect() ) == 0:
			isLive = grade >= ItemTypeEnum.TALISMAN_IMMORTAL
			immortalEffectID1 = g_tmEffect.getEffects( ItemTypeEnum.TALISMAN_IMMORTAL )
			immortalEffectID2 = g_tmEffect.getEffects( ItemTypeEnum.TALISMAN_IMMORTAL )
			immortalEffect = [ ( immortalEffectID1, isLive ), ( immortalEffectID2, False ) ]
			self.setImmortalEffect( immortalEffect, owner )
		# ������Ʒ���ԣ�Ĭ�ϵ�һ�������Ǽ����
		if len( self.getDeityEffect() ) == 0:
			isLive = grade >= ItemTypeEnum.TALISMAN_DEITY
			deityEffectID1 = g_tmEffect.getEffects( ItemTypeEnum.TALISMAN_DEITY )
			deityEffectID2 = g_tmEffect.getEffects( ItemTypeEnum.TALISMAN_DEITY )
			deityEffect = [ ( deityEffectID1, isLive ), ( deityEffectID2, False ) ]
			self.setDeityEffect( deityEffect, owner )
		# ������������
		flawEffect = g_tmEffect.getFlawEffect()
		if len( flawEffect ):
			self.setFlawEffect( flawEffect, owner )

	def getExp( self ):
		"""
		��ȡ������ǰ����ֵ
		"""
		return self.query( "tm_exp", 0 )

	def getMaxExp( self ):
		"""
		��÷������������ֵ
		"""
		return g_tmEffect.getMaxExp( self.getLevel() )

	def addExp( self, exp, owner = None ):
		"""
		�������Ӿ���ֵ
		@param		exp		:	��������ֵ
		@type		exp		:	INT64
		@param		owner	:	����ӵ����
		@type		owner	:	entity
		@return				:	None
		"""
		#--------- ����Ϊ������ϵͳ���ж� --------#
		if owner != None and exp >=0:
			gameYield = owner.wallow_getLucreRate()
			exp = exp * gameYield
		#--------- ����Ϊ������ϵͳ���ж� --------#
		self.setExp( self.getExp() + exp, owner )

	def setExp( self, exp, owner = None ):
		"""
		���÷����ľ���ֵ
		@param		exp		:	��������ֵ
		@type		exp		:	INT64
		@param		owner	:	����ӵ����
		@type		owner	:	entity
		@return				:	None
		"""
		self.set( "tm_exp", exp, owner )

	def setLevel( self, lv, owner = None ):
		"""
		�趨�����ĵȼ�
		@param		lv		:	�����ȼ�
		@type		lv		:	INT64
		@param		owner	:	����ӵ����
		@type		owner	:	entity
		@return				:	None
		"""
		oldLevel = self.getLevel()
		if oldLevel == lv: return

		# ���õȼ�
		self.set( "level", lv, owner )

		# �����װ��û��װ�����߲�����װ��ֱ�ӷ���
		if not self.isAlreadyWield(): return False
		if not self.canWield( owner ): return False

		# �������ѡ����
		skillList = g_tmEffect.getSkillListByID(self.id)
		if 0 != len(skillList) and 0 == self.query( "spell", 0 ):
			odd = g_tmEffect.getOdds(self.getLevel())
			if random.randint(1, 10000) <= odd * 10000:
				skillID = random.choice(skillList) * 1000 + 1
				self.setSKillID( skillID, owner )
				if owner: owner.addSkill( skillID )

		# ��������������������
		# ж�ػ�������
		extraEffect = self.getExtraEffect()
		newExtraEffect = dict( extraEffect )
		baseExtraEffect = self.queryBaseData( "eq_extraEffect", {} )
		for key, value in extraEffect.iteritems():
			effectClass = g_equipEffect.getEffect( key )
			if effectClass is None: continue
			# ����������
			beginValue = baseExtraEffect.get( key )
			if beginValue is None: continue
			param = g_tmEffect.getBaseUpParam()
			newValue = beginValue + lv * param
			# ж�ؾ�����
			effectClass.detach( owner, value, self )
			# ����������
			effectClass.attach( owner, newValue, self )
			# �洢������
			newExtraEffect[key] = newValue
		# �����»�����������
		self.set( "eq_extraEffect", newExtraEffect, owner )

		if owner is None: return
		totalEffect = []
		# ��Ʒ����
		commonEffect = self.getCommonEffect()
		totalEffect.extend( commonEffect )
		# ��Ʒ����
		immortalEffect = self.getImmortalEffect()
		totalEffect.extend( immortalEffect )
		# ��Ʒ����
		deityEffect = self.getDeityEffect()
		totalEffect.extend( deityEffect )

		for key, state in totalEffect:
			# ����δ���������
			if not state: continue
			# ��ȡ���Խű�
			effectKey =  g_tmEffect.getEffectID( key )
			effectClass = g_equipEffect.getEffect( effectKey )
			if effectClass is None: continue
			# �������Բ�ֵ
			param = g_tmEffect.getUpParam( key )
			value = ( lv - oldLevel ) * param
			# �������Բ�ֵ
			effectClass.attach( owner, value, self )

		# ˢ���������
		owner.calcDynamicProperties()

	def getPotential( self ):
		"""
		��ȡ������ǰǱ��ֵ
		"""
		return self.query( "tm_potential", 0 )

	def getMaxPotential( self ):
		"""
		��÷����������Ǳ��ֵ
		"""
		if 0 == self.getSkillLevel():
			return 0
		return g_tmEffect.getPotential(self.getSkillLevel())

	def addPotential( self, exp, owner = None ):
		"""
		��������Ǳ��ֵ
		@param		exp		:	����Ǳ��ֵ
		@type		exp		:	INT64
		@param		owner	:	����ӵ����
		@type		owner	:	entity
		@return				:	None
		"""
		self.setPotential( self.getPotential() + exp, owner )

	def setPotential( self, exp, owner = None ):
		"""
		���÷�����Ǳ��
		@param		exp		:	��������ֵ
		@type		exp		:	INT64
		@param		owner	:	����ӵ����
		@type		owner	:	entity
		@return				:	None
		"""
		self.set( "tm_potential", exp, owner )

	def getSkillLevel( self ):
		"""
		��÷������ܵĵȼ�
		"""
		return self.query( "spell", 0 ) % 1000

	def setSkillLevel( self, lv, owner = None ):
		"""
		�趨�������ܵĵȼ�
		@param		lv		:	�������ܵȼ�
		@type		lv		:	INT64
		@param		owner	:	����ӵ����
		@type		owner	:	entity
		@return				:	None
		"""
		skillID = self.query( "spell", 0 )
		if 0 == skillID:return
		newSkillID = skillID - self.getSkillLevel() + lv
		self.setSKillID( newSkillID, owner )

	def getGrade( self ):
		"""
		��ȡ������Ʒ��
		"""
		return self.query( "tm_grade", ItemTypeEnum.TALISMAN_COMMON )

	def setGrade( self, grade, owner = None ):
		"""
		���÷�����Ʒ��
		@param		grade	:	����Ʒ��
		@type		grade	:	INT8
		@param		owner	:	����ӵ����
		@type		owner	:	entity
		@return				:	None
		"""
		if grade == self.getGrade(): return
		if grade < ItemTypeEnum.TALISMAN_COMMON: return
		if grade > ItemTypeEnum.TALISMAN_DEITY: return
		self.set( "tm_grade", grade, owner  )
		# ����Ʒ����Ӧ�ĵ�һ������
		if grade == ItemTypeEnum.TALISMAN_IMMORTAL:
			effect = list( self.getImmortalEffect() )
			fuc = self.setImmortalEffect
		elif grade == ItemTypeEnum.TALISMAN_DEITY:
			effect = list( self.getDeityEffect() )
			fuc = self.setDeityEffect
		else:
			return

		if len( effect ) == 0: return
		key, state = effect.pop(0)
		# ���Ǽ���״̬��ֱ�ӷ���
		if state: return
		effectKey =  g_tmEffect.getEffectID( key )
		effectClass = g_equipEffect.getEffect( effectKey )
		if effectClass is None: return
		# ���㸽������
		initEffectValue = g_tmEffect.getInitValue( key )
		param = g_tmEffect.getUpParam( key )
		value = initEffectValue + self.getLevel() * param
		# ��������
		effectClass.attach( owner, value, self )
		# ���ı�������
		effect.insert( 0, ( key, True ) )
		fuc( effect, owner )
		# ����Ҽ�������
		if owner is None: return

		owner.calcDynamicProperties()

	def getSkillID( self ):
		"""
		��ȡ����ID
		"""
		return self.query( "spell", 0 )

	def setSKillID( self, skillID, owner = None ):
		"""
		���÷����ļ���ID
		@param		skillID	:	����ID
		@type		skillID	:	INT64
		@param		owner	:	����ӵ����
		@type		owner	:	entity
		@return				:	None
		"""
		if owner is not None:
			oldID = self.getSkillID()
			if oldID != 0:
				owner.updateSkill( oldID, skillID )
			else:
				owner.addSkill( skillID )
			self.set( "spell", skillID, owner )

	def getCommonEffect( self ):
		"""
		��ȡ�����ķ�Ʒ����
		"""
		return self.query( "tm_commonEffect", [] )

	def getImmortalEffect( self ):
		"""
		��ȡ��������Ʒ����
		"""
		return self.query( "tm_immortalEffect", [] )

	def getDeityEffect( self ):
		"""
		��ȡ��������Ʒ����
		"""
		return self.query( "tm_deityEffect", [] )

	def getFlawEffect( self ):
		"""
		��ȡ��������������
		"""
		return self.query( "tm_flawEffect", {} )

	def setCommonEffect( self, effect, owner = None ):
		"""
		���÷����ķ�Ʒ��������
		@param		effect	:	��������
		@type		effect	:	dict
		@param		owner	:	����ӵ����
		@type		owner	:	entity
		@return				:	None
		"""
		self.set( "tm_commonEffect", effect, owner )

	def setImmortalEffect( self, effect, owner = None ):
		"""
		���÷�������Ʒ��������
		@param		effect	:	��������
		@type		effect	:	dict
		@param		owner	:	����ӵ����
		@type		owner	:	entity
		@return				:	None
		"""
		self.set( "tm_immortalEffect", effect, owner )

	def setDeityEffect( self, effect, owner = None ):
		"""
		���÷�������Ʒ��������
		@param		effect	:	��������
		@type		effect	:	dict
		@param		owner	:	����ӵ����
		@type		owner	:	entity
		@return				:	None
		"""
		self.set( "tm_deityEffect", effect, owner )

	def setFlawEffect( self, effect, owner = None ):
		"""
		���÷�������������
		@param		effect	:	��������
		@type		effect	:	dict
		@param		owner	:	����ӵ����
		@type		owner	:	entity
		@return				:	None
		"""
		self.set( "tm_flawEffect", effect, owner )

	def wield( self, owner, update = True ):
		"""
		װ������

		@param  owner: ����ӵ����
		@type   owner: Entity
		@return:    True װ���ɹ���False װ��ʧ��
		@return:    BOOL
		"""
		if owner is None: return
		if not CEquip.wield( self, owner, update ):
			return False

		# װ������
		skillID = self.getSkillID()
		if 0 != skillID and not owner.hasSkill( skillID ):
			#���װ�����߿��Է�����װ��װ�� �� ��������װ��������Ϊ�ϡ��������������װ��װ������ô������Ӧ�ļ��ܣ�����Ѿ�ӵ���˵ġ�
			#�ٵ���addSkill �����𾯸棬��Ȼ���Ƕ�֪�����������ǾͰ���������ų������⾯�淢����
			owner.addSkill(skillID)

		intensifyLevel = self.getIntensifyLevel()
		grade = self.getGrade()
		# ��������
		totalEffect = []
		# ��Ʒ����
		commonEffect = self.getCommonEffect()
		totalEffect.extend( commonEffect )
		# ��Ʒ����
		immortalEffect = self.getImmortalEffect()
		totalEffect.extend( immortalEffect )
		# ��Ʒ����
		deityEffect = self.getDeityEffect()
		totalEffect.extend( deityEffect )

		for key, state in totalEffect:	# ��������
			# ����δ���������
			if not state: continue
			# ��ȡ���Խű�
			effectKey =  g_tmEffect.getEffectID( key )
			effectClass = g_equipEffect.getEffect( effectKey )
			if effectClass is None: continue
			# ���㸽������
			initEffectValue = g_tmEffect.getInitValue( key )
			param = g_tmEffect.getUpParam( key )
			value = initEffectValue + self.getLevel() * param
			if intensifyLevel != 0:
				iRate = g_talisman.getIntensifyRate( grade, intensifyLevel )	# ǿ�����ӱ���
				value = (1.0 + iRate) * value
			# ��������
			effectClass.attach( owner, value, self )

		if intensifyLevel != 0:
			baseExtraEffect = self.getExtraEffect()
			for key, value in baseExtraEffect.iteritems():
				effectClass = g_equipEffect.getEffect( key )
				if effectClass is None: continue
				iRate = g_talisman.getIntensifyRate( grade, intensifyLevel )	# ǿ�����ӱ���
				value *= iRate
				effectClass.attach( owner, value, self  )

		# ��������
		flawEffect = self.getFlawEffect()
		for key, value in flawEffect.iteritems():
			effectClass = g_equipEffect.getEffect( key )
			if effectClass is None: continue
			effectClass.attach( owner, value, self )

		if update: owner.calcDynamicProperties()
		return True

	def unWield( self, owner, update = True ):
		"""
		ж��װ��

		@param  owner: ����ӵ����
		@type   owner: Entity
		@return:    ��
		"""
		if owner is None: return
		# ���û��װ��Ч������unwield
		if not self.isAlreadyWield(): return

		# ж��
		skillID = self.getSkillID()
		if 0 != skillID:owner.removeSkill(skillID)

		intensifyLevel = self.getIntensifyLevel()
		grade = self.getGrade()
		# ��������
		totalEffect = []
		# ��Ʒ����
		commonEffect = self.getCommonEffect()
		totalEffect.extend( commonEffect )
		# ��Ʒ����
		immortalEffect = self.getImmortalEffect()
		totalEffect.extend( immortalEffect )
		# ��Ʒ����
		deityEffect = self.getDeityEffect()
		totalEffect.extend( deityEffect )

		if intensifyLevel != 0:
			baseExtraEffect = self.getExtraEffect()
			for key, value in baseExtraEffect.iteritems():
				effectClass = g_equipEffect.getEffect( key )
				if effectClass is None: continue
				iRate = g_talisman.getIntensifyRate( grade, intensifyLevel )	# ǿ�����ӱ���
				value *= iRate
				effectClass.detach( owner, value, self  )

		for key, state in totalEffect:
			# ����δ���������
			if not state: continue
			# ��ȡ���Խű�
			effectKey =  g_tmEffect.getEffectID( key )
			effectClass = g_equipEffect.getEffect( effectKey )
			if effectClass is None: continue
			# ���㸽������
			initEffectValue = g_tmEffect.getInitValue( key )
			param = g_tmEffect.getUpParam( key )
			value = initEffectValue + self.getLevel() * param
			if intensifyLevel != 0:
				iRate = g_talisman.getIntensifyRate( grade, intensifyLevel )	# ǿ�����ӱ���
				value = (1.0 + iRate) * value
			# ��������
			effectClass.detach( owner, value, self )

		# ��������
		flawEffect = self.getFlawEffect()
		for key, value in flawEffect.iteritems():
			effectClass = g_equipEffect.getEffect( key )
			if effectClass is None: continue
			effectClass.detach( owner, value, self )

		CEquip.unWield( self, owner, update )
		return True