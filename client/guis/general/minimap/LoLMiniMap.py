# -*- coding: gb18030 -*-
#
"""
implement lolminimap class

"""

import csdefine
import csstatus
import event.EventCenter as ECenter
import gbref
import Timer
import csconst
from guis import *
import Language
from guis.common.PyGUI import PyGUI
from guis.common.RootGUI import RootGUI
from guis.common.Frame import HVFrame
from guis.controls.Control import Control
import math

class LoLMiniMap( RootGUI, HVFrame ):
	"""
	英雄联盟小地图
	"""
	__DM_ORIGIN		= 1									# 原始大小模式
	__DB_ADATPED	= 2									# 适应屏幕大小模式
	
	def __init__( self ):
		frm = GUI.load( "guis/general/minimap/lolmini.gui" )
		uiFixer.firstLoadFix( frm )
		RootGUI.__init__( self, frm )
		HVFrame.__init__( self, frm )
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "TOP"
		self.moveFocus = False
		self.posZSegment = ZSegs.L4
		self.activable_ = False
		self.escHide_ = False
		self.__pyRoleSigns = {}							# 玩家标记
		self.__pyBossSigns = {}							# boss标记
		self.__pyMonsterSigns = {}						# 添加到小地图的怪物标志
		self.__updateTimerID = 0
		self.__viewArea = None
		self.__scale = 1.0

		self.__dspMode = self.__DM_ORIGIN				# 地图的显示模式
		self.__delaycbids = {}
		self.__AoIRoleIDs = []							# AOI范围角色id

		self.__initialize( frm )

		self.__triggers = {}
		self.__registerTriggers()
	
	def __initialize( self, frm ):
		"""
		初始化地图
		"""
		self.__pyMap = Control( frm.map )
		self.__pyMap.focus = True
		self.__pyMap.moveFocus = True

		self.__viewSize = self.__pyMap.size

		self.__pyPointer = PyGUI( frm.map.pointer )
		self.__pyPointer.gui.position.z = 0.6
		self.__pyCamera = PyGUI( frm.map.camera )
	
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_SHOW_YXLMCOPY_MINIMAP"] = self.__onShowLoLMinMap
		self.__triggers["EVT_ON_HIDE_YXLMCOPY_MINIMAP"] = self.__onHideLoLMinMap
		self.__triggers["EVT_ON_SET_YXLMCOPY_BOSS_SPAWN_SIGN"] = self.__onSetMonsterSpawnPos
		self.__triggers["EVT_ON_UPDATE_YXLMCOPY_BOSS_SIGN"] = self.__onUpdateBossPos
		self.__triggers["EVT_ON_SET_YXLMCOPY_BOSS_DIED_SIGN"] = self.__onsetMonsterDiedPos
		self.__triggers["EVT_ON_RESOLUTION_CHANGED"] = self.__onResolutionChanged
		self.__triggers["EVT_ON_PVP_ON_RECEIVE_ENEMY_POS"] = self.__onReceiveEnemyPos
		self.__triggers["EVT_ON_PVP_ON_DISPOSE_ENEMY_SIGN"] = self.__onDisposeEnemy
		self.__triggers["EVT_ON_MONSTER_GET_DAMAGE"]	= self.__onGetDamage		#防御塔或基地受到一定伤害时图标闪烁
		
		for key in self.__triggers :
			ECenter.registerEvent( key, self )
			
	# ----------------------------------------------------------------
	def __onShowLoLMinMap( self, spaceLabel ):
		"""
		显示英雄联盟地图
		"""
		player = BigWorld.player()
		area = rds.mapMgr.getWholeArea( spaceLabel, player.position[2] )
		self.__viewArea = area
		self.__pyMap.texture = area.texture							
		size = area.mapBound.size
		self.__viewSize = size
		self.__pyMap.mapping = area.mapMapping
		width, height = size
		cwidth, cheight = self.__pyMap.size
		scaleX = cwidth / width
		scaleY = cheight / height
		if abs( scaleX ) < abs( scaleY ) :
			self.__scale = scaleX
		else :
			self.__scale = scaleY
		self.show()
	
	def __onHideLoLMinMap( self ):
		"""
		隐藏英雄联盟地图
		"""
		self.hide()
	
	def __onSetMonsterSpawnPos( self, id, className, spawnPos, relation, signType ):
		"""
		设置怪物初始位置（boss、防御塔、基地）
		"""
		if signType == Sign.ST_NPC:		
			self.__onUpdateBossPos( id, className, spawnPos, relation )
		else:
			self.__onsetBaseOrTowerSpawnPos( id, className, spawnPos, relation, signType )		
	
	def __onUpdateBossPos( self, id, className,pos, relation ):
		"""
		更新boss坐标
		"""
		pyBossSign = None
		if id in self.__pyBossSigns:
			pyBossSign = self.__pyBossSigns[id]
		else:
			pyBossSign = Sign( self, className, Sign.ST_NPC, relation )
			self.__pyMap.addPyChild( pyBossSign )
			self.__pyBossSigns[id] = pyBossSign
		if pyBossSign:
			self.__locateSign( pyBossSign, pos )
			pyBossSign.setStyle( Sign.ST_NPC, relation )
	
	def __onsetMonsterDiedPos( self, id, className, spawnPos, diedPos, relation ):
		"""
		boss 防御塔 基地死亡时
		"""
		if self.__pyBossSigns.has_key( id ):
			self.__onsetBossDiedPos( id, className, spawnPos, diedPos, relation )
		else:
			self.__onsetMonsterDied( id )
	 
	def __onsetBossDiedPos( self, id, className, spawnPos, diedPos, relation ):
		"""
		更新boss死亡位置,30秒后消失
		"""
		if id in self.__pyBossSigns:
			pyBossSign = self.__pyBossSigns[id]
			self.__locateSign( pyBossSign, diedPos )
			order = 0
			while order in self.__delaycbids : order += 1
			pyBossSign.getGui().materialFX = "COLOUR_EFF"
			self.__delaycbids[order] = BigWorld.callback( 30, Functor( self.__delayDisposeSign, id, order ) )
			
	def __onsetBaseOrTowerSpawnPos( self, id, className, spawnPos, relation, signType ):
		"""
		设置基地、防御塔初始位置
		"""
		if id in self.__pyMonsterSigns:
			pyMonsterSign = self.__pyMonsterSigns[ id ]
		else:
			pyMonsterSign = Sign( self, className, signType, relation )
			self.__pyMap.addPyChild( pyMonsterSign )
			self.__pyMonsterSigns[id] = pyMonsterSign
		if pyMonsterSign:
			self.__locateSign( pyMonsterSign, spawnPos )
			pyMonsterSign.setStyle(signType, relation )
		
	def __onsetMonsterDied( self, id ):
		"""
		防御塔、基地死亡
		"""
		if id in self.__pyMonsterSigns:
			pyMonsterSign = self.__pyMonsterSigns.get( id )
			pyMonsterSign.getGui().materialFX = "COLOUR_EFF"
			pyMonsterSign.onCancelFlash()
	
	def __onGetDamage( self, id, seconds ):
		"""
		友方防御塔或者基地受到一定伤害时图标闪烁
		"""
		pySign = None
		if self.__pyMonsterSigns.has_key( id ):
			pySign = self.__pyMonsterSigns[id]
		if pySign is not None:
			pySign.flash( seconds )
			
	
	def __delayDisposeSign( self, id, order ):
		"""
		30秒后延迟隐藏
		"""
		if id in self.__pyBossSigns:
			pyBossSign = self.__pyBossSigns.pop( id )
			pyBossSign.dispose()
			BigWorld.cancelCallback( self.__delaycbids.pop( order ) )
	
	def __onResolutionChanged( self, preReso ):
		"""
		当屏幕分辨率改变时被调用
		"""
		if not self.visible:return
