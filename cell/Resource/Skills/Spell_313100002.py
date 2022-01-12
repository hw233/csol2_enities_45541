# -*- coding: gb18030 -*-
#
# $Id: Spell_313100002.py,v 1.12 2008-04-16 08:26:45 zhangyuxing Exp $

"""
"""

from SpellBase import *
import csstatus
import csdefine

class Spell_313100002( Spell ):
	"""
	����
	��������ೡ����������Ŷ����������������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self._receiverObject = ReceiverObject.newInstance( 0, self )		# �����߶������а��������ߵ�һЩ�Ϸ����ж�
		self._castObjectType = csdefine.SKILL_CAST_OBJECT_TYPE_NONE	# ʩչĿ�����ͣ�see also CAST_OBJECT_TYPE_*
		self._castObject = ObjectDefine.newInstance( self._castObjectType, self )
		
	def getIntonateTime( self , caster ):
		"""
		virtual method.
		��ȡ�������������ʱ�䣬������ʱ������б�Ҫ�����Ը��������߾��������ʱ����

		@param caster:	ʹ�ü��ܵ�ʵ�塣�����Ժ���չ����ĳЩ�츳��Ӱ��ĳЩ���ܵ�Ĭ������ʱ�䡣
		@type  caster:	Entity
		@return:		�ͷ�ʱ��
		@rtype:			float
		"""
		return caster.queryTemp( "quest_box_intone_time", 0.0 )
		
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
		return csstatus.SKILL_GO_ON

	def getReceivers( self, caster, target ):
		"""
		virtual method
		ȡ�����еķ���������������Entity�б�
		���е�onArrive()������Ӧ�õ��ô˷�������ȡ��Ч��entity��
		@return: array of Entity

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@rtype: list of Entity
		"""
		entity = target.getObject()
		if entity is None or entity.isDestroyed:
			return []
		return [ entity ]
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		# ʩ���߿����Ҳ��� �μ�receiveOnReal�ӿ�
		if not caster:
			return
					
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
			
		# �ص����������Լ�ִ��ĳЩ���飬��Ϊ����ķ�����˷��������Ŀ�Ĳ�һ�����������ķ�������ȡ��
		receiver.onReceiveSpell( caster, self )
		
		#֪ͨ��Ҵ�����Ŀ���Ѿ����
		receiver.onIncreaseQuestTaskState( caster.id )
		
# $Log: not supported by cvs2svn $
# Revision 1.11  2007/12/27 02:00:39  phw
# method modified: getIntonateTime(), popTemp -> queryTemp
#
# Revision 1.10  2007/12/22 08:23:09  kebiao
# �޸ĵ���ģ��
#
# Revision 1.9  2007/12/22 08:10:18  kebiao
# ��Ϊ����Ϊ�ǹ̶��� ����ǿ����һЩ����
#
# Revision 1.8  2007/12/22 03:26:01  kebiao
# ��������
#
# Revision 1.7  2007/12/22 01:06:12  phw
# method modified: receive(), ��receiver���лص�onReceiveSpell()
#
# Revision 1.6  2007/12/19 04:15:59  kebiao
# ����onIncreaseQuestTaskState��ؽӿ� ȥ����������
#
# Revision 1.5  2007/12/19 04:03:46  kebiao
# no message
#
# Revision 1.4  2007/12/19 03:41:26  kebiao
# < 		receiver.onSetQuestTaskComplete( caster.id, 0 )
# to:
# > 		receiver.onIncreaseQuestTaskState( caster.id, 0 )
#
# Revision 1.3  2007/12/19 02:26:45  kebiao
# ��ӣ�onSetTaskComplete���ĳ������Ŀ��
#
# Revision 1.2  2007/12/18 05:57:56  kebiao
# ������һЩ������ӿڣ� ��Ϊ�˼���Ϊ�̶�����²Ż�ʹ�õĶ�����������Щ�������
#
# Revision 1.1  2007/12/18 04:16:30  kebiao
# no message
#
#