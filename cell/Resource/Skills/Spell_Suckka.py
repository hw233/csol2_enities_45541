# -*- coding: gb18030 -*-
#
# $Id: Spell_Suckka.py,v 1.2 2008-05-30 03:05:19 yangkai Exp $

"""
吸魂技能基础
"""

from SpellBase import *
import random
import ItemTypeEnum

# 怪物每个等级所对应的魂魄总数
kaVal_Data = {
	1:40,2:40,3:41,4:41,5:41,6:41,7:42,8:42,9:42,10:43,11:44,12:45,13:45,14:45,15:46,16:46,17:46,18:47,19:47,20:47,21:49,22:49,23:50,24:50,25:50,26:51,27:51,28:52,29:52,30:52,31:53,32:55,33:55,34:55,35:56,36:56,37:57,38:57,39:57,40:58,41:59,42:60,43:61,44:61,45:62,46:62,47:62,48:63,49:63,50:64,51:65,52:67,53:67,54:68,55:68,56:68,57:69,58:69,59:70,60:70,61:71,62:72,63:73,64:74,65:75,66:76,67:76,68:77,69:77,70:78,71:79,72:80,73:81,74:82,75:83,76:83,77:84,78:84,79:85,80:86,81:87,82:88,83:89,84:90,85:91,86:92,87:92,88:93,89:94,90:94,91:95,92:96,93:97,94:98,95:99,96:100,97:102,98:102,99:103,100:104,101:104,102:105,103:106,104:107,105:107,106:108,107:109,108:110,109:110,110:111,111:112,112:113,113:114,114:116,115:117,116:117,117:118,118:119,119:120,120:121,121:122,122:123,123:124,124:125,125:126,126:127,127:128,128:129,129:130,130:131,131:132,132:133,133:134,134:135,135:136,136:137,137:138,138:139,139:140,140:141,141:142,142:143,143:144,144:145,145:146,146:147,147:148,148:149,149:150,150:151
}

class Spell_Suckka( Spell ):
	"""
	吸魂技能基础 用于魂魄石
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		self._doubleRate = 0 #吸魂暴击几率

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self._doubleRate = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 )  	#地图名称

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		
		if not caster:
			return
			
		itemInstance = receiver.getItem_( ItemTypeEnum.CWT_CIMELIA )
		if itemInstance is None:
			return

		suckCount = int( kaVal_Data[ caster.level ] / receiver.popTemp( "bootyOwnerCount", 1 ) )
		if random.randint( 0, 100 ) <= self._doubleRate:
			suckCount *= 2
		
		itemInstance.addKa( receiver, suckCount )
			
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/02/20 08:33:56  kebiao
# no message
#
#