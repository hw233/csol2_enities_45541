# -*- coding: gb18030 -*-
#
# $Id: ObjectDefine.py,v 1.11 2008-08-29 03:56:22 qilan Exp $

"""
����ѡ��
"""

from bwdebug import *
from csdefine import *
import csdefine
import csconst
import csstatus
import weakref
import utils
import ReceiverObject
import gbref
import Math

class ObjectNone:
	"""
	��ʩ��λ�úͶ���
	"""
	def __init__( self, parent ):
		"""
		"""
		self.parent = weakref.proxy( parent )

	def init( self, dict ):
		"""
		virtual method.
		spell�����ļ�python dict
		"""
		pass
		
	def valid( self, caster, target ):
		"""
		virtual method.
		У��Ŀ���Ƿ����ѡ��Ҫ��
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		return csstatus.SKILL_GO_ON

	def convertCastObject( self, caster, targetEntity ):
		"""
		�����͸�����Ҫת��ʩչ����
		@param   caster: ʩ����
		@type    caster: Entity
		@param targetEntity: �ܻ���
		@type  targetEntity: Entity
		"""
		return None
	
class ObjectPosition( ObjectNone ):
	"""
	ʩ��Ŀ��Ϊλ��
	"""
	def __init__( self, parent ):
		"""
		"""
		ObjectNone.__init__( self, parent )
		
	def valid( self, caster, target ):
		"""
		virtual method.
		���ʩչ��ʼʱҪ�� (������δ�ͷų�ʱ�ļ��)
		У��Ŀ���Ƿ����ѡ��Ҫ��
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		if not target or target.getObject() is None :
			# ��ѡ��һ��ʩ��λ��
			return csstatus.SKILL_MISS_POSITION
			
		if target.getType() != csdefine.SKILL_TARGET_OBJECT_POSITION:
			return csstatus.SKILL_CAST_POSITION_ONLY
		
		# �����Ǳ����жϵ�
		distance = caster.position.flatDistTo( target.getObjectPosition() )
		range = self.parent.getRangeMax(caster)
		if range > 0.0 and distance > range:		# �������ƫ��
			# ����Ŀ��̫Զ
			return csstatus.SKILL_TOO_FAR
			
		range = self.parent.getRangeMin(caster)
		if range > 0.0 and distance < range:		# �������ƫ��
			# ����Ŀ��̫��
			return csstatus.SKILL_TOO_NEAR
			
		return csstatus.SKILL_GO_ON

class ObjectEntity( ObjectNone ):
	"""
	ʩ��Ŀ��ΪEntity
	"""
	def __init__( self, parent ):
		"""
		"""
		ObjectNone.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell�����ļ�python dict
		"""
		self._receiverObject = ReceiverObject.newInstance(  eval( dict[ "conditions" ] ), self.parent )
		self._receiverObject.init( dict )
	
	def convertCastObject( self, caster, targetEntity ):
		"""
		�����͸�����Ҫת��ʩչ����
		@param   caster: ʩ����
		@type    caster: Entity
		@param targetEntity: �ܻ���
		@type  targetEntity: Entity
		"""
		return self._receiverObject.convertCastObject( caster, targetEntity )

	def valid( self, caster, target ):
		"""
		virtual method.
		���ʩչ��ʼʱҪ�� (������δ�ͷų�ʱ�ļ��)
		У��Ŀ���Ƿ����ѡ��Ҫ��
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		state = self._receiverObject.validCastObject( caster, target )
		if csstatus.SKILL_GO_ON != state:
			return state
		
		# �����ж�
		distanceBB = caster.distanceBB( target.getObject() )
		range = self.parent.getRangeMax(caster)
		if range > 0.0 and distanceBB > range:		# �������ƫ��
			# ����Ŀ��̫Զ
			return csstatus.SKILL_TOO_FAR
		range = self.parent.getRangeMin(caster)
		if range > 0.0 and distanceBB < range:		# �������ƫ��
			# ����Ŀ��̫��
			return csstatus.SKILL_TOO_NEAR
		return csstatus.SKILL_GO_ON

class ObjectEntitys( ObjectEntity ):
	"""
	ʩ��Ŀ��ΪEntitys
	"""
	def __init__( self, parent ):
		"""
		"""
		ObjectEntity.__init__( self, parent )

	def valid( self, caster, target ):
		"""
		virtual method.
		���ʩչ��ʼʱҪ�� (������δ�ͷų�ʱ�ļ��)
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		У��Ŀ���Ƿ����ѡ��Ҫ��
		"""
		state = self._receiverObject.validCastObject( caster, target )
		if csstatus.SKILL_GO_ON != state:
			return state
		
		# �����ж�
		distanceBB = caster.distanceBB( target.getObject() )
		range = self.parent.getRangeMax(caster)
		if range > 0.0 and distanceBB > range:		# �������ƫ��
			# ����Ŀ��̫Զ
			return csstatus.SKILL_TOO_FAR
		range = self.parent.getRangeMin(caster)
		if range > 0.0 and distanceBB < range:		# �������ƫ��
			# ����Ŀ��̫��
			return csstatus.SKILL_TOO_NEAR
		return csstatus.SKILL_GO_ON
		
