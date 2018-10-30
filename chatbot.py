import os
import time
import boto3
from boto3.s3.transfer import S3Transfer
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

boto3.setup_default_session(
    region_name='ap-northeast-2',
    aws_access_key_id=os.getenv('FLANB_AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('FLANB_AWS_SECRET_ACCESS_KEY'))

s3_client = boto3.client('s3')
s3_transfer = S3Transfer(s3_client)


class FBChatbotTest:
    def init(self):
        chrome_options = Options()
        chrome_options.add_argument('headless')
        chrome_options.add_argument('window-size=1920x1080')
        chrome_options.add_argument("disable-gpu")
        self.driver = webdriver.Chrome('./chromedriver_%s' % os.getenv('FLANB_OS'), chrome_options=chrome_options)
        self.driver.get('https://www.messenger.com/t/TravelFlan')
        self.driver.implicitly_wait(1)
        self.login(os.getenv('FLANB_FB_ADMIN_ACCOUNT'), os.getenv('FLANB_FB_ADMIN_PASSWORD'))
        self.clear()
        # 시작하기
        self.execute_while_limited(self.driver.find_element_by_xpath, '//a[@class="_2xh6 _2xh7"]').click()

    def send_keys_with_speed(self, element, text, pause=0.1):
        for character in text:
            element.send_keys(character)
            time.sleep(pause)

    def execute(self, method, times):
        start_time = time.time()
        print('%s start' % (method.__name__, ))
        for e in range(times):
            self.init()
            print('Try %s.....' % (e+1,))
            if self._execute(method) is True:
                print('%s end' % (method.__name__,))
                self.driver.quit()
                print('SUCCESSFUL! %s secs' % (time.time() - start_time))
                return True
            else:
                filename = 'screenshots/' + str(datetime.now()) + '.png'
                self.driver.save_screenshot(filename)
                s3_transfer.upload_file('./%s' % filename, 'flanb-data', 'travis/screenshots/%s/%s' % (
                    os.getenv('TRAVIS_BUILD_NUMBER'), str(datetime.now()) + '.png'))
                self.driver.quit()
        return False

    def _execute(self, method):
        try:
            return method()
        except Exception as e:
            print(e)
            return False

    def execute_while_limited(self, command, param, timeout=30):
        for i in range(timeout-1):
            try:
                cmd = command(param)
            except Exception as e:
                time.sleep(1)
            else:
                # print('%s(\'%s\')' % (command.__name__, param))
                # time.sleep(1)
                return cmd
        raise Exception('[FAILED] %s(\'%s\')' % (command.__name__, param))

    def clear(self):
        # settings button
        self.execute_while_limited(self.driver.find_element_by_xpath,
                                   '//*[@class="_1jt6"]//*[@class="_5blh _4-0h"]').click()
        # remove button
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()="삭제"]|//*[text()="Delete"]').click()
        time.sleep(1)
        # remove button
        self.execute_while_limited(self.driver.find_element_by_xpath,
                                   '//button[@class="_3quh _30yy _2t_ _3ay_ _5ixy"]').click()
        self.driver.get('https://www.messenger.com/t/TravelFlan')

    def login(self, id, pw):
        print('login...')
        self.execute_while_limited(self.driver.find_element_by_id, 'email').send_keys(id)
        self.execute_while_limited(self.driver.find_element_by_id, 'pass').send_keys(pw)
        self.execute_while_limited(self.driver.find_element_by_id, 'loginbutton').click()
        print('login succeed')

    def back_to_main(self):
        # Menu button
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[@class="_3km2"]').click()
        # Back to main menu button
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[@class="_1wc8 _1wc9"]').click()

    def itinerary(self):
        self.back_to_main()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//a[text()="Start Planning"]').click()

        self.execute_while_limited(self.driver.find_element_by_xpath, '//div[text()="Itinerary"]').click()
        self.driver.implicitly_wait(3)
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()="Get started"]').click()
        self.driver.switch_to.frame('messenger_ref')
        self.execute_while_limited(self.driver.find_element_by_xpath, '//span[text()="seoul"]').click()
        self.driver.execute_script("window.scrollTo(0,500)")
        self.execute_while_limited(self.driver.find_element_by_xpath, '//span[text()="3 Day"]').click()
        self.driver.execute_script("window.scrollTo(0,800)")
        self.execute_while_limited(self.driver.find_element_by_xpath, '//li[@class="theme-filter"]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//li[@class="theme-filter"]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//li[@class="theme-filter"]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//span[text()="Send to TravelFlan"]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath,
                                   '//*[text()="Btw, we just saved 4 hours for you! Did you like our service?"]')
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()="⭐⭐⭐⭐⭐"]').click()
        return True

    def hotels(self):
        self.back_to_main()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//a[text()="Start Planning"]').click()

        self.execute_while_limited(self.driver.find_element_by_xpath, '//div[text()="Hotels"]').click()
        self.driver.implicitly_wait(3)
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()="Get started"]').click()
        self.driver.implicitly_wait(1)
        self.driver.switch_to.frame('messenger_ref')
        self.send_keys_with_speed(
            self.execute_while_limited(self.driver.find_element_by_xpath, '//div[@class="SearchBox"]//input'), 'seoul')
        self.execute_while_limited(self.driver.find_elements_by_xpath,
                                   '//ul[@class="ul--HotelsSearchResult"]//div')[0].click()
        self.execute_while_limited(self.driver.find_element_by_xpath,
                                   '//label[text()="Search without room details"]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath,
                                   '//*[text()[contains(., "Send to TravelFlan")]]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath,
                                   '//*[text()="You are nearly there! Here\'s your search result:"]')
        return True

    def restaurants(self):
        self.back_to_main()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//a[text()="Start Planning"]').click()

        self.execute_while_limited(self.driver.find_element_by_xpath, '//div[text()="Restaurants"]').click()
        self.driver.implicitly_wait(3)
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()="Get started"]').click()
        self.driver.implicitly_wait(1)
        self.driver.switch_to.frame('messenger_ref')
        time.sleep(3)
        self.send_keys_with_speed(
            self.execute_while_limited(self.driver.find_element_by_xpath, '//input[@class="geocoder-search"]'), 'seoul')
        time.sleep(1)
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()="Seoul, South Korea"]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//span[text()="Korean"]').click()
        time.sleep(1)
        self.driver.execute_script("window.scrollTo(0,10000)")
        self.execute_while_limited(self.driver.find_element_by_xpath, '//span[text()="Restaurant"]').click()
        time.sleep(1)
        self.driver.execute_script("window.scrollTo(0,10000)")
        self.execute_while_limited(self.driver.find_element_by_xpath, '//span[text()="Rice"]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath,
                                   '//*[text()[contains(., "Send to TravelFlan")]]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath,
                                   '//*[text()="Btw, we just saved 25 minutes for you! Did you like our service?"]')
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()="⭐⭐⭐⭐⭐"]').click()
        return True

    def weather(self):
        self.back_to_main()
        time.sleep(1)
        self.execute_while_limited(self.driver.find_element_by_xpath, '//a[@class="_32rk _32rh _1cy6"]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//a[text()="Get Help"]').click()

        self.execute_while_limited(self.driver.find_element_by_xpath, '//div[text()="Weather"]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath,
                                   '//*[text()[contains(., "What is the location that you wish to search for?")]]')
        time.sleep(5)
        action = ActionChains(self.driver)
        action.send_keys('seoul')
        action.send_keys(Keys.RETURN)
        action.perform()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//div[@class="_3u69 _36wf _2pi9"]').click()

        self.execute_while_limited(self.driver.find_element_by_xpath,
                                   '//*[text()="Keep exploring our services and products"]')
        return True

    def directions(self):
        self.back_to_main()
        time.sleep(1)
        self.execute_while_limited(self.driver.find_element_by_xpath, '//a[@class="_32rk _32rh _1cy6"]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//a[text()="Get Help"]').click()

        self.execute_while_limited(self.driver.find_element_by_xpath, '//div[text()="Directions"]').click()
        self.driver.implicitly_wait(3)
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()="Get started"]').click()
        self.driver.implicitly_wait(3)
        self.driver.switch_to.frame('messenger_ref')
        time.sleep(3)
        self.send_keys_with_speed(
            self.execute_while_limited(self.driver.find_elements_by_xpath, '//input[@class="trans-search"]')[0],
            'seoul')
        time.sleep(1)
        # self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()[contains(., "Seoul, 대한민국")]]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()="Seoul, South Korea"]').click()
        self.send_keys_with_speed(
            self.execute_while_limited(self.driver.find_elements_by_xpath, '//input[@class="trans-search"]')[1],
            'busan')
        time.sleep(1)
        # self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()[contains(., "Busan, 대한민국")]]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()="Busan, South Korea"]').click()
        time.sleep(1)
        self.execute_while_limited(self.driver.find_element_by_xpath,
                                   '//*[text()[contains(., "Send to TravelFlan")]]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath,
                                   '//*[text()="Keep exploring our services and products"]')
        return True

    def main(self):
        if not self.execute(self.itinerary, 5):
            raise Exception('FAILED ITINERARY')
        if not self.execute(self.hotels, 5):
            raise Exception('FAILED HOTELS')
        if not self.execute(self.restaurants, 5):
            raise Exception('FAILED RESTAURANTS')
        if not self.execute(self.weather, 5):
            raise Exception('FAILED WEATHER')
        if not self.execute(self.directions, 5):
            raise Exception('FAILED DIRECTIONS')


