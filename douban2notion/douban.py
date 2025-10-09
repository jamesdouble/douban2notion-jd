import argparse
from email import feedparser
import json
import os
import re
import pendulum
from retrying import retry
import requests
from douban2notion.notion_helper import NotionHelper
from douban2notion import utils
from typing import List
import feedparser
## Aliyun
import oss2
import uuid
from urllib.request import urlretrieve

from config import movie_properties_type_dict,book_properties_type_dict, TAG_ICON_URL, USER_ICON_URL, UserInterests
from utils import get_icon
from dotenv import load_dotenv

DOUBAN_API_HOST = os.getenv("DOUBAN_API_HOST", "frodo.douban.com")
DOUBAN_API_KEY = os.getenv("DOUBAN_API_KEY", "0ac44ae016490db2204ce0a042db2916")

from douban2notion.config import movie_properties_type_dict,book_properties_type_dict, TAG_ICON_URL, USER_ICON_URL
from douban2notion.utils import get_icon
from dotenv import load_dotenv

# Configure Alibaba Cloud OSS
OSS_ACCESS_KEY_ID = os.getenv("OSS_ACCESS_KEY_ID")
OSS_ACCESS_KEY_SECRET = os.getenv("OSS_ACCESS_KEY_SECRET")
OSS_BUCKET_NAME = os.getenv("OSS_BUCKET_NAME")
OSS_ENDPOINT = os.getenv("OSS_ENDPOINT")

print(
    f"OSS_ACCESS_KEY_ID = {OSS_ACCESS_KEY_ID}\n"
    f"OSS_ACCESS_KEY_SECRET = {OSS_ACCESS_KEY_SECRET}\n"
    f"OSS_ENDPOINT = {OSS_ENDPOINT}\n"
    f"OSS_BUCKET_NAME = {OSS_BUCKET_NAME}\n"
)

# Initialize OSS bucket
auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)

def upload_image_to_oss(image_url: str) -> str:
    """
    Downloads an image from a URL and uploads it to Alibaba Cloud OSS.
    Returns the new URL of the image in OSS.
    """
    try:
        if not OSS_ACCESS_KEY_ID or len(OSS_ACCESS_KEY_ID) <= 0:
            return image_url

        # Download the image to a temporary file
        local_filename = f"/tmp/{uuid.uuid4()}.jpg"
        urlretrieve(image_url, local_filename)

        # Generate a unique key for the image in OSS
        oss_key = f"images/{uuid.uuid4()}.jpg"

        # Upload the image to OSS
        with open(local_filename, "rb") as file:
            bucket.put_object(oss_key, file)

        # Construct the OSS URL
        oss_url = f"https://{OSS_BUCKET_NAME}.{OSS_ENDPOINT}/{oss_key}"

        return oss_url
    except Exception as e:
        print(f"Error uploading image to OSS: {e}")
        return image_url  # Fallback to the original URL if upload fails

load_dotenv()
rating = {
    0: "未评分",
    1: "⭐️",
    2: "⭐️⭐️",
    3: "⭐️⭐️⭐️",
    4: "⭐️⭐️⭐️⭐️",
    5: "⭐️⭐️⭐️⭐️⭐️",
}
movie_status = {
    "mark": "想看",
    "doing": "在看",
    "done": "看过",
}
book_status = {
    "mark": "想读",
    "doing": "在读",
    "done": "读过",
}
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

headers = {
    "host": DOUBAN_API_HOST,
    "authorization": f"Bearer {AUTH_TOKEN}" if AUTH_TOKEN else "",
    "user-agent": "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 15_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.16(0x18001023) NetType/WIFI Language/zh_CN",
    "referer": "https://servicewechat.com/wx2f9b06c1de1ccfca/84/page-frame.html",
}
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def fetch_subjects(user, type_, status):
    offset = 0
    page = 0
    url = f"https://{DOUBAN_API_HOST}/api/v2/user/{user}/interests"
    total = 0
    results = []
    while True:
        params = {
            "type": type_,
            "count": 50,
            "status": status,
            "start": offset,
            "apiKey": DOUBAN_API_KEY,
        }
        response = requests.get(url, headers=headers, params=params)
        
        if response.ok:
            response = response.json()
            interests = response.get("interests")
            print(f"Current Page = {len(interests)}")
            if len(interests)==0:
                print(f"---- { status } fetch Done! -----")
                break
            results.extend(interests)
            print(f"total = {total}")
            print(f"size = {len(results)}")
            page += 1
            offset = page * 50
        else:
            print(response.text)
            return results
    return results

