# -*- coding: utf-8 -*-
from encodings import gb18030
import time, sys, math, copy, random
import BigWorld, ResMgr
import Const, csdefine, SkillTargetObjImpl
from Monster import Monster
from Math import *
import random

USE_SKILL_ID = 0

AUTO_SKILL_ID = 111696001 		#������

class Role(BigWorld.Entity):
	BOT_STATE_FIGHT_STEP_FIND 	= 0x00						# Ѱ��
	BOT_STATE_FIGHT_STEP_MOVE	= 0x01						# �ƶ�
	BOT_STATE_FIGHT_STEP_FIGHT	= 0x02						# ս��


	def __init__( self ):
		# �Զ�ս�����
		self.autoFightState = Role.BOT_STATE_FIGHT_STEP_FIND
		self.autoFightTargetID = 0
		self.autoHitTime = 0
		self.skillList = []
		self.count = 0
		self.skillTestList = []
		self.currentSpace = ""
		# Ŀ��ID
		self.targetID = 0

		# ���Ǳ�clientApp��role
		if self.id != self.clientApp.id:
			return

		self.wizCommand("/set_attr level 100")
		self.wizCommand("/set_attr HP_Max 99000000")
		self.wizCommand("/set_attr HP 99000000")
		self.wizCommand("/set_attr MP_Max 99000000")
		self.wizCommand("/set_attr MP 99000000")

		#self.goFengMingCheng()
		self.clientApp.addTimer(1.0, self.goFengMingCheng, False)
		return

		r = random.random()
		if r > 0.9:
			self.flyToFengmingOutSide()
		elif r > 0.8:
			self.flyToFeilaishi()
		elif r > 0.7:
			self.flyToBanquanxiang()
		elif r > 0.6:
			self.flyToBishijian()
		elif r > 0.5:
			self.flyToYinkecun()
		elif r > 0.4:
			self.flyToYunMengze02()
		elif r > 0.3:
			self.flyToYunMengze01()
		elif r > 0.2:
			self.flyToPengLai()
		elif r > 0.1:
			self.flyToBeiMing()
		elif r > 0.0:
			self.flyToKunlun()


	# ----------------------------------------------------------------------------------------------------
	# called by engine
	# ----------------------------------------------------------------------------------------------------
	def prerequisites( self ):
		"""
		This method will be called before EnterWorld method
		# �˷�����enterWorld����֮ǰ����
		# ��������ʹ�õ�ģ��·����BigWorld������Զ��ں�̨����·����Դ
		# ����ռ�����̵߳���Դ���������ᵼ����ҽ���Ƚ϶��entity������
		# ����������
		"""
		return []

	def enterWorld( self ):
		"""
		This method is called when the entity enters the world
		Any of our properties may have changed underneath us,
		so we do most of the entity setup here
		"""
		pass

	def leaveWorld( self ):
		"""
		This method is called when the entity leaves the world
		"""
		pass

	###############################################################################
	# ������ר�� 																  #
	###############################################################################
	def getClass( self ):
		"""
		ȡ������ְҵ
		@return: INT
		"""
		return self.raceclass & csdefine.RCMASK_CLASS

	def autoMove(self, state):
		"""
		��ʼ�Զ��ƶ�
		"""
		BigWorld.bots[self.id].autoMove = state

	def sendMessage(self, channel, msg, target=""):
		"""
		�����˷�����Ϣ
		channel 		Ƶ��
		msg				��Ϣ
		"""
		self.base.chat_sendMessage(channel, target,  msg, "")

	def useDefaultBuff(self):
		"""
		�ͷ�Ĭ��BUFF
		"""
		cl = self.getClass()
		skill = 0
		if cl == csdefine.CLASS_FIGHTER:
			skill = 322206001							# ��׳
		elif cl == csdefine.CLASS_SWORDMAN:
			skill = 322208001							# ׿Խ
		elif cl == csdefine.CLASS_ARCHER:
			skill = 322211001							# ����
		elif cl == csdefine.CLASS_MAGE:
			skill = 322221001							# �ϻ�
		self.cell.useSpell( skill, SkillTargetObjImpl.createTargetObjEntity(self) )

	def entitiesInRange(self, Type):
		"""
		Ѱ��
		"""
		entities = []
		for i in BigWorld.bots[self.id].entities.values():
			if i.__class__ == Type and (not i.hasFlag(csdefine.ENTITY_FLAG_SPEAKER)):
				entities.append(i)
		return entities

	def entityNearest(self, Type):
		"""
		Ѱ������Ĺ�
		"""
		p = BigWorld.bots[self.id]
		monsters = self.entitiesInRange(Type)
		monster = None
		dis = 99999
		for m in monsters:
			d = m.position.distTo(p.position)
			if d < dis:
				monster = m
				dis = d
		return monster

	def entityRandom(self, Type):
		"""
		Ѱ������Ĺ�
		"""
		p = BigWorld.bots[self.id]
		monster = None
		monsters = self.entitiesInRange(Type)
		if len(monsters) >= 1:
			monster = random.choice(monsters)
		return monster

	def get_entity_by_id(self, nID):
		"""
		��ȡentity
		"""
		if BigWorld.bots[self.id].entities.has_key(nID):
			monster = BigWorld.bots[self.id].entities[nID]
			return monster
		return None

	def is_enemy(self, target):
		"""�Ƿ��ǵ���"""
		return not self.entity_has_flag(target, csdefine.ENTITY_FLAG_SPEAKER)

	def can_fight_to(self, target):
		"""�Ƿ��ǿ�ս��Ŀ��"""
		if not self.is_enemy(target):
			return False
		else:
			state = getattr(target, "state", csdefine.ENTITY_STATE_DEAD)
			return state != csdefine.ENTITY_STATE_DEAD

	def entity_dead(self, entity):
		"""�Ƿ�����"""
		state = getattr(entity, "state", None)
		return state == csdefine.ENTITY_STATE_DEAD

	def entity_has_flag(self, entity, flag):
		flags = getattr(entity, "flags", None)
		return flags is not None and ((1 << flag) & flags) == (1 << flag)

	def entities_in_sight(self, filter = lambda e: True):
		"""������Ұ��Χ�ڵ�entity������ͨ��filter���˵Ĳ���"""
		result = []
		for entity in BigWorld.bots[self.id].entities.values():
			if filter(entity):
				result.append(entity)
		return result

	def entities_by_class_names(self, class_names):
		"""����entity��className����"""
		filter = lambda e: getattr(e, "className", None) in class_names
		return self.entities_in_sight(filter)

	def entities_by_class_type(self, type_name):
		"""����entity����������"""
		filter = lambda e: e.__class__.__name__ == type_name
		return self.entities_in_sight(filter)

	def entities_fightable(self):
		"""������ս����λ"""
		return self.entities_in_sight(self.can_fight_to)

	def entities_fightable_by_class_names(self, class_names):
		"""����className������ս����λ"""
		filter = lambda e: getattr(e, "className", None) in class_names and\
			self.can_fight_to(e)
		return self.entities_in_sight(filter)

	def entities_nearest_by_class_names(self, class_names):
		"""����className���������һ��"""
		filter = lambda e: getattr(e, "className", None) in class_names
		entities = self.entities_in_sight(filter)
		if len(entities) == 0:
			return None
		else:
			entities.sort(key = lambda e: self.position.distTo(e.position))
			return entities[0]

	def enemy_nearest(self):
		"""���������һ������"""
		enemies = self.entities_fightable()
		if len(enemies) == 0:
			return None
		else:
			enemies.sort(key = lambda e: self.position.distTo(e.position))
			return enemies[0]

	def enemy_nearest_by_class_names(self, class_names):
		"""����className��������Ŀ�ս����λ"""
		enemies = self.entities_fightable_by_class_names(class_names)
		if len(enemies) == 0:
			return None
		else:
			enemies.sort(key = lambda e: self.position.distTo(e.position))
			return enemies[0]

	def bind_target(self, target):
		"""��Ϊ��ǰĿ��"""
		self.targetID = target.id

	def get_target(self):
		"""��ȡ��ǰĿ��"""
		return self.get_entity_by_id(self.targetID)

	def spell_target(self, target_id, skill_id):
		"""��Ŀ��ʩ�ż���"""
		target = self.get_entity_by_id(self.targetID)
		if target is None:
			print "Can't find target by id", target_id
		else:
			wrapped_target = SkillTargetObjImpl.createTargetObjEntity(target)
			self.cell.useSpell(skill_id, wrapped_target)
			print "skill %s has been used on target %s" % (skill_id, target_id)

	def fightTo(self, entity, target, spell = USE_SKILL_ID):
		"""
		�Զ�ս��ѭ��
		"""
		p = BigWorld.bots[self.id]
		if self.position.distTo(entity.position) >= 1.0:
			# �ƶ�
			self.flyTo(entity.position)

		spell=getattr( self, "useSkillID", spell )
		if spell == 0 and len(self.skillTestList) > 0:
			index = self.count%len(self.skillTestList)
			spell = self.skillTestList[index]
			self.count += 1
			self.cell.useSpell(spell, target)
		else:
			self.autoUseSkill()

	def autoFightLoop(self):
		p = BigWorld.bots[self.id]
		if self.autoFightState == Role.BOT_STATE_FIGHT_STEP_FIND:
			self.autoHitTime = 0
			monster = self.entityRandom(Monster)
			if monster:
				# �ҵ�������¼���ƶ�
				self.autoFightTargetID = monster.id
				self.flyTo(monster.position)
				self.autoFightState = Role.BOT_STATE_FIGHT_STEP_MOVE
		elif self.autoFightState == Role.BOT_STATE_FIGHT_STEP_MOVE:
			# �ƶ�
			autoFightTarget = self.get_entity_by_id(self.autoFightTargetID)
			if autoFightTarget is None or self.autoHitTime >= 60:
				# Ѱ�Ҳ���������ƶ�ʱ�䳬��60�룬ת��Ѱ��״̬
				self.autoFightState = Role.BOT_STATE_FIGHT_STEP_FIND
				return
			if autoFightTarget.position.distTo(p.position) <= 4.0:
				self.autoFightState = Role.BOT_STATE_FIGHT_STEP_FIGHT
			else:
				self.flyTo(autoFightTarget.position)
			self.autoHitTime += 1

		elif self.autoFightState == Role.BOT_STATE_FIGHT_STEP_FIGHT:
			# ս��
			autoFightTarget = self.get_entity_by_id(self.autoFightTargetID)
			if autoFightTarget is None or autoFightTarget.HP <= 0 or self.autoHitTime >= 600:
				# Ѱ�Ҳ������������������ƶ�ʱ�䳬��60�룬ת��Ѱ��״̬
				self.autoFightState = Role.BOT_STATE_FIGHT_STEP_FIND
				return
			target = SkillTargetObjImpl.createTargetObjEntity(autoFightTarget)
			self.fightTo(autoFightTarget, target)
			self.autoHitTime += 1

		else:
			# �����ϲ����ܳ��ֵ����
			self.autoFightState == Role.BOT_STATE_FIGHT_STEP_FIND

	def moveTo(self, posx, posy, posz, posp):
		"""
		�ƶ���ĳ��
		"""
		x = posx + random.randint(-posp, +posp)
		z = posz + random.randint(-posp, +posp)
		BigWorld.bots[self.id].moveTo((x, posy, z))

	def moveToPos(self, position):
		"""
		�ƶ���ĳ��
		"""
		print "%s move to position %s" % (self.playerName, position)
		self.wizCommand("/moveto %f %f %f" % (position[0], position[1], position[2]))
		#BigWorld.bots[self.id].moveTo(position)

	def flyTo( self, position ):
		"""
		�ɵ���ǰ��ͼĳ����
		"""
		x, y, z = position
		spaceLabel = getattr( self, "currentSpace", "" )
		if self.currentSpace != "":
			print "fly to target!(%s,%f,%f,%f)"%(spaceLabel, x, y, z )
			self.wizCommand("/goto %s %f %f %f"%(spaceLabel, x, y, z ))
		else:
			print "I am not in a space currently."

	def flySpace(self, spaceLabel, position):
		"""
		�ɵ�ָ����ͼĳ����
		"""
		x, y, z = position
		name = getattr(self, "playerName", "Bot unkown name")
		print "%s fly to space %s at (%f, %f, %f)" % (name, spaceLabel, x, y, z)
		self.wizCommand("/goto %s %f %f %f"%(spaceLabel, x, y, z))
		self.currentSpace = spaceLabel

	def wizCommand(self, strCmd):
		"""
		GMָ��
		"""
		if strCmd[0] == "/":
			lstStrCmd = strCmd.split(None, 1)
			if 2 == len(lstStrCmd):
				key, param = lstStrCmd
				key = key[1:]
			else:
				param = ""
				key = lstStrCmd[0]
				key = key[1:]
			self.cell.wizCommand(self.id, key, param)

	def goFengMingCheng(self):
		"""
		GMָ�������
		"""
		self.flySpace("fengming", (75, 15, 16))
		#self.wizCommand("/goto fengming 75 15 16")

	def goFengMing(self):
		"""
		GMָ�����
		"""
		self.flySpace("fengming", (75, 8, -384))
		#self.wizCommand("/goto fengming  75 8 -384")

	def useItemRevive(self):
		"""
		ʹ�ø���ҩ
		"""
		self.cell.useItemRevive()

	def withdrawEidolon(self):
		"""
		�ջ�С����
		"""
		self.cell.withdrawEidolon()

	def autoUseSkill(self):
		"""
		�ͷ�ս������
		"""
		if not AUTO_SKILL_ID in self.skillList:
			self.wizCommand("/add_skill %i"%AUTO_SKILL_ID)
			self.skillList.append( AUTO_SKILL_ID )
		self.cell.useSpell(AUTO_SKILL_ID, SkillTargetObjImpl.createTargetObjEntity(self))

	def flyToFengmingOutSide( self ):
		"""
		���е�����Ұ��
		"""
		self.flySpace("fengming", ((random.randint(-351, 863), 30, random.randint(-958, 235))))
		#self.wizCommand("/goto fengming %i 30 %i"%(random.randint(-351, 863), random.randint(-958, 235) ))
		#self.currentSpace = "fengming"

	def flyToFeilaishi( self ):
		"""
		���е�����ʯ
		"""
		self.flySpace("xin_fei_lai_shi_001", ((random.randint(-660, 275), 30, random.randint(-552, 605) )))
		#self.wizCommand("/goto xin_fei_lai_shi_001 %i 30 %i"%(random.randint(-660, 275), random.randint(-552, 605) ))
		#self.currentSpace = "xin_fei_lai_shi_001"


	def flyToBanquanxiang( self ):
		"""
		���е���Ȫ��
		"""
		self.flySpace("zly_ban_quan_xiang", ((random.randint(-160, 927), 30, random.randint(-532, 885) )))
		#self.wizCommand("/goto zly_ban_quan_xiang %i 30 %i"%(random.randint(-160, 927), random.randint(-532, 885) ))
		#self.currentSpace = "zly_ban_quan_xiang"

	def flyToBishijian( self ):
		"""
		���е�������
		"""
		self.flySpace("zly_bi_shi_jian", ((random.randint(-911, 281), 30, random.randint(-922, -127) )))
		#self.wizCommand("/goto zly_bi_shi_jian %i 30 %i"%(random.randint(-911, 281), random.randint(-922, -127) ))
		#self.currentSpace = "zly_bi_shi_jian"

	def flyToYinkecun( self ):
		"""
		���е�ӭ�ʹ�
		"""
		self.flySpace("zly_ying_ke_cun", ((random.randint(-900, 190), 30, random.randint(-240, 925) )))
		#self.wizCommand("/goto zly_ying_ke_cun %i 30 %i"%(random.randint(-900, 190), random.randint(-240, 925) ))
		#self.currentSpace = "zly_ying_ke_cun"

	def flyToYunMengze02( self ):
		"""
		���е�������02
		"""
		self.flySpace("yun_meng_ze_02", ((random.randint(-31, 900), 30, random.randint(-366, 940) )))
		#self.wizCommand("/goto yun_meng_ze_02 %i 30 %i"%(random.randint(-31, 900), random.randint(-366, 940) ))
		#self.currentSpace = "yun_meng_ze_02"

	def flyToYunMengze01( self ):
		"""
		���е�������01
		"""
		self.flySpace("yun_meng_ze_01", ((random.randint(-930, 230), 30, random.randint(-550, 939) )))
		#self.wizCommand("/goto yun_meng_ze_01 %i 30 %i"%(random.randint(-930, 230), random.randint(-550, 939) ))
		#self.currentSpace = "yun_meng_ze_01"

	def flyToPengLai( self ):
		"""
		����
		"""
		self.flySpace("peng_lai", ((random.randint(-770, 730), 30, random.randint(-700, 838) )))
		#self.wizCommand("/goto peng_lai %i 100 %i"%(random.randint(-770, 730), random.randint(-700, 838) ))
		#self.currentSpace = "peng_lai"

	def flyToBeiMing( self ):
		"""
		��ڤ
		"""
		self.flySpace("bei_ming", ((random.randint(-2000, 2000), 30, random.randint(-2000, 2000) )))
		#self.wizCommand("/goto bei_ming %i 30 %i"%(random.randint(-2000, 2000), random.randint(-2000, 2000) ))
		#self.currentSpace = "bei_ming"

	def flyToKunlun( self ):
		"""
		����
		"""
		self.flySpace("kun_lun", ((random.randint(-595, 700), 30, random.randint(-580, 623) )))
		#self.wizCommand("/goto kun_lun %i 30 %i"%(random.randint(-595, 700), random.randint(-580, 623) ))

	def ChangeEquip( self, inf ):
		if self.getClass() == 48: #������
			self.wizCommand( "/set_lefthand 5130100 %d 0 "%inf )
			self.wizCommand( "/set_righthand 0 0 0 " )
			self.wizCommand( "/set_body 2040090 %d "%inf )
			self.wizCommand( "/set_vola 2050090 %d "%inf )
			self.wizCommand( "/set_breech 2060090 %d "%inf)
			self.wizCommand( "/set_feet 2070090 %d "%inf )
		elif self.getClass() == 16: #սʿ
			self.wizCommand( "/set_righthand 5210090 %d 0 "%inf )
			self.wizCommand( "/set_lefthand 0 0 0 " )
			self.wizCommand( "/set_body 3040090 %d "%inf )
			self.wizCommand( "/set_vola 3050090 %d "%inf )
			self.wizCommand( "/set_breech 3060090 %d "%inf)
			self.wizCommand( "/set_feet 3070090 %d "%inf )
		elif self.getClass() == 32: #����
			self.wizCommand( "/set_righthand 5271000 %d 0 "%inf )
			self.wizCommand( "/set_lefthand 5271000 %d 0 "%inf )
			self.wizCommand( "/set_body 1040090 %d "%inf )
			self.wizCommand( "/set_vola 1050090 %d "%inf )
			self.wizCommand( "/set_breech 1060090 %d "%inf)
			self.wizCommand( "/set_feet 1070090 %d "%inf )
		elif self.getClass() == 64: #��ʦ
			self.wizCommand( "/set_righthand 5120255 %d 0 "%inf )
			self.wizCommand( "/set_lefthand 0 0 " )
			self.wizCommand( "/set_body 4040090 %d "%inf )
			self.wizCommand( "/set_vola 4050090 %d "%inf )
			self.wizCommand( "/set_breech 4060090 %d "%inf)
			self.wizCommand( "/set_feet 4070090 %d "%inf )

	def setNormalAttr(self):
		self.wizCommand("/set_attr level 100")
		self.wizCommand("/set_attr HP_Max 99000000")
		self.wizCommand("/set_attr HP 99000000")
		self.wizCommand("/set_attr MP_Max 99000000")
		self.wizCommand("/set_attr MP 99000000")

	def setFullAttr( self )	:
		self.wizCommand("/set_attr_full")


	def addSkillForTestParticle( self ):
		skillL = []
		skill = 0
		skillInfo = []
		if self.getClass() == 48: #������
			skillInfo = [[322462001,312104001,322116001,311155001,311141001,323224001,311120001,311123001],
				[322463001,312104001,311156001,311141001,323231001,311120001,311123001]]
		elif self.getClass() == 16: #սʿ
			skillInfo = [[322458001,311129001,311152001,311107001,323200001,311101001,311104001],
				 [322459001,311129001,321203001,311151001,323208001,311101001,311104001]]
		elif self.getClass() == 32: #����
			skillInfo = [[322460001,322437001,311153001,322419001,323220001,311114001,312101001],
				[322461001,312101001,311154001,323214001,323220001,311114001,322473001]]
		elif self.getClass() == 64: #��ʦ
			skillInfo = [[322464001,312110001,312642001,323195001,322720001,323189001,312112001,322522001],
				[322465001,312643001,322448001,323189001,322522001,312642001]]

		skillL = random.choice(skillInfo)
		for i in skillL:
			self.wizCommand( "/add_skill %d"%i )
		skill = skillL[0]
		self.skillTestList = skillL[1:]
		#ʹ��Ĭ���ķ�
		self.cell.useSpell( skill, SkillTargetObjImpl.createTargetObjEntity(self) )

	def onEnterSpace( self ):
		"""
		"""
		print "----->>> bot %s enter space" % self.id

	def onLeaveSpace( self ):
		"""
		"""
		print "----->>> bot %s leave space" % self.id


############################
# End of class Role        #
############################