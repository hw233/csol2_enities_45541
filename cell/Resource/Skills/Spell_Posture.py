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
	姿态技能，切换到某个姿态
	
	如果已经在当前姿态则无法使用此技能
	避免已经在当前姿态，玩家使用成功技能进入cd导致玩家相当长一段时间内无法切换此姿态
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )
		self.posture = 0		# 此技能对应的姿态，如果已经处于此姿态则不允许再使用此技能
		
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
		if ownerEntity.getPosture() == csdefine.ENTITY_POSTURE_NONE and not ownerEntity.hasSkill( self.getID() ):	# 无心法并且还没学习该技能的时候
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
				if ownerEntity.findBuffByBuffID( buffID ):			# 找到玩家身上的buff
					ownerEntity.removeBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )


class Spell_PostureInFight( Spell_BuffNormal ):
	"""
	姿态技能，两个姿态间来回切换
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
		法术到达所要做的事情
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
		#找对应等级的姿态技能
		pBuffID = connectBuff.keys()[0]
		skillID = connectBuff[ pBuffID ][1]
		cBuffID = connectBuff[ pBuffID ][0]
		for tempSkillID in caster.attrSkillBox:	# 如果存在级别高于skillID的同类技能
			if tempSkillID / 1000 == skillID / 1000 and skillID % 1000 <= tempSkillID % 1000:
				skillID = tempSkillID
		
		#加对应等级的姿态buff
		connectL = g_skills[ skillID ]._buffLink
		for buffData in connectL:
			buff = buffData.getBuff()
			buffID = buff.getBuffID()
			if buffID == pBuffID:
				buff.receive( caster, caster )
				break	
			
		#加附带buff	
		for buffData in self._buffLink:
			buff = buffData.getBuff()
			buffID = buff.getBuffID()
			if buffID == cBuffID:
				buff.receive( caster, caster )
				break	
		
		