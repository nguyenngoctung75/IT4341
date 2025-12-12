import re
import yaml

raw_text = """
Quận Ba Đình gồm các phường: Trúc Bạch, Vĩnh Phúc, Cống Vị, Điện Biên, Kim Mã, Liễu Giai, Đội Cấn, Ngọc Hà, Phúc Xá, Quán Thánh, Giảng Võ, Ngọc Khánh, Thành Công và Nguyễn Trung Trực

quận Đống Đa: Cát Linh, Hàng Bột, Kim Liên, Láng Hạ, Khâm Thiên, Khương Thượng, Láng Thượng, Ô Chợ Dừa, Phương Liên, Nam Đồng, Ngã Tư Sở, Phương Mai, Quang Trung, Thổ Quan, Trung Liệt, Quốc Tử Giám, Thịnh Quang, Trung Phụng, Trung Tự, Văn Miếu và Văn Chương.

quận Bắc Từ Liêm:  Cổ Nhuế 1, Cổ Nhuế 2, Thụy Phương, Liên Mạc, Đức Thắng, Đông Ngạc, Thượng Cát, Tây Tựu, Phúc Diễn, Minh Khai, Phú Diễn, Xuân Đỉnh và Xuân Tảo.

quận Hoàn Kiếm: Chương Dương, Cửa Đông, Hàng Bạc, Hàng Bài, Cửa Nam, Đồng Xuân, Hàng Bồ, Hàng Bông, Hàng Buồm, Hàng Mã, Hàng Trống, Hàng Đào, Hàng Gai, Lý Thái Tổ, Phan Chu Trinh, Tràng Tiền, Phúc Tân và Trần Hưng Đạo.

quận Hoàng Mai:  Mai Hùng, Quỳnh Dị, Quỳnh Xuân, Quỳnh Phương và Quỳnh Thiện, Quỳnh Trang, Quỳnh Lập, Quỳnh Vinh, Quỳnh Liên và Quỳnh Lộc.

 quận Cầu Giấy : Dịch Vọng, Dịch Vọng Hậu, Nghĩa Tân, Quan Hoa, Mai Dịch, Nghĩa Đô, Trung Hòa và Yên Hòa.

quận Hà Đông: Biên Giang, Đồng Mai, Hà Cầu, La Khê, Mộ Lao, Yên Nghĩa, Dương Nội, Nguyễn Trãi, Phú La, Kiến Hưng, Phúc La, Phú Lãm, Phú Lương, Quang Trung, Vạn Phúc, Yết Kiêu và Văn Quán

quận Nam Từ Liêm: Cầu Diễn, Phú Đô, Mễ Trì, Mỹ Đình 1, Mỹ Đình 2, Đại Mỗ, Phương Canh, Xuân Phương và Tây Mỗ.

quận Hai Bà Trưng:  Bách Khoa, Bạch Đằng, Đống Mác, Đồng Nhân, Bạch Mai, Cầu Dền, Đồng Tâm, Lê Đại Hành, Minh Khai, Nguyễn Du, Quỳnh Lôi, Phạm Đình Hổ, Phố Huế, Quỳnh Mai, Trương Định, Vĩnh Tuy, Thanh Lương và Thanh Nhàn.

quận Tây Hồ:  Bưởi, Nhật Tân, Phú Thượng, Tứ Liên, Xuân La, Quảng An, Thụy Khuê và Yên Phụ.

quận Long Biên: Bồ Đề, Cự Khối, Giang Biên, Long Biên, Đức Giang, Gia Thụy, Phúc Đồng, Phúc Lợi, Ngọc Lâm, Ngọc Thụy, Sài Đồng, Thạch Bàn, Việt Hưng và Thượng Thanh.

quận Thanh Xuân:  Hạ Đình, Khương Đình, Khương Trung, Khương Mai, Kim Giang, Nhân Chính, Thanh Xuân Bắc, Thanh Xuân Nam, Phương Liệt, Thanh Xuân Trung và Thượng Đình.

quận Gia Lâm: Trâu Quỳ, Yên Viên,  Cổ Bi, Đặng Xá, Dương Quang, Kim Sơn, Dương Xá, Phú Thị, Đông Dư, Văn Đức, Lệ Chi, Đa Tốn, Kim Lan, Kiêu Kỵ, Bát Tràng, Yên Viên, Ninh Hiệp, Yên Thường, Dương Hà, Đình Xuyên, Phù Đổng, Trung Mầu.


quận Ứng Hòa: Vân Đình,  Cao Thành, Đông Lỗ, Đại Cường, Đồng Tiến, Đại Hùng, Đồng Tân, Hoa Sơn, Đội Bình, Hòa Phú, Hòa Xá, Hòa Nam, Hồng Quang, Hòa Lâm, Kim Đường, Minh Đức, Phương Tú, Liên Bạt, Phù Lưu, Lưu Hoàng, Quảng Phú Cầu, Trường Thịnh, Tảo Dương Văn, Sơn Công, Trung Tú, Trầm Lộng, Viên Nội, Vạn Thái và Viên An.

quận Mỹ Đức: Đại Nghĩa,  An Mỹ, An Phú, Đại Hưng, Đốc Tín, An Tiến, Bột Xuyên, Đồng Tâm, Hồng Sơn, Hùng Tiến, Hương Sơn, Hợp Thanh, Hợp Tiến, Lê Thanh, Mỹ Thành, Thượng Lâm, Tuy Lai, Phù Lưu Tế, Phúc Lâm, Phùng Xá, Vạn Kim và Xuy Xá.

quận Thanh Oai:  Kim Bài,  Bích Hòa, Bình Minh, Cự Khê, Dân Hòa, Cao Dương, Hồng Dương, Liên Châu, Cao Viên, Đỗ Động, Mỹ Hưng, Kim An, Tam Hưng, Kim Thư, Phương Trung, Thanh Mai, Tân Ơc, Thanh Cao, Thanh Thùy, Thanh Văn và Xuân Dương.

quận Phúc Thọ: Phúc Thọ, Liên Hiệp, Long Xuyên, Hát Môn, Hiệp Thuận, Ngọc Tảo, Phúc Hòa, Tam Hiệp, Tam Thuấn, Phụng Thượng, Sen Phương, Thanh Đa, Thọ Lộc, Trạch Mỹ Lộc, Vân Hà, Vân Nam, Thượng Cốc, Tích Giang, Vân Phúc, Võng Xuyên và Xuân Đình.

quận Ba Vì: Tây Đằng, Ba Trại, Ba Vì, Châu Sơn, Chu Minh, Cẩm Lĩnh, Đồng Thái, Cam Thượng, Khánh Thượng, Cổ Đô, Minh Châu, Đông Quang, Minh Quang, Phú Cường, Phong Vân, Phú Châu, Phú Đông, Phú Phương, Tản Lĩnh, Phú Sơn, Thái Hòa, Tản Hồng, Thuần Mỹ, Sơn Đà, Thụy An, Vạn Thắng, Tiên Phong, Vân Hòa, Tòng Bạt, Yên Bài, và Vật Lại.

quận Thạch Thất:  Liên Quan, Bình Phú, Bình Yên, Canh Nậu, Chàng Sơn, Cần Kiệm, Cẩm Yên, Đại Đồng, Hữu Bằng, Kim Quan, Dị Nậu, Đồng Trúc, Hương Ngải, Hạ Bằng, Lại Thượng, Phú Kim, Thạch Xá, Tân Xã, Phùng Xá, Thạch Hòa, Tiến Xuân, Yên Trung, và Yên Bình.

Quận Sơn Tây: Phú Thịnh, Quang Trung, Lê Lợi, Ngô Quyền, Sơn Lộc, Trung Hưng, Trung Sơn Trầm, Xuân Khanh, Viên Sơn, Cổ Đông, Xuân Sơn, Kim Sơn, Đường Lâm, Thanh Mỹ và Sơn Đông.

Quận Chương Mỹ gồm Chúc Sơn , Xuân Mai, Đại Yên, Đông Phương Yên, Đồng Phú, Hòa Chính, Đồng Lạc, Hoàng Diệu, Đông Sơn, Hoàng Văn Thụ, Lam Điền, Hữu Văn, Hồng Phong, Mỹ Lương, Hợp Đồng, Nam Phương Tiến, Phụng Châu, Phú Nghĩa, Ngọc Hòa, Quảng Bị, Phú Nam An, Tân Tiến, Thanh Bình, Tiên Phương, Thủy Xuân Tiên, Tốt Động, Thượng Vực, Thụy Hương, Trường Yên, Trần Phú, Văn Võ, và Trung Hòa.

Quận Đông Anh : Đông Anh ,Bắc Hồng, Cổ Loa, Dục Tú, Xuân Nộn, Hải Bối, Đại Mạch, Đông Hội, Võng La, Kim Chung, Kim Nỗ, Liên Hà, Mai Lâm, Tàm Xá, Nguyên Khê, Thụy Lâm, Vân Nội, Tiên Dương, Việt Hùng, Xuân Canh, Nam Hồng, Vân Hà, và Uy Nỗ.

Quận Quốc Oai:  Quốc Oai ,Cấn Hữu, Đông Yên, Đại Thành, Đồng Quang, Hòa Thạch, Liệp Tuyết, Nghĩa Hương, Phú Mãn, Ngọc Liệp, Phượng Cách, Sài Sơn, Ngọc Mỹ, Thạch Thán, Tân Hòa, Tuyết Nghĩa, Tân Phú, Yên Sơn, Đông Xuân, Cộng Hòa, và Phú Cát.

Quận Hoài Đức : Trạm Trôi , An Khánh, Di Trạch, Đông La, An Thượng, Cát Quế, Đắc Sở, Đức Thượng, Lại Yên, Dương Liễu, La Phù, Kim Chung, Sơn Đồng, Vân Canh, Minh Khai, Song Phương, Tiền Yên, Vân Côn, Yên Sở, và Đức Giang.

Quận Thanh Trì:  Văn Điển  , Đại Áng, Liên Ninh, Đông Mỹ, Ngọc Hồi, Hữu Hòa, Duyên Hà, Ngũ Hiệp, Tả Thanh Oai, Tứ Hiệp, Thanh Liệt, Tam Hiệp, Tân Triều, Vĩnh Quỳnh, Yên Mỹ, và Vạn Phúc.

quận Mê Linh: Chi Đông, Quang Minh, Hoàng Kim, Kim Hoa, Chu Phan, Đại Thịnh, Liên Mạc, Mê Linh, Tiền Phong, Thanh Lâm, Tam Đồng, Tiến Thắng, Thạch Đà, Tiến Thịnh, Vạn Yên, Tráng Việt, Văn Khê,  Tự Lập

quận Đan Phượng: Phùng, Đan Phượng, Đồng Tháp, Liên Hà, Liên Hồng, Hạ Mỗ, Hồng Hà, Liên Trung, Tân Lập, Song Phượng, Phương Đình, Thọ An, Trung Châu, Thọ Xuân, Thượng Mỗ, và Tân Hội

quận Phú Xuyên: Phú Xuyên, Phú Minh, Hoàng Long, Hồng Minh, Hồng Thái, Đại Thắng, Chuyên Mỹ, Đại Xuyên, Minh Tân, Nam Triều, Khai Thái, Phú Túc, Nam Phong, Phúc Tiến, Quang Trung, Phú Yên, Sơn Hà, Quang Lãng, Phượng Dực, Tân Dân, Vân Từ, Tri Thủy, Tri Trung, Bạch Hạ, Văn Hoàng, Châu Can, và Nam Tiến.

quận Sóc Sơn: Sóc Sơn, Đông Xuân, Đức Hòa, Bắc Phú, Bắc Sơn, Hiền Ninh, Hồng Kỳ, Minh Phú, Minh Trí, Kim Lũ, Mai Đình, Nam Sơn, Phú Cường, Quang Tiến, Phù Lỗ, Tân Dân, Phù Linh, Tân Hưng, Tiên Dược, Tân Minh, Thanh Xuân, Trung Giã, Việt Long, Xuân Thu, Xuân Giang, và Phú Minh.

quận Thường Tín: Thường Tín, Hòa Bình, Chương Dương, Hiền Giang, Dũng Tiến, Duyên Thái, Hà Hồi, Khánh Hà, Hồng Vân, Minh Cường, Nghiêm Xuyên, Lê Lợi, Liên Phương, Nguyễn Trãi, Quất Động, Tân Minh, Nhị Khê, Ninh Sở, Thắng Lợi, Thống Nhất, Tô Hiệu, Thư Phú, Tiền Phong, Tự Nhiên, Vạn Điểm, Văn Tự, Văn Bình, Văn Phú, và Vân Tảo.
"""

