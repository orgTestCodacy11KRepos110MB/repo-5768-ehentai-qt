import re

from bs4 import BeautifulSoup, Tag


class BookBaseInfo(object):
    def __init__(self):
        self.id = 0
        self.title = ""
        self.bookUrl = ""
        self.token = ""       # 收藏和下载使用
        self.apiUid = ""      # TODO
        self.apiKey = ""      # TODO
        self.category = ""
        self.timeStr = ""
        self.imgData = None
        self.imgUrl = ""
        self.tags = []


class BookPageInfo(object):
    def __init__(self):
        self.kv = {}
        self.pages = 0
        self.picUrl = {}
        self.comment = []


class BookInfo(object):
    def __init__(self):
        self.baseInfo = BookBaseInfo()
        self.pageInfo = BookPageInfo()


def ParseBookInfo(data):
    soup = BeautifulSoup(data, features="lxml")
    tag = soup.find("div", id="gdd")
    table = tag.find("table")
    book = BookInfo()
    info = book.pageInfo
    for tr in table.find_all("tr"):
        key = tr.find("td", class_="gdt1").text.replace(":", "")
        value = tr.find("td", class_="gdt2").text
        info.kv[key] = value
    info.posted = info.kv.get("Posted")
    info.language = info.kv.get("Language")
    info.fileSize = info.kv.get("File Size")
    mo = re.search(r'\d+', info.kv.get("Length"))
    if mo:
        info.pages = int(mo.group())
    mo = re.search(r"\d+", info.kv.get("Favorited", ""))
    if mo:
        info.favorites = int(mo.group())

    for tag in soup.find_all("div", class_="gdtm"):
        url = tag.a.attrs.get('href')
        index = int(tag.a.img.attrs.get('alt'))
        info.picUrl[index] = url
    table = soup.find("table", class_="ptt")
    maxPage = 1
    for td in table.tr.children:
        if getattr(td, "a", None):
            pages = td.a.text
            datas = re.findall(r"\d+", pages)
            if not datas:
                continue
            maxPage = max(maxPage, int(datas[0]))

    comment = soup.find("div", id="cdiv")
    for tag in comment.find_all("div", class_="c1"):
        times = tag.find("div", class_="c3").text
        data = tag.find("div", class_="c6").text
        info.comment.append([times, data])
    base = book.baseInfo
    data = soup.find_all("script", {'type': "text/javascript"})
    mo = re.search("(?<=var gid =\s)\d+", data[1].next)
    base.id = mo.group()
    mo = re.search("(?<=var token = \")\w+", data[1].next)
    base.token = mo.group()
    mo = re.search("(?<=var apiuid =\s)\d+", data[1].next)
    base.apiuid = mo.group()
    mo = re.search("(?<=var apikey = \")\w+", data[1].next)
    base.apikey = mo.group()
    mo = re.search("(?<=var average_rating =\s)\d+(.\d+)", data[1].next)
    base.average_rating = mo.group()
    mo = re.search("(?<=var display_rating =\s)\d+(.\d+)", data[1].next)
    base.display_rating = mo.group()
    tag = soup.find("div", id="gdc")
    base.category = tag.text.replace("\n", "")
    tag = soup.find("h1", id="gn")
    base.title = tag.text
    tag = soup.find("div", id="gd1")
    base.imgUrl = re.search("(?<=url\()\S*(?=\))", tag.div.attrs.get("style")).group()

    table = soup.find("div", id="taglist")
    for tc in table.find_all("td", class_="tc"):
        print(tc.text)
        td = tc.find_next_sibling()
        if td:
            for div in td.find_all("div"):
                base.tags.append(tc.text+div.text)
    return book, maxPage

def ParseBookInfo1(data):
    soup = BeautifulSoup(data, features="lxml")
    tag = soup.find("div", id="gdd")
    table = tag.find("table")
    from src.book.book import BookPageInfo
    info = BookPageInfo()
    for tr in table.find_all("tr"):
        key = tr.find("td", class_="gdt1").text.replace(":", "")
        value = tr.find("td", class_="gdt2").text
        info.kv[key] = value
    info.posted = info.kv.get("Posted")
    info.language = info.kv.get("Language")
    info.fileSize = info.kv.get("File Size")
    mo = re.search(r'\d+', info.kv.get("Length"))
    if mo:
        info.pages = int(mo.group())
    for tag in soup.find_all("div", class_="gdtm"):
        url = tag.a.attrs.get('href')
        index = int(tag.a.img.attrs.get('alt'))
        info.picUrl[index] = url
    table = soup.find("table", class_="ptt")
    maxPage = 1
    for td in table.tr.children:
        if getattr(td, "a", None):
            pages = td.a.text
            datas = re.findall(r"\d+", pages)
            if not datas:
                continue
            maxPage = max(maxPage, int(datas[0]))

    comment = soup.find("div", id="cdiv")
    for tag in comment.find_all("div", class_="c1"):
        times = tag.find("div", class_="c3").text
        data = tag.find("div", class_="c6").text
        info.comment.append([times, data])
    return info, maxPage

