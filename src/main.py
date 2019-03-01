import config, webbrowser, twitter, os, time, urllib, sqlite3
import oauth2 as oauth
import tkinter.ttk as ttk
from tkinter import *
from screeninfo import get_monitors
from PIL import Image, ImageTk

#twitter_access_token
def getOthToken():
    request_token_url = 'https://api.twitter.com/oauth/request_token'
    access_token_url = 'https://api.twitter.com/oauth/access_token'
    authorize_url = 'https://api.twitter.com/oauth/authorize'

    consumer = oauth.Consumer(CK, CS)
    client = oauth.Client(consumer)

    # Step 1: Get a request token. This is a temporary token that is used for
    # having the user authorize an access token and to sign the request to obtain
    # said access token.

    resp, content = client.request(request_token_url, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])

    request_token = dict(urllib.parse.parse_qsl(content))
    '''
    print(request_token)

    print("Request Token:")
    print("    - oauth_token        = %s" % request_token[b'oauth_token'])
    print("    - oauth_token_secret = %s" % request_token[b'oauth_token_secret'])
    print()
    '''

    # Step 2: Redirect to the provider. Since this is a CLI script we do not
    # redirect. In a web application you would redirect the user to the URL
    # below.

    #print("Go to the following link in your browser:")
    url = "%s?oauth_token=%s" % (
        authorize_url, request_token[b'oauth_token'].decode())
    webbrowser.open(url)
    #print(url)
    #print()

    # After the user has granted access to you, the consumer, the provider will
    # redirect you to whatever URL you have told them to redirect to. You can
    # usually define this in the oauth_callback argument as well.
    oauth_verifier = getPIN()
    athRoot.destroy()

    # Step 3: Once the consumer has redirected the user back to the oauth_callback
    # URL you can request the access token the user has approved. You use the
    # request token to sign this request. After this is done you throw away the
    # request token and use the access token returned. You should store this
    # access token somewhere safe, like a database, for future use.
    token = oauth.Token(request_token[b'oauth_token'],
    request_token[b'oauth_token_secret'])
    token.set_verifier(oauth_verifier)
    client = oauth.Client(consumer, token)

    resp, content = client.request(access_token_url, "POST")
    access_token = dict(urllib.parse.parse_qsl(content))
    '''
    print(access_token)

    print("Access Token:")
    print("    - oauth_token        = %s" % access_token[b'oauth_token'])
    print("    - oauth_token_secret = %s" % access_token[b'oauth_token_secret'])
    print()
    print("You may now access protected resources using the access tokens above.")
    print()
    '''
    #access_tokenをデータベースに保存
    dbname = 'access_token.db'
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    create_table = '''create table token (access_token varchar(64), access_token_secret varchar(64))'''
    try:
        c.execute(create_table)
    except sqlite3.OperationalError:
        pass
    sql = 'insert into token (access_token, access_token_secret) values (?, ?)'
    token = (access_token[b'oauth_token'], access_token[b'oauth_token_secret'])
    c.execute(sql, token)
    conn.commit()
    conn.close()

    return access_token

def getPIN():
    athLabel = Label(athRoot, text="認証画面で出るPINを入力してね").pack()
    athEntry = Entry(athRoot)
    athEntry.pack()
    athSubmit = Button(athRoot, text="決定", command=smtClicked).pack()
    athRoot.mainloop()
    return athEntry.get()

def smtClicked():
    athRoot.quit()

#display monitor size
def rtnDekGeometry():
    '''
    get_monitorsからは[monitor(WxH+X+Y)]という文字列+geometry形で出力されるので
    文字列へ置換を行い、geometry型へ整形する
    '''

    # 全モニタの情報を取得
    plainMonitorInfo = []
    for m in get_monitors():
        plainMonitorInfo.append(str(m))
        print(str(m))
    print(plainMonitorInfo)

    # geometry型に整形
    monitorInfo = []
    for m in plainMonitorInfo:
        m = m.replace('monitor(', '')
        m = m.replace(')', '')
        monitorInfo.append(m)
    print(monitorInfo)

    #dekSize = str(get_monitors())
    #dekStrSize = len(str(get_monitors()))
    #print(dekSize)
    #dekSize = dekSize[9:(dekStrSize - 2)]
    #dekSize = "1920x1080+0+0"
    return str(monitorInfo[0])

