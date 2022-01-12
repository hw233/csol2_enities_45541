# -*- coding: gb18030 -*-
#
#作用区域移动 技能的客户端脚本
# edit by wuxo 2012-4-27

import csdefine
import BigWorld
from gbref import rds
import SkillTargetObjImpl
from SpellBase import Spell
from config.client.NpcSkillName import Datas as npcSkillName

class Spell_MoveEffect( Spell ):
	def __init__( self ):
		"""
		从sect构造SkillBase
		@param sect:			技能配置文件的XML Root Section
		@type sect:				DataSection
		"""
		Spell.__init__( self )
		self._offsetYaw = 0.0
		self.eid = 0
		self.caster = None
		self._isOnce = None	
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		if dict[ "param2" ] != "":
			self._offsetYaw = float( dict[ "param2" ] )
		else:
			self._offsetYaw = 0.0
		self._isOnce = bool( int( dict[ "param3" ] ) )
		
		
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

		pos = targetObject.getObjectPosition()
		model = caster.getModel()
		if model:
			scale = model.scale[0]
			k = scale * model.height * 0.8
		dPos = ( pos[0], pos[1] + k, pos[2] )
		self.eid = BigWorld.createEntity( "CameraEntity", caster.spaceID, 0, dPos, (0,0,0), {"isFall":False} )
		BigWorld.callback(0.1, self.onCreate)
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

	def isMoveSpell( self ):
		"""
		判断是否是作用区域技能
		@return: BOOL
		"""
		return True
	
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