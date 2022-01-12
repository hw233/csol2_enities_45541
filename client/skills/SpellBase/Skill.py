# -*- coding: gb18030 -*-
#
# $Id: Skill.py,v 1.3 2008-07-15 06:54:32 kebiao Exp $

"""
���������ࡣ
"""

import csstatus
import csdefine
from SkillBase import SkillBase
import skills
from Buff import Buff

class Skill( SkillBase ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		SkillBase.__init__( self )
		self._buffLink = []

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			������������
		@type dict:				Python dict
		"""
		SkillBase.init( self, dict )
		if dict.has_key( "buff" ): #list
			index = 0
			for datI in xrange( len( dict[ "buff" ] ) ):
				dat = dict[ "buff" ][datI]
				inst = None
				if len( dat[ "ClientClass" ] ) > 0:
					sid =  str(int(dat["ID"]))
					buffclass = "skills.Buff_" + sid + ":Buff_" + sid
					inst = smartImport( buffclass )()
				else:
					inst = Buff()
				inst.init( dat )
				inst.setSource( self.getID(), index )
				self._buffLink.append( inst )
				skills.register( inst.getID(), inst )
				index += 1

	def getType( self ):
		"""
		@return: ��������
		"""
		return csdefine.BASE_SKILL_TYPE_PASSIVE

	def getPosture( self ) :
		"""
		��ȡ����������̬
		"""
		cndDict = self._datas[ "CasterCondition" ]
		if len( cndDict ) > 0 :
			cnd = cndDict[ "conditions" ]
			if len( cnd ) > 0 :
				value = eval( cnd, csdefine.__dict__ )
				if value & csdefine.CASTER_CONDITION_POSTURE :
					for extraValue in cndDict["ExtraValue"].split( ";" ):
						valueList = extraValue.split( "'" )
						if len( valueList ) < 1 or valueList[0] != "Posture":
							continue
						return int( valueList[1] )
		return SkillBase.getPosture( self )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		return csstatus.SKILL_PASSIVE

	def isHomingSkill( self ):
		"""
		�ж��Ƿ��������� 	by ����
		@return: BOOL
		"""
		return False

	def getBuffLink( self ):
		"""
		@return: ���ܲ�����BUFF [buffInstance,...]
		"""
		return self._buffLink
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/02/27 08:09:24  kebiao
# add:import csdefine
#
# Revision 1.1  2008/01/05 03:47:16  kebiao
# �������ܽṹ��Ŀ¼�ṹ
#
#