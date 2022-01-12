# -*- coding: gb18030 -*-

#飞翔传送技能服务器脚本


import csdefine
import csstatus
from Spell_BuffNormal import Spell_BuffNormal

BUFF_ID = 299037

class Spell_TrapFlyTeleport( Spell_BuffNormal ):
	def __init__( self ):
		"""
		初始化技能数据
		"""
		Spell_BuffNormal.__init__( self )
		self.modelNum  = [] #坐骑模型列表
		self.isChoosePlayer  = False #是否选择玩家的坐骑
		
	def init( self, data ):
		Spell_BuffNormal.init( self, data )
		if data["param1"] != "":
			self.modelNum  = data["param1"].split(";")
		if data["param2"] != "":
			self.isChoosePlayer = bool( int(data["param2"]) )

	def cast( self, caster, target ):
		"""
		"""
		# 引导技能检测
		caster.delHomingOnCast( self )
		self.setCooldownInIntonateOver( caster )
		# 处理消耗
		self.doRequire_( caster )
		#通知所有客户端播放动作/做其他事情
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )
		
		# 法术施放完毕通知，不一定能打中人哦(是否能打中已经和施法没任何关系了)！
		# 如果是channel法术(未实现)，只有等法术结束后才能调用
		self.onSkillCastOver_( caster, target )
		
		caster.addCastQueue( self, target, 0.5 )
		entity = target.getObject()
		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			entity.setTemp( "FLY_TELEPORT_VEHICLE_INFO", ( [ int(model) for model in self.modelNum ], self.isChoosePlayer ) )
			entity.base.getAllVehicleDatasFromBase()
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		for index, buff in enumerate( receiver.attrBuffs ):
			if int(buff["skill"].getBuffID()) == BUFF_ID:
				return
		receiver.stopMoving()
		receiver.clearBuff( [csdefine.BUFF_INTERRUPT_NONE] ) #中断buff
		self.receiveLinkBuff( caster, receiver )