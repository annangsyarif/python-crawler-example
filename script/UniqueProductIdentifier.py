from nltk import word_tokenize
import nltk
from script.FindMeasurements import remove_measurements
from nltk.corpus import stopwords

nltk.download('punkt')

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class UniqueProductIdentifier:
    def __init__(self):
        self.unique_products = []

    def preprocess_text(self, text):
        # Tokenisasi dan konversi ke huruf kecil
        tokens = word_tokenize(text.lower())
        
        # Hapus stop words
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token.isalnum() and token not in stop_words]
        
        return tokens


    def jaccard_similarity(self, set1, set2):
        intersection = len(set(set1) & set(set2))
        union = len(set(set1) | set(set2))
        return intersection / union if union != 0 else 0
    
    def representative_sentence(self, tokens1, tokens2):
        common_tokens = [token for token in tokens1 if token in tokens2]
        representative_sentence = " ".join(common_tokens) 

        return representative_sentence

    def identify_unique_products_dataframe(self, df, productmaster_df):
        id = 0
        if productmaster_df is not None:
            self.unique_products = productmaster_df.to_dict(orient="records")
        
        for _, product in df.iterrows():
            name = remove_measurements(product['name'].lower()).replace("-", "").replace("  "," ")
            tokens = self.preprocess_text(name)

            # similarity check
            found = False
            if len(self.unique_products) > 0:
                for unique_product in self.unique_products:
                    similarity = self.jaccard_similarity(tokens, unique_product['tokens'])
                    if similarity > 0.5 and (product['detail'] == unique_product['detail']):
                        found = True
                        unique_product['occurrences'].append(product['name'])
                        unique_product['name'] = self.representative_sentence(tokens, unique_product['tokens'])
                        slice_ = list(set(tokens) - set(unique_product['tokens']))
                        for val_ in slice_:
                            unique_product['tokens'].append(val_)
                        break

            # handle new product
            if not found:
                id += 1
                self.unique_products.append({
                    'name': name,
                    'id': id,
                    'tokens': tokens,
                    'detail': product['detail'],
                    'occurrences': [product['name']]
                })

        return self.unique_products