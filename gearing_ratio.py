# pyinstaller --onefile --add-data "cninfo.js:." --hidden-import pandas --hidden-import requests --hidden-import colorama --clean "Gearing Ratio.py"

import pandas as pd
import time
import base64
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from io import BytesIO
from bs4 import BeautifulSoup
from tqdm import tqdm
import pathlib
from importlib import resources
from datetime import datetime
import sys
import os


def resource_path(relative_path):
    """获取资源的绝对路径（适用于开发环境和PyInstaller打包后环境）"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def _getResCode1():
    """
    Generate the CNInfo API authentication token using AES-CBC encryption.
    Equivalent to the JavaScript getResCode1() function in cninfo.js.
    Key/IV: '1234567887654321', input: current Unix timestamp as string.
    """
    key       = b'1234567887654321'
    iv        = b'1234567887654321'
    plaintext = str(int(time.time())).encode('utf-8')
    cipher    = AES.new(key, AES.MODE_CBC, iv)
    return base64.b64encode(cipher.encrypt(pad(plaintext, AES.block_size))).decode()


def stock_profile_cninfo(symbol: str = "600030") -> pd.DataFrame:
    """
    巨潮资讯-个股-公司概况
    https://webapi.cninfo.com.cn/#/company
    :param symbol: 股票代码
    :type symbol: str
    :return: 公司概况
    :rtype: pandas.DataFrame
    :raise: Exception，如果服务器返回的数据无法被解析
    """
    url = "https://webapi.cninfo.com.cn/api/sysapi/p_sysapi1133"
    params = {
        "scode": symbol,
    }
    mcode = _getResCode1()
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Content-Length": "0",
        "Host": "webapi.cninfo.com.cn",
        "Accept-Enckey": mcode,
        "Origin": "https://webapi.cninfo.com.cn",
        "Pragma": "no-cache",
        "Proxy-Connection": "keep-alive",
        "Referer": "https://webapi.cninfo.com.cn/",
        "X-Requested-With": "XMLHttpRequest",
    }
    r = requests.post(url, params=params, headers=headers)
    data_json = r.json()
    columns = [
        "公司名称",
        "英文名称",
        "曾用简称",
        "A股代码",
        "A股简称",
        "B股代码",
        "B股简称",
        "H股代码",
        "H股简称",
        "入选指数",
        "所属市场",
        "所属行业",
        "法人代表",
        "注册资金",
        "成立日期",
        "上市日期",
        "官方网站",
        "电子邮箱",
        "联系电话",
        "传真",
        "注册地址",
        "办公地址",
        "邮政编码",
        "主营业务",
        "经营范围",
        "机构简介",
    ]
    count = data_json["count"]
    if count == 1:
        redundant_json = data_json["records"][0]
        records_json = {}
        i = 0
        for k, v in redundant_json.items():
            if i == (len(redundant_json) - 4):
                break
            records_json[k] = v
            i += 1
        del i
        temp_df = pd.Series(records_json).to_frame().T
        temp_df.columns = columns
    elif count == 0:
        temp_df = pd.DataFrame(columns=columns)
    else:
        raise Exception("数据错误！")
    return temp_df


def stock_financial_report_sina(
    stock: str = "sh600600", symbol: str = "资产负债表"
) -> pd.DataFrame:
    """
    新浪财经-财务报表-三大报表
    https://vip.stock.finance.sina.com.cn/corp/go.php/vFD_FinanceSummary/stockid/600600/displaytype/4.phtml
    :param stock: 股票代码
    :type stock: str
    :param symbol: choice of {"资产负债表", "利润表", "现金流量表"}
    :type symbol: str
    :return: 新浪财经-财务报表-三大报表
    :rtype: pandas.DataFrame
    """
    symbol_map = {"资产负债表": "fzb", "利润表": "lrb", "现金流量表": "llb"}
    url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
    params = {
        "paperCode": f"{stock}",
        "source": symbol_map[symbol],
        "type": "0",
        "page": "1",
        "num": "1000",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    df_columns = [
        item["date_value"] for item in data_json["result"]["data"]["report_date"]
    ]
    big_df = pd.DataFrame()
    temp_df = pd.DataFrame()
    for date_str in df_columns:
        temp_df = pd.DataFrame(
            data_json["result"]["data"]["report_list"][date_str]["data"]
        )
        temp_df = temp_df[["item_title", "item_value"]]
        temp_df["item_value"] = pd.to_numeric(temp_df["item_value"], errors="coerce")
        temp_tail_df = pd.DataFrame.from_dict(
            data={
                "数据源": data_json["result"]["data"]["report_list"][date_str]["data_source"],
                "是否审计": data_json["result"]["data"]["report_list"][date_str]["is_audit"],
                "公告日期": data_json["result"]["data"]["report_list"][date_str]["publish_date"],
                "币种": data_json["result"]["data"]["report_list"][date_str]["rCurrency"],
                "类型": data_json["result"]["data"]["report_list"][date_str]["rType"],
                "更新日期": datetime.fromtimestamp(
                    data_json["result"]["data"]["report_list"][date_str]["update_time"]
                ).isoformat(),
            },
            orient="index",
        )
        temp_tail_df.reset_index(inplace=True)
        temp_tail_df.columns = ["item_title", "item_value"]
        temp_df = pd.concat(objs=[temp_df, temp_tail_df], ignore_index=True)
        temp_df.columns = ["项目", date_str]
        big_df = pd.concat(objs=[big_df, temp_df[date_str]], axis=1, ignore_index=True)

    big_df = big_df.T
    big_df.columns = temp_df["项目"]
    big_df = pd.concat(objs=[pd.DataFrame({"报告日": df_columns}), big_df], axis=1)
    big_df = big_df.loc[:, ~big_df.columns.duplicated(keep="first")]
    return big_df


if __name__ == "__main__":
    from colorama import init
    init(autoreset=True)

    while True:
        code = input("Please input the stock ticker: ")
        flag = True
        while flag:
            proposed_borrowing = input("Please input the proposed_borrowing (in million): ")
            if proposed_borrowing == 'T':
                flag = False
            else:
                proposed_borrowing = int(proposed_borrowing) * 1000000

                while len(code) != 6:
                    print("Please try again")
                    code = input("Please input a valid stock ticker: ")

                stock_profile_cninfo_df = stock_profile_cninfo(symbol=code)
                selected_cols = ['公司名称', '英文名称', '所属市场', 'A股代码', 'B股代码', '主营业务']

                values_list = stock_profile_cninfo_df.loc[0, selected_cols].values.tolist()
                index_list  = stock_profile_cninfo_df.loc[0, selected_cols].index.tolist()

                for i in range(len(values_list)):
                    print(index_list[i] + "   " + str(values_list[i]))

                print("___________________")

                df2 = stock_financial_report_sina(stock=code, symbol="资产负债表").head(1)
                selected_cols = ['报告日', '短期借款', '应付票据', '一年内到期的非流动负债', '应付债券', '长期借款', '租赁负债', '所有者权益(或股东权益)合计', '资产总计']

                values_list2 = df2.loc[0, selected_cols].values.tolist()
                index_list2  = df2.loc[0, selected_cols].index.tolist()

                if pd.isna(values_list2[1]): values_list2[1] = 0
                if pd.isna(values_list2[2]): values_list2[2] = 0
                if pd.isna(values_list2[3]): values_list2[3] = 0
                if pd.isna(values_list2[4]): values_list2[4] = 0
                if pd.isna(values_list2[5]): values_list2[5] = 0
                if pd.isna(values_list2[6]): values_list2[6] = 0

                for i in range(len(index_list2)):
                    print(index_list2[i] + "   " + str(values_list2[i]))

                print("___________________")

                total_debt0 = values_list2[1] + values_list2[2] + values_list2[3] + values_list2[4] + values_list2[5] + values_list2[6]
                total_debt1 = float(total_debt0) + float(proposed_borrowing)
                gr = total_debt1 / float(df2.loc[0, selected_cols].loc['所有者权益(或股东权益)合计']) * 100

                print("total debt before =", total_debt0)
                print("proposed borrowing =", proposed_borrowing)
                print("total debt after the proposed borrowing =", total_debt1)
                print("total equity =", float(df2.loc[0, selected_cols].loc['所有者权益(或股东权益)合计']))
                print("___________________")
                print()
                print('\033[33;1m' + 'Gearing ratio = ' + str(gr) + '\033[0m')
                print("___________________")

                print("Resulting debt/equity ratio exceed 300 percent?")
                if gr > 300:
                    print(f"\033[0;31mYes! Please check\033[0m")
                else:
                    print(f"\033[0;32mNo\033[0m")

                print("Proposed amount more than twice the company's total debt?")
                if proposed_borrowing / total_debt0 > 2:
                    print(f"\033[0;31mYes! Please check\033[0m")
                else:
                    print(f"\033[0;32mNo\033[0m")
