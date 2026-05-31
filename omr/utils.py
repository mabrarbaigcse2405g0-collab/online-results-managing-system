import cv2
import numpy as np

def detect_answers(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # blur + edge detect
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edged = cv2.Canny(blur, 50, 150)

    # find contours (bubbles)
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    bubbles = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # filter circle-like shapes
        if 20 < w < 60 and 20 < h < 60:
            bubbles.append((x, y, w, h))

    # sort top to bottom
    bubbles = sorted(bubbles, key=lambda b: b[1])

    answers = {}
    options = ['A', 'B', 'C', 'D']

    question_no = 1

    for i in range(0, len(bubbles), 4):
        row = bubbles[i:i+4]

        if len(row) < 4:
            continue

        row = sorted(row, key=lambda b: b[0])  # left to right

        max_fill = 0
        selected = None

        for idx, (x, y, w, h) in enumerate(row):
            bubble = gray[y:y+h, x:x+w]
            total = cv2.countNonZero(bubble)

            if total > max_fill:
                max_fill = total
                selected = options[idx]

        answers[str(question_no)] = selected
        question_no += 1

    return answers