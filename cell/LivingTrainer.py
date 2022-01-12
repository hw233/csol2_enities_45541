# -*- coding: gb18030 -*-
# $Id: livingTrainer.py, jiangyi Exp $

import BigWorld
import NPC
from bwdebug import *
import csstatus

class LivingTrainer( NPC.NPC ):
	"""
	An Trainer class for cell.
	�����NPC
	"""
	def __init__( self ):
		NPC.NPC.__init__( self )
		# ��ʼ���������е�����

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

		#if not self.validLearn( srcEntity, skillID ):
		if not self.getScript().validLearn( srcEntity, skillID ):
			srcEntity.statusMessage( csstatus.LEARN_SKILL_FAIL )
			return
			
		srcEntity.liv_learnSkill( skillID )
		srcEntity.statusMessage( csstatus.LIVING_LEARN_NEW_SKILL_SUCESS )
			
	def oblive( self, srcEntityId, skillID ):
		"""
		Exposed Method
		����һ�������
		"""
		srcEntity = BigWorld.entities[srcEntityId]

		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > 10:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return
			
		if srcEntity.liv_obliveSkill( skillID ):
			srcEntity.statusMessage( csstatus.LIVING_OBLIVE_SKILL_SUCCESS )
		
	def skillLevelUp( self, srcEntityId, skillID ):
		"""
		Exposed Method
		����һ�������
		"""
		srcEntity = BigWorld.entities[srcEntityId]

		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > 10:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return
			
		if not self.getScript().validLevelUp( srcEntity, skillID ):
			srcEntity.statusMessage( csstatus.LIVING_CANT_LEVEL_UP_SKILL )
			return
			
		if not self.getScript().payMoney( srcEntity, skillID ):
			srcEntity.statusMessage( csstatus.SKILL_NOT_ENOUGH_MONEY )
			return
			
		srcEntity.liv_skillLevelUp( skillID )
		#srcEntity.statusMessage( csstatus.LIVING_LEVEL_UP_SKILL_SUCCESS )

# livingTrainer.py
