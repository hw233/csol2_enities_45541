# -*- coding: gb18030 -*-
#

"""
控制场景技能的显示 by mushuang
如果玩家身上有这个buff，则显示场景技能
当这个buff从玩家身上去掉时，则隐藏场景技能

此buff会自动根据玩家的职业加载配置中对应的场景技能
"""

import BigWorld
import csconst
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

FIGHTER = "fighter"
ARCHER = "archer"
MAGE = "mage"
SWORDMAN = "swordman"

class Buff_22019( Buff_Normal ):
	"""
	example:
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._spaceSkillList = {} # { 职业1:[ skill1, skill2 ], 职业2:[ skill1, skill2 ], ... }
		self._available = True
		
	def __getProperSkillList( self, player ):
		"""
		根据玩家职业获取对应的职业技能列表
		"""
		metier = player.getClass()
		skillList = None
		
		if metier == csdefine.CLASS_FIGHTER:
			skillList = self._spaceSkillList.get( FIGHTER, [] )
		elif metier == csdefine.CLASS_SWORDMAN :
			skillList = self._spaceSkillList.get( SWORDMAN, [] )
		elif metier == csdefine.CLASS_ARCHER:
			skillList = self._spaceSkillList.get( ARCHER, [] )
		elif metier == csdefine.CLASS_MAGE:
			skillList = self._spaceSkillList.get( MAGE, [] )
		else:
			skillList = []
		
		return skillList
	
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		# Param1: 空间技能（字符串），
		# 格式：职业1:skill1,skill2..;职业2:skill1,skill2..;职业3:skill1,skill2..
		# 职业关键字如下：fighter(战士)，swordman（剑客），archer（射手），mage（法师）
		Buff_Normal.init( self, dict )
		
		try:
			metierSkills = dict["Param1"].split( ";" ) # [ "职业1:skill1,skill2..", "职业2:skill1,skill2." ]
			for tmp in metierSkills:
				metierName,skillListStr = tmp.split( ":" )
				skillList = skillListStr.split( "," )
				for skill in skillList:
					if skill == "": continue
					skillID = int( skill )
					
					if not self._spaceSkillList.has_key( metierName ):
						self._spaceSkillList[ metierName ] = []
					
					self._spaceSkillList[ metierName ].append( skillID )
		except:
			ERROR_MSG( "Parse failed, please check Param1's format!" )
			self._available = False

	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		
		if not self._available:
			ERROR_MSG( "Incorrect initialization, buff function disabled!" )
			return
		
		skillList = self.__getProperSkillList( receiver )
		
		if len( skillList ) == 0:
			ERROR_MSG( "No skill config found, please check integrity of corresponding config!" )
			return
		
		# 通知客户端显示场景技能栏
		receiver.client.initSpaceSkills( skillList, csdefine.SPACE_TYPE_BEFORE_NIRVANA )

	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果重新加载的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		
		if not self._available:
			ERROR_MSG( "Incorrect initialization, buff function disabled!" )
			return
		
		skillList = self.__getProperSkillList( receiver )
		
		if len( skillList ) == 0:
			ERROR_MSG( "No skill config found, please check integrity of corresponding config!" )
			return
		
		# 通知客户端显示场景技能栏
		receiver.client.initSpaceSkills( skillList, csdefine.SPACE_TYPE_BEFORE_NIRVANA )
		

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		
		# 通知客户端隐藏场景技能
		receiver.client.onCloseCopySpaceInterface()

#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
#
#