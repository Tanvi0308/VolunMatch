import math
from collections import Counter
from db import get_db_connection
from nlp_matcher import extract_keywords

# --- Pure Python TF-IDF and Cosine Similarity implementation ---
def compute_tf(text):
    words = text.lower().split()
    tf_dict = Counter(words)
    total_words = len(words)
    for word in tf_dict:
        tf_dict[word] = tf_dict[word] / float(total_words) if total_words > 0 else 0
    return tf_dict

def compute_idf(documents):
    N = len(documents)
    idf_dict = {}
    all_words = set(word for doc in documents for word in doc.lower().split())
    
    for word in all_words:
        count = sum(1 for doc in documents if word in doc.lower().split())
        idf_dict[word] = math.log((1 + N) / (1 + count)) + 1 # scikit-learn smooth idf
    return idf_dict

def compute_tfidf(tf_dict, idf_dict):
    tfidf = {}
    for word, tf in tf_dict.items():
        tfidf[word] = tf * idf_dict.get(word, 0)
    
    # Normalize (L2)
    norm = math.sqrt(sum(val ** 2 for val in tfidf.values()))
    if norm > 0:
        for word in tfidf:
            tfidf[word] = tfidf[word] / norm
    return tfidf

def cosine_sim(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])
    
    sum1 = sum([val**2 for val in vec1.values()])
    sum2 = sum([val**2 for val in vec2.values()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    
    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

class RecommenderEngine:
    def __init__(self):
        self.volunteer_profiles = {}
        self.project_profiles = {}
        self.volunteer_data = {}
        self.project_data = {}
        
    def load_data(self):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Load Volunteers
            cursor.execute("""
                SELECT v.id, v.name, GROUP_CONCAT(s.name, ' ') as skills
                FROM volunteers v
                LEFT JOIN volunteer_skills vs ON v.id = vs.volunteer_id
                LEFT JOIN skills s ON vs.skill_id = s.id
                WHERE v.is_admin = 0
                GROUP BY v.id
            """)
            for row in cursor.fetchall():
                self.volunteer_data[row['id']] = row
                skills_text = str(row['skills']) if row['skills'] else ''
                self.volunteer_profiles[row['id']] = skills_text
                
            # Load Projects
            cursor.execute("""
                SELECT p.id, p.title, p.description, GROUP_CONCAT(s.name, ' ') as skills
                FROM projects p
                LEFT JOIN project_skills ps ON p.id = ps.project_id
                LEFT JOIN skills s ON ps.skill_id = s.id
                GROUP BY p.id
            """)
            for row in cursor.fetchall():
                self.project_data[row['id']] = row
                desc = str(row['description']) if row['description'] else ''
                explicit_skills = str(row['skills']) if row['skills'] else ''
                extracted_skills = extract_keywords(desc)
                self.project_profiles[row['id']] = f"{explicit_skills} {' '.join(extracted_skills)}"
                
        finally:
            conn.close()

    def _get_similarities(self, target_text, corpus_dict):
        all_texts = [target_text] + list(corpus_dict.values())
        idf_dict = compute_idf(all_texts)
        
        target_tf = compute_tf(target_text)
        target_tfidf = compute_tfidf(target_tf, idf_dict)
        
        scores = []
        for doc_id, doc_text in corpus_dict.items():
            if not doc_text.strip():
                scores.append((doc_id, 0.0))
                continue
                
            doc_tf = compute_tf(doc_text)
            doc_tfidf = compute_tfidf(doc_tf, idf_dict)
            sim = cosine_sim(target_tfidf, doc_tfidf)
            scores.append((doc_id, sim))
            
        return sorted(scores, key=lambda x: x[1], reverse=True)

    def recommend_projects_for_volunteer(self, volunteer_id, top_n=5):
        self.load_data()
        if volunteer_id not in self.volunteer_profiles or not self.project_profiles:
            return []
            
        vol_text = self.volunteer_profiles[volunteer_id]
        if not vol_text.strip(): return []
        
        top_projects = self._get_similarities(vol_text, self.project_profiles)[:top_n]
        
        results = []
        for p_id, score in top_projects:
            if score > 0:
                p_data = self.project_data[p_id]
                results.append({
                    'id': p_id,
                    'title': p_data['title'],
                    'description': p_data['description'],
                    'skills': p_data['skills'],
                    'match_score': round(score * 100, 1)
                })
        return results

    def recommend_volunteers_for_project(self, project_id, top_n=5):
        self.load_data()
        if project_id not in self.project_profiles or not self.volunteer_profiles:
            return []
            
        proj_text = self.project_profiles[project_id]
        if not proj_text.strip(): return []
        
        top_vols = self._get_similarities(proj_text, self.volunteer_profiles)[:top_n]
        
        results = []
        for v_id, score in top_vols:
            if score > 0:
                v_data = self.volunteer_data[v_id]
                results.append({
                    'id': v_id,
                    'name': v_data['name'],
                    'skills': v_data['skills'],
                    'match_score': round(score * 100, 1)
                })
        return results

engine = RecommenderEngine()

def get_project_recommendations(volunteer_id, top_n=5):
    return engine.recommend_projects_for_volunteer(volunteer_id, top_n)

def get_volunteer_recommendations(project_id, top_n=5):
    return engine.recommend_volunteers_for_project(project_id, top_n)
