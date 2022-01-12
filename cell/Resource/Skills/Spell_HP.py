# -*- coding: gb18030 -*-
#
# $Id: Spell_HP.py,v 1.1 2008-08-30 10:01:12 wangshufeng Exp $

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

import Const
from SpellBase import *
from Spell_Magic import Spell_Magic


class Spell_HP( Spell_Magic ):
	"""
	���ƣ����߷����������̣�ֱ�ӻ�������е�����Ч���ļ��ܴ���
	���ܼ�Ѫ��=X%��ɫ����ֵ����+�̶�Y��
	
	param1Ϊ�̶���yֵ
	param2Ϊ�������ޱ�������10���ʾ10%
	"""
	def __init__( self ):
		"""
		"""
		Spell_Magic.__init__( self )
		self._p1 = 0
		
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		self._p1 = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 	
		self._p2 = int( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else 0 ) / 100.0
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		cureHP = int( caster.MP_Max * self._p2 + self._p1 )
		changeHP = receiver.addHP( cureHP )
		caster.doCasterOnCure( receiver, changeHP )		# ����Ŀ��ʱ����
		receiver.doReceiverOnCure( caster, changeHP )   	# ������ʱ����
		
		#����Ŀ������һ��ǳ�������������ж� add by wuxo 2012-5-17
		if caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
			caster.client.onAddRoleHP( receiver.id, cureHP )
			#KILL_HP_TARGET_CURE %s��%s�ָ�����%i������ֵ��
			#SKILL_TARGET_HP_CURE  ���%s�ָ���%s%i������ֵ��
			#SKILL_HP_CURE     ���%s�ָ�����%i������ֵ��
			if receiver.isEntityType(csdefine.ENTITY_TYPE_ROLE):#�����������
				if caster.id != receiver.id: #�����˼�Ѫ
					#���%s�ָ���%s%i������ֵ��
					caster.statusMessage( csstatus.SKILL_TARGET_HP_CURE, self.getName(), receiver.getName(), cureHP )
					#%s��%s�ָ�����%i������ֵ��
					receiver.statusMessage( csstatus.SKILL_HP_TARGET_CURE, caster.getName(), self.getName(), cureHP )
				else: #���Լ���Ѫ
					#���%s�ָ�����%i������ֵ��
					caster.statusMessage( csstatus.SKILL_HP_CURE, self.getName(), cureHP )
			elif receiver.isEntityType(csdefine.ENTITY_TYPE_PET): #�������ǳ���
				#SKILL_HP_CURE_PET  ���%sΪ��ĳ���ָ���%i������ֵ��
				#SKILL_HP_TARGET_CURE_PET %s��%sΪ��ĳ���ָ���%i������ֵ��
				#SKILL_HP_CURE_TARGET_PET  (CB):���%sΪ%s�ĳ���ָ���%i������ֵ��
				petOwner = receiver.getOwner().entity
				if petOwner.id == caster.id: #���Լ��ĳ����Ѫ
					#���%sΪ��ĳ���ָ���%i������ֵ��
					caster.statusMessage( csstatus.SKILL_HP_CURE_PET, self.getName(), cureHP )
				else:#�����˵ĳ����Ѫ
					#���%sΪ%s�ĳ���ָ���%i������ֵ��
					caster.statusMessage( csstatus.SKILL_HP_CURE_TARGET_PET, self.getName(), petOwner.getName(), cureHP )
					#%s��%sΪ��ĳ���ָ���%i������ֵ��
					receiver.statusMessage( csstatus.SKILL_HP_TARGET_CURE_PET, caster.getName(), self.getName(), cureHP )
		
		
		
		
	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		�����ִ�Ŀ��ͨ�档��Ĭ������£��˴�ִ�п�������Ա�Ļ�ȡ��Ȼ�����receive()�������ж�ÿ���������߽��д���
		ע���˽ӿ�Ϊ�ɰ��е�receiveSpell()

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		
		�̳���ȥ�����ڹ㷶Χ����Ŀ��Ĵ����Ա����Ѫ�俪ս������ by ����
		"""
		# ��ȡ����������
		receivers = self.getReceivers( caster, target )
		# ������û�л���Ŀ�꣬���ܹ�������Ŀ�꣬��������
		for receiver in receivers:
			# ����ս������ģ������ֵ�,��ģ���ֵ��ֵ�п��ܱ�����BUFF���ܸı��Ӱ��ս����ֵ
			# ��������֮ǰ�����Ĺ���
			self.onReceiveBefore_( caster, receiver )
			if receiver.state != csdefine.ENTITY_STATE_DEAD:
				self.receive( caster, receiver )
			# �Խ����߶��ԣ����ܼ����Ƿ����У����ܼ��ܹ�������
			# ��ӳ��
			self.receiveEnemy( caster, receiver )
			# ��recevei֮����ܽ�ɫ�Ѿ�������
			if caster.isDestroyed:
				return


		if not caster.isDestroyed:
			caster.onSkillArrive( self, receivers )
		
#$Log: not supported by cvs2svn $
#
#