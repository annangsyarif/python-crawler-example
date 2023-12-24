# Fungsi untuk menyusun hasil dalam format yang diinginkan untuk productprice
def format_product_price_results(alldata, productmaster):
    productprice = []
    for _,data in alldata.iterrows():
        item = data.to_dict()
        for _,unique_product in productmaster.iterrows():
            if data['name'] in unique_product['occurrences']:
                item['productmaster_id'] = unique_product['id']
        
        productprice.append(item)
    
    return productprice