# -*- coding: gb18030 -*-
#
# $Id: Time.py,v 1.1 2007-05-15 08:30:01 kebiao Exp $
"""
kebiao:由于客护短完全可以使用这个Time来代替本地time来进行各种时间上的计算 效率上并没有什么损耗 但好处是跟服务器时间同步的。
	   因此没有将模块名与默认的time()接口名取名为 ServerTime 相关的意思
"""
import time
import struct
import BigWorld

__OTHER_DELAY__ = 0.1 #其他延迟 服务器和客护短所有经过的call时间 和 一些 socket接口可能产生的一些等待 一些杂的延迟保守评估

class Time:
    """
	    与服务器同步的time模块
	    使用时直接:
	    from Time import *
	    Time.time()
    """
    recordServerTime = 0.0	# 记录初始通信时服务器时间与客户端运行时间的差值

    @classmethod
    def init( self, serverTime ):
        """
        服务器应该在客户端连接上服务器或者使用前此模块前初始化客户端的时间偏移值才能达到同步
        @param serverTime:服务器传输过来的 time.time()获取的时间
        @type serverTime:string
        """
        self.recordServerTime = float( struct.unpack( "=d" , serverTime )[ 0 ] ) +  __OTHER_DELAY__ - BigWorld.time()

    @classmethod
    def time( self ):
        """
        #返回与服务器99%一致的time()时间值
        """
        return BigWorld.time() + self.recordServerTime

    @classmethod
    def localtime( self, giveTime = 0 ):
        """
        返回服务器当前时间
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