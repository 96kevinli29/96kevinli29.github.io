"""Names and country groups shared by build_data.py and build_page.py."""

# Chinese display names by ISO3 code. Add an entry when a new economy enters the selection.
ZH = {
    "SGP": "新加坡", "MAC": "澳门", "QAT": "卡塔尔", "BMU": "百慕大", "NOR": "挪威", "CHE": "瑞士",
    "GUY": "圭亚那", "BRN": "文莱", "CYM": "开曼群岛", "USA": "美国", "ISL": "冰岛", "FRO": "法罗群岛",
    "HKG": "香港", "AND": "安道尔", "ARE": "阿联酋", "GRL": "格陵兰", "SMR": "圣马力诺", "SAU": "沙特",
    "AUS": "澳大利亚", "BHR": "巴林", "CAN": "加拿大", "GBR": "英国", "KOR": "韩国", "ISR": "以色列",
    "NZL": "新西兰", "SXM": "荷属圣马丁", "KWT": "科威特", "JPN": "日本", "PRI": "波多黎各", "ABW": "阿鲁巴",
    "VIR": "美属维尔京群岛", "RUS": "俄罗斯", "TUR": "土耳其", "KAZ": "哈萨克斯坦", "PAN": "巴拿马", "OMN": "阿曼",
    "MYS": "马来西亚", "BHS": "巴哈马", "URY": "乌拉圭", "TCA": "特克斯和凯科斯", "CHL": "智利", "TTO": "特立尼达和多巴哥",
    "KNA": "圣基茨和尼维斯", "SYC": "塞舌尔", "ATG": "安提瓜和巴布达", "MNE": "黑山", "BLR": "白俄罗斯", "SRB": "塞尔维亚",
    "CRI": "哥斯达黎加", "MUS": "毛里求斯", "CUW": "库拉索", "ARG": "阿根廷", "GEO": "格鲁吉亚", "CHN": "中国",
    "DOM": "多米尼加共和国", "LCA": "圣卢西亚", "MDV": "马尔代夫", "ALB": "阿尔巴尼亚", "MKD": "北马其顿", "THA": "泰国",
    "AZE": "阿塞拜疆", "BRB": "巴巴多斯", "MEX": "墨西哥", "BIH": "波黑", "ARM": "亚美尼亚", "BRA": "巴西",
    "PLW": "帕劳", "VCT": "圣文森特和格林纳丁斯", "DMA": "多米尼克", "SUR": "苏里南", "COL": "哥伦比亚", "TKM": "土库曼斯坦",
    "GAB": "加蓬", "IND": "印度", "IDN": "印尼", "VNM": "越南", "ZAF": "南非", "NGA": "尼日利亚",
    "PHL": "菲律宾", "BGD": "孟加拉国", "PAK": "巴基斯坦", "EGY": "埃及", "IRN": "伊朗", "PER": "秘鲁",
    "EUU": "欧盟",
}

# Country names used by Wikipedia tables that differ from World Bank names.
ALIAS = {
    "Vietnam": "VNM", "Iran": "IRN", "Egypt": "EGY", "United States": "USA", "Russia": "RUS", "South Korea": "KOR",
    "Turkey": "TUR", "Türkiye": "TUR", "Hong Kong": "HKG", "Macau": "MAC", "Macao": "MAC", "Brunei": "BRN",
    "Bahamas": "BHS", "The Bahamas": "BHS", "Curaçao": "CUW", "Curacao": "CUW", "Sint Maarten": "SXM", "U.S. Virgin Islands": "VIR",
    "United States Virgin Islands": "VIR", "Saint Kitts and Nevis": "KNA", "Saint Lucia": "LCA", "Saint Vincent and the Grenadines": "VCT", "Faroe Islands": "FRO", "Greenland": "GRL",
    "Turks and Caicos Islands": "TCA", "Cayman Islands": "CYM", "Bermuda": "BMU", "Aruba": "ABW", "United Arab Emirates": "ARE", "Bosnia and Herzegovina": "BIH",
    "North Macedonia": "MKD", "Trinidad and Tobago": "TTO", "Antigua and Barbuda": "ATG", "Dominican Republic": "DOM", "Puerto Rico": "PRI", "Czech Republic": "CZE",
    "Czechia": "CZE",
}

# EU-27 members, merged into one economy "EUU".
EU = "AUT BEL BGR HRV CYP CZE DNK EST FIN FRA DEU GRC HUN IRL ITA LVA LTU LUX MLT NLD POL PRT ROU SVK SVN ESP SWE".split()

# Small territories left out because they miss two or more dimensions.
EXCLUDE = set("BMU FRO SXM TCA CUW PLW AND SMR CYM GRL PRI ABW VIR".split())

# Wikipedia's metro list files these cities under another country.
METRO_CITY = {"Hong Kong": "HKG", "Macau": "MAC", "San Juan": "PRI"}

# G20 members shown by default (France, Germany, Italy are inside the EU).
G20 = "ARG AUS BRA CAN CHN IND IDN JPN KOR MEX RUS SAU ZAF TUR GBR USA EUU".split()
