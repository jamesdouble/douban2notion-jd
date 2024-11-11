
RICH_TEXT = "rich_text"
URL = "url"
RELATION = "relation"
NUMBER = "number"
DATE = "date"
FILES = "files"
STATUS = "status"
TITLE = "title"
SELECT = "select"
MULTI_SELECT = "multi_select"

book_properties_type_dict = {
    "书名":TITLE,
    "短评":RICH_TEXT,
    "ISBN":RICH_TEXT,
    "豆瓣链接":URL,
    "作者":RELATION,
    "评分":SELECT,
    "封面":FILES,
    "分类":RELATION,
    "状态":STATUS,
    "日期":DATE,
    "简介":RICH_TEXT,
    "豆瓣链接":URL,
    "出版社":MULTI_SELECT,
}

TAG_ICON_URL = "https://www.notion.so/icons/tag_gray.svg"
USER_ICON_URL = "https://www.notion.so/icons/user-circle-filled_gray.svg"
BOOK_ICON_URL = "https://www.notion.so/icons/book_gray.svg"


movie_properties_type_dict = {
    "豆瓣ID": RICH_TEXT,
    "豆瓣链接":URL,
    "电影名":TITLE,
    "短评":RICH_TEXT,
    "导演":RELATION,
    "演员":MULTI_SELECT,
    "封面":FILES,
    "分类":RELATION,
    "状态":STATUS,
    "类型":SELECT,
    "评分":SELECT,
    "日期":DATE,
    "简介":RICH_TEXT,
    "发布年份": SELECT,
    "原名": RICH_TEXT
}

## 用户相关的观影评价，Subject -> MovieSubject
'''
    "interests": [
        {
            "comment": "",
            "rating": {
                "count": 1,
                "max": 5,
                "star_count": 3.0,
                "value": 3
            },
            "sharing_text": "我的评分：★★★ https://movie.douban.com/subject/26431328/ 来自@豆瓣App",
            "sharing_url": "https://www.douban.com/doubanapp/dispatch?uri=/subject/26431328/interest/4198334688",
            "tags": [],
            "charts": [],
            "platforms": [],
            "vote_count": 0,
            "create_time": "2024-06-18 21:50:50",
            "status": "done",
            "id": 4198334688,
            "is_private": false,
            "subject": 
'''

class UserInterests:

    def __init__(self, data):
        # 对应影视或书
        if data.get("subject") is None:
            return
        subject_json = data.get("subject")
        self.subject = MovieSubject(subject_json)
        # 评价更新时间
        self.createTime = data.get("create_time")
        # 状态 (想看, 在看, 看过)
        self.status = data.get("status")
        # 评分 1 ~ 5
        if data.get("rating"):
            self.rating = data.get("rating").get("value")
        else:
            self.rating = 0
        # 短评
        if data.get("comment"):
            self.comment = data.get("comment")
        else:
            self.comment = ""
        
class MovieSubject:

    # 从 UserInterests 接口返回的，不完整
    def __init__(self, interests_subject):
        # 豆瓣 ID
        self.doubanID = interests_subject.get("id")
        # 标题
        self.title = interests_subject.get("title")
        # 豆瓣链接
        self.url = interests_subject.get("url")
        # 封面地址
        self.cover_url = interests_subject.get("pic").get("large")
        # 类型 (TV or Movie)
        self.type = interests_subject.get("type")
        # 分类
        if interests_subject.get("genres"):
            self.genres = interests_subject.get("genres")
        else:
            self.genres = []
        # 演员
        if interests_subject.get("actors"):
            self.actors = interests_subject.get("actors")[0:100]
        else:
            self.actors = []
        # 导演
        if interests_subject.get("directors"):
            self.directos = interests_subject.get("directors")[0:100]
        else:
            self.directos = []
        # 发布年份
        if interests_subject.get("year"):
            self.pubYear = interests_subject.get("year")
        else:
            self.pubYear = "无"
        # 豆瓣网友评分
        self.doubanRate = interests_subject.get("rating").get("value")

    def update_detail(self, detail):
        # 标题(原文)
        if detail.get("original_title"):
            self.originTitle = detail.get("original_title")
        else:
            self.originTitle = self.title
        # 介绍
        self.intro = detail.get("intro")
        # 集数
        self.episodesCount = detail.get("episodes_count")

 

