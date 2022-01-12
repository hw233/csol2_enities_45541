# -*- coding: cp950 -*-

# --------------------------------------------------------------------
# 全局文本標簽
# --------------------------------------------------------------------
# 時間
CHTIME_YEAR							= "年"
CHTIME_MONTH						= "月"
CHTIME_DAY							= "天"
CHTIME_WEEK							= "星期"
CHTIME_HOUR							= "小時"
CHTIME_MINUTE						= "分鐘"
CHTIME_SECOND						= "秒"
CHTIME_HMS							= "%i 小時 %i 分鐘 %i 秒"
CHTIME_MS							= "%i 分鐘 %i 秒"

# 金錢
MONEY_GOLD							= "金"
MONEY_SILVER						= "銀"
MONEY_COPPER						= "銅"
MONEY_GOLD_COIN						= "金幣"
MONEY_SILVER_COIN					= "銀幣"
MONEY_COPPER_COIN					= "銅幣"
MONEY_GSP							= "%i 金 %i 銀 %i 銅"
MONEY_GS							= "%i 金 %i 銀"
MONEY_SP							= "%i 銀 %i 銅"

# 數字
NUM_0								= "零"
NUM_1								= "一"
NUM_2								= "二"
NUM_3								= "三"
NUM_4								= "四"
NUM_5								= "五"
NUM_6								= "六"
NUM_7								= "七"
NUM_8								= "八"
NUM_9								= "九"
NUM_10								= "十"
NUM_COUPLE							= "雙"

# 確認
QUERY_YES							= "是"
QUERY_NO							= "否"

# 性別
GENDER_MAN							= "男"
GENDER_WOMAN						= "女"
GENDER_MALE							= "雄"
GENDER_FEMALE						= "雌"
GENDER_UNIT_MAN						= "男性"
GENDER_UNIT_WOMAN					= "女性"
GENDER_UNIT_MALE					= "雄性"
GENDER_UNIT_FEMALE					= "雌性"

# 職業
PROFESSION_UNKNOW					= "未知"
PROFESSION_FIGHTER				 	= "戰士"
PROFESSION_SWORD				 	= "劍客"
PROFESSION_ARCHER					= "射手"
PROFESSION_MAGIC					= "法師"
PROFESSION_WARLOCK					= "巫師"		# （廢棄）
PROFESSION_PRIEST					= "祭師"		# （廢棄）
PROFESSION_PALADIN					= "騎士"		# （廢棄）

# 顏色
WHITE								= "白色"
BLUE								= "藍色"
GOLD								= "金色"
PINK								= "粉色"
GREEN								= "綠色"
ORANGE								= "橙色"

# --------------------------------------------------------------------
# 寵物（寵物屬性不打算跟人物共享，因為還不知道策劃是否還會修改寵物屬性）
# --------------------------------------------------------------------
PET_HIERARCHY_GROWNUP				= "成年"
PET_HIERARCHY_INFANCY1				= "寶寶"
PET_HIERARCHY_INFANCY2				= "二代寶寶"

PET_TYPE_STRENGTH					= "力量型"		# （不打算跟人物共享，因為還不知道策劃是否還會修改寵物屬性）
PET_TYPE_SMART						= "敏捷型"		# （不打算跟人物共享，因為還不知道策劃是否還會修改寵物屬性）
PET_TYPE_INTELLECT					= "智力型"		# （不打算跟人物共享，因為還不知道策劃是否還會修改寵物屬性）
PET_TYPE_BALANCED					= "均衡型"		# （不打算跟人物共享，因為還不知道策劃是否還會修改寵物屬性）

PET_CORPOREITY_NAME					= "體質屬性"	# （不打算跟人物共享，因為還不知道策劃是否還會修改寵物屬性）
PET_STRENGTH_NAME					= "力量屬性"	# （不打算跟人物共享，因為還不知道策劃是否還會修改寵物屬性）
PET_INTELLECT_NAME					= "智力屬性"	# （不打算跟人物共享，因為還不知道策劃是否還會修改寵物屬性）
PET_DEXTERITY_NAME					= "敏捷屬性"	# （不打算跟人物共享，因為還不知道策劃是否還會修改寵物屬性）

PET_CHARACTER_SUREFOOTED			= "穩重型"
PET_CHARACTER_CLOVER				= "聰慧型"
PET_CHARACTER_CANNILY				= "精明型"
PET_CHARACTER_BRAVE					= "勇敢型"
PET_CHARACTER_LIVELY				= "活潑型"

PET_GROWNUP_DSP_NAME				= "%s"				# 成年寵物默認名稱 ‘%s’為寵物前身的名稱
PET_INFANCY1_DSP_NAME				= "%s寶寶" 			# 一代寵物默認名稱
PET_INFANCY2_DSP_NAME				= "二代%s寶寶"		# 二代寵物默認名稱