class ObjectItem( ObjectNone ):
	"""
	ʩ��Ŀ��Ϊ��Ʒ
	"""
	def __init__( self, parent ):
		"""
		"""
		ObjectNone.__init__( self, parent )

	def init( self, dict ):
		"""
		virtual method.
		spell�����ļ�python dict
		"""
		self._receiverObject = ReceiverObject.newInstance( eval( dict[ "conditions" ] ), self.parent)
		self._receiverObject.init( dict )

	def convertCastObject( self, caster, targetEntity ):
		"""
		�����͸�����Ҫת��ʩչ����
		@param   caster: ʩ����
		@type    caster: Entity
		@param targetEntity: �ܻ���
		@type  targetEntity: Entity
		"""
		return self._receiverObject.convertCastObject( caster, targetEntity )

	def valid( self, caster, target ):
		"""
		virtual method.
		���ʩչ��ʼʱҪ�� (������δ�ͷų�ʱ�ļ��)
		У��Ŀ���Ƿ����ѡ��Ҫ��
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		# �ж��Ƿ�Ϊ��Ч��Ŀ��
		return self._receiverObject.validCastObject( caster, target )
	
class ObjectCursorPosition( ObjectNone ):
	def __init__( self, parent ):
		ObjectNone.__init__( self, parent )
	
	def convertCastObject( self, caster, targetEntity ):
		cursorPos = gbref.cursorToDropPoint()
		return cursorPos
	
	def valid( self, caster, target ):
		"""
		virtual method.
		���ʩչ��ʼʱҪ�� (������δ�ͷų�ʱ�ļ��)
		У��Ŀ���Ƿ����ѡ��Ҫ��
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		distance = caster.position.flatDistTo( target.getObjectPosition() )
		range = self.parent.getRangeMax(caster)
		if range > 0.0 and distance > range:		# �������ƫ��
			# ����Ŀ��̫Զ
			return csstatus.SKILL_TOO_FAR
			
		range = self.parent.getRangeMin(caster)
		if range > 0.0 and distance < range:		# �������ƫ��
			# ����Ŀ��̫��
			return csstatus.SKILL_TOO_NEAR
			
		return csstatus.SKILL_GO_ON

g_objects = {
	csdefine.SKILL_CAST_OBJECT_TYPE_NONE		:	ObjectNone,			# ��λ����Ŀ��
	csdefine.SKILL_CAST_OBJECT_TYPE_POSITION	:	ObjectPosition,		# λ��
	csdefine.SKILL_CAST_OBJECT_TYPE_ENTITY		:	ObjectEntity,		# entity
	csdefine.SKILL_CAST_OBJECT_TYPE_ITEM		:	ObjectItem,			# ��Ʒ
	csdefine.SKILL_CAST_OBJECT_TYPE_ENTITYS		:	ObjectEntitys,		# entitys
}

def newInstance( objectType, spellInstance ):
	"""
	��ȡ����ѡ��ʵ����
	@type objectType:	string
	"""
	return g_objects[objectType]( spellInstance )


#
# $Log: not supported by cvs2svn $
# Revision 1.10  2008/08/29 02:35:27  qilan
# �������������ж�˳��
#
# Revision 1.9  2008/07/15 04:08:01  kebiao
# �����������޸ĵ�datatool��س�ʼ����Ҫ�޸�
#
# Revision 1.8  2008/04/16 07:19:48  zhangyuxing
# no message
#
# Revision 1.7  2008/04/15 06:52:43  zhangyuxing
# ������������޵ȼ����ԣ����ж�����ʾBUG
#
# Revision 1.6  2008/03/29 08:58:15  phw
# ����distanceBB()�ĵ��÷�ʽ��ԭ����utilsģ���е��ã���Ϊֱ���� entity ���ϵ���
#
# Revision 1.5  2008/03/29 07:39:08  kebiao
# ȥ�����ܼ�������ƫ��
#
# Revision 1.4  2008/03/03 06:36:33  kebiao
# ������С������ж�
#
# Revision 1.3  2008/03/01 08:35:21  kebiao
# ����validTarget�ӿ� ������ʩչĿ�����͵�����ж� ������������ �����
#
# Revision 1.2  2008/01/24 05:45:58  kebiao
# ���Ӷ�ʩ��Ŀ�꼶��Ҫ��Ĺ���
#
# Revision 1.1  2008/01/05 03:47:16  kebiao
# �������ܽṹ��Ŀ¼�ṹ
#
#
