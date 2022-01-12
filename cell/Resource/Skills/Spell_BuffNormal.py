# -*- coding: gb18030 -*-
#
# $Id: Spell_BuffNormal.py,v 1.10 2008-07-04 03:50:57 kebiao Exp $

"""
"""

import csdefine
from SpellBase import *
import csstatus
import csconst
from Spell_Item import Spell_Item
import Math

class Spell_Buff( SystemSpell ):
	"""
	��Ҫ����ϵͳҪ��ʩ��һ��BUFF�� ��ʱ��ϵͳENTITY�����������ϵͳBUFF�� ������2��ENTITY����һ��
	CELL bigword.entities���Ҳ����� ϵͳֻ��Ҫ������� role.cell.spellTarget ʩ����Ϊ�Լ� �Ϳ��Ժܷ���ĵ�ʩ��BUFF
	��������ϣ� �����BUFF����һЩ ѣ��֮����ж�.
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		SystemSpell.__init__( self )

	def init( self, data ):
		"""
		��ȡ��������
		@param data: ��������
		@type  data: python dict
		"""
		SystemSpell.init( self, data )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		self.receiveLinkBuff( caster, receiver )

class Spell_BuffNormal( Spell ):
	"""
	��������ʩ��BUFF ���� ������ʩ��BUFF��  ���ܲ������κ����� ֻ��ʩ��һ��BUFF
	��Ҫ�ǲ����˺������һ���Ż���  �ü��ܻ���Ҫϸ��Ϊ ����ͷ��� �����Ż�.
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )

	def init( self, data ):
		"""
		��ȡ��������
		@param data: ��������
		@type  data: python dict
		"""
		Spell.init( self, data )

	def getCastRange( self, caster ):
		"""
		�����ͷž���
		"""
		if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS or self.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			val1 = caster.magicSkillRangeVal_value
			val2 = caster.magicSkillRangeVal_percent
			if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
				val1 = caster.phySkillRangeVal_value
				val2 = caster.phySkillRangeVal_percent
			return ( self._skillCastRange + val1 ) * ( 1 + val2 / csconst.FLOAT_ZIP_PERCENT )
		return Spell.getCastRange( self, caster )

	def getRangeMax( self, caster ):
		"""
		virtual method.
		@param caster: ʩ���ߣ�ͨ��ĳЩ��Ҫ���������Ϊ����ķ����ͻ��õ���
		@return: ʩ������
		"""
		if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS or self.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			val1 = caster.magicSkillRangeVal_value
			val2 = caster.magicSkillRangeVal_percent
			if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
				val1 = caster.phySkillRangeVal_value
				val2 = caster.phySkillRangeVal_percent
			return ( self._rangeMax + val1 ) * ( 1 + val2 / csconst.FLOAT_ZIP_PERCENT )
		return Spell.getRangeMax( self, caster )

	def calcExtraRequire( self, caster ):
		"""
		virtual method.
		���㼼�����ĵĶ���ֵ�� ������װ�����߼���BUFFӰ�쵽���ܵ�����
		return : (�������ĸ���ֵ���������ļӳ�)
		"""
		if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS or self.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			val1 = caster.magicManaVal_value
			val2 = caster.magicManaVal_percent
			if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
				val1 = caster.phyManaVal_value
				val2 = caster.phyManaVal_percent
			return ( val1, val2 / csconst.FLOAT_ZIP_PERCENT )
		return ( 0, 0.0 )

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
		#�����Ĭ��һ�༼�ܵ�ʩ���ж�
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO  > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if ( caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ) ) & caster.hasFlag( csdefine.ROLE_FLAG_FLY_TELEPORT ):
			return csstatus.SKILL_CANT_CAST
		if self.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
				return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_MAGIC ):
				return csstatus.SKILL_CANT_CAST
		elif self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
			if caster.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
				return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_PHY ):
				return csstatus.SKILL_CANT_CAST
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER

		return Spell.useableCheck( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		self.receiveLinkBuff( caster, receiver )

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
		Spell.onArrive( self, caster, target )
		# ���Լ���ʹ�ô���
		if self.isMalignant():
			caster.doOnUseMaligSkill( self )

class Spell_ItemBuffNormal( Spell_Item ):
	"""
	��Ҫ������Ʒ������صļ���ֱ��ʩ��һ��BUFF��   ������Ҫ������Ʒ�������Ե�
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Item.__init__( self )

	def init( self, data ):
		"""
		��ȡ��������
		@param data: ��������
		@type  data: python dict
		"""
		Spell_Item.init( self, data )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		self.receiveLinkBuff( caster, receiver )		# ���ն����CombatSpellЧ����ͨ����buff(������ڵĻ�)

class Spell_BuffNormal_With_Homing( Spell_BuffNormal ):
	"""
	�����������ܼ��ݵ�Spell_BuffNormal���� by ����
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )
		
	def cast( self, caster, target ):
		"""
		ȥ������ӿ��й����������ܵļ�⣬��˵�����Ǿ�������������ֶ������ʺ��ӵײ���
		"""
		self.setCooldownInIntonateOver( caster )
		# ��������
		self.doRequire_( caster )
		#֪ͨ���пͻ��˲��Ŷ���/����������
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )

		#��֤�ͻ��˺ͷ������˴����������һ��
		delay = self.calcDelay( caster, target )
		if delay <= 0.1:
			# ˲��
			caster.addCastQueue( self, target, 0.1 )
		else:
			# �ӳ�
			caster.addCastQueue( self, target, delay )

		# ����ʩ�����֪ͨ����һ���ܴ�����Ŷ(�Ƿ��ܴ����Ѿ���ʩ��û�κι�ϵ��)��
		# �����channel����(δʵ��)��ֻ�еȷ�����������ܵ���
		self.onSkillCastOver_( caster, target )



