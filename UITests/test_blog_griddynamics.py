from selene.conditions import clickable, exact_text, size_at_least, visible
from selene.tools import s, set_driver, visit
from selenium import webdriver


class TestBlogGridDynamics:

    def setup_class(self):
        driver = webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub',
                                  desired_capabilities={'browserName': 'chrome',
                                                        'version': '73.0',
                                                        "screenResolution": "1920x1080x24",
                                                        'enableVNC': True,
                                                        'enableVideo': False})
        driver.set_window_size(1920, 1080)
        set_driver(driver)

    def test_find_link_is_available(self):
        visit("http://blog.griddynamics.com")
        s(".explore a").should_be(visible)
        s(".explore a").should_be(clickable)

    def test_result_list_has_at_least_one_article_for_2017(self):
        visit("http://blog.griddynamics.com")
        s(".explore a").click()
        all_years_article_text = s("#explrlst").ss(".explor .cntt a")[0].text
        s("#filter2").hover().s("[data-year=year2017]").click()
        s("#explrlst").ss(".explor .cntt a")[0].should_not_have(exact_text(all_years_article_text.encode('utf-8')))
        s("#explrlst").ss(".explor").should_be(size_at_least(1))

    def test_result_list_has_at_least_one_article_for_current_year(self):
        visit("http://blog.griddynamics.com")
        s(".explore a").click()
        all_years_article_text = s("#explrlst").ss(".explor .cntt a")[0].text
        s("#filter2").hover().s("[data-year=year2017]").click()
        s("#explrlst").ss(".explor .cntt a")[0].should_not_have(exact_text(all_years_article_text.encode('utf-8')))
        s("#filter2").hover().s("[data-year=all]").click()
        s("#explrlst").ss(".explor").should_be(size_at_least(1))
        s("#explrlst").ss(".explor .cntt a")[0].should_have(exact_text(all_years_article_text.encode('utf-8')))
