# -*- coding:gb18030 -*-

from Spell_BuffNormal import Spell_BuffNormal


# Ӣ�����˸�����NPCװ����������ҵı�����
# ֻ�ǽ�����һ����ʱ�����Դ�ţ���˲���
# ����ͨ��Ʒ��ʹ�����̣���Ϊ��ͨ��Ʒʹ��
# ʱ�����ұ����в���ʹ�õ���Ʒ����ᵼ
# ����Ʒ�Ҳ���������
class Spell_Item_YXLM( Spell_BuffNormal ) :

	def cast( self, caster, target ):
		"""
		virtual method.
		��ʽ��һ��Ŀ���λ��ʩ�ţ���з��䣩�������˽ӿ�ͨ��ֱ�ӣ����ӣ���intonate()�������á�

		ע���˽ӿڼ�ԭ���ɰ��е�castSpell()�ӿ�

		@param     caster: ʹ�ü��ܵ�ʵ��
		@type      caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		Spell_BuffNormal.cast( self, caster, target )
		caster.removeTemp( "item_using" )
