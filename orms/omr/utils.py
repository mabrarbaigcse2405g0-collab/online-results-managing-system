from pathlib import Path
import json
import re

import cv2
import numpy as np


OPTIONS = ("1", "2", "3", "4")


def _load_images(file_path):
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        try:
            from pdf2image import convert_from_path
        except ImportError as exc:
            raise RuntimeError(
                "PDF support requires pdf2image and Poppler. Upload JPG/PNG or install Poppler."
            ) from exc

        pages = convert_from_path(str(path), dpi=180, first_page=1, last_page=1)
        if not pages:
            raise ValueError("The PDF contains no readable page.")
        arr = np.array(pages[0])
        return [cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)]

    image = cv2.imread(str(path))
    if image is None:
        raise ValueError("The uploaded image could not be read.")
    return [image]


def _resize_for_detection(image, max_width=1800):
    h, w = image.shape[:2]
    if w <= max_width:
        return image, 1.0
    scale = max_width / float(w)
    return cv2.resize(image, (int(w * scale), int(h * scale))), scale


def _candidate_bubbles(thresh):
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    candidates = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area <= 20:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        if not (12 <= w <= 100 and 12 <= h <= 100):
            continue

        ratio = w / float(h)
        if not 0.70 <= ratio <= 1.30:
            continue

        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue

        circularity = 4 * np.pi * area / (perimeter * perimeter)
        if circularity < 0.35:
            continue

        candidates.append((x, y, w, h))

    return candidates


def _deduplicate(candidates):
    result = []
    for item in sorted(candidates, key=lambda b: (b[1], b[0])):
        x, y, w, h = item
        cx, cy = x + w / 2, y + h / 2

        if any(
            abs(cx - (xx + ww / 2)) < min(w, ww) * 0.45
            and abs(cy - (yy + hh / 2)) < min(h, hh) * 0.45
            for xx, yy, ww, hh in result
        ):
            continue
        result.append(item)
    return result


def _group_rows(bubbles):
    if not bubbles:
        return []

    bubbles = sorted(bubbles, key=lambda b: (b[1] + b[3] / 2, b[0]))
    median_h = np.median([b[3] for b in bubbles])
    tolerance = max(8, median_h * 0.65)

    rows = []
    for bubble in bubbles:
        cy = bubble[1] + bubble[3] / 2
        placed = False

        for row in rows:
            row_cy = np.mean([b[1] + b[3] / 2 for b in row])
            if abs(cy - row_cy) <= tolerance:
                row.append(bubble)
                placed = True
                break

        if not placed:
            rows.append([bubble])

    rows.sort(key=lambda row: np.mean([b[1] for b in row]))

    # A question row must have at least four candidates. If extra contours
    # are present, take the four most evenly spaced candidates.
    clean_rows = []
    for row in rows:
        row = sorted(row, key=lambda b: b[0])
        if len(row) < 4:
            continue

        if len(row) > 4:
            best = None
            best_score = None
            for i in range(len(row) - 3):
                group = row[i:i+4]
                xs = [b[0] for b in group]
                gaps = np.diff(xs)
                score = float(np.std(gaps))
                if best_score is None or score < best_score:
                    best, best_score = group, score
            row = best

        clean_rows.append(row)

    return clean_rows


def _read_answers_from_image(image):
    image, _ = _resize_for_detection(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Otsu is more robust than a fixed threshold for different scans.
    thresh = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    kernel = np.ones((2, 2), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    bubbles = _deduplicate(_candidate_bubbles(thresh))
    rows = _group_rows(bubbles)

    answers = {}
    multiple_marked = []

    for question_no, row in enumerate(rows, start=1):
        row = sorted(row, key=lambda b: b[0])
        scores = []

        for x, y, w, h in row:
            pad_x = max(1, int(w * 0.15))
            pad_y = max(1, int(h * 0.15))
            roi = thresh[y + pad_y:y + h - pad_y, x + pad_x:x + w - pad_x]
            fill_ratio = cv2.countNonZero(roi) / float(max(1, roi.size))
            scores.append(fill_ratio)

        # Empty bubbles usually have a much lower fill ratio. Require a
        # meaningful absolute fill and a clear margin over the runner-up.
        order = np.argsort(scores)[::-1]
        best_i = int(order[0])
        best = float(scores[best_i])
        second = float(scores[int(order[1])]) if len(order) > 1 else 0.0

        if best < 0.25:
            answers[str(question_no)] = None
            continue

        if second >= best * 0.88:
            answers[str(question_no)] = None
            multiple_marked.append(question_no)
            continue

        answers[str(question_no)] = OPTIONS[best_i]

    return answers, multiple_marked


def detect_answers(file_path):
    images = _load_images(file_path)
    answers = {}
    multiple = []

    for image in images:
        page_answers, page_multiple = _read_answers_from_image(image)
        if not page_answers:
            continue

        offset = len(answers)
        for key, value in page_answers.items():
            answers[str(offset + int(key))] = value
        multiple.extend(offset + q for q in page_multiple)

    if not answers:
        raise ValueError(
            "No OMR bubble rows were detected. Use a clear, straight JPG/PNG scan "
            "of the expected 4-option answer sheet."
        )

    return answers, multiple


def parse_answer_key(text):
    """Accept JSON or simple lines such as 1:1, 2:2, 3:4."""
    text = text.strip()
    if not text:
        return {}

    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return {
                str(k): str(v).strip()
                for k, v in data.items()
                if str(v).strip() in OPTIONS
            }
    except json.JSONDecodeError:
        pass

    result = {}
    for line in text.splitlines():
        match = re.match(r"\s*(\d+)\s*[:=,\-]\s*([1-4])\s*$", line)
        if match:
            result[match.group(1)] = match.group(2)
    return result


def calculate_score(student_answers, answer_key):
    total = len(answer_key)
    marks = sum(
        1
        for q, correct in answer_key.items()
        if student_answers.get(str(q)) == str(correct).upper()
    )
    return marks, total
