# -*- coding: gb18030 -*-
#
# $Id: CombatSpell.py,v 1.37 2008-08-11 06:01:33 kebiao Exp $

"""
������
"""

import Language
import csdefine
import csstatus
from bwdebug import *
from csdefine import *
from Spell import Spell,BuffData
from SkillAttack import SkillAttack
import Const
import random
import csconst
import SkillMessage

class CombatSpell( Spell, SkillAttack ):
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		SkillAttack.__init__( self )

	def init( self, dictDat ):
		"""
		��ȡ��������
		"""
		Spell.init( self, dictDat )
		SkillAttack.init( self, dictDat )

	def onReceiveBefore_( self, caster, receiver ):
		"""
		virtual method = 0.
		���ܷ���֮ǰ��Ҫ��������
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		pass

	def onHit( self, damageType, caster, receiver ):
		"""
		���������к�ص� by ����
		"""
		pass

	def persentDamage( self, caster, receiver, damageType, damage ):
		"""
		virtual method.
		�������߳��������˺�
		ͨ��������Щ�����Ҫ���� ��Ҫ���ݶ�ĳentity���������˺� �������������Ӱ��
		"""
		# �˺����� �����˺��Ǹ�Ŀ��ģ� �����˺��Ǹ��Լ���
		
		finiDamage = damage
		shareDamage = 0
		if caster.damage_share_percent > 0:
			finiDamage = max( 1, damage * ( 1 - ( caster.damage_share_percent / csconst.FLOAT_ZIP_PERCENT ) ) )
			shareDamage = damage - finiDamage

		if shareDamage > 0:
			caster.receiveSpell( receiver.id, self.getID(), damageType, shareDamage, 0 )
			caster.receiveDamage( receiver.id, self.getID(), damageType, shareDamage )

		receiver.receiveSpell( caster.id, self.getID(), damageType, finiDamage, 0 )
		receiver.receiveDamage( caster.id, self.getID(), damageType, finiDamage )

		# �п�����Զ�̼��ܣ� ����Ŀ���ʩ����������������Ѿ������ˡ�
		if not caster.isDestroyed:
			caster.doAttackerAfterDamage( self, receiver, finiDamage )
		# �п�����Զ�̼��ܣ�����Ŀ��֮ǰ��Ŀ����Ѿ�������
		if not receiver.isDestroyed:
			receiver.doVictimOnDamage( self, caster, finiDamage )
			receiver.reboundDamage( caster.id, self.getID(), finiDamage, damageType )

	def isDoubleHit( self, caster, receiver ):
		"""
		virtual method.
		�жϹ������Ƿ񱬻�
		return type:bool
		"""
		return random.random() < ( caster.double_hit_probability + ( receiver.be_double_hit_probability - receiver.be_double_hit_probability_reduce ) / csconst.FLOAT_ZIP_PERCENT )

	def isResistHit( self, caster, receiver ):
		"""
		virtual method.
		�жϱ��������Ƿ��м�
		return type:bool
		"""
		return random.random() < receiver.resist_hit_probability

	def use( self, caster, target ):
		"""
		virtual method.
		����� target/position ʩչһ���������κη�����ʩ������ɴ˽���
		dstEntity��position�ǿ�ѡ�ģ����õĲ�����None���棬���忴���������Ƕ�Ŀ�껹��λ�ã�һ��˷���������client����ͳһ�ӿں���ת������
		Ĭ��ɶ��������ֱ�ӷ��ء�
		ע���˽ӿڼ�ԭ���ɰ��е�cast()�ӿ�
		@param   caster: ʩ����
		@type    caster: Entity

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		caster.doOnUseSkill( self )	# ��������ʹ��ʱ���б� ������������ ����ʱ�� �� XX ���ĵĸı�
		Spell.use( self, caster, target )

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

		# ��ȡ����������
		receivers = self.getReceivers( caster, target )
		# ������û�л���Ŀ�꣬���ܹ�������Ŀ�꣬��������
		caster.equipAbrasion( 100.0 )

		for receiver in receivers:
			# ��������֮ǰ�����Ĺ���
			receiver.clearBuff( self._triggerBuffInterruptCode )
			self.onReceiveBefore_( caster, receiver )
			self.receive( caster, receiver )
			# �Խ����߶��ԣ����ܼ����Ƿ����У����ܼ��ܹ�������
			# ��ӳ��
			self.receiveEnemy( caster, receiver )
			# ��receive֮����ܽ�ɫ�Ѿ�������
			if caster.isDestroyed:
				return

		# ���Լ���ʹ�ô���
		caster.doOnUseMaligSkill( self )
		if not caster.isDestroyed:
			caster.onSkillArrive( self, receivers )

	def onMiss( self, damageType, caster, receiver ):
		"""
		����δ����
		"""
		# ���㿪�˲���������û���㣬��˳�����п��ܴ��ڵģ���Ҫ֪ͨ�ܵ�0���˺�
		receiver.receiveSpell( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0, 0 )
		receiver.receiveDamage( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0 )
		caster.doAttackerOnDodge( receiver, damageType )
		receiver.doVictimOnDodge( caster, damageType )
		
	def calReduceDamage( self,caster, receiver ):
		"""
		����ʵ�ʼ�����
		�ȼ����� = (�����ȼ�-�ط��ȼ�)*4% 
		ʵ�ʼ���=MAX(�ط���������-�����Ƶ�����-�ȼ�����,0) 
		"""
		disLevel = 0
		if caster.level  > receiver.level:
			disLevel = ( caster.level - receiver.level ) * 0.04
		
		return max( receiver.reduce_role_damage - caster.add_role_damage - disLevel, 0.0 )
		
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if receiver.isDestroyed:
			return

		damageType = self._damageType

		# ����������
		hit = self.calcHitProbability( caster, receiver )
		if receiver.effect_state & csdefine.EFFECT_STATE_INVINCIBILITY > 0 or not random.random() < hit:
			self.onMiss( damageType, caster, receiver )				# ������δ����
			return

		# ִ�����к����Ϊ
		caster.doAttackerOnHit( receiver, damageType )				# �����ߴ���
		receiver.doVictimOnHit( caster, damageType )				# �ܻ��ߴ���
		self.onHit( damageType, caster, receiver )					# ���������к�ص�

		if caster.queryTemp( "ELEM_ATTACK_EFFECT", "" ):	# �����Ԫ�ع���Ч��������������˺���������
			self.__receiveElemDamage( caster, receiver )
			return

		# ���㼼�ܹ������ͼ���ֱ���˺�
		skillDamage = self.calcSkillHitStrength( caster,receiver, 0, 0 )
		attackdamage = self.calcDamage( caster, receiver, skillDamage )
		# ����Ԫ���˺� Ԫ���˺��б� ������ֱ�Ϊ �����ױ�4��Ԫ�����������˺�
		elemDamageList = self.calcElemDamage( caster, receiver )

		# �����ܻ�װ���˺�
		equipmentDamage = int( skillDamage - attackdamage )
		receiver.equipDamage( equipmentDamage )

		# �ж��Ƿ񱬻�
		if self.isDoubleHit( caster, receiver ):
			damageType |= csdefine.DAMAGE_TYPE_FLAG_DOUBLE
			dm = self.calcDoubleMultiple( caster )
			# ��ͨ�˺�����
			attackdamage *= dm
			# Ԫ�ر���
			elemDamageList = [ x * dm for x in elemDamageList ]
			# ִ�гɹ����������Ϊ
			caster.doAttackerOnDoubleHit( receiver, damageType )	# �����ߴ���
			receiver.doVictimOnDoubleHit( caster, damageType )   	# �ܻ��ߴ���

		# ����˴ι������м� ִ�гɹ��мܺ����Ϊ
		if self.isResistHit( caster, receiver ):
			caster.doAttackerOnResistHit( receiver, damageType )	# �����ߴ���
			receiver.doVictimOnResistHit( caster, damageType )   	# �ܻ��ߴ���
			attackdamage -= attackdamage * receiver.resist_hit_derate
			damageType |= csdefine.DAMAGE_TYPE_RESIST_HIT

		# �˺�����  ��Ϊ�������֮���������ܻ�ο��˴ε�������������˺����Դ˽ӿڲ��ܷŵ�receiveDamage��
		attackdamage = self.calcDamageScissor( caster, receiver, attackdamage )

		# Ԫ���˺�����
		self.calcElemDamageDeep( receiver, elemDamageList )

		# Ԫ���˺�����
		self.calcElemDamageScissor( receiver, elemDamageList )

		# ����ԭʼ�����˺�
		basedamage = attackdamage + elemDamageList[0] + elemDamageList[1] + elemDamageList[2] + elemDamageList[3]

		# �������� ��Ϊ�������֮���������ܻ�ο��˴ε�������������˺����Դ˽ӿڲ��ܷŵ�receiveDamage��
		finiDamage = self.calcShieldSuck( caster, receiver, attackdamage, self._damageType, elemDamageList )

		# ����Ԫ���˺�
		finiDamage_ss = finiDamage + elemDamageList[0] + elemDamageList[1] + elemDamageList[2] + elemDamageList[3]

		# ��ʾ�������ֿ����˺�
		if basedamage - finiDamage_ss > 0:
			SkillMessage.spell_DamageSuck( caster, receiver, int( basedamage - finiDamage_ss  ) )
		
		#�������С��Ƶд�����ʵ�ʼ��� 
		reRate = self.calReduceDamage( caster, receiver )
		rm =  1 - reRate
		finiDamage *= rm
		elemDamageList = [ x * rm for x in elemDamageList ]
		
		finiDamage +=  elemDamageList[0] + elemDamageList[1] + elemDamageList[2] + elemDamageList[3]
		
		# �������ҵȼ������ɵ��˺��䶯 by����
		finiDamage = self.damageWithLevelWave( caster, receiver, finiDamage )
		
		# �����ֻ����˺� ����Ҳ�����1���˺�
		self.persentDamage( caster, receiver, damageType, max( 1, int( finiDamage ) ) )
		self.receiveLinkBuff( caster, receiver )					# ���ն����CombatSpellЧ����ͨ����buff(������ڵĻ�)

	def __receiveElemDamage( self, caster, receiver ):
		"""
		Ԫ�ع���Ч���˺�����
		"""
		damageType = self._damageType

		# ���㼼�ܹ������ͼ���ֱ���˺�
		skillDamage = self.calcSkillHitStrength( caster,receiver, 0, 0 )
		attackdamage = self.calcDamage( caster, receiver, skillDamage )

		# �����ܻ�װ���˺�
		equipmentDamage = int( skillDamage - attackdamage )
		receiver.equipDamage( equipmentDamage )

		# ����˴ι������м� ִ�гɹ��мܺ����Ϊ
		if self.isResistHit( caster, receiver ):
			caster.doAttackerOnResistHit( receiver, damageType )	# �����ߴ���
			receiver.doVictimOnResistHit( caster, damageType )   	# �ܻ��ߴ���
			attackdamage -= attackdamage * receiver.resist_hit_derate
			damageType |= csdefine.DAMAGE_TYPE_RESIST_HIT

		# �˺�����
		attackdamage = self.calcDamageScissor( caster, receiver, attackdamage )

		# ����Ԫ���˺� Ԫ���˺��б� ������ֱ�Ϊ �����ױ�4��Ԫ�����������˺�
		elemDamageList = self.calcElemDamage( caster, receiver, attackdamage )
		attackdamage = 0	# ��ͨ�˺���Ϊ0

		# �ж��Ƿ񱬻�
		if self.isDoubleHit( caster, receiver ):
			damageType |= csdefine.DAMAGE_TYPE_FLAG_DOUBLE
			dm = self.calcDoubleMultiple( caster )
			# ��ͨ�˺�����
			attackdamage *= dm
			# Ԫ�ر���
			elemDamageList = [ x * dm for x in elemDamageList ]
			# ִ�гɹ����������Ϊ
			caster.doAttackerOnDoubleHit( receiver, damageType )	# �����ߴ���
			receiver.doVictimOnDoubleHit( caster, damageType )   	# �ܻ��ߴ���

		# Ԫ���˺�����
		self.calcElemDamageDeep( receiver, elemDamageList )

		# Ԫ���˺�����
		self.calcElemDamageScissor( receiver, elemDamageList )

		# ����ԭʼ�����˺�
		basedamage = attackdamage + elemDamageList[0] + elemDamageList[1] + elemDamageList[2] + elemDamageList[3]

		# �������� ��Ϊ�������֮���������ܻ�ο��˴ε�������������˺����Դ˽ӿڲ��ܷŵ�receiveDamage��
		finiDamage = self.calcShieldSuck( caster, receiver, attackdamage, self._damageType, elemDamageList )

		# ����Ԫ���˺�
		finiDamage_ss = finiDamage + elemDamageList[0] + elemDamageList[1] + elemDamageList[2] + elemDamageList[3]

		# ��ʾ�������ֿ����˺�
		if basedamage - finiDamage_ss > 0:
			SkillMessage.spell_DamageSuck( caster, receiver, int( basedamage - finiDamage_ss  ) )

		#�������С��Ƶд�����ʵ�ʼ��� 
		reRate = self.calReduceDamage( caster, receiver )
		rm =  1 - reRate
		finiDamage *= rm
		elemDamageList = [ x * rm for x in elemDamageList ]

		finiDamage +=  elemDamageList[0] + elemDamageList[1] + elemDamageList[2] + elemDamageList[3]

		# �������ҵȼ������ɵ��˺��䶯 by����
		finiDamage = self.damageWithLevelWave( caster, receiver, finiDamage )

		# �����ֻ����˺� ����Ҳ�����1���˺�
		self.persentDamage( caster, receiver, damageType, max( 1, int( finiDamage ) ) )
		self.receiveLinkBuff( caster, receiver )					# ���ն����CombatSpellЧ����ͨ����buff(������ڵĻ�)

	def damageWithLevelWave( self, caster, receiver, attackdamage ):
		"""
		�������ҵȼ������ɵ��˺��䶯 by����
		"""
		if caster.getEntityType() != csdefine.ENTITY_TYPE_MONSTER or receiver.getEntityType() != csdefine.ENTITY_TYPE_ROLE:
			return attackdamage

		levelWave = caster.level - receiver.level

		if levelWave < 4:
			return attackdamage
		elif levelWave > 13:
			return attackdamage * 2
		else:
			return attackdamage * ( 1 + ( levelWave - 3 ) / 10.0 )


