#coding=utf8

import random
import urllib
import urllib2
import time
import sys
import pprint
import pylibmc as memcache
import json

#import memcache
#import json
global test_userid
#test_userid = 169

#test_uid = [22911L, 22921L, 22931L, 22941L, 22951L, 22961L, 22971L, 22981L, 22991L, 23001L, 23011L, 23021L, 23031L, 23041L, 23051L, 23061L, 23071L, 23081L, 23091L, 23101L, 23111L, 23121L, 23131L, 23141L, 23151L, 23161L, 23171L, 23181L, 23191L, 23201L, 23211L, 23221L, 23231L, 23241L, 23251L, 23261L, 23271L, 23281L, 23291L, 23301L, 23311L, 23321L, 23331L, 23341L, 23351L, 23361L, 23371L, 23381L, 23391L, 23401L, 23411L, 23421L, 23431L, 23441L, 23451L, 23461L, 23471L, 23481L, 23491L, 23501L, 23511L, 23521L, 23531L, 23541L, 23551L, 23561L, 23571L, 23581L, 23591L, 23601L, 23611L, 23621L, 23631L, 23641L, 23651L, 23661L, 23671L, 23681L, 23691L, 23701L, 23711L, 23721L, 23731L, 23741L, 23751L, 23761L, 23771L, 23781L, 23791L, 23801L, 23811L, 23821L, 23831L, 23841L, 23851L, 23861L, 23871L, 23881L, 23891L, 23901L, 23911L, 23921L, 23931L, 23941L, 23951L, 23961L, 23971L, 23981L, 23991L, 24001L, 24011L, 24021L, 24031L, 24041L, 24051L, 24061L, 24071L, 24081L, 24091L, 24101L, 24111L, 24121L, 24131L, 24141L, 24151L, 24161L, 24171L, 24181L, 24191L, 24201L, 24211L, 24221L, 24231L, 24241L, 24251L, 24261L, 24271L, 24281L, 24291L, 24301L, 24311L, 24321L, 24331L, 24341L, 24351L, 24361L, 24371L, 24381L, 24391L, 24401L, 24411L, 24421L, 24431L, 24441L, 24451L, 24461L, 24471L, 24481L, 24491L, 24501L, 24511L, 24521L, 24531L, 24541L, 24551L, 24561L, 24571L, 24581L, 24591L, 24601L, 24611L, 24621L, 24631L, 24641L, 24651L, 24661L, 24671L, 24681L, 24691L, 24701L, 24711L, 24721L, 24731L, 24741L, 24751L, 24761L, 24771L, 24781L, 24791L, 24801L, 24811L, 24821L, 24831L, 24841L, 24851L, 24861L, 24871L, 24881L, 24891L, 24901L, 24911L, 24921L, 24931L, 24941L, 24951L, 24961L, 24971L, 24981L, 24991L, 25001L, 25011L, 25021L, 25031L, 25041L, 25051L, 25061L, 25071L, 25081L, 25091L, 25101L, 25111L, 25121L, 25131L, 25141L, 25151L, 25161L, 25171L]