class Spell_CertainBuffNormal( Spell_BuffNormal ):
	"""
	����ѣ�Ρ���Ĭ�ȸ�������Ӱ��ļ���
	��������������״̬
	add by wuxo 2012-6-19
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )
		self._triggerBuffInterruptCode = []
		
	def init( self, data ):
		"""
		"""
		for val in data[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )
		Spell_BuffNormal.init( self, data )
		
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
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		# ��鼼��cooldown
		if not self.isCooldown( caster ):
			return csstatus.SKILL_NOT_READY

		# ʩ��������
		state = self.checkRequire_( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		# ʩ���߼��
		state = self.castValidityCheck( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# ���Ŀ���Ƿ���Ϸ���ʩչ
		state = self.getCastObject().valid( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state
		return csstatus.SKILL_GO_ON
	
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		receiver.clearBuff( self._triggerBuffInterruptCode ) #�ж�buff
		self.receiveLinkBuff( caster, receiver )
		
class Spell_SpaceItemBuffNormal( Spell_ItemBuffNormal ):
	
	def __init__( self ):
		"""
		"""
		Spell_ItemBuffNormal.__init__( self )
		self.spaceName = ""
		self.radius = 0.0
		self.position = None
		
	def init( self, data ):
		"""
		"""
		Spell_ItemBuffNormal.init( self, data )
		self.spaceName = str( data[ "param1" ] )
		self.radius = float( data[ "param2" ] )
		self.position = Math.Vector3( eval(data["param3"]) )
	
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
		if self.spaceName != caster.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ):
			return csstatus.SKILL_SPELL_NOT_SPACENNAME
		if ( caster.position - self.position ).length > self.radius:
			return csstatus.SKILL_SPELL_NOT_SPACENNAME
		return Spell_ItemBuffNormal.useableCheck( self, caster, target )


class Spell_DistanceBuffNormal( Spell_BuffNormal ):
	"""
	�о���Ҫ��ļ�buff
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )
		self._triggerBuffInterruptCode = []
		self.minDistance = 0.0
		self.maxDistance = 0.0
		
	def init( self, data ):
		"""
		"""
		for val in data[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )
		Spell_BuffNormal.init( self, data )
		param1 = data["param1"].split(";")
		if len( param1 ) == 2:
			self.minDistance = float( param1[0] )
			self.maxDistance = float( param1[1] )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		receiver.clearBuff( self._triggerBuffInterruptCode ) #�ж�buff
		dis = ( caster.position - receiver.position ).length
		if self.minDistance < dis <  self.maxDistance:
			self.receiveLinkBuff( caster, receiver )
		


# $Log: not supported by cvs2svn $
# Revision 1.9  2008/07/03 02:49:39  kebiao
# �ı� ˯�� �����Ч����ʵ��
#
# Revision 1.8  2008/05/20 01:32:01  kebiao
# modify a bug.
#
# Revision 1.7  2008/05/19 08:52:53  kebiao
# �޸�spell_buffnormal �̳�
#
# Revision 1.6  2007/12/25 03:09:29  kebiao
# ����Ч����¼����ΪeffectLog
#
# Revision 1.5  2007/12/13 00:48:08  kebiao
# ����������״̬�ı䲿�֣���Ϊ�ײ�����س�ͻ���� �������Ͳ��ٹ��ĳ�ͻ����
#
# Revision 1.4  2007/12/12 07:33:04  kebiao
# ��ӳ�ûһ���жϷ�ʽ
#
# Revision 1.3  2007/12/06 02:51:48  kebiao
# ����жϵ�ǰ�Ƿ�����ʩ�����ж�
#
# Revision 1.2  2007/12/03 03:59:46  kebiao
# ������Ʒ�ͷ�BUFF
#
# Revision 1.1  2007/10/26 07:07:52  kebiao
# ����ȫ�µĲ߻�ս��ϵͳ������
#
# Revision 1.8  2007/08/15 03:28:57  kebiao
# �¼���ϵͳ
#
#
#