#
# $Log: not supported by cvs2svn $
# Revision 1.36  2008/07/28 03:17:12  kebiao
# �����мܼ��˹�ʽ
#
# Revision 1.35  2008/07/04 03:51:05  kebiao
# ��Ч��״̬��ʵ���Ż�
#
# Revision 1.34  2008/07/03 02:49:02  kebiao
# �ı� ˯�� �����Ч����ʵ��
#
# Revision 1.33  2008/07/01 06:17:04  zhangyuxing
# ȥ��װ����ļ�����ʱ������Ϣ
#
# Revision 1.32  2008/06/26 00:55:32  zhangyuxing
# ���룺���¼����;ö����ķ�ʽ
#
# Revision 1.31  2008/06/19 04:08:17  kebiao
# ǿ�ƶ����˸����ͼ���Ϊ����
#
# Revision 1.30  2008/06/04 01:17:06  kebiao
# ����BUFF�ͷ�λ��
#
# Revision 1.29  2008/05/28 06:35:33  kebiao
# �޸Ĺ���Ŀ�� ��Ŀ��û�����ܵ�������������1���˺�
#
# Revision 1.28  2008/04/23 00:50:32  kebiao
# ���ӹ�����δ���лص�
#
# Revision 1.27  2008/04/10 04:07:51  kebiao
# ��Ϊ�ڽ����˺�֮ǰ֪ͨ�ͻ��˽��ܼ��ܴ���
#
# Revision 1.26  2008/04/10 03:51:50  kebiao
# ��Ϊ�ڽ����˺�֮ǰ֪ͨ�ͻ��˽��ܼ��ܴ���
#
# Revision 1.25  2008/04/10 03:27:31  kebiao
# modify to receiveSpell pertinent.
#
# Revision 1.24  2008/03/31 09:04:33  kebiao
# �޸�receiveDamage��֪ͨ�ͻ��˽���ĳ���ܽ���ֿ�
# ����ͨ��receiveSpell֪ͨ�ͻ���ȥ���֣�֧�ָ����ܲ�ͬ�ı���
#
# Revision 1.23  2008/02/27 07:15:33  kebiao
# ���ִ����б�����damageType
#
# Revision 1.22  2008/02/27 06:52:20  kebiao
# doAttackerOnHit ����damageType
#
# Revision 1.21  2008/02/25 09:26:34  kebiao
# �޸��˺��������� �� ���ܼ������
#
# Revision 1.20  2008/02/13 08:39:47  kebiao
# �޸Ļ��ܼ��������λ��
#
# Revision 1.19  2008/01/30 07:22:13  kebiao
# �޸��˺������Ĵ���λ��
#
# Revision 1.18  2008/01/29 01:27:27  kebiao
# ���������˺����͵ı�־
#
# Revision 1.17  2008/01/15 07:22:33  kebiao
# �޸ĳɹ����к�ִ�����BUFF�Ĳ���
#
# Revision 1.16  2007/12/25 03:10:24  kebiao
# �����޵��ж�
#
# Revision 1.15  2007/12/21 09:00:31  kebiao
# ���ע��
#
# Revision 1.14  2007/12/18 04:15:18  kebiao
# ����onReceiveBefore����λ��
#
# Revision 1.13  2007/11/30 05:50:42  kebiao
# �����˺���������
#
# Revision 1.12  2007/11/28 01:44:02  kebiao
# �����ṹ
#
# Revision 1.11  2007/11/27 02:08:27  kebiao
# �޸�ս������
#
# Revision 1.10  2007/11/26 08:21:12  kebiao
# ADD:persentDamage����
#
# Revision 1.9  2007/11/24 06:58:22  kebiao
# �������ܹ�ϵ
#
# Revision 1.8  2007/11/23 02:00:28  kebiao
# ����һ���˺����̲�������˺�֧��
#
# Revision 1.7  2007/11/20 08:19:26  kebiao
# ս��ϵͳ��2�׶ε���
#
# Revision 1.6  2007/11/01 03:21:55  kebiao
# ȥ������ʱ��
#
# Revision 1.5  2007/10/26 07:08:51  kebiao
# ����ȫ�µĲ߻�ս��ϵͳ������
#
# Revision 1.4  2007/08/30 08:00:39  kebiao
# add:getMaxLevel
#
# Revision 1.3  2007/08/16 02:34:30  yangkai
# ���ݲ߻�����װ���;�ĥ�����
# �����Ƿ�����Ŀ�궼ĥ���;�
# ĥ���;úͼ��������й�
# װ���;�ĥ������� CombatSpell::onArrive()
#
# Revision 1.2  2007/08/15 09:04:25  kebiao
# �޸Ľӿ�
#
# Revision 1.1  2007/08/15 04:23:06  kebiao
# �����Լ���
#
#
#