test_uid = [32261, 32271, 32281, 32291, 32301, 32311, 32321, 32331, 32341, 32351, 32361, 32371, 32381, 32391, 32401, 32411, 32421, 32431, 32441, 32451, 32461, 32471, 32481, 32491, 32501, 32511, 32521, 32531, 32541, 32551, 32561, 32571, 32581, 32591, 32601, 32611, 32621, 32631, 32641, 32651, 32661, 32671, 32681, 32691, 32701, 32711, 32721, 32731, 32741, 32751, 32761, 32771, 32781, 32791, 32801, 32811, 32821, 32831, 32841, 32851, 32861, 32871, 32881, 32891, 32901, 32911, 32921, 32931, 32941, 32951, 32961, 32971, 32981, 32991, 33001, 33011, 33021, 33031, 33041, 33051, 33061, 33071, 33081, 33091, 33101, 33111, 33121, 33131, 33141, 33151, 33161, 33171, 33181, 33191, 33201, 33211, 33221, 33231, 33241, 33251, 33261, 33271, 33281, 33291, 33301, 33311, 33321, 33331, 33341, 33351, 33361, 33371, 33381, 33391, 33401, 33411, 33421, 33431, 33441, 33451, 33461, 33471, 33481, 33491, 33501, 33511, 33521, 33531, 33541, 33551, 33561, 33571, 33581, 33591, 33601, 33611, 33621, 33631, 33641, 33651, 33661, 33671, 33681, 33691, 33701, 33711, 33721, 33731, 33741, 33751, 33761, 33771, 33781, 33791, 33801, 33811, 33821, 33831, 33841, 33851, 33861, 33871, 33881, 33891, 33901, 33911, 33921, 33931, 33941, 33951, 33961, 33971, 33981, 33991, 34001, 34011, 34021, 34031, 34041, 34051, 34061, 34071, 34081, 34091, 34101, 34111, 34121, 34131, 34141, 34151, 34161, 34171, 34181, 34191, 34201, 34211, 34221, 34231, 34241, 34251, 34261, 34271, 34281, 34291, 34301, 34311, 34321, 34331, 34341, 34351, 34361, 34371, 34381, 34391, 34401, 34411, 34421, 34431, 34441, 34451, 34461, 34471, 34481, 34491, 34501, 34511, 34521, 34531, 34541, 34551, 34561, 34571, 34581, 34591, 34601, 34611, 34621, 34631, 34641, 34651, 34661, 34671, 34681, 34691, 34701, 34711, 34721, 34731, 34741, 34751, 34761, 34771, 34781, 34791, 34801, 34811, 34821, 34831, 34841, 34851, 34861, 34871, 34881, 34891, 34901, 34911, 34921, 34931, 34941, 34951, 34961, 34971, 34981, 34991, 35001, 35011, 35021, 35031, 35041, 35051, 35061, 35071, 35081, 35091, 35101, 35111, 35121, 35131, 35141, 35151, 35161, 35171, 35181, 35191, 35201, 35211, 35221, 35231, 35241, 35251, 35261, 35271, 35281, 35291, 35301, 35311, 35321, 35331, 35341, 35351, 35361, 35371, 35381, 35391, 35401, 35411, 35421, 35431, 35441, 35451, 35461, 35471, 35481, 35491, 35501, 35511, 35521, 35531, 35541, 35551, 35561, 35571, 35581, 35591, 35601, 35611, 35621, 35631, 35641, 35651, 35661, 35671, 35681, 35691, 35701, 35711, 35721, 35731, 35741, 35751, 35761, 35771, 35781, 35791, 35801, 35811, 35821, 35831, 35841, 35851, 35861, 35871, 35881, 35891, 35901, 35911, 35921, 35931, 35941, 35951, 35961, 35971, 35981, 35991, 36001, 36011, 36021, 36031, 36041, 36051, 36061, 36071, 36081, 36091, 36101, 36111, 36121, 36131, 36141, 36151, 36161, 36171, 36181, 36191, 36201, 36211, 36221, 36231, 36241, 36251, 36261, 36271, 36281, 36291, 36301, 36311, 36321, 36331, 36341, 36351, 36361, 36371, 36381, 36391, 36401, 36411, 36421, 36431, 36441, 36451, 36461, 36471, 36481, 36491, 36501, 36511, 36521, 36531, 36541, 36551, 36561, 36571, 36581, 36591, 36601, 36611, 36621, 36631, 36641, 36651, 36661, 36671, 36681, 36691, 36701, 36711, 36721, 36731, 36741, 36751, 36761, 36771, 36781, 36791, 36801, 36811, 36821, 36831, 36841, 36851, 36861, 36871, 36881, 36891, 36901, 36911, 36921, 36931, 36941, 36951, 36961, 36971, 36981, 36991, 37001, 37011, 37021, 37031, 37041, 37051, 37061, 37071, 37081, 37091, 37101, 37111, 37121, 37131, 37141, 37151, 37161, 37171, 37181, 37191, 37201, 37211, 37221, 37231, 37241, 37251, 37261, 37271, 37281, 37291, 37301, 37311, 37321, 37331, 37341, 37351, 37361, 37371, 37381, 37391, 37401, 37411, 37421, 37431, 37441, 37451, 37461, 37471, 37481, 37491, 37501, 37511, 37521, 37531, 37541, 37551, 37561, 37571, 37581, 37591, 37601, 37611, 37621, 37631, 37641, 37651, 37661, 37671, 37681, 37691, 37701, 37711, 37721, 37731, 37741, 37751, 37761, 37771, 37781, 37791, 37801, 37811, 37821, 37831, 37841, 37851, 37861, 37871, 37881, 37891, 37901, 37911, 37921, 37931, 37941, 37951, 37961, 37971, 37981, 37991, 38001, 38011, 38021, 38031, 38041, 38051, 38061, 38071, 38081, 38091, 38101, 38111, 38121, 38131, 38141, 38151, 38161, 38171, 38181, 38191, 38201, 38211, 38221, 38231, 38241, 38251, 38261, 38271, 38281, 38291, 38301, 38311, 38321, 38331, 38341, 38351, 38361, 38371, 38381, 38391, 38401, 38411, 38421, 38431, 38441, 38451, 38461, 38471, 38481, 38491, 38501, 38511, 38521, 38531, 38541, 38551, 38561, 38571, 38581, 38591, 38601, 38611, 38621, 38631, 38641, 38651, 38661, 38671, 38681, 38691, 38701, 38711, 38721, 38731, 38741, 38751, 38761, 38771, 38781, 38791, 38801, 38811, 38821, 38831, 38841, 38851, 38861, 38871, 38881, 38891, 38901, 38911, 38921, 38931, 38941, 38951, 38961, 38971, 38981, 38991, 39001, 39011, 39021, 39031, 39041, 39051, 39061, 39071, 39081, 39091, 39101, 39111, 39121, 39131, 39141, 39151, 39161, 39171, 39181, 39191, 39201, 39211, 39221, 39231, 39241, 39251, 39261, 39271, 39281, 39291, 39301, 39311, 39321, 39331, 39341, 39351, 39361, 39371, 39381, 39391, 39401, 39411, 39421, 39431, 39441, 39451, 39461, 39471, 39481, 39491, 39501, 39511, 39521, 39531, 39541, 39551, 39561, 39571, 39581, 39591, 39601, 39611, 39621, 39631, 39641, 39651, 39661, 39671, 39681, 39691, 39701, 39711, 39721, 39731, 39741, 39751, 39761, 39771, 39781, 39791, 39801, 39811, 39821, 39831, 39841, 39851, 39861, 39871, 39881, 39891, 39901, 39911, 39921, 39931, 39941, 39951, 39961, 39971, 39981, 39991, 40001, 40011, 40021, 40031, 40041, 40051, 40061, 40071, 40081, 40091, 40101, 40111, 40121, 40131, 40141, 40151, 40161, 40171, 40181, 40191, 40201, 40211, 40221, 40231, 40241, 40251, 40261, 40271, 40281, 40291, 40301, 40311, 40321, 40331, 40341, 40351, 40361, 40371, 40381, 40391, 40401, 40411, 40421, 40431, 40441, 40451, 40461, 40471, 40481, 40491, 40501, 40511, 40521, 40531, 40541, 40551, 40561, 40571, 40581, 40591, 40601, 40611, 40621, 40631, 40641, 40651, 40661, 40671, 40681, 40691, 40701, 40711, 40721, 40731, 40741, 40751, 40761, 40771, 40781, 40791, 40801, 40811, 40821, 40831, 40841, 40851, 40861, 40871, 40881, 40891, 40901, 40911, 40921, 40931, 40941, 40951, 40961, 40971, 40981, 40991, 41001, 41011, 41021, 41031, 41041, 41051, 41061, 41071, 41081, 41091, 41101, 41111, 41121, 41131, 41141, 41151, 41161, 41171, 41181, 41191, 41201, 41211, 41221, 41231, 41241, 41251, 41261, 41271, 41281, 41291, 41301, 41311, 41321, 41331, 41341, 41351, 41361, 41371, 41381, 41391, 41401, 41411, 41421, 41431, 41441, 41451, 41461, 41471, 41481, 41491, 41501, 41511, 41521, 41531, 41541, 41551, 41561, 41571, 41581, 41591, 41601, 41611, 41621, 41631, 41641, 41651, 41661, 41671, 41681, 41691, 41701, 41711, 41721, 41731, 41741, 41751, 41761, 41771, 41781, 41791, 41801, 41811, 41821, 41831, 41841, 41851, 41861, 41871, 41881, 41891, 41901, 41911, 41921, 41931, 41941, 41951, 41961, 41971, 41981, 41991, 42001, 42011, 42021, 42031, 42041, 42051, 42061, 42071, 42081, 42091, 42101, 42111, 42121, 42131, 42141, 42151, 42161, 42171, 42181, 42191, 42201, 42211, 42221, 42231, 42241, 42251]