#		self.__reboundMap()

	def __onReceiveEnemyPos( self, enemyId, pos ):
		"""
		更新敌人位置坐标
		"""
		pySign = None
		if enemyId in self.__pyRoleSigns:
			pySign = self.__pyRoleSigns[enemyId]
		else:
			pySign = Sign( self, enemyId, Sign.ST_ROLE, csdefine.RELATION_ANTAGONIZE )
			self.__pyRoleSigns[enemyId] = pySign
			self.__pyMap.addPyChild( pySign )
		self.__locateSign( pySign, pos )
	
	def __onDisposeEnemy( self, enemyId ):
		"""
		清除不在队友周围的敌人标记
		"""
		if enemyId in self.__pyRoleSigns:
			roleSign = self.__pyRoleSigns.pop( enemyId )
			self.delPyChild( roleSign )
			roleSign.dispose()

	# -------------------------------------------------
	def __reboundMap( self ) :
		"""
		改变分别率后重新设置地图的显示模式
		"""
		if self.__dspMode == self.__DM_ORIGIN :
			self.orginMapSize()
		else :
			self.adaptMapSize()

	def __update( self ) :
		"""
		定时更新地图所有标记
		"""
		if not rds.statusMgr.isInWorld() : return
		player = BigWorld.player()
		for id, teamMater in player.teamMember.items():
			if id == player.id:
				self.__rotatePointer( player )
				self.__locatePointer( player )
			else:
				pos = teamMater.position
				pySign = None
				if id in self.__pyRoleSigns:
					pySign = self.__pyRoleSigns[id]
				else:
					pySign = Sign( self, id, Sign.ST_ROLE, csdefine.RELATION_FRIEND )
					self.__pyRoleSigns[id] = pySign
					self.__pyMap.addPyChild( pySign )
				self.__locateSign( pySign, pos )
		for id, entity in BigWorld.entities.items():		#显示角色AOI范围内的其他玩家
			if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and \
			not id in player.teamMember:
				pos = entity.position
				player.baoZangBroadCastEnemyPos( id, pos )
				if not id in self.__AoIRoleIDs:
					self.__AoIRoleIDs.append( id )
		for id in self.__AoIRoleIDs:
			if not id in [entity.id for entity in player.entitiesInRange( csconst.ROLE_AOI_RADIUS, lambda entity : entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) )]:
				player.baoZangBroadCastDisposeEnemy( id )
				self.__AoIRoleIDs.remove( id )

	def __locateSign( self, pySign, pos ):
		"""
		设置 entity 标记的位置
		"""
		if pySign is None:return
		if self.__viewArea is None:return
		x, y = self.__viewArea.worldPoint2TexturePoint( pos )
		pySign.center = x*self.__scale
		pySign.middle = y*self.__scale
		pySign.setPosition( pos )
	
	def __rotatePointer( self, player ):
		"""
		设置玩家面向
		"""
		util.rotateGui( self.__pyPointer.getGui(), player.yaw )
		util.rotateGui( self.__pyCamera.getGui(), BigWorld.camera().direction.yaw )
		
	def __locatePointer( self, player ):
		"""
		设置玩家位置
		"""
		if self.__viewArea is None:return
		x, y = self.__viewArea.worldPoint2TexturePoint( player.position )
		self.__pyPointer.center = x*self.__scale
		self.__pyPointer.middle = y*self.__scale
		self.__pyCamera.center = x*self.__scale
		self.__pyCamera.middle = y*self.__scale
	
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )
	
	def orginMapSize( self ):
		"""
		设置地图大小为原始大小
		"""
		width, height = self.__viewSize
		cwidth, cheight = self.__pyMap.size
		if width < cwidth and height < cheight :
			self.adaptMapSize()
		else :
			self.__scale = 1.0
			self.__dspMode = self.__DM_ORIGIN

	def adaptMapSize( self ) :
		"""
		将地图大小设置为适应窗口大小
		"""
		width, height = self.__viewSize
		cwidth, cheight = self.__pyMap.size
		scaleX = cwidth / width
		scaleY = cheight / height
		if abs( scaleX ) < abs( scaleY ) :
			self.__scale = scaleX
		else :
			self.__scale = scaleY
		self.__dspMode = self.__DB_ADATPED
	
	def onLeaveWorld( self ) :
		self.hide()
	
	def show( self ):
		Timer.cancel( self.__updateTimerID )
		self.__updateTimerID = Timer.addTimer(0, 3.0, self.__update )
		RootGUI.show( self )

	def hide( self ) :
		RootGUI.hide( self )
		Timer.cancel( self.__updateTimerID )
		self.__updateTimerID = 0
		for pyRoleSign in self.__pyRoleSigns.values():
			pyRoleSign.dispose()
		for pyBossSign in self.__pyBossSigns.values():
			pyBossSign.dispose()
		for pyMonsterSign in self.__pyMonsterSigns.values():
			self.delPyChild( pyMonsterSign )
			pyMonsterSign.dispose()
		self.__pyRoleSigns = {}
		self.__pyBossSigns = {}
		self.__pyMonsterSigns = {}
		self.__delaycbids = {}

