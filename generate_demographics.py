import yaml
import re
import random

# Raw data provided by user (The 12 districts)
raw_csv = """
1,Bắc Từ Liêm,Phường Thụy Phương,"13.676","4.748"
2,Bắc Từ Liêm,Phường Xuân Tảo,"20.652","9.138"
3,Bắc Từ Liêm,Phường Đức Thắng,"19.923","16.603"
4,Bắc Từ Liêm,Phường Minh Khai,"36.709","7.555"
5,Bắc Từ Liêm,Phường Cổ Nhuế 1,"45.274","20.394"
6,Bắc Từ Liêm,Phường Cổ Nhuế 2,"44.780","11.056"
7,Bắc Từ Liêm,Phường Tây Tựu,"20.727","3.845"
8,Bắc Từ Liêm,Phường Liên Mạc,"12.966","2.166"
9,Bắc Từ Liêm,Phường Xuân Đỉnh,"39.993","11.361"
10,Bắc Từ Liêm,Phường Đông Ngạc,"23.922","9.926"
11,Bắc Từ Liêm,Phường Phúc Diễn,"23.734","10.936"
12,Bắc Từ Liêm,Phường Thượng Cát,"8.593","2.208"
13,Bắc Từ Liêm,Phường Phú Diễn,"42.882","17.016"
14,Đống Đa,Phường Cát Linh,"11.064","30.733"
15,Đống Đa,Phường Hàng Bột,"18.527","59.764"
16,Đống Đa,Phường Khâm Thiên,"9.753","51.331"
17,Đống Đa,Phường Khương Thượng,"15.712","46.211"
18,Đống Đa,Phường Kim Liên,"13.795","40.573"
19,Đống Đa,Phường Láng Hạ,"25.369","26.704"
20,Đống Đa,Phường Láng Thượng,"19.967","16.233"
21,Đống Đa,Phường Nam Đồng,"14.619","35.656"
22,Đống Đa,Phường Ngã Tư Sở,"7.804","33.930"
23,Đống Đa,Phường Ô Chợ Dừa,"34.354","30.135"
24,Đống Đa,Phường Phương Liên,"17.693","39.317"
25,Đống Đa,Phường Phương Mai,"18.154","30.257"
26,Đống Đa,Phường Quang Trung,"14.489","34.497"
27,Đống Đa,Phường Quốc Tử Giám,"8.140","42.842"
28,Đống Đa,Phường Thịnh Quang,"18.669","40.584"
29,Đống Đa,Phường Thổ Quan,"16.412","56.593"
30,Đống Đa,Phường Trung Liệt,"21.668","28.511"
31,Đống Đa,Phường Trung Phụng,"16.998","73.904"
32,Đống Đa,Phường Trung Tự,"16.649","32.188"
33,Đống Đa,Phường Văn Chương,"16.619","50.360"
34,Đống Đa,Phường Văn Miếu,"9.578","33.027"
35,Nam Từ Liêm,Phường Cầu Diễn,"27.017","15.093"
36,Nam Từ Liêm,Phường Mỹ Đình 1,"30.264","13.273"
37,Nam Từ Liêm,Phường Mỹ Đình 2,"33.666","17.353"
38,Nam Từ Liêm,Phường Phú Đô,"15.983","6.687"
39,Nam Từ Liêm,Phường Mễ Trì,"32.169","6.888"
40,Nam Từ Liêm,Phường Trung Văn,"43.757","15.739"
41,Nam Từ Liêm,Phường Đại Mỗ,"32.920","6.610"
42,Nam Từ Liêm,Phường Tây Mỗ,"28.808","4.761"
43,Nam Từ Liêm,Phường Phương Canh,"20.117","7.707"
44,Nam Từ Liêm,Phường Xuân Phương,"17.743","6.428"
45,Hà Đông,Phường La Khê,"12.935","4.980"
46,Hà Đông,Phường Mộ Lao,"24.221","19.223"
47,Hà Đông,Phường Biên Giang,"8.350","3.538"
48,Hà Đông,Phường Yên Nghĩa,"24.058","3.471"
49,Hà Đông,Phường Đồng Mai,"16.050","2.525"
50,Hà Đông,Phường Dương Nội,"25.950","4.435"
51,Hà Đông,Phường Vạn Phúc,"14.289","9.992"
52,Hà Đông,Phường Yết Kiêu,"8.623","41.061"
53,Hà Đông,Phường Phúc La,"6.243","4.491"
54,Hà Đông,Phường Hà Cầu,"14.876","9.769"
55,Hà Đông,Phường Phú La,"6.526","3.691"
56,Hà Đông,Phường Văn Quán,"23.570","16.835"
57,Hà Đông,Phường Phú Lương,"17.581","2.618"
58,Hà Đông,Phường Quang Trung,"16.274","19.374"
59,Hà Đông,Phường Phú Lãm,"13.109","4.928"
60,Hà Đông,Phường Kiến Hưng,"11.390","2.685"
61,Hà Đông,Phường Nguyễn Trãi,"13.563","32.292"
62,Ba Đình,Phường Cống Vị,"16.330","31.404"
63,Ba Đình,Phường Điện Biên,"8.895","9.463"
64,Ba Đình,Phường Đội Cấn,"14.033","22.634"
65,Ba Đình,Phường Giảng Võ,"18.435","46.088"
66,Ba Đình,Phường Kim Mã,"15.571","32.440"
67,Ba Đình,Phường Liễu Giai,"20.546","28.145"
68,Ba Đình,Phường Ngọc Hà,"19.479","24.349"
69,Ba Đình,Phường Ngọc Khánh,"21.182","20.367"
70,Ba Đình,Phường Nguyễn Trung Trực,"7.466","46.663"
71,Ba Đình,Phường Phúc Xá,"22.024","23.939"
72,Ba Đình,Phường Quán Thánh,"7.971","10.352"
73,Ba Đình,Phường Thành Công,"24.126","37.697"
74,Ba Đình,Phường Trúc Bạch,"7.514","14.450"
75,Ba Đình,Phường Vĩnh Phúc,"23.000","31.081"
76,Hai Bà Trưng,Phường Nguyễn Du,"10.078","19.380"
77,Hai Bà Trưng,Phường Bạch Đằng,"19.807","17.528"
78,Hai Bà Trưng,Phường Phạm Đình Hổ,"12.962","27.004"
79,Hai Bà Trưng,Phường Lê Đại Hành,"9.493","11.038"
80,Hai Bà Trưng,Phường Đồng Nhân,"8.196","54.640"
81,Hai Bà Trưng,Phường Phố Huế,"8.896","44.480"
82,Hai Bà Trưng,Phường Đống Mác,"9.815","65.433"
83,Hai Bà Trưng,Phường Thanh Lương,"23.038","14.220"
84,Hai Bà Trưng,Phường Thanh Nhàn,"21.750","29.794"
85,Hai Bà Trưng,Phường Cầu Dền,"12.620","70.111"
86,Hai Bà Trưng,Phường Bách Khoa,"9.994","18.856"
87,Hai Bà Trưng,Phường Đồng Tâm,"19.681","38.590"
88,Hai Bà Trưng,Phường Vĩnh Tuy,"39.122","24.605"
89,Hai Bà Trưng,Phường Bạch Mai,"16.000","64.000"
90,Hai Bà Trưng,Phường Quỳnh Mai,"11.890","69.941"
91,Hai Bà Trưng,Phường Quỳnh Lôi,"14.755","59.020"
92,Hai Bà Trưng,Phường Minh Khai,"19.108","40.655"
93,Hai Bà Trưng,Phường Trương Định,"21.087","40.551"
94,Long Biên,Phường Thượng Thanh,"13.153","2.695"
95,Long Biên,Phường Ngọc Thụy,"18.568","2.065"
96,Long Biên,Phường Giang Biên,"4.600","977"
97,Long Biên,Phường Đức Giang,"25.767","10.692"
98,Long Biên,Phường Việt Hưng,"7.884","2.058"
99,Long Biên,Phường Gia Thụy,"9.721","8.101"
100,Long Biên,Phường Ngọc Lâm,"19.604","17.349"
101,Long Biên,Phường Phúc Lợi,"7.820","1.261"
102,Long Biên,Phường Bồ Đề,"16.159","4.252"
103,Long Biên,Phường Sài Đồng,"14.029","15.416"
104,Long Biên,Phường Long Biên,"9.455","1.308"
105,Long Biên,Phường Thạch Bàn,"11.300","2.144"
106,Long Biên,Phường Phúc Đồng,"6.994","1.413"
107,Long Biên,Phường Cự Khối,"5.652","1.161"
108,Cầu Giấy,Phường Dịch Vọng,"27.979","21.196"
109,Cầu Giấy,Phường Dịch Vọng Hậu,"31.879","21.540"
110,Cầu Giấy,Phường Mai Dịch,"40.527","20.063"
111,Cầu Giấy,Phường Nghĩa Đô,"35.054","27.174"
112,Cầu Giấy,Phường Nghĩa Tân,"22.207","32.657"
113,Cầu Giấy,Phường Quan Hoa,"34.055","41.030"
114,Cầu Giấy,Phường Trung Hòa,"54.770","22.264"
115,Cầu Giấy,Phường Yên Hòa,"47.467","22.931"
116,Hoàng Mai,Phường Đại Kim,"52.926","19.387"
117,Hoàng Mai,Phường Định Công,"47.847","17.721"
118,Hoàng Mai,Phường Giáp Bát,"18.474","31.312"
119,Hoàng Mai,Phường Hoàng Liệt,"94.415","19.467"
120,Hoàng Mai,Phường Hoàng Văn Thụ,"43.189","25.405"
121,Hoàng Mai,Phường Lĩnh Nam,"30.095","5.374"
122,Hoàng Mai,Phường Mai Động,"48.476","59.847"
123,Hoàng Mai,Phường Tân Mai,"26.664","52.282"
124,Hoàng Mai,Phường Thanh Trì,"25.600","7.665"
125,Hoàng Mai,Phường Thịnh Liệt,"38.738","13.176"
126,Hoàng Mai,Phường Trần Phú,"14.072","3.554"
127,Hoàng Mai,Phường Tương Mai,"30.005","40.547"
128,Hoàng Mai,Phường Vĩnh Hưng,"39.873","22.152"
129,Hoàng Mai,Phường Yên Sở,"24.226","3.342"
130,Hoàn Kiếm,Phường Phúc Tân,"18.541","23.469"
131,Hoàn Kiếm,Phường Đồng Xuân,"9.444","55.552"
132,Hoàn Kiếm,Phường Hàng Mã,"6.894","40.552"
133,Hoàn Kiếm,Phường Hàng Buồm,"7.620","63.500"
134,Hoàn Kiếm,Phường Hàng Đào,"5.339","76.271"
135,Hoàn Kiếm,Phường Hàng Bồ,"5.431","60.344"
136,Hoàn Kiếm,Phường Cửa Đông,"6.652","44.346"
137,Hoàn Kiếm,Phường Lý Thái Tổ,"5.556","23.150"
138,Hoàn Kiếm,Phường Hàng Bạc,"5.133","57.033"
139,Hoàn Kiếm,Phường Hàng Gai,"5.779","64.211"
140,Hoàn Kiếm,Phường Chương Dương,"23.034","22.363"
141,Hoàn Kiếm,Phường Hàng Trống,"8.344","24.541"
142,Hoàn Kiếm,Phường Cửa Nam,"6.354","24.438"
143,Hoàn Kiếm,Phường Hàng Bông,"6.833","37.961"
144,Hoàn Kiếm,Phường Tràng Tiền,"6.734","17.721"
145,Hoàn Kiếm,Phường Trần Hưng Đạo,"9.212","19.600"
146,Hoàn Kiếm,Phường Phan Chu Trinh,"7.168","17.067"
147,Hoàn Kiếm,Phường Hàng Bài,"5.775","21.388"
148,Thanh Xuân,Phường Hạ Đình,"18.580","26.699"
149,Thanh Xuân,Phường Khương Đình,"31.695","24.202"
150,Thanh Xuân,Phường Khương Mai,"21.543","20.362"
151,Thanh Xuân,Phường Khương Trung,"35.000","47.431"
152,Thanh Xuân,Phường Kim Giang,"13.494","58.925"
153,Thanh Xuân,Phường Nhân Chính,"50.982","30.883"
154,Thanh Xuân,Phường Phương Liệt,"25.817","27.511"
155,Thanh Xuân,Phường Thanh Xuân Bắc,"21.225","42.948"
156,Thanh Xuân,Phường Thanh Xuân Nam,"12.904","41.069"
157,Thanh Xuân,Phường Thanh Xuân Trung,"33.418","31.040"
158,Thanh Xuân,Phường Thượng Đình,"28.101","42.010"
159,Tây Hồ,Phường Bưởi,"25.838","18.455"
160,Tây Hồ,Phường Nhật Tân,"7.104","6.897"
161,Tây Hồ,Phường Phú Thượng,"14.365","2.444"
162,Tây Hồ,Phường Quảng An,"10.015","10.015"
163,Tây Hồ,Phường Thụy Khuê,"14.063","6.927"
164,Tây Hồ,Phường Tứ Liên,"18.069","5.147"
165,Tây Hồ,Phường Xuân La,"28.972","13.289"
166,Tây Hồ,Phường Yên Phụ,"23.942","16.626"
"""

