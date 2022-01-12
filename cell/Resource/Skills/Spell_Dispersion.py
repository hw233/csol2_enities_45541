# -*- coding: gb18030 -*-
#
# $Id: Spell_Dispersion.py,v 1.26 2008-08-14 01:11:36 kebiao Exp $

"""
��ɢ������
"""

from SpellBase import *
from Resource import DispersionTable
import csdefine
import csstatus

class Spell_Dispersion( Spell ):
	"""
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		#self._dispelType = []
		self._triggerBuffInterruptCode = []							# �ü��ܴ�����Щ��־���ж�ĳЩBUFF

	def init( self, dict ):
		"""
		��ȡ����
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )

		self._dispelAmount = int( dict.get( "param1" , 0 ) )			# ������ɢ���� DispelAmount
		#st = dict.readString( "param2" )						# ����ɢ�������� ���� ����...
		#for t in st.split(";"):
		#	if len( t ) <= 0: continue
		#	t = int( t )
		#	if t == 0:
		#		self._dispelType.append( csdefine.SKILL_EFFECT_STATE_BENIGN )
		#	elif t == 1:
		#		self._dispelType.append( csdefine.SKILL_EFFECT_STATE_MALIGNANT )
		#	elif t == 2:
		#		self._dispelType.append( csdefine.SKILL_RAYRING_EFFECT_STATE_BENIGN )
		#	elif t == 3:
		#		self._dispelType.append( csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT )
		#self._dispelBuffType = section.readInt( "param3" )		# ����ɢ��BUFF���
		""" ��Ϊ���� ��ֻ���� BUFF������   ������ɢ����������� Ӧ��ȥ�̳�ʵ��
		t = section.readInt( "param2" )
		self._dispellTable = DispersionTable.instance()[t]			# ����ɢ�����б� DispelTable
		"""
		for val in dict[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )

	def onReceiveBefore_( self, caster, receiver ):
		"""
		virtual method.
		���ܷ���֮ǰ��Ҫ��������
		"""
		# ĥ��
		#caster.equipAbrasion()
		pass

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
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
		return Spell.useableCheck( self, caster, target )

	def canDispel( self, caster, receiver, buffData ):
		"""
		�ɷ���ɢ
		"""
		skill = buffData["skill"]
		"""
		if self._dispelBuffType != 0 and skill.getBuffType() != self._dispelBuffType:
			return False
		if skill.getEffectState() in self._dispelType and skill.getLevel() < self.getLevel():# ֻ����ɢ���Լ�����׵�BUFF
			return True
		"""
		if skill.getLevel() < self.getLevel():# ֻ����ɢ���Լ�����׵�BUFF
			if skill.cancelBuff( self._triggerBuffInterruptCode ):
				return True
		return False

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		# ��ɢĿ�����ϵ�buff
		rmb = []
		count = 0
		for index, buff in enumerate( receiver.getBuffs() ):
			if self.canDispel( caster, receiver, buff ):
				rmb.append( index )
				count += 1
				if count >= self._dispelAmount:
					break

		# ����
		rmb.reverse()
		for index in rmb:
			receiver.removeBuff( index, self._triggerBuffInterruptCode )

class Spell_EffectDispersion( Spell ):
	"""
		սʿ�б�����ɢ�� :1
		��ʦ��ѣ����ɢ�� :2
		�����м�����ɢ�� :3
		�����л�˯��ɢ�� :4
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		#self._dispelType = []
		self._triggerBuffInterruptCode = []							# �ü��ܴ�����Щ��־���ж�ĳЩBUFF

	def init( self, dict ):
		"""
		��ȡ����
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )

		self._dispelAmount = int( dict.get( "param1" , 0 ) )			# ������ɢ���� DispelAmount
		"""
		��ɢ����
		սʿ�б�����ɢ�� :EFFECT_STATE_VERTIGO
		��ʦ��ѣ����ɢ�� :EFFECT_STATE_VERTIGO
		�����м�����ɢ�� :EFFECT_STATE_VERTIGO
		�����л�˯��ɢ�� :EFFECT_STATE_VERTIGO
		"""
		type = dict.get( "param2" , "" )
		if len( type ) > 0:
			self._effectType = eval( "csdefine." + type )
		else:
			self._effectType = -1

		for val in dict[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )

	def onReceiveBefore_( self, caster, receiver ):
		"""
		virtual method.
		���ܷ���֮ǰ��Ҫ��������
		"""
		# ĥ��
		#caster.equipAbrasion()
		pass

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
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER

		if self._effectType != csdefine.EFFECT_STATE_VERTIGO and caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if self._effectType != csdefine.EFFECT_STATE_SLEEP and caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if self._effectType != csdefine.EFFECT_STATE_HUSH_MAGIC and caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
		return Spell.useableCheck( self, caster, target )

	def canDispel( self, caster, receiver, buffData ):
		"""
		�ɷ���ɢ
		"""
		skill = buffData["skill"]
		if skill.getLevel() < self.getLevel():# ֻ����ɢ���Լ�����׵�BUFF
			if skill.cancelBuff( self._triggerBuffInterruptCode ):
				return True
		return False

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		receiver.clearBuff( self._triggerBuffInterruptCode )


class Spell_DispelAndTeleport( Spell_Dispersion ) :
	"""
	��ɢ��ҵ�buffͬʱ����Ҵ��͵�ĳ��ָ��λ�ã�ʹ���жϰ���
	��ɢ���ܵ������жϣ�������ɢ���ܴ���
	"""
	def __init__( self ) :
		Spell_Dispersion.__init__( self )
		self.spaceName = ""
		self.position = None
		self.direction = None

	def init( self, dict ) :
		Spell_Dispersion.init( self, dict )
		self.spaceName = dict["param2"].strip()
		self.position = tuple( [ float( i ) for i in dict["param3"].split(" ") ] )
		self.direction = tuple( [ float( i ) for i in dict["param4"].split(" ") ] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		Spell_Dispersion.receive( self, caster, receiver )
		receiver.gotoSpace( self.spaceName, self.position, self.direction )



# $Log: not supported by cvs2svn $
# Revision 1.25  2008/08/13 02:24:55  kebiao
# ����BUFF�ж�ʧЧ����
#
# Revision 1.24  2008/07/15 04:06:26  kebiao
# �����������޸ĵ�datatool��س�ʼ����Ҫ�޸�
#
# Revision 1.23  2008/06/02 06:39:09  kebiao
# no message
#
# Revision 1.22  2008/05/28 05:59:47  kebiao
# �޸�BUFF�������ʽ
#
# Revision 1.21  2008/01/02 07:29:49  kebiao
# �������ܲ��ֽṹ��ӿ�
#
# Revision 1.20  2007/12/20 09:09:23  kebiao
# ����µ��ж�����
#
# Revision 1.19  2007/12/18 04:15:42  kebiao
# ����onReceiveBefore����λ��
#
# Revision 1.18  2007/12/17 01:36:36  kebiao
# ����PARAM0Ϊparam1
#
# Revision 1.17  2007/12/13 01:47:26  kebiao
# ��Ӱ�BUFFTYPE��ɢ֧��
#