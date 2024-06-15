
## Roblox Group Wall Scam Detector

## Overview

This project fetches posts from a specified Roblox group's wall, classifies them using a pre-trained SVM model, and deletes posts identified as potential scams based on the classification results.

## Requirements

- Python 3.x
- Required Python packages (install using `pip install -r requirements.txt`):
  - `joblib`
  - `requests`
  - `pandas`
  - `scikit-learn`

## Setup

1. Clone the repository and install dependencies:

   ```bash
   git clone https://github.com/MidnightKittenCat/Roblox-Group-Wall-Scam-Scrubber.git
   cd "Roblox-Group-Wall-Scam-Scrubber"
   pip install -r requirements.txt
   ```

2. Prepare the environment:
    - Obtain a valid Roblox session cookie (`ROBLOX_COOKIE`) with necessary permissions.
    - Update `GROUP_ID` with the target Roblox group ID.
    - Ensure `tfidf_vectorizer.joblib` and `svm_classifier.joblib` are available in the project directory (download if necessary).

## Usage

Run the script `main.py` to execute the main functionality:

```bash
python main.py
```

## Files

- `main.py`: Contains the main script to fetch group wall posts, classify them, and delete scam posts.
- `tfidf_vectorizer.joblib`: Serialized TF-IDF vectorizer model.
- `svm_classifier.joblib`: Serialized SVM classifier model.
- `requirements.txt`: List of Python dependencies.

## Contributing

Contributions are welcome! If you find any issues or have suggestions, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