import gevent
#from gevent import monkey
#monkey.patch_all()


def clean_data(userid):
    mc = memcache.Client(['172.16.8.212:11211'])
    mc.delete('%d_package'%userid)

def get_camp(userid):
    mc = memcache.Client(['172.16.8.212:11211'])
    profile = mc.get('%d_profile'%int(userid))
    return profile['camp']

def create_profile(userid):
    profile = dict(gold=9999999)
    mc = memcache.Client(['172.16.8.212:11211'])
    mc.set('%d_profile'%userid, profile)

def show_scene_count():
    mc = memcache.Client(['172.16.8.212:11211'])
    scene_list = mc.get('scene_list')
    all_gsid = scene_list.values()
    keys = ['%s_map_userlist'%i for i in all_gsid]
    res = [(k.split('_')[0], len(i.keys())) for k, i in mc.get_multi(keys).items() if len(i.keys())!=0]
    print res

def enter(userid, mapname):
    """
    Arguments:
    - `userid`:
    - `mapname`:
    """
    mc = memcache.Client(['172.16.8.212:11211'])
    pos = mc.get('%d_position'%userid)
    camp = get_camp(userid)
    channel = pos.split('@')[-1]
    req = urllib2.Request('http://172.16.8.212/admin/enter')
    req.data=json.dumps({
        'userid':userid,
        'mapname':mapname,
        'gsid':urllib.quote('city%d@%s'%(int(camp), channel)),
        })
    res = urllib2.urlopen(req).read()
    return res

