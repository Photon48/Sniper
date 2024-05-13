"""
    This project implements curser control for automated browser navigation using Computer Vision & language multi-modal models.

    Auther: Photon48
    Start Date: 09/05/2024


"""

__author__ = "Photon48"
__email__ = "rishu.goyal@outlook.com.au"
__status__ = "In Progress"

from PIL import Image, ImageOps, ImageDraw, ImageFont
from llm import encode_image, llm_call
import os, sys
import pytesseract
import time
import streamlit as st


def main(user_goal, uploaded_image):
    pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"


    class Sniper:
        def __init__(self, image_path: str, focal_point: int, grid_size: int, user_goal):

            """
            Initalize our Open AI innstance and setup housekeeping
            
            Attributes
            __________

            image_path : str
                Shows the  location of the  path to our image in the file directory. Make sure image is in JPG.
                Better Quality = Better results
                Use Light Mode when taking Screenshots.

            
            """
            self.focal_point = focal_point
            # ingest focal_point into image_path
            # image_path = os.path.splitext(image_path)[0] + str(focal_point) + os.path.splitext(image_path)[1]
            self.image_path = image_path
            self.image_name = os.path.splitext(image_path)[0]
            self.grid_image_path = f"all_images/{self.image_path}"
            self.sub_images_file_path = []
            self.best_next_image_path = None
            self.best_next_image = None
            self.grid_size = grid_size
            self.user_goal = user_goal
            self.image = Image.open(f"{self.image_path}")

        
        def calculate_border(self, i:int, j:int, grid_size:int, border_width:int) -> list:
            """
            We calculate which images receive a border to create a grid depending on image location.
            
            Attributes
            ----------
            
            i, j : str
                Are two nested iterators where i is for row, j is for column.

            grid_size : str
                a single number. if 2, grid sub_images will be 2x2, if 3, 3x3, and so on.
            """

            return (border_width if j > (grid_size-1) else 0, 
                    border_width if i > (grid_size-1) else 0, 
                    border_width if j < grid_size - 1 else 0, 
                    border_width if i < grid_size - 1 else 0)

        def crop_sub_image(self, i:int, j:int, sub_image_width:int, sub_image_height:int) -> object:
            """
            We calculate dimensions of crops depending on image location and crop them from image, returing an object.
            
            Attributes
            ----------

            i, j : str
                Are two nested iterators where i is for row, j is for column.

            sub_image_width, sub_image_height : str
                The calculated width and height of a single grid box OR sub_image
            """

            left = j * sub_image_width
            upper = i * sub_image_height
            right = (j + 1) * sub_image_width
            lower = (i + 1) * sub_image_height
            return self.image.crop((left, upper, right, lower))

        def grid_borders(self, grid_size: int):
            """
            This breaks down a single image into n x n gridd sub_images.
            
            Attributes
            ----------
            
            grid_size : str
                a single number. if 2, grid sub_images will be 2x2, if 3, 3x3, and so on.
            """

            width, height = self.image.size
            sub_image_height = height // grid_size
            sub_image_width = width  // grid_size

            # Some important draw variables.
            color = "black"
            # Calculated to fit any image size.
            border_width = int(min(self.image.size) * 0.03)
            font_size = int(min(self.image.size) * 0.1)

            # Load a font. You may need to download a font file (.ttf)
            font = ImageFont.truetype("fonts/Arial_Bold.ttf", font_size)
            sub_images = []
            ocr_strings = []
            for i in range(grid_size):
                for j in range(grid_size):
                    # Lets break down our image into sub_images.
                    sub_image = self.crop_sub_image(i, j, sub_image_width, sub_image_height)


                    # Here, we are saving our sub_images/grid_boxes
                    os.makedirs(f"all_images/{self.image_name}", exist_ok=True)
                    # Save the sub-image in the new directory
                    sub_image_file_path = f"all_images/{self.image_name}/grid_box{(i * grid_size + j + 1)}.png"
                    sub_image.save(sub_image_file_path, quality=95)
                    
                    # Lets add a number trnasposed to each sub_image.
                    draw = ImageDraw.Draw(sub_image)
                    number_width = int((self.image.size[0]/grid_size) * 0.45)
                    number_length = int((self.image.size[1]/grid_size) * 0.45)
                    draw.text((number_width, number_length), str(i * grid_size + j + 1), fill=color, font=font)
                    
                    #conduct OCR on seperated images.
                    ocr_string = pytesseract.image_to_string(sub_image)
                    ocr_strings.append(ocr_string)
                    # print(ocr_string)


                    border = self.calculate_border(i, j, grid_size, border_width)
                    sub_image = ImageOps.expand(sub_image, border=border, fill=color)
                    sub_images.append(sub_image)
            ocr_strings = [f"\n____________\nGrid Box: {i+1}\n{ocr_string}" for i, ocr_string in enumerate(ocr_strings)]
            ocr_strings = "".join(ocr_strings)
            return sub_images, ocr_strings
            
        def create_grid(self, sub_images: object, grid_size: int) -> object:
            """
            This creates our final grid image.
            
            Attributes
            ----------
            
            sub_images : list
                a list of  sub_images.
            
            grid_size : str
                a single number. if 2, grid sub_images will be 2x2, if 3, 3x3, and so on.
            """
            # We create a new image of the right size.
            width, height = self.image.size
            grid_image = Image.new(self.image.mode, (width, height))

            sub_image_width = sub_images[0].width
            sub_image_height = sub_images[0].height

            # Paste the sub-images into new image.
            for i in range(grid_size):
                for j in range(grid_size):
                    # We calulate index (location in i, j table)for each sub_image
                    sub_image = sub_images[i * grid_size + j]
                    # We place the sub_image at the right position of the grid.
                    grid_image.paste(sub_image, (j * sub_image_width, i * sub_image_height))

            # Save the new image
            grid_image.save(self.grid_image_path, quality=95)

            return grid_image
        
        def aim_sniper(self):
            """
            Fire the Sniper to the target.
            
            """
            st.write("Aiming Sniper...")
            # Breakdown our image into grid boxes and add borders(our eventual grid)
            sub_images,  ocr_strings = self.grid_borders(self.grid_size)
            print(ocr_strings)
            # Show a sectain sub_image
            # sub_images[1].show()

            # Lets create our final image grid
            grid_image = self.create_grid(sub_images, self.grid_size)
            # grid_image.show()

            #Conduct Vision Search
            # Lets encode our grid_image
            base64_image = encode_image(self.grid_image_path)
            # Lets finnally call our LLM + Vision 
            best_option = llm_call(self.user_goal, base64_image, self.grid_size, ocr_strings)
            print(f"Best Option is:{best_option}")        
            self.best_next_image_path = f"all_images/{self.image_name}/grid_box{best_option}.png"
            self.best_next_image = Image.open(self.best_next_image_path)
            self.best_next_image.save(f"{os.path.splitext(self.image_path)[0] + str(self.focal_point+1)}.png", quality=95)
            self.best_next_image_path = f"{os.path.splitext(self.image_path)[0] + str(self.focal_point+1)}.png"
            return best_option


            
    def fire_sniper(best_option1, best_option2):
        st.write("Firing Sniper...")
        target_image = Image.open(f"all_images/{second_image.image_name}/grid_box{best_option2}.png")
        # Create a draw object.
        draw = ImageDraw.Draw(target_image)  
        # Calculate the center and radius of the circle
        width, height = target_image.size
        center = (width // 2, height // 2)
        radius = min(width, height) // 5

        # Draw the circle
        draw.ellipse((center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius), outline='red', width=10)

        # Save the blended image
        target_image.save(f"all_images/{second_image.image_name}/grid_box{best_option2}.png")

        # Combine all sub images into one.
        # Open the images
        filenames = [f"all_images/{second_image.image_name}/grid_box{i}.png" for i in range(1, 10)]
        images = [Image.open(filename) for filename in filenames]
        
        # Calculate the size of the combined image
        width, height = images[0].size
        combined_width = width * 3
        combined_height = height * 3

        # Create a new image of the combined size
        combined_image = Image.new('RGB', (combined_width, combined_height))

        # Paste the images into the combined image
        for i in range(3):
            for j in range(3):
                image = images[i * 3 + j]
                combined_image.paste(image, (j * width, i * height))

        # Save the combined image
        combined_image.save(f"all_images/{inital_image.image_name}/grid_box{best_option1}.png")

        # Now lets combine our inital scope.

        # Get the list of image filenames
        filenames = [f"all_images/{inital_image.image_name}/grid_box{i}.png" for i in range(1, 10)]

        # Open the images
        images = [Image.open(filename) for filename in filenames]

        # Calculate the size of the combined image
        width, height = images[0].size
        combined_width = width * 3
        combined_height = height * 3

        # Create a new image of the combined size
        combined_image_initial = Image.new('RGB', (combined_width, combined_height))

        # Paste the images into the combined image
        for i in range(3):
            for j in range(3):
                image = images[i * 3 + j]
                combined_image_initial.paste(image, (j * width, i * height))

        # Save the combined image
        combined_image_initial_path = f"{inital_image.image_name}Final_image.png"
        combined_image_initial.save(combined_image_initial_path)
        # combined_image_initial.show()
        return combined_image_initial_path

    #___________________________________________________________________________________________

    # CONSTANTS Variables. Change only these!
    # Change this to either 2 to repersent a 2x2 grid, OR 3, to repersent a 3x3 grid. 4 for 4x4 grid can happen, but use with caution.
    grid_size = 3

    #Write the goal you're trying to acheive in the screenshot.
    # user_goal = "Please click on the LinkedIn blue logo on the search bar on your top left."

    #___________________________________________________________________________________________
    # Lets initalize our object
    st.write("Loading Sniper...")

    inital_image = Sniper(uploaded_image, 1, grid_size, user_goal)
    #Conduct Vision Search
    best_option1 = inital_image.aim_sniper()

    time.sleep(1)

    second_image = Sniper(inital_image.best_next_image_path, 2, grid_size, user_goal)

    best_option2 = second_image.aim_sniper()
    grid_image = Image.open(second_image.best_next_image_path)
    # grid_image.show()
    final_image_path = fire_sniper(best_option1, best_option2)
    return final_image_path



if __name__ == "__main__":
    main()


