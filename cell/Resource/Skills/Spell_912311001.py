# -*- coding: gb18030 -*-
"""
ʹ�ý��ҵļ���
"""
import csstatus
import BigWorld
from Spell_Item import Spell_Item
from bwdebug import *


class Spell_912311001( Spell_Item ):
	"""
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Item.__init__( self )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		item.freeze(caster)				#������Ʒ
		caster.onlottery( item.uid )	#֪ͨ��Ʒ��ʼ�齱
		Spell_Item.receive( self, caster, receiver )

	def updateItem( self , caster ):
		"""
		������Ʒʹ��
		ע������ֻ��ȥ����Ʒ��ʹ�ã�����ɾ����Ʒ�����齱����Ʒ�ŵ��������ʱ��ɾ������
		"""
		caster.removeTemp( "item_using" )

	def useableCheck( self, caster, target ):
		"""
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		��Ҫ��������Ϣ�����ⲻ��ʹ����Ʒʱ��ʾʹ�ü���
		"""
		if caster.havelotteryItem():		#�����ǰ����ʹ�ø���Ʒ
			return csstatus.SKILL_ITEM_NOT_READY

		return Spell_Item.useableCheck( self, caster, target )