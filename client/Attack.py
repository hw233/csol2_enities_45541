# -*- coding: gb18030 -*-

"""
implement role's attack action.

18:10 2009-2-6 : written by wangshufeng
"""

import BigWorld
import Math
import csdefine
import csstatus
import csconst
import csstatus_msgs as StatusMsgs
from config.client.msgboxtexts import Datas as mbmsgs

from AbstractTemplates import MultiLngFuncDecorator
import skills as Skill
from skills.Spell_Item import Spell_Item
import SkillTargetObjImpl
import GUIFacade
import Const
import Define
import ResMgr
from skills.Spell_Item import Spell_Item

from bwdebug import *
from Function import Functor
from keys import *
import gbref
from gbref import rds
import event.EventCenter as ECenter
from DroppedBox import DroppedBox
from MessageBox import showMessage
from MessageBox import MB_OK_CANCEL
from MessageBox import RS_OK
from MessageBox import MB_OK
import PetEpitome
import ItemTypeEnum
from items.ItemDataList import ItemDataList
from config.client.labels import ChatFacade as lbs_ChatFacade

g_items = ItemDataList.instance()

AutoFightConfig = {	"AutoFightConfig"	:	{},
					"plusSkillTarget"		:	[],
					"autoPlusSkillList"	:	[]}		# �ɹ����߱��棨�ؿͻ��˲�������Զ�ս��������Ϣ)
					

class languageDepart_AFEnter( MultiLngFuncDecorator ):
	"""
	�����԰汾���������� by ����
	"""
	@staticmethod
	def locale_default( autoFight, owner ):
		"""
		�����
		"""
		languageDepart_AFEnter.originalFunc( autoFight, owner )
		autoFight.persistentTimerID = BigWorld.callback( Const.AUTO_FIGHT_PERSISTENT_TIME, autoFight.cancel )

	@staticmethod
	def locale_big5( autoFight, owner ):
		"""
		�����
		"""
		languageDepart_AFEnter.originalFunc( autoFight, owner )
		if autoFight.owner.af_time_limit <= 0 and autoFight.owner.af_time_extra <= 0:
			autoFight.leave()
			autoFight.owner.statusMessage( csstatus.AUTO_FIGHT_TIME_LIMIT )
			return
		p_time = 0
		if autoFight.owner.af_time_extra > 0:
			p_time = autoFight.owner.af_time_extra
		else:
			p_time = autoFight.owner.af_time_limit
		autoFight.persistentTimerID = BigWorld.callback( p_time, autoFight.cancel )
		autoFight.owner.base.onEnterAutoFight()

class languageDepart_AFLeave( MultiLngFuncDecorator ):
	"""
	�����԰汾���������� by ����
	"""
	@staticmethod
	def locale_big5( autoFight ):
		"""
		�����
		"""
		languageDepart_AFLeave.originalFunc( autoFight )
		autoFight.owner.base.onLeaveAutoFight()

class AutoRestore:
	"""
	�Զ��ָ�
	"""
	def __init__( self ):
		"""
		"""
		self.__cfgPath = ""
		sect = self.getConfigSect()
		self.hpPercent = sect.readFloat( "Role_HP" ) # Ѫ����ʣ�����������ֵ�����Զ���Ѫ
		self.mpPercent = sect.readFloat( "Role_MP" ) # ħ��ֵ��ʣ�������ڴ�ֵ���Զ�ʹ����ҩ

	def restore( self, entity ):
		"""
		�ָ�entity
		"""

		# ����������������ж� by����
		if entity.getCurrentSpaceType() in Const.SPACE_FORBIT_AUTO_DRUG: return

		try:	# �ݴ���0����
			hpPercent = float( entity.HP ) / float( entity.HP_Max )
			mpPercent = float( entity.MP ) / float( entity.MP_Max )
		except:
			return

		# �Ƿ񵽲�Ѫ�������Ƿ��������Ʒ���Ƿ���Ʒ����CD
		if hpPercent < self.hpPercent:
			entity.qb_autoRestoreHP()

		if mpPercent < self.mpPercent:
			entity.qb_autoRestoreMP()

	def setHpPercent( self, hpPercent ):
		"""
		"""
		self.hpPercent = hpPercent
		self.__cfgSect.save()

	def setMpPercent( self, mpPercent ):
		"""
		"""
		self.mpPercent = mpPercent
		self.__cfgSect.save()

	def getHpPercent( self ):
		"""
		"""
		return self.hpPercent

	def getMpPercent( self ):
		"""
		"""
		return self.mpPercent

	def getConfigSect( self ) :
		"""
		��ȡ�Զ���Ѫ������������
		"""
		if self.__cfgPath != "" :
			ResMgr.purge( self.__cfgPath )
		accountName = rds.gameMgr.getCurrAccountInfo()["accountName"]
		roleName = rds.gameMgr.getCurrRoleHexName()
		self.__cfgPath = "account/%s/%s/auto_fight.xml" % ( accountName, roleName )
		self.__cfgSect = ResMgr.openSection( self.__cfgPath )
		if self.__cfgSect is None :
			self.__cfgSect = ResMgr.openSection( self.__cfgPath, True )
			self.__cfgSect.createSection( "Role_HP" )
			self.__cfgSect.createSection( "Role_MP" )
			self.__cfgSect.createSection( "Pet_HP" )
			self.__cfgSect.createSection( "Pet_MP" )
			self.__cfgSect.createSection( "isAutoConjure" )
			self.__cfgSect.createSection( "isAutoAddJoy" )
			self.__cfgSect.createSection( "isAutoPlus" )
			self.__cfgSect.createSection( "radius" )
			self.__cfgSect.createSection( "radiusAdd" )
			self.__cfgSect.createSection( "joyLess" )
			self.__cfgSect.createSection( "autoRepair" )
			self.__cfgSect.createSection( "autoReboin" )
			self.__cfgSect.createSection( "repairRate" )
			self.__cfgSect.createSection( "isAutoPickUp" )
			self.__cfgSect.createSection( "plusSkillTarget" )
			self.__cfgSect.createSection( "plusSkills" )
			self.__cfgSect.createSection( "isIgnorePickUp" )
			self.__cfgSect.createSection( "pickUpTypeList" )
			self.__cfgSect.createSection( "ignoredList" )
			self.__cfgSect.writeFloat( "Role_HP", 0.6 )
			self.__cfgSect.writeFloat( "Role_MP", 0.6 )
			self.__cfgSect.writeFloat( "Pet_HP", 0.6 )
			self.__cfgSect.writeFloat( "Pet_MP", 0.6 )
			self.__cfgSect.writeBool( "isAutoConjure", 0 )
			self.__cfgSect.writeBool( "isAutoAddJoy", 0 )
			self.__cfgSect.writeBool( "isAutoPlus", 0 )
			self.__cfgSect.writeInt( "radius", 0 )
			self.__cfgSect.writeInt( "radiusAdd", 15 )
			self.__cfgSect.writeInt( "joyLess", 0 )
			self.__cfgSect.writeBool( "autoRepair", 0 )
			self.__cfgSect.writeBool( "autoReboin", 0 )
			self.__cfgSect.writeInt( "repairRate", 0 )
			self.__cfgSect.writeBool( "isAutoPickUp", 0 )
			self.__cfgSect.writeVector3( "plusSkillTarget", (0, 0, 0) )
			self.__cfgSect.writeBool( "isIgnorePickUp", 1 )
			self.__cfgSect.writeString( "pickUpTypeList", "" )
			self.__cfgSect.writeString( "ignoredList", "" )
			self.__cfgSect.save()
		return self.__cfgSect
	
	def saveCfgSect( self ):
		"""
		��������
		"""
		self.__cfgSect.save()

class PetAutoRestore( AutoRestore ):
	"""
	�����Զ��ָ�
	"""
	def __init__( self ):
		"""
		"""
		AutoRestore.__init__( self )
		sect = AutoRestore().getConfigSect()
		self.hpPercent = sect.readFloat( "Pet_HP" )		# Ѫ����ʣ�����������ֵ�����Զ���Ѫ
		self.mpPercent = sect.readFloat( "Pet_MP" )		# ħ��ֵ��ʣ�������ڴ�ֵ���Զ�ʹ����ҩ

	def restore( self, entity ):
		"""
		���entity�Ƿ���Իָ�

		@param entity : ����entity
		"""
		try:	# �ݴ���0����
			hpPercent = float( entity.HP ) / float( entity.HP_Max )
			mpPercent = float( entity.MP ) / float( entity.MP_Max )
		except:
			return
		player = BigWorld.player()
		if hpPercent < self.hpPercent:
			player.qb_autoRestorePetHP()

		if mpPercent < self.mpPercent:
			player.qb_autoRestorePetMP()


class AttackArgumentFactory:
	"""
	����״̬������װ����
	"""
	def __init__( self ):
		"""
		"""
		pass

	@staticmethod
	def getAttackArgument( state, arg ):
		"""
		"""
		if state == Const.ATTACK_STATE_ONCE:
			attackArgument = OnceAttackArg( state, arg )
		elif state == Const.ATTACK_STATE_AUTO_CONFIRM_SPELL:
			attackArgument = AttackConfirmSpellArg( state, arg )
		elif state == Const.ATTACK_STATE_AUTO_SPELL_CURSOR:
			attackArgument = AttackConfirmSpellArg( state, arg )
		elif state == Const.ATTACK_STATE_SPELL_AND_HOMING:
			attackArgument = AttackHomingSpellArg( state, arg )
		else:
			attackArgument = None

		return attackArgument


class OnceAttackArg:
	"""
	ATTACK_STATE_ONCE״̬���в�����װʵ��
	"""
	def __init__( self, state, arg ):
		"""
		@param state :	����״̬
		@param arg :	����˹���״̬��Ҫ�Ĳ���
		"""
		self.param = arg[ 0 ]


class AttackConfirmSpellArg:
	"""
	ATTACK_STATE_AUTO_CONFIRM_SPELL״̬���в�����װʵ��
	"""
	def __init__( self, state, arg ):
		"""
		@param state :	����״̬
		@param arg :	����˹���״̬��Ҫ�Ĳ���
		"""
		self.param = arg[ 0 ]

class AttackHomingSpellArg:
	"""
	ATTACK_STATE_HOMING_SPELL״̬���в�����װʵ��
	"""
	def __init__( self, state, arg ):
		"""
		@param state :	����״̬
		@param arg :	����˹���״̬��Ҫ�Ĳ���
		"""
		self.param = arg[ 0 ]

class AutoFightArg:
	"""
	ATTACK_STATE_AUTO_FIGHT״̬���в�����װʵ��
	"""
	def __init__( self, state, arg ):
		"""
		@param state :	����״̬
		@param arg :	����˹���״̬��Ҫ�Ĳ���
		"""
		self.param = None


class AttackBase:
	"""
	����ʵ������
	"""
	def __init__( self, owner ):
		"""
		@param owner : ��ʵ���������ߣ�Ŀǰֻ���ǽ�ɫ��
		"""
		self.owner = owner

	def enter( self, attackArgument ):
		"""
		�����״̬��ĳ�ʼ��
		@param arg : �ⲿ������
		"""
		pass

	def leave( self ):
		"""
		�뿪��״̬ʱ��������
		"""
		pass

	def action( self ):
		"""
		�����״̬Ӧ��ִ�е���Ϊ
		"""
		pass

	def actionEnd( self ):
		"""
		��Ϊִ�н����󣬽��š���
		"""
		pass

	def canChangeState( self, oldState, attackArgument ):
		"""
		����Ƿ��ܽ����״̬

		@param oldState : ת��������״̬
		@type oldState : UINT8
		@param attackArgument : ��װ����
		@type attackArgument : see AttackArgumentFactory
		"""
		if BigWorld.player().isFollowing():	# ����״̬���������ս��
			return False
		return True

	def interruptAttack( self, reason ):
		"""
		��Ϲ�����Ϊ
		"""
		pass

	def onStateChanged( self, oldState, newState ):
		"""
		��ҵ�ս��״̬�ı�
		"""
		if oldState == csdefine.ENTITY_STATE_FIGHT and newState != csdefine.ENTITY_STATE_FIGHT:
			self.owner.cancelAttackState()

	def onItemDrop( self, dropEntity ):
		"""
		����Ʒ����
		"""
		pass

	def onReceiveSpell( self, casterID ):
		"""
		�ܵ��˺�

		@param casterID : �����˺���entity id
		"""
		pass

	def onSpellInterrupted( self, skillID, reason ):
		"""
		����������ͷż���
		"""
		pass


class NoAttack( AttackBase ):
	"""
	�޹���״̬
	"""
	def __init__( self, owner ):
		"""
		"""
		AttackBase.__init__( self, owner )
		self.state = Const.ATTACK_STATE_NONE

	def canChangeState( self, oldState, attackArgument ):
		"""
		����Ƿ��ܽ����״̬

		@param oldState : ת��������״̬
		@type oldState : UINT8
		@param attackArgument : ��װ����
		@type attackArgument : see AttackArgumentFactory
		"""
		if self.owner.state == csdefine.ENTITY_STATE_DEAD: return False
		return True

	def enter( self, attackArgument ) :
		"""
		ȡ������״̬
		"""
		self.owner.hideSpellingItemCover()

	def interruptAttack( self, reason ):
		"""
		�����ҽ�Ҫ
		"""
		if self.owner.isChange2AutoSpell():
			self.owner.cancelAutoFight2AutoSpellTimer()

	def onReceiveSpell( self, casterID ):
		"""
		�ܵ��˺�

		@param casterID : �����˺���entity id
		"""
		enemyEntity = BigWorld.entities.get( casterID )
		if enemyEntity is None:
			return

		if self.owner.isMoving():
			return

		# fightControl��counter������entities\common\config\client\viewinfosetting.xml�У�����Ƿ��Զ�����������
		if rds.viewInfoMgr.getSetting( "fightControl", "counter" ):
			rds.targetMgr.bindTarget( enemyEntity )
			self.owner.changeAttackState( Const.ATTACK_STATE_NORMAL )

