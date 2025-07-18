import os
import base64
from mutagen.flac import FLAC


def save_image(data, album_name, script_dir):
    thumbnail_dir = os.path.join(script_dir, 'cd_thumbnails')
    os.makedirs(thumbnail_dir, exist_ok=True)

    file_path = f"cd_thumbnails/{album_name}.jpg"
    with open(file_path, 'wb') as img_file:
        img_file.write(data)

    return file_path


def get_album_info(base_dir, script_dir):
    album_info_list = []
    total_length = 0

    for root, dirs, files in os.walk(base_dir):
        album_length = 0
        album_year = ""
        album_name = os.path.basename(root)
        artist_name = os.path.basename(os.path.dirname(root))
        album_cover_path = None

        for file in files:
            if file.endswith('.flac'):
                file_path = os.path.join(root, file)
                audio = FLAC(file_path)

                # Get track length and add to total album length
                if audio.info.length:
                    album_length += int(audio.info.length)

                # Get album year from metadata
                if 'date' in audio and not album_year:
                    album_year = audio['date'][0]

                # Get album cover
                if not album_cover_path and audio.pictures:
                    album_cover_path = save_image(audio.pictures[-1].data, album_name, script_dir)

        if album_length > 0:
            album_info_list.append((artist_name, album_name, album_year, album_length, album_cover_path))
            total_length += album_length

    return album_info_list, total_length


def generate_html(album_info_list, total_length):
    html_string = """
    <!DOCTYPE html>
<html>
  <head>
    <title>My CDs</title>
    <link rel="icon" href="../graphics/icon.png" type="image/x-icon">
    <meta charset="UTF-8">
    <link rel="stylesheet" href="../styles/fonts.css">
    <link rel="stylesheet" href="../styles/transitions.css">
    <link rel="stylesheet" href="../styles/global.css">
    <link rel="stylesheet" href="cds.css">
    <script type="text/javascript" src="../scripts/global.js"></script>


  </head>
  <body id="cds_body">
    <audio id="hover" src="../sounds/hover.wav"></audio>
    <audio id="click" src="../sounds/click.wav"></audio>

    <div class="transition transition-1 is-active"></div>
    <div id="home"><img src="../graphics/home.svg" onmouseenter="handleHover()" onmousedown='clickWaitGo(event, "/")'></div>


    <div id="cds_content">
      <h1>The CDs I'm craving</h1>
      <p></p>
      <p>Mariya Takeuchi - Variety (30TH Annversary Edition)</p>
      <p>Brad Sucks - I Don't Know What I'm Doing</p>
      <p>Voltaire: To the Bottom of the Sea</p>
      <p>Sons of Perdition - The Kingdom Is On Fire</p>
      <p>Yasuha - Transit</p>
      <p>Brad Sucks - Guess Who's a Mess</p>
      <p>Brad Sucks - Out of It</p>
      <p>Swans - White Light From The Mouth Of Infinity</p>
      <p></p><p></p>
      <h1>My collection</h1>
      <p></p>
    <div id="showcase">
      
      """

    for artist_name, album_name, album_year, album_length, album_cover_path in album_info_list:
        if album_cover_path:
            img_tag = f'<img src="{album_cover_path}" alt="{album_name} cover" width="200" height="200">\n'
        else:
            img_tag = '<img src="" alt="No cover available" width="200" height="200">\n'
        html_string += f'<div class="cd">{img_tag}<p>{artist_name} - {album_name} ({album_year})</p></div>\n'

    html_string += f'''</div>
    <p>{len(album_info_list)} CDs with total length of {total_length} seconds</p>
    <p>This would total to {(len(album_info_list)*14)/365:.2f} years of new album every two weeks</p>
    <p>Assuming about 15PLN per CD it's {(len(album_info_list)*15) / ((len(album_info_list)*14)/30):.2f} PLN/month</p>
    <p></p>
    <p>Unlike with streaming services...</p>
    <p></p>
    <p>...You get a hard coppy of loslees FLAC record</p>
    <p>...Music is yours to keep forever and can be even passed on as inheritance</p>
    <p>...They keep their value ({(len(album_info_list)*14)} PLN you won't get back form streaming)</p>
    
      <p></p><p></p><p></p><p></p><p></p><p></p>
      <img src="redpill.png" alt="meme" width="360" height="400">
      <p>credit: stolen</p>
      <p></p><p></p><p>

    </div>

    
  <script type="text/javascript" src="../scripts/transition.js"></script>
  </body>

</html>
    '''

    return html_string


if __name__ == "__main__":
    base_music_dir = "E:\\Music"
    script_dir = os.path.dirname(os.path.abspath(__file__))

    album_info_list, total_length = get_album_info(base_music_dir, script_dir)
    html_string = generate_html(album_info_list, total_length)

    html_file_path = os.path.join(script_dir, "cds.html")
    with open(html_file_path, "w", encoding="utf-8") as html_file:
        html_file.write(html_string)

