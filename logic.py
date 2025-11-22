import pandas as pd
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import generate_data  # Import the generation script

class EntityResolver:
    def __init__(self, crm_file="crm_database.csv"):
        # AUTO-FIX: Generate data if missing
        if not os.path.exists(crm_file):
            print(f"⚠️ {crm_file} not found. Generating data now...")
            generate_data.generate_data()
            
        self.df_crm = pd.read_csv(crm_file)
        self.graph = nx.Graph()
        self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
        
        # Pre-compute vectors
        # Fill NaNs to avoid crashes
        self.df_crm['name'] = self.df_crm['name'].fillna('')
        self.df_crm['company'] = self.df_crm['company'].fillna('')
        
        self.df_crm['combined_features'] = self.df_crm['name'] + " " + self.df_crm['company']
        self.crm_vectors = self.vectorizer.fit_transform(self.df_crm['combined_features'])
        
        self._build_initial_graph()

    def _build_initial_graph(self):
        for _, row in self.df_crm.iterrows():
            self.graph.add_node(row['name'], type='Person', crm_id=row['crm_id'])
            self.graph.add_node(row['company'], type='Company')
            self.graph.add_edge(row['name'], row['company'], relation='WORKS_AT')

    def resolve_entity(self, messy_text, threshold=0.6):
        try:
            query_vec = self.vectorizer.transform([messy_text])
            similarity_scores = cosine_similarity(query_vec, self.crm_vectors)
            
            best_match_idx = similarity_scores.argmax()
            best_score = similarity_scores[0, best_match_idx]
            
            result = {
                "input_text": messy_text,
                "match_found": False,
                "match_score": float(best_score),
                "match_details": {}
            }

            if best_score > threshold:
                matched_row = self.df_crm.iloc[best_match_idx]
                result["match_found"] = True
                result["match_details"] = matched_row.to_dict()
                
                # Graph Logic
                company_node = matched_row['company']
                if self.graph.has_node(company_node):
                    colleagues = [n for n in self.graph.neighbors(company_node) if n != matched_row['name']]
                    result["potential_colleagues"] = colleagues[:3]
            
            return result
        except Exception as e:
            return {"error": str(e), "match_found": False}

# Initialize
resolver = EntityResolver()