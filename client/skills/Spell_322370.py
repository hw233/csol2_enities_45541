# -*- coding: gb18030 -*-
#
# $Id: Spell_322370.py,v 1.6 2008-08-06 06:11:18 kebiao Exp $

"""
Spell�����ࡣ
"""
import BigWorld
from bwdebug import *
from skills.Spell_Item import Spell_Item
import ItemTypeEnum
import csstatus
import SkillTargetObjImpl
from gbref import rds

class Spell_322370( Spell_Item ):
	def __init__( self ):
		"""
		��python dict����SkillBase
		"""
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type dict:				python dict
		"""
		Spell_Item.init( self, dict )

	def cast( self, caster, targetObject ):
		"""
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		#�Զ������ԣ���ֻ�Ქ��һ��
		pet = caster.pcg_getActPet()
		if pet is None: return
		self.pose.cast( pet, self.getID(), targetObject )
		targetPet = SkillTargetObjImpl.createTargetObjEntity( targetObject.getObject().pcg_getActPet() )
		if targetPet is None: return
		rds.skillEffect.playCastEffects( pet, targetPet, self.getID() )

	def receiveSpell( self, target, casterID, damageType, damage ):
		"""
		���ܼ��ܴ���

		@type   casterID: OBJECT_ID
		@type    skillID: INT
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		player = BigWorld.player()
		if casterID:
			try:
				caster = BigWorld.entities[casterID]
			except KeyError:
				#�����������ԭ���� �ڷ�������һ��entity����һ��entityʩ�� ���������ǿ��ĵ�ʩ���ߵ�
				#���ͻ��˿��ܻ���Ϊĳԭ�� �磺�����ӳ� ���ڱ���û�и��µ�AOI�е��Ǹ�ʩ����entity����
				#��������ִ��� written by kebiao.  2008.1.8
				return
		else:
			caster = None

		# ������Ч����
		pass

#
# $Log: not supported by cvs2svn $
# Revision 1.5  2008/08/06 03:31:31  kebiao
# ����receiveDamage�ӿڲ��� skill.receiveSpell ȥ��skillID
#
# Revision 1.4  2008/07/21 03:04:09  huangyongwei
# caster.pcg_getOutPet(),
# ��Ϊ
# caster.pcg_getActPet(),
#
# Revision 1.3  2008/03/31 08:39:23  kebiao
# no message
#
#
#