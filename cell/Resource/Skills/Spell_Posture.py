# -*- coding:gb18030 -*-

import csstatus
from Spell_BuffNormal import Spell_BuffNormal
from interface.State import State
from bwdebug import *
import csdefine
from Love3 import g_skills
import copy

class Spell_Posture( Spell_BuffNormal ):
	"""
	��̬���ܣ��л���ĳ����̬
	
	����Ѿ��ڵ�ǰ��̬���޷�ʹ�ô˼���
	�����Ѿ��ڵ�ǰ��̬�����ʹ�óɹ����ܽ���cd��������൱��һ��ʱ�����޷��л�����̬
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )
		self.posture = 0		# �˼��ܶ�Ӧ����̬������Ѿ����ڴ���̬��������ʹ�ô˼���
		
	def init( self, data ):
		"""
		"""
		Spell_BuffNormal.init( self, data )
		self.posture = int( data["param1"] if len( data["param1"] ) > 0 else 0 )
		
	def useableCheck( self, caster, target ):
		"""
		"""
		entity = target.getObject()
		if entity is None or not isinstance( entity, State ):
			ERROR_MSG( "entity is none or not an inheritance of State object." )
			return csstatus.SKILL_MISS_TARGET
		if entity.isPosture( self.posture ):
			return csstatus.SKILL_ALREDAY_IN_POSTURE
			
		return Spell_BuffNormal.useableCheck( self, caster, target )
		
	def attach( self, ownerEntity ):
		"""
		"""
		if ownerEntity.getPosture() == csdefine.ENTITY_POSTURE_NONE and not ownerEntity.hasSkill( self.getID() ):	# ���ķ����һ�ûѧϰ�ü��ܵ�ʱ��
			for buffData in self._buffLink:
				buff = buffData.getBuff()
				buffID = buff.getBuffID()
				newBuff = { "skill" : buff, "persistent" : buff.calculateTime( ownerEntity ), "currTick" : 0, "caster" : ownerEntity.id, "state" : 0, "index" : 0, "sourceType" : 0, "isNotIcon" : True }
				ownerEntity.addBuff( newBuff )
			return
		for buffData in self._buffLink:
			buff = buffData.getBuff()
			buffID = buff.getBuffID()
			for index, ownerBuff in enumerate( ownerEntity.attrBuffs ):
				if ownerBuff["skill"].getBuffID() == buffID:
					newBuff = { "skill" : buff, "persistent" : buff.calculateTime( ownerEntity ), "currTick" : 0, "caster" : ownerEntity.id, "state" : 0, "index" : 0, "sourceType" : 0, "isNotIcon" : True }
					ownerEntity.removeBuff( index, [ csdefine.BUFF_INTERRUPT_NONE ] )
					ownerEntity.addBuff( newBuff )
			
	def detach( self, ownerEntity ):
		"""
		"""
		if ownerEntity.queryTemp( "roleUpdateSkill", False ):
			for buffData in self._buffLink:
				buffID = buffData.getBuff().getBuffID()
				if ownerEntity.findBuffByBuffID( buffID ):			# �ҵ�������ϵ�buff
					ownerEntity.removeBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )


class Spell_PostureInFight( Spell_BuffNormal ):
	"""
	��̬���ܣ�������̬�������л�
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )
		self.connectBuff = {}
		
	def init( self, data ):
		"""
		"""
		Spell_BuffNormal.init( self, data )
		if data["param1"] != "":
			param2 = data["param1"].split("|")
			for buffIDs in param2:
				buffIDL = buffIDs.split(";")
				self.connectBuff[ int(buffIDL[0])] = ( int( buffIDL[1] ), int( buffIDL[2] ) )
		
		
	def useableCheck( self, caster, target ):
		"""
		"""
		entity = target.getObject()
		if entity is None or not isinstance( entity, State ):
			ERROR_MSG( "entity is none or not an inheritance of State object." )
			return csstatus.SKILL_MISS_TARGET
		return Spell_BuffNormal.useableCheck( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		connectBuff = copy.deepcopy( self.connectBuff )
		for key in self.connectBuff:
			for index, ownerBuff in enumerate( caster.attrBuffs ):
				if ownerBuff["skill"].getBuffID() == key:
					caster.removeBuff( index, [ csdefine.BUFF_INTERRUPT_NONE ] )
					del connectBuff[ key ]
					break
		if len( connectBuff ) == 2 or len( connectBuff ) == 0 :
			return
		#�Ҷ�Ӧ�ȼ�����̬����
		pBuffID = connectBuff.keys()[0]
		skillID = connectBuff[ pBuffID ][1]
		cBuffID = connectBuff[ pBuffID ][0]
		for tempSkillID in caster.attrSkillBox:	# ������ڼ������skillID��ͬ�༼��
			if tempSkillID / 1000 == skillID / 1000 and skillID % 1000 <= tempSkillID % 1000:
				skillID = tempSkillID
		
		#�Ӷ�Ӧ�ȼ�����̬buff
		connectL = g_skills[ skillID ]._buffLink
		for buffData in connectL:
			buff = buffData.getBuff()
			buffID = buff.getBuffID()
			if buffID == pBuffID:
				buff.receive( caster, caster )
				break	
			
		#�Ӹ���buff	
		for buffData in self._buffLink:
			buff = buffData.getBuff()
			buffID = buff.getBuffID()
			if buffID == cBuffID:
				buff.receive( caster, caster )
				break	
		
		