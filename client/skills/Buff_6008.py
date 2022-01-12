# -*- coding: gb18030 -*-
#
# �ƶ�Ѹ�ݿͻ���buff�ű�
# edit by wuxo 2012-8-13


from bwdebug import *
from SpellBase import *
import BigWorld

class Buff_6008( Buff ):
	"""
	"""
	def __init__( self ):
		"""
		��python dict����SkillBase
		"""
		Buff.__init__( self )
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			���������ֵ�����
		@type dict:				Python dict
		"""
		Buff.init( self, dict )

	def cast( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.cast( self, caster, target )
		if caster.id == BigWorld.player().id:
			caster.addBlurEffect()
			if not caster.isMoving():#û���ƶ�
				buffs = caster.attrBuffs
				for buff in buffs:
					skill = buff["skill"]
					if skill.getBuffID() == self.getBuffID():
						index = buff["index"]
						caster.requestRemoveBuff( index )
						return
		caster.setArmCaps()
		
	def end( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		Buff.end( self, caster, target )
		if caster.id == BigWorld.player().id:
			caster.delBlurEffect()
			caster.wasdFlag  = [ False,False,False,False ]
			if caster.physics.velocity.length >0 : #��������ƶ� physics���ٶȿ��ܻ��Ǽӳɵ�
				caster.updateVelocity()
		caster.setArmCaps()	