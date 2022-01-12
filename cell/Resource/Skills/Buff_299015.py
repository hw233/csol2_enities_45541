# -*- coding: gb18030 -*-

"""
׷��
"""

import csconst
from Buff_Normal import Buff_Normal

class Buff_299015( Buff_Normal ):
	"""
	׷��buff
	"""
	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		����buff����ʾbuff��ÿһ������ʱӦ����ʲô��

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL�������������򷵻�True�����򷵻�False
		@rtype:  BOOL
		"""
		if receiver.spaceType == "fu_ben_jian_yu":
			return False
			
		spaceScript = receiver.getCurrentSpaceScript()
		
		# �ж��Ƿ��ץ���ﷸ�ĵ�ͼ �������ͷ�׷��buff
		if spaceScript.canArrest:
			receiver.setTemp( "gotoPrison", True )
			receiver.gotoSpace( "fu_ben_jian_yu", (0,0,0), (0,0,0) )
			return False
			
		return Buff_Normal.doLoop( self, receiver, buffData )
			