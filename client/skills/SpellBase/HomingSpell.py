# -*- coding: gb18030 -*-
#
# $Id: Spell.py,v 1.00 14:08 2010-3-18 jiangyi Exp $

"""
HomingSpell�����ࡣ
"""
from Spell import Spell
import skills
from gbref import rds
import BigWorld
import ItemTypeEnum
from bwdebug import *
import csdefine
import Define
import csstatus
import math
import Math
from config.skill.Skill.SkillDataMgr import Datas as SKILL_DATA

class HomingSpell( Spell ):
	"""
	��������ģ��
	"""
	def __init__( self ):
		"""
		����SkillBase
		"""
		Spell.__init__( self )
		self.childSkill = None

	def isHomingSkill( self ):
		"""
		�ж��Ƿ��������� 	by ����
		@return: BOOL
		"""
		return True
	
	def isNormalHomingSkill( self ):
		"""
		�ж��Ƿ�������ͨ�������� by wuxo
		@return: BOOL
		"""
		return False

	def interrupt( self, caster, reason ):
		"""
		��ֹʩ�ż��ܡ�
		@param caster:			ʩ����Entity
		@type caster:			Entity
		"""
		if reason in [csstatus.SKILL_NOT_READY,csstatus.SKILL_CANT_CAST]:return
		if reason == csstatus.SKILL_INTERRUPTED_BY_TIME_OVER :return
		Spell.interrupt( self, caster, reason )
		rds.skillEffect.stopHomingEffects( caster )
		model = caster.getModel()
		if model is None:return
		for name in model.queue:
			rds.actionMgr.stopAction( caster.getModel(), name )

	def rotate( self, caster, receiver ):
		"""
		ת������
		"""
		if caster.id == receiver.id:
			return
		#���˻�˯��ѣ�Ρ������Ч��ʱ�����Զ�ת��
		EffectState_list = csdefine.EFFECT_STATE_FIX | csdefine.EFFECT_STATE_VERTIGO | csdefine.EFFECT_STATE_SLEEP | csdefine.EFFECT_STATE_BE_HOMING
		if caster.effect_state & EffectState_list != 0: return
		
		new_yaw = (receiver.position - caster.position).yaw
		BigWorld.player().am.turnModelToEntity = 0
		BigWorld.player().model.yaw = new_yaw
		BigWorld.dcursor().yaw = new_yaw
		BigWorld.player().am.turnModelToEntity = 1
	
	def cast( self, caster, targetObject ):
		"""
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		if caster.id == BigWorld.player().id:
			target = targetObject.getObject()
			skillID = self.getID()
			childID = int( SKILL_DATA.__getitem__( skillID )["param2"].split(",")[0] )
			param4 = SKILL_DATA.__getitem__( childID )["param4"].split(";")
			attackTargetDis = 0.0
			attackTrackDis = 6.0
			if len( param4 ) >= 2:
				attackTargetDis = float( param4[0] )
				attackTrackDis = float( param4[1] )
			caster.setPhysicsHoming( attackTargetDis, attackTrackDis, target )
		Spell.cast( self, caster, targetObject )
		

class NormalHomingSpell( HomingSpell ):
	"""
	������ͨ��������ģ��by wuxo
	"""
	def isNormalHomingSkill( self ):
		"""
		�ж��Ƿ�������ͨ�������� 
		@return: BOOL
		"""
		return True
	
	def __idConvert( self, skillID ):
		"""
		ת������IDΪϵ��ID
		�磺311120001 -> 311120
		�����Զ��弼��ID����ת��
		"""
		# ����IDС��1000Ϊ�������ã�����ת��
		if skillID < csdefine.SKILL_ID_LIMIT:
			return skillID
		return skillID/1000

	def getIcon( self ):
		"""
		����������ͼ��ʹ������ͼ��ͼ��
		"""
		id = self.__idConvert( self.getID() )
		if not id in Define.TRIGGER_SKILL_IDS: 
			return Spell.getIcon( self )
		pl = BigWorld.player()
		try:
			if pl.primaryHandEmpty():
				return Spell.getIcon( self )
			else:
				item = pl.getItem_( ItemTypeEnum.CWT_RIGHTHAND )
				return item.icon()
		except AttributeError, errstr:
			WARNING_MSG( errstr )
			return Spell.getIcon( self )