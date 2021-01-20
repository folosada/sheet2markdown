import json
import cv2
import numpy as np
import io
import imageio
import base64

def contour_minor_than_image(contour_area, image_area):
    p = (contour_area * 100) / image_area
    return (p <= 90)

def detect_square(image):
    gray = cv2.imdecode(image, flags=cv2.IMREAD_GRAYSCALE)
    image_area = gray.shape[0] * gray.shape[1]
    blur = cv2.GaussianBlur(gray, (5, 5), 0)    
    threshold = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]    
    contours, hierarchy = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 

    biggest_contour = contours[0]
    biggest_contour_area = cv2.contourArea(biggest_contour)
    for index in range(1, len(contours)):
        contour_area = cv2.contourArea(contours[index])
        if (contour_area > biggest_contour_area and contour_minor_than_image(contour_area, image_area)):
            biggest_contour = contours[index]
            biggest_contour_area = contour_area

    x, y, w, h = cv2.boundingRect(biggest_contour)
    ROI = gray[y:y+h, x:x+w]    
    return cv2.imencode('.jpg', ROI)


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    print(event)
    body = json.loads(event['body'])

    image_base64 = body.get('image', '')

    image_stream = io.BytesIO(base64.b64decode(image_base64))

    file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)

    cropped_image = detect_square(file_bytes)

    base64_result = base64.b64encode(cropped_image[1])

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "image": base64_result.decode('utf-8'),
            }
        ),
    }
