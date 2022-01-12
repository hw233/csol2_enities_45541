# -*- coding: gb18030 -*-
# $Id: Trainer.py,v 1.14 2008-06-21 01:33:46 zhangyuxing Exp $

import BigWorld
import NPC
from bwdebug import *
import csstatus

class Trainer( NPC.NPC ):
	"""An Trainer class for cell.
	ѵ��ʦNPC

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
			srcEntity.statusMessage( csstatus.LEARN_SKILL_FAIL )		# hyw
			return

		state = self.spellTarget( skillID, srcEntityId )
		if state != csstatus.SKILL_GO_ON:
			INFO_MSG( "%i: skill %i use state = %i." % ( self.id, skillID, state ) )
			
	def sendTrainInfoToPlayer( self, srcEntityId, researchType ):
		"""
		"""
		srcEntity = BigWorld.entities[srcEntityId]

		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > 10:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		srcEntity.clientEntity( self.id ).receiveTrainInfos( list( self.getScript().attrTrainInfo )	)	# attrTrainInfo declare in srcClass()



# Trainer.py