def go_city(userid):
    req = urllib2.Request('http://172.16.8.212/scene/back_to_city')
    req.add_data(urllib.urlencode({
        'userid':userid,
        }))
    res = urllib2.urlopen(req).read()
    return res

def leave(userid, mapname):
    """
    Arguments:
    - `userid`:
    - `mapname`:
    """
    req = urllib2.Request('http://172.16.8.212/admin/leave')
    req.data=json.dumps({
        'userid':userid,
        'mapname':mapname,
        'gsid':urllib.quote('city1@1'),
        })
    res = urllib2.urlopen(req).read()
    return res

def acceptable_task(userid):
    req = urllib2.Request('http://172.16.8.212/task/acceptable_task?userid=%d'%int(userid))
    res = urllib2.urlopen(req).read()
    return res

def register_player(account_id, name):
    req = urllib2.Request('http://172.16.8.212/profile/register')
    req.add_data(urllib.urlencode({
        "role":random.choice(['warrior', 'master', 'priest']),
        "account_id":account_id,
        "gender":random.choice(['male', 'female']),
        "name":"test%s"%name,
        "idcard":"test",
        "camp":random.randint(1,4),
        "client":"flash",
        }))
    res = urllib2.urlopen(req).read()
    return res

def register_account(email, password, invite_code):
    req = urllib2.Request('http://172.16.8.212/account/signup')
    req.add_data(urllib.urlencode({
        "form_email":email,
        "form_password":password,
        "invite_code":invite_code,
        "form_name":'test',
        "client":"robot",
        }))
    res = urllib2.urlopen(req).read()
    return res

