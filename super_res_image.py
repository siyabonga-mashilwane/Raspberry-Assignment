import argparse
import time
import cv2
import os

ap = argparse.ArgumentParser()
ap.add_argument("-m", "--model", required=True, help="path to super resolution model")
ap.add_argument("-i", "--image", required=True, help="path to input image we want to increase resolution of")
args = vars(ap.parse_args())

# extract the model name and model scale from the file path
modelName = os.path.basename(args["model"]).split("_")[0].lower()
modelSize = args["model"].split("_x")[-1].split(".")[0]
modelSize = int(modelSize) if modelSize.isdigit() else 1

print("[INFO] loading super resolution model: {}".format(args["model"]))
print("[INFO] model name: {}".format(modelName))
print("[INFO] model size: {}".format(modelSize))

sr = cv2.dnn_superres.DnnSuperResImpl_create()
sr.readModel(args["model"])
sr.setModel(modelName, modelSize)

image = cv2.imread(args["image"])
print("[INFO] w: {}, h: {}".format(image.shape[1], image.shape[0]))

start = time.time()
upscaled = sr.upsample(image)
end = time.time()

print("[INFO] super resolution took {:.6f} seconds".format(end - start))
print("[INFO] w: {}, h: {}".format(upscaled.shape[1],upscaled.shape[0]))

#Compare this model with Bicubic interpolation
start = time.time()
bicubic = cv2.resize(image, (upscaled.shape[1], upscaled.shape[0]), interpolation=cv2.INTER_CUBIC)
end = time.time()
print("[INFO] bicubic interpolation took {:.6f} seconds".format(end - start))

# display the original image and the upscaled image
cv2.imshow("Original", image)
cv2.imshow("Upscaled", upscaled)
cv2.imshow("Bicubic", bicubic)
cv2.waitKey(0)