## Project: Search and Sample Return
[//]: # (Image References)
[image1]: ./misc/rover_image.jpg
[image2]: ./calibration_images/example_grid1.jpg
[image3]: ./calibration_images/example_rock1.jpg

### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

This is the writeup.

### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.

In order to detect obstacles and rock samples, I added a new function `color_threshold()` in the notebook `Rover_Project_Test_Notebook.ipynb`, cell #7. This function is a slightly modified version of the `color_thresh()` function. I set the value range for each color channel (i.e. R, G and B) to detect obstacles and rock samples. For instance, I detect obstacles if the RGB values are all smaller than or equal to 120, and detect rock samples if the R and G values are greater than or equal to 120 and the B value is smaller than or equal to 100.

#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result.

According to the instruction 1) to 6) in the notebook (cell #14), I modified `process_image()` function as shown below.

##### 1) Define source and destination points for perspective transform
I defined the source and destination points for perspective transform by examining an image. I defined the source point by checking the coordiates of the four corner points in a grid image. I defined the destination point as a 10-pixel square located at the bottom of a warped image (precisely speaking, 6 pixels above from the bottom of the warped image).

##### 2) Apply perspective transform
I Applied the perspective transform function `perspect_transform()` defined in the cell #5 in the notebook.

##### 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
I applied the color threshold function `color_threshold()` mentioned above.

##### 4) Convert thresholded image pixel values to rover-centric coords
I applied `rover_coords()` function defined in the cell #12 in the notebook.

##### 5) Convert rover-centric pixel values to world coords
I applied `pix_to_world()` function defined in the cell #12 in the notebook.

##### 6) Update worldmap
To update the worldmap, I incremented the value of the each channel of the worldmap by 1. I updated the value of the R channel of the worldmap corresponding to the coordinates where obstacles are detected. Similary, the G channel updated where rock samples are detected and the B channel updated where navigable areas are found.

The output movie is `output/test_mapping.mp4`.

### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

The `perception_step()` function determines where the rover can move. It processes an image by the same pipeline as the `process_image()` function in the notebook. Then it converts navigable areas in the rover coodinate to the rover polar coodinates and calculates navigable distances and angles.

#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

I Launced the simulator with the settings shown below.
```
Graphics Quality: Good
Screen Resolution: 1024x768
FPS: 27
```

The results were almost good not perfect. The rover sometimes moved aruond the same area and got stuck there. To avoid this behavior and to improve its exploration, the rover can remember where it has reached by storing the coodinates where it has visited. Then it can be encouraged to move to the area it has never visited.
In the results, the rover didn't pick up rock samples (although it sometimes happened to pick up one). In order to pick up rock samples not by chance, the rover can speed down if it finds a rock sample. Then, it can approach to it by using the location information of the sample appearing in the rover coordinate.
