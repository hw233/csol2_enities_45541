# -*- coding: gb18030 -*-
#
# $Id: Buff.py,v 1.20 2008-08-06 06:11:09 kebiao Exp $

"""
Buff�ࡣ
"""
import BigWorld
from bwdebug import *
from SkillBase import SkillBase
import GUIFacade
from event.EventCenter import *
import csdefine
import csstatus
from gbref import rds
from Function import Functor

class Buff( SkillBase ):
	def __init__( self ):
		"""
		"""
		SkillBase.__init__( self )
		self._sourceSkillID = 0								# Դ���ܵ�ID (��Դ���ܳ�ʼ��)
		self._sourceSkillIdx = 0							# ��BUFF��Դ�������ϵ�λ��(��Դ���ܳ�ʼ��)

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type  dict:			python �ֵ�
		"""
		SkillBase.init( self, dict )

	def setSource( self, sourceSkillID, sourceIndex ):
		"""
		����Դ������Ϣ
		"""
		self._sourceSkillID = sourceSkillID
		self._sourceSkillIdx = sourceIndex

	def getSourceSkillID( self ):
		"""
		���Դ���ܵ�ID
		"""
		return self._sourceSkillID

	def isBenign( self ):
		"""
		virtual method.
		�ж�Ч���Ƿ�Ϊ����
		"""
		return self.getEffectState() == csdefine.SKILL_EFFECT_STATE_BENIGN

	def isMalignant( self ):
		"""
		virtual method.
		�ж�Ч���Ƿ�Ϊ����
		"""
		return self.getEffectState() == csdefine.SKILL_EFFECT_STATE_MALIGNANT

	def getEffectState( self ):
		return self._datas[ "EffectState" ]	# buff ��Ч�����ͣ�1 ���ԣ�0 δ���壨���ԣ���-1 ����

	def getBuffType( self ):
		"""
		virtual method.
		��ȡ��BUFF�����
		"""
		if self._datas.has_key( "Type" ):
			return self._datas[ "Type" ]
		return csdefine.BUFF_TYPE_NONE			# BUFF���

	def getID( self ):
		"""
		��ȡ���� ����ID
		"""
		return ( self._sourceSkillID * 100 ) + self._sourceSkillIdx + 1 #sourceIndex + 1 ����ΪBUFF����IDʵ���Ǽ���ID+BUFF���ڵ����� �������1 ��ôskillID+0=skillID

	def getEffectID( self ):
		"""
		��ȡBUFF��Ч��ID
		"""
		return ( self._sourceSkillID/1000 * 100 ) + self._sourceSkillIdx + 1

	def getIcon( self ):
		"""
		����buff��ͼ���÷���
		"""
		return rds.spellEffect.getIcon( self.getEffectID() * 1000 )

	def getType( self ):
		"""
		@return: ��������
		"""
		return csdefine.BASE_SKILL_TYPE_BUFF			# ������� ��ǿ��ΪBUFF ��ΪBUFFʵ��Ҳ�Ǽ���ϵͳ�е�һԱ���������Ƕ���һ��ϵ�е�Type���ࣩ

	def getBuffID( self ):
		"""
		ȡ��BUFF�����ı�� BUFFID (����BUFFIDʹ���˼���*N��ɵ�ID ������IDΪ������BUFFID)
		"""
		return self._datas[ "ID" ]

	def getPersistent( self ) :
		"""
		��ȡ buff �ĳ���ʱ��
		hyw -- 2008.09.24
		"""
		return self._datas[ "Persistent" ]

	def cast( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		# self._buffID * 1000 ��ԭ����Ϊ�˷����Ч��ȡ�Ǳ߲��ô������
		# ת�����ID����Ϊbuff�Ĺ�Ч���úͼ��ܵ���һ�������Ǽ����кܶ༶��
		# �磺����322718001 ������322718���Ǳ��ѻ����ID
		# ����001��ʾһ���ġ���Ч�����Ǳ߾���ת������322718Ϊ���ܵ�ID���õ�
		# ���� ����self._buffID * 1000������ͳһ��ȡ
		self.playEffect( caster, target )

	def playEffect( self, caster, target ):
		"""
		����buffЧ��
		"""
		skillID = self.getEffectID() * 1000
		if hasattr( caster,"isLoadModel" ) and caster.isLoadModel:
			caster.delayCastEffects.append( Functor( rds.skillEffect.playBuffEffects, caster, target, skillID ) )
		else:
			rds.skillEffect.playBuffEffects( caster, target, skillID )
	
		# buff����Ч����һ��������BUFF����������
		self.pose.buffCast( target, skillID )

	def end( self, caster, target ):
		"""
		@param caster	:	ʩ����Entity
		@type caster	:	Entity
		@param target	: 	ʩչ����
		@type  target	: 	����Entity
		"""
		skillID = self.getEffectID() * 1000
		rds.skillEffect.stopBuffEffects( caster, target, skillID )
		self.pose.buffEnd( target, skillID )

	def receiveSpell( self, target, casterID, damageType, damage  ):
		"""
		���ܼ��ܴ���

		@type   casterID: OBJECT_ID
		@type    skillID: INT
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		player = BigWorld.player()
		caster = None
		if casterID:
			try:
				caster = BigWorld.entities[casterID]
			except KeyError:
				#�����������ԭ���� �ڷ�������һ��entity����һ��entityʩ�� ���������ǿ��ĵ�ʩ���ߵ�
				#���ͻ��˿��ܻ���Ϊĳԭ�� �磺�����ӳ� ���ڱ���û�и��µ�AOI�е��Ǹ�ʩ����entity����
				#��������ִ��� written by kebiao.  2008.1.8
				casterID = 0

		# �ص��˺���Ϣ ��һ���˺���HP ������0 �������� ����Ȼ���˺�
		target.onReceiveDamage( casterID, self, damageType, damage  )
		# ������Ч����
		self._skillAE( player, target, caster, damageType, damage  )

	def _skillAE( self, player, target, caster, damageType, damage ):
		"""
		���ܲ����˺�ʱ�Ķ���Ч���ȴ���
		@param player:			����Լ�
		@type player:			Entity
		@param target:			Spellʩ�ŵ�Ŀ��Entity
		@type target:			Entity
		@param caster:			Buffʩ���� ����ΪNone
		@type castaer:			Entity
		@param damageType:		�˺�����
		@type damageType:		Integer
		@param damage:			�˺���ֵ
		@type damage:			Integer
		"""
		if damageType & csdefine.DAMAGE_TYPE_REBOUND == csdefine.DAMAGE_TYPE_REBOUND:
			return

		casterID = 0
		if caster:
			rds.skillEffect.playHitEffects( caster, target, self.getEffectID() * 1000 )
			casterID = caster.id