def rtnDekWidth():
    dekWidth = int(dekSize[0:4])
    return dekWidth

def rtnDekHeight():
    try:
        dekHeight58 = int(dekSize[5:8])
        dekHeight59 = int(dekSize[5:9])
    except ValueError:
        pass

    try:
        dekHeight = max(dekHeight58, dekHeight59)
    except UnboundLocalError:
        dekHeight = dekHeight58

    return int(dekHeight)

#setScrollList
def setList():
    srlListBox.delete(0, srlListBox.size())
    if lstNmeCmbBox.get() == "Follow":
        for j in range(15):
            print(j)
            if j == 0:
                lstFollow.append(api.GetFriendsPaged(screen_name=scrName))
            else:
                lstFollow.append(api.GetFriendsPaged(screen_name=scrName, cursor=lstFollow[j - 1][0]))
            if lstFollow[j][0] == 0:
                break
        for j in range(len(lstFollow)):
            for i in range(len(lstFollow[j][2])):
                try:
                    lstFollower.append(lstFollow[j][2][i].screen_name)
                except TypeError:
                    pass
        #print(len(lstFollower))
        #print(lstFollower)
        srlListBox.insert(END, *lstFollower)
        return
    listmembers = api.GetListMembers(slug=lstNmeCmbBox.get(), owner_screen_name=scrName)
    usrList = [u.screen_name for u in listmembers]
    srlListBox.insert(END, *usrList)

def callback(event):
    selectUser = srlListBox.get(srlListBox.nearest(event.y))
    print(selectUser)
    #if lstNmeCmbBox.get() != "Follow":
    chkLstMember(selectUser)
    getImgURL(selectUser)
    setImage()
    sctUser.clear()
    sctUser.append(selectUser)

#setImage
def download_image(url, dst_path):
    try:
        data = urllib.request.urlopen(url).read()
        with open(dst_path, mode="wb") as f:
            f.write(data)
    except urllib.error.URLError as e:
        print(e)
'''
def download_image(url, timeout = 10):
    response = requests.get(url, allow_redirects=False, timeout=timeout)
    if response.status_code != 200:
        e = Exception("HTTP status: " + response.status_code)
        raise e

    content_type = response.headers["content-type"]
    if 'image' not in content_type:
        e = Exception("Content-Type: " + content_type)
        raise e
    
    return response.content
'''

def getImgURL(usrName):
    urlList = api.GetUserTimeline(screen_name=usrName, count=200, include_rts=False)
    urls.clear()
    for i in range(len(urlList)):
        try:
            urls.append(urlList[i].media[0].media_url)
        except TypeError:
            pass
    dld4Image()
    strExtImage = '追加読み込み(後' + str(len(urls)) + '枚)'
    nxtImgButton.configure(text=strExtImage)

#4件だけ保存#
def dld4Image():
    download_dir = 'tmp'
    sleep_time_sec = 0.1
    passes.clear()

    try:
        os.mkdir("tmp")
    except FileExistsError:
        pass
    for i in range(len(urls)):
        filename = os.path.basename(urls[i])
        dst_path = os.path.join(download_dir, filename)
        time.sleep(sleep_time_sec)
        img = download_image(urls[i], dst_path)
        img = Image.open(dst_path, 'r')
        img.thumbnail((dekWdhQuote, dekWdhQuote))
        if img.mode != "RGB":
            try:
                img = img.convert("RGB")
                print("RGB converted")
            except IOError:
                print("Cannot converted")
        #canvas = Canvas(grdFrame, width=dekWdhQuote, height=dekWdhQuote, relief=RIDGE, bd=2, bg='red')
        #canvas.create_image(0, 0, image=img, anchor=NW)
        #print(canvas)
        #passes.append(ImageTk.PhotoImage(image=img))
        lstLabel = [Label(grdFrame, text=i, width=dekWdhQuote, height=dekWdhQuote, image=passes[i]).grid(row=(int)(i / 2), column=(i % 2), padx=2, pady=2, sticky=NE) for i in range(len(passes))]
        img.save(dst_path, 'JPEG', quality=100, optimize=True)
        passes.append(ImageTk.PhotoImage(file=dst_path))
        os.remove(dst_path)
        if i >= 3:
            break
    i = 0
    while i <= 3:
        try:
            urls.pop(0)
        except IndexError:
            pass
        i += 1
    print(urls)

