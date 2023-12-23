import re
def find_measurements(text):
    pattern = r'(\d+(\.\d+)?)\s*(kilogram|kilo|gram|liter|l|L|gr|g|kg|ml)'
    matches = re.findall(pattern, text)
    measurements = []
    for match in matches:
        value = float(match[0])
        unit = match[2]
        measurements.append(f"{value}{unit.lower()}")

    pattern_decimal_followed_by_char = r'(\d+\.\d+)\s*([a-zA-Z])'
    matches_decimal_followed_by_char = re.findall(pattern_decimal_followed_by_char, text)
    
    for match_decimal_followed_by_char in matches_decimal_followed_by_char:
        value = float(match_decimal_followed_by_char[0])
        unit = match_decimal_followed_by_char[1]
        measurements.append(f"{value}{unit.lower()}")
    
    if len(measurements) == 0:
        return None
    else:
        return measurements[0]

def remove_measurements(text):
    # Pola regex untuk mengenali pengukuran
    pattern = r'(\d+(\.\d+)?)\s*(kilogram|kilo|gram|liter|l|L|gr|g|kg|ml)'

    # Fungsi untuk menggantikan setiap pencocokan dengan string kosong
    def replace_measurement(match):
        return ''

    # Menggunakan re.sub dengan fungsi replace_measurement pada setiap pencocokan
    text_without_measurements = re.sub(pattern, replace_measurement, text)

    # Pola regex tambahan untuk mengenali pengukuran desimal yang diikuti oleh karakter
    pattern_decimal_followed_by_char = r'(\d+\.\d+)\s*([a-zA-Z])'

    # Menggunakan re.sub untuk menghapus pengukuran desimal yang diikuti oleh karakter
    text_without_measurements = re.sub(pattern_decimal_followed_by_char, '', text_without_measurements)

    return text_without_measurements.strip()