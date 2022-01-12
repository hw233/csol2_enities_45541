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
	Ӣ������С��ͼ
	"""
	__DM_ORIGIN		= 1									# ԭʼ��Сģʽ
	__DB_ADATPED	= 2									# ��Ӧ��Ļ��Сģʽ
	
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
		self.__pyRoleSigns = {}							# ��ұ��
		self.__pyBossSigns = {}							# boss���
		self.__pyMonsterSigns = {}						# ��ӵ�С��ͼ�Ĺ����־
		self.__updateTimerID = 0
		self.__viewArea = None
		self.__scale = 1.0

		self.__dspMode = self.__DM_ORIGIN				# ��ͼ����ʾģʽ
		self.__delaycbids = {}
		self.__AoIRoleIDs = []							# AOI��Χ��ɫid

		self.__initialize( frm )

		self.__triggers = {}
		self.__registerTriggers()
	
	def __initialize( self, frm ):
		"""
		��ʼ����ͼ
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
		self.__triggers["EVT_ON_MONSTER_GET_DAMAGE"]	= self.__onGetDamage		#������������ܵ�һ���˺�ʱͼ����˸
		
		for key in self.__triggers :
			ECenter.registerEvent( key, self )
			
	# ----------------------------------------------------------------
	def __onShowLoLMinMap( self, spaceLabel ):
		"""
		��ʾӢ�����˵�ͼ
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
		����Ӣ�����˵�ͼ
		"""
		self.hide()
	
	def __onSetMonsterSpawnPos( self, id, className, spawnPos, relation, signType ):
		"""
		���ù����ʼλ�ã�boss�������������أ�
		"""
		if signType == Sign.ST_NPC:		
			self.__onUpdateBossPos( id, className, spawnPos, relation )
		else:
			self.__onsetBaseOrTowerSpawnPos( id, className, spawnPos, relation, signType )		
	
	def __onUpdateBossPos( self, id, className,pos, relation ):
		"""
		����boss����
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
		boss ������ ��������ʱ
		"""
		if self.__pyBossSigns.has_key( id ):
			self.__onsetBossDiedPos( id, className, spawnPos, diedPos, relation )
		else:
			self.__onsetMonsterDied( id )
	 
	def __onsetBossDiedPos( self, id, className, spawnPos, diedPos, relation ):
		"""
		����boss����λ��,30�����ʧ
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
		���û��ء���������ʼλ��
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
		����������������
		"""
		if id in self.__pyMonsterSigns:
			pyMonsterSign = self.__pyMonsterSigns.get( id )
			pyMonsterSign.getGui().materialFX = "COLOUR_EFF"
			pyMonsterSign.onCancelFlash()
	
	def __onGetDamage( self, id, seconds ):
		"""
		�ѷ����������߻����ܵ�һ���˺�ʱͼ����˸
		"""
		pySign = None
		if self.__pyMonsterSigns.has_key( id ):
			pySign = self.__pyMonsterSigns[id]
		if pySign is not None:
			pySign.flash( seconds )
			
	
	def __delayDisposeSign( self, id, order ):
		"""
		30����ӳ�����
		"""
		if id in self.__pyBossSigns:
			pyBossSign = self.__pyBossSigns.pop( id )
			pyBossSign.dispose()
			BigWorld.cancelCallback( self.__delaycbids.pop( order ) )
	
	def __onResolutionChanged( self, preReso ):
		"""
		����Ļ�ֱ��ʸı�ʱ������
		"""
		if not self.visible:return
#		self.__reboundMap()

	def __onReceiveEnemyPos( self, enemyId, pos ):
		"""
		���µ���λ������
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
		������ڶ�����Χ�ĵ��˱��
		"""
		if enemyId in self.__pyRoleSigns:
			roleSign = self.__pyRoleSigns.pop( enemyId )
			self.delPyChild( roleSign )
			roleSign.dispose()

	# -------------------------------------------------
	def __reboundMap( self ) :
		"""
		�ı�ֱ��ʺ��������õ�ͼ����ʾģʽ
		"""
		if self.__dspMode == self.__DM_ORIGIN :
			self.orginMapSize()
		else :
			self.adaptMapSize()

	def __update( self ) :
		"""
		��ʱ���µ�ͼ���б��
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
		for id, entity in BigWorld.entities.items():		#��ʾ��ɫAOI��Χ�ڵ��������
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
		���� entity ��ǵ�λ��
		"""
		if pySign is None:return
		if self.__viewArea is None:return
		x, y = self.__viewArea.worldPoint2TexturePoint( pos )
		pySign.center = x*self.__scale
		pySign.middle = y*self.__scale
		pySign.setPosition( pos )
	
	def __rotatePointer( self, player ):
		"""
		�����������
		"""
		util.rotateGui( self.__pyPointer.getGui(), player.yaw )
		util.rotateGui( self.__pyCamera.getGui(), BigWorld.camera().direction.yaw )
		
	def __locatePointer( self, player ):
		"""
		�������λ��
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
		���õ�ͼ��СΪԭʼ��С
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
		����ͼ��С����Ϊ��Ӧ���ڴ�С
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
	ST_MONSTER_BELONG_TEAM_BASE		= 0x02	#����
	ST_MONSTER_BELONG_TEAM_TOWER	= 0x03	#������
	
	#���Ͳ�����У����>boss >���� >������
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
		��ȡ entity ����
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
		������� �Լ����
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
		��������
		"""
		self.entityPos = pos
		
	def flash( self, seconds ):
		"""
		ͼ����˸
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
	