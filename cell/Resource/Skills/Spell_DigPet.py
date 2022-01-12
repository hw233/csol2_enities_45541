# -*- coding: gb18030 -*-
#
# $Id: Spell_DigPet.py,v 1.9 2008-08-02 09:24:52 songpeifang Exp $

"""
�ٻ���ҳ���
"""
import BigWorld

import csdefine
import csstatus
import csconst
from bwdebug import *

import Const
from SpellBase import *
from PetFormulas import formulas
import utils

class Spell_DigPet( Spell ):
	"""
	�ٻ���ҳ���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )

	def use( self, caster, target ):
		"""
		virtual method.
		����� target/position ʩչһ���������κη�����ʩ������ɴ˽���
		dstEntity��position�ǿ�ѡ�ģ����õĲ�����None���棬���忴���������Ƕ�Ŀ�껹��λ�ã�һ��˷���������client����ͳһ�ӿں���ת������
		Ĭ��ɶ��������ֱ�ӷ��ء�
		ע���˽ӿڼ�ԭ���ɰ��е�cast()�ӿ�
		@param   caster: ʩ����
		@type    caster: Entity

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		if caster.attrIntonateSkill and caster.attrIntonateSkill.getID() == self.getID() or\
			( caster.attrHomingSpell and caster.attrHomingSpell.getType() in Const.INTERRUPTED_BASE_TYPE ) :
			caster.interruptSpell( csstatus.SKILL_NO_MSG )
		Spell.use( self, caster, target )

	def useableCheck( self, caster, target ) :
		if caster.attrIntonateSkill and caster.attrIntonateSkill.getID() == self.getID() or\
			( caster.attrHomingSpell and caster.attrHomingSpell.getType() in Const.INTERRUPTED_BASE_TYPE ) :
			caster.interruptSpell( csstatus.SKILL_NO_MSG )
	
		#�����Ĭ��һ�༼�ܵ�ʩ���ж�
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB

		status = Spell.useableCheck( self, caster, target )
		if status == csstatus.SKILL_GO_ON :
			ownerLevel = caster.level
			dbid = caster.queryTemp( "pcg_conjuring_dbid" )
			if not caster.pcg_petDict.has_key( dbid ) :														# Ҫ�����ĳ��ﲻ����
				status = csstatus.PET_CONJURE_FAIL_NOT_EXIST
			elif caster.pcg_isActPet( dbid ) :																# Ҫ�����ĳ����Ѿ����ڳ���״̬
				status = csstatus.PET_CONJURE_FAIL_CONJURED
			elif ownerLevel < caster.pcg_petDict.get( dbid ).takeLevel:										# ��ҵ��ڳ���������ȼ�Ҳ�����ٻ� by����
				status = csstatus.SKILL_PET_NOT_TAKE_LEVEL
			elif ownerLevel < caster.pcg_petDict.get( dbid ).level - csconst.PET_CONJURE_OVER_LEVEL :		# hyw( 2008.05.23 )
				status = csstatus.PET_CONJURE_FAIL_LESS_LEVEL
		if status != csstatus.SKILL_GO_ON :
			caster.pcg_onConjureResult( 0, None )
			caster.statusMessage( status )																	# ����ٻ�ʧ�ܵ�ԭ��
		# ��ֹ����ԭ���µĲ���ʩ��
		if caster.actionSign( csdefine.ACTION_FORBID_SPELL ):
			return csstatus.SKILL_CANT_CAST
		return status
		
	def cast( self, caster, target ):
		"""
		virtual method.
		��ʽ��һ��Ŀ���λ��ʩ�ţ���з��䣩�������˽ӿ�ͨ��ֱ�ӣ����ӣ���intonate()�������á�

		ע���˽ӿڼ�ԭ���ɰ��е�castSpell()�ӿ�

		@param     caster: ʹ�ü��ܵ�ʵ��
		@type      caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		# �������ܼ��
		caster.delHomingOnCast( self )
		self.setCooldownInIntonateOver( caster )
		# ��������
		self.doRequire_( caster )
		#֪ͨ���пͻ��˲��Ŷ���/����������
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )
		
		# ����ʩ�����֪ͨ����һ���ܴ�����Ŷ(�Ƿ��ܴ����Ѿ���ʩ��û�κι�ϵ��)��
		# �����channel����(δʵ��)��ֻ�еȷ�����������ܵ���
		self.onSkillCastOver_( caster, target )
		
		#��֤�ͻ��˺ͷ������˴����������һ��
		caster.addCastQueue( self, target, 2.0 )

	def onSpellInterrupted( self, caster ):
		"""
		��ʩ�������ʱ��֪ͨ��
		��Ϻ���Ҫ��һЩ����
		"""
		Spell.onSpellInterrupted( self, caster )
		caster.removeTemp( "pcg_conjuring_dbid" )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		dbid = receiver.queryTemp( "pcg_conjuring_dbid" )
		if dbid is None :
			ERROR_MSG( "conjure pet fail, can find pet" )
			return
		position = formulas.getPosition( caster.position, caster.yaw )
		# ����entity��ر�����ײ��ȷ�����Է��ڵ�����
		pos = utils.navpolyToGround( caster.spaceID, position, 5.0, 5.0 )
		receiver.base.pcg_conjurePet( dbid, pos, caster.direction )
