# -*- coding: gb18030 -*-

import time
from bwdebug import *
import csdefine
from CrondScheme import *
from CEquip import CEquip

class CFashionDateLimit( CEquip ):
	"""
	ͨ�������������Ƶ�ʱװ
	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )
		# ����Ʒ��������ӻ����ʱ��
		# cmd��ʽΪ��ճ̱�cmd��ʽ : min hour day mon week
		# example : 0 * * * 7
		self._cmd = self.queryTemp( "param1", "" )

	def activaLifeTime( self, owner = None ):
		"""
		����һ����Ʒ��ʹ��ʱ��
		���������������߼�ʱ����ôowner����ΪNone
		��Ϊ����Ӧ��֪ͨaddLifeItemsToManage
		
		����ͨ����ճ��뵱ǰʱ���������һ��ʱ��
		"""
		t = time.time()
		year, month, day, hour, minute = time.localtime( t )[:5]
		scheme = Scheme()
		scheme.init( cmd )
		nextTime = scheme.calculateNext( year, month, day, hour, minute )
		interval = nextTime - t
		self.setLifeTime( interval, owner )
		CEquip.activaLifeTime( self, owner )