# --------------------------------------------------------------------
# implement sign
# --------------------------------------------------------------------
import Timer
class Sign( Control ) :
	
	ST_ROLE							= 0x00
	ST_NPC							= 0x01
	ST_MONSTER_BELONG_TEAM_BASE		= 0x02	#基地
	ST_MONSTER_BELONG_TEAM_TOWER	= 0x03	#防御塔
	
	#类型层次排列，玩家>boss >基地 >防御塔
	TYPE_LEVEL = { "role": 0.7,		
				"npc":0.75,
				"base": 0.8,
				"tower":0.85 }

	def __init__( self, pyMap, className, style, relation ) :
		self.sign_ = GUI.Simple( "" )
#		self.sign_.tiled = True
		Control.__init__( self, self.sign_ )
		self.setToDefault()
		self.sign_.horizontalAnchor = "CENTER"
		self.sign_.verticalAnchor = "CENTER"
		self.__pyMap = pyMap
		self.className_ = className
		self.style_ = style
		self.flashTimerID = 0
		self.flashTime = 0
		self.isFlashing = False
		self.entityPos = (0, 0, 0)
		self.size = ( 12, 12 )	

		self.crossFocus = True
		self.setStyle( style, relation )

	def dispose( self ) :
		self.className_ = ""
		Control.dispose( self )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def getDescription_( self ) :
		"""
		获取 entity 描述
		"""
		name = ""
		if self.style_ in [ self.ST_NPC, self.ST_MONSTER_BELONG_TEAM_BASE, self.ST_MONSTER_BELONG_TEAM_TOWER ]:
			npcData = rds.npcDatasMgr.getNPC( self.className_ )
			if npcData is None:return
			name = npcData.getName()
		else:
			entity = BigWorld.entities.get( self.className_ )
			if entity is None:return
			name = entity.getName()
		return name

	# -------------------------------------------------
	def onMouseEnter_( self ) :
		tips = "@A{C}"
		tips += self.getDescription_()
		px, py, pz = self.entityPos
		tips += "%d, %d" % ( px, pz )
		toolbox.infoTip.showESignTips( self, tips )

	def onMouseLeave_( self ) :
		toolbox.infoTip.hide()

	# -------------------------------------------------
	def setStyle( self, style, relation ) :
		"""
		设置外观 以及层次
		"""
		player = BigWorld.player()
		if style == self.ST_ROLE:
			self.gui.position.z = self.TYPE_LEVEL.get( "role" )
			texture = "guis/general/minimap/fd_role.dds"
			if relation == csdefine.RELATION_ANTAGONIZE:
				texture = "guis/general/minimap/em_role.dds"
		elif style == self.ST_NPC:
			self.gui.position.z = self.TYPE_LEVEL.get( "npc" )
			texture = "guis/general/minimap/fd_npc.dds"
			if relation == csdefine.RELATION_ANTAGONIZE:
				texture = "guis/general/minimap/em_npc.dds"
		elif style == self.ST_MONSTER_BELONG_TEAM_BASE:
			self.gui.position.z = self.TYPE_LEVEL.get( "base" )
			texture = "guis/general/minimap/fd_base.dds"
			if relation == csdefine.RELATION_ANTAGONIZE:
				texture = "guis/general/minimap/em_base.dds"
		elif style == self.ST_MONSTER_BELONG_TEAM_TOWER:
			self.gui.position.z = self.TYPE_LEVEL.get( "tower" )
			texture = "guis/general/minimap/fd_tower.dds"
			if relation == csdefine.RELATION_ANTAGONIZE:
				texture = "guis/general/minimap/em_tower.dds"
				
		if not self.isFlashing:	
			self.texture = texture
			parent = self.getGui().parent
			if parent : parent.reSort()
	
	def setPosition( self, pos ):
		"""
		更新坐标
		"""
		self.entityPos = pos
		
	def flash( self, seconds ):
		"""
		图标闪烁
		"""
		Timer.cancel( self.flashTimerID)
		self.flashTimerID = 0
		self.flashTime = seconds
		self.flashTimerID = Timer.addTimer( 0, 1, self.__onFlash )
		
	def __onFlash( self ):
		self.flashTime -= 1
		if self.flashTime <= 0:
			self.onCancelFlash()
		elif self.texture.endswith( "fd_base.dds" ) and not self.isFlashing:
			self.isFlashing = True
			self.size = ( 32, 32 )
			self.texture = "guis/general/minimap/flash_fd_base.texanim"
		elif self.texture.endswith( "fd_tower.dds" ) and not self.isFlashing:
			self.isFlashing = True
			self.size = ( 32, 32 )
			self.texture = "guis/general/minimap/flash_fd_tower.texanim"
		
			
	def onCancelFlash( self ):
		Timer.cancel( self.flashTimerID )
		self.isFlashing = False
		self.flashTimerID = 0
		self.flashTime = 0
		if self.texture.endswith( "fd_base.texanim" ):
			self.size = ( 12, 12 )
			self.texture = "guis/general/minimap/fd_base.dds"
		if self.texture.endswith( "fd_tower.texanim" ):
			self.size = ( 12, 12 )
			self.texture = "guis/general/minimap/fd_tower.dds"
	