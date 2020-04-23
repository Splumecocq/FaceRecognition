# Face Recognition

The objective of this project of is to build an elementary interface to apply modern algorithm of **Face Recognition** on real-time video from Webcam.
The first implementation is based on:
* **MTCNN** (Multi-task Cascaded Convolutional Networks) to faces detection
* and inception_resnet trained on VGGFace2 to extract face features and recognition
This can identify myself (Simon):
![Exemple my face](https://raw.githubusercontent.com/Splumecocq/FaceRecognition/master/Image/MyFace_Recognation.jpg)


:construction:
Next algorithms as **SDD** (Single Shot Detector ) and **Yolo** (You only look once) will be added later.

# Contribution
My contribution is an interface with the details of MTCNN and the possibility to custom the network:
-	Number of boxes after each neuronal networks
-	Possibility to switch from cpu to gpu
-	Update the thresholds at each levels
Example 2:

The program is organized according to the following diagram:



