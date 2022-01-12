# -*- coding:gb18030 -*-

from bwdebug import *
from Spell_BuffNormal import Spell_BuffNormal
import csdefine
import csstatus
import time

class Spell_322486( Spell_BuffNormal ):
	"""
	生机盎然
	
	如果目标存在回春术产生的BUFF，立刻触发buff的剩余治疗效果并结束BUFF，同时按一定比例提高BUFF的收益（法术）
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )
		self.param1 = 0		# 影响的技能，此技能产生的buff才能被影响
		self.param2 = 0		# buff id
		self.param3 = 0		# 提高的比例
		
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
			if buff.getID() / 100000 != self.param1:	# 去掉buff index、去掉技能级别
				continue
			cureHP = int( ( buffData["persistent"] - time.time() ) / buff._loopSpeed * buff._param * ( 1+self.param3 ) )
			if cureHP <= 0:
				return
			receiver.addHP( cureHP )
			receiver.removeBuff( index, [csdefine.BUFF_INTERRUPT_NONE] )
			if caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
				caster.client.onAddRoleHP( receiver.id, cureHP )
			#增加目标是玩家还是宠物或者其他的判断 add by wuxo 2012-5-17
			if caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
				caster.client.onAddRoleHP( receiver.id, cureHP )
				#KILL_HP_TARGET_CURE %s的%s恢复了你%i点生命值。
				#SKILL_TARGET_HP_CURE  你的%s恢复了%s%i点生命值。
				#SKILL_HP_CURE     你的%s恢复了你%i点生命值。
				if receiver.isEntityType(csdefine.ENTITY_TYPE_ROLE):#接受者是玩家
					if caster.id != receiver.id: #给别人加血
						#你的%s恢复了%s%i点生命值。
						caster.statusMessage( csstatus.SKILL_TARGET_HP_CURE, self.getName(), receiver.getName(), cureHP )
						#%s的%s恢复了你%i点生命值。
						receiver.statusMessage( csstatus.SKILL_HP_TARGET_CURE, caster.getName(), self.getName(), cureHP )
					else: #给自己加血
						#你的%s恢复了你%i点生命值。
						caster.statusMessage( csstatus.SKILL_HP_CURE, self.getName(), cureHP )
				elif receiver.isEntityType(csdefine.ENTITY_TYPE_PET): #接受者是宠物
					#SKILL_HP_CURE_PET  你的%s为你的宠物恢复了%i点生命值。
					#SKILL_HP_TARGET_CURE_PET %s的%s为你的宠物恢复了%i点生命值。
					#SKILL_HP_CURE_TARGET_PET  (CB):你的%s为%s的宠物恢复了%i点生命值。
					petOwner = receiver.getOwner().entity
					if petOwner.id == caster.id: #给自己的宠物加血
						#你的%s为你的宠物恢复了%i点生命值。
						caster.statusMessage( csstatus.SKILL_HP_CURE_PET, self.getName(), cureHP )
					else:#给别人的宠物加血
						#你的%s为%s的宠物恢复了%i点生命值。
						caster.statusMessage( csstatus.SKILL_HP_CURE_TARGET_PET, self.getName(), petOwner.getName(), cureHP )
						#%s的%s为你的宠物恢复了%i点生命值。
						receiver.statusMessage( csstatus.SKILL_HP_TARGET_CURE_PET, caster.getName(), self.getName(), cureHP )
				
			break
			