def ParsePictureInfo(data):
    soup = BeautifulSoup(data, features="lxml")
    tag = soup.find("div", id="gdd")
    table = tag.find("table")
    for tr in table.find_all("tr"):
        key = tr.find("td", class_="gdt1").text.replace(":", "")
        value = tr.find("td", class_="gdt2").text
    for tag in soup.find_all("div", class_="gdtm"):
        url = tag.a.attrs.get('href')
        index = int(tag.a.img.attrs.get('alt'))

    table = soup.find("table", class_="ptt")
    maxPage = 1
    for td in table.tr.children:
        if getattr(td, "a", None):
            pages = td.a.text
            datas = re.findall(r"\d+", pages)
            if not datas:
                continue
            maxPage = max(maxPage, int(datas[0]))
    comment = soup.find("div", id="cdiv")
    for tag in comment.find_all("div", class_="c1"):
        times = tag.find("div", class_="c3").text
        data = tag.find("div", class_="c6").text



def ParseImgInfo(data):
    soup = BeautifulSoup(data, features="lxml")
    tag = soup.find("div", id="i3")
    imgUrl = tag.a.img.attrs.get("src")
    mo = re.search("(?<=showkey)(\s*=\s*\")\w+", "; var showkey = \"n1efkp39mtk\";")
    imgKey = mo.group().replace("\"", "").replace("=", "").replace(" ", "")
    return


def ParseImgInfo2(data):
    # soup = BeautifulSoup(data, features="lxml")
    # tag = soup.find("div", id="i3")
    # imgUrl = tag.a.img.attrs.get("src")
    # mo = re.search("(?<=showkey)(\s*=\s*\")\w+", "; var showkey = \"n1efkp39mtk\";")
    # imgKey = mo.group().replace("\"", "").replace("=", "").replace(" ", "")
    tag = data.get('i3')
    mo = re.search("(?<=src=\")\S+\"", tag)
    imgUrl = mo.group().replace("\\/", "/").replace("\"", "")
    return


def ParseFavorite(data):
    soup = BeautifulSoup(data, features="lxml")
    table = soup.find_all("div", class_="fp")
    favorite = {}
    isUpdate = False
    for index, tr in enumerate(table):
        count = 0
        for tag in tr.children:
            if isinstance(tag, Tag):
                if len(tag.attrs) == 1 and tag.attrs.get("style"):
                    mo = re.search(r"\d+", tag.text)
                    if mo:
                        count = int(mo.group())
                        break

        favorite[index] = count
    return favorite

def ParseHomeInfo(data):
    soup = BeautifulSoup(data, features="lxml")
    tag = soup.find("div", class_="homebox")
    print(tag.text)
    mo = re.search("(?<=You are currently at\s)\d*", tag.text)
    curNum = 0
    if mo:
        curNum = int(mo.group())
    mo = re.search("(?<=towards a limit of\s)\d*", tag.text)
    maxNum = 0
    if mo:
        maxNum = int(mo.group())
    return curNum, maxNum

def ParseAddFavorite(data):
    soup = BeautifulSoup(data, features="lxml")
    tag = soup.find("textarea")
    note = tag.text
    table = soup.find_all("input")
    favorite = {}
    isUpdate = False
    for tr in table:
        if tr.attrs.get("type") == "radio":
            favorite[tr.attrs.get("value")] = tr.attrs.get("checked") == "checked"
        elif tr.attrs.get("type") == "submit":
            if tr.attrs.get("value") == "Apply Changes":
                isUpdate = True
    return note, favorite, isUpdate

def ParseLoginUserName(data):
    soup = BeautifulSoup(data, features="lxml")
    table = soup.find("div", id="userlinks")
    if not table:
        return "", ""
    tag = table.find("a")
    if not tag:
        return "", ""
    name = tag.text
    userId = "", ""
    mo = re.search("(?<=showuser=)\w+", tag.attrs.get("href", ""))
    if mo:
        userId = mo.group()
    return userId, name

