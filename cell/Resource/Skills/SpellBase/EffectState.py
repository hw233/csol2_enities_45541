# -*- coding: gb18030 -*-
#
# $Id: EffectState.py,v 1.9 2008-05-20 06:41:56 kebiao Exp $

"""
����Ч������
"""

import BigWorld
import Language
import csstatus
import csdefine
from bwdebug import *
from Domain_Fight import g_fightMgr

class EffectState:
	def __init__( self ):
		"""
		���캯����
		"""
		self._effectState = csdefine.SKILL_EFFECT_STATE_NONE		# ��SKILL��״̬�����ԡ���ӹ(��״̬)������
		self._enmity = 0											# ������ɵĵ���

	def init( self, dictDat ):
		"""
		���ַ�����Ϊ�������أ�
		@param dictDat: ���ַ������������ɸ��������Լ�����
		@type  dictDat: STRING
		"""
		try:
			self._enmity = dictDat[ "Enmity" ]  #int type
		except:
			self._enmity = 0

		try:
			self._effectState = dictDat[ "EffectState" ] #int type
		except:
			self._effectState = 0

	def getEffectState( self ):
		"""
		��ȡ����Ч��״̬
		"""
		return self._effectState

	def isRayRingEffect( self ):
		"""
		�Ƿ�Ϊ�⻷Ч��
		"""
		return self._effectState in [ csdefine.SKILL_RAYRING_EFFECT_STATE_BENIGN, csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT ]

	def isBenign( self ):
		"""
		virtual method.
		�жϷ���Ч���Ƿ�Ϊ����
		"""
		return self._effectState in [ csdefine.SKILL_EFFECT_STATE_BENIGN, csdefine.SKILL_RAYRING_EFFECT_STATE_BENIGN ]

	def isMalignant( self ):
		"""
		virtual method.
		�жϷ���Ч���Ƿ�Ϊ����
		"""
		return self._effectState in [ csdefine.SKILL_EFFECT_STATE_MALIGNANT, csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT ]

	def isNeutral( self ):
		"""
		virtual method.
		�жϷ���Ч���Ƿ������Լ���
		"""
		return self._effectState == csdefine.SKILL_EFFECT_STATE_NONE
		
	def canCancel( self ):
		"""
		virtual method.
		�жϵ�ǰ�����Ƿ�����ȡ��
		"""
		return self._effectState == csdefine.SKILL_EFFECT_STATE_BENIGN		# ֻ������Ч������ȡ��

	def getEnmity( self ):
		"""
		��ó��
		"""
		return self._enmity

	def receiveEnemy( self, caster, receiver ):
		"""
		һ��������Ч�������ж�������������Ĺ������б����ʩ���ߵĳ��
		����������ǹ���ֱ����ӱ�����BUFF�ĳ��ֵ
		@param   caster: ʩ���ߣ����û��ʩ������ΪNone
		@type    caster: Entity
		@param receiver: ������
		@type  receiver: Entity
		"""
		if self._effectState == csdefine.SKILL_EFFECT_STATE_NONE or \
			not hasattr( receiver, "getState" ) or receiver.getState() == csdefine.ENTITY_STATE_DEAD or \
			not hasattr( caster, "getState" ) or caster.getState() == csdefine.ENTITY_STATE_DEAD:
			return

		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if self.isBenign():
				receiver.cureToEnemy( caster , self._enmity )
		else:
			if self.isMalignant():
				g_fightMgr.buildEnemyRelation( receiver, caster )
				
				if caster.isEntityType( csdefine.ENTITY_TYPE_PET ) :
					owner = caster.getOwner()
					g_fightMgr.buildEnemyRelation( receiver, owner.entity )


#
# $Log: not supported by cvs2svn $
# Revision 1.7  2008/04/17 07:29:16  kebiao
# ����ս���б����BUG �� ���﹥�� ��ɫ������ս��״̬������
# BUFF���漼�ܺ������б�Ĺ�ϵ
#
# Revision 1.6  2008/04/15 07:07:12  kebiao
# �޸�ս���б����
#
# Revision 1.5  2008/01/15 04:14:05  kebiao
# ��ӳ��﹥��ʱ������Ҳ�����˲������
#
# Revision 1.4  2007/12/20 07:14:46  kebiao
# ��ӹ⻷Ч���ж�
#
# Revision 1.3  2007/12/14 03:28:22  kebiao
# �޸���ӳ�޽ӿ��н�ɫ���жϷ�ʽ
#
# Revision 1.2  2007/11/20 08:19:26  kebiao
# ս��ϵͳ��2�׶ε���
#
# Revision 1.1  2007/07/20 06:53:14  kebiao
# ����Ч��
#
#
#
