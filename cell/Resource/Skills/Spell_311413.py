# -*- coding: gb18030 -*-
#
# $Id: Spell_311413.py,v 1.7 2008-07-15 04:06:26 kebiao Exp $

"""
���ܶ���Ʒʩչ����������
"""

from SpellBase import *
from Spell_PhysSkill import Spell_PhysSkill2
import utils
import csstatus
import csdefine
from VehicleHelper import getCurrVehicleID
import ECBExtend

class Spell_311413( Spell_PhysSkill2 ):
	"""
	��� ������ˣ����ٿ���Ŀ�꣬���һ�����˺���8��֮�ڣ�20��֮�ⲻ�ܳ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_PhysSkill2.__init__( self )
		self._triggerBuffInterruptCode = []							# �ü��ܴ�����Щ��־���ж�ĳЩBUFF
		self.config_movespeed = 0
		self.delay_time = 1.0

	def init( self, dict ):
		"""
		��ȡ����
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_PhysSkill2.init( self, dict )
		for val in dict[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )
		if dict[ "param2" ] == "":
			self.config_movespeed = self.getFlySpeed()
		else :
			self.config_movespeed = float( dict[ "param2" ] )
		self.delay_time = float ( dict[ "param3" ] )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		if getCurrVehicleID( caster ):
			return csstatus.SKILL_CANT_USE_ON_VEHICLE
		return Spell_PhysSkill2.useableCheck( self, caster, target )

	def getCastRange( self, caster ):
		"""
		�����ͷž���
		"""
		return self.getRangeMax( caster ) + 5

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
		caster.move_speed = self.config_movespeed
		caster.updateTopSpeed()
		caster.clearBuff( self._triggerBuffInterruptCode ) #ɾ�������������п���ɾ����BUFF
		#֪ͨ���пͻ��˲��Ŷ���/����������
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )
		self.setCooldownInIntonateOver( caster )
		# ��������
		self.doRequire_( caster )
		#��֤�ͻ��˺ͷ������˴����������һ��
		delay = self.calcDelay( caster, target )
		# �ӳ�
		caster.addCastQueue( self, target, delay + 0.35 )
		# ����ʩ�����֪ͨ����һ���ܴ�����Ŷ(�Ƿ��ܴ����Ѿ���ʩ��û�κι�ϵ��)��
		# �����channel����(δʵ��)��ֻ�еȷ�����������ܵ���
		self.onSkillCastOver_( caster, target )

	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		�����ִ�Ŀ��ͨ�档��Ĭ������£��˴�ִ�п�������Ա�Ļ�ȡ��Ȼ�����receive()�������ж�ÿ���������߽��д���
		ע���˽ӿ�Ϊ�ɰ��е�receiveSpell()

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		Spell_PhysSkill2.onArrive( self, caster, target )
		dist = caster.distanceBB( target.getObject() )
		delayTime = dist / caster.move_speed * self.delay_time
		caster.addTimer( delayTime, 0, ECBExtend.CHARGE_SPELL_CBID )
	#	caster.client.onAssaultEnd()    ����ע�͵���Ŀ����ȡ���������˶Գ��ֹͣ���ж�

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		distanceBB = caster.distanceBB( receiver )
	#	if distanceBB > 3.5:       ����ע�͵���Ŀ����ʹ�ü��ܶ����Բ���Ч��
	#		return

		Spell_PhysSkill2.receive( self, caster, receiver )


# $Log: not supported by cvs2svn $
# Revision 1.6  2008/05/28 05:59:47  kebiao
# �޸�BUFF�������ʽ
#
# Revision 1.5  2008/05/27 08:36:02  kebiao
# �����˳��
#
# Revision 1.4  2008/03/04 08:38:55  kebiao
# ������С������ж�
#
# Revision 1.3  2007/12/29 09:07:28  kebiao
# no message
#
# Revision 1.2  2007/12/29 03:48:06  kebiao
# ���ӳ��֧��
#
# Revision 1.1  2007/11/26 08:45:44  kebiao
# �ü���1�ڴ��룬 ��������Ҫ֧��
#
# Revision 1.1  2007/11/24 08:35:30  kebiao
# no message
#