## 看过接口返回的数据中，Subject 对应一个影视
'''
"subject": {
                "rating": {
                    "count": 410992,
                    "max": 10,
                    "star_count": 4.5,
                    "value": 9.4
                },
                "controversy_reason": "",
                "pubdate": [
                    "2011-12-04(英国)"
                ],
                "pic": {
                    "large": "https://img9.doubanio.com/view/photo/m_ratio_poster/public/p1403875505.jpg",
                    "normal": "https://img9.doubanio.com/view/photo/s_ratio_poster/public/p1403875505.jpg"
                },
                "honor_infos": [
                    {
                        "kind": "tv",
                        "uri": "douban://douban.com/subject_collection/ECZY5KBOQ?type=rank&category=movie&rank_type=tv_genre",
                        "rank": 2,
                        "title": "高分经典欧洲剧榜"
                    }
                ],
                "is_show": false,
                "vendor_icons": [],
                "year": "2011",
                "card_subtitle": "2011 / 英国 / 剧情 科幻 惊悚 / 奥图·巴瑟赫斯特 尤洛斯·林 布莱恩·威尔许 / 罗里·金尼尔 鲁伯特·艾弗雷特",
                "id": "7054120",
                "genres": [
                    "剧情",
                    "科幻",
                    "惊悚"
                ],
                "title": "黑镜 第一季",
                "is_released": true,
                "actors": [
                    {
                        "name": "罗里·金尼尔"
                    },
                ],
                "type": "tv",
                "has_linewatch": false,
                "vendor_desc": "",
                "cover_url": "https://img9.doubanio.com/view/photo/m_ratio_poster/public/p1403875505.jpg",
                "sharing_url": "https://movie.douban.com/subject/7054120/",
                "url": "https://movie.douban.com/subject/7054120/",
                "release_date": null,
                "uri": "douban://douban.com/tv/7054120",
                "subtype": "tv",
                "directors": [
                    {
                        "name": "奥图·巴瑟赫斯特"
                    },
                    {
                        "name": "尤洛斯·林"
                    },
                    {
                        "name": "布莱恩·威尔许"
                    }
                ],
                "album_no_interact": false,
                "article_intros": [],
                "null_rating_reason": ""
            }
'''

