# -*- coding: gb18030 -*-

#���贫�ͼ��ܷ������ű�


import csdefine
import csstatus
from Spell_BuffNormal import Spell_BuffNormal

BUFF_ID = 299037

class Spell_TrapFlyTeleport( Spell_BuffNormal ):
	def __init__( self ):
		"""
		��ʼ����������
		"""
		Spell_BuffNormal.__init__( self )
		self.modelNum  = [] #����ģ���б�
		self.isChoosePlayer  = False #�Ƿ�ѡ����ҵ�����
		
	def init( self, data ):
		Spell_BuffNormal.init( self, data )
		if data["param1"] != "":
			self.modelNum  = data["param1"].split(";")
		if data["param2"] != "":
			self.isChoosePlayer = bool( int(data["param2"]) )

	def cast( self, caster, target ):
		"""
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
		
		caster.addCastQueue( self, target, 0.5 )
		entity = target.getObject()
		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			entity.setTemp( "FLY_TELEPORT_VEHICLE_INFO", ( [ int(model) for model in self.modelNum ], self.isChoosePlayer ) )
			entity.base.getAllVehicleDatasFromBase()
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		for index, buff in enumerate( receiver.attrBuffs ):
			if int(buff["skill"].getBuffID()) == BUFF_ID:
				return
		receiver.stopMoving()
		receiver.clearBuff( [csdefine.BUFF_INTERRUPT_NONE] ) #�ж�buff
		self.receiveLinkBuff( caster, receiver )