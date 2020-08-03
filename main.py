from urllib import request
import urllib
import sys
import os
import re
import socket
import shutil
import hashlib
from time import sleep


def get_md5(str):
    return hashlib.md5(str.encode('utf-8')).hexdigest()


def del_file(filepath):
    """
    删除某一目录下的所有文件或文件夹
    """
    del_list = os.listdir(filepath)
    for f in del_list:
        file_path = os.path.join(filepath, f)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


def init_path(del_path, ret_path):
    """
    初始化目录
    """
    if not os.path.isdir(del_path):
        os.makedirs(del_path)
    del_file(del_path)

    if not os.path.isdir(ret_path):
        os.makedirs(ret_path)


class CatchVideo(object):
    def __init__(self, url):
        self.headers = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36"
        replace_regex = re.compile(r'index\d*\.ts')
        url, number = replace_regex.subn('index%d.ts', url)
        self.url = url
        self.path = url[0:url.rfind('/')+1]
        self.index_file = self.path + 'index.m3u8'
        self.start = 0
        self.end = 0
        self.download_path = os.getcwd() + '\\download\\'
        self.result_path = os.getcwd() + '\\av\\'
        self.url_md5 = get_md5(url)
        init_path(self.download_path, self.result_path)
        self.shell = 'cd ' + self.download_path + '&& copy /b ' + \
            '*.ts' + ' ' + self.url_md5 + '.ts && xcopy /y ' + \
            self.url_md5 + '.ts ' + self.result_path
        print(self.shell)

    def get_url(self, index):
        return self.url % index

    def download_file(self, url, filename):
        n = 5
        while n > 0:
            n -= 1
            try:
                rq = request.Request(url)
                rq.add_header('User-Agent', self.headers)
                response = request.urlopen(rq)
                resread = response.read()
                with open(self.download_path + filename, "wb") as f:
                    f.write(resread)
                response.close()
                break
            except urllib.error.URLError as e:
                print(e.reason)
                break
            except socket.timeout as e2:
                print(e2.reason)
        if n < 5:
            return True
        else:
            return False

    def do_download(self):
        result = self.download_file(self.index_file, 'index.m3u8')
        if result == False:
            return False
        else:
            result = self.parse_m3u8_file()
            if result == False:
                return False
            else:
                for index in range(self.start, self.end):
                    result = self.download_file(self.get_url(
                        index), 'index' + str(index + 1).zfill(6) + '.ts')
                    if result == False:
                        return True

    def parse_m3u8_file(self):
        try:
            f = open(self.download_path + 'index.m3u8', 'r', encoding='utf-8')
            text_list = f.readlines()
            files = []
            for i in text_list:
                if i.find('#EX') == -1:
                    files.append(i)
            f.close()
            length_file = len(files)
            self.end = length_file
            return True
        except Exception as e:
            return False

    def do_merge(self):
        print(os.system(self.shell))


if __name__ == '__main__':
    if 2 == len(sys.argv):
        catch_video = CatchVideo(sys.argv[1])
        socket.setdefaulttimeout(60)
        catch_video.do_download()
        catch_video.do_merge()
