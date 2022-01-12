# -*- coding: gb18030 -*-
#
# $Id: Sound.py,v 1.27 2008-08-26 08:01:10 yangkai Exp $

"""
implement sound manager class

2006/06/08: writen by panguankong
"""

import BigWorld
import Language
from bwdebug import *
from gbref import rds
from event.EventCenter import *
from Function import Functor
import Const

test = False
class Sound :
	__inst = None

	gb_audioSect = { "switchvocality" : 1,
					 "vocalityvolume" : 1.0,
					 "switcheffect"   : 1,
					 "effectvolume"   : 1.0,
					 "switchbgeffect" : 1,
					 "bgeffectvolume" : 1.0,
					 "mastervolume"   : 1.0
					}

	def __init__( self ):
		assert Sound.__inst is None		# 禁止产生多次实例
		self.__pyBgSound = None
		self.__pyVoice = None
		self.__pyBgEffect = None
		self.__pyFightSound = None
		self.isBgplay = False
		self.bgVol = 0.0
		self.isEffplay = False
		self.effVol = 0.0
		self.isBgEffPlay = False
		self.bgEffVol = 0.0
		self.masterVol = 0.0
		self.isPlayFightSound = False
		self.__bgLocked = False			# 背景音乐上锁
		self.__bgEffLocked = False		# 背景音效上锁
		self.__gossipSound = None		# 当前播放的对话音效
		self.__delayStopcbid = 0
		self.__delayPlaycbid = 0
		self.__delayStopBgEffcdid = 0
		self.__delayPlayBgEffcbid = 0
		self.__delayStopFightcdid = 0
		self.__delayPlayFightcdid = 0

	@classmethod
	def instance( SELF ) :
		if SELF.__inst is None :
			SELF.__inst = Sound()
		return SELF.__inst


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def lockBgPlay( self, locked ) :
		"""
		上锁/解锁背景音乐播放
		一旦上锁，背景音乐将不能再进行任何操作，包括停止，切换等
		"""
		self.__bgLocked = locked

	def lockBgEffectPlay( self, locked ):
		"""
		上锁/解锁背景音效播放
		一旦上锁，背景音效将不能再进行任何操作，包括停止，切换等
		"""
		self.__bgEffLocked = locked

	# -------------------------------------------------
	def playVocality( self, name, pyModel ):
		"""
		播放3D声音
		@param name:			文件名
		@type name:			string
		@param pyModel:		播放声音的模型
		@type pyModel:			pyModel
		"""
		if pyModel is None: return
		sound = pyModel.getSound( name )
		if sound is not None:
			if self.isEffplay:
				sound.volume = self.effVol
				sound.play()
			else:
				sound.stop()
		return sound

	def stopVocality( self, name, pyModel ):
		"""
		停止声音播放
		"""
		if pyModel is None: return

		sound = pyModel.getSound( name )
		if sound is not None: sound.stop()

	def stopVocalitySound( self, pySound ):
		"""
		停止声音播放
		"""
		pySound.stop()

	# -------------------------------------------------
	def playUI( self, name ):
		"""
		播放UI声音
		@param name:			文件名
		@type name:			string
		"""
		if rds.statusMgr.isBusy() :
			return False
		sound = BigWorld.getSound( name )
		if sound is not None:
			if self.isEffplay:
				sound.volume = self.effVol
				sound.play()
			else:
				sound.stop()
			return True
		return False

	def play2DSound( self, name, isGossipVoice = False ):
		"""
		播放2D音效,为播放音效事件增加的函数,受界面音效参数影响
		@param name:			声音路径名
		@type name:			string
		@param isGossipVoice:			是否为对话语音
		@type isGossipVoice:			bool
		add by wuxo 2011-9-5
		"""
		sound = BigWorld.getSound( name )
		player = BigWorld.player()
		if sound is not None:
			if self.isEffplay:
				sound.volume = self.effVol
				sound.play()
				if isGossipVoice:
					self.__gossipSound = sound
					duration = sound.duration
					BigWorld.callback( duration, player.resetsSoundPriority )
			else:
				sound.stop()
		elif isGossipVoice:
			player.resetsSoundPriority()

	def stop2DSound(self,name):
		"""
		停止名为name的2D音效的播放
		add by wuxo 2011-9-5
		"""
		sound = BigWorld.getSound( name )
		if sound is not None:
			sound.stop()

	# -------------------------------------------------
	def playVoice( self, name ) :
		"""
		播放比较长的语音
		"""
		self.__pyVoice = BigWorld.getSound( name )
		if self.__pyVoice is not None :
			self.__pyVoice.play()

	def switchVoice( self, name ) :
		"""
		切换语音
		"""
		if self.__pyVoice is not None :
			self.stopVoice()
		self.playVoice( name )

	def stopVoice( self ):
		"""
		停止语音播放
		"""
		if self.__pyVoice:
			self.__pyVoice.stop()
			self.__pyVoice = None

	# -------------------------------------------------
	def playFightMusic( self ):
		"""
		播放战斗状态下背景音乐
		"""
		if self.__pyFightSound:		# 上个音乐还没停止
			self.__delayPlayFightMusic()
			if self.__delayStopFightcdid > 0:
				BigWorld.cancelCallback( self.__delayStopFightcdid )
				self.__delayStopFightcdid = 0
			return

		self.__pyFightSound = BigWorld.getSound( Const.FIGHT_MUSIC_PATH )
		if self.__pyFightSound:
			self.setBgPlay( False )		# 停止背景音乐
			self.setBgEffPlay( False )	# 停止背景音效
			self.isPlayFightSound = True
			self.__pyFightSound.volume = self.bgVol
			if self.bgVol > 0.0:
				self.__pyFightSound.play()

	def stopFightMusic( self ):
		"""
		停止战斗状态下背景音乐，采用缓缓终止的方式
		"""
		if self.__pyFightSound is None: return
		if self.__delayPlayFightcdid > 0:	# 取消可能存在的渐入回调
			BigWorld.cancelCallback( self.__delayPlayFightcdid )
			self.__delayPlayFightcdid = 0
		vol = self.__pyFightSound.volume
		vol -= 0.1
		self.__pyFightSound.volume = vol
		if vol <= 0.0:
			self.__pyFightSound.stop()
			self.__pyFightSound = None
			self.isPlayFightSound = False
			self.__delayStopFightcdid = 0
			self.setBgPlay( True )		# 开启背景音乐
			self.setBgEffPlay( True )	# 开启背景音效
			return
		self.__delayStopFightcdid = BigWorld.callback( 0.5, self.stopFightMusic )

	def __delayPlayFightMusic( self ):
		"""
		渐入战斗背景音乐
		"""
		if self.__pyFightSound is None: return
		vol = self.__pyFightSound.volume
		vol += 0.1
		if vol >= self.bgVol:
			vol = self.bgVol
		self.__pyFightSound.volume = vol
		if vol >= self.bgVol: return
		self.__delayPlayFightcdid = BigWorld.callback( 0.5, self.__delayPlayFightMusic )

	# -------------------------------------------------
	def playMusic( self, name ):
		"""
		播放背景音乐

		@param name: 音乐文件名及路径
		@type  name: STRING
		"""
		if self.__bgLocked : return
		self.__pyBgSound = BigWorld.getSound( name )
		if self.__pyBgSound:
			self.__pyBgSound.volume = self.bgVol
			if self.isBgplay:
				self.__pyBgSound.play()

	def switchMusic( self, name ):
		"""
		切换背景音乐
		这个函数和playMusic 不同之处在于 playMusic 是立马缓冲并播放音乐
		而这个函数会缓缓终止当前正在播放的音乐再接着播放切换的音乐
		缓冲时间定为3秒
		@param name: 音乐文件名及路径
		@type  name: STRING
		"""
		if self.__bgLocked : return
		if self.__pyBgSound is None:
			self.playMusic( name )
		elif self.__pyBgSound.name != name.split( "/" )[-1]:	# 不同的音乐才切换
			if self.__delayStopcbid > 0:
				BigWorld.cancelCallback( self.__delayStopcbid )
				self.__delayStopcbid = 0
			bgVol = self.bgVol
			functor = Functor( self.__delayStopMusic, name, bgVol )
			self.__delayStopcbid = BigWorld.callback( 0.0, functor )

	def __delayStopMusic( self, name, bgVol ):
		"""
		缓冲关闭音乐
		"""
		bgVol -= 0.1
		self.__pyBgSound.volume = bgVol
		if bgVol <= 0.0:
			self.stopMusic()
			if self.__delayPlaycbid > 0:
				BigWorld.cancelCallback( self.__delayPlaycbid )
				self.__delayPlaycbid = 0
			functor = Functor( self.__delayPlayMusic, name, bgVol )
			self.__delayPlaycbid = BigWorld.callback( 0.0, functor )
			return
		functor = Functor( self.__delayStopMusic, name, bgVol )
		self.__delayStopcbid = BigWorld.callback( 0.5, functor )
	
	def __delayPlayMusic( self, name, bgVol ):
		"""
		缓冲播放音乐
		"""
		
		if self.__pyBgSound is None:
			self.playMusic( name )
		if self.__pyBgSound is None: return
		bgVol += 0.1
		self.__pyBgSound.volume = bgVol
		if bgVol >= self.bgVol:
			return
		functor = Functor( self.__delayPlayMusic, name, bgVol )
		self.__delayPlaycbid = BigWorld.callback( 0.5, functor )

	def stopMusic( self ):
		"""
		停止音乐播放
		"""
		if self.__bgLocked : return
		if self.__pyBgSound:
			self.__pyBgSound.stop()
			self.__pyBgSound = None

	# -------------------------------------------------
	def playBgEffect( self, name ):
		"""
		播放背景音效

		@param name: 音乐文件名及路径
		@type  name: STRING
		"""
		if self.__bgEffLocked: return
		if self.__pyBgEffect: return
		self.__pyBgEffect = BigWorld.getSound( name )
		if self.__pyBgEffect:
			self.__pyBgEffect.volume = self.bgEffVol
			if self.isBgEffPlay:
				self.__pyBgEffect.play()

	def switchBgEffect( self, name ):
		"""
		切换背景音效
		这个函数和playBgEffect不同之处在于playBgEffect是立马缓冲并播放音乐
		而这个函数会缓缓终止当前正在播放的音效再接着播放切换的音效
		@param name: 音乐文件名及路径
		@type  name: STRING
		"""
		if self.__bgEffLocked: return
		if self.__pyBgEffect is None:
			self.playBgEffect( name )
		elif self.__pyBgEffect.name != name.split( "/" )[-1]:	# 不同的音效才切换
			if self.__delayStopBgEffcdid > 0:
				BigWorld.cancelCallback( self.__delayStopBgEffcdid )
				self.__delayStopBgEffcdid = 0
			bgEffVol = self.bgEffVol
			functor = Functor( self.__delayStopBgEffect, name, bgEffVol )
			self.__delayStopBgEffcdid = BigWorld.callback( 0.0, functor )

	def __delayStopBgEffect( self, name, bgEffVol ):
		"""
		缓冲关闭背景音效
		"""
		bgEffVol -= 0.1
		self.__pyBgEffect.volume = bgEffVol
		if bgEffVol <= 0.0:
			self.stopBgEffect()
			if self.__delayPlayBgEffcbid > 0:
				BigWorld.cancelCallback( self.__delayPlayBgEffcbid )
				self.__delayPlayBgEffcbid = 0
			functor = Functor( self.__delayPlayBgEffect, name, bgEffVol )
			self.__delayPlayBgEffcbid = BigWorld.callback( 0.0, functor )
			return
		functor = Functor( self.__delayStopBgEffect, name, bgEffVol )
		self.__delayStopBgEffcdid = BigWorld.callback( 0.5, functor )

	def __delayPlayBgEffect( self, name, bgEffVol ):
		"""
		缓冲播放背景音效
		"""
		if self.__pyBgEffect is None:
			self.playBgEffect( name )
		if self.__pyBgEffect is None: return
		bgEffVol += 0.1
		self.__pyBgEffect.volume = bgEffVol
		if bgEffVol >= self.bgEffVol: return
		functor = Functor( self.__delayPlayBgEffect, name, bgEffVol )
		self.__delayPlayBgEffcbid = BigWorld.callback( 0.5, functor )

	def stopBgEffect( self ):
		"""
		停止背景音效播放
		"""
		if self.__bgEffLocked : return
		if self.__pyBgEffect:
			self.__pyBgEffect.stop()
			self.__pyBgEffect = None

	# -------------------------------------------------
	def setVocalityVol( self, vol ):
		self.effVol = vol

	def setBgVol( self, vol ):
		self.bgVol = vol
		if self.__pyBgSound:
			self.__pyBgSound.volume = vol
		if self.__pyFightSound:
			self.__pyFightSound.volume = vol

	def setBgEffVol( self, vol ):
		self.bgEffVol = vol
		if self.__pyBgEffect:
			self.__pyBgEffect.volume = vol

	def setMasterVol( self, vol ) :
		self.masterVol = vol
		BigWorld.setMasterVolume( vol )

	def setEffPlay( self, checked ):
		self.isEffplay = checked

	def setBgPlay( self, checked ):
		self.isBgplay = checked
		if self.__pyBgSound and not self.isPlayFightSound:
			if checked:
				self.__pyBgSound.play()
			else:
				self.__pyBgSound.stop()
		if self.__pyFightSound and self.isPlayFightSound:
			if checked:
				self.__pyFightSound.play()
			else:
				self.__pyFightSound.stop()

	def setBgEffPlay( self, checked ):
		if self.isPlayFightSound: return
		self.isBgEffPlay = checked
		if self.__pyBgEffect:
			if checked:
				self.__pyBgEffect.play()
			else:
				self.__pyBgEffect.stop()

	def initAudioSetting( self, cfgSect ):#界面初始化时，调用相关配置

		subsect = cfgSect["audiosetting"]
		if subsect is None:
			sect = cfgSect
			audioSect = sect.createSection( "audiosetting" )
			for tag ,value in self.gb_audioSect.iteritems():
				if tag == "switchvocality" or tag == "switcheffect" or tag == "switchbgeffect":
					audioSect.writeBool( tag, self.gb_audioSect[tag] )
				else:
					audioSect.writeFloat( tag, self.gb_audioSect[tag] )

		self.sect = cfgSect["audiosetting"]
		self.isBgplay = self.sect.readBool( "switchvocality" )
		self.bgVol = self.sect.readFloat( "vocalityvolume" )
		self.isEffplay = self.sect.readBool( "switcheffect" )
		self.effVol = self.sect.readFloat( "effectvolume" )
		self.isBgEffPlay = self.sect.readBool( "switchbgeffect" )
		self.bgEffVol = self.sect.readFloat( "bgeffectvolume" )
		self.masterVol = self.sect.readFloat( "mastervolume" )

		BigWorld.setMasterVolume( self.masterVol )

	def rollBackSect( self, tag, val ):
		if self.sect.has_key( tag ):
			if tag == "switchvocality" or tag == "switcheffect":
				 self.sect.writeBool( tag, val )
			else:
				 self.sect.writeFloat( tag, val )

	def getAudioval( self, tag ):
		if self.sect is None :
			if self.gb_audioSect.has_key( tag ):
				value = self.gb_audioSect[tag]
				return value
		else:
			if self.sect.has_key( tag ):
				if tag == "switchvocality" or tag == "switcheffect":
					value = self.sect.readBool( tag )
				else:
					value = self.sect.readFloat( tag )
				return value

	def onWindowsActive( self, active ):
		"""
		窗口得失焦点回调
		"""
		if active:
			vol = self.masterVol
		else:
			vol = 0
		BigWorld.setMasterVolume( vol )

	def getGossipSound( self ):
		"""
		获取当前播放的对话语音
		"""
		return self.__gossipSound


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
soundMgr = Sound.instance()