#全部保存, 使わない#
def dldImage(urls):
    download_dir = 'tmp'
    sleep_time_sec = 1
    passes.clear()

    try:
        os.mkdir("tmp")
    except FileExistsError:
        pass
    for url in urls:
        filename = os.path.basename(url)
        dst_path = os.path.join(download_dir, filename)
        time.sleep(sleep_time_sec)
        download_image(url, dst_path)
        img = Image.open(dst_path, 'r')
        img.thumbnail((dekWdhQuote, dekWdhQuote))
        if img.mode != "RGB":
            try:
                img = img.convert("RGB")
                print("RGB converted")
            except IOError:
                print("Cannot converted")
        img.save(dst_path, 'JPEG', quality=100, optimize=True)
        passes.append(ImageTk.PhotoImage(file=dst_path))

def nxtImage():
    dld4Image()
    setImage()
    strExtImage = '追加読み込み(後' + str(len(urls)) + '枚)'
    nxtImgButton.configure(text=strExtImage)

def setImage():
    print(passes)
    lstLabel = [Label(grdFrame, text=i, width=dekWdhQuote, height=dekWdhQuote, image=passes[i]).grid(row=(int)(i / 2), column=(i % 2), padx=2, pady=2, sticky=NE) for i in range(len(passes))]

#リスト関連
#リストに入ってるかチェック#
def chkLstMember(selectUser):
    lstMmbShip = api.GetMemberships(screen_name=selectUser, filter_to_owned_lists=True)
    lstChecked = []
    for i in range(len(lstMmbShip)):
        try:
            lstChecked.append(lstMmbShip[i].slug)
        except TypeError:
            pass
    for i in range(len(ChkBoxList)):
        flgChkList[i].set(False)
        if i == (len(ChkBoxList) - 1):
            '''
            for k in range(len(lstFollower)):
                for j in range(len(usrList)):
                    print("lstFollower: " + str(lstFollower[k]) + " , usrList: " + usrList[j])
                    if lstFollower[k] == usrList[j]:
                        flgChkList[i].set(True)
            '''
            print("lstFollower: " + str(lstFollower))
            for j in range(len(lstFollower)):
                if lstFollower[j] == selectUser:
                    print("Yes")
                    flgChkList[i].set(True)
        else:
            for j in range(len(lstChecked)):
                if lstChecked[j] == ChkBoxList[i].cget("text"):
                    flgChkList[i].set(True)


#リストにぶち込む！#
def chkBtnCallBack(event):
    try:
        flgNumber = (int(str(event.widget)[21:23]) - 1)
        lstString = ChkBoxList[flgNumber].cget("text")
        if flgChkList[flgNumber].get() == False:
            print("Checkbutton[" + str(flgNumber) + "]がTrueになった!")
            print(lstString)
            print(scrName)
            print(sctUser[0])
            if lstString == "Follow":
                api.CreateFriendship(screen_name=sctUser[0], follow=False)
            else:
                api.CreateListsMember(slug=lstString, owner_screen_name=scrName, screen_name=sctUser[0])
        else:
            if lstString == "Follow":
                api.DestroyFriendship(screen_name=sctUser[0])
            else:
                api.CreateListsMember(slug=lstString, owner_screen_name=scrName, screen_name=sctUser[0])
    except ValueError:
        if flgChkList[0].get() == False:
            print("Checkbutton[" + str(0) + "]がTrueになった!")
            lstString = ChkBoxList[0].cget("text")
            print(lstString)
            print(scrName)
            print(sctUser[0])
            api.CreateListsMember(slug=lstString, owner_screen_name=scrName, screen_name=sctUser[0])
        else:
            api.DestroyListsMember(slug=lstString, owner_screen_name=scrName, screen_name=sctUser[0])

#twitterAuth
CK = config.CONSUMER_KEY
CS = config.CONSUMER_SECRET

