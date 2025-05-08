from flask import Flask, request, render_template, redirect, url_for
import os
import tempfile
from parser.fileReader import extractText
from parser.nlpExtractor import nlpExtractor
from matcher.matchEngine import matchResumeToJob
from feedback.logger import logParse
from feedback.logger import logFeedback

app = Flask(__name__)

default_job = {
    "skillsRequired": [
        "Python", "Machine Learning", "Natural Language Processing (NLP)",
        "Data Visualization", "Deep Learning", "Statistical Analysis",
        "SQL", "Big Data", "Model Deployment"
    ],
    "experienceRequired": "3+ years in Data Science or a related field",
    "educationRequired": "Bachelor's or Master's degree in Computer Science, Data Science, or related field"
}

def build_default_job_text():
    return " ".join(default_job["skillsRequired"]) + " " + \
           default_job["experienceRequired"] + " " + \
           default_job["educationRequired"]

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload-resume', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        # Step 1: Handle file upload
        f = request.files.get('file')
        if not f:
            return "No file uploaded", 400

        # Save resume
        with tempfile.NamedTemporaryFile(delete=False, suffix=f.filename) as t:
            resume_path = t.name
            f.save(resume_path)

        # Step 2: Handle job description input
        if request.form.get('compare_option') == 'custom':
            jd = request.files.get('jd_file')
            if jd:
                with tempfile.NamedTemporaryFile(delete=False, suffix=jd.filename) as j:
                    jd_path = j.name
                    jd.save(jd_path)
                job_text = extractText(jd_path)
                os.remove(jd_path)
            else:
                job_text = build_default_job_text()
        else:
            job_text = build_default_job_text()

        # Step 3: Extract data from the resume and calculate the score
        resume_text = extractText(resume_path)
        entities, _, _ = nlpExtractor(resume_text)
        score = matchResumeToJob(resume_text, job_text)

        # Step 4: Prepare parsed data
        data = {
            "name": entities.get("NAME", ""),
            "email": (entities.get("EMAIL") or [""])[0],
            "phone": (entities.get("PHONE") or [""])[0],
            "skills": entities.get("SKILLS") or [],
            "education": entities.get("EDUCATION") or [],
            "experience": entities.get("EXPERIENCE_YEARS", ""),
            "score": f"{score:.2f}"
        }

        # Step 5: Log the parsed data and get the log file name
        log_fn = logParse(resume_text, data, score)

        # Clean up resume file
        os.remove(resume_path)

        # Pass log filename into the template for feedback collection
        return render_template('result.html', log_fn=log_fn, **data)

    return render_template('upload.html')

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    log_fn = request.form.get('log_fn')
    fb = request.form.get('feedback') == 'yes'
    if log_fn:
        logFeedback(log_fn, fb)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
