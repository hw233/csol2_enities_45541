# -*- coding: gb18030 -*-
#
#����ģ�ͼ���
#by wuxo 2012-3-22

from Spell_BuffNormal import Spell_BuffNormal

class Spell_ChangeModel( Spell_BuffNormal ):
	"""
	����ģ�ͼ���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_BuffNormal.__init__( self )
		self.modelNumber = ""
		
	def init( self, dict ):
		"""
		��ȡ����
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_BuffNormal.init( self, dict )
		self.modelNumber = str(dict["param1"])
		if dict["param2"] != "" :
			self.modelScale  = float( dict["param2"] )
		else:
			self.modelScale  = 1.0

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
		
	def receive( self, caster, receiver ):
		"""
		������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		receiver.setModelNumber( self.modelNumber )
		receiver.modelScale = self.modelScale
		self.receiveLinkBuff( caster, receiver )		# ���ն����CombatSpellЧ����ͨ����buff(������ڵĻ�)
	
