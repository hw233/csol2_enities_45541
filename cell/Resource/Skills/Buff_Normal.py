# -*- coding: gb18030 -*-
#
# $Id: Buff_Normal.py,v 1.23 2008-09-04 06:14:35 kebiao Exp $

"""
���������ࡣ
"""

from bwdebug import *
from SpellBase.Buff import Buff
from SpellBase.SkillAttack import SkillAttack
import BigWorld
import csconst
import csstatus
import csdefine
from Resource.SkillLoader import g_buffLimit


class Buff_Normal( Buff, SkillAttack ):
	"""
		���ܵĳ�����Ч��
		����"Buff"�����"Buff_"��ͷ
		ע������Ϊ�ɰ��е�Condition��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff.__init__( self )
		SkillAttack.__init__( self )
		self._15SecondRuleTimeval = 15.0 # buff15������е�ʱ��ȡֵ BUFF����ʱ�����15 ��15�� ���� ������ʱ����
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff.init( self, dict )
		SkillAttack.init( self, dict )
		if self._persistent < 15.0:
			self._15SecondRuleTimeval = self._persistent
			
	def _replaceLowLvBuff( self, caster, receiver, newBuff, buffs ):
		"""
		Buff �� �滻������  ��buffs���滻��ͼ����BUFF
		@param receiver: �ܻ���
		@type  receiver: Entity
		@param newBuff: ��BUFF������
		@type  newBuff: BUFF
		@param buffs: ׼�������жϵ�buff�����б�
		"""
		lowBuffIdx = buffs[ 0 ]
		#��һ�� ��buffs�ҳ����Լ�����ͻ��ߵ����Լ������BUFF
		for bIndex in buffs:
			if receiver.getBuff( bIndex )[ "skill" ].getLevel() <= receiver.getBuff( lowBuffIdx )[ "skill" ].getLevel():
				lowBuffIdx = bIndex

		#�ҳ���ͼ�������滻
		if self.getLevel() >= receiver.getBuff( lowBuffIdx )[ "skill" ].getLevel():
			receiver.setTemp( "SAME_TYPE_BUFF_REPLACE", True )
			receiver.removeBuff( lowBuffIdx, [ csdefine.BUFF_INTERRUPT_NONE ] )
			receiver.setTemp( "SAME_TYPE_BUFF_REPLACE", False )
			receiver.addBuff( newBuff )
		else:
			#caster.statusMessage( csstatus.SKILL_ADDBUFF_FAIL_LOW_LV )#���ʧ��
			return
		
	def _addBuffToSameType( self, receiver, newBuff ):
		"""
		��ͬһ��BUFF�����һ����BUFF �������̹���
		@param receiver: �ܻ���
		@type  receiver: Entity
		@param newBuff: ��BUFF������
		@type  newBuff: BUFF
		"""
		# ��ȡ����ͬ����ͬ���ʵ�BUFF��DEBUFF
		buffs = receiver.getBuffIndexsByType( self.getBuffType(), self._effectState ) #��ȡ���е�BUFF ���� DEBUFF
		# ��ѯ��BUFF����Ӧ�������ܹ�ͬʱ���ڵ������Ƿ񳬹�  BUFF����   XXX���ͣ�(buff)3/(debuff)4��
		buffcount = len( buffs )
		receiver.setTemp( "SAME_TYPE_BUFF_REPLACE", True )
		if buffcount > 0:
			if buffcount >= g_buffLimit.getBuffLimit( self.getBuffType(), self._effectState ):
				receiver.removeBuff( receiver.findRemainTimeMinByIndexs( buffs ), [csdefine.BUFF_INTERRUPT_NONE] )
			else:
				# ��ȡ����ͬ���ʣ�����ͬ���ͣ���BUFF��DEBUFF �Ƿ�����
				buffs = receiver.getBuffIndexsByEffectType( self._effectState )
				if len( buffs ) >= 16: # buff or debuff
					receiver.removeBuff( receiver.findRemainTimeMinByIndexs( buffs ), [csdefine.BUFF_INTERRUPT_NONE] )
		receiver.setTemp( "SAME_TYPE_BUFF_REPLACE", False )
		receiver.addBuff( newBuff )
	
	def _findAllCanReplaceBySType( self, receiver, buffs ):
		"""
		��buffs �ҳ������ܹ��͸�BUFF��Դ���ͽ����滻������BUFF����
		@param receiver: �ܻ���
		@type  receiver: Entity
		@param buffs: ׼�������жϵ�buff�����б�
		"""
		limitSourceTypeList = g_buffLimit.getSourceLimit( self._sourceType )
		replaceList = []
		for bIdx in buffs:
			if receiver.getBuff( bIdx )["skill"].getSourceType() in limitSourceTypeList:
				replaceList.append( bIdx )
		return replaceList

	def calcTwoSecondRule( self, source, skillDamageExtra ):
		"""
		virtual method.
		������2�������� (������ buff or spell)
		"""
		return skillDamageExtra * self._shareValPercent

	def calcBuff15SecondRule( self, damage ):
		"""
		virtual method.
		buff��15�������� (������ buff)
		@param damage: ��ɫ�Ĺ����� �����������
		"""
		return int( damage * self._15SecondRuleTimeval / 15.0 )

	def receive( self, caster, receiver ):
		"""
		���ڸ�Ŀ��ʩ��һ��buff�����е�buff�Ľ��ն�����ͨ���˽ӿڣ�
		�˽ӿڱ����жϽ������Ƿ�ΪrealEntity��
		����������Ҫͨ��receiver.receiveOnReal()�ӿڴ���

		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
			
		if receiver.getState() == csdefine.ENTITY_STATE_DEAD:
			return
			
		newBuff = self.getNewBuffData( caster, receiver )
		
		#������Ҫ���ߵ����ͷǳ��Ķ�ǳ��Ĳ�ȷ�����ʹ�øô���ʽ
		#receiver is real,���Կ�����ô��
		state = receiver.doImmunityBuff( caster, newBuff )
		if state != csstatus.SKILL_GO_ON:
			DEBUG_MSG( "addbuff state is ", state )
			return
		# ����⻷Ч��
		"""
		�⻷Ч��������BUFF/DEBUFF���滻�ж�֮�С���Ч����Դ�����ر�ָ���Ĺ⻷Ч��
		���⻷Ч������Ϊ��ָ����Χ������Ϊ�̶�������ƶ����򡪡�����Ч���޳���ʱ���Ч������
		��ռ���ض���BUFF/DEBUFFλ�ã����ᱻ����Ч���滻�������Ա����ߵȼ�����ͬЧ���滻��
		ָ��ΪBUFF��DEBUFF�Ĺ⻷Ч���ֱ���ʾ��BUFF��DEBUFF��λ�á��⻷Ч��������ɳ��������ļ��㡣
		"""
		if self.isRayRingEffect():
			# ��ȡ����ͬ����ͬ���ʵĹ⻷BUFF��⻷DEBUFF
			buffs = receiver.getBuffIndexsByType( self.getBuffType(), self._effectState )
			if len( buffs ) > 0: #������ɳ��������ļ��� ��ͬ��⻷Ч����ô �滻�ȼ���׵� ����ֱ�����
				self._replaceLowLvBuff( caster, receiver, newBuff, buffs )
			else:
				receiver.addBuff( newBuff )
			return
		
		buffs = receiver.findBuffsByBuffID( self._buffID )
		#�ж��Ƿ�����ͬ��buff
		if len( buffs ) > 0:
			if not self._isAppendPrevious:
				replaceList = self._findAllCanReplaceBySType( receiver, buffs )
				if len( replaceList ) > 0:
					self._replaceLowLvBuff( caster, receiver, newBuff, replaceList )
				else:
					if len( buffs ) >= self._stackable:
						self._replaceLowLvBuff( caster, receiver, newBuff, buffs )
					else:
						self._addBuffToSameType( receiver, newBuff )
			else:
				self.doAppend( receiver, buffs[0] )
		else:
			self._addBuffToSameType( receiver, newBuff )
		
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
		ERROR_MSG( "I do not support this the function!" )

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
		ERROR_MSG( "I do not support this the function!" )
		return csstatus.SKILL_UNKNOW