class WDChatbotTest:
    def init(self):
        chrome_options = Options()
        chrome_options.add_argument('headless')
        chrome_options.add_argument('window-size=1920x1080')
        chrome_options.add_argument("disable-gpu")
        self.driver = webdriver.Chrome('./chromedriver_%s' % os.getenv('FLANB_OS'), chrome_options=chrome_options)
        self.driver.get('https://www.travelflan.com/')
        self.driver.implicitly_wait(1)
        time.sleep(5)
        self.driver.switch_to.frame('tf-widget-iframe')
        self.execute_while_limited(self.driver.find_element_by_xpath, '//div[@class="tf-icon"]').click()
        time.sleep(1)
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()[contains(., "歡迎來到TravelFlan")]]')

    def send_keys_with_speed(self, element, text, pause=0.1):
        for character in text:
            element.send_keys(character)
            time.sleep(pause)

    def execute(self, method, times):
        start_time = time.time()
        print('%s start' % (method.__name__,))
        for e in range(times):
            self.init()
            print('Try %s.....' % (e+1,))
            if self._execute(method) is True:
                print('%s end' % (method.__name__,))
                self.driver.quit()
                print('SUCCESSFUL! %s secs' % (time.time() - start_time))
                return True
            else:
                filename = 'screenshots/' + str(datetime.now()) + '.png'
                self.driver.save_screenshot(filename)
                s3_transfer.upload_file('./%s' % filename, 'flanb-data', 'travis/screenshots/%s/%s' % (
                    os.getenv('TRAVIS_BUILD_NUMBER'), str(datetime.now()) + '.png'))
                self.driver.quit()
        return False

    def _execute(self, method):
        try:
            return method()
        except Exception as e:
            print(e)
            return False

    def execute_while_limited(self, command, param, timeout=30):
        for i in range(timeout-1):
            try:
                cmd = command(param)
            except Exception as e:
                time.sleep(1)
            else:
                # print('%s(\'%s\')' % (command.__name__, param))
                # time.sleep(1)
                return cmd
        raise Exception('[FAILED] %s(\'%s\')' % (command.__name__, param))

    def itinerary(self):
        self.execute_while_limited(self.driver.find_element_by_xpath,
                                   '//div[@class="quickmenu-image itinerary"]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()=" 首爾 "]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()="3 天 "]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()[contains(., "景點推薦")]]').click()
        self.driver.execute_script("window.scrollTo(0,10000)")
        self.execute_while_limited(self.driver.find_element_by_xpath, '//div[text()=" 送出 "]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()[contains(., "首爾的第1天行程")]]')
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()[contains(., "首爾的第2天行程")]]')
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()[contains(., "首爾的第3天行程")]]')
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()[contains(., "評分")]]')
        return True

    def hotels(self):
        self.execute_while_limited(self.driver.find_element_by_xpath, '//div[@class="quickmenu-image hotel"]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//button[@class="hotel__button"]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath,
                                   '//div[@class="SearchBox"]/input[@class="inputBox"]').send_keys('首爾')
        time.sleep(1)
        self.execute_while_limited(self.driver.find_elements_by_xpath, '//ul[@class="ul--HotelsSearchResult"]/li')[
            0].click()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()[contains(., "暫不指定客房要求")]]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath,
                                   '//*[text()[contains(., "Send to TravelFlan")]]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()[contains(., "按此瀏覽")]]')
        return True

    def booking(self):
        self.execute_while_limited(self.driver.find_element_by_xpath, '//div[@class="quickmenu-image booking"]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()[contains(., "歡迎使用”餐廳預約服務”，請")]]')
        return True

    def weather(self):
        self.execute_while_limited(self.driver.find_element_by_xpath, '//div[@class="quickmenu-image weather"]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()[contains(., "您想查詢哪裡的天氣呢 ?")]]')
        self.execute_while_limited(self.driver.find_element_by_xpath,
                                   '//div[@class="search--input__box"]/input[@class="search--input"]').send_keys('서울')
        time.sleep(1)
        self.execute_while_limited(self.driver.find_elements_by_xpath, '//ul[@class="search--result__container"]/li')[
            0].click()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()[contains(., "送出")]]').click()
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()[contains(., "的天氣")]]')
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()[contains(., " 是")]]').click()
        forecast = self.execute_while_limited(
            self.driver.find_elements_by_xpath,
            '//div[@class="Weather-forecast__container"]/div[@class="Weather-day__container"]')
        assert len(forecast) == 10
        return True

    def directions(self):
        self.execute_while_limited(self.driver.find_element_by_xpath, '//div[@class="quickmenu-image direction"]').click()
        self.execute_while_limited(
            self.driver.find_element_by_xpath,
            '//div[@class="search--input__box add-padding"]/input[@class="search--input"]').send_keys('首爾')
        time.sleep(1)

        self.execute_while_limited(self.driver.find_elements_by_xpath, '//ul[@class="search--result__container"]/li')[
            0].click()
        time.sleep(5)
        self.execute_while_limited(
            self.driver.find_element_by_xpath,
            '//div[@class="search--input__box add-padding"]/input[@class="search--input"]')
        time.sleep(5)
        self.execute_while_limited(
            self.driver.find_elements_by_xpath,
            '//div[@class="search--input__box add-padding"]/input[@class="search--input"]')[1].send_keys('釜山')
        time.sleep(1)
        self.execute_while_limited(self.driver.find_elements_by_xpath, '//ul[@class="search--result__container"]/li')[
            0].click()
        time.sleep(1)
        self.execute_while_limited(self.driver.find_element_by_xpath, '//*[text()[contains(., "送出")]]').click()
        return True

    def main(self):
        if not self.execute(self.itinerary, 5):
            raise Exception('FAILED ITINERARY')
        if not self.execute(self.hotels, 5):
            raise Exception('FAILED HOTELS')
        if not self.execute(self.booking, 5):
            raise Exception('FAILED BOOKING')
        if not self.execute(self.weather, 5):
            raise Exception('FAILED WEATHER')
        if not self.execute(self.directions, 5):
            raise Exception('FAILED DIRECTIONS')


if __name__ == '__main__':
    # fb_test = FBChatbotTest()
    # fb_test.main()
    wd_test = WDChatbotTest()
    wd_test.main()
