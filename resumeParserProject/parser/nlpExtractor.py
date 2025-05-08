import spacy
import re

defaultNlp = spacy.load("en_core_web_md")

knownSkills = [
    "Python", "Java", "C#", "C++", "JavaScript", "TypeScript",
    "HTML", "CSS", "SQL", "NoSQL", "R", "MATLAB", "Scala",
    "Go", "Kotlin", "Swift", "Objective-C", "PHP", "Ruby",
    "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas", "NumPy", "SciPy",
    "NLTK", "spaCy", "OpenCV", "Tableau", "Power BI", "Excel",
    "Hadoop", "Spark", "Flink", "Hive", "Pig", "Kafka", "HBase",
    "Docker", "Kubernetes", "AWS", "Azure", "Google Cloud Platform", "GCP",
    "Linux", "Unix", "Git", "SVN", "Jenkins", "CI/CD", "Ansible", "Terraform",
    "REST", "GraphQL", "Microservices", "SOAP",
    "React", "Angular", "Vue.js", "Node.js", "Express.js", "Django", "Flask",
    "Spring", "Spring Boot", "Ruby on Rails", "Laravel",
    "Blockchain", "Ethereum", "Hyperledger", "Smart Contracts",
    "AWS Lambda", "Serverless", "BigQuery", "Redshift", "Snowflake",
    "PowerShell", "Bash", "SAS", "Looker", "Qlik",
    "Elasticsearch", "Logstash", "Kibana", "Prometheus", "Grafana",
]
educationKeywords = ["B.Tech", "M.Tech", "Bachelor", "Master", "PhD", "MCA", "BSC"]


def cleanText(text):
    if isinstance(text, str):
        return text.replace("  ", " ").strip()
    return str(text).replace("  ", " ").strip()


def extractNameFromText(text):
    doc = defaultNlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON" and not any(ch.isdigit() for ch in ent.text):
            return ent.text.strip()
    return text.split('\n', 1)[0].strip()


def extractCustomEntities(text):
    emails = re.findall(r"\b[\w.-]+?@\w+?\.\w+?\b", text)
    phones = re.findall(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", text)
    name = extractNameFromText(text)
    return {"EMAIL": emails, "PHONE": phones, "NAME": name}


def extractSkills(cleanedText, nounPhrases):
    found = set()
    for skill in knownSkills:
        if re.search(rf"\b{re.escape(skill)}\b", cleanedText, flags=re.IGNORECASE):
            found.add(skill)
    for phrase in nounPhrases:
        for skill in knownSkills:
            if skill.lower() in phrase.lower():
                found.add(skill)
    return list(found)


def extractEducation(cleanedText, nounPhrases):
    found = set()
    
    degreePatterns = [
        r"(BSC(?:[\.\s]?of\sScience)?\s+[A-Za-z &]+)",
        r"(B\.Tech\s+[A-Za-z &]+)",
        r"(M\.Tech\s+[A-Za-z &]+)",
        r"(Bachelor(?: of [A-Za-z &]+))", 
        r"(Master(?: of [A-Za-z &]+))"
    ]
    for pattern in degreePatterns:
        matches = re.findall(pattern, cleanedText, flags=re.IGNORECASE)
        for m in matches:
            found.add(m.strip())

    for phrase in nounPhrases:
        for degree in educationKeywords:
            if re.search(rf"\b{re.escape(degree)}\b", phrase, flags=re.IGNORECASE):
     
                if len(phrase.split()) > 1:
                    found.add(phrase.strip())
                else:
                    found.add(degree)
    return list(found)


def extractExperience(cleanedText):
    matches = re.findall(r"(\d+\+?)\s*(years|yrs|year)", cleanedText.lower())
    if matches:
        return matches[0][0]
    rangeMatch = re.search(r"(\d{4})\s*[-–]\s*(Present|\d{4})", cleanedText)
    if rangeMatch:
        return f"{rangeMatch.group(1)}-{rangeMatch.group(2)}"
    return None


def extractDates(cleanedText):
    pattern = (r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?"
               r"|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)(?:[\s\-]\d{4})?")
    return list(set(re.findall(pattern, cleanedText, flags=re.IGNORECASE)))


def nlpExtractor(rawText):
    cleaned = cleanText(rawText)
    doc = defaultNlp(cleaned)
    entities = {}
    for ent in doc.ents:
        if ent.label_ in ("PERSON", "ORG") and not any(ch.isdigit() for ch in ent.text):
            entities.setdefault(ent.label_, []).append(ent.text.strip())
    entities.update(extractCustomEntities(cleaned))
    nounPhrases = [chunk.text for chunk in doc.noun_chunks
                   if len(chunk.text.split()) > 1 and not any(substr in chunk.text for substr in ["|", "http", "linkedin", ".com"])]
    verbs = [token.text for token in doc if token.pos_ == "VERB"]
    skills = extractSkills(cleaned, nounPhrases)
    education = extractEducation(cleaned, nounPhrases)
    experience = extractExperience(cleaned)
    dates = extractDates(cleaned)
    if skills:
        entities["SKILLS"] = skills
    if education:
        entities["EDUCATION"] = education
    if experience:
        entities["EXPERIENCE_YEARS"] = experience
    if dates:
        entities["DATES"] = dates
    return entities, nounPhrases, verbs