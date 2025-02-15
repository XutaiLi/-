import random
import time
from DrissionPage import ChromiumPage
import json
import pandas as pd
import os
from bs4 import BeautifulSoup
# 获取用户基本信息
def extract_info_from_ul(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    info_dict = {
        'room_type': '',
        'stay_date': '',
        'travel_type': '',
        'review_count': ''
    }
    # 遍历所有的li元素
    for li in soup.find_all('li'):
        # 获取图标类型
        icon_type = li.find('i').get('type')
        # 获取文本内容
        text = li.find('span').text.strip()

        # 根据图标类型分类信息
        if icon_type == 'bed':
            info_dict['room_type'] = text
        elif icon_type == 'ic_new_calendar_line':
            info_dict['stay_date'] = text
        elif icon_type == 'beach':
            info_dict['travel_type'] = text
        elif icon_type == 'game':
            info_dict['review_count'] = text

    return info_dict

# 获取评分
def extract_full_score(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    score = soup.find('strong').text.strip()
    total = soup.find('span', class_='total').text.strip()  # 获取 "/ 5"
    total = total.split('/')[1]
    # 如果找不到评分或总分,返回空字典
    if not score or not total:
        return {
            'score': 0,
            'total': 0
        }
    return {
        'score': score,
        'total': total
    }

# 获取评论
def extract_comment(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    comment_data = {
        'text': '',
        'images': []
    }

    # 提取评论文本
    try:
        comment_text = soup.find('div', class_='comment').find('p').text.strip()
    except Exception as e:
        comment_text = soup.find('div', class_='unsefulcomment').find('p').text.strip()
    comment_data['text'] = comment_text

    # 提取图片列表
    images = []
    pictures = soup.find('ul', class_='pictures')
    if pictures:
        for img in pictures.find_all('img'):
            img_url = img.get('src')
            if img_url:
                # 确保URL是完整的
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                images.append(img_url)
    comment_data['images'] = images

    return comment_data

# 打包所有信息
def parse_review_card(card, hotel_id,star,add,start,sum,num,photo):
    """
    解析单个评论卡片的所有信息

    Args:
        card: 评论卡片元素
        hotel_id: 酒店ID

    Returns:
        dict: 包含所有评论信息的字典
    """
    try:
        # 获取用户基本信息
        result = extract_info_from_ul(card.ele('.other').html)

        # 获取评分信息
        score = extract_full_score(card.ele('.m-score_single').html)

        # 获取评论内容和图片
        try:
            comment = extract_comment(card.ele('.comment').html)
        except Exception as e:
            comment = extract_comment(card.ele('.unsefulcomment').html)

        # 构建完整的评论数据
        review = {
            # 信息
            'hotel_id': hotel_id,
            'hotel_star':star,
            'hotel_add':add,
            'hotel_sum': sum,
            'hotel_start':start,
            'hotel_num':num,
            'hotel_photo_num':photo,
            'user_name': card.ele('.name').text,
            'room_type': result['room_type'],
            'stay_date': result['stay_date'],
            'travel_type': result['travel_type'],
            'review_count': result['review_count'],

            # 评分信息
            'score': score['score'],
            'total': score['total'],

            # 评论内容
            'comment': comment['text'],

            # 图片链接
            'photos': comment['images'],

            # 发布信息
            'publish_info': card.ele('.reviewDate').text,
        }

        return review

    except Exception as e:
        print(f"解析评论卡片时出错: {str(e)}")
        return review

# 提取id
def extract_hotel_id_from_url(url):
    """从 URL 中提取酒店 ID"""
    try:
        # 使用split分割URL，取最后一个部分
        hotel_id = url.split('/')[-1]
        # 去掉.html后缀
        hotel_id = hotel_id.replace('.html', '')
        return hotel_id
    except Exception as e:
        print(f"解析酒店ID时出错: {e}")
        return url

# 评论总量
def parse_review_count(page):
    """
    使用BeautifulSoup解析评论数量
    返回: 评论总数(int)
    """
    try:
        from bs4 import BeautifulSoup

        # 获取页面HTML
        html_content = page.html
        soup = BeautifulSoup(html_content, 'html.parser')

        # 查找评论标题元素
        title_element = soup.find('h2', class_='o-module-tit')
        if title_element:
            # 获取span中的文本
            span_text = title_element.find('span').text
            print("获取到的span文本:", span_text)

            # 提取数字
            import re
            match = re.search(r'(\d+[,\d]*)', span_text)
            if match:
                # 移除逗号并转换为整数
                review_count = int(match.group(1).replace(',', ''))
                print(f"解析到评论总数: {review_count}")
                return review_count

        print("未能从文本中提取评论数")
        return 0

    except Exception as e:
        print(f"解析评论数量时出错: {e}")
        return 0

#酒店星级图片的网址，需要从网址中解析出来
def hotel_star(page):
    #class ="detail-headline_new_level" src="http://webresource.c-ctrip.com/ResH5HotelOnline/R1/hotel_detail_icon_diamond3_20180824.png" alt="hotel-level"
    #定位元素

    try:
        star=page.ele(f'@@class=detail-headline_new_level@@alt=hotel-level')
        url_star=star.attr('src')
        print("star",url_star)
        return url_star
    except Exception as e:
        print(f"星级获取失败: {e}")
        return 0

#地址
def address_get(page):
    #<span class="detail-headline_position_text">上海浦东新区川沙镇陈桥村1189号</span>
    try:
        add=page.ele('.detail-headline_position_text').text
        print("地址",add)
        return add
    except Exception as e:
        print(f"地址获取失败: {e}")
        return 0

#简介
def com_address_get(page):
    #<div class="m-h-d-eclips-ie text-ellipsis-4"><span>上海蔓言·民宿位于上海迪士尼度假区东大门，距离乐园5分钟左右车程。 本店专门为迪士尼游客量身而打造的网红民宿，民宿有免费早餐，中晚餐也可以提前预定。本店提供迪士尼乐园早晚专车接送服务，迪士尼地铁站接送和浦东机场接送机服务，需要接送的客人可提前联系管家电话。选择蔓言，让您的迪士尼之游更加省心 安心和放心。蔓言会让您的选择更加值得，我们期待与您的相会。</span><br></div>
    try:
        for i in range(0,5):

            add=page.ele('.m-h-d-eclips-ie text-ellipsis-4').text
            print("简介",add)
            time.sleep(1)
            if add:
                break

        return add
    except Exception as e:
        print(f"简介获取失败: {e}")
        return 0

#开业时间
def start_time(page):
    #<span class="detail-headline_desc_ky">开业：2021</span>
    try:
        start=page.ele('.detail-headline_desc_ky').text
        print("开业时间",start)
        return start
    except Exception as e:
        print(f"位置1开业时间获取失败: {e}")
        return 0

#房间总数，含有其他介绍，比如装修，开业，后期清理
def romm_num(page):
    #<ul class="basic-sub clearfix"><li>开业：2021</li><li>客房数：18</li></ul>
    try:
        start=page.ele('.basic-sub clearfix').text
        print("房间数量",start)
        return start
    except Exception as e:
        print(f"房间数量获取失败: {e}")
        return 0

#酒店照片总数
def photo_num(page):
    ##<span class="detail-headalbum_focus_des">查看所有274张照片</span>
    try:
        start=page.ele('.detail-headalbum_focus_des').text
        print("照片数量",start)
        return start
    except Exception as e:
        print(f"照片数量获取失败: {e}")
        return 0

#获取页面总数
def total(page):
#    <li class="m-pagination_numbers">
#       <div class="m_num">1</div>
#       <div class="m_num">2</div>
#       <div class="m_num m_num_checked">3</div>
#       <div class="m_num">4</div>
#       <div class="m_num">5</div>
#       <div class="m_num">...</div>
#       <div class="m_num">48</div></li>
    try:
        start=page.ele('.m-pagination_numbers').texts()
        print("总页数",start)
        return start
    except Exception as e:
        print(f"总页数获取失败: {e}")
        return 1

#折叠打开
def unfold(page,hotel_id,star,add,start,sum,num,photo):
    try:
        op = page.ele('.unusefulReview-info-show')
        op.click()
        print("展开成功")
        #展开成功后，一直点击更多评论
        #<div class="unusefulReview-more"><button type="outline" class="u-btn u-btn-outline u-btn-small active"><span>查看更多折叠评论</span></button></div>
        while True:
            try:
                op2 = page.ele('.unusefulReview-more')
                op2.click()
                random_seconds = random.randint(1, 10)
                time.sleep(random_seconds)
            except Exception as e:
                print("所有评论都已展开")
                break
        return 1
    except Exception as e:
        return 0
def after_unfold(page):
        pass

#<div class="unusefulReview-info-show"><span>查看更多</span><i type="ic_new_dropdown_line" class="u-icon u-icon-ic_new_dropdown_line unusefulReview-drop_line"></i></div>

#总过程
def get_individual_data(url):
    page = ChromiumPage()

    page.get(url)
    star=hotel_star(page)
    add=address_get(page)
    start=start_time(page)
    sum=com_address_get(page)
    num=romm_num(page)
    photo=photo_num(page)
    # 判断要抓多少页，方便停止
    page_num_max=total(page)
    #总评论数
    review_count = parse_review_count(page)
    print(f"该酒店共有 {review_count} 条评论")
    # time.sleep(3)
    #已经抓取的评论数量
    review_num=0
    page_num = 1
    # 用于存放当前页面评论信息，
    while True:

        hotel_id = extract_hotel_id_from_url(url)
        #每一页都尝试点击展开评论，防止有折叠评论
        t=unfold(page, hotel_id, star, add, start, sum, num, photo)
        # # 获取所有评论卡片
        # review_cards = page.eles('.m-reviewCard-item')
        #加速
        review_cards = page.s_eles('.m-reviewCard-item')
        print("此轮数量",len(review_cards))
        review_num=review_num+len(review_cards)
        print(f"已获取{review_num}评论，共{review_count}评论")
        i=0
        for card in review_cards:
            i+=1
            if t==1:
                print(i)
            review = parse_review_card(card, hotel_id,star,add,start,sum,num,photo)
            if review:
                # reviews_data.append(review)
                df_result = pd.DataFrame([review])
                csv_filename = 'beijing_review_list1.csv'
                # 判断文件是否存在
                if not os.path.exists(csv_filename):
                    # 第一次写入，包含表头
                    df_result.to_csv(csv_filename, index=False, encoding='utf-8-sig')
                    print(f"创建新文件并写入数据：{csv_filename}")
                else:
                    # 追加模式，不包含表头
                    df_result.to_csv(csv_filename, mode='a', header=False, index=False, encoding='utf-8-sig')
                    #print("当前爬取页数为", page_num, f"追加数据到文件：{csv_filename}")

        page.scroll.down(6500)
        if review_num == review_count:
            break


        # 点击下一页
        try:
            next_page = page.ele('.u-icon u-icon-arrowRight')
            next_page.click()
            page_num = page_num+1
            if page_num % 5 == 0:
                time.sleep(random.randint(5, 10))
            if page_num % 10 == 0:
                time.sleep(random.randint(1, 15))

        except Exception as e:
            print(f"点击下一页时出错: {e}")
            break


        try:
            if int(page_num) > int(page_num_max[-1]):
                break
        except Exception as e:
            if int(page_num_max)==1:
                break
    
    return
# 调试
# url=('https://hotels.ctrip.com/hotels/121612883.html')
# get_individual_data(url)

