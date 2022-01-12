# -*- coding: gb18030 -*-
#
# $Id: Spell_313100004.py,v 1.6 2008-08-13 03:42:15 phw Exp $

"""
"""

from SpellBase import *
import csstatus
import csdefine

class Spell_313100004( Spell ):
	"""
	����
	����Ʒ������������ೡ����������Ŷ����������������
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
		entityScript = target.getObject().getScript()
		if len( entityScript.param1 ):
			if caster.checkItemFromNKCK_( int(entityScript.param1), 1 ):
				return csstatus.SKILL_GO_ON
			else:
				caster.statusMessage( csstatus.SKILL_MISSING_ITEM )
				return csstatus.SKILL_MISSING_ITEM
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

		caster.removeItemTotal( int( receiver.getScript().param1, 10 ), 1, csdefine.DELETE_ITEM_SYS_RECLAIM_ITEM )	# ɾ����Ʒ

		# �ص����������Լ�ִ��ĳЩ���飬��Ϊ����ķ�����˷��������Ŀ�Ĳ�һ�����������ķ�������ȡ��
		receiver.onReceiveSpell( caster, self )

		#֪ͨ��Ҵ�����Ŀ���Ѿ����
		receiver.onIncreaseQuestTaskState( caster.id )

# $Log: not supported by cvs2svn $
# Revision 1.5  2008/04/16 08:26:56  zhangyuxing
# ��ReceiverObjectʵ������һ���������������ṩ��رȽ���Ϣ��
#
# Revision 1.4  2007/12/27 08:26:32  phw
# no message
#
# Revision 1.3  2007/12/27 08:15:23  phw
# method modified: receive(), ����ɾ��������Ʒ�Ĵ���
#
# Revision 1.2  2007/12/27 08:03:03  phw
# method modified: useableCheck(), fixed: AttributeError: 'QuestBox' object has no attribute 'param1'
#
# Revision 1.1  2007/12/27 07:49:33  phw
# no message
#
#