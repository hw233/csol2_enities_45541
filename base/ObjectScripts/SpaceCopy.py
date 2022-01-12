# -*- coding: gb18030 -*-
#
# $Id: SpaceCopy.py,v 1.5 2008-04-16 05:50:45 phw Exp $

"""
"""

import random
import Language
import Love3
import csdefine
import csstatus
from bwdebug import *
from GameObject import GameObject
from Space import Space

class SpaceCopy( Space ):
	"""
	ע���˽ű�ֻ������ƥ��SpaceDomainCopy��SpaceCopy��̳�������ࡣ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		Space.__init__( self )
		self._maxCopy = 0				# �����͵�space����ܹ��������ĸ��� 0 ��������

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLoadEntityProperties_( self, section ) :
		"""
		virtual method. template method, called by GameObject::load() when an entity initialized.
		initialize entity's properties from PyDataSection
		note: all properties here must be defined in ".def" fine
		@type			section : PyDataSection
		@param			section : python data section load from entity's coonfig file
		@return					: None
		"""
		Space.onLoadEntityProperties_( self, section )

		# ����ר�ò���( for base only )
		self.setEntityProperty( "waitingCycle",	section.readInt("waitingCycle") )	# ��ת���ڣ��ռ�����Һ�رյ�ʱ��
		self.setEntityProperty( "maxPlayer",	section.readInt("maxPlayer") )		# �ռ���������������� 0 Ϊ������

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------

	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		Space.load( self, section )
		self._maxCopy = section.readInt("maxCopy")


	#------------------------------------------------------------------------------------------------------------------------------------

	def packedDomainData( self, entity ):
		"""
		virtual method.
		�������������ʱ��Ҫ��ָ����domain���������
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		# ����databaseID������space domain�ܹ���������ȷ�ļ�¼�����Ĵ����ߣ�
		# �Ҳ��õ�������ڶ�ʱ���ڣ��ϣ����ߺ�����ʱ�һظ��������⣻
		return { 'dbID' : entity.databaseID, 'spaceKey': entity.databaseID }

	def onEnter( self, selfEntity, baseMailBox, params ):
		"""
		virtual method.
		��ҽ����˿ռ�
		@param baseMailbox: cell mailbox
		@type baseMailbox: mailbox
		@param params: һЩ���ڸ�entity����space�Ķ�������� (domain����)
		@type params : PY_DICT = None
		"""
		selfEntity.stopCloseCountDownTimer()			# ���ҳ���ֹͣ�رյ���ʱ����

	def onLeave( self, selfEntity, baseMailBox, params  ):
		"""
		virtual method.
		����뿪�ռ�
		@param baseMailbox: ���mailbox
		@type baseMailbox: mailbox
		@param params: һЩ���ڸ�entity����space�Ķ�������� (domain����)
		@type params : PY_DICT = None
		"""
		if selfEntity.getCurrentPlayerCount() == 0 and selfEntity.waitingCycle > 0:
			selfEntity.startCloseCountDownTimer( selfEntity.waitingCycle )	# ���Կ�ʼ�رյ���ʱ�������û��ʼ��

	def onCloseSpace( self, selfEntity ):
		"""
		virtual method.
		space�������ڽ���������ɾ��space,���������һЩ׼��ɾ��ʱҪ��������
		"""
		pass

	def checkIntoDomainEnable( self, entity ):
		"""
		virtual method.
		���domain�Ľ�������
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX,
		"""
		return csstatus.SPACE_OK
	
	def nofityTeamDestroy( self, selfEntity, teamEntityID ):
		"""
		�����ɢ
		"""
		pass

# SpaceNormal.py
