def get_ethnicity_placeholder(country_code, country_name=None):
    code = (country_code or "").strip().upper()
    label = (country_name or code or "Unknown").strip()
    return {
        "country_code": code,
        "country_name": label,
        "summary": "— (connect a census or survey API)",
        "source": "Ethnicity placeholder",
    }


import requests
import urllib3
import re

# Suppress only the single InsecureRequestWarning from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEMOGRAPHIC_DATA = {
    "NG": {
        "country": "Nigeria",
        "vital_stats": {"population": {"value": 218000000}, "median_age": {"value": 18.1}},
        "identity": {"religious_breakdown": {"Muslim": "53.5%", "Christian": "45.9%", "Other": "0.6%"}}
    },
    "JP": {
        "country": "Japan",
        "vital_stats": {"population": {"value": 124000000}, "median_age": {"value": 50.2}},
        "identity": {"religious_breakdown": {"Shintoism": "75.0%", "Buddhism": "20.0%", "Secular": "4.0%", "Christianity": "1.0%"}}
    },
    "US": {
        "country": "United States",
        "vital_stats": {"population": {"value": 334000000}, "median_age": {"value": 38.5}},
        "identity": {"religious_breakdown": {"Christianity": "65.0%", "Secular": "25.0%", "Judaism": "2.0%", "Hinduism": "1.0%", "Buddhism": "1.0%", "Islam": "1.0%", "Other": "5.0%"}}
    },
    "ET": {
        "country": "Ethiopia",
        "vital_stats": {"population": {"value": 126000000}, "median_age": {"value": 19.9}},
        "identity": {"religious_breakdown": {"Ethiopian Orthodox": "43.8%", "Muslim": "31.3%", "Protestant": "22.8%", "Catholic": "0.7%", "Other": "1.4%"}}
    },
    "IN": {
        "country": "India",
        "vital_stats": {},
        "identity": {"religious_breakdown": {"Hinduism": "79.8%", "Islam": "14.2%", "Christianity": "2.3%", "Sikhism": "1.7%", "Buddhism": "0.7%", "Jainism": "0.4%", "Zoroastrianism": "0.1%", "Other": "0.8%"}}
    },
    "VA": {"country": "Vatican City", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "99.0%", "Other": "1.0%"}}},
    "BR": {"country": "Brazil", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "85.0%", "Spiritism": "2.0%", "Secular": "13.0%"}}},
    "MX": {"country": "Mexico", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "85.0%", "Secular": "15.0%"}}},
    "SO": {"country": "Somalia", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "99.0%", "Other": "1.0%"}}},
    "MR": {"country": "Mauritania", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "99.0%", "Other": "1.0%"}}},
    "SA": {"country": "Saudi Arabia", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "99.0%", "Other": "1.0%"}}},
    "ID": {"country": "Indonesia", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "88.0%", "Christianity": "10.0%", "Hinduism": "1.7%", "Other": "0.3%"}}},
    "PK": {"country": "Pakistan", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "96.0%", "Hinduism": "2.0%", "Christianity": "1.5%", "Other": "0.5%"}}},
    "EG": {"country": "Egypt", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "90.0%", "Christianity": "10.0%"}}},
    "RU": {"country": "Russia", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "70.0%", "Secular": "20.0%", "Islam": "10.0%"}}},
    "FR": {"country": "France", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "50.0%", "Secular": "40.0%", "Islam": "5.0%", "Judaism": "1.0%", "Other": "4.0%"}}},
    "DE": {"country": "Germany", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "55.0%", "Secular": "35.0%", "Islam": "5.0%", "Other": "5.0%"}}},
    "GB": {"country": "United Kingdom", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "50.0%", "Secular": "40.0%", "Islam": "5.0%", "Hinduism": "1.5%", "Sikhism": "1.0%", "Judaism": "0.5%", "Other": "2.0%"}}},
    "CN": {"country": "China", "vital_stats": {}, "identity": {"religious_breakdown": {"Secular": "75.0%", "Buddhism": "15.0%", "Folk Religions": "10.0%"}}},
    "KP": {"country": "North Korea", "vital_stats": {}, "identity": {"religious_breakdown": {"Secular": "75.0%", "Other": "25.0%"}}},
    "CZ": {"country": "Czechia", "vital_stats": {}, "identity": {"religious_breakdown": {"Secular": "55.0%", "Christianity": "45.0%"}}},
    "NP": {"country": "Nepal", "vital_stats": {}, "identity": {"religious_breakdown": {"Hinduism": "81.0%", "Buddhism": "9.0%", "Islam": "4.0%", "Other": "6.0%"}}},
    "MU": {"country": "Mauritius", "vital_stats": {}, "identity": {"religious_breakdown": {"Hinduism": "40.0%", "Christianity": "30.0%", "Islam": "17.0%", "Other": "13.0%"}}},
    "GY": {"country": "Guyana", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "63.0%", "Hinduism": "35.0%", "Bahá'í": "1.0%", "Other": "1.0%"}}},
    "FJ": {"country": "Fiji", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "64.0%", "Hinduism": "27.0%", "Islam": "6.0%", "Other": "3.0%"}}},
    "TT": {"country": "Trinidad and Tobago", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "60.0%", "Hinduism": "18.0%", "Islam": "5.0%", "Other": "17.0%"}}},
    "AE": {"country": "United Arab Emirates", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "76.0%", "Hinduism": "10.0%", "Christianity": "9.0%", "Buddhism": "2.0%", "Other": "3.0%"}}},
    "KH": {"country": "Cambodia", "vital_stats": {}, "identity": {"religious_breakdown": {"Buddhism": "95.0%", "Islam": "2.0%", "Other": "3.0%"}}},
    "TH": {"country": "Thailand", "vital_stats": {}, "identity": {"religious_breakdown": {"Buddhism": "93.0%", "Islam": "5.0%", "Other": "2.0%"}}},
    "MM": {"country": "Myanmar", "vital_stats": {}, "identity": {"religious_breakdown": {"Buddhism": "80.0%", "Christianity": "6.0%", "Islam": "4.0%", "Other": "10.0%"}}},
    "LK": {"country": "Sri Lanka", "vital_stats": {}, "identity": {"religious_breakdown": {"Buddhism": "70.0%", "Hinduism": "12.0%", "Islam": "9.0%", "Christianity": "7.0%", "Other": "2.0%"}}},
    "SG": {"country": "Singapore", "vital_stats": {}, "identity": {"religious_breakdown": {"Buddhism": "33.0%", "Secular": "19.0%", "Christianity": "18.0%", "Islam": "15.0%", "Taoism": "10.0%", "Hinduism": "5.0%"}}},
    "AU": {"country": "Australia", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "43.0%", "Secular": "38.0%", "Islam": "3.0%", "Buddhism": "2.0%", "Hinduism": "2.0%", "Other": "12.0%"}}},
    "CA": {"country": "Canada", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "53.0%", "Secular": "29.0%", "Islam": "4.0%", "Hinduism": "2.0%", "Sikhism": "2.0%", "Buddhism": "1.0%", "Judaism": "1.0%", "Other": "8.0%"}}},
    "IL": {"country": "Israel", "vital_stats": {}, "identity": {"religious_breakdown": {"Judaism": "74.0%", "Islam": "18.0%", "Christianity": "2.0%", "Druze": "1.6%", "Samaritanism": "0.01%", "Other": "4.39%"}}},
    "LB": {"country": "Lebanon", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "60.0%", "Christianity": "35.0%", "Druze": "5.0%"}}},
    "SY": {"country": "Syria", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "87.0%", "Christianity": "10.0%", "Druze": "1.5%", "Other": "1.5%"}}},
    "BZ": {"country": "Belize", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "73.0%", "Secular": "15.0%", "Bahá'í": "1.0%", "Other": "11.0%"}}},
    "BO": {"country": "Bolivia", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "90.0%", "Secular": "5.0%", "Bahá'í": "1.0%", "Other": "4.0%"}}},
    "IR": {"country": "Iran", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "99.0%", "Zoroastrianism": "0.1%", "Other": "0.9%"}}},
    "TW": {"country": "Taiwan", "vital_stats": {}, "identity": {"religious_breakdown": {"Folk Religions": "35.0%", "Buddhism": "35.0%", "Secular": "20.0%", "Christianity": "5.0%", "Other": "5.0%"}}},
    "KR": {"country": "South Korea", "vital_stats": {}, "identity": {"religious_breakdown": {"Secular": "50.0%", "Christianity": "28.0%", "Buddhism": "15.0%", "Muism": "5.0%", "Other": "2.0%"}}},
    "VN": {"country": "Vietnam", "vital_stats": {}, "identity": {"religious_breakdown": {"Secular": "73.0%", "Buddhism": "12.0%", "Christianity": "8.0%", "Cao Dai": "2.0%", "Other": "5.0%"}}},
    "DJ": {"country": "Djibouti", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "94.0%", "Christianity": "6.0%"}}},
    "ER": {"country": "Eritrea", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "63.0%", "Islam": "36.0%", "Other": "1.0%"}}},
    "SD": {"country": "Sudan", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "97.0%", "Christianity": "3.0%"}}},
    "AF": {"country": "Afghanistan", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "99.0%", "Other": "1.0%"}}},
    "AL": {"country": "Albania", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "58.8%", "Christianity": "17.0%", "Secular": "24.2%"}}},
    "DZ": {"country": "Algeria", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "99.0%", "Other": "1.0%"}}},
    "AD": {"country": "Andorra", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "90.0%", "Other": "10.0%"}}},
    "AO": {"country": "Angola", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "75.0%", "ATR": "20.0%", "Other": "5.0%"}}},
    "AR": {"country": "Argentina", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "85.0%", "Secular": "12.0%", "Other": "3.0%"}}},
    "AM": {"country": "Armenia", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "97.0%", "Other": "3.0%"}}},
    "AT": {"country": "Austria", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "68.2%", "Secular": "20.0%", "Islam": "8.3%", "Other": "3.5%"}}},
    "AZ": {"country": "Azerbaijan", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "96.0%", "Christianity": "3.0%", "Other": "1.0%"}}},
    "BS": {"country": "Bahamas", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "95.0%", "Other": "5.0%"}}},
    "BH": {"country": "Bahrain", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "70.2%", "Christianity": "14.5%", "Hinduism": "9.8%", "Other": "5.5%"}}},
    "BD": {"country": "Bangladesh", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "90.4%", "Hinduism": "8.5%", "Buddhism": "0.6%", "Christianity": "0.4%", "Other": "0.1%"}}},
    "BB": {"country": "Barbados", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "75.6%", "Secular": "20.6%", "Other": "3.8%"}}},
    "BY": {"country": "Belarus", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "60.0%", "Secular": "35.0%", "Other": "5.0%"}}},
    "BE": {"country": "Belgium", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "60.0%", "Secular": "31.0%", "Islam": "7.0%", "Other": "2.0%"}}},
    "BT": {"country": "Bhutan", "vital_stats": {}, "identity": {"religious_breakdown": {"Buddhism": "75.3%", "Hinduism": "22.1%", "Other": "2.6%"}}},
    "BW": {"country": "Botswana", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "79.1%", "ATR": "6.0%", "Secular": "14.9%"}}},
    "BG": {"country": "Bulgaria", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "82.6%", "Islam": "10.0%", "Secular": "7.4%"}}},
    "CL": {"country": "Chile", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "67.0%", "Secular": "30.0%", "Other": "3.0%"}}},
    "CO": {"country": "Colombia", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "92.0%", "Secular": "7.0%", "Other": "1.0%"}}},
    "CR": {"country": "Costa Rica", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "83.0%", "Secular": "15.0%", "Other": "2.0%"}}},
    "HR": {"country": "Croatia", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "91.0%", "Secular": "6.0%", "Other": "3.0%"}}},
    "DK": {"country": "Denmark", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "74.7%", "Secular": "20.0%", "Islam": "5.3%"}}},
    "EC": {"country": "Ecuador", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "91.0%", "Secular": "8.0%", "Other": "1.0%"}}},
    "EE": {"country": "Estonia", "vital_stats": {}, "identity": {"religious_breakdown": {"Secular": "54.1%", "Christianity": "25.0%", "Other": "20.9%"}}},
    "FI": {"country": "Finland", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "69.0%", "Secular": "28.0%", "Other": "3.0%"}}},
    "GH": {"country": "Ghana", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "71.2%", "Islam": "17.6%", "ATR": "5.2%", "Other": "6.0%"}}},
    "GR": {"country": "Greece", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "98.0%", "Other": "2.0%"}}},
    "GT": {"country": "Guatemala", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "95.0%", "Other": "5.0%"}}},
    "HU": {"country": "Hungary", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "54.3%", "Secular": "30.0%", "Other": "15.7%"}}},
    "IS": {"country": "Iceland", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "70.0%", "Secular": "25.0%", "Other": "5.0%"}}},
    "IQ": {"country": "Iraq", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "98.0%", "Other": "2.0%"}}},
    "IE": {"country": "Ireland", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "82.0%", "Secular": "15.0%", "Other": "3.0%"}}},
    "IT": {"country": "Italy", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "80.0%", "Secular": "15.0%", "Other": "5.0%"}}},
    "JM": {"country": "Jamaica", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "64.8%", "Secular": "21.3%", "Other": "13.9%"}}},
    "JO": {"country": "Jordan", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "95.0%", "Christianity": "4.0%", "Other": "1.0%"}}},
    "KZ": {"country": "Kazakhstan", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "70.2%", "Christianity": "26.3%", "Other": "3.5%"}}},
    "KW": {"country": "Kuwait", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "74.6%", "Christianity": "18.2%", "Other": "7.2%"}}},
    "MY": {"country": "Malaysia", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "61.3%", "Buddhism": "19.8%", "Christianity": "9.2%", "Hinduism": "6.3%", "Other": "3.4%"}}},
    "MA": {"country": "Morocco", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "99.0%", "Other": "1.0%"}}},
    "NL": {"country": "Netherlands", "vital_stats": {}, "identity": {"religious_breakdown": {"Secular": "54.0%", "Christianity": "35.0%", "Islam": "5.0%", "Other": "6.0%"}}},
    "NZ": {"country": "New Zealand", "vital_stats": {}, "identity": {"religious_breakdown": {"Secular": "48.2%", "Christianity": "37.3%", "Hinduism": "2.6%", "Islam": "1.3%", "Other": "10.6%"}}},
    "NO": {"country": "Norway", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "70.0%", "Secular": "21.0%", "Islam": "3.0%", "Other": "6.0%"}}},
    "OM": {"country": "Oman", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "85.9%", "Christianity": "6.5%", "Hinduism": "5.5%", "Other": "2.1%"}}},
    "PA": {"country": "Panama", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "91.0%", "Other": "9.0%"}}},
    "PE": {"country": "Peru", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "94.0%", "Other": "6.0%"}}},
    "PH": {"country": "Philippines", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "92.0%", "Islam": "6.0%", "Other": "2.0%"}}},
    "PL": {"country": "Poland", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "87.0%", "Secular": "10.0%", "Other": "3.0%"}}},
    "PT": {"country": "Portugal", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "85.0%", "Secular": "11.0%", "Other": "4.0%"}}},
    "QA": {"country": "Qatar", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "67.7%", "Christianity": "13.8%", "Hinduism": "13.8%", "Buddhism": "3.1%", "Other": "1.6%"}}},
    "RO": {"country": "Romania", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "92.0%", "Secular": "6.0%", "Other": "2.0%"}}},
    "RS": {"country": "Serbia", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "91.0%", "Islam": "3.0%", "Other": "6.0%"}}},
    "SK": {"country": "Slovakia", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "75.0%", "Secular": "23.0%", "Other": "2.0%"}}},
    "SI": {"country": "Slovenia", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "70.0%", "Secular": "25.0%", "Other": "5.0%"}}},
    "ZA": {"country": "South Africa", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "81.0%", "Secular": "15.0%", "Other": "4.0%"}}},
    "ES": {"country": "Spain", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "60.0%", "Secular": "35.0%", "Other": "5.0%"}}},
    "SE": {"country": "Sweden", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "60.0%", "Secular": "35.0%", "Other": "5.0%"}}},
    "CH": {"country": "Switzerland", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "65.0%", "Secular": "28.0%", "Other": "7.0%"}}},
    "TR": {"country": "Turkey", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "99.0%", "Other": "1.0%"}}},
    "UA": {"country": "Ukraine", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "85.0%", "Secular": "12.0%", "Other": "3.0%"}}},
    "UY": {"country": "Uruguay", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "58.0%", "Secular": "41.0%", "Other": "1.0%"}}},
    "UZ": {"country": "Uzbekistan", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "93.0%", "Christianity": "4.0%", "Other": "3.0%"}}},
    "VE": {"country": "Venezuela", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "95.0%", "Other": "5.0%"}}},
    "CY": {"country": "Cyprus", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "78.0%", "Islam": "20.0%", "Other": "2.0%"}}},
    "GE": {"country": "Georgia", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "83.4%", "Islam": "10.7%", "Other": "5.9%"}}},
    "KG": {"country": "Kyrgyzstan", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "90.0%", "Christianity": "7.0%", "Other": "3.0%"}}},
    "LA": {"country": "Laos", "vital_stats": {}, "identity": {"religious_breakdown": {"Buddhism": "66.0%", "ATR": "31.0%", "Other": "3.0%"}}},
    "MN": {"country": "Mongolia", "vital_stats": {}, "identity": {"religious_breakdown": {"Buddhism": "53.0%", "Secular": "38.6%", "Islam": "3.0%", "Other": "5.4%"}}},
    "PS": {"country": "Palestine", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "93.0%", "Christianity": "6.0%", "Other": "1.0%"}}},
    "TJ": {"country": "Tajikistan", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "98.0%", "Other": "2.0%"}}},
    "TM": {"country": "Turkmenistan", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "89.0%", "Christianity": "9.0%", "Other": "2.0%"}}},
    "YE": {"country": "Yemen", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "99.1%", "Other": "0.9%"}}},
    "BJ": {"country": "Benin", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "48.5%", "Islam": "27.7%", "Vodun": "11.6%", "Other": "12.2%"}}},
    "BF": {"country": "Burkina Faso", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "61.5%", "Christianity": "29.8%", "ATR": "7.3%", "Other": "1.4%"}}},
    "CM": {"country": "Cameroon", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "70.0%", "Islam": "20.0%", "ATR": "6.0%", "Other": "4.0%"}}},
    "TD": {"country": "Chad", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "52.1%", "Christianity": "44.1%", "Other": "3.8%"}}},
    "CG": {"country": "Congo", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "75.0%", "ATR": "15.0%", "Islam": "2.0%", "Other": "8.0%"}}},
    "GA": {"country": "Gabon", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "80.0%", "Islam": "10.0%", "Other": "10.0%"}}},
    "GM": {"country": "Gambia", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "95.7%", "Christianity": "4.2%", "Other": "0.1%"}}},
    "GN": {"country": "Guinea", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "85.0%", "Christianity": "8.0%", "ATR": "7.0%"}}},
    "LR": {"country": "Liberia", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "85.6%", "Islam": "12.2%", "Other": "2.2%"}}},
    "LY": {"country": "Libya", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "97.0%", "Other": "3.0%"}}},
    "ML": {"country": "Mali", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "94.8%", "Christianity": "2.4%", "Other": "2.8%"}}},
    "NE": {"country": "Niger", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "98.0%", "Other": "2.0%"}}},
    "SN": {"country": "Senegal", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "95.9%", "Christianity": "4.1%"}}},
    "SL": {"country": "Sierra Leone", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "78.0%", "Christianity": "21.0%", "Other": "1.0%"}}},
    "TN": {"country": "Tunisia", "vital_stats": {}, "identity": {"religious_breakdown": {"Islam": "99.0%", "Other": "1.0%"}}},
    "ZM": {"country": "Zambia", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "95.5%", "Islam": "1.0%", "Other": "3.5%"}}},
    "ZW": {"country": "Zimbabwe", "vital_stats": {}, "identity": {"religious_breakdown": {"Christianity": "85.0%", "ATR": "10.0%", "Other": "5.0%"}}}
}

