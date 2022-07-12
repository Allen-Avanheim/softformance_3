import re
from os import path, mkdir, listdir, remove, system

try:
    import aspose.words as aw
    import requests
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    system('pip install -r requirements.txt')
    import aspose.words as aw
    import requests
    from bs4 import BeautifulSoup


class WebCrawler:
    """
    The Web crawler, which will recursively walk
    over the website and download all images from
    its pages and then convert it all into one single format
    """

    def __init__(self, url_init: str) -> None:
        self.__site = url_init
        self.__directory_name = 'img'

    def __create_directory(self) -> None:
        if not path.exists(self.__directory_name):
            mkdir(self.__directory_name)

    def convert_all_images_to_png(self) -> None:
        files = listdir(self.__directory_name)
        for file in files:
            file_name, file_extension = self.__find_file_name_and_extension(file)
            if file_extension != 'png':
                self.__format_to_png(file_name, file_extension)

    @staticmethod
    def __find_file_name_and_extension(file: str) -> tuple:
        dot_position = file.rfind('.')
        file_name = file[:dot_position]
        file_extension = file[dot_position + 1:]
        return file_name, file_extension

    def __format_to_png(self, name: str, extension: str) -> None:
        doc = aw.Document()
        builder = aw.DocumentBuilder(doc)

        old_path = f"{self.__directory_name}\\{name}.{extension}"
        new_path = f"{self.__directory_name}\\{name}.png"

        shape = builder.insert_image(old_path)
        shape.image_data.save(new_path)

        self.__delete_file(old_path)

    @staticmethod
    def __delete_file(path_for_deleting: str) -> None:
        remove(path_for_deleting)

    def __find_images(self) -> tuple:
        response = requests.get(self.__site)
        soup = BeautifulSoup(response.text, 'html.parser')
        image_tags = tuple(soup.find_all('img'))
        urls = self.__find_urls(image_tags)
        return self.__format_url_list(urls)

    @staticmethod
    def __find_urls(image_tags: tuple) -> tuple:
        urls = []
        sources = ('src', 'data-src', 'data-srcset')
        for img in image_tags:
            counter = 0
            while counter < 3:
                try:
                    if counter == 2:
                        urls.extend(img[sources[counter]].split(','))
                    else:
                        urls.append(img[sources[counter]])
                except KeyError:
                    pass
                finally:
                    counter += 1
        return tuple(urls)

    @staticmethod
    def __format_url_list(url_list: tuple) -> tuple:
        return tuple(map(lambda url: url.
                         replace(' 1x', '').
                         replace(' 2x', '').
                         replace(' 3x', '').
                         strip(), url_list))

    def __download_img(self, path_for_download: str, url: str) -> None:
        with open(path_for_download, 'wb') as f:
            if 'http' not in url:
                url = f'{self.__site}{url}'
            response = requests.get(url)
            f.write(response.content)
            img_name = path_for_download.split('\\')[1]
            print(f'Downloading {img_name}...')

    def download_all_images(self) -> None:
        self.__create_directory()
        urls = self.__find_images()
        for url in urls:
            filename = re.search(r'/([\w_-]+[.](jpg|jpeg|gif|png|svg))$', url)
            if filename:
                path_for_download = self.__directory_name + "\\" + filename.group(1)
                self.__download_img(path_for_download, url)


if __name__ == "__main__":
    url_of_site = 'https://www.softformance.com/'
    web_crawler = WebCrawler(url_of_site)
    web_crawler.download_all_images()
    web_crawler.convert_all_images_to_png()
