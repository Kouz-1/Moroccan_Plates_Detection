import cv2
import numpy as np
import matplotlib.pyplot as plt

def find_contours(dimensions, img):
    # Find all contours
    cntrs, _ = cv2.findContours(img.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Retrieve potential dimensions
    lower_width, upper_width, lower_height, upper_height = dimensions

    # Take top 15 largest contours
    cntrs = sorted(cntrs, key=cv2.contourArea, reverse=True)[:15]

    # Create list to hold valid contours
    filtered_cntrs = []

    for cntr in cntrs:
        intX, intY, intWidth, intHeight = cv2.boundingRect(cntr)
        x, y, w, h = intX, intY, intWidth, intHeight
        roi = img[y:y+h, x:x+w]

        area = w * h
        white_pixels = cv2.countNonZero(roi)
        density = white_pixels / area if area != 0 else 0

        valid = False

        if 300 < area < 1400 and 20 < h < 40 and w < 15 and density > 0.5:
                valid = True
        if 300 < area < 1400 and 20 < h < 40 and w > 15 and density > 0.25:
                valid = True
        if 300 < area < 1400 and not(20 < h < 40) and density > 0.4:
                valid = True
        if not(300 < area < 1400) and  (h < 30) and (w > 30) and (density > 0.3):
            valid = True
        if not(300 < area < 1400) and  (w < 30) and (h > 30) and (density > 0.3):
            valid = True
        if h > 4 * w:
              continue
        if w > 3 * h:
            continue
        if density < 0.25:
           continue
        if density > 0.8:
           continue
           
        #elif (5 < h < 15) and (25 < w < 35) and (density > 0.4):
            #valid = True
            
        if not valid:
            continue



        # Passed all filters
        filtered_cntrs.append(cntr)

    # ---------- Second Loop: Process Filtered Contours ----------
    x_cntr_list = []
    img_res = []

    # Use image copy for visualization
    ii = cv2.cvtColor(img.copy(), cv2.COLOR_GRAY2BGR)

    for cntr in filtered_cntrs:
        intX, intY, intWidth, intHeight = cv2.boundingRect(cntr)

        if lower_width * 0 < intWidth < upper_width * 10 and lower_height * 0 < intHeight < upper_height * 15:
            x_cntr_list.append(intX)

            char_copy = np.zeros((44, 24), dtype=np.uint8)
            char = img[intY:intY+intHeight, intX:intX+intWidth]
            char = cv2.resize(char, (20, 40))
            char = cv2.subtract(255, char)

            # Add border
            char_copy[2:42, 2:22] = char
            char_copy[0:2, :] = 0
            char_copy[:, 0:2] = 0
            char_copy[42:44, :] = 0
            char_copy[:, 22:24] = 0

            img_res.append(char_copy)

            # Draw rectangle on image
            cv2.rectangle(ii, (intX, intY), (intX + intWidth, intY + intHeight), (50, 50, 200), 2)

    # Show result
    plt.imshow(ii, cmap='gray')
    plt.title('Predict Segments')
    plt.show()
    cv2.imwrite('contourrr.jpg',ii)
    # arbitrary function that stores sorted list of character indeces
    indices = sorted(range(len(x_cntr_list)), key=lambda k: x_cntr_list[k])
    img_res_copy = []
    for idx in indices:
        img_res_copy.append(img_res[idx])# stores character images according to their index
    img_res = np.array(img_res_copy)

    return img_res