def fetch_subject_detail(douban_id, type):
    print(f"抓取 TV {douban_id} 详细信息")
    url = f"https://{DOUBAN_API_HOST}/api/v2/{type}/{douban_id}"
    params = {
        "apiKey": DOUBAN_API_KEY,
    }
    response = requests.get(url, headers=headers, params=params)

    if response.ok:
        return response.json()
    else:
        return {}

def insert_movie(douban_name,notion_helper):
    notion_movies = notion_helper.query_all(database_id=notion_helper.movie_database_id)
    notion_movie_dict = {}
    for i in notion_movies:
        # 从notion获取已存在的数据库数据
        movie = {}
        for key, value in i.get("properties").items():
            movie[key] = utils.get_property_value(value)
        # 使用豆瓣链接当做唯一 Unique Key
        notion_movie_dict[movie.get("豆瓣链接")] = {
            "短评": movie.get("短评"),
            "状态": movie.get("状态"),
            "日期": movie.get("日期"),
            "评分": movie.get("评分"),
            "page_id": i.get("id")
        }
    print(f"Current Notion Movie Database Count: {len(notion_movie_dict)}")
    results: List[UserInterests] = []
    for i in movie_status.keys():
        movie_subjects = fetch_subjects(douban_name, "movie", i)
        for json_data in movie_subjects:
            try:
                userInterests = UserInterests(json_data)
                results.append(userInterests)
            except:
                continue          
    for result in results:
        movie = {}
        if not result:
            print(result)
            continue
        subject = result.subject
        movie["电影名"] = subject.title
        create_time = result.createTime

        if(subject.title=="未知电影" or subject.title=="未知电视剧") and subject.url in unknown_dict:
            unknown = unknown_dict.get(subject.url)
            subject["title"] = unknown.get("title")
            subject["pic"]["large"] = unknown.get("img")
        movie["电影名"] = subject.title
        create_time = result.createTime
        create_time = pendulum.parse(create_time,tz=utils.tz)
        #时间上传到Notion会丢掉秒的信息，这里直接将秒设置为0
        create_time = create_time.replace(second=0)
        movie["日期"] = create_time.int_timestamp
        movie["豆瓣链接"] = subject.url
        movie["状态"] = movie_status.get(result.status)
        if result.rating:
            movie["评分"] = rating.get(result.rating)
        if result.comment:
            movie["短评"] = result.comment
        if notion_movie_dict.get(movie.get("豆瓣链接")):
            notion_movive = notion_movie_dict.get(movie.get("豆瓣链接"))
            if (
                notion_movive.get("日期") != movie.get("日期")
                or notion_movive.get("短评") != movie.get("短评")
                or notion_movive.get("状态") != movie.get("状态")
                or notion_movive.get("评分") != movie.get("评分")
            ):
                properties = utils.get_properties(movie, movie_properties_type_dict)
                notion_helper.get_date_relation(properties,create_time)
                notion_helper.update_page(
                    page_id=notion_movive.get("page_id"),
                    properties=properties
            )

        else:
            print(f"插入{movie.get('电影名')}")
            movie["类型"] = subject.type
            movie["豆瓣ID"] = subject.doubanID
            if subject.type == 'tv':
                # 拉取 TV 详细信息
                detail_data = fetch_subject_detail(subject.doubanID, 'tv')
                subject.update_detail(detail_data)
            elif subject.type == 'movie':
                detail_data = fetch_subject_detail(subject.doubanID, 'movie')
                subject.update_detail(detail_data)
            else:
                subject.update_detail({})
            cover = subject.get("pic").get("normal")
            if not cover.endswith('.webp'):
                cover = cover.rsplit('.', 1)[0] + '.webp'
            movie["封面"] = upload_image_to_oss(cover)
            movie["原名"] = subject.originTitle
            if subject.get("genres"):
                movie["分类"] = [
                    notion_helper.get_relation_id(
                        x, notion_helper.category_database_id, TAG_ICON_URL
                    )
                    for x in subject.genres
                ]
            if subject.actors:
                l = []
                actors = subject.actors
                for actor in actors:
                    if actor.get("name"):
                        if "/" in actor.get("name"):
                            l.extend(actor.get("name").split("/"))
                        else:
                            l.append(actor.get("name"))  
                movie["演员"] = [
                    notion_helper.get_relation_id(
                        x.get("name"), notion_helper.actor_database_id, USER_ICON_URL
                    )
                    for x in subject.get("actors")[0:100]
                ]
            if subject.get("directors"):
                movie["导演"] = [
                    notion_helper.get_relation_id(
                        x.get("name"), notion_helper.director_database_id, USER_ICON_URL
                    )
                    for x in subject.directos
                ]
            movie["发布年份"] = subject.pubYear
            properties = utils.get_properties(movie, movie_properties_type_dict)
            notion_helper.get_date_relation(properties,create_time)
            parent = {
                "database_id": notion_helper.movie_database_id,
                "type": "database_id",
            }
            notion_helper.create_page(
                parent=parent, properties=properties, icon=get_icon(cover)
            )


