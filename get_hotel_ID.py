import time
from DrissionPage import ChromiumPage
import json
import pandas as pd
import os


# 点击行政区标签
def click_admin_area_tab(page):
    """点击行政区标签"""
    try:
        admin_area_tab = page.ele('@aria-label=行政区')
        print("admin",admin_area_tab)
        admin_area_tab.click()
        print("成功点击行政区标签")
        time.sleep(3)
        return True
    except Exception as e:
        print(f"点击行政区标签失败: {e}")
        return False

#换城市时记得更换存储文件名

#上海
#url='https://hotels.ctrip.com/hotels/list?countryId=1&city=2&provinceId=0'
#area = [ '黄浦区','浦东新区','静安区', '徐汇区', '松江区',  '崇明区', '闵行区', '长宁区', '嘉定区', '青浦区', '杨浦区', '宝山区', '普陀区', '奉贤区', '虹口区', '金山区']

# #北京
# url='https://hotels.ctrip.com/hotels/list?countryId=1&city=1&provinceId=0'
# area=['朝阳区','海淀区','西城区','东城区','丰台区','通州区','昌平区','延庆区','怀柔区','大兴区','密云区','顺义区','石景山区','门头沟区','房山区','平谷区']
# #丰台区,怀柔区,大兴区,顺义区

#西安
# url='https://hotels.ctrip.com/hotels/list?countryId=1&city=10&provinceId=0'
# area=['鄠邑区','阎良区','莲湖区','新城区','高陵区','雁塔区','未央区','临潼区','碑林区','长安区','灞桥区']

#合肥  ,'蜀山区','包河区','瑶海区'
url='https://hotels.ctrip.com/hotels/list?countryId=1&city=278&provinceId=0'
area=['庐阳区']

# 创建对象
page = ChromiumPage()
# 访问网页
page.get(url)
# page.set.window.hide()


for area_name in area:
    page.refresh()
    time.sleep(1)
    ##点击“按照行政区排序”
    click_admin_area_tab(page)
    time.sleep(2)
    try:
        ## 热门区域点击
        #area_element = page.ele(f'@aria-label={area_name}')
        #行政区域点击
        #需要双元素定位，不然会定位到热门区域，导致点击不了！！！
        area_element= page.ele(f'@@class=filter-item single@@aria-label={area_name}')
        # print(area_element)
        area_element.click.left()
        print("成功点击", area_name)
        time.sleep(3)
        #需要先滚动，加载几次，才能找到”更多页面“
        # 滚动加载部分，
        for j in range(1, 40,):
            try:
                #模拟人滚动，
                for i in range(20, 90):
                    try:
                        page.run_js(f"document.documentElement.scrollTop={i * 100*j}")
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"滚动出错: {e}")
                        time.sleep(3)
                        continue
                # page.scroll.to_location(300,50)
                try:
                    #尝试是否发现“更多页面”，
                    morepage = page.ele('.btn-box')
                    morepage.click()
                except:
                    print("没有更多页面或点击更多按钮失败")
                    break
            except Exception as e:
                print(f"加载更多页面时出错: {e}")
                time.sleep(3)
                continue

        # 数据抓取部分
        hotel_info = []
        try:
            hotel_cards = page.eles('.hotel-card')
            hotels = page.eles('.hotelName')
            prices = page.eles('.sale')

            for card, name, price in zip(hotel_cards, hotels, prices):
                try:
                    data_exposure = card.attr('data-exposure')
                    if data_exposure:
                        data = json.loads(data_exposure)
                        hotel_data = {
                            'id': data['data']['masterhotelid'],
                            'name': name.text,
                            'price': price.text.replace('¥', '').strip()
                        }
                        hotel_info.append(hotel_data)
                        print(f"酒店ID: {hotel_data['id']}, 名称: {hotel_data['name']}, 价格: {hotel_data['price']}")
                except Exception as e:
                    print(f"处理单个酒店数据时出错: {e}")
                    time.sleep(3)
                    continue

            # 保存数据
            if hotel_info:
                df = pd.DataFrame(hotel_info)
                if not os.path.exists('hotels2.csv'):
                    df.to_csv('hotels_hefei.csv', index=False, encoding='utf-8')
                else:
                    df.to_csv('hotels_hefei.csv', mode='a', header=False, index=False, encoding='utf-8')
                print(f"{area_name} 区域数据保存成功")
                
        except Exception as e:
            print(f"获取酒店数据时出错: {e}")
            time.sleep(3)
            continue

    except Exception as e:
        print(f"处理 {area_name} 区域时出错: {e}")
        time.sleep(3)
        continue


