# -*- coding:gb18030 -*-

from bwdebug import *
from Spell_BuffNormal import Spell_BuffNormal
import csdefine
import csstatus
import time

class Spell_322486( Spell_BuffNormal ):
	"""
	������Ȼ
	
	���Ŀ����ڻش���������BUFF�����̴���buff��ʣ������Ч��������BUFF��ͬʱ��һ���������BUFF�����棨������
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )
		self.param1 = 0		# Ӱ��ļ��ܣ��˼��ܲ�����buff���ܱ�Ӱ��
		self.param2 = 0		# buff id
		self.param3 = 0		# ��ߵı���
		
	def init( self, data ):
		"""
		"""
		Spell_BuffNormal.init( self, data )
		self.param1 = int( data[ "param1" ] if len( data[ "param1" ] ) > 0 else 0 )
		self.param2 = int( data[ "param2" ] if len( data[ "param2" ] ) > 0 else 0 )
		self.param3 = int( data[ "param3" ] if len( data[ "param3" ] ) > 0 else 0 ) / 100.0
		
	def receive( self, caster, receiver ):
		"""
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		Spell_BuffNormal.receive( self, caster, receiver )
		buffIndexs = receiver.findBuffsByBuffID( self.param2 )
		if not buffIndexs:
			return
		for index in buffIndexs:
			buffData = receiver.getBuff( index )
			buff = buffData["skill"]
			if buff.getID() / 100000 != self.param1:	# ȥ��buff index��ȥ�����ܼ���
				continue
			cureHP = int( ( buffData["persistent"] - time.time() ) / buff._loopSpeed * buff._param * ( 1+self.param3 ) )
			if cureHP <= 0:
				return
			receiver.addHP( cureHP )
			receiver.removeBuff( index, [csdefine.BUFF_INTERRUPT_NONE] )
			if caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
				caster.client.onAddRoleHP( receiver.id, cureHP )
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
				
			break
			