districts_list = []
wards_list = []
district_id_counter = 1
ward_id_counter = 1

# Normalize text
lines = raw_text.strip().split('\n')

for line in lines:
    line = line.strip()
    if not line:
        continue

    # Regex to capture District Name and Wards part
    # Matches "Quận X..." or "quận Y..."
    # Tries to handle separators like ":", "gồm các phường:", "gồm"
    match = re.match(r'(?:Quận|quận)\s+([^:]+?)\s*(?:gồm các phường|:|gồm)\s*(.*)', line, re.IGNORECASE)

    if match:
        district_name = match.group(1).strip()
        wards_str = match.group(2).strip().lstrip(':').strip()

        # Clean district name further if it has trailing stuff?
        # The regex [^:]+ might capture spaces, user input is fairly clean though.

        districts_list.append({
            'id': district_id_counter,
            'name': 'Quận ' + district_name if not district_name.lower().startswith('thị xã') else district_name
        })

        # Process wards
        # Wards are separated by comma (,), " và ", or just " " if OCR error but user used commas mostly.
        # User input uses ", " and " và " and "." at the end.

        # Replace " và " with "," and remove "."
        wards_clean = wards_str.replace(' và ', ', ').replace('.', '').replace(';', ',')
        ward_names = [w.strip() for w in wards_clean.split(',')]

        for w_name in ward_names:
            if w_name:
                wards_list.append({
                    'id': ward_id_counter,
                    'district_id': district_id_counter,
                    'name': w_name
                })
                ward_id_counter += 1

        district_id_counter += 1

# Write to YAML
with open('districts.yml', 'w', encoding='utf-8') as f:
    yaml.dump(districts_list, f, allow_unicode=True, sort_keys=False)

with open('wards.yml', 'w', encoding='utf-8') as f:
    yaml.dump(wards_list, f, allow_unicode=True, sort_keys=False)

print(f"Generated districts.yml with {len(districts_list)} districts.")
print(f"Generated wards.yml with {len(wards_list)} wards.")
