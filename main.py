import time
import requests
import joblib
import logging
import yaml
import tracemalloc
import psutil
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
from logging.handlers import RotatingFileHandler

# Load configuration from YAML file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Setup logging
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
log_file = 'app.log'
log_handler = RotatingFileHandler(log_file, maxBytes=1e6, backupCount=1)
log_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

# Configuration constants
ROBLOX_COOKIE = config['roblox']['cookie']
GROUP_ID = config['roblox']['group_id']
BASE_URL = config['fetching']['base_url'].format(group_id=GROUP_ID)
REQUEST_DELAY = config['fetching']['request_delay']
RATE_LIMIT_DELAY = config['fetching']['rate_limit_delay']
MAX_PAGES = config['fetching']['max_pages']
STARTING_PAGE = config['fetching']['starting_page']
BATCH_SIZE = config['fetching']['batch_size']
LOG_INTERVAL = config['performance']['log_interval']

# File paths
SCAM_COMMENTS_FILE = config['files']['scam_comments']
TFIDF_VECTORIZER_FILE = config['files']['tfidf_vectorizer']
SVM_CLASSIFIER_FILE = config['files']['svm_classifier']
BEST_PARAMS_FILE = config['files']['best_params']

# Classifier parameters
CLASSIFIER_PARAMS = config['classifier']

# Load machine learning models
vectorizer = joblib.load(TFIDF_VECTORIZER_FILE)
svm_classifier = joblib.load(SVM_CLASSIFIER_FILE)

HEADERS = {
    'Cookie': f'.ROBLOSECURITY={ROBLOX_COOKIE}',
    'Content-Type': 'application/json'
}

def preprocess_text(text: str) -> str:
    """Convert text to lowercase."""
    return text.lower()

def fetch_csrf_token() -> str:
    """Fetch CSRF token required for Roblox API requests."""
    response = requests.post('https://auth.roblox.com/v2/login', headers=HEADERS)
    if response.status_code in [200, 403]:
        return response.headers.get('x-csrf-token')
    else:
        raise Exception(f'Failed to fetch CSRF token: {response.text}')

def delete_post(post_id: int) -> None:
    """Delete a post from the group wall by its ID."""
    delete_url = f'https://groups.roproxy.com/v1/groups/{GROUP_ID}/wall/posts/{post_id}'
    response = requests.delete(delete_url, headers=HEADERS)
    if response.status_code == 200:
        logger.info(f'Successfully deleted post {post_id}.')
    else:
        logger.error(f'Failed to delete post {post_id}: {response.status_code} - {response.text}')

def fetch_group_wall_posts(cursor: str = None) -> dict:
    """Retrieve posts from the group wall."""
    url = BASE_URL
    if cursor:
        url += f"&cursor={cursor}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        logger.warning("Rate limit exceeded. Retrying after delay...")
        time.sleep(RATE_LIMIT_DELAY)
        return fetch_group_wall_posts(cursor)
    else:
        raise Exception(f'Error fetching posts: {response.text}')

def save_scam_comments(comments: list) -> None:
    """Save identified scam comments to a text file."""
    with open(SCAM_COMMENTS_FILE, 'w', encoding='utf-8') as file:
        for comment in comments:
            file.write(comment + '\n')

def is_scam(post: dict, vectorizer: TfidfVectorizer, classifier: Pipeline) -> tuple:
    """Determine if a post is a scam using the trained classifier."""
    content = post.get("body", "")
    processed_content = preprocess_text(content)
    transformed_content = vectorizer.transform([processed_content])
    prediction = classifier.predict(transformed_content)[0]
    probability = classifier.predict_proba(transformed_content)[0][1]
    return prediction, probability, processed_content

def optimize_classifier(vectorizer: TfidfVectorizer, data, labels):
    """Optimize the SVM classifier using GridSearchCV."""
    pipeline = Pipeline([
        ('tfidf', vectorizer),
        ('svc', SVC(probability=CLASSIFIER_PARAMS['probability']))
    ])

    param_grid = {
        'svc__C': [0.1, 1, 10],
        'svc__kernel': ['linear', 'rbf'],
    }

    grid_search = GridSearchCV(pipeline, param_grid, cv=5, n_jobs=-1, verbose=1)
    grid_search.fit(data, labels)

    logger.info(f"Best parameters found: {grid_search.best_params_}")
    joblib.dump(grid_search.best_params_, BEST_PARAMS_FILE)
    return grid_search.best_estimator_

def process_posts(posts, vectorizer, classifier, scam_comments, posts_processed):
    """Process each post and determine if it is a scam."""
    for post in posts:
        prediction, probability, content = is_scam(post, vectorizer, classifier)
        logger.info(f"Post ID: {post['id']}, Prediction: {'Scam' if prediction == 1 else 'Not a Scam'}, Probability: {probability:.4f}")

        if prediction == 1 and probability > 0.9:
            delete_post(post['id'])
            scam_comments.append(content)

        posts_processed += 1
        time.sleep(REQUEST_DELAY)

        if posts_processed >= MAX_PAGES * BATCH_SIZE:
            break

    return posts_processed

def log_performance_metrics(start_time):
    """Log performance metrics at regular intervals."""
    current, peak = tracemalloc.get_traced_memory()
    cpu_usage = psutil.cpu_percent()
    mem_usage = psutil.virtual_memory().percent
    logger.info(f"Memory usage: {current / 10**6:.2f}MB; Peak: {peak / 10**6:.2f}MB; CPU usage: {cpu_usage}%; Memory usage: {mem_usage}%")
    execution_time = time.time() - start_time
    logger.info(f"Execution time: {execution_time:.2f} seconds")

def main_loop():
    """Main loop to fetch and process posts from the group wall."""
    try:
        HEADERS['X-CSRF-TOKEN'] = fetch_csrf_token()
        
        logger.info("Starting to fetch group wall posts...")
        scam_comments = []
        posts_processed = 0
        page_number = STARTING_PAGE
        cursor = None

        # Performance monitoring
        tracemalloc.start()
        start_time = time.time()

        while page_number < STARTING_PAGE + MAX_PAGES:
            logger.info(f"Fetching page {page_number}...")
            response_data = fetch_group_wall_posts(cursor)
            posts = response_data.get('data', [])

            posts_processed = process_posts(posts, vectorizer, svm_classifier, scam_comments, posts_processed)
            
            cursor = response_data.get('nextPageCursor')
            if not cursor:
                logger.info("No more pages to fetch.")
                break

            if page_number % LOG_INTERVAL == 0:
                log_performance_metrics(start_time)
            
            page_number += 1

        save_scam_comments(scam_comments)
        logger.info(f"Total posts processed: {posts_processed}")
        log_performance_metrics(start_time)

    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error: {req_err}")
    except Exception as gen_err:
        logger.error(f"An error occurred: {gen_err}")

if __name__ == "__main__":
    main_loop()
