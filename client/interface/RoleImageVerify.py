# -*- coding: gb18030 -*-
#
# $Id: RoleImageVerify.py,v 1.9 2007-06-14 10:32:35 huangyongwei Exp $

"""
"""

import BigWorld
from bwdebug import *
import os

TEMP_FILE = "temp/%s.dds"

class RoleImageVerify:
	"""
	"""
	def __init__( self ):
		self.ivfImage = []	# image packet array as string
		self.ivfImageFilePrefix = 0
		pass

	"""
	def onImageVerify( self, image ):
		@param image: 图片数据
		@type  image: BLOB
		@return: 无
		print "opts =", opts
		pass
	"""

	def onImageVerify( self, maxPacket, currPacket, image ):
		"""
		@param  maxPacket: 最多有几个包
		@type   maxPacket: UINT8
		@param currPacket: 当前是第几个包
		@type  currPacket: UINT8
		@param      image: 图片数据
		@type       image: BLOB
		@return: 无
		"""
		print "maxPacket = %i, currPacket = %i" % (maxPacket, currPacket)
		if currPacket == 1:
			self.ivfImage = [e for e in xrange( maxPacket )]
		self.ivfImage[currPacket-1] = image
		if maxPacket == currPacket:
			self.ivfImage = "".join( self.ivfImage )
			self.ivfShowQuest( self.ivfImage )

	def onivfAnswer( self, index ):
		"""
		@param index: 选择的选项索引,从0开始.
		"""
		self.base.onReplyImageVerify( index )

	def ivfShowQuest( self, imageData ):
		imgFile = TEMP_FILE % int(self.ivfImageFilePrefix)
		self.ivfImageFilePrefix += 1
		try:
			f = open( imgFile, "wb" )
		except IOError:
			ERROR_MSG( "Can't open file from directory 'temp'" )
			return
		f.write( imageData )
		f.close()
		#print "image receive finish."
		#GMgr.antiCheatWindow.show( self.onivfAnswer, imgFile )
		#self.removeImage( imgFile )

	def removeImage( self, filePath ):
		try:
			f = open( filePath )
		except IOError:
			return
		f.close()
		os.remove( filePath )

#
# $Log: not supported by cvs2svn $
# Revision 1.8  2006/09/27 04:44:00  huangyongwei
# 去掉了对旧界面的引用：from hui.GUIsManager import GUIsManager as GMgr
#
# Revision 1.7  2006/05/18 08:19:43  huangyongwei
# no message
#
# Revision 1.6  2006/05/18 03:28:26  huangyongwei
# no message
#
# Revision 1.5  2005/11/25 08:03:45  phw
# no message
#
# Revision 1.4  2005/11/25 04:42:02  phw
# no message
#
# Revision 1.3  2005/11/25 03:00:27  phw
# 请在res/里创建一个temp目录用于放置临时图片
#
# Revision 1.2  2005/11/24 08:59:04  phw
# no message
#
# Revision 1.1  2005/11/23 09:32:11  phw
# no message
#
#
