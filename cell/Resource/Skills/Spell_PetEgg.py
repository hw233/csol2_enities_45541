# -*- coding: gb18030 -*-

import csstatus
import csconst
import csdefine
import random
from Love3 import g_objFactory
from Spell_Item import Spell_Item
from bwdebug import *

class Spell_PetEgg( Spell_Item ):
	"""
	���ﵰ����
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )
		self.petClassID = 0
		self.petTypeDict = {}

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self.petClassID = ( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else "" )
		for sParam in ( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else "" ) .split( ";" ):
			petTypeList = sParam.split( ":" )
			self.petTypeDict[int( petTypeList[0] )] = float( petTypeList[1] ) / 100	# self.petTypeDict:{ ����1:����1, ����}

	def getCatchPetType( self ):
		"""
		��ó���ı���
		"""
		rate = random.random()
		rateSect = 0.0
		for hierarchy, petRate in self.petTypeDict.iteritems():
			rateSect += petRate
			if rate < petRate:
				return hierarchy

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		�ܷ�ʹ�ü��ܵļ��

		@param caster : ʩչ������
		@type caster : BigWorld.entity
		@param target : ʩչ����
		@type target : һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		baseStatus = Spell_Item.useableCheck( self, caster, target )
		if baseStatus != csstatus.SKILL_GO_ON:
			return baseStatus

		if caster.pcg_isFull():
			return csstatus.SKILL_MISSING_FULL_PET
		petScriptObject = g_objFactory.getObject( self.petClassID )

		# 14:33 2009-10-22��wsf���˴�������ű��Ƿ������Ȩ��֮�ƣ���ֹ�߻�������������Ҳ�����ص���ʧ��
		if petScriptObject is None:
			ERROR_MSG( "--->>>����ű�( %s )������!" % self.petClassID )
			caster.client.onStatusMessage( csstatus.PET_CONFIG_NOT_FIND, "" )
			return csstatus.PET_ADD_JOYANCY_FAIL_UNKNOW

		if caster.level < petScriptObject.takeLevel or petScriptObject.minLv - csconst.PET_CATCH_OVER_LEVEL > caster.level:
			return csstatus.PET_LEVEL_CANT_FIT
		return csstatus.SKILL_GO_ON

	def castValidityCheck( self, caster, receiver ):
		"""
		virtual method.
		У�鼼���Ƿ����ʩչ��
		�˽ӿڽ������ڵ�������������ж��Ƿ��ܶ�Ŀ��ʩչ��
		�����Ҫ�ж�һ�������Ƿ��ܶ�Ŀ��ʹ�ã�Ӧ��ʹ��intonateValidityCheck()������
		�˽ӿڻᱻintonateValidityCheck()�ӿڵ��ã��������ʱĳЩ������Ҫ�������������жϣ�
		��������ش˽ӿڲ���������жϣ�����ֻ������intonateValidityCheck()�ӿڡ�

		ע���˽ӿ��Ǿɰ��е�validCast()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		state = Spell_Item.castValidityCheck( self, caster, receiver )
		if state != csstatus.SKILL_GO_ON:
			return state
		if caster.pcg_isFull():
			return csstatus.SKILL_MISSING_FULL_PET
		return state

	def receive( self, caster, receiver ):
		"""
		virtual method.
		��������Ҫ��������
		���Ƕ��Լ�ʹ�õ���Ʒ���ܣ����receiver�϶���real entity
		"""
		monsterScriptObject = g_objFactory.getObject( self.petClassID )
		petID = monsterScriptObject.mapPetID
		level = random.randint( monsterScriptObject.minLv, monsterScriptObject.maxLv )
		defaultSkillIDs = g_objFactory.getObject( petID ).getDefSkillIDs( level )
		modelNumbers = monsterScriptObject.getEntityProperty( "modelNumber" )
		if len( modelNumbers ):
			modelNumber = modelNumbers[ random.randint( 0, len(modelNumbers) - 1 ) ]
		else:
			modelNumber = ""
		receiver.base.pcg_catchPet( self.petClassID, level, modelNumber, defaultSkillIDs, self.getCatchPetType(), caster.getByUid( caster.queryTemp( "item_using" ) ).isBinded(),False, False )