class OnceAttack( AttackBase ):
	"""
	ʹ�ü��ܹ���һ��
	"""
	def __init__( self, owner ):
		"""
		"""
		AttackBase.__init__( self, owner )
		self.state = Const.ATTACK_STATE_ONCE
		self.skillID = 0

	def enter( self, attackArgument ):
		"""
		"""
		self.skillID = attackArgument.param
		self.action()

	def leave( self ):
		"""
		"""
		pass

	def canChangeState( self, oldState, attackArgument ):
		"""
		����Ƿ��ܽ����״̬

		@param oldState : ת��������״̬
		@type oldState : UINT8
		@param attackArgument : ��װ����
		@type attackArgument : see AttackArgumentFactory
		"""
		# �Զ�ս��״̬�£����ܽ����״̬
		if oldState == Const.ATTACK_STATE_AUTO_FIGHT: return False
		# ��ҵ�ǰ�����������ܽ����״̬��
		if self.owner.intonating(): return False
		# ָ�����ܲ������ͷţ����ܽ����״̬��
		skillID = attackArgument.param
		if hasattr( self.owner, "isInHomingSpell" ) and self.owner.isInHomingSpell and skillID / 1000 not in Const.HOMING_SPELL_CAN_USE_SKILL_LIST:return False
		skillInstance = Skill.getSkill( skillID )
		if not skillInstance.isCooldown( self.owner ) :
			self.owner.statusMessage( csstatus.SKILL_NOT_READY )
			self.owner.showInvalidItemCover( skillID )
			return False
		return AttackBase.canChangeState( self, oldState, attackArgument )

	def action( self ):
		"""
		"""
		self.owner.autoRestore()
		self.spellSkill()
		
	def actionEnd( self ):
		"""
		"""
		self.owner.cancelAttackState()

	def spellSkill( self ):
		"""
		�ͷż��ܹ���

		ʹ��ָ�����ܹ���Ŀ�꣺
		�������̫Զ����ô�ӽ����Ϸ�����󹥻�Ŀ�ꣻ
		���������������ô����Ŀ�ꣻ
		�����˳���״̬��
		"""
		skillInstance = Skill.getSkill( self.skillID )
		target = skillInstance.getCastObject().convertCastObject( self.owner, self.owner.targetEntity )	# ��������п���ֻ�ܶ��Լ��ͷ�
		
		if target is None:
			self.owner.statusMessage( csstatus.SKILL_NO_TARGET )
			self.owner.cancelAttackState()
			return
		
		spellTarget = SkillTargetObjImpl.createTargetObjEntity( target )
		if skillInstance.getCastObjectType() == csdefine.SKILL_CAST_OBJECT_TYPE_NONE:
			skillInstance.spell( self.owner, spellTarget )
			self.actionEnd()
			return

		# �߻�Ҫ���һ��Ŀ���ж��ǺϷ�֮��������� �����Զ��Ŀ�꿿�� �����֮���ɹ��������Ϣ
		state = skillInstance.useableCheck( self.owner, spellTarget )
		if state != csstatus.SKILL_GO_ON:
			if state != csstatus.SKILL_TOO_FAR:
				self.owner.showInvalidItemCover( self.skillID )
				if state is not None:
					self.owner.statusMessage( state )
				self.owner.cancelAttackState()
			else:	# ����Ǿ���̫Զ���ӽ��󹥻�
				self.owner.showSpellingItemCover( self.skillID )
				spellRange = skillInstance.getRangeMax( self.owner )
				self.owner.pursueEntity( target, spellRange, self.pursueAttack )
		else:
			if self.owner.isMoving() and self.owner.isInSpellRange( target, skillInstance ):	# ԭ���İ汾��ֹͣ�ƶ�0.1����ٹ���
				self.owner.stopMove()
			skillInstance.spell( self.owner, spellTarget )
			self.actionEnd()

	def pursueAttack( self, owner, targetEntity, success ):
		"""
		׷��Ŀ��Ļص�
		"""
		if self.owner.attackState != self.state:
			return

		if targetEntity is None:
			owner.cancelAttackState()
			return

		if BigWorld.player().targetEntity != targetEntity :
			owner.cancelAttackState()
			return

		if not success:
			owner.cancelAttackState()
			return

		self.spellSkill()

	def onStateChanged( self, oldState, newState ):
		"""
		��ҵ�ս��״̬�ı�
		"""
		if newState != csdefine.ENTITY_STATE_FIGHT:
			self.owner.cancelAttackState()

	def interruptAttack( self, reason ):
		"""
		��������ϣ���״̬������������Ƴ���״̬
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		if self.owner.isPursueState( ) or ( self.owner.vehicle and self.owner.vehicle.isPursueState() ):
			return
		self.owner.cancelAttackState()

class AutoNormalAttack( AttackBase ):
	"""
	��������ͨ�����������磺����������Ŀ��
	"""
	def __init__( self, owner ):
		"""
		"""
		AttackBase.__init__( self, owner )
		self.state = Const.ATTACK_STATE_NORMAL
		self.timerID = 0

	def enter( self, attackArgument ):
		"""
		�����״̬��ĳ�ʼ��
		"""
		self.action()

	def action( self ):
		"""
		��״̬��Ϊ��ʼ
		"""
		self.owner.autoRestore()
		self.spellSkill()

	def leave( self ):
		"""
		�뿪��״̬ʱ��������
		"""
		BigWorld.cancelCallback( self.timerID )

	def spellSkill( self ):
		"""
		�ͷż��ܹ���
		"""
		skillID = self.owner.getNormalAttackSkillID() 
		target = self.owner.targetEntity
		skillInstance = Skill.getSkill( skillID )

		if target is None:
			self.owner.statusMessage( csstatus.SKILL_NO_TARGET )
			self.owner.cancelAttackState()
			return

		# �߻�Ҫ���һ��Ŀ���ж��ǺϷ�֮��������� �����Զ��Ŀ�꿿�� �����֮���ɹ��������Ϣ
		spellTarget = SkillTargetObjImpl.createTargetObjEntity( target )
		state = skillInstance.useableCheck( self.owner, spellTarget )
		# ���Լ��ܲŽ���pk��ʾ�ж�
		if skillInstance.isMalignant():
			pkMessage = self.owner.pkStateMessage()
			if pkMessage is not None:
				self.owner.statusMessage( pkMessage )
		if state != csstatus.SKILL_GO_ON:
			if state != csstatus.SKILL_TOO_FAR:
				self.owner.showInvalidItemCover( skillID )
				if state is not None :
					self.owner.statusMessage( state )		# out put error message to system information panel( in RoleChat.py )
				self.owner.cancelAttackState()
			else:	# ����Ǿ���̫Զ���ӽ��󹥻�
				spellRange = skillInstance.getRangeMax( self.owner )
				self.owner.pursueEntity( target, spellRange, self.pursueAttack )
		else:
			if self.owner.isMoving() and self.owner.isInSpellRange( target, skillInstance ):	# ԭ���İ汾��ֹͣ�ƶ�0.1����ٹ���
				self.owner.stopMove()
				DEBUG_MSG( "---------->>>stopMove" )
			skillInstance.spell( self.owner, spellTarget )
			self.actionEnd()

	def actionEnd( self ):
		"""
		�ɹ�ִ��һ����Ϊ��Ĵ���������ɹ�����ô��;�϶��˳������״̬��
		"""
		if self.owner.pkStateMessage() is not None:
			return
		self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )	# �ظ������Ϊ�Ļص�ʱ��Ӧ�ú͹����ٶ�һ��

	def interruptAttack( self, reason ):
		"""
		��������ϣ���״̬������������Ƴ���״̬
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		if self.owner.isPursueState( ) or ( self.owner.vehicle and self.owner.vehicle.isPursueState() ):
			return
		self.owner.cancelAttackState()

	def pursueAttack( self, owner, targetEntity, success ):
		"""
		׷��Ŀ��Ļص�
		"""
		if self.owner.attackState != self.state:
			return
		if targetEntity is None:
			owner.cancelAttackState()	# ��������ڱ�����ʱ��ҿ����Ѿ���Ĭ�Ϲ���״̬
			return
		if BigWorld.player().targetEntity != targetEntity :
			owner.cancelAttackState()
			return
		if not success:
			owner.cancelAttackState()
			return
		self.spellSkill()

	def canChangeState( self, oldState, attackArgument ):
		"""
		����Ƿ��ܽ����״̬

		@param oldState : ת��������״̬
		@type oldState : UINT8
		@param attackArgument : ��װ����
		@type attackArgument : see AttackArgumentFactory
		"""
		# �Զ�ս��״̬�£����ܽ����״̬
		if oldState == Const.ATTACK_STATE_AUTO_FIGHT: return
		# ��ҵ�ǰ�����������ܽ����״̬��
		if self.owner.intonating(): return False
		# ָ�����ܲ������ͷţ����ܽ����״̬��
		skillID = 0
		if attackArgument:
			skillID = attackArgument.param
		if hasattr( self.owner, "isInHomingSpell" ) and self.owner.isInHomingSpell and skillID / 1000 not in Const.HOMING_SPELL_CAN_USE_SKILL_LIST:return False
		return AttackBase.canChangeState( self, oldState, attackArgument )

	def onStateChanged( self, oldState, newState ):
		"""
		��ҵ�ս��״̬�ı�
		"""
		if newState != csdefine.ENTITY_STATE_FIGHT:
			self.owner.cancelAttackState()

	def onSpellInterrupted( self, skillID, reason ):
		"""
		����������ͷż���
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		self.owner.cancelAttackState()


class AutoConfirmSpellAttack( AttackBase ):
	"""
	�Զ�ʹ��ָ���ļ��ܹ�����ָ���ļ���ֻʹ��һ�Σ�ʹ�ú����ʹ����ͨ������
	"""
	def __init__( self, owner ):
		"""
		"""
		AttackBase.__init__( self, owner )
		self.state = Const.ATTACK_STATE_AUTO_CONFIRM_SPELL
		self.timerID = 0
		self.skillID = 0
		self.skillHasUsed = False					# ָ�������Ƿ�ʹ�ù�

	def enter( self, attackArgument ):
		"""
		�����״̬��ĳ�ʼ��
		"""
		self.skillID = attackArgument.param		# ʹ��ָ���ļ���
		self.action()

	def leave( self ):
		"""
		�뿪��״̬ʱ��������
		"""
		self.skillID = 0
		self.skillHasUsed = False
		BigWorld.cancelCallback( self.timerID )

	def interruptAttack( self, reason ):
		"""
		��������ϣ���״̬������������Ƴ���״̬
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		if self.owner.isPursueState( ) or ( self.owner.vehicle and self.owner.vehicle.isPursueState() ):
			return
		self.owner.cancelAttackState()

	def action( self ):
		"""
		��״̬��Ϊ��ʼ
		"""
		self.owner.autoRestore()
		if not self.canAction():
			self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )	# �ظ������Ϊ�Ļص�ʱ��Ӧ�ú͹����ٶ�һ��
			return
		self.spellSkill()

	def canAction( self ):
		"""
		�Ƿ��ܿ�ʼ��Ϊ
		"""
		if self.owner.intonating():
			return False
		if hasattr( self.owner, "isInHomingSpell" ) and self.owner.isInHomingSpell:return False
		return True

	def getSkillID( self ):
		"""
		���ʹ�ü���
		"""
		if self.skillHasUsed:
			return self.owner.getNormalAttackSkillID()
		return self.skillID

	def spellSkill( self ):
		"""
		�ͷż��ܹ���

		ʹ��ָ�����ܹ���Ŀ��һ�κ�ʹ����ͨ�����ܹ���Ŀ�꣬
		13:44 2009-5-31�޸ģ����������ȴ�У��򱾴ι������ɹ���
		���ħ�����㣬��ôʹ����ͨ����Ŀ�ꣻ
		���Ŀ�겻����ͨ�����ܹ�����Χ����callback��⣻
		���������������ô����Ŀ�ꣻ
		�����˳���״̬��
		"""
		target = self.owner.targetEntity
		skillInstance = Skill.getSkill( self.getSkillID() )
		target = skillInstance.getCastObject().convertCastObject( self.owner, target )

		if target is None:
			self.owner.statusMessage( csstatus.SKILL_NO_TARGET )
			self.owner.cancelAttackState()
			return
		# �߻�Ҫ���һ��Ŀ���ж��ǺϷ�֮��������� �����Զ��Ŀ�꿿�� �����֮���ɹ��������Ϣ
		spellTarget = SkillTargetObjImpl.createTargetObjEntity( target )
		state = skillInstance.useableCheck( self.owner, spellTarget )
		# ���Լ��ܲŽ���pk��ʾ�ж�
		if skillInstance.isMalignant():
			pkMessage = self.owner.pkStateMessage()
			if pkMessage is not None:
				self.owner.statusMessage( pkMessage )
		if state != csstatus.SKILL_GO_ON:
			if state == csstatus.SKILL_OUTOF_MANA:	# ʹ����ͨ�������ܹ���
				self.owner.showInvalidItemCover( self.skillID )
				skillInstance = Skill.getSkill( self.owner.getNormalAttackSkillID() )
				state2 = skillInstance.useableCheck( self.owner, spellTarget )
				if state2 == csstatus.SKILL_GO_ON:
					skillInstance.spell( self.owner, spellTarget )
					self.actionEnd()
				elif state2 == csstatus.SKILL_TOO_FAR:
					spellRange = skillInstance.getRangeMax( self.owner )
					self.owner.pursueEntity( target, spellRange, self.pursueAttack )
				else:
					if state is not None :
						self.owner.statusMessage( state )
					self.owner.cancelAttackState()
			elif state != csstatus.SKILL_TOO_FAR:
				if not self.skillHasUsed:	#Ϊ�˽����ͨ�������ܺ͵�ǰ���ܵĹ���CD����add by wuxo 2011-12-12
					self.owner.showInvalidItemCover( self.skillID )
					if state is not None:
						self.owner.statusMessage( state )
					self.owner.cancelAttackState()
				else:
					self.actionEnd()
			else:	# ����Ǿ���̫Զ���ӽ��󹥻�
				if not self.skillHasUsed:
					self.owner.showSpellingItemCover( self.skillID )
					spellRange = skillInstance.getRangeMax( self.owner )
					self.owner.pursueEntity( target, spellRange, self.pursueAttack )
				else:
					self.actionEnd()
		else:
			if self.owner.isMoving() and self.owner.isInSpellRange( target, skillInstance ):	# ԭ���İ汾��ֹͣ�ƶ�0.1����ٹ���
				self.owner.stopMove()
			skillInstance.spell( self.owner, spellTarget )
			if not self.skillHasUsed:
				self.skillHasUsed = True					# ָ�������Ѿ�ʹ�ù���
				if not skillInstance.isMalignant() and ( self.owner.state != csdefine.ENTITY_STATE_FIGHT ):
					self.owner.cancelAttackState()
					return
			self.actionEnd()

	def actionEnd( self ):
		"""
		�ɹ�ִ��һ����Ϊ��Ĵ���������ɹ�����ô��;�϶��˳������״̬��
		"""
		if self.owner.pkStateMessage() is not None:
			return
		self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )	# �ظ������Ϊ�Ļص�ʱ��Ӧ�ú͹����ٶ�һ��

	def pursueAttack( self, owner, targetEntity, success ):
		"""
		׷��Ŀ��Ļص�
		"""
		if self.owner.attackState != self.state:
			return

		if targetEntity is None:
			owner.cancelAttackState()
			return

		if BigWorld.player().targetEntity != targetEntity :
			owner.cancelAttackState()
			return

		if not success:
			owner.cancelAttackState()
			return
		self.spellSkill()

	def canChangeState( self, oldState, attackArgument ):
		"""
		����Ƿ��ܽ����״̬

		@param oldState : ת��������״̬
		@type oldState : UINT8
		@param attackArgument : ��װ����
		@type attackArgument : see AttackArgumentFactory
		"""
		# �Զ�ս��״̬�£����ܽ����״̬
		if oldState == Const.ATTACK_STATE_AUTO_FIGHT: return False
		# ��ҵ�ǰ�����������ܽ����״̬��
		if self.owner.intonating(): return False
		# ָ�����ܲ������ͷţ����ܽ����״̬��
		skillID = attackArgument.param
		skillInstance = Skill.getSkill( skillID )
		if not skillInstance.isCooldown( self.owner ) :
			self.owner.statusMessage( csstatus.SKILL_NOT_READY )
			self.owner.showInvalidItemCover( skillID )
			return False
		return AttackBase.canChangeState( self, oldState, attackArgument )

	def onStateChanged( self, oldState, newState ):
		"""
		��ҵ�ս��״̬�ı�
		"""
		if newState != csdefine.ENTITY_STATE_FIGHT:
			self.owner.cancelAttackState()

	def onSpellInterrupted( self, skillID, reason ):
		"""
		����������ͷż���
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		self.owner.cancelAttackState()

class AutoConfirmSpellAttackCursor( AttackBase ):
	"""
	�Զ�ʹ��ָ���ļ��ܹ�����ָ���ļ���ֻʹ��һ�Σ�ʹ�ú����ʹ����ͨ������
	"""
	def __init__( self, owner ):
		"""
		"""
		AttackBase.__init__( self, owner )
		self.state = Const.ATTACK_STATE_AUTO_SPELL_CURSOR
		self.timerID = 0
		self.skillID = 0
		self.attPos = Math.Vector3( (0, 0, 0) )
		self.skillHasUsed = False					# ָ�������Ƿ�ʹ�ù�
		
	def enter( self, attackArgument ):
		"""
		�����״̬��ĳ�ʼ��
		"""
		self.owner.stopMove()					# ֹͣ�ƶ����п������Զ�Ѱ·��
		self.skillID = attackArgument.param		# ʹ��ָ���ļ���
		cursorDropPoint = gbref.cursorToDropPoint()
		if cursorDropPoint:
			self.attPos = Math.Vector3( cursorDropPoint )
		self.action()

	def leave( self ):
		"""
		�뿪��״̬ʱ��������
		"""
		self.skillID = 0
		self.skillHasUsed = False
		self.attPos = Math.Vector3( (0, 0, 0) )
		BigWorld.cancelCallback( self.timerID )

	def action( self ):
		"""
		��״̬��Ϊ��ʼ
		"""
		self.owner.autoRestore()
		if not self.canAction():
			self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )	# �ظ������Ϊ�Ļص�ʱ��Ӧ�ú͹����ٶ�һ��
			return
		self.spellSkill()

	def actionEnd( self ):
		"""
		��Ϊִ�н����󣬽��š���
		"""
		if self.owner.pkStateMessage() is not None:
			return
		self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )	# �ظ������Ϊ�Ļص�ʱ��Ӧ�ú͹����ٶ�һ��
	
	def canAction( self ):
		"""
		�Ƿ��ܿ�ʼ��Ϊ
		"""
		if self.owner.intonating():
			return False
		if hasattr( self.owner, "isInHomingSpell" ) and self.owner.isInHomingSpell:return False
		return True
		
	def getSkillID( self ):
		"""
		���ʹ�ü���
		"""
		if self.skillHasUsed:
			return self.owner.getNormalAttackSkillID()
		return self.skillID

	def canChangeState( self, oldState, attackArgument ):
		"""
		����Ƿ��ܽ����״̬

		@param oldState : ת��������״̬
		@type oldState : UINT8
		@param attackArgument : ��װ����
		@type attackArgument : see AttackArgumentFactory
		"""
		# �Զ�ս��״̬�£����ܽ����״̬
		if oldState == Const.ATTACK_STATE_AUTO_FIGHT: return False
		# ��ҵ�ǰ�����������ܽ����״̬��
		if self.owner.intonating(): return False
		# ָ�����ܲ������ͷţ����ܽ����״̬��
		skillID = attackArgument.param
		skillInstance = Skill.getSkill( skillID )
		if not skillInstance.isCooldown( self.owner ) :
			self.owner.statusMessage( csstatus.SKILL_NOT_READY )
			self.owner.showInvalidItemCover( skillID )
			return False
		return AttackBase.canChangeState( self, oldState, attackArgument )
	
	def onStateChanged( self, oldState, newState ):
		"""
		��ҵ�ս��״̬�ı�
		"""
		if newState != csdefine.ENTITY_STATE_FIGHT:
			self.owner.cancelAttackState()

	def onSpellInterrupted( self, skillID, reason ):
		"""
		����������ͷż���
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		self.owner.cancelAttackState()
		
	def spellSkill( self ):
		"""
		�ͷż��ܹ���

		ʹ��ָ�����ܹ���Ŀ��һ�κ�ʹ����ͨ�����ܹ���Ŀ�꣬
		13:44 2009-5-31�޸ģ����������ȴ�У��򱾴ι������ɹ���
		���ħ�����㣬��ôʹ����ͨ����Ŀ�ꣻ
		���Ŀ�겻����ͨ�����ܹ�����Χ����callback��⣻
		���������������ô����Ŀ�ꣻ
		�����˳���״̬��
		"""
		if self.getSkillID() == 0 or self.getSkillID() == None:
			return
			
		skillInstance = Skill.getSkill( self.getSkillID() )
		cursorPos = self.attPos

		spellTarget = SkillTargetObjImpl.createTargetObjPosition( cursorPos )
		state = skillInstance.useableCheck( self.owner, spellTarget )
		# ���Լ��ܲŽ���pk��ʾ�ж�
		if skillInstance.isMalignant():
			pkMessage = self.owner.pkStateMessage()
			if pkMessage is not None:
				self.owner.statusMessage( pkMessage )
		if state != csstatus.SKILL_GO_ON:
			if state == csstatus.SKILL_TOO_FAR:
				if not self.skillHasUsed:
					import math
					self.owner.showSpellingItemCover( self.skillID )
					spellRange = skillInstance.getRangeMax( self.owner )
					self.owner.pursuePosition( cursorPos, spellRange, self.onPursuePositionAttack )
				else:
					self.actionEnd()
			elif state == csstatus.SKILL_CANT_DIRECTION_ERR:
				matrix = Math.Matrix()
				matrix.setTranslate( cursorPos )
				self.owner.turnaround( matrix, self.onTurnaroundAttack )
			elif state == csstatus.SKILL_CANT_ARRIVAL:
				self.owner.statusMessage( csstatus.SKILL_CANT_ARRIVAL )
		else:
			if self.owner.isMoving() and self.owner.isInSpellDis( cursorPos, skillInstance ):	# ԭ���İ汾��ֹͣ�ƶ�0.1����ٹ���
				self.owner.stopMove()
			
			skillInstance.spell( self.owner, spellTarget )
			if not self.skillHasUsed:
				self.skillHasUsed = True					# ָ�������Ѿ�ʹ�ù���
				if not skillInstance.isMalignant() and ( self.owner.state != csdefine.ENTITY_STATE_FIGHT ):
					self.owner.cancelAttackState()
					return
			self.actionEnd()
	
	def onTurnaroundAttack( self, success):
		if not success and self.owner:
			self.owner.cancelAttackState()
			return
		
		self.spellSkill()
		
	def onPursuePositionAttack( self, owner, targetPos, success ):
		if not success and self.owner:
			self.owner.cancelAttackState()
			return
		
		self.spellSkill()