# Missing District Data (Name: (Population, Area_km2)) - Approx 2022-2023
# User noted all are "Quận" in districts.yml
MISSING_DISTRICT_DATA = {
    "quận sơn tây": (151090, 117.20),
    "quận ba vì": (305933, 421.80),
    "quận chương mỹ": (347564, 237.48),
    "quận đan phượng": (185653, 77.83),
    "quận đông anh": (437308, 185.68),
    "quận gia lâm": (292943, 116.64),
    "quận hoài đức": (257633, 84.92),
    "quận mê linh": (241633, 141.29),
    "quận mỹ đức": (203778, 188.86),
    "quận phú xuyên": (229847, 171.11),
    "quận phúc thọ": (194754, 117.80),
    "quận quốc oai": (203079, 151.10),
    "quận sóc sơn": (357652, 305.10),
    "quận thạch thất": (223844, 207.20),
    "quận thanh oai": (227541, 129.62),
    "quận thanh trì": (288839, 63.49),
    "quận thường tín": (262222, 127.70),
    "quận ứng hòa": (212224, 182.73),
}

def load_yaml(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def normalize_string(s):
    return s.strip().lower()

def distribute_value(total, n, random_factor=0.3):
    """
    Distribute a total value into n parts with some randomness.
    random_factor: 0 means equal distribution, 1 means extreme variance.
    """
    if n <= 0: return []
    if n == 1: return [total]

    # Generate random weights
    weights = [1.0 + random.uniform(-random_factor, random_factor) for _ in range(n)]
    sum_weights = sum(weights)

    # Distribute
    parts = [(w / sum_weights) * total for w in weights]

    return parts

def main():
    districts = load_yaml('districts.yml')
    wards = load_yaml('wards.yml')

    # Build lookup maps
    district_map = {normalize_string(d['name']): d['id'] for d in districts} # Full name key: "quận ba đình"
    district_map_short = {normalize_string(d['name'].replace('Quận ', '').replace('Huyện ', '').replace('Thị xã ', '')): d['id'] for d in districts}

    ward_map = {} # (District ID, Normalized Ward Name) -> Ward ID
    wards_by_district = {} # District ID -> List of Ward IDs

    for w in wards:
        key = (w['district_id'], normalize_string(w['name']))
        ward_map[key] = w['id']
        if w['district_id'] not in wards_by_district:
            wards_by_district[w['district_id']] = []
        wards_by_district[w['district_id']].append(w['name'])

    demographics_list = []
    processed_ward_ids = set()

    # 1. Process Provided CSV Data
    lines = raw_csv.strip().split('\n')
    for line in lines:
        parts = line.split(',')
        if len(parts) < 5:
            continue

        stt = parts[0]
        district_name_raw = parts[1]
        ward_name_raw = parts[2]
        pop_raw = parts[3].replace('"', '')
        density_raw = parts[4].replace('"', '')

        population = int(pop_raw.replace('.', ''))
        density = float(density_raw.replace('.', '')) / 1000.0

        d_name_clean = normalize_string(district_name_raw)

        # Try finding district ID (Short name mostly from CSV: "Bắc Từ Liêm")
        d_id = district_map_short.get(d_name_clean)
        if not d_id:
             # Try full name if user provided full name in CSV
            d_id = district_map.get(d_name_clean)

        if d_id:
            w_name_clean = normalize_string(ward_name_raw.replace('Phường ', '').replace('Xã ', '').replace('Thị trấn ', ''))
            w_key = (d_id, w_name_clean)
            w_id = ward_map.get(w_key)

            if w_id:
                demographics_list.append({
                    'id': int(stt),
                    'ward_id': w_id,
                    'population': population,
                    'density': round(density, 3)
                })
                processed_ward_ids.add(w_id)
            else:
                print(f"Ward not found: {ward_name_raw} in {district_name_raw}")
        else:
            print(f"District not found: {district_name_raw}")

    next_id = len(demographics_list) + 1

    # 2. Generate Data for Missing Districts
    for d_name, (d_pop, d_area) in MISSING_DISTRICT_DATA.items():
        # Find ID
        d_id = district_map.get(d_name)
        if not d_id:
             # Try reconstructing full name just in case mismatch
             print(f"Warning: Configured missing district '{d_name}' not found in structure.")
             continue

        # Get wards
        d_wards = wards_by_district.get(d_id, [])
        n_wards = len(d_wards)

        if n_wards == 0:
            print(f"No wards found for {d_name}")
            continue

        print(f"Generating data for {d_name} ({n_wards} wards, Pop: {d_pop}, Area: {d_area})")

        # Distribute Population and Area
        pop_parts = distribute_value(d_pop, n_wards, random_factor=0.2)
        area_parts = distribute_value(d_area, n_wards, random_factor=0.4)

        # Assign to wards
        for i, w_name in enumerate(d_wards):
            w_name_clean = normalize_string(w_name)
            w_id = ward_map.get((d_id, w_name_clean))

            if w_id and w_id not in processed_ward_ids:
                pop = int(pop_parts[i])
                area = area_parts[i]

                final_density = (pop / area) / 1000.0

                demographics_list.append({
                    'id': next_id,
                    'ward_id': w_id,
                    'population': pop,
                    'density': round(final_density, 3)
                })
                next_id += 1
                processed_ward_ids.add(w_id)

    # Write output
    with open('ward_demographics.yml', 'w', encoding='utf-8') as f:
        yaml.dump(demographics_list, f, allow_unicode=True, sort_keys=False)

    print(f"Generated ward_demographics.yml with {len(demographics_list)} entries.")

if __name__ == "__main__":
    main()
