# -*- coding: gb18030 -*-
#
# $Id: SkillBox.py,v 1.41 2008-07-22 03:20:39 yangkai Exp $

"""
技能栏 cell 部分

2005/04/28 : writen by penghuawei( for role )
2007/12/06 : huangyongwei let it implemented by pet also
"""

import BigWorld
import csstatus
from bwdebug import *
from Resource.SkillLoader import g_skills
import csdefine
import csconst
import SkillTargetObjImpl
from ObjectScripts.GameObjectFactory import g_objFactory



class SkillBox:
	def __init__( self ):
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def initSkills( self ):
		"""
		实现技能效果。
		"""
		for skillID in self.attrSkillBox:
			self._attachSkill( skillID )

	def getSkills( self ):
		"""
		real entity method.
		获取玩家的技能列表

		@return: array of SKILLID
		"""
		return self.attrSkillBox

	def hasSkill( self, skillID ):
		"""
		real entity method.
		判断是否有指定的技能

		@return: BOOL
		"""
		for tempSkillID in self.attrSkillBox:	# 如果存在级别高于skillID的同类技能,也认为entity具有此技能15:17 2008-12-2,wsf
			if tempSkillID / 1000 == skillID / 1000 and skillID % 1000 <= tempSkillID % 1000:
				return True
		return False
		#return skillID in self.attrSkillBox

	# -------------------------------------------------
	def addSkill( self, skillID ):
		"""
		real entity method.
		增加一个技能。
		@param skillID:	要增加的技能标识
		@type skillID:	int
		@return:		是否成功
		@rtype:			bool
		"""
		if skillID in self.attrSkillBox:
			WARNING_MSG( "%s(%i): skill %i already exist." % (self.getName(), self.id, skillID ) )
			return False
		
		if self._attachSkill( skillID ):
			self.attrSkillBox.append( skillID )
			self.client.onAddSkill( skillID )
			return True
		return False


	def _attachSkill( self, skillID ):
		"""
		"""
		if g_skills.has( skillID ):
			try:
				g_skills[skillID].attach( self )
				return True
			except:
				EXCEHOOK_MSG("%s(%i):initSkill %i wrong, pass" % (self.getName(), self.id, skillID ) )
				return False
		else:
			WARNING_MSG( "%s(%i): skill %i not exist, remove it now." % (self.getName(), self.id, skillID ) )
			return False


	def removeSkill( self, skillID ):
		"""
		real entity method.
		去除一个技能。
		@param skillID:	要去除的技能标识
		@type skillID:	string
		@return:		是否成功
		@rtype:			bool
		"""
		try:
			idx = self.attrSkillBox.index( skillID )
		except ValueError:
			WARNING_MSG( "%s(%i): skill %i not exist." % (self.getName(), self.id, skillID ) )
			return False

		self.client.onRemoveSkill( skillID )
		# 删除技能效果
		try:
			g_skills[skillID].detach( self )
		except KeyError:
			WARNING_MSG( "%s(%i): skill %i release fail." % (self.getName(), self.id, skillID ) )

		# 必须先移去skill技能后才删除
		self.attrSkillBox.pop( idx )
		return True

	def updateSkill( self, oldSkillID, newSkillID ):
		"""
		更新一个技能（从一个技能ID改为另一个技能ID）

		@type oldSkillID: SKILLID
		@type newSkillID: SKILLID
		"""
		# 获取旧技能索引
		try:
			idx = self.attrSkillBox.index( oldSkillID )
		except ValueError:
			WARNING_MSG( "%s(%i): skill %i not exist." % (self.getName(), self.id, oldSkillID ) )
			return False

		try:
			self.attrSkillBox[idx] = newSkillID
		except TypeError, errstr:
			ERROR_MSG( "update skill error %s(%i): %s" % (self.getName(), self.id, errstr) )
			return False
		self.client.onUpdateSkill( oldSkillID, newSkillID )

		# 删除旧技能效果
		self.setTemp( "SAME_TYPE_SKILL_REPLACE", True )
		try:
			g_skills[oldSkillID].detach( self )
		except KeyError:
			WARNING_MSG( "%s(%i): skill %i release fail." % (self.getName(), self.id, oldSkillID ) )
		self.setTemp( "SAME_TYPE_SKILL_REPLACE", False )

		# 触发新技能效果
		try:
			g_skills[newSkillID].attach( self )
		except KeyError:
			WARNING_MSG( "%s(%i): skill %i init fail." % (self.getName(), self.id, newSkillID ) )
		return True

	def removeAllSkill( self ):
		"""
		删除所有技能(仅用于GM命令)
		"""
		for skillID in list( self.attrSkillBox ):
			self.removeSkill( skillID )


	# ----------------------------------------------------------------
	# exposed methods
	# ----------------------------------------------------------------
	def useSpell( self, srcEntityID, skillID, target ):
		"""
		Exposed method.
		请求向某人的物品施法，所有player法术由此进。

		@param  skillID: 法术标识符
		@type   skillID: INT16
		@param targetID: 目标entityID
		@type  targetID: OBJECT_ID
		"""
		if not self.hackVerify_( srcEntityID ) : return				# implements in Role.py( by hyw )

		#如果处在不允许使用自身技能的状态下
		flag = self.queryTemp( "NOT_USE_SELF_SKILL_FLAG", 0 )
		if flag and self.hasSkill( skillID ) :
			return
			
		if self.attrTriggerSpell.has_key(skillID) and self.attrTriggerSpell[skillID]["skillID"] != 0: #是否是触发技能
			skillID = self.attrTriggerSpell[skillID]["skillID"]

		if self.hasFlag( csdefine.ROLE_FLAG_AREA_SKILL_ONLY ):
			self.statusMessage( csstatus.USE_SPACE_SPELL_NOLY )
			return

		if self.isState( csdefine.ENTITY_STATE_VEND ):	# 摆摊状态不允许释放任何技能
			self.statusMessage( csstatus.SKILL_STATE_VEND )
			return

		if skillID not in csconst.SKILL_ID_ACTIONS and not self.hasSkill( skillID ):
			printStackTrace()
			ERROR_MSG( "%s(%i): skill not has. %i" % (self.getName(), self.id, skillID) )
			self.client.spellInterrupted( skillID, csstatus.SKILL_NOT_EXIST )
			return
		if target is None or target.getObject() == None:
			ERROR_MSG( "target is lost!" )
			self.client.spellInterrupted( skillID, csstatus.SKILL_MISS_TARGET )
			return
		state = self.castSpell( skillID, target )
		if state != csstatus.SKILL_GO_ON:
			INFO_MSG( "%i: skill %i use state = %i." % ( self.id, skillID, state ) )
			self.client.spellInterrupted( skillID, state )
			return

		LOG_MSG( "databaseID(%i), playerName(%s), playerLevel(%i), skillID(%i), skillName(%s)"\
			%( self.databaseID, self.getName(), self.level, skillID, g_skills[skillID].getName() ) )
			
	def useSpaceSpell( self, srcEntityID, skillID, target ):
		"""
		Exposed method.
		使用空间技能，请求向某人的物品施法
		
		@param  skillID: 法术标识符
		@type   skillID: INT16
		@param target: 施法对象
		@type  target: SKILLTARGETOBJ
		"""
		if not self.hackVerify_( srcEntityID ) : return
		flag = self.queryTemp("FLY_TEL_SKILL_FLAG", 0 )
		spaceScript = g_objFactory.getObject( self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		if ( not spaceScript.canUseSkill( self, skillID ) ) and ( not flag ):
			ERROR_MSG( "player( %s ) can not use skill in this space." % self.getName() )
			return
		if target is None or target.getObject() == None:
			ERROR_MSG( "target is lost!" )
			self.client.spellInterrupted( skillID, csstatus.SKILL_MISS_TARGET )
			return
		state = self.castSpell( skillID, target )
		if state != csstatus.SKILL_GO_ON:
			INFO_MSG( "%i: skill %i use state = %i." % ( self.id, skillID, state ) )
			self.client.spellInterrupted( skillID, state )
			return
			
		LOG_MSG( "databaseID(%i), playerName(%s), playerLevel(%i), skillID(%i), skillName(%s)"\
			%( self.databaseID, self.getName(), self.level, skillID, g_skills[skillID].getName() ) )
			
	# -------------------------------------------------
	def requestRemoveBuff( self, srcEntityID, index ) :
		"""
		Exposed method.
		请求删除良性 buff

		@param  buffUID: 要删除的 buff uid
		@type   buffUID: UID
		"""
		if not self.hackVerify_( srcEntityID ) : return				# implements in Role.py( by hyw )
		self.removeBuffByIndex( index, [csdefine.BUFF_INTERRUPT_REQUEST_CANCEL] )

	def onDestroy( self ):
		"""
		entity销毁通知,技能detach
		"""
		for skillID in self.attrSkillBox:
			if g_skills.has( skillID ):
				g_skills[skillID].detach( self )

	def beforePostureChange( self, newPosture ):
		"""
		姿态改变之前，卸除当前姿态的被动技能效果
		
		@param newPosture : 改变后的姿态
		"""
		for skillID in self.attrSkillBox:
			if not g_skills.has( skillID ):
				ERROR_MSG( "%s(%i): skill %i not exist, remove it now." % (self.getName(), self.id, skillID ) )
				self.attrSkillBox.remove( skillID )
				continue
			# 如果加载技能失败，则跳过，继续加载其他技能
			try:
				skill = g_skills[skillID]
			except:
				EXCEHOOK_MSG("%s(%i):loadSkill %i wrong, pass" % (self.getName(), self.id, skillID ) )
				continue

			if skill.getType() != csdefine.BASE_SKILL_TYPE_POSTURE_PASSIVE:
				continue
			if skill.getEffectPosture() == self.getPosture():
				skill.detach( self )
				
	def afterPostureChange( self, oldPosture ):
		"""
		姿态改变之后，附着当前姿态技能效果
		
		@param oldPosture : 改变前的姿态
		"""
		for skillID in self.attrSkillBox:
			if not g_skills.has( skillID ):
				ERROR_MSG( "%s(%i): skill %i not exist, remove it now." % (self.getName(), self.id, skillID ) )
				self.attrSkillBox.remove( skillID )
				continue
			try:
				skill = g_skills[skillID]
			except:
				ERROR_MSG( "%s(%i): skill %i is not right !" % (self.getName(), self.id, skillID ) )
				continue
			if skill.getType() != csdefine.BASE_SKILL_TYPE_POSTURE_PASSIVE:
				continue
			if skill.getEffectPosture() == self.getPosture():
				skill.attach( self )
				

	def addSavedBuff( self, buff ):
		"""
		添加一个Buff。

		@param buff			:	instance of BUFF
		@type  buff			:	BUFF
		"""
		buff[ "index" ] = self.newBuffIndex()
		casterID = buff["caster"]
		spell = buff["skill"]
		spell.doReload( self, buff )
		self.attrBuffs.append( buff )
		casterID = buff["caster"]
		self.onAddBuff( buff )

		if self.buffTimer == 0:
			self.buffTimer = self.addTimer( 1, 1, ECBExtend.BUFF_TIMER_CBID )



# SkillBox.py