class AutoHomingSpellAttack( AttackBase ):
	"""
	�Զ�ʹ���������ܹ���
	"""
	def __init__( self, owner ):
		"""
		"""
		AttackBase.__init__( self, owner )
		self.state = Const.ATTACK_STATE_HOMING_SPELL
		self.timerID = 0

	def enter( self, attackArgument ):
		"""
		�����״̬��ĳ�ʼ��
		@param arg : �ⲿ������
		"""
		self.owner.autoRestore()
		self.tryUseSkill()

	def leave( self ):
		"""
		�뿪��״̬ʱ��������
		"""
		BigWorld.cancelCallback( self.timerID )
		self.timerID = 0

	def canAction( self ):
		"""
		"""
		if self.owner.intonating(): return False
		if self.owner.isInHomingSpell: return False
		skillID = self.owner.getLastUseAutoSkillID()
		skillInstance = Skill.getSkill( skillID )
		if hasattr( self.owner, "isInHomingSpell" ) and self.owner.isInHomingSpell:return False
		if not skillInstance.isCooldown( self.owner ):return False
		return True

	def action( self ):
		if self.canAction():
			self.tryUseSkill()
		else:
			self.actionEnd()

	def tryUseSkill( self ):

		skillID = self.owner.getLastUseAutoSkillID()
		skillInstance = Skill.getSkill( skillID )
		target = self.owner.targetEntity
		target = skillInstance.getCastObject().convertCastObject( self.owner, target )
		if target is None:
			self.owner.cancelAttackState()
			return

		# �߻�Ҫ���һ��Ŀ���ж��ǺϷ�֮��������� �����Զ��Ŀ�꿿�� �����֮���ɹ��������Ϣ
		spellTarget = SkillTargetObjImpl.createTargetObjEntity( target )
		state = skillInstance.useableCheck( self.owner, spellTarget )
		# ���Լ��ܲŽ���pk��ʾ�ж�
		if skillInstance.isMalignant():
			pkMessage = self.owner.pkStateMessage()
			if pkMessage is not None:
				self.owner.statusMessage( pkMessage )
		if state == csstatus.SKILL_GO_ON:
			if self.owner.isMoving() and self.owner.isInSpellRange( target, skillInstance ):
				self.owner.stopMove()
			skillInstance.spell( self.owner, spellTarget )
			self.actionEnd()
		elif state == csstatus.SKILL_TOO_FAR:
			self.owner.showSpellingItemCover( skillID )
			spellRange = skillInstance.getRangeMax( self.owner )
			self.owner.pursueEntity( target, spellRange, self.pursueAttack )
		elif state == csstatus.SKILL_OUTOF_MANA:
			self.owner.showInvalidItemCover( skillID )
			self.owner.cancelAttackState()
		else:
			self.owner.showInvalidItemCover( skillID )
			if state is not None:
				self.owner.statusMessage( state )
			self.actionEnd()

	def actionEnd( self ):
		"""
		"""
		if self.owner.pkStateMessage() is not None:
			return
		self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )

	def pursueAttack( self, owner, targetEntity, success ):
		"""
		׷��Ŀ��Ļص�
		"""
		if self.owner.attackState != self.state:
			return

		if targetEntity is None:
			owner.cancelAttackState()
			return

		if BigWorld.player().targetEntity != targetEntity :
			owner.cancelAttackState()
			return

		if not success:
			owner.cancelAttackState()
			return

		self.tryUseSkill()

	def canChangeState( self, oldState, attackArgument ):
		"""
		����Ƿ��ܽ����״̬

		@param oldState : ת��������״̬
		@type oldState : UINT8
		@param attackArgument : ��װ����
		@type attackArgument : see AttackArgumentFactory
		"""
		# �Զ�ս��״̬�£����ܽ����״̬
		if oldState == Const.ATTACK_STATE_AUTO_FIGHT: return
		if oldState == self.state:return False
		return AttackBase.canChangeState( self, oldState, attackArgument )

	def interruptAttack( self, reason ):
		"""
		��������ϣ���״̬������������Ƴ���״̬
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		if self.owner.isPursueState() or ( self.owner.vehicle and self.owner.vehicle.isPursueState() ):
			return
		self.owner.cancelAttackState()

	def onSpellInterrupted( self, skillID, reason ):
		"""
		����������ͷż���
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		self.owner.cancelAttackState()

	def onStateChanged( self, oldState, newState ):
		"""
		��ҵ�ս��״̬�ı�
		"""
		if newState != csdefine.ENTITY_STATE_FIGHT:
			self.owner.cancelAttackState()

