from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def matchResumeToJob(resumeText, jobDescriptionText, topN=5):
    vectorizer = TfidfVectorizer()
    tfidfMatrix = vectorizer.fit_transform([resumeText, jobDescriptionText])
    return cosine_similarity(tfidfMatrix[0:1], tfidfMatrix[1:2])[0][0]

def rankCandidates(resumes, jobDescription):
    scores = []
    for cid, text in resumes:
        sim = matchResumeToJob(text, jobDescription)
        scores.append((cid, sim))
    return sorted(scores, key=lambda x: x[1], reverse=True)