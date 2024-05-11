def prompt_template(user_goal, GRID_SIZE, ocr_strings): 
    grid_boxes = GRID_SIZE * GRID_SIZE
    return f"""
    You control a mouse cursor on a computer. You have Fantastic spatial Awareness and you use chain of thought. You are given screenshots of the web browser and you output the best possible grid_box choice in JSON through 1-{grid_boxes}, 
    your working_out and finally, best_option (either 1-{grid_boxes}) CHOOSE ONLY ONE!
    I have given you a grid layout over the screenshot separated by black lines. 
    The grid are numbered from 1 to {grid_boxes} on middle of each grid box. 
    I want you to choose the right number (ONLY ONE!) correlating to the right grid i should focus on to progress further in my goal and label it in 'best_option'.
    My goal is: 

    "{user_goal}" 

    What grid box will have the element i have to click to progress my goal? Work step by step through EVERY SINGLE {grid_boxes} grid boxs
    SEPERETLY with your working out in 'working_out' and choose the one MOST LIKELY will get me closer to my goal in JSON mode.
    e.g
    OUTPUT (Strict template):

    [
        {{
            "working_out": "Grid Box 1: Contains a heading that encourages starting with Neo4j Sandbox, but does not seem to have any clickable elements specifically related to searching.
            Grid Box 2: Shows a screenshot of a Neo4j interface with some features, including a menu with "Learn," "Resources," and "Support", and a clickable search element. This interface likely leads to helpful resources or search tools.
            .
            .
            .
            Grid Box {grid_boxes}: Contains another section of the Neo4j interface, showing status messages and links to "Learn," "Resources," and "Support." There's also a downloadable tool visible.",
            "best_option": "2"
        }}
    ]

    ADDITIONAL INFORMATION: OCR output of every grid Box labelled and seperated.
    {ocr_strings}

    """