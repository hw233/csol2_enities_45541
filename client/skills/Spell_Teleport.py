# -*- coding: gb18030 -*-
#
#edit by wuxo 2013-12-24
from SpellBase import Spell
import BigWorld
from gbref import rds

class Spell_Teleport( Spell ):
	"""
	ͬ��ͼ���� �޷������һ������·��
	"""
	def __init__( self ):
		"""
		���캯����
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
		Spell.cast( self, caster, targetObject )
		if targetObject.getObject() == BigWorld.player():
			rds.roleFlyMgr.stopFly( False )
			BigWorld.player().checkTelepoertFly()
	
