from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from .forms import UploadImageForm
from .models import UploadedImage
from .tasks import perform_object_detection
from .models import UploadedImage, DetectionResult
import cv2
import torch
import logging
from django.core.files import File
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import UploadImageForm
from .models import UploadedImage, DetectionResult
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import UploadImageForm
from .models import UploadedImage, DetectionResult
import cv2
import torch
import pandas as pd
import os

@login_required
def upload_image(request):
    try:
        if request.method == 'POST':
            form = UploadImageForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_image = form.save(commit=False)
                uploaded_image.user = request.user
                uploaded_image.save()

                # Trigger asynchronous task for object detection
                # perform_object_detection.delay(uploaded_image.id)
                # print(f"Object detection task triggered for image ID: {uploaded_image.id}")

                # Process the uploaded image and perform object detection
                process_and_save_detection_results(uploaded_image)

                # Redirect to the detection results page
                return redirect('detection_results', image_id=uploaded_image.id)
            else:
                form = UploadImageForm()
        else:
            form = UploadImageForm()
    except Exception as e:
        print(f"Error in upload_image view: {e}")
        raise

    return render(request, 'upload.html', {'form': form})

def process_and_save_detection_results(uploaded_image):
    try:
        # Load YOLOv5 model
        model = torch.hub.load('ultralytics/yolov5', 'yolov5n')

        # Read uploaded image and perform detection
        img_path = uploaded_image.image.path
        img = cv2.imread(img_path)
        img = cv2.resize(img, (1000, 650))
        result = model(img)

        # Convert detected result to pandas data frame
        data_frame = result.pandas().xyxy[0]

        # Process each detection from the data frame
        for index, detection in data_frame.iterrows():
            x1 = int(detection['xmin'])
            y1 = int(detection['ymin'])
            x2 = int(detection['xmax'])
            y2 = int(detection['ymax'])
            label = detection['name']
            confidence = detection['confidence']
            # Directory to save output images (modify this to your desired directory)
            output_directory = 'detection'

            # Create the directory if it doesn't exist
            os.makedirs(output_directory, exist_ok=True)
            # Save the modified image with bounding boxes
            output_image_path = os.path.join(output_directory, f'output_{uploaded_image.id}.jpg')
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 0), 2)
            cv2.putText(img, f"{label} ({confidence:.2f})", (x1, y1 - 5), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)
            cv2.imwrite(output_image_path, img)
            #from django.core.files import File

            # Create DetectionResult object
            with open(output_image_path, 'rb') as f:
                image_file = File(f)
                detection_result = DetectionResult.objects.create(
                uploaded_image=uploaded_image,
                label=label,
                confidence=confidence,
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
                    )
                detection_result.image.save(f'output_{uploaded_image.id}.jpg', image_file)

            

    except Exception as e:
        raise RuntimeError(f"Error during object detection for image ID {uploaded_image.id}: {e}")

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UploadedImage, DetectionResult



@login_required
def gallery_detected(request):
    try:
        detecteds = DetectionResult.objects.all()
        return render(request, 'gallery.html', {'detecteds': detecteds})
    except Exception as e:
        raise e

@login_required
def detection_results(request, image_id):
    try:
        uploaded_image = get_object_or_404(UploadedImage, id=image_id)
        #related_videos = AlphabetVideo.objects.exclude(pk=_id)[:5]
        
        # Assuming you retrieve the appropriate DetectionResult instance here
        detection_result = uploaded_image.detectionresult_set.first()  # Retrieve the first detection result

        if detection_result:
            # Use the processed image URL from the detection result
            image_url = detection_result.image.url
        else:
            image_url = None  # Handle case where no detection result is found

        print(f"Retrieved detection result for image ID {image_id}: {image_url}")
        
        # Pass the processed image URL instead of the uploaded image URL to the template
        return render(request, 'detection_results.html', {'image_url': image_url})
    
    except Exception as e:
        print(f"Error in detection_results view: {e}")
        raise

from django.http import JsonResponse
from .models import DetectionResult

def check_detection_status(request, image_id):
    try:
        uploaded_image = UploadedImage.objects.get(id=image_id)
        detection_results = DetectionResult.objects.filter(uploaded_image=uploaded_image)
        if detection_results.exists():
            return JsonResponse({'status': 'complete'})
        else:
            return JsonResponse({'status': 'processing'})
    except UploadedImage.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Image not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
