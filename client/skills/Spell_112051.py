# -*- coding: gb18030 -*-

"""
Spell�����ࡣ
"""
import BigWorld
from bwdebug import *
from SpellBase import *
import csstatus
import csdefine
from gbref import rds

MODEL_PATH = "particles/model/gw1355.model"

class Spell_112051( Spell ):
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )


	def cast( self, caster, targetObject ):
		"""
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		caster.setVisibility( False )
		Spell.cast( self, caster, targetObject )
