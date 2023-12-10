"""
Парсер плагина SPP

1/2 документ плагина
"""
import logging
import os
import time
from selenium.webdriver.common.by import By
from src.spp.types import SPP_document
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import dateparser
from datetime import datetime
import pytz
from random import uniform


class EBA:
    """
    Класс парсера плагина SPP

    :warning Все необходимое для работы парсера должно находится внутри этого класса

    :_content_document: Это список объектов документа. При старте класса этот список должен обнулиться,
                        а затем по мере обработки источника - заполняться.


    """

    SOURCE_NAME = 'eba'
    _content_document: list[SPP_document]
    HOST = "https://www.abe-eba.eu/publications/"
    _content_document: list[SPP_document]
    utc = pytz.UTC
    date_begin = utc.localize(datetime(2023, 10, 1))

    def __init__(self, webdriver, *args, **kwargs):
        """
        Конструктор класса парсера

        По умолчанию внего ничего не передается, но если требуется (например: driver селениума), то нужно будет
        заполнить конфигурацию
        """
        # Обнуление списка
        self._content_document = []

        self.driver = webdriver
        self.wait = WebDriverWait(self.driver, timeout=20)

        # Логер должен подключаться так. Вся настройка лежит на платформе
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(f"Parser class init completed")
        self.logger.info(f"Set source: {self.SOURCE_NAME}")
        ...

    def content(self) -> list[SPP_document]:
        """
        Главный метод парсера. Его будет вызывать платформа. Он вызывает метод _parse и возвращает список документов
        :return:
        :rtype:
        """
        self.logger.debug("Parse process start")
        self._parse()
        self.logger.debug("Parse process finished")
        return self._content_document

    def _parse(self):
        """
        Метод, занимающийся парсингом. Он добавляет в _content_document документы, которые получилось обработать
        :return:
        :rtype:
        """
        # HOST - это главная ссылка на источник, по которому будет "бегать" парсер
        self.logger.debug(F"Parser enter to {self.HOST}")

        # ========================================
        # Тут должен находится блок кода, отвечающий за парсинг конкретного источника
        # -

        self.driver.get("https://www.abe-eba.eu/publications/")  # Открыть страницу со списком RFC в браузере
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.publication')))
        el_list = self.driver.find_elements(By.XPATH, '//div[contains(@class, \'media-body\')]')
        # print(f'len(el_list) = {len(el_list)}')
        for el in el_list:
            links = el.find_elements(By.TAG_NAME, 'a')
            web_link = None
            for link in links:
                if link.get_attribute('href').endswith('.pdf'):
                    web_link = link.get_attribute('href')
                    break
            if web_link is None:
                self.logger.debug(f'pdf web link not found, skipping:\n{el.text}')

                continue
            try:
                abstract = el.find_element(By.TAG_NAME, 'h3').find_element(By.TAG_NAME, 'small').text
            except:
                abstract = ''
            title = el.find_element(By.TAG_NAME, 'h3').text.replace(abstract, '')
            pub_date = dateparser.parse(el.find_element(By.TAG_NAME, 'h6').text)
            document = SPP_document(
                None,
                title=title,
                abstract=abstract if abstract else None,
                text=None,
                web_link=web_link,
                local_link=None,
                other_data=None,
                pub_date=pub_date,
                load_date=None,
            )
            # Логирование найденного документа
            self.logger.info(self._find_document_text_for_logger(document))
            self._content_document.append(document)

        # ---
        # ========================================
        ...

    @staticmethod
    def _find_document_text_for_logger(doc: SPP_document):
        """
        Единый для всех парсеров метод, который подготовит на основе SPP_document строку для логера
        :param doc: Документ, полученный парсером во время своей работы
        :type doc:
        :return: Строка для логера на основе документа
        :rtype:
        """
        return f"Find document | name: {doc.title} | link to web: {doc.web_link} | publication date: {doc.pub_date}"

