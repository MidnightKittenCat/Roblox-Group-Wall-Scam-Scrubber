# Roblox Group Wall Post Scam Detector

This Python script identifies and removes potential scam posts from a Roblox group wall. It utilizes a pre-trained Support Vector Machine (SVM) model to classify post content as scam or not scam.

**Requirements:**

* Python 3.x
* requests library
* pandas library
* scikit-learn library
* joblib library

**Instructions:**

1. Save the script as `roblox_group_scam_detector.py`.
2. Replace the following placeholders with your own values:
    * `ROBLOX_COOKIE`: Your Roblox security cookie.
    * `GROUP_ID`: The ID of the Roblox group to monitor.
3. Make sure you have trained and saved the TF-IDF vectorizer and SVM classifier models beforehand. The script expects them to be saved as `tfidf_vectorizer.joblib` and `svm_classifier.joblib`, respectively.
4. Run the script from your terminal: `python roblox_group_scam_detector.py`

**How it Works:**

1. The script first obtains a CSRF token from Roblox using a POST request.
2. It then enters a loop that iterates through pages of group wall posts.
3. For each post, the script preprocesses the content (converts it to lowercase) and uses the loaded vectorizer and SVM model to predict whether it's a scam or not.
4. If the prediction is "scam" with a high confidence probability (above 0.9), the script attempts to delete the post and stores the preprocessed content in a list.
5. The script continues iterating through pages until it reaches the maximum number of pages specified or encounters an error.
6. Finally, it saves the list of suspected scam post content to a file named `scam_comments.txt`.

**Important Notes:**

* This script leverages a pre-trained model for scam detection. The accuracy of the model depends on the training data used.
* Modifying Roblox's website structure or authentication methods may break the script.
* Use this script responsibly and ethically.
