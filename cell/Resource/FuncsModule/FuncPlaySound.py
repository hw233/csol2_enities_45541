# -*- coding: gb18030 -*-

import BigWorld
from Function import Function
import csdefine

class FuncPlaySound( Function ):
	"""
	播放指定路径语音
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.param1 = section.readString( 'param1' )	# 音频文件路径
		self.priority = csdefine.GOSSIP_PLAY_VOICE_PRIORITY_OPTION

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.client.playSound( self.param1, 2, 0, self.priority )	# 默认播放2D语音

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True
		
class FuncPlaySoundFromGender( Function ):
	"""
	根据性别播放指定路径语音
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.param1 = section.readString( 'param1' )	# 音频文件路径（男性）
		self.param2 = section.readString( 'param2' )	# 音频文件路径（女性）
		self.priority = csdefine.GOSSIP_PLAY_VOICE_PRIORITY_OPTION

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if player.getGender() == csdefine.GENDER_MALE:
			player.client.playSound( self.param1, 2, 0, self.priority )	# 默认播放2D语音
		elif player.getGender() == csdefine.GENDER_FEMALE:
			player.client.playSound( self.param2, 2, 0, self.priority )	# 默认播放2D语音

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True