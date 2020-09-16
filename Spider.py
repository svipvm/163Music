import requests
from lxml import etree
import csv
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0'
}
base_path = os.getcwd()

def getModulesByURL(url):
    try:
        html = requests.get(url, headers=headers).content.decode()
        html = etree.HTML(html)
        songModules = html.xpath('//ul[@id="m-song-module"]')[0]
        artistName = html.xpath('//h2[@id="artist-name"]/text()')[0]
        titles = songModules.xpath('./li/p[@class="dec dec-1 f-thide2 f-pre"]/@title')
        hrefs = songModules.xpath('./li/p[@class="dec dec-1 f-thide2 f-pre"]/a/@href')
        times = songModules.xpath('.//span[@class="s-fc3"]/text()')
        hrefs = ['https://music.163.com' + href for href in hrefs]
        with open(base_path + '\\Modules.csv', 'a', newline='', encoding='utf-8') as f:
            file = csv.writer(f)
            for i in range(0, len(titles)):
                file.writerow([titles[i], hrefs[i], times[i]])
        return artistName, titles, hrefs, times
    except:
        return None

def getMusic(path, url):
    try:
        url = 'http://music.163.com/song/media/outer/url?id={}.mp3'.format(url.split('=')[1])
        with open(path, 'bw') as f:
            content = requests.get(url, headers=headers).content
            f.write(content)
    except:
        return None

def solveModule(artistName, path, url):
    try:
        html = requests.get(url, headers=headers).content.decode()
        html = etree.HTML(html)
        content = html.xpath('//meta[@property="og:music:album:song"]/@content')
        titles = [elem.split(';')[0].split("=")[1] for elem in content]
        href = [elem.split(';')[1].split("=", 1)[1] for elem in content]
        for index in range(0, len(titles)):
            nowPath = path + "\\" + titles[index].replace(' ', '') + '.mp3'
            print('正在处理歌曲：' + titles[index] + " \n\tURL：" + href[index])
            getMusic(nowPath, href[index])
            with open(base_path + '\\MusicList.csv', 'a', newline='', encoding='utf-8') as f:
                file = csv.writer(f)
                file.writerow([artistName, path.split('\\')[-1], titles[index]])
    except:
        return None


def main():
    global base_path
    id = input('请输入歌手ID：')
    url = 'https://music.163.com/artist/album?id={}&limit=12&offset='.format(id)
    base_path += '\\' + id
    if os.path.exists(base_path) == False:
        os.mkdir(base_path)
    with open(base_path + '\\Modules.csv', 'w', newline='', encoding='utf-8') as f:
        file = csv.writer(f)
        file.writerow(['专辑', '链接', '时间'])
    with open(base_path + '\\MusicList.csv', 'w', newline='', encoding='utf-8') as f:
        file = csv.writer(f)
        file.writerow(['歌手', '专辑', '歌曲'])
    for page in range(0, 500, 12):
        artistName, titles, hrefs, times = getModulesByURL(url + str(page))
        for index in range(0, len(titles)):
            path = base_path + '\\' + titles[index].replace(' ', '')
            if os.path.exists(path) == False:
                os.mkdir(path)
            print('-------------------- {} 专辑 {} --------------------'.format(artistName, titles[index]))
            solveModule(artistName, path, hrefs[index])
        if len(titles) < 12: break

if __name__ == '__main__':
    main()
    print('欢迎下次使用！')