#access_tokenをデータベースにから取り出す
dbname = 'access_token.db'
conn = sqlite3.connect(dbname)
try:
    c = conn.cursor()
    sql = 'select * from token'
    for sqlResult in c.execute(sql):
        pass
    AT = sqlResult[0].decode()
    ATS = sqlResult[1].decode()
    print("access_tokenある！")
except sqlite3.OperationalError:
    athRoot = Tk()
    athRoot.geometry("200x200+500+200")
    access_token = getOthToken()
    AT = access_token[b'oauth_token'].decode()
    ATS = access_token[b'oauth_token_secret'].decode()
    print("access_tokenない！")
conn.close()

#twitterAPI
passes = []

api = twitter.Api(CK, CS, AT, ATS)
scrName = api.VerifyCredentials().screen_name

lists = api.GetLists(screen_name=scrName)
lists = [l.name for l in lists]
lists.append("Follow")

usrList = []
try:
    listmembers = api.GetListMembers(slug=lists[0], owner_screen_name=scrName)
    usrList = [u.screen_name for u in listmembers]
except twitter.error.TwitterError:
    pass

#mainLoop
root = Tk()
root.option_add('*font', ('FixedSys', 14))
root.title('My First App')
dekSize = rtnDekGeometry()
root.geometry(dekSize)
root.state('zoomed')
dekWdhQuote = int(rtnDekWidth() / 4)
dekWdhHarf = int(rtnDekWidth() / 2)
dekFulHeight = rtnDekHeight()

#frame
frame1 = Frame(root, width = dekWdhQuote, height = dekFulHeight, bg = 'blue')
frame2 = Frame(root, width = dekWdhHarf, height = dekFulHeight, bg = 'red')
frame3 = Frame(root, width = dekWdhQuote, height = dekFulHeight, bg = 'yellow')
frame1.place(relx=0.0, rely=0.0)
frame2.place(relx=0.25, rely=0.0)
frame3.place(relx=0.75, rely=0.0)

#users_tab
urls = []
sctUser = []
lstFollow = []
lstFollower = []
listString = StringVar()
la = Label(frame1, text='リストメンバー', bg='yellow', relief=RIDGE, bd=2)
la.place(relx=0.0, rely=0.0)
lstNmeLabel = Label(frame1, text='リスト名:')
lstNmeLabel.place(relx=0.0, rely=0.03)
lstName = StringVar()
lstNmeCmbBox = ttk.Combobox(frame1, textvariable=lstName, width=27)
lstNmeCmbBox["values"] = lists
lstNmeCmbBox.place(relx=0.2, rely=0.03)
lstNmeSubmit = Button(frame1, text='設定', command=setList)
lstNmeSubmit.place(relx=0.85, rely=0.025)
srlListBox = Listbox(frame1, width=47, height=39)
srlListBox.insert(END, *usrList)
srlListBox.bind("<Button-1>", callback)
srlListBox.place(relx=0.0, rely=0.06)

#images_tab
lb = Label(frame2, text='画像', bg='yellow', relief=RIDGE, bd=2)
lb.place(relx=0.0, rely=0.0)
strExtImage = '追加読み込み(後' + str(len(urls)) + '枚)'
nxtImgButton = Button(frame2, text=strExtImage, command=nxtImage)
nxtImgButton.place(relx=0.1, rely=0.0)
grdFrame = Frame(frame2, width = dekWdhHarf, height = dekFulHeight, bg = 'white')
grdFrame.place(relx=0.0, rely=0.03)
lstLabel = setImage()

#lists_tab
lc = Label(frame3, text='リスト一覧', bg='yellow', relief=RIDGE, bd=2)
lc.place(relx=0.0, rely=0.0)
flgChkList = [BooleanVar() for i in range(len(lists))]
ChkBoxList = [Checkbutton(frame3, text=lists[n], variable=flgChkList[n]) for n in range(len(lists))]
for n in range(len(ChkBoxList)):
    flgChkList[n].set(False)
    ChkBoxList[n].bind("<Button-1>", chkBtnCallBack)
    ChkBoxList[n].place(relx=0.0, rely=(0.03 + 0.03 * n))
root.mainloop()
