import joblib
import requests
import pandas as pd
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline

ROBLOX_COOKIE = 'CookieHere'
GROUP_ID = 123456
BASE_URL = f'https://groups.roblox.com/v2/groups/{GROUP_ID}/wall/posts?SortOrder=Desc'
HEADERS = {
    'Cookie': f'.ROBLOSECURITY={ROBLOX_COOKIE}',
    'Content-Type': 'application/json',
    'X-CSRF-TOKEN': ''
}
REQUEST_DELAY = 0.001
RATE_LIMIT_DELAY = 5
MAX_PAGES = 12500
STARTING_PAGE = 1

def preprocess_text(text):
    return text.lower()

def get_csrf_token():
    response = requests.post('https://auth.roblox.com/v2/login', headers=HEADERS)
    print(f"CSRF Token Response Status: {response.status_code}")
    if response.status_code == 200 or response.status_code == 403:
        csrf_token = response.headers.get('x-csrf-token')
        print(f"Obtained CSRF Token: {csrf_token}")
        return csrf_token
    else:
        print(f"CSRF Token Response Text: {response.text}")
        raise Exception('Failed to obtain CSRF token.')

def delete_group_post(post_id):
    delete_url = f'https://groups.roproxy.com/v1/groups/{GROUP_ID}/wall/posts/{post_id}'
    try:
        response = requests.delete(delete_url, headers=HEADERS)
        if response.status_code == 200:
            print(f'Successfully deleted post ID {post_id}')
        else:
            print(f'Failed to delete post ID {post_id}, Status Code: {response.status_code}, Response: {response.text}')
    except Exception as e:
        print(f'Failed to delete post ID {post_id}: {str(e)}')

def get_group_wall_posts(cursor=None):
    url = BASE_URL
    if cursor:
        url += f"&cursor={cursor}"
    response = requests.get(url, headers=HEADERS)
    print(f"Group Wall Posts Response Status: {response.status_code}")
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        print("Rate limit hit. Waiting before retrying...")
        time.sleep(RATE_LIMIT_DELAY)
        return get_group_wall_posts(cursor)
    else:
        print(f"Group Wall Posts Response Text: {response.text}")
        raise Exception('Failed to fetch group wall posts.')

def save_scam_comments(scam_comments):
    with open('scam_comments.txt', 'w', encoding='utf-8') as f:
        for comment in scam_comments:
            f.write(comment + '\n')

def check_if_scam(post, vectorizer, svm_classifier):
    content = post.get("body") or ""
    preprocessed_content = preprocess_text(content)
    prediction = svm_classifier.predict(vectorizer.transform([preprocessed_content]))[0]
    probability = svm_classifier.predict_proba(vectorizer.transform([preprocessed_content]))[0][1]
    return prediction, probability, preprocessed_content

# Load the saved models
vectorizer = joblib.load('./models/tfidf_vectorizer.joblib')
svm_classifier = joblib.load('./modelsvm_classifier.joblib')

# Obtain CSRF token
csrf_token = get_csrf_token()
HEADERS['X-CSRF-TOKEN'] = csrf_token

print("Fetching group wall posts...")
scam_comments = []  # List to store scam comments
posts_checked = 0
cursor = None
page_number = STARTING_PAGE

# Iterate over pages of group wall posts
while posts_checked < MAX_PAGES:
    try:
        print(f"Fetching page {page_number}...")
        response_json = get_group_wall_posts(cursor)
        data = response_json.get('data', [])

        # Process each post on the current page
        for post in data:
            prediction, probability, preprocessed_content = check_if_scam(post, vectorizer, svm_classifier)
            print(f"Post ID: {post['id']}")
            print(f"Content: {post['body']}")
            print(f"Prediction: {'Scam' if prediction == 1 else 'Not a scam'} (Probability: {probability:.4f})")
            print("=" * 50)

            # Delete the post if it's identified as a scam with high confidence
            if prediction == 1 and probability > 0.9:
                delete_group_post(post['id']) # Delete the post if it's identified as a scam
                scam_comments.append(preprocessed_content)

            posts_checked += 1
            time.sleep(REQUEST_DELAY)

        cursor = response_json.get('nextPageCursor')
        if not cursor:
            print("No more pages to fetch.")
            break
        page_number += 1

    except requests.exceptions.RequestException as e:
        print(f"Error fetching group wall posts: {str(e)}")
        break
    except Exception as e:
        print(f"Error processing posts: {str(e)}")
        break

# Save scam comments to a file
save_scam_comments(scam_comments)

print(f"Total posts checked: {posts_checked}")