class SpellAutoHomingAttack( AttackBase ):
	"""
	ʹ�÷���ͨ�������ܹ���һ�κ������������ܹ���
	"""
	def __init__( self, owner ):
		"""
		"""
		AttackBase.__init__( self, owner )
		self.state = Const.ATTACK_STATE_SPELL_AND_HOMING
		self.skillID = 0
		self.timerID = 0
		self.isSkillUse = False

	def enter( self, attackArgument ):
		"""
		�����״̬��ĳ�ʼ��
		@param arg : �ⲿ������
		"""
		self.owner.autoRestore()
		self.skillID = attackArgument.param
		self.tryUseSkill()

	def leave( self ):
		"""
		�뿪��״̬ʱ��������
		"""
		BigWorld.cancelCallback( self.timerID )
		self.timerID = 0
		self.isSkillUse = False
		self.skillID = 0

	def getSkillID( self ):
		"""
		"""
		if self.isSkillUse: return self.owner.getLastUseAutoSkillID()
		return self.skillID

	def canAction( self ):
		"""
		�Ƿ��ܿ�ʼ��Ϊ
		"""
		if self.owner.intonating(): return False
		if self.owner.isInHomingSpell: return False
		return True

	def action( self ):
		"""
		"""
		if not self.canAction():
			self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )	# �ظ������Ϊ�Ļص�ʱ��Ӧ�ú͹����ٶ�һ��
			return
		self.tryUseSkill()

	def tryUseSkill( self ):
		"""
		����ʹ�ü���
		"""
		skillID = self.getSkillID()
		skillInstance = Skill.getSkill( skillID )
		target = self.owner.targetEntity
		target = skillInstance.getCastObject().convertCastObject( self.owner, target )
		if target is None:
			self.owner.statusMessage( csstatus.SKILL_NO_TARGET )
			self.owner.cancelAttackState()
			return
		# �߻�Ҫ���һ��Ŀ���ж��ǺϷ�֮��������� �����Զ��Ŀ�꿿�� �����֮���ɹ��������Ϣ
		spellTarget = SkillTargetObjImpl.createTargetObjEntity( target )
		state = skillInstance.useableCheck( self.owner, spellTarget )
		# ���Լ��ܲŽ���pk��ʾ�ж�
		if skillInstance.isMalignant():
			pkMessage = self.owner.pkStateMessage()
			if pkMessage is not None:
				self.owner.statusMessage( pkMessage )

		if state == csstatus.SKILL_GO_ON:
			if self.owner.isMoving() and self.owner.isInSpellRange( target, skillInstance ):
				self.owner.stopMove()
			skillInstance.spell( self.owner, spellTarget )
			if not self.isSkillUse:
				self.isSkillUse = True
				if not skillInstance.isMalignant() and ( self.owner.state != csdefine.ENTITY_STATE_FIGHT ):
					self.owner.cancelAttackState()
					return
			self.actionEnd()
		elif state == csstatus.SKILL_TOO_FAR:
			self.owner.showSpellingItemCover( skillID )
			spellRange = skillInstance.getRangeMax( self.owner )
			self.owner.pursueEntity( target, spellRange, self.pursueAttack )
		else:
			self.owner.showInvalidItemCover( skillID )
			self.actionEnd()

	def actionEnd( self ):
		"""
		�ɹ�ִ��һ����Ϊ��Ĵ���������ɹ�����ô��;�϶��˳������״̬��
		"""
		if self.owner.pkStateMessage() is not None:
			return
		self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )

	def pursueAttack( self, owner, targetEntity, success ):
		"""
		׷��Ŀ��Ļص�
		"""
		if self.owner.attackState != self.state:
			return

		if targetEntity is None:
			owner.cancelAttackState()
			return

		if BigWorld.player().targetEntity != targetEntity :
			owner.cancelAttackState()
			return

		if not success:
			owner.cancelAttackState()
			return

		self.tryUseSkill()

	def canChangeState( self, oldState, attackArgument ):
		"""
		����Ƿ��ܽ����״̬

		@param oldState : ת��������״̬
		@type oldState : UINT8
		@param attackArgument : ��װ����
		@type attackArgument : see AttackArgumentFactory
		"""
		# �Զ�ս��״̬�£����ܽ����״̬
		if oldState == Const.ATTACK_STATE_AUTO_FIGHT: return
		# ��ҵ�ǰ�����������ܽ����״̬��
		if self.owner.intonating(): return False
		# ָ�����ܲ������ͷţ����ܽ����״̬��
		skillID = attackArgument.param
		skillInstance = Skill.getSkill( skillID )
		if not skillInstance.isCooldown( self.owner ) :
			self.owner.statusMessage( csstatus.SKILL_NOT_READY )
			self.owner.showInvalidItemCover( skillID )
			return False
		return AttackBase.canChangeState( self, oldState, attackArgument )

	def interruptAttack( self, reason ):
		"""
		��������ϣ���״̬������������Ƴ���״̬
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		if self.owner.isPursueState() or ( self.owner.vehicle and self.owner.vehicle.isPursueState() ):
			return
		self.owner.cancelAttackState()

	def onSpellInterrupted( self, skillID, reason ):
		"""
		����������ͷż���
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		self.owner.cancelAttackState()

	def onStateChanged( self, oldState, newState ):
		"""
		��ҵ�ս��״̬�ı�
		"""
		if newState != csdefine.ENTITY_STATE_FIGHT:
			self.owner.cancelAttackState()

