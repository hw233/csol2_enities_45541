# -*- coding: gb18030 -*-
#

"""
���Ƴ������ܵ���ʾ by mushuang
���������������buff������ʾ��������
�����buff���������ȥ��ʱ�������س�������

��buff���Զ�������ҵ�ְҵ���������ж�Ӧ�ĳ�������
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
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._spaceSkillList = {} # { ְҵ1:[ skill1, skill2 ], ְҵ2:[ skill1, skill2 ], ... }
		self._available = True
		
	def __getProperSkillList( self, player ):
		"""
		�������ְҵ��ȡ��Ӧ��ְҵ�����б�
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
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		# Param1: �ռ似�ܣ��ַ�������
		# ��ʽ��ְҵ1:skill1,skill2..;ְҵ2:skill1,skill2..;ְҵ3:skill1,skill2..
		# ְҵ�ؼ������£�fighter(սʿ)��swordman�����ͣ���archer�����֣���mage����ʦ��
		Buff_Normal.init( self, dict )
		
		try:
			metierSkills = dict["Param1"].split( ";" ) # [ "ְҵ1:skill1,skill2..", "ְҵ2:skill1,skill2." ]
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
		Ч����ʼ�Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
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
		
		# ֪ͨ�ͻ�����ʾ����������
		receiver.client.initSpaceSkills( skillList, csdefine.SPACE_TYPE_BEFORE_NIRVANA )

	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�����¼��صĴ���

		@param receiver: Ч��ҪӰ���ʵ��
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
		
		# ֪ͨ�ͻ�����ʾ����������
		receiver.client.initSpaceSkills( skillList, csdefine.SPACE_TYPE_BEFORE_NIRVANA )
		

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		
		# ֪ͨ�ͻ������س�������
		receiver.client.onCloseCopySpaceInterface()

#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
#
#