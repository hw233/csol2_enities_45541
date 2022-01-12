# -*- coding: gb18030 -*-
#
# $Id: FuncAboutPet.py,v 1.4 2008-06-19 07:49:25 fangpengjun Exp $

"""
实现与宠物相关的对话函数
"""

import csdefine

# --------------------------------------------------------------------
# 宠物合成
# --------------------------------------------------------------------
class FuncCombinePet :
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.pcg_dlgCombinePet( talkEntity )
		player.endGossip( talkEntity )

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
		if player.pcg_dlgCanCombinePet() :
			return True
		return False


# --------------------------------------------------------------------
# 购买经验石
# --------------------------------------------------------------------
class FuncBuyGem :
	def __init__( self, param ):
		"""
		param format: 无

		@param param: 由实现类自己解释格式
		@type  param: string
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		player.ptn_dlgBuyTrainGem( talkEntity )
		player.gem_activateGem( talkEntity.id )

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
		if player.ptn_dlgAllownActivateTrainGem() :
			return True
		return False



# --------------------------------------------------------------------
# 宠物繁殖
# --------------------------------------------------------------------
class FuncProcreatePet :
	def __init__( self, param ):
		"""
		param format: 无

		@param param: 由实现类自己解释格式
		@type  param: string
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		player.pft_dlgShowProcreateDialog( talkEntity )

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

# --------------------------------------------------------------------
# 提取繁殖完成的宠物
# --------------------------------------------------------------------
class FuncGetProcreatedPet :
	def __init__( self, param ):
		"""
		param format: 无

		@param param: 由实现类自己解释格式
		@type  param: string
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		player.pft_dlgTakeProcreatePet( talkEntity )

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

# --------------------------------------------------------------------
# 宠物租赁
# --------------------------------------------------------------------
class FuncHireStorage :
	def __init__( self, param ):
		"""
		param format: 无

		@param param: 由实现类自己解释格式
		@type  param: string
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		player.client.pst_openHire( talkEntity.id )

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
		if player.pst_dlgCanBeHired() :
			return True
		return False



# --------------------------------------------------------------------
# 租用小仓库
# --------------------------------------------------------------------
class FuncOpenStorage :
	def __init__( self, param ):
		"""
		param format: 无

		@param param: 由实现类自己解释格式
		@type  param: string
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		player.pst_dlgOpen( talkEntity )

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
		if player.pst_dlgCanBeOpen() :
			return True
		return False
