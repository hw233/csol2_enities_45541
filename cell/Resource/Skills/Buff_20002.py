# -*- coding: gb18030 -*-

import BigWorld
import csconst
import csdefine
import csstatus
from bwdebug import *
from Buff_Normal import Buff_Normal

class Buff_20002( Buff_Normal ):
	"""
	Ǳ��buff
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = ( int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  / 100.0 ) * csconst.FLOAT_ZIP_PERCENT
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )

	def springOnUseMaligSkill( self, caster, skill ):
		"""
		ʹ�ö��Լ��ܱ�����
		"""
		buffID = self.getBuffID()
		caster.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )

	def springOnDamage( self, caster, skill ):
		"""
		�����˺���
		"""
		buffID = self.getBuffID()
		caster.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )

	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч����ʼ�Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		# ʹ�ö��Լ��ܺ󴥷����˺������
		receiver.appendOnUseMaligSkill( buffData[ "skill" ] )
		# �����к�
		receiver.appendVictimHit( buffData[ "skill" ] )
		#CSOL-1239�������ڲ߻�Ҫ��ɾ������ʱע�ͷ�ֹ�Ժ�Ҫ�Ļ���
		## ���ݽ����߲�ͬ�в�ͬ��Ч�����߻���Ϊ���ﲻ�ܱ�����Ӱ��
		#if not receiver.isEntityType( csdefine.ENTITY_TYPE_PET ) and receiver.getClass() == csdefine.CLASS_SWORDMAN:
		#	# ����100%
		#	receiver.double_hit_probability_value += csconst.FLOAT_ZIP_PERCENT
		#	receiver.calcDoubleHitProbability()
		#	receiver.magic_double_hit_probability_value += csconst.FLOAT_ZIP_PERCENT
		#	receiver.calcMagicDoubleHitProbability()
		#	# ������100%
		#	receiver.be_double_hit_probability += csconst.FLOAT_ZIP_PERCENT
		#	receiver.be_magic_double_hit_probability += csconst.FLOAT_ZIP_PERCENT
		# �ƶ��ٶ�-50%
		receiver.move_speed_percent -= self._p1
		receiver.calcMoveSpeed()
		# Ǳ�еȼ�ֵ����
		receiver.sneakLevelAmend += self._p2
		# �����־
		receiver.effectStateInc( csdefine.EFFECT_STATE_PROWL )

	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�����¼��صĴ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		# ʹ�ö��Լ��ܺ󴥷����˺������
		receiver.appendOnUseMaligSkill( buffData[ "skill" ] )
		# �����к�
		receiver.appendVictimHit( buffData[ "skill" ] )
		
		## ���ݽ����߲�ͬ�в�ͬ��Ч�����߻���Ϊ���ﲻ�ܱ�����Ӱ��
		#if not receiver.isEntityType( csdefine.ENTITY_TYPE_PET ) and receiver.getClass() == csdefine.CLASS_SWORDMAN:
		#	# ����100%
		#	receiver.double_hit_probability_value += csconst.FLOAT_ZIP_PERCENT
		#	receiver.calcDoubleHitProbability()
		#	receiver.magic_double_hit_probability_value += csconst.FLOAT_ZIP_PERCENT
		#	receiver.calcMagicDoubleHitProbability()
		#	# ������100%
		#	receiver.be_double_hit_probability += csconst.FLOAT_ZIP_PERCENT
		#	receiver.be_magic_double_hit_probability += csconst.FLOAT_ZIP_PERCENT
		# �ƶ��ٶ�-50%
		receiver.move_speed_percent -= self._p1
		# Ǳ�еȼ�ֵ����
		receiver.sneakLevelAmend += self._p2
		# �����־
		receiver.effectStateInc( csdefine.EFFECT_STATE_PROWL )

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		# ʹ�ö��Լ��ܺ󴥷����˺������
		receiver.removeOnUseMaligSkill( buffData[ "skill" ].getUID() )
		# �����к�
		receiver.removeVictimHit( buffData[ "skill" ].getUID() )
		## ���ݽ����߲�ͬ�в�ͬ��Ч�����߻���Ϊ����Ӧ�ò��ܱ�����Ӱ��
		#
		#if not receiver.isEntityType( csdefine.ENTITY_TYPE_PET ) and receiver.getClass() == csdefine.CLASS_SWORDMAN:
		#	# ����100%
		#	receiver.double_hit_probability_value -= csconst.FLOAT_ZIP_PERCENT
		#	receiver.calcDoubleHitProbability()
		#	receiver.magic_double_hit_probability_value -= csconst.FLOAT_ZIP_PERCENT
		#	receiver.calcMagicDoubleHitProbability()
		#	# ������100%
		#	receiver.be_double_hit_probability -= csconst.FLOAT_ZIP_PERCENT
		#	receiver.be_magic_double_hit_probability -= csconst.FLOAT_ZIP_PERCENT
		# �ƶ��ٶ�50%
		receiver.move_speed_percent += self._p1
		receiver.calcMoveSpeed()
		# Ǳ�еȼ�ֵ����
		receiver.sneakLevelAmend -= self._p2
		# �����־
		receiver.effectStateDec( csdefine.EFFECT_STATE_PROWL )

		buffID = self.getBuffID()
		if receiver.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = receiver.getOwner()
			if owner.etype == "REAL":
				owner.entity.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )
			else:
				owner.entity.remoteCall( "removeAllBuffByBuffID",( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] ))
			#���֮ǰ������״̬��������ԭ
			mode = receiver.queryTemp("Snake_buff", -1)
			if mode != -1:
				receiver.tussleMode = mode
			receiver.removeTemp("Snake_buff")
		elif receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			
			#���Ǳ��Buff�󴥷���������  by ������ 2010-09-28
			receiver.onRemoveBuffProwl()
		
			actPet = receiver.pcg_getActPet()
			if actPet:
				if actPet.etype == "REAL":
					actPet.entity.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )
				else:
					actPet.entity.remoteCall( "removeAllBuffByBuffID", ( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] ) )
			