#
# $Log: not supported by cvs2svn $
# Revision 1.19  2008/08/06 06:09:49  qilan
# method modify��_SkillAE()����Ϊ_skillAE()
#
# Revision 1.18  2008/08/06 03:31:08  kebiao
# ����receiveDamage�ӿڲ��� skill.receiveSpell ȥ��skillID
#
# Revision 1.17  2008/08/05 02:03:19  qilan
# ������_receiveDamageAE()����Ϊ_SkillAE()
# ȥ��ϵͳ��Ϣ��ص���������_receiveDamageSysInfo()/_receiveDamageFlyText()
# ע���˺�ϵͳ��Ϣ�ŵ��ܷ��ߵ�entity��
#
# Revision 1.16  2008/07/31 09:15:25  qilan
# �����˽�ɫ�ܵ�Debuff�˺�������������ʾ
#
# Revision 1.15  2008/07/21 03:04:22  huangyongwei
# caster.pcg_getOutPet(),
# ��Ϊ
# caster.pcg_getActPet(),
#
# Revision 1.14  2008/07/15 06:54:32  kebiao
# ���ܲ���ͳһʹ��section ��Ϊpython����������������ڴ棬Language.section
# ��C�ṹ�洢 ���ή���ڴ�����
#
# Revision 1.13  2008/07/09 01:33:35  kebiao
# ����˺��ص�����
#
# Revision 1.12  2008/06/30 06:20:09  kebiao
# ����    self._receiveDamageAE( player, target, caster, param1, param2, skillID )
# UnboundLocalError: local variable 'caster' referenced before assignment
#
# Revision 1.11  2008/05/30 03:06:16  yangkai
# װ������������Ĳ����޸�
#
# Revision 1.10  2008/04/17 06:42:32  wangshufeng
# SKILL_EFFECT_STATE_BENIGN -> csdefine.SKILL_EFFECT_STATE_BENIGN
#
# Revision 1.9  2008/03/31 09:05:00  kebiao
# �޸�receiveDamage��֪ͨ�ͻ��˽���ĳ���ܽ���ֿ�
# ����ͨ��receiveSpell֪ͨ�ͻ���ȥ���֣�֧�ָ����ܲ�ͬ�ı���
#
# Revision 1.8  2008/03/18 07:52:11  kebiao
# �����˳��﹥���������ʾ��Ϣ
#
# Revision 1.7  2008/02/25 09:27:27  kebiao
# �����˺�������ʾ
#
# Revision 1.6  2008/02/22 02:57:34  kebiao
# ���ӳ��﹥��ðѪ��ʾ
#
# Revision 1.5  2008/01/31 07:20:45  kebiao
# ����ս����Ϣ
#
# Revision 1.4  2008/01/25 10:08:43  yangkai
# �����ļ�·���޸�
#
# Revision 1.3  2008/01/24 07:37:00  kebiao
# modify buffid is 0
#
# Revision 1.2  2008/01/24 07:07:11  kebiao
# add method:getBuffID
#
# Revision 1.1  2008/01/05 03:47:16  kebiao
# �������ܽṹ��Ŀ¼�ṹ
#
#