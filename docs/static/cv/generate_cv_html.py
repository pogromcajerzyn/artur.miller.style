

if __name__ == "__main__":

    # TODO I can create expandable content here by usu=ing <pre id="empty_pre1"></pre> empty divs
    # TODO above 3 "switches" for the whole div categories <SKILLS AND TRAINING> <WORK HISTORY> <WORK HISTORY>

    html_content = (f"""
    <!DOCTYPE html>
    <html>
      <head>
        <title>CV</title>
        <link rel="icon" href="../graphics/icon.png" type="image/x-icon">
        <meta charset="UTF-8">
        <link rel="stylesheet" href="../styles/fonts.css">
        <link rel="stylesheet" href="../styles/transitions.css">
        <link rel="stylesheet" href="../styles/global.css">
        <link rel="stylesheet" href="cv.css">
        <script type="text/javascript" src="../scripts/global.js"></script>
      </head>
      <body id="cv_body">
      
        <audio id="hover" src="../sounds/hover.wav"></audio>
        <audio id="click" src="../sounds/click.wav"></audio>
        
        <div class="transition transition-1 is-active">
        </div>
        
        <div id="home"><img src="../graphics/home.svg" 
        onmouseenter="handleHover()" onmousedown='clickWaitGo(event, "/")'>
        </div>

        
        <div id="cv_content">

    <pre>
    Hello!
    Welcome to my CV
    This page is under construction :)
           So wait for the update soon
                               See ya!

    </pre>
            <pre><a class="selectable"
                    id="skills_and_training_button"
                    onmouseenter="handleHover()"
            >&lt; SKILLS AND TRAINING &gt;</a>     <a class="selectable"
                                                      id="work_history_button"
            onmouseenter="handleHover()"
            >&lt; WORK HISTORY  &gt;</a>     <a class="selectable"
                                                id="education_button"
            onmouseenter="handleHover()"
            >&lt; EDUCATION &gt;</a>     <a class="selectable"
                                                id="expand_all_button"
            onmouseenter="handleHover()"
            >&lt; EXPAND ALL &gt;</a>

    </pre>

    <pre>
    2022 - 2024
    ..............................
    |          CREOTECH          |
    ..............................
    </pre>

    <pre>
    2021 - 2022
    ..............................
    |         SatRev S.A         |
    ..............................
    </pre>

    <pre style="color: gray;">
    2017 - 2021
    ..............................
    |  Metrologist...      and   |
    |  Courier, Security staff   |
    ..............................
    </pre>


<!--            This is max width-->
<!--    <pre>.........................................................................................................................................</pre>-->
        </div>

      <script type="text/javascript" src="cv.js"></script>
      <script type="text/javascript" src="../scripts/transition.js"></script>
      </body>

    </html>
    
    """)

    with open("cv.html", "w") as file:
        file.write(html_content)
