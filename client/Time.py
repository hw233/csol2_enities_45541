# -*- coding: gb18030 -*-
#
# $Id: Time.py,v 1.1 2007-05-15 08:30:01 kebiao Exp $
"""
kebiao:���ڿͻ�����ȫ����ʹ�����Time�����汾��time�����и���ʱ���ϵļ��� Ч���ϲ�û��ʲô��� ���ô��Ǹ�������ʱ��ͬ���ġ�
	   ���û�н�ģ������Ĭ�ϵ�time()�ӿ���ȡ��Ϊ ServerTime ��ص���˼
"""
import time
import struct
import BigWorld

__OTHER_DELAY__ = 0.1 #�����ӳ� �������Ϳͻ������о�����callʱ�� �� һЩ socket�ӿڿ��ܲ�����һЩ�ȴ� һЩ�ӵ��ӳٱ�������

class Time:
    """
	    �������ͬ����timeģ��
	    ʹ��ʱֱ��:
	    from Time import *
	    Time.time()
    """
    recordServerTime = 0.0	# ��¼��ʼͨ��ʱ������ʱ����ͻ�������ʱ��Ĳ�ֵ

    @classmethod
    def init( self, serverTime ):
        """
        ������Ӧ���ڿͻ��������Ϸ���������ʹ��ǰ��ģ��ǰ��ʼ���ͻ��˵�ʱ��ƫ��ֵ���ܴﵽͬ��
        @param serverTime:��������������� time.time()��ȡ��ʱ��
        @type serverTime:string
        """
        self.recordServerTime = float( struct.unpack( "=d" , serverTime )[ 0 ] ) +  __OTHER_DELAY__ - BigWorld.time()

    @classmethod
    def time( self ):
        """
        #�����������99%һ�µ�time()ʱ��ֵ
        """
        return BigWorld.time() + self.recordServerTime

    @classmethod
    def localtime( self, giveTime = 0 ):
        """
        ���ط�������ǰʱ��
        return tuple
        """
        if giveTime == 0:
        	giveTime = self.time()
        return time.localtime( giveTime )

#
# $Log: not supported by cvs2svn $
#
#
#