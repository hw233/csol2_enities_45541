# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
"""
from Function import Function
import csdefine
import BigWorld
import csstatus
import csconst
import time

def calculateOnSave( self, timeVal ):
	"""
	�ڱ����������ݵ�ʱ�����¼����ӳ�ֵ��
	1.��ȡʣ��ʱ��(��Ҫ�������ߺ��Ƿ��ʱ)
	2.����ʣ��ʱ��

	@type  timeVal: INT32
	@return: �������µ�cooldownʱ�䣻���Ǽ������д�������ֵ���Ǵ�cellData���õģ���˸�ֵ��һ��ʹ��BigWorld.time()����������
	@rtype:  INT32
	"""
	if timeVal == 0: return timeVal		# �޳���ʱ�䣬������
	# ȡ��ʣ��ʱ�䣬�����ȳ�������ֵ��ȡ������ʣ��ʱ��
	return int( timeVal - time.time() )

class FuncCloseDoubleExpRemainTime( Function ):
	"""
	����˫������ʱ��
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.saveDoubleExpBuff()
		player.endGossip( talkEntity )

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
		return True

