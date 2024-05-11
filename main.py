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

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# CONSTANTS
GRID_SIZE = 3

class Sniper:
    def __init__(self, image_path: str, focal_point: str):

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
        self.image_path = image_path
        self.image = None
        self.final_image_path = None
        self.sub_images_file_path = []
        self.best_next_image_path = None
        self.best_next_image = None



    def load_sniper(self):
        """
        Load your image into the sniper.
        
        """
        self.image = Image.open(f"{self.image_path}")
        print(self.image.format, self.image.size, self.image.mode)
    
    
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
                # Get the image name without the extension
                parent_image_name = os.path.splitext(self.image_path)[0]
                # Create the directory if it doesn't exist
                self.final_image_path = f"all_images/{self.image_path}"
                os.makedirs(f"all_images/{parent_image_name}", exist_ok=True)
                # Save the sub-image in the new directory
                sub_image_file_path = f"all_images/{parent_image_name}/grid_box{(i * grid_size + j + 1)}.png"
                sub_image.save(sub_image_file_path, quality=95)
                
                # Lets save our sub_images_file_path onto our object before drawing a border.
                self.sub_images_file_path.append(sub_image_file_path)
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
        new_image = Image.new(self.image.mode, (width, height))

        sub_image_width = sub_images[0].width
        sub_image_height = sub_images[0].height

        # Paste the sub-images into new image.
        for i in range(grid_size):
            for j in range(grid_size):
                # We calulate index (location in i, j table)for each sub_image
                sub_image = sub_images[i * grid_size + j]
                # We place the sub_image at the right position of the grid.
                new_image.paste(sub_image, (j * sub_image_width, i * sub_image_height))

        # Save the new image
        new_image.save(f"all_images/{self.image_path}", quality=95)

        return new_image
    
    def aim_sniper(self):
        """
        Fire the Sniper to the target.
        
        """
    
        # Breakdown our image into grid boxes and add borders(our eventual grid)
        sub_images,  ocr_strings = self.grid_borders(GRID_SIZE)
        print(ocr_strings)
        # Show a sectain sub_image
        # sub_images[1].show()

        # Lets create our final image grid
        final_image = self.create_grid(sub_images, GRID_SIZE)
        final_image.show()

        #Conduct Vision Search
        # Lets encode our final_image
        base64_image = encode_image(self.final_image_path)
        # Lets finnally call our LLM + Vision 
        best_option = llm_call(USER_GOAL, base64_image, GRID_SIZE, ocr_strings)
        print(f"Best Option is:{best_option}")        
        self.best_next_image_path = f"all_images/{os.path.splitext(self.image_path)[0]}/grid_box{best_option}.png"
        self.best_next_image = Image.open(self.best_next_image_path)
        parent_image_name = os.path.splitext(self.image_path)[0]
        self.best_next_image.save(f"all_images/{parent_image_name}level2.png", quality=95)

    def fire_sniper(self):
        # First, let's make a 9x9 grid of our original image
        width, height = self.image.size
        # Calculate the size of each grid cell
        grid_size_x = width // 9
        grid_size_y = height // 9
        # Create a list to hold the cropped images
        cropped_images = []

        # Loop over the image and add each grid cell to the list
        for i in range(9):
            for j in range(9):
                left = j * grid_size_x
                upper = i * grid_size_y
                right = (j+1) * grid_size_x
                lower = (i+1) * grid_size_y
                cropped_img = self.image.crop((left, upper, right, lower))
                cropped_images.append(cropped_img)

        # Now cropped_images list contains all the cropped images
        cropped_images[0].show()
        cropped_images[1].show()
        cropped_images[2].show()

        

        
        
        


#___________________________________________________________________________________________

# CONSTANTS Variables. Change only these!
# Change this to either 2 to repersent a 2x2 grid, OR 3, to repersent a 3x3 grid. 4 for 4x4 grid can happen, but use with caution.
GRID_SIZE = 3

#Write the goal you're trying to acheive in the screenshot.
USER_GOAL = "I am currently on LinkedIn's job search page. I want to check out the Principal in AI & ML engineering role at Mantel Group"

#___________________________________________________________________________________________
# Lets initalize our object
inital_image = Sniper("linkedinAI.png")
inital_image.load_sniper()

#Conduct Vision Search
inital_image.aim_sniper()


second_image = Sniper(inital_image.best_next_image_path)
second_image.load_sniper()

second_image.aim_sniper()
final_image = Image.open(second_image.best_next_image_path)
final_image.show()

# inital_image.fire_sniper()