PET_TRAIN_TYPE_COMMON				= "普通"			# 普通代練
PET_TRAIN_TYPE_HARD					= "刻苦"			# 刻苦代練

PET_JOYANCY_ANGRY					= "生氣"
PET_JOYANCY_DEPRESSED				= "郁悶"
PET_JOYANCY_NORMAL					= "普通"
PET_JOYANCY_WELL					= "快樂"

PET_ACTION_MODE_FOLLOW				= "跟隨"
PET_ACTION_MODE_KEEPING				= "停留"
PET_TUSSLE_MODE_ACTIVE				= "主動"
PET_TUSSLE_MODE_PASSIVE				= "被動"
PET_TUSSLE_MODE_GUARD				= "防禦"


# --------------------------------------------------------------------
# 聊天
# --------------------------------------------------------------------
CHAT_CHANNEL_NEAR					= "附近"
CHAT_CHANNEL_LOCAL					= "本地"
CHAT_CHANNEL_TEAM					= "隊伍"
CHAT_CHANNEL_FAMILY					= "家族"
CHAT_CHANNEL_TONG					= "幫會"
CHAT_CHANNEL_WHISPER				= "密語"
CHAT_CHANNEL_WORLD					= "世界"
CHAT_CHANNEL_RUMOR					= "謠言"
CHAT_CHANNEL_WELKIN_YELL			= "天音"
CHAT_CHANNEL_TUNNEL_YELL			= "地音"
CHAT_CHANNEL_SYSBROADCAST			= "廣播"
CHAT_CHANNEL_NPC_SPEAK				= "NPC"
CHAT_CHANNEL_NPC_TALK				= "NPC對話"
CHAT_CHANNEL_SYSTEM					= "系統"
CHAT_CHANNEL_COMBAT					= "戰鬥"
CHAT_CHANNEL_PERSONAL				= "個人"
CHAT_CHANNEL_MESSAGE				= "消息"
CHAT_CHANNEL_SC_HINT				= "屏幕"
CHAT_CHANNEL_MSGBOX					= "提示"
CHAT_CHANNEL_PLAYMATE				= "玩伴"

# --------------------------------------------------------------------
# Role
# --------------------------------------------------------------------
ROLE_YOUR_TREASURE					= "您的神秘大禮！"
ROLE_SYSTEM_MAIL					= "系統郵件。"
ROLE_YOUR_PRESENT					= "您的神秘禮品。"

# --------------------------------------------------------------------
# RoleQuizGame
# --------------------------------------------------------------------
ROLE_QUIZ_GAME1						= "恭喜您獲得“虎年利是封”一個！"
ROLE_QUIZ_GAME2						= "恭喜您獲得“虎年利是封”一個！"

# --------------------------------------------------------------------
# 家族
# --------------------------------------------------------------------
FAMILY_GRADE_SHAIKH					= "族長"
FAMILY_GRADE_SHAIKH_SUBALTERN		= "副族長"
FAMILY_GRADE_MEMBER					= "普通成員"

# --------------------------------------------------------------------
# 幫會
# --------------------------------------------------------------------
TONG_GRADE_CHIEF					= "幫主"
TONG_GRADE_CHIEF_SUBALTERN			= "副幫主"
TONG_GRADE_BODYGUARD				= "護法"
TONG_GRADE_TONG						= "堂主"
TONG_GRADE_DEALER					= "商人"
TONG_GRADE_RINGLEADER				= "小頭目"
TONG_GRADE_ELITE					= "精英"
TONG_GRADE_MEMBER					= "嘍囉"

# --------------------------------------------------------------------
# PK
# --------------------------------------------------------------------
PK_CONTROL_PROTECT_PEACE			= "和平"
PK_CONTROL_PROTECT_TEAMMATE			= "組隊"
PK_CONTROL_PROTECT_KIN				= "家族"
PK_CONTROL_PROTECT_TONG				= "幫會"
PK_CONTROL_PROTECT_NONE				= "全體"
PK_CONTROL_PROTECT_RIGHTFUL			= "善惡"

# --------------------------------------------------------------------
# 天幣交易
# --------------------------------------------------------------------
YBT_ON_TRADE_MAIL_TITLE		= "天幣交易系統提示。"
YBT_ON_BUY_MAIL_MSG			= "您成功求購%i金天幣，請到“訂單發布”界面中去取出金天幣。"
YBT_ON_SELL_MAIL_MSG			= "您寄售的天幣已成功出售，您獲得%i銅，請到“訂單發布”界面中去取出金錢。"
# --------------------------------------------------------------------
# 按模塊分的文本
# --------------------------------------------------------------------
