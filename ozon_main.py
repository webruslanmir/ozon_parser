import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import random
head_of_link = 'https://www.ozon.ru'


class OzonSellerParse:
    # def __init__(self, keyword: str):
    #     self.keyword = keyword

    def page_down(self, page):
        page.evaluate(f'''
                                const scrollStep = {random.randint(2000, 2300)}; // Размер шага прокрутки (в пикселях)
                                const scrollInterval = {random.randint(100, 140)}; // Интервал между шагами (в миллисекундах)

                                const scrollHeight = document.documentElement.scrollHeight;
                                let currentPosition = 0;
                                const interval = setInterval(() => {{
                                    window.scrollBy(0, scrollStep);
                                    currentPosition += scrollStep;

                                    if (currentPosition >= scrollHeight) {{
                                        clearInterval(interval);
                                    }}
                                }}, scrollInterval);
                            ''')

    def __get_seller_name(self, url: str):
        self.page2 = self.context.new_page()
        self.page2.goto(url=url)
        # time.sleep(5)

        self.page_down(self.page2)
        try:
            self.page2.wait_for_selector(f':text("Продавец")')
            elements = self.page2.query_selector_all('a[href^="https://www.ozon.ru/sell"]')
            seller_name = elements[1].inner_text()
            print(seller_name)
        except Exception:
            print('Seller not found')
            return
        # finally:
        #     self.page2.close()

    def __get_links(self):
        self.page.wait_for_selector("#paginatorContent")
        self.page_down(self.page)
        self.page.wait_for_selector(f':text("Дальше")')

        search_result = self.page.query_selector("#paginatorContent")
        links = search_result.query_selector_all(".tile-hover-target")
        print(len(links))
        for count, link in enumerate(links):
            if count > 10: break
            url = "https://ozon.ru" + link.get_attribute('href')
            self.__get_seller_name(url=url)

    def __get_seller_list(self):
        seller_list = []
        seller_info = self.page.query_selector_all('a[href^="/seller?category="]')
        for el in seller_info:
            end_of_link = el.get_attribute('href')
            soup = BeautifulSoup(el.inner_html(), 'html.parser')
            title, count = soup.findAll('div')[0].findAll('span')
            seller_list.append([title.text.strip(), count.text.strip(), f'{ head_of_link }{end_of_link}'])
        return seller_list

    def parse(self):
        sellers_with_categories = {}
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
            self.context = browser.new_context(geolocation={'latitude': 55.751244, 'longitude': 37.618423},
                                               permissions=["notifications"])
            self.page = self.context.new_page()
            self.page.goto("https://www.ozon.ru/seller")
            # self.page.goto("https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html")
            time.sleep(.5)
            seller_list = self.__get_seller_list()

            for seller in seller_list:

                sellers_with_categories[seller[0]] = {'count': seller[1], }
                self.page.goto(f"{seller[2]}")
                count_first = 0
                # count_last = 0
                repeat_count = 0
                while repeat_count < 40:

                    self.page_down(self.page)
                    count_last = len(self.page.query_selector_all('[data-card-in-a-row="4"]'))
                    print(f'{seller[0]}, {count_last}, rep_count={repeat_count}')
                    if count_last > count_first:
                        count_first = count_last
                        repeat_count = 0
                    elif count_last == count_first:
                        self.page_down(self.page)
                        # count_last = len(self.page.query_selector_all('[data-card-in-a-row="4"]'))
                        repeat_count += 1

                result = self.page.query_selector_all('[data-card-in-a-row="4"]')
                for el in result:
                    soup = BeautifulSoup(el.inner_html(), 'html.parser')
                    shop_link = f'{ head_of_link }{ soup.a["href"] }'
                    self.page.goto(f"{ shop_link }")
                    self.page.click('button:has-text("О магазине")')
                    div_element = self.page.query_selector('div[data-widget="modalLayout"]')
                    soup = BeautifulSoup(div_element.inner_html(), 'html.parser')
                    target_list = soup.find_all('span', class_='tsBody400Small')
                    res = target_list[1].get_text('!!').split('!!')    # IndexError: list index out of range
                    print(res)



if __name__ == "__main__":
    oz = OzonSellerParse()
    oz.parse()

    # time.sleep(20)