def insert_book(douban_name,notion_helper):
    notion_books = notion_helper.query_all(database_id=notion_helper.book_database_id)
    notion_book_dict = {}
    for i in notion_books:
        book = {}
        for key, value in i.get("properties").items():
            book[key] = utils.get_property_value(value)
        notion_book_dict[book.get("豆瓣链接")] = {
            "短评": book.get("短评"),
            "状态": book.get("状态"),
            "日期": book.get("日期"),
            "评分": book.get("评分"),
            "page_id": i.get("id")
        }
    print(f"notion {len(notion_book_dict)}")
    results = []
    for i in book_status.keys():
        results.extend(fetch_subjects(douban_name, "book", i))
    for result in results:
        book = {}
        if not result:
            continue
        subject = result.get("subject")
        book["书名"] = subject.get("title")
        create_time = result.get("create_time")
        create_time = pendulum.parse(create_time,tz=utils.tz)
        #时间上传到Notion会丢掉秒的信息，这里直接将秒设置为0
        create_time = create_time.replace(second=0)
        book["日期"] = create_time.int_timestamp
        book["豆瓣链接"] = subject.get("url")
        book["状态"] = book_status.get(result.get("status"))
        if result.get("rating"):
            book["评分"] = rating.get(result.get("rating").get("value"))
        if result.get("comment"):
            book["短评"] = result.get("comment")
        if notion_book_dict.get(book.get("豆瓣链接")):
            notion_movive = notion_book_dict.get(book.get("豆瓣链接"))
            if (
                notion_movive.get("日期") != book.get("日期")
                or notion_movive.get("短评") != book.get("短评")
                or notion_movive.get("状态") != book.get("状态")
                or notion_movive.get("评分") != book.get("评分")
            ):
                properties = utils.get_properties(book, book_properties_type_dict)
                notion_helper.get_date_relation(properties,create_time)
                notion_helper.update_page(
                    page_id=notion_movive.get("page_id"),
                    properties=properties
            )

        else:
            print(f"插入{book.get('书名')}")
            cover = subject.get("pic").get("large")
            book["封面"] = cover
            book["简介"] = subject.get("intro")
            press = []
            for i in subject.get("press"):
                press.extend(i.split(","))
            book["出版社"] = press
            book["类型"] = subject.get("type")
            if result.get("tags"):
                book["分类"] = [
                    notion_helper.get_relation_id(
                        x, notion_helper.category_database_id, TAG_ICON_URL
                    )
                    for x in result.get("tags")
                ]
            if subject.get("author"):
                book["作者"] = [
                    notion_helper.get_relation_id(
                        x, notion_helper.author_database_id, USER_ICON_URL
                    )
                    for x in subject.get("author")[0:100]
                ]
            properties = utils.get_properties(book, book_properties_type_dict)
            notion_helper.get_date_relation(properties,create_time)
            parent = {
                "database_id": notion_helper.book_database_id,
                "type": "database_id",
            }
            notion_helper.create_page(
                parent=parent, properties=properties, icon=get_icon(cover)
            )

     
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("type")
    options = parser.parse_args()
    type = options.type
    notion_helper = NotionHelper(type)
    is_movie = True if type=="movie" else False
    douban_name = os.getenv("DOUBAN_NAME", None)
    if is_movie:
        insert_movie(douban_name,notion_helper)
    else:
        insert_book(douban_name,notion_helper)
if __name__ == "__main__":
    # main()
    douban_name = os.getenv("DOUBAN_NAME", None)
    for i in movie_status.keys():
        fetch_subjects(douban_name, "movie", i)