class AutoSpellAttack( AttackBase ):
	"""
	�Զ�ʹ�ü��ܹ��������磺�Ҽ�����Ŀ��
	"""
	def __init__( self, owner ):
		"""
		"""
		AttackBase.__init__( self, owner )
		self.state = Const.ATTACK_STATE_AUTO_SPELL
		self.timerID = 0

	def enter( self, attackArgument ):
		"""
		�����״̬��ĳ�ʼ��
		"""
		self.owner.autoRestore()
		self.action()

	def leave( self ):
		"""
		�뿪��״̬ʱ��������
		"""
		BigWorld.cancelCallback( self.timerID )

	def interruptAttack( self, reason ):
		"""
		��������ϣ���״̬������������Ƴ���״̬
		"""
		if self.owner.isPursueState( ) or ( self.owner.vehicle and self.owner.vehicle.isPursueState() ):
			return
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		self.owner.cancelAttackState()

	def action( self ):
		"""
		��״̬��Ϊ��ʼ
		"""
		if not self.canAction():
			self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )	# �ظ������Ϊ�Ļص�ʱ��Ӧ�ú͹����ٶ�һ��
			return
		self.spellSkill()

	def canAction( self ):
		"""
		�Ƿ��ܿ�ʼ��Ϊ
		"""
		if self.owner.intonating() or self.owner.isInHomingSpell:
			return False
		return True

	def spellSkill( self ):
		"""
		�ͷż��ܹ���

		ʹ��ָ�����ܹ���Ŀ�꣺
		���ħ��������߼���û׼���ã���ôʹ����ͨ����Ŀ�ꣻ
		�������̫Զ����ô�ӽ����Ϸ�����󹥻�Ŀ�ꣻ
		���������������ô����Ŀ�ꣻ
		�����˳���״̬��
		"""
		skillInstance = Skill.getSkill( self.owner.getNormalAttackSkillID() )
		self.spellableCheck( skillInstance, self.owner.getNormalAttackSkillID() )

	def spellableCheck( self, skillInstance, skillID ):
		"""
		�����Զ�ս��ʹ�ù���ĸ��� ʹ���Ҽ�ս���ļ���ѡ��ṹҲ����� modified by����
		"""
		target = self.owner.targetEntity
		if target is None:
			self.owner.cancelAttackState()
			return True
		# �߻�Ҫ���һ��Ŀ���ж��ǺϷ�֮��������� �����Զ��Ŀ�꿿�� �����֮���ɹ��������Ϣ
		spellTarget = SkillTargetObjImpl.createTargetObjEntity( target )
		state = skillInstance.useableCheck( self.owner, spellTarget )
		if state != csstatus.SKILL_GO_ON:
			if state in [ csstatus.SKILL_NOT_READY, csstatus.SKILL_OUTOF_MANA ]:	# ʹ����ͨ�������ܹ���
				self.owner.showInvalidItemCover( skillID )
				skillInstance = Skill.getSkill( self.owner.getNormalAttackSkillID() )
				state2 = skillInstance.useableCheck( self.owner, spellTarget )
				if state2 == csstatus.SKILL_GO_ON:
					skillInstance.spell( self.owner, spellTarget )
					self.actionEnd()
					return True
				elif state2 == csstatus.SKILL_TOO_FAR:
					spellRange = skillInstance.getRangeMax( self.owner )
					self.owner.pursueEntity( target, spellRange, self.pursueAttack )
					return True
				else:
					if state is not None:
						self.owner.statusMessage( state )
					self.owner.cancelAttackState()
					return False
			elif state != csstatus.SKILL_TOO_FAR:
				self.owner.showInvalidItemCover( skillID )
				if state is not None:
					self.owner.statusMessage( state )
				self.owner.cancelAttackState()
				return False
			else:	# ����Ǿ���̫Զ���ӽ��󹥻�
				self.owner.showSpellingItemCover( skillID )
				spellRange = skillInstance.getRangeMax( self.owner )
				self.owner.pursueEntity( target, spellRange, self.pursueAttack )
				return True
		else:
			if self.owner.isMoving() and self.owner.isInSpellRange( target, skillInstance ):	# ԭ���İ汾��ֹͣ�ƶ�0.1����ٹ���
				self.owner.stopMove()
			skillInstance.spell( self.owner, spellTarget )
			self.actionEnd()
			return True

	def actionEnd( self ):
		"""
		�ɹ�ִ��һ����Ϊ��Ĵ���������ɹ�����ô��;�϶��˳������״̬��
		"""
		if self.owner.pkStateMessage() is not None:
			return
		self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )	# �ظ������Ϊ�Ļص�ʱ��Ӧ�ú͹����ٶ�һ��

	def pursueAttack( self, owner, targetEntity, success ):
		"""
		׷��Ŀ��Ļص�
		"""
		if self.owner.attackState != self.state:
			return

		if targetEntity is None:
			owner.cancelAttackState()
			return

		if BigWorld.player().targetEntity != targetEntity :
			owner.cancelAttackState()
			return

		if not success:
			owner.cancelAttackState()
			return

		self.spellSkill()

	def canChangeState( self, oldState, attackArgument ):
		"""
		����Ƿ��ܽ����״̬

		@param oldState : ת��������״̬
		@type oldState : UINT8
		@param attackArgument : ��װ����
		@type attackArgument : see AttackArgumentFactory
		"""
		if oldState == self.state: return False
		# �Զ�ս��״̬�£����ܽ����״̬
		if oldState == Const.ATTACK_STATE_AUTO_FIGHT: return False
		return AttackBase.canChangeState( self, oldState, attackArgument )

	def onStateChanged( self, oldState, newState ):
		"""
		��ҵ�ս��״̬�ı�
		"""
		if newState != csdefine.ENTITY_STATE_FIGHT:
			self.owner.cancelAttackState()

	def onSpellInterrupted( self, skillID, reason ):
		"""
		����������ͷż���
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		self.owner.cancelAttackState()

class SpellAndAutoHomingAttack( AttackBase ):
	"""
	ָ�����������������������ܽ���ʹ��״̬
	"""
	def __init__( self, owner ):
		"""
		"""
		AttackBase.__init__( self, owner )
		self.state = Const.ATTACK_STATE_AUTO_SPELL_HOMING
		self.timerID = 0

	def enter( self, attackArgument ):
		"""
		�����״̬��ĳ�ʼ��
		"""
		self.owner.autoRestore()
		self.action()

	def leave( self ):
		"""
		�뿪��״̬ʱ��������
		"""
		BigWorld.cancelCallback( self.timerID )

	def interruptAttack( self, reason ):
		"""
		��������ϣ���״̬������������Ƴ���״̬
		"""
		if self.owner.isPursueState( ) or ( self.owner.vehicle and self.owner.vehicle.isPursueState() ):
			return
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		self.owner.cancelAttackState()

	def action( self ):
		"""
		��״̬��Ϊ��ʼ
		"""
		if not self.canAction():
			self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.action )	# �ظ������Ϊ�Ļص�ʱ��Ӧ�ú͹����ٶ�һ��
			return
		self.tryUseSkill()

	def canAction( self ):
		"""
		�Ƿ��ܿ�ʼ��Ϊ
		"""
		if self.owner.intonating():
			return False
		if hasattr( self.owner, "isInHomingSpell" ) and self.owner.isInHomingSpell:return False
		return True

	def tryUseSkill( self ):
		"""
		����ʹ�ü���
		�ݲ߻����¹����Զ�ս�����ϵ�3������Ҫ����CD�������
		"""
		# Ŀ�겻������ֱ���˳���״̬
		target = self.owner.targetEntity
		if target is None:
			self.owner.statusMessage( csstatus.SKILL_NO_TARGET )
			self.owner.cancelAttackState()
			return True
		spellTarget = SkillTargetObjImpl.createTargetObjEntity( target )

		skillIDList = self.owner.getAutoSkillIDList()
		# ���û�аڷż��ܣ���ʹ��Ĭ��������������
		if len( skillIDList ) == 0:
			lastUseAutoSkillID = self.owner.getLastUseAutoSkillID()
		else:
			# ����ʹ�óɹ���������һ��tick���
			for skillID in skillIDList:
				if self.useSkill( skillID, target ):
					return

			# �Զ�ս�����ڷŵļ��ܶ�����ʹ�ã����Զ�ʹ��������������
			lastUseAutoSkillID = self.owner.getLastUseAutoSkillID()
			self.useSkill( lastUseAutoSkillID, target )

	def useSkill( self, skillID, target ):
		"""
		ʹ��һ�����ܣ�׷����Ϊ��ʹ�óɹ���
		"""
		skillInstance = Skill.getSkill( skillID )
		spellTarget = SkillTargetObjImpl.createTargetObjEntity( target )
		state = skillInstance.useableCheck( self.owner, spellTarget )
		# ����̫Զ���ӽ��󹥻�
		if state == csstatus.SKILL_TOO_FAR:
			self.owner.showSpellingItemCover( skillID )
			spellRange = skillInstance.getRangeMax( self.owner )
			self.owner.pursueEntity( target, spellRange, self.pursueAttack )
		elif state == csstatus.SKILL_GO_ON:
			if self.owner.isMoving() and self.owner.isInSpellRange( target, skillInstance ):
				self.owner.stopMove()
			skillInstance.spell( self.owner, spellTarget )
			self.actionEnd()
		else:
			self.owner.showInvalidItemCover( skillID )
			return False
		return True

	def pursueAttack( self, owner, targetEntity, success ):
		"""
		׷��Ŀ��Ļص�
		"""
		if self.owner.attackState != self.state:
			return

		if targetEntity is None:
			owner.cancelAttackState()
			return

		if BigWorld.player().targetEntity != targetEntity :
			owner.cancelAttackState()
			return

		if not success:
			owner.cancelAttackState()
			return

		self.tryUseSkill()

	def actionEnd( self ):
		"""
		�ɹ�ִ��һ����Ϊ��Ĵ���������ɹ�����ô��;�϶��˳������״̬��
		"""
		if self.owner.pkStateMessage() is not None:
			return
		self.timerID = BigWorld.callback( self.owner.hit_speed + Const.AUTO_ATTACK_DELAY_AMEND, self.tryUseSkill )	# �ظ������Ϊ�Ļص�ʱ��Ӧ�ú͹����ٶ�һ��

	def canChangeState( self, oldState, attackArgument ):
		"""
		����Ƿ��ܽ����״̬

		@param oldState : ת��������״̬
		@type oldState : UINT8
		@param attackArgument : ��װ����
		@type attackArgument : see AttackArgumentFactory
		"""
		if oldState == self.state: return False
		# �Զ�ս��״̬�£����ܽ����״̬
		if oldState == Const.ATTACK_STATE_AUTO_FIGHT: return
		# ��ҵ�ǰ�����������ܽ����״̬��
		if self.owner.intonating(): return False
		# ָ�����ܲ������ͷţ����ܽ����״̬��
		skillIDList = self.owner.getAutoSkillIDList()
		if len( skillIDList ) == 0: return False
		skillID = skillIDList[0]
		skillInstance = Skill.getSkill( skillID )
		if not skillInstance.isCooldown( self.owner ) :
			self.owner.statusMessage( csstatus.SKILL_NOT_READY )
			self.owner.showInvalidItemCover( skillID )
			return False
		return AttackBase.canChangeState( self, oldState, attackArgument )

	def onStateChanged( self, oldState, newState ):
		"""
		��ҵ�ս��״̬�ı�
		"""
		if newState != csdefine.ENTITY_STATE_FIGHT:
			self.owner.cancelAttackState()

	def onSpellInterrupted( self, skillID, reason ):
		"""
		����������ͷż���
		"""
		if reason not in [ csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1, csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 ]: return
		self.owner.cancelAttackState()

class AutoFightAttack( AttackBase ):
	"""
	�Զ�ս��״̬
	"""
	def __init__( self, owner ):
		"""
		"""
		AttackBase.__init__( self, owner )
		self.state = Const.ATTACK_STATE_AUTO_FIGHT
		self.timerID = 0
		self.startPosition = ( 0, 0, 0 )			# �Զ�ս����ʼλ��
		self.running = False						# �Զ�������Ϊ�Ƿ�����ִ��
		self.pickUpList = []						# ʰȡ�б�
		self.lastDropEntityID = 0				# ���ʰȡ��entityID����ΪdropEntity��������ʱ������Ѿ�ʰȡ���ˣ�������һ��ʰȡ�����������ҵ���entity������ʰȡ����
		self.startPickUpDelayTimerID = 0		# ��ʼ�Զ�ʰȡ��ʱ��timerID
		self.persistentTimerID = 0				# ��ʼһ���Զ�ս������ʱ���timer
		self.controlSkillID = -1				# �Զ�ս�������ֶ�ʹ�ü��ܣ������ڼ�¼�ü���id����-1��� by ����
		self.defaultSkillID = 0
		# �Զ�ս����������� by ����
		self.actPetInfo = None					# �Զ�ս�����Լ�¼��ս����ļ�Ҫ����
		self.AFconfig = {}
		self.onceMessageList = []					# ���۵��Զ�ս��һ������ʾ��Ϣ

	def cancel( self ):
		"""
		�뿪��״̬
		"""
		self.owner.cancelAttackState()
		self.owner.statusMessage( csstatus.AUTO_FIGHT_TIME_OUT )

	@languageDepart_AFEnter
	def enter( self, attackArgument ):
		"""
		"""
		self.defaultSkillID = Define.SKILL_ID_TRIGGER_SKILLS.get( self.owner.getClass() )
		self.AFconfig = self.owner.getAutoFightConfig()
		self.startPosition = self.owner.position
		self.setAutoPet( False )
		self.owner.cell.enterAutoFight()
		ECenter.fireEvent( "EVT_ON_START_AUTOFIGHT" )
		self.timerID = BigWorld.callback( Const.AUTO_FIGHT_DETECT, self.autoFightDetect )
		self.pickUpAction()
		self.pyBox = None					# ����ȷ�Ͽ�

	def autoFightDetect( self ):
		"""
		�Զ�ս����ʼ��ÿ��Const.AUTO_FIGHT_DETECTִ�е�һ�����
		"""
		BigWorld.cancelCallback( self.timerID )
		self.timerID = BigWorld.callback( Const.AUTO_FIGHT_DETECT, self.autoFightDetect )
		self.owner.autoRestore()
		if not self.canAction():
			return
		self.action()

	def onStateChanged( self, oldState, newState ):
		"""
		��ɫ״̬�ı�
		"""
		if newState == csdefine.ENTITY_STATE_DEAD:
			if self.AFconfig["autoReboin"]:
				if self.actAutoReboin():
					return
			self.owner.cancelAttackState()

	@languageDepart_AFLeave
	def leave( self ):
		"""
		�뿪��״̬
		"""
		ECenter.fireEvent( "EVT_ON_STOP_AUTOFIGHT" )
		ECenter.fireEvent( "EVT_ON_STOP_AUTO_SKILL", self.defaultSkillID )
		self.running = False
		self.startPosition = ( 0, 0, 0 )
		self.pickUpList = []
		self.onceMessageList = []
		self.owner.resetAutoFightList()
		self.owner.stopPickUp()
		self.lastDropEntityID = 0
		self.defaultSkillID = Define.SKILL_ID_TRIGGER_SKILLS.get( self.owner.getClass() )
		BigWorld.cancelCallback( self.timerID )
		BigWorld.cancelCallback( self.startPickUpDelayTimerID )
		BigWorld.cancelCallback( self.persistentTimerID )
		self.owner.cell.leaveAutoFight()
		self.setAutoPet( True )
		self.pyBox = None					# ����ȷ�Ͽ�

	def action( self ):
		"""
		��ʼ�Զ�����
		"""
		self.running = True						# �Զ���������������
		self.AFconfig = self.owner.getAutoFightConfig()
		# Ѱ��Ŀ��
		target = self.__getTarget()
		if self.AFconfig["isAutoConjure"]: self.actPetAutoConj()	# �����ٻ�
		if self.AFconfig["isAutoAddJoy"]: self.actPetAutoJoyCharge( self.AFconfig["joyLess"] )	# ���ֶȲ���
		if self.AFconfig["autoRepair"]: self.actAutoRepair( self.AFconfig["repairRate"] )	#�Զ�ʹ����Ʒ����װ��
		if target and not target.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and target.hasFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED ):
			self.autoRangeCheck()	# �ع鷶Χ						# �˴��Զ��������н���
			return
		if target and target != self.owner.targetEntity:
			rds.targetMgr.bindTarget( target )
		self.__attackTarget( target )
		self.autoRangeCheck()	# �ع鷶Χ

	def __attackTarget( self, target ):
		"""
		����Ŀ��
		@param target :	BigWorld entity
		"""
		if self.controlSkillID > 0:	# �����ʱ����ֶ��ͷż��ܣ������ȴ�������ֶ��ͷŵļ��� by ����
			skillInstance = Skill.getSkill( self.controlSkillID )
			# �ֶ��ͷż��ܼ�ⲻͨ������תΪʹ���Զ�ս�����ļ���
			targetObject = skillInstance.getCastObject().convertCastObject( self.owner, target )
			spellTarget = SkillTargetObjImpl.createTargetObjEntity( targetObject )
			state = skillInstance.useableCheck( self.owner, spellTarget )
			if state != csstatus.SKILL_GO_ON and state != csstatus.SKILL_TOO_FAR:
				self.owner.statusMessage( state )
				skillInstance = self.__getAutoUseSkillInstance( target )
		else:						# ����ʹ���Զ�ս�����ļ���
			skillInstance = self.__getAutoUseSkillInstance( target )
		self.__useSkill( target, skillInstance )
		self.controlSkillID = -1	# �ֶ����������Ƿ�ɹ�ʹ�ö����

	def __getAutoUseSkillInstance( self, target ):
		"""
		"""
		skillInstance = Skill.getSkill( self.defaultSkillID )
		idList = self.owner.getAutoSkillIDList()		# ����Զ�ս�����ļ�����
		for skillID in idList:
			skillInstance = self.__getAutoUseSpellAttack( target, skillID )      # ����б��п��ü���
			if skillInstance is not Skill.getSkill( self.defaultSkillID ):break
		return skillInstance

	def __useSkill( self, target, skillInstance ):
		"""
		ʹ��һ������ �������ܺ����漼��ͨ��
		"""
		target = skillInstance.getCastObject().convertCastObject( self.owner, target )
		spellTarget = SkillTargetObjImpl.createTargetObjEntity( target )
		state = skillInstance.useableCheck( self.owner, spellTarget )
		if state != csstatus.SKILL_GO_ON:
			if state == csstatus.SKILL_TOO_FAR:		# ����Ǿ���̫Զ���ӽ��󹥻�
				self.owner.showSpellingItemCover( skillInstance.getID() )
				self.owner.pursueEntity( target, skillInstance.getRangeMax( self.owner ), self.pursueAttack )
		else:
			if self.owner.isMoving() and self.owner.isInSpellRange( target, skillInstance ):
				self.owner.stopMove()
			skillInstance.spell( self.owner, spellTarget )
			#self.__setDefaultSkill( skillInstance )

	def __setDefaultSkill( self, skillInstance ):
		"""
		����Ĭ�ϵĹ������ܣ�������ͨ����
		"""
		homing = skillInstance.isHomingSkill()
		if skillInstance.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL or homing:
			#self.owner.isInHomingSpell = homing
			self.defaultSkillID = skillInstance.getID()
			ECenter.fireEvent( "EVT_ON_AUTO_NOR_SKILL_CHANGE", self.defaultSkillID )

	def canAction( self ):
		"""
		�ж���Ϊ�Ƿ��ܹ���ִ�С�

		�������ִ���У���ô��ִ�С�
		���������ˣ���ôִ�С�
		"""
		if self.running or self.owner.intonating():
			return False
		if hasattr( self.owner, "isInHomingSpell" ) and self.owner.isInHomingSpell:return False
		return True

	def actionEnd( self ):
		"""
		��Ϊ����
		"""
		self.running = False

	def pursueAttack( self, owner, targetEntity, success ):
		"""
		�ӽ��󹥻�
		"""
		if self.owner.attackState != self.state:
			return

		if targetEntity is None:
			self.actionEnd()
			return

		if BigWorld.player().targetEntity != targetEntity:
			self.actionEnd()
			return

		if not success:
			self.actionEnd()
			return

		self.__attackTarget( targetEntity )

	def __getAutoUseSpell( self, target ):
		"""
		@param target :	entity

		��һ��target������ԭ���ǣ���ȷ˵������ʵ���Ļ���Ǻ�target�����йصġ�
		"""
		skillInstance = Skill.getSkill( self.owner.getAutoSkillID() )
		target = skillInstance.getCastObject().convertCastObject( self.owner, target )
		target = SkillTargetObjImpl.createTargetObjEntity( target )
		state = skillInstance.useableCheck( self.owner, target )
		if skillInstance.getType() == csdefine.BASE_SKILL_TYPE_PASSIVE or state != csstatus.SKILL_GO_ON:
			skillInstance = Skill.getSkill( self.defaultSkillID )
		return skillInstance

	def __getAutoUseSpellAttack( self, target, skillID ):
		"""
		@param target :	entity
		��Ϊ�Զ�ս��Ҫ���Ӽ����� ����Զ�ս���й����༼�� by����
		"""
		skillInstance = Skill.getSkill( skillID )
		target = skillInstance.getCastObject().convertCastObject( self.owner, target )
		target = SkillTargetObjImpl.createTargetObjEntity( target )
		state = skillInstance.useableCheck( self.owner, target )
		if skillInstance.getType() != csdefine.BASE_SKILL_TYPE_PASSIVE and state == csstatus.SKILL_GO_ON:
			return skillInstance
		return Skill.getSkill( self.defaultSkillID )

		
	def __getTarget( self ):
		"""
		����µĹ���Ŀ��
		"""
		target = self.owner.targetEntity
		if target is not None and self.AFconfig["radius"] > 0 and \
			( target.position.distTo( self.startPosition ) - target.getBoundingBox().z ) > self.AFconfig["radius"] :
				rds.targetMgr.unbindTarget()
				self.owner.statusMessage( csstatus.AUTO_FIGHT_TARGET_OUT_RANGE )
				target = None
		if not self.__targetCnd( target ):
			target = self.__getNearbyMonster()
		return target

	def __targetCnd( self, target ):
		"""
		"""
		player = BigWorld.player()
		
		if target is None or not ( ( target.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and self.owner.qieCuoTargetID == target.id ) or \
			( target.isEntityType( csdefine.ENTITY_TYPE_PET ) and self.owner.qieCuoTargetID == target.ownerID ) or target.utype in Const.ATTACK_MOSNTER_LIST ) or \
				not target.isAlive() or target.hasFlag( csdefine.ENTITY_FLAG_SPEAKER ) or self.owner.isQuestMonster( target ) or \
			 		( not target.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and target.hasFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED ) ) or \
			 			target.hasFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE ) or target.hasFlag( csdefine.ENTITY_FLAG_FRIEND_ROLE ) or \
			 			target.hasFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE_2 ):
			 				return False
		if target.hasFlag( csdefine.ENTITY_FLAG_UNVISIBLE ):
			pid = target.ownerVisibleInfos[ 0 ]
			tid = target.ownerVisibleInfos[ 1 ]
			if pid == player.id or ( player.isInTeam() and tid == player.teamID ):
				return True
			return False
		return True

	def __getNearbyMonster( self, meter = Const.AUTO_ATTACK_RANGE ):
		"""
		��ȡ���Լ������һ������
		ԭ��Ϊ��__getLatestMonster
		�޸Ĳ�������Ϊ��__getNearbyMonster��hyw -- 2008.11.08��
		"""
		autoFightList = self.owner.getAutoFightList()
		for index in xrange( len( autoFightList ) - 1, -1, -1 ):
			target = BigWorld.entities.get( autoFightList[ index ] )
			if target is None or not target.isAlive() or \
				( self.AFconfig["radius"] > 0 and ( target.position.distTo( self.startPosition ) - target.getBoundingBox().z ) > self.AFconfig["radius"] ):
				del autoFightList[ index ]
			else :
				if not self.__targetCnd( target ):
					continue
				return target

		monsters = self.owner.entitiesInRange( meter, cnd = self.attackVerifier )
		
		spaceType = self.owner.getCurrentSpaceType()
		if spaceType == csdefine.SPACE_TYPE_CITY_WAR:
			isRight = self.owner.tongInfos['right'].keys()[0] == self.owner.tong_dbID
			for monster in monsters:
				if not self.__targetCnd( monster ):
					continue
				if monster.isRight != isRight:
					return monster
		else:
			for monster in monsters:
				if not self.__targetCnd( monster ):
					continue
				return monster

		return None

	def attackVerifier( self, entity ) :
		"""
		�Ƿ��ǿɹ�������( hyw -- 2008.11.08 )
		"""
		# ��ѡ��Χ��Ĳ���ѡ��
		if self.AFconfig["radius"] > 0 and ( entity.position.distTo( self.startPosition ) - entity.getBoundingBox().z ) > self.AFconfig["radius"] :
			return False

		if self.AFconfig["isAutoPlus"] and entity.isEntityType( csdefine.ENTITY_TYPE_PET ):
			if self.owner.qieCuoTargetID == entity.ownerID:
				return True
			else:
				self.autoPlusSkillPet( entity )
		elif self.AFconfig["isAutoPlus"] and entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if self.owner.qieCuoTargetID == entity.id:
				return True
			else:
				self.autoPlusSkill( entity )

		if entity.isEntityType( csdefine.ENTITY_TYPE_TONG_NAGUAL ):
			# ������������and��һ��
			if not self.owner.tong_dbID in entity.enemyTongDBIDList:
				return False
		elif not entity.utype in Const.ATTACK_MOSNTER_LIST:		# �����ǹ���
			if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and self.owner.qieCuoTargetID == entity.id:
				return True
			if entity.isEntityType( csdefine.ENTITY_TYPE_PET )  and self.owner.qieCuoTargetID == entity.ownerID:
				return True
 			return False

		if not hasattr( entity, "modelNumber" ):
			return False

		if entity.getState() != csdefine.ENTITY_STATE_FREE:								# ����ս��״̬�µ�һЩ���������ҲҪ����Ϊ���Զ�ս��
			target = BigWorld.entities.get( entity.targetID, None )

			if target is None:															#1.���﹥����Ŀ�겻����Ұ��Χ��
				return True

			if self.owner.id == target.id:												#2.���﹥����Ŀ�����Լ�
				return True

			pet = self.owner.pcg_getActPet()
			if pet is not None and pet.id == target.id:									#3.���﹥����Ŀ�����Լ��ĳ���
				return True

			if self.owner.isTeamMember( target.id ):									#4.���﹥����Ŀ�����Լ��Ķ�Ա
				return True

			if target.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ):				#5.���﹥����Ŀ����ڣ������Լ����ڳ�
				if BigWorld.entities[entity.targetID].ownerID == self.owner.id:
					return True

			if not target.getEntityType() in [csdefine.ENTITY_TYPE_ROLE, csdefine.ENTITY_TYPE_PET, csdefine.ENTITY_TYPE_VEHICLE_DART]:				#6.���﹥����Ŀ�겻����ң����ǳ�������ڳ�������Ա�ѡ��
				return True

		else:							#7.��������ս��״̬�Ĺ�������Ա���Ϊ�Զ�ս��Ŀ��
			return True

		return False

	def onItemDrop( self, dropEntity ):
		"""
		ʰȡ֪ͨ
		"""
		self.pickUpAction()

	def pickUpAction( self ):
		"""
		ʰȡ��Ϊ��ʼ
		"""
		if not self.owner.getPickItemNeed():
			return

		self.pickUpList = self.getDropItemsNearBy()
		if len( self.pickUpList ) == 0:
			return

		# ���˵�ʰȡ��������
		tempPickUpList = list( self.pickUpList )
		[ self.pickUpList.remove( tempDropEntity ) for tempDropEntity in tempPickUpList if tempDropEntity.isLooked == True ]
		if len( self.pickUpList ) == 0: # ���˺���б�Ϊ���򷵻�
			return
		dropEntity = self.pickUpList.pop()
		if dropEntity.id == self.lastDropEntityID and len( self.pickUpList ) != 0:
			dropEntity = self.pickUpList.pop()

		self.lastDropEntityID = dropEntity.id
		dropEntity.isLooked = True
		self.owner.startPickUp( dropEntity )
		BigWorld.callback( Const.AUTO_PICK_UP_DELAY, Functor( self.__pickUpAllItem, dropEntity ) )

	def __pickUpAllItem( self, dropEntity ):
		"""
		��ȡ������Ʒ
		"""
		# ����ѡ��ʰȡ
		isIPU = self.AFconfig["isIgnorePickUp"] #�Ƿ����ʰȡ		
		if isIPU:
			igList = self.AFconfig["ignoredList"]#�����б�
			if len( igList ) <= 0: #
				dropEntity.pickUpAllItems()
			else:
				indexs = []
				for k in dropEntity.boxItems:
					put = k["item"].getPickUpType()
					# �����k["item"].getQuality() - 1����Ϊ�����÷����϶���0~4��Ʒ�ʷ�Χ�����ʹ��20000��Ϊ��װ�����Ҳֻ�������
					put = put + (k["item"].getQuality() - 1) if put in ItemTypeEnum.PICK_UP_TYPE_QUALITY_AREA else put
					if put in igList:
						continue
					indexs.append( k["order"] )
				if len( indexs ) > 0:
					dropEntity.cell.pickDropItems( indexs )
		else:
			pList = self.AFconfig["pickUpTypeList"]#ʰȡ�б�
			if len( pList ):
				indexs = []
				for k in dropEntity.boxItems:
					put = k["item"].getPickUpType()
					# �����k["item"].getQuality() - 1����Ϊ�����÷����϶���0~4��Ʒ�ʷ�Χ�����ʹ��20000��Ϊ��װ�����Ҳֻ�������
					put = put + (k["item"].getQuality() - 1) if put in ItemTypeEnum.PICK_UP_TYPE_QUALITY_AREA else put
					if put in pList:
						indexs.append( k["order"] )
				if len( indexs ) > 0:
					dropEntity.cell.pickDropItems( indexs )
		self.owner.stopPickUp()
		if len( self.pickUpList ) == 0:
			return
		dropEntity = self.pickUpList.pop()
		self.lastDropEntityID = dropEntity.id
		self.owner.startPickUp( dropEntity )
		BigWorld.callback( Const.AUTO_PICK_UP_DELAY, Functor( self.__pickUpAllItem, dropEntity ) )

	def getDropItemsNearBy( self, range = Const.AUTO_PICK_UP_DISTANCE ):
		"""
		������Χ����Ʒ
		"""
		return self.owner.entitiesInRange( range, cnd = lambda ent : ent.__class__ == DroppedBox and ent.canPickUp )

	def setControlSkillID( self, skillID ):
		"""
		�����Զ�ս����;����ֶ�ʹ�õļ���ID by ����
		"""
		self.controlSkillID = skillID

	#------------------�����Զ�ս�����ù��� 17:13 2009-12-4 by ����------------------
	def actPetAutoConj( self ):
		"""
		�����ٻ��������﹦��
		"""
		owner = self.owner
		if self.actPetInfo != None and owner.pcg_getActPet() is None:
			conjResult = self.actPetInfo.conjureForAutoFight( owner )
			if conjResult == 1 or conjResult == -1 or conjResult in self.onceMessageList:
				return
			else:
				owner.statusMessage( conjResult )
				self.onceMessageList.append( conjResult )

	def setAutoPet( self, reset ):
		"""
		�����Զ�����ļ�Ҫ����
		@ param : reset �Ƿ��ֵĬ��ֵ
		@ param : reset BOOL
		"""
		if reset:
			self.actPetInfo = None
			return
		pet = self.owner.pcg_getActPet()
		if pet is None: return
		self.actPetInfo = self.owner.pcg_getPetEpitomes()[ pet.databaseID ]

	def actPetAutoJoyCharge( self, joyLess ):
		"""
		���������ֶȹ���
		@ param : joyLess �����е��貹����С���ֶ�
		@ param : joyLess INT8
		"""
		if self.actPetInfo is None: return
		owner = self.owner
		pet = owner.pcg_getActPet()
		if pet is None: return
		if pet.joyancy >= joyLess: return
		index = ( pet.level - 1 ) / 30
		itemID = csconst.pet_joyancy_items[index]
		if not self.actPetInfo.addJoyanceForAutoFight( owner ):
			if csstatus.SKILL_PET_JOYANCY_ITEM_NO_EXIST in self.onceMessageList:
				return
			owner.statusMessage( csstatus.SKILL_PET_JOYANCY_ITEM_NO_EXIST, g_items.id2name( itemID ) )
			self.onceMessageList.append( csstatus.SKILL_PET_JOYANCY_ITEM_NO_EXIST )
			
	def actAutoRepair( self, rate ):
		"""
		�Զ�ʹ����Ʒ����װ��
		"""
		equips = self.owner.getItems( csdefine.KB_EQUIP_ID )
		needRep = False
		for equip in equips:
			hardMax = equip.getHardinessLimit()
			if hardMax == 0:
				continue
			hardNow = float(equip.getHardiness())
			if (hardNow/hardMax * 100) < rate:
				needRep = True
				break
		if needRep:
			repItems = self.owner.findItemsFromNKCK_( Const.AUTO_FIGHT_REPAIR_ITEM_ID )
			if len(repItems) <= 0:
				if csstatus.EQUIP_REPAIR_NO_REP_ITEM not in self.onceMessageList:
					self.owner.statusMessage( csstatus.EQUIP_REPAIR_NO_REP_ITEM )
					self.onceMessageList.append( csstatus.EQUIP_REPAIR_NO_REP_ITEM )
				return
			item = repItems[0]
			self.owner.useItemDependOnType( item.getUid(), item, item.getType() )
			
	def actAutoReboin( self ):
		"""
		�Զ�����
		"""
		p_state = self.owner.getState()
		if p_state == csdefine.ENTITY_STATE_DEAD:
			reboinItems = self.owner.findItemsFromNKCK_( Const.AUTO_FIGHT_REBOIN_ITEM_ID )
			if len(reboinItems) <= 0:
				if self.owner.level < 30:
					return False
				ECenter.fireEvent( "EVT_ON_HIDE_REVIVE_BOX" )
				def query( rs_id ):
					if rs_id == RS_OK:
						ECenter.fireEvent( "EVT_ON_TOGGLE_SPECIAL_SHOP" )
				if not self.pyBox is None:
					self.pyBox.visible = False
					self.pyBox = None
				self.pyBox = showMessage( mbmsgs[0x00c7], "", MB_OK_CANCEL, query )
				return False
			item = reboinItems[0]
			self.owner.cell.useItemRevive()
			#self.attackState = Const.ATTACK_STATE_AUTO_FIGHT
		return True

	def autoRangeCheck( self ):
		"""
		�����ԭ����룬������Ļ��������ߣ����뷶Χ�ھͲ�����
		"""
		if self.AFconfig["radius"] == 0:
			self.actionEnd()
			return
		owner = self.owner
		if ( owner.position.distTo( self.startPosition ) - owner.getBoundingBox().z ) < self.AFconfig["radius"]:
			self.actionEnd()
			return
		owner.moveTo( self.startPosition )
		self.actionEnd()

	def autoPlusSkillPet( self, pet ):
		"""
		��������Զ����漼�ܵ���ع���
		"""
		owner = self.owner
		plusInfo = owner.getAutoPlusInfo()
		if plusInfo[1] == 1:
			p = owner.pcg_getActPet()
			if p is not None and p.id == pet.id:
				skillID = self.checkPlusSkill( pet )
				if skillID <= 0: return
				skillInstance = Skill.getSkill( skillID )
				if skillInstance._datas["ReceiverCondition"]["conditions"] == "RECEIVER_CONDITION_ENTITY_ROLE":
					self.__useSkill( pet, skillInstance )
				return
		if plusInfo[2] == 1 and plusInfo[1] == 1:
			o = pet.getOwner()
			if o is not None and o.id != owner.id and o.id in owner.teamMember:
				skillID = self.checkPlusSkill( pet )
				if skillID <= 0: return
				skillInstance = Skill.getSkill( skillID )
				if skillInstance._datas["ReceiverCondition"]["conditions"] == "RECEIVER_CONDITION_ENTITY_ROLE":
					self.__useSkill( pet, skillInstance )

	def autoPlusSkill( self, role ):
		"""
		�����ɫ�Զ����漼����صĹ���
		"""
		owner = self.owner
		plusInfo = owner.getAutoPlusInfo()
		if plusInfo[0] == 1 and role.id == owner.id:
			skillID = self.checkPlusSkill( role )
			if skillID <= 0: return
			skillInstance = Skill.getSkill( skillID )
			self.__useSkill( role, skillInstance )
			return
		if plusInfo[2] == 1 and role.id != owner.id and role.id in owner.teamMember:
			skillID = self.checkPlusSkill( role )
			if skillID <= 0: return
			skillInstance = Skill.getSkill( skillID )
			if skillInstance._datas["ReceiverCondition"]["conditions"] == "RECEIVER_CONDITION_ENTITY_ROLE":
				self.__useSkill( role, skillInstance )

	def checkPlusSkill( self, entity ):
		"""
		����������漼�ܵĿ�����
		ע�⣬���漼���Զ��ͷ�ϵͳֻ�Բ���buff�ļ�����Ч�������漼�ܶ����ܲ���buff�ļ���
		��ˣ�һ����˵�ǲ�����ɶ�����
		������漼���б�����˲��ܲ���buff�ļ��ܣ���ô��ڰ���
		"""
		if entity is None: return 0
		skillIDs = self.owner.getAutoPlusSkillIDList()
		if len( skillIDs ) == 0: return 0
		buffSkillIDs = []
		for idx, buff in enumerate( entity.attrBuffs ):
			id = buff["skill"].getID()
			sk = Skill.getSkill( id )
			if sk.getType() == csdefine.BASE_SKILL_TYPE_BUFF:		# ����buff���ܣ���Ҫȷʵȡ����Դ����
				id = sk.getSourceSkillID()
			buffSkillIDs.append( int(id/1000) )

		for skillID in skillIDs:
			id = int(skillID/1000)
			if id not in buffSkillIDs:
				return skillID
		return 0

class Attack:
	"""
	"""
	def __init__( self ):
		"""
		"""
		self.attackState = Const.ATTACK_STATE_NONE
		self.autoSkillID = 0
		self.autoSkillIDList = []		# �Զ�ս���Ķ������ID�� by����
		self.autoPlusSkillList = []		# �Զ�ս���Ķ�����漼��ID by����
		self.castingSpell = 0			# ���������ļ��ܡ�
		self.isInHomingSpell = False
		self.lastUseAutoSkillID = 0	# ���һ��ʹ�õ����Զ����������ļ��ܣ���ͨ��������/���������������ܣ�	
		self.attackInstanceDict = {}
		self.attackInstanceDict[ Const.ATTACK_STATE_NONE ]					= NoAttack( self )
		self.attackInstanceDict[ Const.ATTACK_STATE_ONCE ]					= OnceAttack( self )
		self.attackInstanceDict[ Const.ATTACK_STATE_NORMAL ]				= AutoNormalAttack( self )
		self.attackInstanceDict[ Const.ATTACK_STATE_AUTO_FIGHT ]			= AutoFightAttack( self )
		self.attackInstanceDict[ Const.ATTACK_STATE_AUTO_SPELL ]			= AutoSpellAttack( self )
		self.attackInstanceDict[ Const.ATTACK_STATE_AUTO_CONFIRM_SPELL ]	= AutoConfirmSpellAttack( self )
		self.attackInstanceDict[ Const.ATTACK_STATE_HOMING_SPELL ]			= AutoHomingSpellAttack( self )
		self.attackInstanceDict[ Const.ATTACK_STATE_SPELL_AND_HOMING ]		= SpellAutoHomingAttack( self )
		self.attackInstanceDict[ Const.ATTACK_STATE_AUTO_SPELL_HOMING ]		= SpellAndAutoHomingAttack( self )
		self.attackInstanceDict[ Const.ATTACK_STATE_AUTO_SPELL_CURSOR ]		= AutoConfirmSpellAttackCursor( self )
		# �Զ�ս�����
		rds.shortcutMgr.setHandler( "COMBAT_AUTOFIGHT", self.__toggleAutoFight )
		self.__damageList = []
		self.roleAutoRestore = AutoRestore()		# ��ɫ�Զ��ָ�
		self.petAutoRestore = PetAutoRestore()		# �����Զ��ָ�

		# �Զ�ʰȡ���
		self.autoFight2AutoSpellTimerID = 0
		self.autoRestoreTimerID = 0
		cfgSect = self.roleAutoRestore.getConfigSect()

		# �Զ�ս����������� by ����
		# �Զ����漼�ܶ������� [ ��ɫ�� ��� ���� ]
		self.autoPlusInfo = [0, 0, 0]
		self.autoFightConfig = self.getAutoFightConfig()
		self.isAutoPickUp = self.getPickItemNeed()					# �Ƿ��Զ�ʰȡ
		self.autoPlusInfo = self.getAutoPlusInfo()

	def autoRestoreDetect( self ):
		"""
		��ʼ�Զ��ָ�
		"""
		if self.isAutoRestore():
			BigWorld.cancelCallback( self.autoRestoreTimerID )
		self.autoRestoreTimerID = BigWorld.callback( Const.AUTO_RESTORE_DETECT_INTERVAL, self.autoRestoreDetect )
		self.autoRestore()

	def isAutoRestore( self ):
		"""
		�Ƿ����Զ��ָ���
		"""
		return self.autoRestoreTimerID != 0

	def autoRestore( self ):
		"""
		�Զ��ָ�
		"""
		if self.intonating():
			return
		if self.actionSign( csdefine.ACTION_FORBID_USE_ITEM ):
			return
		self.roleAutoRestore.restore( self )			# ��ɫ�Զ��ָ�
		activePet = self.pcg_getActPet()
		if activePet is not None:
			self.petAutoRestore.restore( activePet )	# �����Զ��ָ�

	def stopAutoRestore( self ):
		"""
		ֹͣ�Զ��ָ�
		"""
		BigWorld.cancelCallback( self.autoRestoreTimerID )
		self.autoRestoreTimerID = 0

	def isChange2AutoSpell( self ):
		"""
		�Ƿ���л����Զ��ͷż��ܹ���״̬
		"""
		return self.autoFight2AutoSpellTimerID != 0

	def cancelAutoFight2AutoSpellTimer( self ):
		"""
		�˳��Զ�ս���л����Զ��ͷż��ܹ���״̬
		"""
		BigWorld.cancelCallback( self.autoFight2AutoSpellTimerID )
		self.autoFight2AutoSpellTimerID = 0

	def setPickItemNeed( self, need ):
		"""
		"""
		sect = self.roleAutoRestore.getConfigSect()
		sect.writeBool( "isAutoPickUp", need )
		self.isAutoPickUp = need
		self.autoFightConfig["isAutoPickUp"] = need
		self.roleAutoRestore.saveCfgSect()

	def getPickItemNeed( self ):
		"""
		"""
		return self.autoFightConfig["isAutoPickUp"]

	def setAutoPlusInfo( self, targetList ):
		"""
		�����Զ����漼�ܶ���
		"""
		sect = self.roleAutoRestore.getConfigSect()
		sect.writeVector3( "plusSkillTarget", tuple( targetList ) )
		self.autoPlusInfo = targetList
		self.autoFightConfig["plusSkillTarget"] = targetList
		AutoFightConfig["plusSkillTarget"] = self.autoPlusInfo
		self.roleAutoRestore.saveCfgSect()

	def getAutoPlusInfo( self ):
		"""
		"""
		targetList = self.autoFightConfig["plusSkillTarget"]
		for index, target in enumerate( list( targetList ) ):
			self.autoPlusInfo[index] = int( target )
		return self.autoPlusInfo

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache�������
		"""
		if self.qb_canAutoRestore() and not self.isAutoRestore():
			self.autoRestoreDetect()

	def leaveWorld( self ) :
		"""
		"""
		self.cancelAttackState()
		self.stopAutoRestore()
		BigWorld.cancelCallback( self.autoFight2AutoSpellTimerID )
		self.autoFight2AutoSpellTimerID = 0

	def getAtackState( self ):
		"""
		��õ�ǰ��ҵĹ���״̬
		"""
		return self.attackState

	def getAutoSkillID( self ):
		"""
		����Զ��ͷŵļ���
		"""
		if skillID == 0 :
			skillID = Define.SKILL_ID_TRIGGER_SKILLS.get( self.getClass() )
		return self.autoSkillID

	def setAutoSkillID( self, skillID = 0  ):
		"""
		�����Զ��ͷż���id
		"""
		if skillID == 0 :
			skillID = Define.SKILL_ID_TRIGGER_SKILLS.get( self.getClass() )
		self.autoSkillID = skillID

	def getAutoSkillIDList( self ):
		"""
		����Զ��ͷŵļ���id list by����
		�����id list��Ԫ��һ��Ҫ�����Զ�ս�����ļ��ܴ���������~
		"""
		return self.autoSkillIDList

	def setAutoSkillIDList( self, skillIDList = [] ):
		"""
		�����Զ��ͷż���id list by����
		"""
		self.autoSkillIDList = skillIDList

	def getAutoPlusSkillIDList( self ):
		"""
		����Զ��ͷŵ����漼��id list by����
		�����id list��Ԫ��һ��Ҫ�������漼�������ϵ�������~
		"""
		cfgSect = self.roleAutoRestore.getConfigSect()
		if cfgSect.has_key( "plusSkills" ):
			skIDStr = cfgSect.readString( "plusSkills" )
			skIDs = skIDStr.split( "|" )
			for skId in skIDs:
				if skId == "" or int( skId ) in self.autoPlusSkillList:continue
				self.autoPlusSkillList.append( int( skId ) )
		return self.autoPlusSkillList

	def setAutoPlusSkillIDList( self, skillIDList = [] ):
		"""
		�����Զ��ͷ����漼��id list by����
		"""
		self.autoPlusSkillList = skillIDList
		skIDStr = ""
		for skillID in skillIDList:
			skIDStr += "%s|"%str( skillID)
		cfgSect = self.roleAutoRestore.getConfigSect()
		if not cfgSect.has_key( "plusSkills" ):
			cfgSect.createSection( "plusSkills" )
		cfgSect.writeString( "plusSkills", skIDStr )
		AutoFightConfig["autoPlusSkillList"] = self.autoPlusSkillList
		self.roleAutoRestore.saveCfgSect()

	def getNormalAttackSkillID( self ):
		"""
		�����ͨ��������id
		"""
		return Define.SKILL_ID_TRIGGER_SKILLS.get( self.getClass() )

	def setLastUseAutoSkillID( self, skillID ):
		"""
		�������һ��ʹ�õ������������ļ���ID����ͨ������/�������ܹ�����
		"""
		self.lastUseAutoSkillID = skillID

	def getLastUseAutoSkillID( self ):
		"""
		������һ��ʹ�õ������������ļ���ID
		"""
		if self.lastUseAutoSkillID == 0 :
			self.lastUseAutoSkillID = Define.SKILL_ID_TRIGGER_SKILLS.get( self.getClass() )
		return self.lastUseAutoSkillID

	def changeAttackState( self, attackState, *arg ):
		"""
		����״̬�ı�
		@param arg : ״̬��Ҫ���ⲿ������
		"""
		attackArgument = AttackArgumentFactory.getAttackArgument( attackState, arg )
		if self.attackState == Const.ATTACK_STATE_AUTO_FIGHT and attackArgument:
			self.attackInstanceDict[ self.attackState ].setControlSkillID( attackArgument.param )
			
		if self.attackInstanceDict[ attackState ].canChangeState( self.attackState, attackArgument ):
			DEBUG_MSG( "attackState change,%i-->>>%i." % ( self.attackState, attackState ) )
			self.attackInstanceDict[ self.attackState ].leave()
			self.attackState = attackState
			self.attackInstanceDict[ self.attackState ].enter( attackArgument )
			ECenter.fireEvent( "EVT_ON_ATTACK_STATE_CHANGTED", attackState )
		else:
			DEBUG_MSG( "Cannot change attackState,%i-->>>%i." % ( self.attackState, attackState ) )

	def cancelAttackState( self ):
		"""
		���ô˽ӿڵ�ԭ����Ϊ��������changeAttackState��changeAttackState�ǿͻ���������Ҫ��֤��
		��cancelAttackState�ǳ������󣬲�����֤��ĳһ������״̬���н�������ô˽ӿ��˳���
		"""
		if self.attackState == Const.ATTACK_STATE_NONE:
			return
		DEBUG_MSG( "attackState change,%i-->>>%i." % ( self.attackState, Const.ATTACK_STATE_NONE ) )
		self.attackInstanceDict[ self.attackState ].leave()
		self.attackState = Const.ATTACK_STATE_NONE
		self.attackInstanceDict[ self.attackState ].enter( None )

	def isInSpellRange( self, target, spell ) :
		"""
		indicate the role whether in spell range now
		"""
		rng = self.distanceBB( target )
		if rng > spell.getRangeMax( self ) :
			return False
		return True
	
	def isInSpellDis( self, pos, spell):
		return True

	def interruptAttack( self, reason ):
		"""
		interrupt attacking
		���������ʲô״̬��ֻҪ�������������ƶ������ϼ��ܡ�
		@param	reason	: ��ϵ�ԭ��һ����csstatus�ж��壩
		@type	reason	: int
		"""
		if self.intonating() or self.isInHomingSpell:
			self.cell.interruptSpellFC( reason )
			self.setCastingSpell( 0 )
			self.isInHomingSpell = False
		self.attackInstanceDict[ self.attackState ].interruptAttack( reason )

	def intonate( self, skillID, intonateTime, targetObject ):
		"""
		intonate
		@type		skillID	: INT
		@param	skillID	: skill id of intonate
		@return 			: None
		"""
		self.showSpellingItemCover( skillID )
		self.setCastingSpell( skillID )

	def castSpell( self, skillID, targetObject ):
		"""
		��ʼʩ��������������������id
		"""
		self.hideSpellingItemCover()
		self.setCastingSpell( 0 )
		if not hasattr( targetObject , "_entityID" ):
			return 
			
		targetID = targetObject._entityID
		skillInstance = Skill.getSkill( skillID )
		if targetID not in self.__damageList and targetID != self.id and skillInstance.isMalignant(): # ���Լ��ܲż����˺��б�
			self.__damageList.insert( -1, targetID )

	def intonating( self ):
		"""
		if player is in attacking state, it will return True
		"""
		return self.castingSpell != 0

	def setCastingSpell( self, skillID ):
		"""
		�������������ļ���id
		"""
		self.castingSpell = skillID

	def onStartHomingSpell( self ):
		"""
		define method.
		��ʼ��������
		"""
		self.isInHomingSpell = True

	def onFiniHomingSpell( self ):
		"""
		������������
		"""
		self.isInHomingSpell = False

	def onSpellInterrupted( self, skillID, reason ):
		"""
		�������ж������Ļص�֪ͨ��
		attack interrupt has been accepted
		"""
		if reason != csstatus.SKILL_INTONATING:
			self.setCastingSpell( 0 )
			GUIFacade.onRoleSpellInterrupted()
		self.attackInstanceDict[ self.attackState ].onSpellInterrupted( skillID, reason )

	def onStateChanged( self, old, new ):
		"""
		when player's state is changed, it will be called
		"""
		self.attackInstanceDict[ self.attackState ].onStateChanged( old, new )
		if new == csdefine.ENTITY_STATE_DEAD:
			self.stopAutoRestore()

		if old == csdefine.ENTITY_STATE_DEAD:
			self.autoRestoreDetect()
		elif old == csdefine.ENTITY_STATE_FIGHT:
			self.resetAutoFightList()

	def onMoveChanged( self, isMoving ):
		"""
		change move state( from moving to standing or reverse )
		see also python_client.chm/Class list/getPhysics().isMovingNotifier
		@type		isMoving : bool
		@param		isMoving : indicate wether in moving state
		@return				 : None
		"""
		if isMoving:						# spelling is interupted when start moving
			if self.intonating() or self.isInHomingSpell:
				self.getPhysics().targetSource = None
				self.getPhysics().targetDest = None
				#self.flushAction()
			if not self.isInHomingSpell:
				self.interruptAttack( csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_2 )
		GUIFacade.onRoleMoved( isMoving )

	# --------------------------------- �Զ�ս����ش��� -----------------------------------------
	def toggleAutoFight( self ):
		"""
		"""
		self.__toggleAutoFight()

	def onPetReceiveDamage( self, petTargetID ):
		if not self.isAutoFight(): return
		if petTargetID not in self.__damageList:
			self.__damageList.insert( -1, petTargetID )

	def onReceiveSpell( self, casterID, skillID, damageType, damage ):
		"""
		�ܵ��˺�
		"""
		if casterID not in self.__damageList:
			self.__damageList.insert( -1, casterID )
			try:
				target = BigWorld.entities[casterID]
			except KeyError:
				pass
			else:
				if target.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or target.isEntityType( csdefine.ENTITY_TYPE_PET ):
		 			spaceType = self.getCurrentSpaceType()
					if spaceType != csdefine.SPACE_TYPE_CITY_WAR:
						targetName = target.getName()
						if self.onFengQi:
							targetName = lbs_ChatFacade.masked
						self.statusMessage( csstatus.ATTACK_CAN_COUNTER, targetName )
		self.attackInstanceDict[ self.attackState ].onReceiveSpell( casterID )

	def getAutoFightList( self ):
		"""
		�����ҵ��Զ�ս��Ŀ��id�б�
		"""
		return self.__damageList

	def resetAutoFightList( self ):
		"""
		�������Զ�ս���б�
		"""
		self.__damageList = []

	def inDamageList( self, entity ):
		"""
		entity�Ƿ����˺��б���
		"""
		return entity.id in self.__damageList
	
	def getDamageLength( self ):
		"""
		����˺��б�ĳ���
		"""
		return len( self.__damageList )

	def isAutoFight( self ):
		"""
		�Ƿ����Զ�ս��״̬
		"""
		return self.attackState == Const.ATTACK_STATE_AUTO_FIGHT

	def __toggleAutoFight( self ):
		"""
		�����Զ�ս��
		"""
		if not self.hasAutoFight:
			if not self.pyBox is None:
				self.pyBox.visible = False
				self.pyBox = None
			self.pyBox = showMessage( mbmsgs[0x0ec6], "", MB_OK )
			return False
		if self.isAutoFight():
			self.stopAutoFight()
		else:
			self.changeAttackState( Const.ATTACK_STATE_AUTO_FIGHT )

	def change2AutoSpell( self ):
		"""
		ת���Զ�ʹ�ü��ܹ���״̬

		9:57 2009-2-16,�������˳��Զ�ս��״̬��������Զ�ʹ�ü��ܹ���״̬��
		13:20 2009-3-20���������Ϊ���˳��Զ�ս�����������ս��״̬������Զ�ʹ�ü��ܹ���״̬��
		"""
		self.changeAttackState( Const.ATTACK_STATE_NONE )

		if self.state == csdefine.ENTITY_STATE_FIGHT:
			# ��ʱhit_speed�Ժ�����Զ�ʹ�ü��ܹ���״̬�����������Զ�����״̬�Ļ��п��������˳���
			# ��Ϊ��ͨ�������п��ܸո�ʹ��������coolDown״̬��ʹ�ü���ʹ�ò��ɹ�����˳��Զ�����״̬��
			delay = self.hit_speed
			self.autoFight2AutoSpellTimerID = BigWorld.callback( delay, Functor( self.changeAttackState, Const.ATTACK_STATE_AUTO_SPELL ) )

	# ---------------------------------- �Զ��ָ� -------------------------------------
	def getRoleHpRestorePercent( self ):
		"""
		��ý�ɫ�Զ���Ѫ�ٷֱ�ֵ
		"""
		return self.roleAutoRestore.getHpPercent()

	def getRoleMpRestorePercent( self ):
		"""
		��ý�ɫ�Զ������ٷֱ�ֵ
		"""
		return self.roleAutoRestore.getMpPercent()

	def getPetHpRestorePercent( self ):
		"""
		��ó����Զ���Ѫ�ٷֱ�ֵ
		"""
		return self.petAutoRestore.getHpPercent()

	def getPetMpRestorePercent( self ):
		"""
		��ó����Զ������ٷֱ�ֵ
		"""
		return self.petAutoRestore.getMpPercent()

	def setRoleHpRestorePercent( self, percent ):
		"""
		���ý�ɫ�Զ���Ѫ�ٷֱ�ֵ
		"""
		sect = self.roleAutoRestore.getConfigSect()
		sect.writeFloat( "Role_HP", percent )
		self.roleAutoRestore.setHpPercent( percent )

	def setRoleMpRestorePercent( self, percent ):
		"""
		���ý�ɫ�Զ������ٷֱ�ֵ
		"""
		sect = self.roleAutoRestore.getConfigSect()
		sect.writeFloat( "Role_MP", percent )
		self.roleAutoRestore.setMpPercent( percent )

	def setPetHpRestorePercent( self, percent ):
		"""
		���ó����Զ���Ѫ�ٷֱ�ֵ
		"""
		sect = self.petAutoRestore.getConfigSect()
		sect.writeFloat( "Pet_HP", percent )
		self.petAutoRestore.setHpPercent( percent )

	def setPetMpRestorePercent( self, percent ):
		"""
		���ó����Զ������ٷֱ�ֵ
		"""
		sect = self.petAutoRestore.getConfigSect()
		sect.writeFloat( "Pet_MP", percent )
		self.petAutoRestore.setMpPercent( percent )

	# ---------------------�Զ�ս������---------------------
	def stopAutoFight( self ):
		"""
		ֹͣ�Զ�ս��
		"""
		self.change2AutoSpell()


	def setAutoFightConfig( self, config = {} ):
		"""
		�����Զ�ս���������
		@ param : config �����ֵ�
		@ param : congig DICT
		"""
		if len( config ) == 0:
			self.autoFightConfig = {
									"isAutoPickUp":False,
									"isAutoConjure":True,
									"isAutoAddJoy":True,
									"isAutoPlus":False,
									"radius":0,
									"radiusAdd":15,
									"joyLess":0,
									"autoRepair":False,
									"autoReboin":False,
									"repairRate":0,
									"isIgnorePickUp":True,
									"pickUpTypeList":[],
									"ignoredList":[]
									}
		else:
			self.autoFightConfig = config
		cfgSect = self.roleAutoRestore.getConfigSect()
		for secKey, value in self.autoFightConfig.items():
			if not cfgSect.has_key( secKey ):
				cfgSect.createSection( secKey )
			if secKey in ["isAutoConjure", "isAutoAddJoy", "isAutoPlus", "autoRepair", "autoReboin", "isIgnorePickUp"]:
				cfgSect.writeBool( secKey, value )
			elif secKey in ["radius", "radiusAdd", "joyLess", "repairRate"]:
				cfgSect.writeInt( secKey, value )
		self.roleAutoRestore.saveCfgSect()
		AutoFightConfig["AutoFightConfig"] = self.autoFightConfig
		
	def setIgnorePickUp( self, value ):
		"""
		�����Ƿ�����Զ�ʰȡ����
		value is bool
		"""
		self.autoFightConfig["isIgnorePickUp"] = value
		cfgSect = self.roleAutoRestore.getConfigSect()
		if not cfgSect.has_key( "isIgnorePickUp" ):
			cfgSect.createSection( "isIgnorePickUp" )
		cfgSect.writeBool( "isIgnorePickUp", value )
		self.roleAutoRestore.saveCfgSect()
		
	def addPickType( self, itemType ):
		"""
		�����Զ�ʰȡ����
		"""
		ptl = self.autoFightConfig["pickUpTypeList"]
		if itemType in ptl:
			return
		ptl.append( itemType )
		
	def removePickType( self, itemType ):
		"""
		�Ƴ��Զ�ʰȡ����
		"""
		ptl = self.autoFightConfig["pickUpTypeList"]
		if not itemType in ptl:
			return
		ptl.remove( itemType )
	
	def getPickUpTypes( self, isIgnored ):
		"""
		��ȡ�������Զ�ʰȡ��Ʒ�����б�
		"""
		cfgSect = self.roleAutoRestore.getConfigSect()
		pickUpTypeList = []
		if not isIgnored: #ʰȡ��
			if cfgSect.has_key( "pickUpTypeList" ):
				typesStr = cfgSect.readString( "pickUpTypeList" ).split( "|" )
				for typeStr in typesStr:
					if typeStr == "":continue
					pickUpTypeList.append( int( typeStr ) )
		else: #
			if cfgSect.has_key( "ignoredList" ):
				typesStr = cfgSect.readString( "ignoredList" ).split( "|" )
				for typeStr in typesStr:
					if typeStr == "":continue
					pickUpTypeList.append( int( typeStr ) )
		return pickUpTypeList
	
	def setPickUpTypes( self, isIgnored, itemTypes = [] ):
		"""
		�����Զ�ʰȡ��Ʒ�����б�
		"""
		cfgSect = self.roleAutoRestore.getConfigSect()
		typesStr = ""
		for itemType in itemTypes:
			typesStr += "%s|"%str( itemType )
		if not isIgnored:
			if not cfgSect.has_key( "pickUpTypeList" ):
				cfgSect.createSection( "pickUpTypeList" )
			cfgSect.writeString( "pickUpTypeList", typesStr )
			self.autoFightConfig["pickUpTypeList"] = itemTypes
		else:
			if not cfgSect.has_key( "ignoredList" ):
				cfgSect.createSection( "ignoredList" )
			cfgSect.writeString( "ignoredList", typesStr )
			self.autoFightConfig["ignoredList"] = itemTypes
		self.roleAutoRestore.saveCfgSect()
		
	def setAutoRepair( self, value ):
		"""
		�����Զ�����
		value is bool
		"""
		cfgSect = self.roleAutoRestore.getConfigSect()
		cfgSect.writeBool( "autoRepair", value )
		self.autoFightConfig["autoRepair"] = value
		AutoFightConfig["AutoFightConfig"] = self.autoFightConfig
		self.roleAutoRestore.saveCfgSect()
		
	def isAutoRepair( self ):
		"""
		�Ƿ��Զ�����״̬
		"""
		return self.autoFightConfig["autoRepair"]
		
	def setAutoRepairRate( self, value ):
		"""
		�����Զ�����ٷֱ�
		value is int
		"""
		cfgSect = self.roleAutoRestore.getConfigSect()
		cfgSect.writeInt( "repairRate", value )
		self.autoFightConfig["repairRate"] = value
		AutoFightConfig["AutoFightConfig"] = self.autoFightConfig
		self.roleAutoRestore.saveCfgSect()
		
	def getAutoRepairRate( self ):
		"""
		����Զ�����ٷֱ�
		"""
		return self.autoFightConfig["repairRate"]
		
	def setAutoReboin( self, value ):
		"""
		�����Զ�����
		value is bool
		"""
		cfgSect = self.roleAutoRestore.getConfigSect()
		cfgSect.writeBool( "autoReboin", value )
		self.autoFightConfig["autoReboin"] = value
		AutoFightConfig["AutoFightConfig"] = self.autoFightConfig
		self.roleAutoRestore.saveCfgSect()
		
	def isAutoReboin( self ):
		"""
		�Ƿ��Զ�����״̬
		"""
		return self.autoFightConfig["autoReboin"]

	def setAutoRange( self, r ):
		"""
		test interface
		"""
		cfgSect = self.roleAutoRestore.getConfigSect()
		cfgSect.writeInt( "radius", value )
		self.autoFightConfig["radius"] = r
		AutoFightConfig["AutoFightConfig"] = self.autoFightConfig
		self.roleAutoRestore.saveCfgSect()

	def getAutoFightConfig( self ):
		"""
		"""
		cfgSect = self.roleAutoRestore.getConfigSect()
		autoConfig = {
						"isAutoConjure":cfgSect.readBool("isAutoConjure"),
						"isAutoAddJoy":cfgSect.readBool("isAutoAddJoy"),
						"isAutoPlus":cfgSect.readBool("isAutoPlus"),
						"radius":cfgSect.readInt("radius"),
						"radiusAdd":cfgSect.readInt("radiusAdd"),
						"joyLess":cfgSect.readInt("joyLess"),
						"autoRepair":cfgSect.readBool("autoRepair"),
						"autoReboin":cfgSect.readBool("autoReboin"),
						"repairRate":cfgSect.readInt("repairRate"),
						"isAutoPickUp":cfgSect.readBool("isAutoPickUp"),
						"plusSkillTarget":cfgSect.readVector3("plusSkillTarget"),
						"isIgnorePickUp":cfgSect.readBool("isIgnorePickUp"),
						"pickUpTypeList":self.getPickUpTypes( False ),
						"ignoredList": self.getPickUpTypes( True )
					}
		return autoConfig

	def onRemoveSkill( self, skillID ):
		"""
		�Ƴ����ܶ�ս��ϵͳ��Ӱ�� by ����
		"""
		if skillID in self.autoPlusSkillList:
			self.autoPlusSkillList.remove(skillID)
		AutoFightConfig["autoPlusSkillList"] = self.autoPlusSkillList
		skIDStr = ""
		for skID in self.autoPlusSkillList:
			skIDStr += "%s|"%str( skID )
		cfgSect = self.roleAutoRestore.getConfigSect()
		cfgSect.writeString( "plusSkills", skIDStr )
		self.roleAutoRestore.saveCfgSect()

	# --------------------------------------------- �Զ�ʰȡ -----------------------------------------
	def onItemDrop( self, dropEntity ):
		"""
		����Ʒ�����֪ͨ

		@param dropEntity :	��������entity
		@type dropEntity :		BigWorld entity
		"""
		self.attackInstanceDict[ self.attackState ].onItemDrop( dropEntity )

	def useSkill( self, skillID ):
		"""
		ͨ����ݼ�ʹ�ü���

		@param skillID:	����ID
		@type skillID :	int64
		"""
		# ���ʹ�õ�����ͨ���������������ܣ�������Զ���ͨ������������������״̬
		if skillID == Define.SKILL_ID_TRIGGER_SKILLS.get( self.getClass() ):
			self.setLastUseAutoSkillID( skillID )
			self.changeAttackState( Const.ATTACK_STATE_NORMAL )
			return
		# ���ʹ�õ������������������ܣ�������Զ�������������״̬
		sk = Skill.getSkill( skillID )
		isHomingSpell = sk.isHomingSkill()
		if isHomingSpell:
			if not sk.isNormalHomingSkill(): #����������������ܽ���ͨ�������� add by wuxo 2011-12-12
				self.setLastUseAutoSkillID( skillID )
				self.changeAttackState( Const.ATTACK_STATE_HOMING_SPELL )
				return

		
		from skills import Spell_Cursor
		from skills import Spell_Position
		if isinstance( sk, Spell_Cursor.Spell_Cursor) or isinstance( sk, Spell_Position.Spell_Position)  :
			self.changeAttackState( Const.ATTACK_STATE_AUTO_SPELL_CURSOR, skillID )
			return

		# ���ʹ�õ������Լ��ܣ�����뼼�ܹ���һ��״̬״̬
		# ���򣬸������һ��ʹ�õ�����ͨ������/����������������
		# �������Ӧ�Ĺ���״̬
		lastUseSkillID = self.getLastUseAutoSkillID()
		self.changeAttackState( Const.ATTACK_STATE_ONCE, skillID )

	def onLClickTargt( self ):
		"""
		����������Ŀ��
		"""
		
		lastUseSkillID = self.getLastUseAutoSkillID()
		if lastUseSkillID == Define.SKILL_ID_TRIGGER_SKILLS.get( self.getClass() ):
			self.changeAttackState( Const.ATTACK_STATE_ONCE,lastUseSkillID )
		else:
			self.changeAttackState( Const.ATTACK_STATE_HOMING_SPELL )

	def onRClickTargt( self ):
		"""
		�Ҽ��������Ŀ��
		"""
		lastUseSkillID = self.getLastUseAutoSkillID()
		if lastUseSkillID == Define.SKILL_ID_TRIGGER_SKILLS.get( self.getClass() ):
			self.changeAttackState( Const.ATTACK_STATE_HOMING_SPELL )
		else:
			self.changeAttackState( Const.ATTACK_STATE_AUTO_SPELL_HOMING )
