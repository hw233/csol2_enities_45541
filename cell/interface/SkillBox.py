# -*- coding: gb18030 -*-
#
# $Id: SkillBox.py,v 1.41 2008-07-22 03:20:39 yangkai Exp $

"""
������ cell ����

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
		ʵ�ּ���Ч����
		"""
		for skillID in self.attrSkillBox:
			self._attachSkill( skillID )

	def getSkills( self ):
		"""
		real entity method.
		��ȡ��ҵļ����б�

		@return: array of SKILLID
		"""
		return self.attrSkillBox

	def hasSkill( self, skillID ):
		"""
		real entity method.
		�ж��Ƿ���ָ���ļ���

		@return: BOOL
		"""
		for tempSkillID in self.attrSkillBox:	# ������ڼ������skillID��ͬ�༼��,Ҳ��Ϊentity���д˼���15:17 2008-12-2,wsf
			if tempSkillID / 1000 == skillID / 1000 and skillID % 1000 <= tempSkillID % 1000:
				return True
		return False
		#return skillID in self.attrSkillBox

	# -------------------------------------------------
	def addSkill( self, skillID ):
		"""
		real entity method.
		����һ�����ܡ�
		@param skillID:	Ҫ���ӵļ��ܱ�ʶ
		@type skillID:	int
		@return:		�Ƿ�ɹ�
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
		ȥ��һ�����ܡ�
		@param skillID:	Ҫȥ���ļ��ܱ�ʶ
		@type skillID:	string
		@return:		�Ƿ�ɹ�
		@rtype:			bool
		"""
		try:
			idx = self.attrSkillBox.index( skillID )
		except ValueError:
			WARNING_MSG( "%s(%i): skill %i not exist." % (self.getName(), self.id, skillID ) )
			return False

		self.client.onRemoveSkill( skillID )
		# ɾ������Ч��
		try:
			g_skills[skillID].detach( self )
		except KeyError:
			WARNING_MSG( "%s(%i): skill %i release fail." % (self.getName(), self.id, skillID ) )

		# ��������ȥskill���ܺ��ɾ��
		self.attrSkillBox.pop( idx )
		return True

	def updateSkill( self, oldSkillID, newSkillID ):
		"""
		����һ�����ܣ���һ������ID��Ϊ��һ������ID��

		@type oldSkillID: SKILLID
		@type newSkillID: SKILLID
		"""
		# ��ȡ�ɼ�������
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

		# ɾ���ɼ���Ч��
		self.setTemp( "SAME_TYPE_SKILL_REPLACE", True )
		try:
			g_skills[oldSkillID].detach( self )
		except KeyError:
			WARNING_MSG( "%s(%i): skill %i release fail." % (self.getName(), self.id, oldSkillID ) )
		self.setTemp( "SAME_TYPE_SKILL_REPLACE", False )

		# �����¼���Ч��
		try:
			g_skills[newSkillID].attach( self )
		except KeyError:
			WARNING_MSG( "%s(%i): skill %i init fail." % (self.getName(), self.id, newSkillID ) )
		return True

	def removeAllSkill( self ):
		"""
		ɾ�����м���(������GM����)
		"""
		for skillID in list( self.attrSkillBox ):
			self.removeSkill( skillID )


	# ----------------------------------------------------------------
	# exposed methods
	# ----------------------------------------------------------------
	def useSpell( self, srcEntityID, skillID, target ):
		"""
		Exposed method.
		������ĳ�˵���Ʒʩ��������player�����ɴ˽���

		@param  skillID: ������ʶ��
		@type   skillID: INT16
		@param targetID: Ŀ��entityID
		@type  targetID: OBJECT_ID
		"""
		if not self.hackVerify_( srcEntityID ) : return				# implements in Role.py( by hyw )

		#������ڲ�����ʹ�������ܵ�״̬��
		flag = self.queryTemp( "NOT_USE_SELF_SKILL_FLAG", 0 )
		if flag and self.hasSkill( skillID ) :
			return
			
		if self.attrTriggerSpell.has_key(skillID) and self.attrTriggerSpell[skillID]["skillID"] != 0: #�Ƿ��Ǵ�������
			skillID = self.attrTriggerSpell[skillID]["skillID"]

		if self.hasFlag( csdefine.ROLE_FLAG_AREA_SKILL_ONLY ):
			self.statusMessage( csstatus.USE_SPACE_SPELL_NOLY )
			return

		if self.isState( csdefine.ENTITY_STATE_VEND ):	# ��̯״̬�������ͷ��κμ���
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
		ʹ�ÿռ似�ܣ�������ĳ�˵���Ʒʩ��
		
		@param  skillID: ������ʶ��
		@type   skillID: INT16
		@param target: ʩ������
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
		����ɾ������ buff

		@param  buffUID: Ҫɾ���� buff uid
		@type   buffUID: UID
		"""
		if not self.hackVerify_( srcEntityID ) : return				# implements in Role.py( by hyw )
		self.removeBuffByIndex( index, [csdefine.BUFF_INTERRUPT_REQUEST_CANCEL] )

	def onDestroy( self ):
		"""
		entity����֪ͨ,����detach
		"""
		for skillID in self.attrSkillBox:
			if g_skills.has( skillID ):
				g_skills[skillID].detach( self )

	def beforePostureChange( self, newPosture ):
		"""
		��̬�ı�֮ǰ��ж����ǰ��̬�ı�������Ч��
		
		@param newPosture : �ı�����̬
		"""
		for skillID in self.attrSkillBox:
			if not g_skills.has( skillID ):
				ERROR_MSG( "%s(%i): skill %i not exist, remove it now." % (self.getName(), self.id, skillID ) )
				self.attrSkillBox.remove( skillID )
				continue
			# ������ؼ���ʧ�ܣ�������������������������
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
		��̬�ı�֮�󣬸��ŵ�ǰ��̬����Ч��
		
		@param oldPosture : �ı�ǰ����̬
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
		���һ��Buff��

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
