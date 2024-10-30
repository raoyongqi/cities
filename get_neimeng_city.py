import requests
import csv
import time

def get_gansu_cities(amap_key):
    """获取甘肃省的地级市列表"""
    url = "https://restapi.amap.com/v3/config/district"
    params = {
        "keywords":"内蒙古自治区",
        "subdistrict": 1,
        "key": amap_key,
        "extensions": "base"
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data["status"] == "1":
        cities = data["districts"][0]["districts"]
        return [city["name"] for city in cities]
    else:
        print("查询地级市列表失败:", data["info"])
        return []

def get_city_location(amap_key, city_name, retries=3):
    """使用地理编码API查询城市的经纬度"""
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {"key": amap_key, "address": city_name}

    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data["status"] == "1" and data["geocodes"]:
                location = data["geocodes"][0]["location"]
                return location.split(",")
            else:
                print(f"查询失败: {city_name}, 错误信息: {data['info']}")
                return None, None
        except requests.exceptions.RequestException as e:
            print(f"请求 {city_name} 经纬度失败，重试 {attempt+1}/{retries}...")
            time.sleep(2)  # 暂停一会再重试
    return None, None

def save_to_csv(city_data, filename="neimeng_cities.csv"):
    with open(filename, mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["City", "Longitude", "Latitude"])
        for city, lon, lat in city_data:
            writer.writerow([city, lon, lat])

if __name__ == "__main__":
    amap_key =  "634d7ad3bd0bfeb370acfa403505291e" # 替换为你的高德API key
    gansu_cities = get_gansu_cities(amap_key)
    
    city_data = []
    for city in gansu_cities:
        lon, lat = get_city_location(amap_key, city)
        if lon and lat:
            city_data.append((city, lon, lat))
        time.sleep(0.5)  # 防止请求过快被限制
    
    if city_data:
        save_to_csv(city_data)
        print("地级市数据已保存到 neimeng_cities.csv 文件中")
