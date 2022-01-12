# -*- coding: gb18030 -*-
#
# $Id: Spell_Face.py,v 1.28 2009-07-29 07:55:41 pengju Exp $

"""
���ű���
2009.07.29: by pengju
"""
import csdefine
import csstatus
from SpellBase import *
from bwdebug import *

class Spell_Face( Spell ) :
	def __init__( self ) :
		Spell.__init__( self )
		self.__face = [] # ���������еı���

	def init( self, dict ) :
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.__face.append( dict[ "param1" ] )
		if dict["param2"] != "" :
			self.__face.append( dict[ "param2" ] )

	def getType( self ) :
		"""
		ȡ�û�����������
		��Щֵ��BASE_SKILL_TYPE_*֮һ
		"""
		return csdefine.BASE_SKILL_TYPE_ACTION

	def useableCheck( self, caster, target ) :
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
		state = caster.getState()
		if state != csdefine.ENTITY_STATE_FREE or self.__face == caster.queryTemp("Temp_Face") : # �������ڷǿ���״̬�����ڲ�ͬ������ʱ����
			return csstatus.SKILL_CAN_NOT_PLAY_FACE
		return csstatus.SKILL_GO_ON

	def receive( self, caster, receiver ) :
		"""
		���ڸ�Ŀ��ʩ��һ��buff�����е�buff�Ľ��ն�����ͨ���˽ӿڣ�
		�˽ӿڱ����жϽ������Ƿ�ΪrealEntity��
		����������Ҫͨ��receiver.receiveOnReal()�ӿڴ���

		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		caster.curActionSkillID = self.getID()
		caster.playFaceAction( self.__face )
