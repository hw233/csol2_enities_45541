# -*- coding: gb18030 -*-
#

from bwdebug import *
from SpellBase import Spell
import csstatus
import csdefine

class Spell_Flaw( Spell ):
	"""
	��������
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.param1 = 0
		self.param2 = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		param1 = dict["param1"]
		if param1 != "": self.param1 = int( param1 )			# ǰ��BUFFID
		param2 = dict["param2"]
		if param2 != "": self.param2 = int( param2 )			# ǰ��BUFF�ȼ�

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

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		if self.param1 != 0:
			# ����Ŀ���Ƿ���ǰ��BUFF
			buffIndexs = receiver.findBuffsByBuffID( self.param1 )
			buffs = [ k for k in buffIndexs if receiver.getBuff( k )["skill"].getLevel() == self.param2 ]
			if len( buffs ) == 0: return

			receiver.removeAllBuffByBuffID( self.param1, [ csdefine.BUFF_INTERRUPT_NONE ] )
		self.receiveLinkBuff( caster, receiver )