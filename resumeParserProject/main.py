import parser.fileReader as fileReader
import parser.nlpExtractor as nlpExtract
import matcher.matchEngine as matchEngine

def parse_resume(resumePath):
    resumeText = fileReader.extractText(resumePath)
    entities, nounPhrases, verbs = nlpExtract.nlpExtractor(resumeText)
    name = entities.get("NAME")
    email = entities.get("EMAIL")
    phone = entities.get("PHONE")
    skills = entities.get("SKILLS")
    education = entities.get("EDUCATION")
    experience = entities.get("EXPERIENCE_YEARS")

    jobDescription = {
        "jobTitle": "Data Scientist",
        "department": "Data Science",
        "location": "Remote",
        "skillsRequired": [
            "Python", "Machine Learning", "Natural Language Processing (NLP)", 
            "Data Visualization", "Deep Learning", "Statistical Analysis", 
            "SQL", "Big Data", "Model Deployment"
        ],
        "experienceRequired": "3+ years in Data Science or a related field",
        "educationRequired": "Bachelor's or Master's degree in Computer Science, Data Science, or related field"
    }

    jobText = " ".join(jobDescription['skillsRequired']) + " " + jobDescription['experienceRequired'] + " " + jobDescription['educationRequired']
    score = matchEngine.matchResumeToJob(resumeText, jobText)

    return {
        "name": name,
        "email": email[0] if email else 'N/A',
        "phone": phone[0] if phone else 'N/A',
        "skills": skills,
        "education": education,
        "experience": experience,
        "score": score
    }
