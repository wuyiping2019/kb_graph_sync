import json
import math
import re
import time
import requests
from utils.common_utils import delete_empty_value
from utils.custom_exception import cast_exception
from zgmsyh_config import SLEEP_SECOND, FIELD_MAPPINGS, PATTERN_Z, PATTERN_E


def process_zgmsyh_mobile(session):
    # https://ment.cmbc.com.cn/CMBC_MBServer/new/app/mobile-bank/finance/selling-list
    url = 'https://ment.cmbc.com.cn/gw/pwx_wx/QryProdListOnMarket.do'
    data = {
        "request": {
            "header": {
                "appId": "",
                "appVersion": "",
                "device": {
                    "osType": "BROWSER",
                    "osVersion": "",
                    "uuid": ""
                }
            },
            "body": {
                "pageSize": 10,
                "currentIndex": 0,
                "pageNo": 1,
                "orderFlag": "6",
                "liveTime": "3",
                "isKJTSS": "0",
                "prdAttr": "0",
                "prdChara": "4",
                "prdTypeNameList": [],
                "fundModeList": [],
                "pfirstAmtList": [],
                "currTypeList": []
            }
        }
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=UTF-8",
        "Host": "ment.cmbc.com.cn",
        "Origin": "https//ment.cmbc.com.cn",
        "Pragma": "no-cache",
        "Referer": "https//ment.cmbc.com.cn/CMBC_MBServer/new/app/mobile-bank/finance/selling-list",
        "sec-ch-ua": "\"Google Chrome\";v=\"95\", \"Chromium\";v=\"95\", \";Not A Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "\"Android\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Mobile Safari/537.36"
    }
    response = session.post(url=url, json=data, headers=headers)
    time.sleep(SLEEP_SECOND)
    try:
        rows = []
        response_str = response.text.encode(response.encoding).decode('utf-8') if response.encoding else response.text
        loads = json.loads(response_str)
        total_size = loads['response']['totalSize']
        page_num = math.ceil(total_size / data['request']['body']['pageSize'])
        for page in range(1, page_num + 1):
            data['request']['body']['currentIndex'] = (page - 1) * 10
            data['request']['body']['pageNo'] = page
            resp = session.post(url=url, json=data, headers=headers)
            time.sleep(SLEEP_SECOND)
            resp_str = resp.text.encode(resp.encoding).decode('utf-8') if resp.encoding else resp.text
            loads = json.loads(resp_str)
            prd_list = loads['response']['prdList']
            for prd in prd_list:
                row = {
                    FIELD_MAPPINGS['??????']: prd['NAV'],
                    FIELD_MAPPINGS['??????????????????']: prd['startDate'],
                    FIELD_MAPPINGS['??????????????????']: prd['endDate'],
                    FIELD_MAPPINGS['????????????']: prd['prdName'],
                    FIELD_MAPPINGS['????????????']: prd['prdTypeName'],
                    # ?????????????????????????????????????????????
                    FIELD_MAPPINGS['??????????????????']: json.dumps({
                                                             'title': prd['divModesName'].split(':')[1].split('(')[
                                                                 0],
                                                             'qsrq': (re.findall(PATTERN_Z,
                                                                                 prd['divModesName']) + re.findall(
                                                                 PATTERN_E, prd['divModesName']))[0].split('???')[0],
                                                             'jsrq': (re.findall(PATTERN_Z,
                                                                                 prd['divModesName']) + re.findall(
                                                                 PATTERN_E, prd['divModesName']))[0].split('???')[1],
                                                             'jz': prd['divModesName'].split(':')[0]
                                                         } if prd.get('prdTypeName', '') == '??????????????????'
                                                              and len(prd['divModesName'].split(':')) >= 2 \
                                                              and len((re.findall(PATTERN_Z, prd[
                        'divModesName']) + re.findall(PATTERN_E, prd['divModesName']))) >= 1 \
                                                             else '').encode().decode('unicode_escape'),
                    FIELD_MAPPINGS['??????']: prd.get('currTypeName', ''),
                    FIELD_MAPPINGS['????????????']: prd.get('prdShortName', ''),
                    FIELD_MAPPINGS['?????????']: str(prd.get('totAmt', '')) + '???' if str(prd.get('totAmt', '')) != '' else '',
                    FIELD_MAPPINGS['??????????????????']: prd.get('ipoStartDate', ''),
                    FIELD_MAPPINGS['??????????????????']: prd.get('ipoEndDate', ''),
                    FIELD_MAPPINGS['????????????']: prd.get('riskLevelName', '')
                }
                keys = [str(key) for key in row.keys()]
                row = delete_empty_value(row) if not delete_empty_value(row) else {}
                # ???????????????
                detail_url = 'https://ment.cmbc.com.cn/gw/pwx_wx/QueryPrdBuyInfo.do'
                detail_headers = {
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Length": "185",
                    "Content-Type": "application/json;charset=UTF-8",
                    "Cookie": "OUTFOX_SEARCH_USER_ID_NCOO=2040096739.6771917; PWX_WX_SESSIONID=34FC7B1B273C572F20EB1F96F27C0193; org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=zh_CN; BIGipServerUEB_tongyidianziqudao_app_41002_pool=!L2XyF0+cO/ssrkw0lXP1ySZhZOpxgnxVuEYnVLA5Hg4K7elqXQ998Lleke6jYiFBhfQpPyRSaWBl7A==",
                    "Host": "ment.cmbc.com.cn",
                    "Origin": "https//ment.cmbc.com.cn",
                    "Pragma": "no-cache",
                    "Referer": "https//ment.cmbc.com.cn/CMBC_MBServer/new/app/mobile-bank/finance/selling-detail?prdCode=FSAE68205A&prdType=4&startDate=2022-03-08",
                    "sec-ch-ua": "\"Google Chrome\";v=\"95\", \"Chromium\";v=\"95\", \";Not A Brand\";v=\"99\"",
                    "sec-ch-ua-mobile": "?1",
                    "sec-ch-ua-platform": "\"Android\"",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Mobile Safari/537.36"}
                detail_data = {
                    "request": {
                        "header": {
                            "appId": "", "appVersion": "",
                            "device": {
                                "osType": "BROWSER",
                                "osVersion": "",
                                "uuid": ""
                            }
                        },
                        "body": {
                            "prdCode": "FSAE68205A",
                            "getVipFlag": "1",
                            "GroupFlag": "1",
                            "isKJTSS": "0"
                        }
                    }
                }
                detail_response = session.post(url=detail_url, json=detail_data, headers=detail_headers)
                time.sleep(SLEEP_SECOND)
                detail_resp_str = detail_response.text.encode(
                    detail_response.encoding) if detail_response.encoding else detail_response.text
                detail_loads = json.loads(detail_resp_str)['response']
                detail_row = {
                    FIELD_MAPPINGS['??????']: str(detail_loads.get('NAV', '')),
                    FIELD_MAPPINGS['??????????????????']: detail_loads.get('endDate', ''),
                    FIELD_MAPPINGS['????????????']: json.dumps(detail_loads.get('channelsName', '').split(';')).encode().decode(
                        'unicode_escape') if detail_loads.get('channelsName', '') else '',
                    FIELD_MAPPINGS['????????????']: detail_loads.get('prdCode', ''),
                    FIELD_MAPPINGS['????????????']: detail_loads.get('statusName', ''),
                    FIELD_MAPPINGS['??????']: detail_loads.get('currTypeName', ''),
                    FIELD_MAPPINGS['????????????']: detail_loads.get('prdShortName', ''),
                    FIELD_MAPPINGS['?????????']: detail_loads.get('prdTrusteeName', ''),
                    FIELD_MAPPINGS['??????????????????']: detail_loads.get('ipoEndDate', ''),
                    FIELD_MAPPINGS['??????????????????']: detail_loads.get('ipoStartDate', ''),
                    FIELD_MAPPINGS['????????????']: detail_loads.get('riskLevelName', ''),
                    FIELD_MAPPINGS['????????????']: detail_loads.get('warmTipsMap', {}).get('tipsTitle', ''),
                    FIELD_MAPPINGS['????????????']: detail_loads.get('livTimeUnitName', '')
                }
                # ??????detail_row???value?????????key
                delete_empty_value(detail_row)
                if not row:
                    row = {}
                if not detail_row:
                    detail_row = {}
                row.update(detail_row)
                # ?????? detail_loads????????????
                url_row = {}
                for detail_url in detail_loads.get('protocol', [{}]):
                    if detail_url.get('fileType', '') == '0':
                        url_row['cpsms'] = json.dumps({
                            'url': detail_url.get('filePath', ''),
                            'title': detail_url.get('fileTitle', '')
                        }).encode().decode('unicode_escape') if detail_url.get('filePath', '') != '' and detail_url.get(
                            'fileTitle', '') != '' else ''
                    elif detail_url.get('fileType', '') == '1':
                        url_row['cphy'] = json.dumps({
                            'url': detail_url.get('filePath', ''),
                            'title': detail_url.get('fileTitle', '')
                        }).encode().decode('unicode_escape') if detail_url.get('filePath', '') != '' and detail_url.get(
                            'fileTitle', '') != '' else ''
                    elif detail_url.get('fileType', '') == '2':
                        url_row['fxjss'] = json.dumps({
                            'url': detail_url.get('filePath', ''),
                            'title': detail_url.get('fileTitle', '')
                        }).encode().decode('unicode_escape') if detail_url.get('filePath', '') != '' and detail_url.get(
                            'fileTitle', '') != '' else ''
                delete_empty_value(url_row)
                if not url_row:
                    url_row = {}
                row.update(url_row)
                # ??????????????????
                lsjz_url = 'https://ment.cmbc.com.cn/gw/pwx_wx/QryFinancingLineTotalData.do'
                lsjz_headers = {"Accept": "application/json, text/plain, */*", "Accept-Encoding": "gzip, deflate, br",
                                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8", "Cache-Control": "no-cache",
                                "Connection": "keep-alive", "Content-Type": "application/json;charset=UTF-8",
                                "Host": "ment.cmbc.com.cn", "Origin": "https//ment.cmbc.com.cn", "Pragma": "no-cache",
                                "Referer": "https//ment.cmbc.com.cn/CMBC_MBServer/new/app/mobile-bank/finance/selling-detail?prdCode=FSAE68205A&prdType=4&startDate=2022-03-08",
                                "sec-ch-ua": "\"Google Chrome\";v=\"95\", \"Chromium\";v=\"95\", \";Not A Brand\";v=\"99\"",
                                "sec-ch-ua-mobile": "?1", "sec-ch-ua-platform": "\"Android\"",
                                "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin",
                                "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Mobile Safari/537.36"}
                lsjz_data = {
                    "request": {
                        "header": {
                            "appId": "", "appVersion": "",
                            "device": {
                                "osType": "BROWSER", "osVersion": "", "uuid": ""}},
                        "body": {
                            "prdCode": row['cpbm'], "startDate": "", "endDate": "",
                            "months": "0", "lineType": ["1", "2"]}}}
                lsjz_response = session.post(url=lsjz_url, json=lsjz_data, headers=lsjz_headers)
                time.sleep(SLEEP_SECOND)
                lsjz_resp_str = lsjz_response.text.encode(lsjz_response.encoding).decode(
                    'utf-8') if lsjz_response.encoding else lsjz_response.text
                lsjz_loads = json.loads(lsjz_resp_str)
                lsjz_row = {'lsjz': []}
                try:
                    # ??????????????????????????????????????????
                    for item in lsjz_loads['response']['map']['navList']:
                        lsjz_row['lsjz'].append(
                            {
                                'jz': item['NAV'],
                                'jzrq': item['issDate']
                            }
                        )
                except Exception as e:
                    print(f'????????????{row["cpbm"]}???????????????')
                # ??????????????????????????????row???
                if lsjz_row['lsjz']:
                    lsjz_row['lsjz'] = json.dumps(lsjz_row['lsjz']).encode().decode('unicode_escape')
                    if not lsjz_row:
                        lsjz_row = {}
                    row.update(lsjz_row)

                # ??????????????????
                syed_url = 'https://ment.cmbc.com.cn/gw/pwx_wx/QueryPrdLimitTrans.do'
                syed_headers = {"Accept": "application/json, text/plain, */*", "Accept-Encoding": "gzip, deflate, br",
                                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8", "Cache-Control": "no-cache",
                                "Connection": "keep-alive", "Content-Type": "application/json;charset=UTF-8",
                                "Host": "ment.cmbc.com.cn", "Origin": "https//ment.cmbc.com.cn", "Pragma": "no-cache",
                                "Referer": "https//ment.cmbc.com.cn/CMBC_MBServer/new/app/mobile-bank/finance/selling-detail?prdCode=FSAE68205A&prdType=4&startDate=2022-03-08",
                                "sec-ch-ua": "\"Google Chrome\";v=\"95\", \"Chromium\";v=\"95\", \";Not A Brand\";v=\"99\"",
                                "sec-ch-ua-mobile": "?1", "sec-ch-ua-platform": "\"Android\"",
                                "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin",
                                "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Mobile Safari/537.36"}
                syed_data = {"request": {"header": {"appId": "", "appVersion": "",
                                                    "device": {"osType": "BROWSER", "osVersion": "", "uuid": ""}},
                                         "body": {"PrdCode": row['cpbm'], "transAcct": ""}}}
                syed_response = session.post(url=syed_url, json=syed_data, headers=syed_headers)
                syed_resp_str = syed_response.text.encode(syed_response.encoding).decode(
                    'utf-8') if syed_response.encoding else syed_response.text
                syed_loads = json.loads(syed_resp_str)
                syed_row = {
                    'syed': ''
                }
                try:
                    syed_row['syed'] = str(syed_loads['response']['TotSaleAmt'])
                except Exception as e:
                    print(f'????????????{row["cpbm"]}???????????????')
                delete_empty_value(syed_row)
                if not syed_row:
                    syed_row = {}
                row.update(syed_row)
                print(row)
                rows.append(row)
        return rows
    except Exception as e:
        exception = cast_exception(e)
        raise exception


if __name__ == '__main__':
    session = requests.session()
    process_zgmsyh_mobile(session)
    session.close()