if __name__ == "__main__":
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "zh-CN,zh;q=0.9,ja;q=0.8",
    }
    # r = requests.get("https://e-hentai.org", proxies={"https": "http://127.0.0.1:10809"})
    # r = requests.get("https://e-hentai.org", proxies={"https": "http://127.0.0.1:10809"})
    # data = {"p":3,"s":"s\/286edf5f6a\/1886873-3","n":"<div class=\"sn\"><a onclick=\"return load_image(1, '97316d4642')\" href=\"https:\/\/e-hentai.org\/s\/97316d4642\/1886873-1\"><img src=\"https:\/\/ehgt.org\/g\/f.png\" \/><\/a><a id=\"prev\" onclick=\"return load_image(2, '052d8a4730')\" href=\"https:\/\/e-hentai.org\/s\/052d8a4730\/1886873-2\"><img src=\"https:\/\/ehgt.org\/g\/p.png\" \/><\/a><div><span>3<\/span> \/ <span>52<\/span><\/div><a id=\"next\" onclick=\"return load_image(4, 'db30a6df2a')\" href=\"https:\/\/e-hentai.org\/s\/db30a6df2a\/1886873-4\"><img src=\"https:\/\/ehgt.org\/g\/n.png\" \/><\/a><a onclick=\"return load_image(52, '2b55577f5f')\" href=\"https:\/\/e-hentai.org\/s\/2b55577f5f\/1886873-52\"><img src=\"https:\/\/ehgt.org\/g\/l.png\" \/><\/a><\/div>","i":"<div>87570749_p0.jpg :: 1280 x 1868 :: 275.3 KB<\/div>","k":"286edf5f6a","i3":"<a onclick=\"return load_image(4, 'db30a6df2a')\" href=\"https:\/\/e-hentai.org\/s\/db30a6df2a\/1886873-4\"><img id=\"img\" src=\"https:\/\/bahkojr.xmgymbdvpsjz.hath.network:60000\/h\/846ecb60b17f755063916a26c238535975a710f7-281958-1280-1868-jpg\/keystamp=1618130700-04778f9774;fileindex=89518293;xres=1280\/87570749_p0.jpg\" style=\"height:1868px;width:1280px\" onerror=\"this.onerror=null; nl('26561-449480')\" \/><\/a>","i5":"<div class=\"sb\"><a href=\"https:\/\/e-hentai.org\/g\/1886873\/50f0a88e47\/\"><img src=\"https:\/\/ehgt.org\/g\/b.png\" referrerpolicy=\"no-referrer\" \/><\/a><\/div>","i6":" &nbsp; <img src=\"https:\/\/ehgt.org\/g\/mr.gif\" class=\"mr\" \/> <a href=\"https:\/\/e-hentai.org\/?f_shash=286edf5f6a9d5e0dbef1ea8a9f632bf83aaba7ca&amp;fs_from=87570749_p0.jpg+from+%5BPixiv%5D+sy4+%2834274728%29\">Show all galleries with this file<\/a>  &nbsp; <img src=\"https:\/\/ehgt.org\/g\/mr.gif\" class=\"mr\" \/> <a href=\"#\" onclick=\"prompt('Copy the URL below.', 'https:\/\/e-hentai.org\/r\/846ecb60b17f755063916a26c238535975a710f7-281958-1280-1868-jpg\/forumtoken\/1886873-3\/87570749_p0.jpg'); return false\">Generate a static forum image link<\/a>  &nbsp; <img src=\"https:\/\/ehgt.org\/g\/mr.gif\" class=\"mr\" \/> <a href=\"#\" id=\"loadfail\" onclick=\"return nl('26561-449480')\">Click here if the image fails loading<\/a> ","i7":" &nbsp; <img src=\"https:\/\/ehgt.org\/g\/mr.gif\" class=\"mr\" \/> <a href=\"https:\/\/e-hentai.org\/fullimg.php?gid=1886873&amp;page=3&amp;key=8dzvg9z9mtk\">Download original 2404 x 3508 5.99 MB source<\/a>","si":26561,"x":"1280","y":"1868"}
    f = open("book_info.html", "rb")
    data = f.read()
    f.close()
    ParseBookInfo(data)
    print()
    pass