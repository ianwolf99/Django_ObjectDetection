from celery import shared_task
from .models import UploadedImage, DetectionResult
import cv2
import torch
import logging

logger = logging.getLogger(__name__)

@shared_task
def perform_object_detection(uploaded_image_id):
    try:
        # Retrieve UploadedImage instance
        uploaded_image = UploadedImage.objects.get(id=uploaded_image_id)
        logger.info(f"Starting object detection for image ID: {uploaded_image_id}")

        # Load YOLOv5 model
        logger.info("Loading YOLOv5 model...")
        model = torch.hub.load('ultralytics/yolov5', 'yolov5n')

        # Read uploaded image and perform detection
        img_path = uploaded_image.image.path
        logger.info(f"Reading image from path: {img_path}")
        img = cv2.imread(img_path)
        img = cv2.resize(img, (1000, 650))
        logger.info("Performing object detection...")
        result = model(img)

        # Process detection results and save to database
        logger.info("Processing detection results...")
        for detection in result.xyxy[0]:
            label = detection['name']
            confidence = detection['confidence']
            x1, y1, x2, y2 = map(int, detection['bbox'])

            # Create DetectionResult object
            DetectionResult.objects.create(
                uploaded_image=uploaded_image,
                label=label,
                confidence=confidence,
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2
            )
            logger.info(f"Detection result saved: label={label}, confidence={confidence}, bbox=({x1},{y1},{x2},{y2})")

        logger.info(f"Object detection completed for image ID: {uploaded_image_id}")
    except Exception as e:
        logger.error(f"Error during object detection for image ID {uploaded_image_id}: {e}")
        raise
