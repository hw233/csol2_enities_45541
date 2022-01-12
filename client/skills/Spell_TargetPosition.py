# -*- coding: gb18030 -*-
#Ϊ��ʵ��λ�ù�Чʵ�ֵĿͻ��˽ű�

import BigWorld
import csdefine
from bwdebug import *
from gbref import rds
from SpellBase import *
import SkillTargetObjImpl
import csarithmetic
from config.client.NpcSkillName import Datas as npcSkillName


class Spell_TargetPosition( Spell ):
	def __init__( self ):
		"""
		��sect����SkillBase
		@param sect:			���������ļ���XML Root Section
		@type sect:				DataSection
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type dict:				python dict
		"""
		Spell.init( self, dict )

	def isTargetPositionSkill( self ):
		"""
		�ж��Ƿ���λ�ù�Ч����
		@return: BOOL
		"""
		return True

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
		self.pose.cast( caster, skillID, targetObject )

		rds.skillEffect.playCastEffects( caster, targetObject, self.getID() )

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