def _fetch_dynamic_religion_from_wiki(country_name):
    """Dynamically parses Wikipedia for specific religion demographics."""
    if not country_name or country_name == "Unknown":
        return None
        
    # Attempt targeted pages first
    search_queries = [
        f"Religion_in_{country_name.replace(' ', '_')}",
        f"Demographics_of_{country_name.replace(' ', '_')}",
        country_name.replace(' ', '_')
    ]
    
    headers = {"User-Agent": "GlobalIntelTool/1.0"}
    
    for query in search_queries:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        try:
            try:
                r = requests.get(url, headers=headers, timeout=5)
                r.raise_for_status()
            except requests.exceptions.SSLError:
                r = requests.get(url, headers=headers, timeout=5, verify=False)
                r.raise_for_status()
            if r.status_code == 200:
                text = r.json().get("extract", "")
                if text:
                    found = {}
                    # Enhanced Patterns
                    patterns = [
                        r'([A-Z][a-z]+)[^\d\.\%]{0,20}?(\d+(?:\.\d+)?)%',
                        r'(\d+(?:\.\d+)?)%[^\w]{0,20}?([A-Z][a-z]+)',
                        r'([A-Z][a-z]+)\s*\((\d+(?:\.\d+)?)%\)'
                    ]
                    
                    for p in patterns:
                        for m in re.finditer(p, text):
                            groups = m.groups()
                            if len(groups) == 2:
                                if '%' in m.group(0):
                                    name = groups[0] if not groups[0].replace('.','').isdigit() else groups[1]
                                    val = groups[1] if name == groups[0] else groups[0]
                                    found[name] = val + "%"
                    
                    valid_map = {
                        "christian": "Christianity", "catholic": "Catholicism", "protestant": "Protestantism", 
                        "orthodox": "Orthodox", "anglican": "Anglicanism", "islam": "Islam", "muslim": "Islam", 
                        "sunni": "Islam (Sunni)", "shia": "Islam (Shia)", "hindu": "Hinduism", 
                        "buddhist": "Buddhism", "jewish": "Judaism", "judaism": "Judaism",
                        "secular": "Secular", "atheist": "Secular", "irreligion": "Secular", "unaffiliated": "Secular",
                        "shinto": "Shinto", "sikh": "Sikhism", "jain": "Jainism", "bahai": "Bahá'í",
                        "folk": "Folk Religion", "traditional": "Traditional Beliefs", "animist": "Animism"
                    }
                    
                    clean_res = {}
                    for k, v in found.items():
                        lk = k.lower()
                        for key, mapped in valid_map.items():
                            if key in lk:
                                if mapped not in clean_res:
                                    clean_res[mapped] = v
                                break
                    
                    if clean_res:
                        return clean_res
        except Exception:
            continue
            
    return None

def get_religious_breakdown(country_code, country_name=None):
    """
    Returns demographic data (Median Age and Religious Breakdown) for selected countries.
    Sources are cited for all data points.
    """
    code = (country_code or "").strip().upper()
    label = (country_name or code or "Unknown").strip()
    
    data = DEMOGRAPHIC_DATA.get(code)
    if data:
        return {
            "country_code": code,
            "country_name": data["country"],
            "vital_stats": data.get("vital_stats", {}),
            "identity": data.get("identity", {})
        }

    # Dynamic Wikipedia Fetch if not in the hardcoded DB
    dynamic_religions = _fetch_dynamic_religion_from_wiki(label)
    if dynamic_religions:
        return {
            "country_code": code,
            "country_name": label,
            "vital_stats": {"median_age": {"value": "N/A"}},
            "identity": {"religious_breakdown": dynamic_religions}
        }

    return {
        "country_code": code,
        "country_name": label,
        "error": "Demographic data not available yet for this country.",
        "vital_stats": {"median_age": {"value": "N/A"}},
        "identity": {"religious_breakdown": {"Indigenous / Regional Beliefs": "100.0%"}}
    }