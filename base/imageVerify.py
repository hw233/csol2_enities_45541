# -*- coding: gb18030 -*-

"""
picture verify base
"""

# $Id: imageVerify.py,v 1.10 2008-01-25 10:05:01 yangkai Exp $

#import gd	# ��ʱ����
import os
import Language
import random
import cStringIO
from bwdebug import *

_g_confPath = "config/server/imageVerify/config.xml"
# ע��������ʹ��bw_web_console���������ʱ���������⣬���ڴ˹��ܵ�ǰ��ʱ���ã������ʱȡ����
#_g_resPaths = os.getenv( "BW_RES_PATH" ).split( ":" )
_g_resPaths = []
_g_bgPath = ""
_g_fgPath = ""

_g_bgs = []
_g_quests = []
_g_img = None			# ��ʱͼƬ
_g_imgSize = (0,0)		# ͼƬ��С

ANSWER_TIME = 300		# ���������ʱ���ڻش𣬵�λ����, ����ΪactiveDelay�ı���
QUEST_TIME = 0			# ÿ���೤ʱ������һ�Σ�����ΪactiveDelay�ı���
FAIL_COUNT = 3			# �������ٴδ������
LOGIN_LOCK_TIME = 300	# ���ߺ��ɫ������ʱ��
FIRST_QUEST_TIME = 60	# ����ҵ�¼���һ����ʾʱ��
ACTIVE_DELAY = 60		# timerÿ�λ���, С��1ʱ��ʾ��ѯ��

def _findAbspath( filePath ):
	global _g_resPaths
	for e in _g_resPaths:
		if e[-1] != "/":
			res = e + "/"
		else:
			res = e
		if os.path.isfile( res + filePath ):
			return res + filePath
	return None

def _loadConfig( confFile ):
	"""
	"""
	section = Language.openConfigSection( confFile )
	if section is None:
		ERROR_MSG( "open config fail.", confFile )
		return
	config = {}

	global _g_bgPath
	global _g_fgPath
	global _g_img
	global ANSWER_TIME
	global QUEST_TIME
	global FAIL_COUNT
	global LOGIN_LOCK_TIME
	global FIRST_QUEST_TIME
	global ACTIVE_DELAY
	global _g_imgSize

	_g_imgSize = section.readVector2( "imageSize" )
	_g_imgSize = (int(_g_imgSize[0]), int(_g_imgSize[1]))	# convert float to int
	# 2009-4-17 19:38 yk ע��
	#_g_img = gd.image( _g_imgSize )

	_g_bgPath = section.readString( "bgPath" )
	if _g_bgPath[-1] not in "\\/":
		_g_bgPath += "/"

	_g_fgPath = section.readString( "fgPath" )
	if _g_fgPath[-1] not in "\\/":
		_g_fgPath += "/"

	if len(_g_bgPath) == 0 or len(_g_fgPath) == 0:
		QUEST_TIME = 0
	else:
		QUEST_TIME = section.readInt( "questTime" )

	ANSWER_TIME = section.readInt( "answerTime" )

	if section.has_key( "failCount" ):
		FAIL_COUNT = section.readInt( "failCount" )
	else:
		FAIL_COUNT = 2

	if section.has_key( "loginLockTime" ):
		LOGIN_LOCK_TIME = section.readInt( "loginLockTime" )
	else:
		LOGIN_LOCK_TIME = 300

	config["firstQuestTime"] = section.readInt( "firstQuestTime" )
	if section.has_key( "firstQuestTime" ):
		FIRST_QUEST_TIME = section.readInt( "firstQuestTime" )
	else:
		FIRST_QUEST_TIME = 60

	if section.has_key( "activeDelay" ):
		ACTIVE_DELAY = section.readInt( "activeDelay" )
		if ACTIVE_DELAY < 1: ACTIVE_DELAY = 0
	else:
		ACTIVE_DELAY = 0

	# �ر������ļ�
	Language.purgeConfig( confFile )
	# the end


def initRes():
	"""
	"""
	global _g_confPath
	_loadConfig( _g_confPath )

	global _g_bgPath
	global _g_fgPath
	global _g_bgs
	global _g_quests

	# clear old value
	_g_bgs = []
	_g_quests = []

	# load background picture
	try:
		files = os.listdir( _g_bgPath )
	except WindowsError, errstr:
		ERROR_MSG( WindowsError, errstr )
		files = []

	count = 0
	err = 0
	for f in files:
		fn = _findAbspath( _g_bgPath + f )
		if fn is None: continue
		if fn.lower().endswith( ".gif" ) or fn.lower().endswith( ".png" ):
			# 2009-4-17 19:37 yk ע��
			"""
			try:
				img = gd.image( fn )
			except Exception, errstr:
				err += 1
				ERROR_MSG( "load file '%s' fail; %s" % (fn, errstr) )
				continue
			"""
			count += 1
			_g_bgs.append( img )
	INFO_MSG( "load background image finish. %i success, %i fail." % (count, err) )


	# load quest picture
	try:
		files = os.listdir( _g_fgPath )
	except WindowsError, errstr:
		ERROR_MSG( WindowsError, errstr )
		files = []

	count = 0
	err = 0
	for f in files:
		fn = _findAbspath( _g_fgPath + f )
		if fn is None: continue
		if fn.lower().endswith( ".gif" ) or fn.lower().endswith( ".png" ):
			newf = f[:f.find( "." )]
			try:
				name, solution = newf.split( "_" )
			except ValueError:
				ERROR_MSG( "file format is like as xxx-nn-xx.gif;", fn )
				continue
			# 2009-4-17 19:37 yk ע��
			"""
			try:
				img = gd.image( fn )
			except Exception, errstr:
				err += 1
				ERROR_MSG( "load file '%s' fail; %s" % (fn, errstr) )
				continue
			"""
			count += 1
			colorIndex = img.colorClosest( (255,255,255) )
			img.colorTransparent( colorIndex )
			# solution(��ȷ��), image(ͼƬ)
			_g_quests.append( ( ord(solution.lower()[0]) - 97, img ) )	# ord(solution.lower()) - ord("a"), chr(97) == "a"
	INFO_MSG( "load foreground image finish. %i success, %i fail." % (count, err) )
	# the end

def createRandomVerify():
	"""
	@return: (opts, solution, imgString)
	"""
	bgimg = _g_bgs[ random.randint( 0, len(_g_bgs) - 1 ) ]
	solution, fgimg = _g_quests[ random.randint( 0, len(_g_quests) - 1 ) ]

	bgimg.copyTo( _g_img )
	#fgimg.copyMergeTo( _g_img, (0,0), (0,0), _g_imgSize, 50 )
	fgimg.copyTo( _g_img )

	# random get one color index from palette
	colorIndex = random.randint( 0, _g_img.colorsTotal() - 1 )

	# draw line
	for e in xrange( 3 ):
		x1 = random.randint( 0, _g_imgSize[0] )
		y1 = random.randint( 0, _g_imgSize[1] )
		x2 = random.randint( 0, _g_imgSize[0] )
		y2 = random.randint( 0, _g_imgSize[1] )
		_g_img.line((x1,y1), (x2,y2), colorIndex)

	# write to string
	imgstr = cStringIO.StringIO()
	_g_img.writeJpeg( imgstr )
	#_g_img.writeGif( imgstr )
	return (solution, imgstr.getvalue())

def createRandomVerify2file( fileName ):
	f = open( fileName, "wb" )
	s = createRandomVerify()
	f.write( s[1] )
	f.close()


# -----------------------------------------------------------------------------------------
# init now
#initRes()	# ��ʱ����


# imageVerify.py
