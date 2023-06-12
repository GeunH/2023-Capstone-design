import argparse
import numpy as np
import torch
import matplotlib.pyplot as plt
import cv2
import os
from PIL import Image


def show_mask(mask, ax, random_color=False):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([30/255, 144/255, 255/255, 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    ax.imshow(mask_image)
    
def show_points(coords, labels, ax, marker_size=375):
    pos_points = coords[labels==1]
    neg_points = coords[labels==0]
    ax.scatter(pos_points[:, 0], pos_points[:, 1], color='green', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)
    ax.scatter(neg_points[:, 0], neg_points[:, 1], color='red', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)   
    
def show_box(box, ax):
    x0, y0 = box[0], box[1]
    w, h = box[2] - box[0], box[3] - box[1]
    ax.add_patch(plt.Rectangle((x0, y0), w, h, edgecolor='green', facecolor=(0,0,0,0), lw=2))    


def process_images(image_dir):
    output_dir = image_dir + "_OUTPUT"

    ## make sure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Get a list of all the image files in the directory
    image_files = [f for f in os.listdir(image_dir) if f.endswith('.jpg')]

    import sys
    sys.path.append("..")
    from segment_anything import sam_model_registry, SamPredictor

    sam_checkpoint = "sam_vit_h_4b8939.pth"
    model_type = "vit_h"

    device = "cuda"

    sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
    sam.to(device=device)

    predictor = SamPredictor(sam)
    count = 0
    for image_file in image_files:
        # Load the image
        image = cv2.imread(os.path.join(image_dir, image_file))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        print("#####%d/%d#####" % (count, len(image_files)))
        count += 1
        # Set the image in the predictor
        predictor.set_image(image)

        # The input box is the whole image
        h, w, _ = image.shape
        input_box = np.array([0, 0, w, h])

        # Predict the mask
        masks, _, _ = predictor.predict(
            point_coords=None,
            point_labels=None,
            box=input_box[None, :],
            multimask_output=False,
        )

        # Apply the mask to the image by setting the alpha channel to 0 (transparent) in the masked areas
        mask = masks[0]
        image_rgba = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
        image_rgba[..., 3] = (1 - mask) * 255

        # Find contours in the mask
        # contours, _ = cv2.findContours((mask * 255).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # # Draw a bounding box around each contour
        # for contour in contours:
        #     x, y, w, h = cv2.boundingRect(contour)
        #     cv2.rectangle(image_rgba, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Save the image to the output directory with Pillow
        Image.fromarray(image_rgba).save(os.path.join(output_dir, image_file), 'PNG')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process images with segmentation and save output.')
    parser.add_argument('image_dir', type=str, help='Directory path of the images')

    args = parser.parse_args()
    image_dir = args.image_dir

    process_images(image_dir)
