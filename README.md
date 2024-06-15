## Roblox Group Wall Scam Detector

## Overview

This project aims to identify potential scam posts on a specified Roblox group's wall using machine learning techniques. It fetches posts from the group's wall, processes them through a pre-trained Support Vector Machine (SVM) classifier, and deletes posts identified as scams based on the classifier's predictions.

## Requirements

- Python 3.x
- Required Python packages (install using `pip install -r requirements.txt`):
  - `requests`
  - `joblib`
  - `pyyaml`
  - `scikit-learn`
  - `psutil`

## Setup

1. **Clone the repository and install dependencies:**

   ```bash
   git clone https://github.com/MidnightKittenCat/Roblox-Group-Wall-Scam-Scrubber.git
   cd Roblox-Group-Wall-Scam-Scrubber
   pip install -r requirements.txt
   ```

2. **Configuration:**

   - Obtain a valid Roblox session cookie (`ROBLOX_COOKIE`) with necessary permissions.
   - Update `GROUP_ID` in the `config.yaml` file with the target Roblox group ID.
   - Ensure `tfidf_vectorizer.joblib` and `svm_classifier.joblib` files are available in the project directory (you may need to train these models or download them).

## Usage

Run the script `main.py` to execute the main functionality:

```bash
python main.py
```

The script will fetch posts from the specified Roblox group's wall, classify them using the pre-trained SVM model, and delete posts identified as potential scams based on the classifier's predictions.

## Files

- `main.py`: Main script for fetching group wall posts, processing them, and deleting scam posts.
- `config.yaml`: Configuration file containing parameters such as API credentials and file paths.
- `tfidf_vectorizer.joblib`: Serialized TF-IDF vectorizer model for text preprocessing.
- `svm_classifier.joblib`: Serialized SVM classifier model for scam detection.
- `requirements.txt`: List of Python dependencies required for the project.

## Contributing

Contributions to improve or extend the functionality of this project are welcome! If you encounter any issues or have suggestions for enhancements, please feel free to open an issue or submit a pull request on [GitHub](https://github.com/YourUsername/Roblox-Group-Wall-Scam-Detector).
