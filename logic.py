import pandas as pd
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import generate_data

class EntityResolver:
    def __init__(self, crm_file="crm_database.csv"):
        # Auto-generate if missing
        if not os.path.exists(crm_file):
            print("Generating data...")
            generate_data.generate_data()
            
        self.crm_file = crm_file
        self.load_db()

    def load_db(self):
        """Reloads the database from CSV"""
        self.df_crm = pd.read_csv(self.crm_file).fillna('')
        self.graph = nx.Graph()
        self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
        
        # Create fingerprints
        self.df_crm['combined_features'] = self.df_crm['name'] + " " + self.df_crm['company']
        self.crm_vectors = self.vectorizer.fit_transform(self.df_crm['combined_features'])
        self._build_initial_graph()

    def _build_initial_graph(self):
        for _, row in self.df_crm.iterrows():
            self.graph.add_node(row['name'], type='Person')
            self.graph.add_node(row['company'], type='Company')
            self.graph.add_edge(row['name'], row['company'], relation='WORKS_AT')

    def get_db_preview(self):
        """Returns top 5 rows and total count for transparency"""
        return {
            "total_records": len(self.df_crm),
            "preview": self.df_crm.head(5).to_dict(orient='records'),
            "filename": self.crm_file
        }

    def bulk_resolve(self, df_messy):
        """
        Takes a DataFrame of messy leads and resolves them all.
        Returns a list of results for the UI.
        """
        results = []
        # Assume the column to clean is the first string column we find, or 'raw_text'
        col_to_clean = df_messy.columns[0] 
        
        for _, row in df_messy.iterrows():
            text = str(row[col_to_clean])
            match_result = self.resolve_single(text)
            
            results.append({
                "original": text,
                "suggested_name": match_result['match_details'].get('name', 'No Match'),
                "suggested_company": match_result['match_details'].get('company', '-'),
                "score": match_result['match_score'],
                "confidence": "High" if match_result['match_score'] > 0.8 else "Low"
            })
        return results

    def resolve_single(self, messy_text):
        # Optimized single resolution
        try:
            query_vec = self.vectorizer.transform([messy_text])
            similarity_scores = cosine_similarity(query_vec, self.crm_vectors)
            best_match_idx = similarity_scores.argmax()
            best_score = float(similarity_scores[0, best_match_idx])
            
            result = {"match_score": best_score, "match_details": {}}
            
            if best_score > 0.6: # Threshold
                result["match_details"] = self.df_crm.iloc[best_match_idx].to_dict()
                
            return result
        except:
            return {"match_score": 0.0, "match_details": {}}

resolver = EntityResolver()