#
# $Log: not supported by cvs2svn $
# Revision 1.22  2008/08/05 00:26:07  huangdong
# ���������󲻽���BUFF���ж�
#
# Revision 1.21  2008/05/28 05:59:25  kebiao
# �޸�BUFF�������ʽ
#
# Revision 1.20  2008/04/25 08:16:10  kebiao
# �¹��� �鿴�Ƿ�����ͬID��BUFF �滻���ǵĹ����� ����������һ������ʱ���Ѿ���ʧ��2/3
#
# Revision 1.19  2008/04/10 03:27:16  kebiao
# ȥ�����BUFFʱ��һЩentity״̬�ж� �ɸ��Ե�entityģ��ȥ����addBuff
# ���ݲ�ͬ���͵�entity�����ض�״̬�����Ƿ�������BUFF
#
# Revision 1.18  2008/01/11 03:24:34  kebiao
# ���entityһЩ״̬����
#
# Revision 1.17  2008/01/02 07:47:15  kebiao
# �������ܲ��ֽṹ��ӿ�
#
# Revision 1.16  2007/12/24 09:13:17  kebiao
# ���BUFF״̬֧�֣�����ɾ��BUFFʱ��������BUG
#
# Revision 1.15  2007/12/22 02:26:57  kebiao
# ����������ؽӿ�
#
# Revision 1.14  2007/12/21 02:32:03  kebiao
# ��ӹ⻷����ע�ͺ��޸�һ��BUG
#
# Revision 1.13  2007/12/20 07:14:54  kebiao
# ��ӹ⻷Ч���ж�
#
# Revision 1.12  2007/12/11 04:05:17  kebiao
# ����ֿ�BUFF֧��
#
# Revision 1.11  2007/12/07 09:01:17  kebiao
# �޸�ע��
#
# Revision 1.10  2007/12/07 04:13:45  kebiao
# ��� �滻ͬ��BUFFʧ�ܷ���ʧ����Ϣ
#
# Revision 1.9  2007/11/30 08:45:13  kebiao
# csstatus.BUFF_INTERRUPT
# TO��
# csdefine.BUFF_INTERRUPT
#
# Revision 1.8  2007/11/20 08:18:10  kebiao
# ս��ϵͳ��2�׶ε���
#
# Revision 1.7  2007/11/02 08:59:26  kebiao
# �޸ļ��ܲ��ֽӿ�
#
# Revision 1.6  2007/08/31 08:59:57  kebiao
# �޸�һ���ӿ�
#
# Revision 1.5  2007/08/18 02:47:23  kebiao
# �޸��˵��ӷ�ʽ
#
# Revision 1.4  2007/08/15 03:27:38  kebiao
# �¼���ϵͳ
#
# Revision 1.3  2007/07/10 07:54:57  kebiao
# ���µ������������ܽṹ��˸�ģ�鲿�ֱ��޸�
#
#
#