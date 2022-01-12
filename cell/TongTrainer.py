# -*- coding: gb18030 -*-
#
# $Id: Trainer.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
Trainer����
"""

import BigWorld
from bwdebug import *
import csdefine
import csstatus
from Trainer import Trainer

class TongTrainer( Trainer ):
	"""
	����CSOL-2116�޸ĺ󣬸�NPCû��ʵ�ʹ���
	������Trainer����
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		Trainer.__init__( self )
		
	def lock( self ):
		"""
		define method.
		Trainer����ס�� ����Ա�޷���������
		"""
		self.locked = True

	def unlock( self ):
		"""
		define method.
		Trainer�������� ����Ա�ָ���������
		"""
		self.locked = False

	def trainPlayer( self, srcEntityId, skillID ):
		"""
		ѵ�����

		@param srcEntityId: ����ʹ����<Expose/>���������ϵͳ�Զ����ݽ����ģ���ʾ���ĸ�client�ϵĵ���
		@type  srcEntityId: int
		@param     skillID: Ҫѵ���ļ���
		@type      skillID: INT
		@return: 			��
		"""
		srcEntity = BigWorld.entities[srcEntityId]

		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > 10:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return
	
	def sendTrainInfoToPlayer( self, srcEntityId, researchType ):
		"""
		Define method.
		���ͼ������ݸ����
		"""
		srcEntity = BigWorld.entities[srcEntityId]

		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > 10:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

	def researchSkill( self, srcEntityId, skillID ):
		"""
		define method.
		�ͻ���������������з��ü���
		"""
		srcEntity = BigWorld.entities[srcEntityId]
		
		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > 10:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

	def clearTongSkill( self, srcEntityId, skillID ):
		"""
		define method.
		ѡ��������ĳ����
		"""
		srcEntity = BigWorld.entities[srcEntityId]
		
		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > 10:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return
		
# Trainer.py
