import json
import cv2
import numpy as np
import io
import imageio


def detect_square(image):
    image = cv2.imdecode(image)

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_image = cv2.medianBlur(gray, 5)

    sharpen_kernel = np.array([-1, -1, -1], [-1, 9, -1], [-1, -1, -1])
    sharpen = cv2.filter2D(blur, -1, sharpen_kernel)

    threshold = cv2.threshold(sharpen, 160, 255, cv2.THRESH_BINARY_INV)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    close = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if (len(contours) > 0):
        contours = contours[0] if len(contours) == 2 else contours[1]

        biggest_contour = contours[0]
        biggest_contour_area = cv2.contour_area(biggest_contour)
        for index in range(1, len(contours)):
            contour_area = cv2.contourArea(contours[index])
            if (contour_area > biggest_contour_area):
                biggest_contour = contours[index]

        x, y, w, h = cv2.boundingRect(biggest_contour)
        ROI = image[y:y+h, x:x+h]
        return cv2.imencode('.jpg', ROI)
    raise Exception('No squares found!')


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

    image = imageio.imread(io.BytesIO(base64.b64decode(image_base64)))

    cropped_image = detect_square(image)

    base64_result = base64.b64encode(cropped_image)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "image": base64_result,
            }
        ),
    }
