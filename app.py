from flask import Flask, request, send_file
import requests
import tempfile
import os
from moviepy.editor import *

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Flask app is running!"

@app.route('/create-video', methods=['POST'])
def create_video():
    try:
        data = request.json
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Download images
            image_paths = []
            for i, img_url in enumerate(data['images']):
                response = requests.get(img_url)
                img_path = os.path.join(tmpdir, f'image_{i}.jpg')
                with open(img_path, 'wb') as f:
                    f.write(response.content)
                image_paths.append(img_path)
            
            # Download audio files
            voice_response = requests.get(data['voiceover'])
            voice_path = os.path.join(tmpdir, 'voiceover.mp3')
            with open(voice_path, 'wb') as f:
                f.write(voice_response.content)
            
            music_response = requests.get(data['background_music'])
            music_path = os.path.join(tmpdir, 'background.mp3')
            with open(music_path, 'wb') as f:
                f.write(music_response.content)
            
            # Create video (3 seconds per image)
            clips = [ImageClip(img).set_duration(3) for img in image_paths]
            video = concatenate_videoclips(clips)
            
            # Add audio
            voice_audio = AudioFileClip(voice_path)
            background_audio = AudioFileClip(music_path).volumex(0.3)  # Lower volume
            final_audio = CompositeAudioClip([voice_audio, background_audio])
            final_video = video.set_audio(final_audio)
            
            # Export
            output_path = os.path.join(tmpdir, 'final_video.mp4')
            final_video.write_videofile(output_path, fps=24, verbose=False)
            
            return send_file(output_path, as_attachment=True, download_name='final_video.mp4')
            
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
