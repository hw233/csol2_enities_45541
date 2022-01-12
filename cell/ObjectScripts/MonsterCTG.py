# -*- coding: gb18030 -*-
#
# $Id: MonsterCTG.py,v 1.1 2007-06-26 00:36:27 kebiao Exp $

"""
����ع���
"""

import Monster
import Language
from bwdebug import *
import LostItemDistr
import items
import LostWorldItems
import random

#���������Ʒ
__DROPITEM__			= (
							( (1.0,("WZT_FS_08",1)), (1.0,("WZT_JS_08",1)), (1.0,("WZT_WS_08",1)), (1.0,("WZT_ZS_08",1)), (1.0,("WZT_SS_08",1)), (1.0,("WZT_JK_08",1)), ),
							( (1.0,("WZS_ZS_09",1)), (1.0,("WZS_WS_09",1)), (1.0,("WZS_SS_09",1)), (1.0,("WZS_JK_09",1)), (1.0,("WZS_FS_09",1)), (1.0,("WZS_JS_09",1)), ),
							( (1.0,("WZS_ZS_10",1)), (1.0,("WZS_WS_10",1)), (1.0,("WZS_SS_10",1)), (1.0,("WZS_JK_10",1)), (1.0,("WZS_FS_10",1)), (1.0,("WZS_JS_10",1)), ),
						  )

#���������
monsterSpwanPos = ( 46.462673, 21.294731, 44.926403 )
				  
class MonsterCTG(Monster.Monster):
	"""
	����ع���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		Monster.Monster.__init__( self )
		
	def getLostItems( self, selfInstance ):
		"""
		virtual method
		��ȡ��ͨ������Ʒ��
		@param selfInstance: ��ȫ�����ݶ�Ӧ�ļ̳���Monster��real Monster entityʵ��
		@type  selfInstance: Monster
		"""
		monsterLevel = selfInstance.level
		index = 0
		if monsterLevel >= 71 and monsterLevel <= 80:
			index = 1
		elif monsterLevel >= 81:
			index = 2
			
		return [  __DROPITEM__[ index ][ random.randint( 0, len( __DROPITEM__[ index ] ) - 1 ) ]  ]

	def generateBossProperty( self, selfInstance, level, passCount, selected ):
		"""
		����BOSS���������
		@param selfInstance: ��ȫ�����ݶ�Ӧ�ļ̳���Monster��real Monster entityʵ��
		@type  selfInstance: Monster
		@param level:��������ߵĵȼ�
		@type level:int32
		@param passCount:����ص� ����
		@param playerCount:���븱��������
		@param selected�����б���ѡ���ڼ���boss?
		"""
		L = level
		s = selected + 3
		monsterLevel = L + 4 + passCount / 3
		
		selfInstance.level 							= monsterLevel
		selfInstance._base_HP_Max 					= ((L-1)*70+100)*(int(int((L/10)+1)/4+s))
		selfInstance.exp							= 200 + monsterLevel * 50 #boss��200��boss�ȼ���50
		selfInstance._base_damage 					= (L*10+50)*2
		selfInstance._base_armor 					= (L*15+100)*int(int((L/10+1)/4+2))
		selfInstance._base_poison_damage 			= int(L/10)*3
		selfInstance._base_poison_resist 			= int(L/10)*3
		selfInstance._base_element_damage			= int(L/10)*3
		selfInstance._base_element_resist 			= int(L/10)*3
		selfInstance._base_spirit_damage 			= int(L/10)*3
		selfInstance._base_spirit_resist 			= int(L/10)*3
		selfInstance._base_hit 						= (L*8+150)*2
		selfInstance._base_dodge 					= (L*10+150)*2 
		selfInstance.spawnPos 						= monsterSpwanPos
		selfInstance.full()

	def generateMonsterProperty( self, selfInstance, level, passCount ):
		"""
		������ͨ���������
		@param selfInstance: ��ȫ�����ݶ�Ӧ�ļ̳���Monster��real Monster entityʵ��
		@type  selfInstance: Monster
		@param level:��������ߵĵȼ�
		@type level:int32
		@param passCount:����ص� ����
		@param playerCount:���븱��������
		"""
		L = level
		selfInstance.level 							= L + passCount / 4 + random.randint( 1, 3 )
		selfInstance._base_HP_Max 					= int(55*L+145+L*L*0.2)
		selfInstance.exp 							= 66 + selfInstance.level * 16 #С�֣�66��С�ֵȼ���16
		selfInstance._base_damage 					= L*10+50
		selfInstance._base_armor 					= L*15+100
		selfInstance._base_poison_damage 			= int(L/10)*2
		selfInstance._base_poison_resist 			= int(L/10)*2
		selfInstance._base_element_damage			= int(L/10)*2
		selfInstance._base_element_resist 			= int(L/10)*2
		selfInstance._base_spirit_damage 			= int(L/10)*2
		selfInstance._base_spirit_resist 			= int(L/10)*2
		selfInstance._base_hit 						= L*8+150
		selfInstance._base_dodge 					= L*10+150
		selfInstance.spawnPos 						= monsterSpwanPos
		selfInstance.full()
#
# $Log: not supported by cvs2svn $
#
#