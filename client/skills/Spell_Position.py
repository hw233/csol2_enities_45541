# -*- coding: gb18030 -*-
#
# $Id: Spell_Position.py,v 1.1 2008-07-24 08:40:51 kebiao Exp $
#modify by wuxo 2012-2-22
"""
Spell技能类。
"""
import BigWorld
import Define
import keys
from bwdebug import *
import gbref 	
from gbref import rds
from StatusMgr import BaseStatus
from UnitSelect import unitSelect
from SpellBase import *
import SkillTargetObjImpl
import csstatus
import csdefine
import csarithmetic
from config.client.NpcSkillName import Datas as npcSkillName

"""
向一个位置施法， 当player请求对位置施法时， 客户端调用技能通用结构spell, 我们在spell中通知客户端上层
请求对位置施法， 上层获得鼠标位置后通过SkillTargetObjImpl.createTargetObjPosition( (0,0,0) )封装一个target
调用技能的spellToPosition接口即可。
"""
class Spell_Position( Spell ):
	def __init__( self ):
		"""
		从sect构造SkillBase
		@param sect:			技能配置文件的XML Root Section
		@type sect:				DataSection
		"""
		Spell.__init__( self )
		self.modelPath = "gzawu/unitselect/unitselect.model"	#给一个默认的光圈路径
		self.modelScale = (1,1,1) #缩放系数

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		self.param3 = str( dict["param3"] ).split(";")
		if len(self.param3) >= 2:
			self.modelPath = self.param3[-2]
			self.modelScale = eval(self.param3[-1])

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		if caster.isInHomingSpell:
			return csstatus.SKILL_CANT_CAST
		return csstatus.SKILL_GO_ON

	def spell( self, caster, target ):
		"""
		向服务器发送Spell请求。

		@param caster:		施放者Entity
		@type  caster:		Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT, see also csdefine.SKILL_*
		"""
		rds.statusMgr.setToSubStatus( Define.GST_IN_WORLD, SpellStatus(self ) )		# 进入 Spell 子状态

	def validPosition( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		return Spell.useableCheck( self, caster, target )

	def spellToPosition( self, caster, target ):
		"""
		向服务器发送Spell请求。
		
		@param caster:		施放者Entity
		@type  caster:		Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT, see also csdefine.SKILL_*
		"""
		assert target.getType() == csdefine.SKILL_TARGET_OBJECT_POSITION, "target is not position."
		Spell.spell( self, caster, target )

	def rotate( self, caster, receiver ):
		pass

	def getSpellScale(self):
		"""
		获得光圈路径和缩放系数
		"""
		return self.modelScale

	def getModelpath(self):
		"""
		获得光圈模型路径
		"""
		return self.modelPath

class Spell_ChasePosition( Spell_Position ):
	def __init__( self ):
		"""
		从sect构造SkillBase
		@param sect:			技能配置文件的XML Root Section
		@type sect:				DataSection
		"""
		Spell_Position.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell_Position.init( self, dict )
		self.eid = 0
		self.caster = None

	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		caster.hasCast = True
		skillID = self.getID()

		# 对动作而言，我只会播放一次
		self.pose.cast( caster, skillID, targetObject )

		dstPos = targetObject.getObjectPosition()
		endDstPos = csarithmetic.getCollidePoint( caster.spaceID, dstPos, dstPos + (0,-20,0) )	 # 作碰撞，防止其停留在空中
		self.eid = BigWorld.createEntity( "CameraEntity", caster.spaceID, 0, endDstPos, (0,0,0), {} )
		BigWorld.callback(0.01, self.onCreate)
		self.caster = caster

		# 技能名称显示
		speller = caster  #重新赋值，防止后面调用混乱
		if hasattr( speller, 'getOwner' ):
			speller = speller.getOwner()

		player = BigWorld.player()
		if player is None: return
		if speller is None: return

		if player.position.distTo( speller.position ) > 20: return
		if hasattr( caster, "className" ):
			sk_id = str( skillID )[:-3]
			if not sk_id: return		# 如果为空，直接返回
			orgSkillID = int( sk_id )	# 支持配置表可变等级NPC技能填写
			skillIDs = npcSkillName.get( caster.className, [] )
			if orgSkillID in skillIDs or skillID in skillIDs:
		 		caster.showSkillName( skillID )
				return
		if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or caster.isEntityType( csdefine.ENTITY_TYPE_PET ):
			caster.showSkillName( skillID )

	def onCreate(self):
		"""
		创建后回调
		"""
		if self.eid:
			en = BigWorld.entity( self.eid )
			en.model = BigWorld.Model("")
			t = SkillTargetObjImpl.createTargetObjEntity(en)
			rds.skillEffect.playCastEffects( self.caster, t, self.getID() )
			BigWorld.callback( 30, self.ondestroy )

	def ondestroy(self):
		"""
		删除创建的实体
		"""
		BigWorld.destroyEntity( self.eid )

# --------------------------------------------------------------------
# Define.GST_IN_WORLD 状态中的子状态，进入这种状态后，鼠标左键按击事件
# 将会被该子状态截获。
# 210.05.15: by huangyongwei
# modify by wuxo 2012-2-22
# --------------------------------------------------------------------
class SpellStatus( BaseStatus ) :
	def __init__( self,spell ) :
		BaseStatus.__init__( self )							# 设置该状态下的鼠标形状，并锁定鼠标形状
		self.__spell = spell
		self.cbID = 0
		self.addSelect()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __leave( self ) :
		"""
		释放该状态
		"""
		if self.cbID != 0:
			BigWorld.cancelCallback( self.cbID )
		unitSelect.hideSpellSite()
		rds.statusMgr.leaveSubStatus( Define.GST_IN_WORLD, self.__class__ )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def handleKeyEvent( self, down, key, mods  ) :
		"""
		准备 spell 状态按键消息在此处理
		如果想截获哪个按键的消息，只要判断是指定按键并返回 True 即可。
		"""
		if rds.worldCamHandler.handleKeyEvent( down, key, mods ) :
			return True

		if rds.uiHandlerMgr.handleKeyEvent( down, key, mods ) :
			self.__leave()
			return False

		if key == keys.KEY_LEFTMOUSE and mods == 0 :						# 鼠标左键按下时被调用
			if down :
				player = BigWorld.player()
				pos = gbref.cursorToDropPoint()								# 获取鼠标按下时所击中的地面位置
				if pos is None: return True
				target = SkillTargetObjImpl.createTargetObjPosition( pos )	# 封装位置目标
				if self.__spell.validPosition( player, target ) == csstatus.SKILL_GO_ON :
					self.__spell.spellToPosition( player, target )
			else :
				self.__leave()
			return True
		elif key == keys.KEY_ESCAPE or key == keys.KEY_RIGHTMOUSE :		# 取消该子状态
			self.__leave()
			return True
		elif checkSkillShortcut( key, mods ) and down:
			self.__leave()
			return True

	def handleMouseEvent( self, dx, dy, dz ) :
		"""
		鼠标移动时被调用
		"""
		if rds.worldCamHandler.handleMouseEvent( dx, dy, dz ) :				# 旋转镜头中
			return True
		self.addSelect()

	def addSelect( self ):
		"""
		加光圈
		"""
		pos = gbref.cursorToDropPoint()		# 获取鼠标按下时所击中的地面位置
		if pos is None: return

		player = BigWorld.player()
		target = SkillTargetObjImpl.createTargetObjPosition( pos )
		if self.__spell.validPosition( player, target ) == csstatus.SKILL_GO_ON:
			unitSelect.setInRangeTexture()
		else:
			unitSelect.setOutOfRangeTexture()
		unitSelect.setSpellSize( 3.0 )
		unitSelect.setSpellSite( pos )
		if self.cbID != 0:
			BigWorld.cancelCallback( self.cbID )

		self.cbID = BigWorld.callback( 0.01, self.addSelect )

def checkSkillShortcut( key, mod ):
	"""
	判断按键是否是技能快捷键
	edit by wuxo
	"""
	sc = rds.shortcutMgr.getSkillbarSC()
	skillbars = []
	for i in sc:
		skillbars.append( i.shortcutString)
	if keys.shortcutToString( key, mod ) in skillbars:
		return True
	return False