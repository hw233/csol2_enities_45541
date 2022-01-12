# -*- coding: gb18030 -*-
#
# $Id:

"""
"""
from bwdebug import *
from NPCObject import NPCObject
import csstatus

# ȫ�ֵ����Գ�ʼ����Ӧ��
g_propsMap = (
				( "visible",					lambda section, key: section[key].asInt ),			# �Ƿ�ɼ�
				( "radius",						lambda section, key: section[key].asFloat ),		# �����뾶
			)

class NPCQuestTrap( NPCObject ):
	"""
	���񴥷���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		NPCObject.__init__( self )

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�

		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		NPCObject.onLoadEntityProperties_( self, section )
		self.setEntityProperty( "visible",		section["visible"].asInt )			# �Ƿ�ɼ�
		self.setEntityProperty( "radius",		section["radius"].asFloat )			# �����뾶

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
		# ����ɶ�¶�����ֻ�ǽ��õײ�Ĵ���
		pass

	def onEnterTrapExt( self, selfEntity , entity, range, userData ):
		"""
		This method is associated with the Entity.addProximity method.
		It is called when an entity enters a proximity trap of this entity.

		@param entity:		The entity that has entered.
		@param range:		The range of the trigger.
		@param userData:	The user data that was passed to Entity.addProximity.
		"""
		if entity.__class__.__name__ != "Role" or not entity.isReal():
			return

		#self.listUsableQuests( selfEntity, entity, "Talk", False )

	def onLeaveTrapExt( self, selfEntity , entity, range, userData ):
		"""
		This method is associated with the Entity.addProximity method.
		It is called when an entity leaves a proximity trap of this entity.

		@param entity:		The entity that has left.
		@param range:		The range of the trigger.
		@param userData:	The user data that was passed to Entity.addProximity.
		"""
		pass

	def gossipWith( self, selfEntity, player, dlgKey ):
		"""
		@param       dlgKey: �Ի��ؼ���
		@type        dlgKey: string
		@return: ��
		"""
		#self.castQuests( selfEntity, player, dlgKey )
		pass