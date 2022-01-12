# -*- coding: gb18030 -*-
#
# role special sign & show formula
# written by gjx 2009-4-3
#

from bwdebug import *
from guis.common.PyGUI import PyGUI
import BigWorld
class RoleSigns( PyGUI ) :

	# 放在前面的优先级最高，最后一个优先级最低
	_SIGN_MAPS = [
				( "cityWarer", "maps/entity_signs/fungus.texanim" ),	# 城战采到蘑菇者
				( "bloodyItem", "maps/npc_signs/tb_npc_jie_001.tga" ),	# 带血物品标记
				( "merchant", "maps/npc_signs/tb_npc_shang_002.tga" ),	# 跑商标记
				( "pillage", "maps/npc_signs/tb_npc_fei_001.tga" ),		# 劫镖任务标记
				( "captain", "maps/npc_signs/tb_js_qi_zi_001.tga" ),	# 队长标记
				( "teammate", "maps/npc_signs/tb_js_qi_zi_002.tga" ),	# 非队长队员标记
				]

	def __init__( self, guiObject ) :
		PyGUI.__init__( self, guiObject )

		# 显示标记，用于指明当前哪些标记是要显示的，并根据优先级进行显示。
		self.__signFlags = {}
		self.__initFlags()
		self.__tongSign = None


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initFlags( self ) :
		"""
		生成与图标相应的标记，指定当前是否显示该标记
		"""
		for flagName, texture in self._SIGN_MAPS :
			self.__signFlags[flagName] = False							# 初始化所有标记，默认不显示

	def __updateSign( self ) :
		"""
		更新需要显示的标记
		"""
		for flagName, texture in self._SIGN_MAPS :
			if self.__signFlags[flagName] :								# 显示优先级最高的标记
				self.texture = texture
				self.visible = True
				if self.texture == "" :
					ERROR_MSG( "Can't find texture:", self._SIGN_MAPS[flagName] )
				break
		else :
			self.visible = False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def showSign( self, entityID, sign, isShow ) :
		"""
		指定显示/隐藏某个标记
		"""
		player = BigWorld.player()
		if self.__signFlags.has_key( sign ) :
			if sign == "captain"and isShow and not player.isTeamMember( entityID ) and player.isInTeam():
					self.__signFlags[sign] = False	# 如果玩家加入了一个队伍，则不显示其它队伍的队长标志
			elif sign == "teammate"and isShow and not player.isTeamMember( entityID ):#不显示其他队伍的队员队伍标志
					self.__signFlags[sign] = False
			else:
				self.__signFlags[sign] = isShow
			
			self.__updateSign()
		else :
			print "------------->>> unknow role sign:", sign
			
	def hideAllSign( self ):
		"""
		隐藏所有的标识
		"""
		for signName in self.__signFlags.iterkeys():
			self.__signFlags[signName] = False
		self.__updateSign()