# Subject 详情接口
'''
{
    "rating": {
        "count": 0,
        "max": 10,
        "star_count": 0.0,
        "value": 0
    },
    "lineticket_url": "",
    "controversy_reason": "",
    "pubdate": [
        "2024(美国)"
    ],
    "last_episode_number": null,
    "interest_control_info": null,
    "pic": {
        "large": "https://img9.doubanio.com/view/photo/m_ratio_poster/public/p2872708614.jpg",
        "normal": "https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2872708614.jpg"
    },
    "year": "2024",
    "vendor_count": 0,
    "body_bg_color": "f4f7f9",
    "is_tv": true,
    "card_subtitle": "2024 / 美国 / 剧情 科幻 悬疑 惊悚 / 本·斯蒂勒 伊费·麦卡德尔 / 亚当·斯科特 布丽特·洛薇尔",
    "album_no_interact": false,
    "ticket_price_info": "",
    "pre_playable_date": null,
    "can_rate": false,
    "head_info": null,
    "forum_info": null,
    "share_activities": [],
    "webisode": null,
    "id": "35783948",
    "gallery_topic_count": 0,
    "languages": [
        "英语"
    ],
    "genres": [
        "剧情",
        "科幻",
        "悬疑"
    ],
    "review_count": 1,
    "variable_modules": [
        {
            "sub_modules": [],
            "id": "rating"
        },
        {
            "sub_modules": [],
            "id": "other_interests"
        },
        {
            "sub_modules": [],
            "id": "video_photos"
        },
        {
            "sub_modules": [],
            "id": "tags"
        },
        {
            "sub_modules": [
                {
                    "id": "screenshot"
                },
                {
                    "id": "doulist"
                },
                {
                    "id": "status"
                },
                {
                    "id": "other_channels"
                }
            ],
            "id": "share"
        },
        {
            "sub_modules": [],
            "id": "related_items"
        },
        {
            "sub_modules": [
                {
                    "id": "count"
                },
                {
                    "data": [
                        {
                            "name": "热门",
                            "id": "hot"
                        },
                        {
                            "name": "最新",
                            "id": "latest"
                        },
                        {
                            "name": "友邻",
                            "id": "friend"
                        }
                    ],
                    "id": "sort_by",
                    "data_type": "sort_by"
                },
                {
                    "id": "rating_scope"
                }
            ],
            "id": "comments"
        },
        {
            "sub_modules": [],
            "id": "honor_infos"
        },
        {
            "sub_modules": [],
            "id": "interest"
        },
        {
            "sub_modules": [],
            "id": "related_subjects"
        },
        {
            "sub_modules": [
                {
                    "data": {
                        "count": 1409,
                        "title": "综合",
                        "uri": "douban://partial.douban.com/subject/35783948/suggest",
                        "source": "综合",
                        "type": "mixed_suggestion",
                        "id": "mixed_suggestion"
                    },
                    "id": "ugc_tab",
                    "data_type": "ugc_tab"
                },
                {
                    "data": {
                        "source": "reviews",
                        "title": "剧评",
                        "type": "review",
                        "sort_by": [
                            {
                                "name": "热门",
                                "id": "hot"
                            },
                            {
                                "name": "最新",
                                "id": "latest"
                            },
                            {
                                "name": "友邻",
                                "id": "friend"
                            }
                        ]
                    },
                    "id": "ugc_tab",
                    "data_type": "ugc_tab"
                },
                {
                    "data": {
                        "count": 1536,
                        "title": "小组讨论",
                        "uri": "douban://partial.douban.com/subject/35783948/group_topic/_content?group_id=732764&sortby=hot",
                        "source": "小组讨论",
                        "type": "custom",
                        "id": "group"
                    },
                    "id": "ugc_tab",
                    "data_type": "ugc_tab"
                },
                {
                    "data": {
                        "count": 116,
                        "title": "幕后&周边",
                        "uri": "douban://partial.douban.com/subject/35783948/group_topic/_content?group_id=732764&topic_tag_id=111331&sortby=new",
                        "source": "幕后&周边",
                        "type": "custom",
                        "id": "group_111331"
                    },
                    "id": "ugc_tab",
                    "data_type": "ugc_tab"
                },
                {
                    "data": {
                        "count": 106,
                        "title": "细节&解读",
                        "uri": "douban://partial.douban.com/subject/35783948/group_topic/_content?group_id=732764&topic_tag_id=111344&sortby=new",
                        "source": "细节&解读",
                        "type": "custom",
                        "id": "group_111344"
                    },
                    "id": "ugc_tab",
                    "data_type": "ugc_tab"
                },
                {
                    "data": {
                        "count": 56,
                        "title": "嬉笑🤡",
                        "uri": "douban://partial.douban.com/subject/35783948/group_topic/_content?group_id=732764&topic_tag_id=111517&sortby=new",
                        "source": "嬉笑🤡",
                        "type": "custom",
                        "id": "group_111517"
                    },
                    "id": "ugc_tab",
                    "data_type": "ugc_tab"
                }
            ],
            "id": "ugc_tabs"
        }
    ],
    "title": "人生切割术 第二季",
    "intro": "《人生切割术》续订第二季，导演本·斯蒂勒及主演亚当·斯科特、扎克·切利、布丽特·洛薇尔、帕特丽夏·阿奎特、约翰·特托罗、克里斯托弗·沃肯、特拉梅尔·提尔曼、詹·塔洛克等悉数回归，同时官宣格温多兰·克里斯蒂、梅里特·韦弗、鲍勃·巴拉班、阿莉雅·肖卡特、罗比·本森、斯特凡诺·卡拉纳特、约翰·诺贝尔、奥拉维尔·达里·奥拉夫松全新加盟。",
    "interest_cmt_earlier_tip_title": "发布于上映前",
    "has_linewatch": false,
    "comment_count": 1088,
    "forum_topic_count": 1,
    "ticket_promo_text": "",
    "webview_info": {},
    "is_released": false,
    "vendors": [],
    "actors": [
        {
            "name": "亚当·斯科特"
        },
        {
            "name": "布丽特·洛薇尔"
        },
        {
            "name": "帕特丽夏·阿奎特"
        },
        {
            "name": "克里斯托弗·沃肯"
        },
        {
            "name": "约翰·特托罗"
        },
        {
            "name": "迪辰·拉克曼"
        },
        {
            "name": "扎克·切利"
        },
        {
            "name": "詹·塔洛克"
        },
        {
            "name": "迈克尔·切鲁斯"
        },
        {
            "name": "特拉梅尔·提尔曼"
        },
        {
            "name": "格温多兰·克里斯蒂"
        },
        {
            "name": "梅里特·韦弗"
        },
        {
            "name": "鲍勃·巴拉班"
        },
        {
            "name": "阿莉雅·肖卡特"
        },
        {
            "name": "罗比·本森"
        },
        {
            "name": "斯特凡诺·卡拉纳特"
        },
        {
            "name": "约翰·诺贝尔"
        },
        {
            "name": "奥拉维尔·达里·奥拉夫松"
        }
    ],
    "interest": null,
    "subtype": "tv",
    "episodes_count": 10,
    "color_scheme": {
        "is_dark": true,
        "primary_color_light": "486072",
        "_base_color": [
            0.572463768115942,
            0.3709677419354838,
            0.24313725490196078
        ],
        "secondary_color": "f4f7f9",
        "_avg_color": [
            0.5666666666666668,
            0.2427184466019417,
            0.403921568627451
        ],
        "primary_color_dark": "30404c"
    },
    "type": "tv",
    "linewatches": [],
    "info_url": "https://www.douban.com/doubanapp//h5/movie/35783948/desc",
    "tags": [],
    "vendor_desc": "",
    "durations": [
        "45分钟"
    ],
    "cover": {
        "description": "",
        "author": {
            "loc": {
                "id": "118204",
                "name": "泉州",
                "uid": "quanzhou"
            },
            "kind": "user",
            "name": "熊猫仔",
            "reg_time": "2016-10-31 09:40:47",
            "url": "https://www.douban.com/people/153224896/",
            "uri": "douban://douban.com/user/153224896",
            "avatar": "https://img3.doubanio.com/icon/up153224896-2.jpg",
            "is_club": false,
            "type": "user",
            "id": "153224896",
            "uid": "153224896"
        },
        "url": "https://movie.douban.com/photos/photo/2872708614/",
        "image": {
            "normal": {
                "url": "https://img9.doubanio.com/view/photo/m/public/p2872708614.jpg",
                "width": 433,
                "height": 600,
                "size": 0
            },
            "large": {
                "url": "https://img9.doubanio.com/view/photo/l/public/p2872708614.jpg",
                "width": 630,
                "height": 872,
                "size": 0
            },
            "raw": null,
            "small": {
                "url": "https://img9.doubanio.com/view/photo/s/public/p2872708614.jpg",
                "width": 433,
                "height": 600,
                "size": 0
            },
            "primary_color": "DFDFDF",
            "is_animated": false
        },
        "uri": "douban://douban.com/photo/2872708614",
        "create_time": "2022-05-08 14:19:19",
        "position": 0,
        "owner_uri": "douban://douban.com/tv/35783948",
        "type": "photo",
        "id": "2872708614",
        "sharing_url": "https://www.douban.com/doubanapp/dispatch?uri=/photo/2872708614/"
    },
    "cover_url": "https://img9.doubanio.com/view/photo/m_ratio_poster/public/p2872708614.jpg",
    "trailers": [
        {
            "sharing_url": "https://www.douban.com/doubanapp/dispatch?uri=/tv/35783948/trailer%3Ftrailer_id%3D316340%26trailer_type%3DA",
            "video_url": "https://vt1.doubanio.com/202406252038/cf614c30754974e0f0cdbaff8139fcf7/view/movie/M/703160340.mp4",
            "title": "其它预告片：Apple TV+新剧混剪预告",
            "type_name": "预告片",
            "uri": "douban://douban.com/tv/35783948/trailer?trailer_id=316340&trailer_type=A",
            "cover_url": "https://img3.doubanio.com/img/trailer/medium/2909287607.jpg",
            "term_num": 0,
            "n_comments": 3,
            "create_time": "2024-06-11",
            "file_size": 35221103,
            "runtime": "01:44",
            "type": "A",
            "id": "316340",
            "desc": ""
        }
    ],
    "header_bg_color": "30404c",
    "is_douban_intro": false,
    "ticket_vendor_icons": [
        "https://img9.doubanio.com/view/dale-online/dale_ad/public/0589a62f2f2d7c2.jpg"
    ],
    "honor_infos": [
        {
            "kind": "tv",
            "uri": "douban://douban.com/subject_collection/ECYM6MCVA?type=rank&category=movie&rank_type=year",
            "rank": 8,
            "title": "豆瓣2024最值得期待剧集"
        }
    ],
    "sharing_url": "https://movie.douban.com/subject/35783948/",
    "subject_collections": [],
    "wechat_timeline_share": "screenshot",
    "uri": "douban://douban.com/tv/35783948",
    "restrictive_icon_url": "",
    "rate_info": "",
    "release_date": null,
    "countries": [
        "美国"
    ],
    "original_title": "Severance Season 2",
    "is_restrictive": false,
    "webisode_count": 0,
    "episodes_info": "",
    "url": "https://movie.douban.com/subject/35783948/",
    "directors": [
        {
            "name": "本·斯蒂勒"
        },
        {
            "name": "伊费·麦卡德尔"
        }
    ],
    "is_show": false,
    "vendor_icons": [],
    "pre_release_desc": "",
    "video": null,
    "aka": [
        "生活割离术（港）",
        "人生切割术（台）",
        "切割"
    ],
    "realtime_hot_honor_infos": [],
    "null_rating_reason": "尚未播出",
    "interest_cmt_earlier_tip_desc": "该短评的发布时间早于公开上映时间，作者可能通过其他渠道提前观看，请谨慎参考。其评分将不计入总评分。"
}
'''