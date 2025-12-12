import unicodedata

def flexible_normalize(text):
    text = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    text = text.lower()
    return text

addr = "125 P. Hoàng Ngân, Trung Hoà, Cầu Giấy, Hà Nội, Vietnam"
ward = "Trung Hòa"

print(f"Address: {addr}")
print(f"Ward: {ward}")
print(f"Norm Address: {flexible_normalize(addr)}")
print(f"Norm Ward: {flexible_normalize(ward)}")

if flexible_normalize(ward) in flexible_normalize(addr):
    print("MATCH!")
else:
    print("NO MATCH")
