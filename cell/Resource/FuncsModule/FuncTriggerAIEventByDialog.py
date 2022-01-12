# -*- coding: gb18030 -*-


"""
"""
from Function import Function
import csdefine
import BigWorld
import time
import csstatus
from interface.GameObject import GameObject

class FuncTriggerAIEventByDialog( Function ):
	"""
	�Ի��ı�AI�ȼ�(�öԻ�ѡ������)
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		pass
		
	def do( self, player, talkEntity = None ):
		"""
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		pass
		
	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		talkEntity.remoteCall( "doAllEventAI", ( csdefine.AI_EVENT_TALK, ) )		#�������remoteCall������Ҫ��Ϊ�˱���talkEntityΪghost�����
		return False