def addmoney(userid, count):
    pass

def multi_buy(userid, items):
    req = urllib2.Request('http://172.16.8.212/trade/store/multi_buy')
    req.add_data(urllib.urlencode(dict(
        items=items,
        userid=userid
        )))
    urllib2.urlopen(req)

def package_buy(userid, pay_method, package_id):
    req = urllib2.Request('http://172.16.8.212/trade/store/package_buy')
    req.add_data(urllib.urlencode(dict(
        pay_method=pay_method,
        userid=userid,
        package_id=str(package_id),
        )))
    urllib2.urlopen(req)

def buy(userid, itemtype, itemid, count):
    req = urllib2.Request('http://172.16.8.212/trade/store/buy')
    req.add_data(urllib.urlencode(dict(
        itemtype=itemtype,
        itemid=itemid,
        count=count,
        userid=userid,
        )))
    urllib2.urlopen(req)

def combine(userid, combineid):
    req = urllib2.Request('http://172.16.8.212:9999/combine/combine')
    req.add_data(urllib.urlencode(dict(
        combine_id=combineid,
        userid=userid,
        )))
    urllib2.urlopen(req)

def get_package(userid):
    req = urllib2.Request('http://172.16.8.212/package/get_data?userid=%d&format=json'%userid)
    res = urllib2.urlopen(req).read()
    return json.loads(res)

def worker(count):
    #create_profile(test_userid)
    res = register_player(account_id=211, count=count)
    userid = json.loads(res)['userid']
    print userid
    buy(userid, 'material', '1', 1)
    buy(userid, 'material', '2', 1)
    buy(userid, 'material', '3', 1)
    buy(userid, 'material', '4', 1)
    buy(userid, 'material', '5', 1)
    assert len(get_package(userid)) == 5, 'really package:'+str(len(get_package(userid)))
    combine(userid, 4)
    assert len(get_package(userid)) == 1, 'really package:'+str(len(get_package(userid)))
    print 'finish..', count
    #clean_data(userid)

def multi_register(count):
    res = register_player(account_id=1061, count=count)
    userid = json.loads(res)
    global test_uid
    test_uid.append(userid)


def new_user(email):
    res1 = register_account(email=email, password='123456', invite_code='daydayup')
    accountid = json.loads(res1)['accountid']
    res2 = register_player(account_id=accountid, name='test_dongyi')
    print res2
    return json.loads(res2)['userid']

if __name__ == '__main__':
    emails = ['dongyi@test%d.com'%i for i in range(1, 2000)]
    for email in emails:
        try:
            userid = new_user(email)
            multi_buy(userid, 'material@6@200,material@7@200,consume@102@10,consume@101@10')
        except:
            print 'error'
            continue
    #jobs = [gevent.spawn(multi_register, cnt) for cnt in range(50000, 51000)]
    #gevent.joinall(jobs)
    #enter(169, 'city1')
    #print test_uid
    """
    cmd = sys.argv[1]
    count = 0
    for i in test_uid[:400]:
        if count % 5 == 0:
            time.sleep(1)
        if count %10 == 0:
            show_scene_count()
        if cmd == 'enter':
            camp = get_camp(i)
            if int(camp) > 3:
                continue
            go_city(i)
            enter(i, 'city%d'%int(camp))
        elif cmd == 'leave':
            camp = get_camp(i)
            if int(camp) > 3:
                continue
            leave(i, 'city%d'%int(camp))
        count += 1
        #leave(i, 'city1')
    """
    #userid = test_uid[0]
    #print userid
    #multi_buy(userid, 'material', 6, 200)
    #multi_buy(userid, 'material@6@200,material@7@200')
    #pprint.pprint(get_package(userid))
