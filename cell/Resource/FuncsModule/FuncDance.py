# -*- coding: gb18030 -*-
# ������ȡ����buff
"""
"""
from Function import Function
import cschannel_msgs
import ShareTexts as ST
import BigWorld
from csdefine import *
import time
import csconst
import csstatus
import Const

class FuncTakeDanceBuff( Function ):
	"""
	��ȡ����buff
	"""
	def __init__( self, section ):
		"""
		param1: CLASS_*

		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.skillID = section.readInt( "param1" )  			# ����ID
		self._param2 = section.readInt( "param2" )				# һ��������ȡ����

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )

		if not player.danceRecord["danceDailyRecord"].checklastTime():		# �ж��Ƿ�Ϊͬһ��
			player.danceRecord["danceDailyRecord"].reset()
		if player.danceRecord["danceDailyRecord"].getDegree() >= self._param2:		# �жϴ���
			player.statusMessage( csstatus.JING_WU_SHI_KE_LIMIT_NUM )
			return

		player.spellTarget( self.skillID, player.id )
		player.danceRecord["danceDailyRecord"].incrDegree()	# ��ȡ������1

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

class FuncFreezeDanceBuff( Function ):
	"""
	��������buff
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )

		buffs = player.findBuffsByBuffID( Const.JING_WU_SHI_KE_DANCE_BUFF )
		if len( buffs ) <= 0:
			player.statusMessage( csstatus.JING_WU_SHI_KE_NO_BUFF )
			return
		player.client.saveDanceBuff()		# ֪ͨ�ͻ���Ҫ������

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

def calculateOnLoad( timeVal ):
	"""
	�ڼ����������ݵ�ʱ�����¼����ӳ�ֵ��
	1.��ȡʣ��ʱ��(��Ҫ�������ߺ��Ƿ��ʱ)
	2.�������ڵķ���������ʱ��

	@type  timeVal: INT32
	@return: �������µ�cooldownʱ��
	@rtype:  INT32
	"""
	if timeVal == 0: return timeVal		# �޳���ʱ�䣬������
	return int( timeVal + time.time() )		# int( (ʣ��ʱ�� + ��ǰ����ʱ��) * ����ֵ )

class FuncResumeDanceBuff( Function ):
	"""
	�ָ�����ʱ��
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )

		if not player.danceRecord["freezeDanceDailyRecord"].checklastTime():		# ���û�е��춳���dance buff
			player.statusMessage( csstatus.JING_WU_SHI_KE_NO_FREEZON_BUFF )
			return

		buff = player.danceRecord[ "freezeBuff" ]
		buff[ "persistent" ] = calculateOnLoad( buff[ "persistent" ] )
		player.danceRecord[ "freezeBuff" ] = { "skill" : None, "persistent" : 0, "currTick" : 0, "caster" : 0, "state" : 0, "index" : 0 }
		player.danceRecord[ "freezeDanceDailyRecord" ]._lastTime = 0		# ��ȡdance buff�����ö���ʱ��Ϊ0


		player.addSavedBuff( buff )

		player.statusMessage( csstatus.JING_WU_SHI_KE_RESUME )

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

class FuncQueryDancePoint( Function ):
	"""
	��ѯ�赸����
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.setGossipText( cschannel_msgs.DANCE_VOICE_1 %( player.dancePoint ) )
		player.sendGossipComplete( talkEntity.id )

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
